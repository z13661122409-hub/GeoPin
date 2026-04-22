from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class GeoPinConfig:
    viewer_host: str = "127.0.0.1"
    viewer_port: int = 4173
    session_dir: Path = Path.cwd() / ".geopin_sessions"
    user_agent: str = "GeoPin/0.1 (https://github.com/yourname/geopin)"
    geocode_timeout_seconds: float = 12.0
    max_points_per_session: int = 5

    @property
    def base_url(self) -> str:
        return f"http://{self.viewer_host}:{self.viewer_port}"
