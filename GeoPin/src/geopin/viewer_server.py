from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .config import GeoPinConfig
from .session_store import SessionStore


def build_viewer_app(config: GeoPinConfig, store: SessionStore) -> FastAPI:
    app = FastAPI(title="GeoPin Viewer", version="0.1.0")
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/viewer")

    @app.get("/healthz")
    async def healthz() -> JSONResponse:
        return JSONResponse({"status": "ok", "viewer": True})

    @app.get("/viewer")
    async def viewer() -> FileResponse:
        return FileResponse(static_dir / "viewer.html")

    @app.get("/api/sessions/{session_id}")
    async def read_session(session_id: str) -> JSONResponse:
        try:
            session = store.read(session_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse(session.model_dump(mode="json"))

    @app.get("/api/meta")
    async def meta() -> JSONResponse:
        return JSONResponse(
            {
                "name": "GeoPin Viewer",
                "version": "0.1.0",
                "base_url": config.base_url,
            }
        )

    return app
