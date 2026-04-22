from __future__ import annotations

import os
import subprocess
import sys
from typing import Final

WINDOW_TITLE: Final[str] = "GeoPin"
WINDOW_WIDTH: Final[int] = 1180
WINDOW_HEIGHT: Final[int] = 780


def run_window(
    url: str,
    title: str = WINDOW_TITLE,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
) -> None:
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError(
            "pywebview is not installed. Install it with `pip install pywebview` or reinstall GeoPin."
        ) from exc

    webview.create_window(
        title,
        url=url,
        width=width,
        height=height,
        min_size=(900, 560),
        resizable=True,
        text_select=False,
    )
    webview.start(debug=False)



def spawn_window(
    url: str,
    title: str = WINDOW_TITLE,
    width: int = WINDOW_WIDTH,
    height: int = WINDOW_HEIGHT,
) -> None:
    cmd = [
        sys.executable,
        "-m",
        "geopin",
        "window",
        "--url",
        url,
        "--title",
        title,
        "--width",
        str(width),
        "--height",
        str(height),
    ]

    kwargs: dict[str, object] = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }

    if os.name == "nt":
        detached = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        new_group = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        kwargs["creationflags"] = detached | new_group
    else:
        kwargs["start_new_session"] = True

    subprocess.Popen(cmd, **kwargs)
