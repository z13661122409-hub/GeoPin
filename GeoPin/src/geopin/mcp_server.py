from __future__ import annotations

import logging
import threading
import webbrowser
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP

from .config import GeoPinConfig
from .desktop_window import spawn_window
from .geocoder import AmbiguousPlaceError, Geocoder, PlaceNotFoundError
from .models import Point, ResolveAndShowResponse, SessionData, ViewerResponse
from .session_store import SessionStore
from .viewer_server import build_viewer_app

logger = logging.getLogger(__name__)


class GeoPinRuntime:
    def __init__(self, config: GeoPinConfig) -> None:
        self.config = config
        self.store = SessionStore(config.session_dir)
        self.geocoder = Geocoder(config)
        self._viewer_started = False

    def ensure_viewer_started(self) -> None:
        if self._viewer_started:
            return

        app = build_viewer_app(self.config, self.store)

        def run_viewer() -> None:
            uvicorn.run(
                app,
                host=self.config.viewer_host,
                port=self.config.viewer_port,
                log_level="warning",
            )

        thread = threading.Thread(target=run_viewer, name="geopin-viewer", daemon=True)
        thread.start()
        self._viewer_started = True
        logger.info("GeoPin viewer started at %s", self.config.base_url)

    def create_viewer_response(self, points: list[Point]) -> ViewerResponse:
        self.ensure_viewer_started()
        session_id = self.store.create(SessionData(points=points))
        return ViewerResponse(
            viewer_url=f"{self.config.base_url}/viewer?session={session_id}",
            session_id=session_id,
        )


def build_mcp_server(config: GeoPinConfig) -> FastMCP:
    runtime = GeoPinRuntime(config)
    mcp = FastMCP("geopin")

    @mcp.tool()
    async def resolve_place(place_text: str) -> dict[str, Any]:
        """Resolve a place name into a normalized label and coordinates."""
        try:
            result = await runtime.geocoder.resolve(place_text)
        except AmbiguousPlaceError as exc:
            return {
                "error": "ambiguous_place",
                "query": exc.query,
                "candidates": exc.candidates,
            }
        except PlaceNotFoundError as exc:
            return {
                "error": "place_not_found",
                "message": str(exc),
                "query": place_text,
            }
        return result.model_dump(mode="json")

    @mcp.tool()
    async def show_pin(
        points: list[dict[str, Any]],
        open_in_browser: bool = False,
        open_in_window: bool = False,
    ) -> dict[str, Any]:
        """Show one or more existing coordinates on the local 3D globe viewer."""
        typed_points = [Point.model_validate(item) for item in points[: config.max_points_per_session]]
        response = runtime.create_viewer_response(typed_points)
        if open_in_browser:
            webbrowser.open(response.viewer_url)
        if open_in_window:
            spawn_window(response.viewer_url)
        return response.model_dump(mode="json")

    @mcp.tool()
    async def resolve_and_show(
        places: list[str],
        open_in_browser: bool = False,
        open_in_window: bool = False,
    ) -> dict[str, Any]:
        """Resolve one or more place names and immediately show them on the local 3D globe viewer."""
        resolved_points: list[Point] = []
        for place_text in places[: config.max_points_per_session]:
            try:
                result = await runtime.geocoder.resolve(place_text)
            except AmbiguousPlaceError as exc:
                return {
                    "error": "ambiguous_place",
                    "query": exc.query,
                    "candidates": exc.candidates,
                }
            except PlaceNotFoundError as exc:
                return {
                    "error": "place_not_found",
                    "message": str(exc),
                    "query": place_text,
                }
            resolved_points.append(
                Point(
                    label=result.resolved_name,
                    lat=result.lat,
                    lng=result.lng,
                    confidence=result.confidence,
                )
            )

        viewer = runtime.create_viewer_response(resolved_points)
        if open_in_browser:
            webbrowser.open(viewer.viewer_url)
        if open_in_window:
            spawn_window(viewer.viewer_url)
        return ResolveAndShowResponse(
            resolved_points=resolved_points,
            viewer_url=viewer.viewer_url,
            session_id=viewer.session_id,
            mode="3d_globe",
        ).model_dump(mode="json")

    return mcp
