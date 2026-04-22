from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import uvicorn

from .config import GeoPinConfig
from .desktop_window import run_window
from .mcp_server import GeoPinRuntime, build_mcp_server
from .viewer_server import build_viewer_app

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GeoPin CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    viewer = sub.add_parser("viewer", help="Run the local GeoPin viewer only.")
    viewer.add_argument("--viewer-host", default="127.0.0.1")
    viewer.add_argument("--viewer-port", type=int, default=4173)
    viewer.add_argument("--session-dir", default=".geopin_sessions")

    mcp = sub.add_parser("mcp", help="Run the MCP server and background viewer.")
    mcp.add_argument("--viewer-host", default="127.0.0.1")
    mcp.add_argument("--viewer-port", type=int, default=4173)
    mcp.add_argument("--session-dir", default=".geopin_sessions")

    window = sub.add_parser("window", help="Open GeoPin in a native desktop window.")
    window.add_argument("--viewer-host", default="127.0.0.1")
    window.add_argument("--viewer-port", type=int, default=4173)
    window.add_argument("--session-dir", default=".geopin_sessions")
    window.add_argument("--session-id", default=None)
    window.add_argument("--url", default=None)
    window.add_argument("--title", default="GeoPin")
    window.add_argument("--width", type=int, default=1180)
    window.add_argument("--height", type=int, default=780)

    return parser


def config_from_args(args: argparse.Namespace) -> GeoPinConfig:
    return GeoPinConfig(
        viewer_host=args.viewer_host,
        viewer_port=args.viewer_port,
        session_dir=Path(args.session_dir),
    )


def run_viewer(config: GeoPinConfig) -> None:
    runtime = GeoPinRuntime(config)
    app = build_viewer_app(config, runtime.store)
    uvicorn.run(app, host=config.viewer_host, port=config.viewer_port, log_level="info")


def wait_for_viewer(base_url: str, timeout_seconds: float = 10.0) -> None:
    import time

    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(f"{base_url}/healthz", timeout=1.5) as response:
                if response.status == 200:
                    return
        except URLError as exc:
            last_error = exc
        except Exception as exc:
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Viewer did not become ready at {base_url}.") from last_error


def run_window_mode(config: GeoPinConfig, args: argparse.Namespace) -> None:
    runtime = GeoPinRuntime(config)
    if args.url:
        target_url = args.url
    else:
        runtime.ensure_viewer_started()
        wait_for_viewer(config.base_url)
        target_url = f"{config.base_url}/viewer?session={args.session_id}" if args.session_id else f"{config.base_url}/viewer"
    run_window(target_url, title=args.title, width=args.width, height=args.height)


def run_mcp(config: GeoPinConfig) -> None:
    server = build_mcp_server(config)
    logger.info("Starting GeoPin MCP server.")
    logger.info("Background viewer will be available at %s", config.base_url)
    server.run()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = config_from_args(args)

    if args.command == "viewer":
        run_viewer(config)
        return

    if args.command == "mcp":
        run_mcp(config)
        return

    if args.command == "window":
        run_window_mode(config, args)
        return

    parser.error("Unknown command.")
