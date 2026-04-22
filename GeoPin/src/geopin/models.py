from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Point(BaseModel):
    label: str = Field(..., min_length=1, max_length=160)
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class SessionData(BaseModel):
    points: list[Point] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("points")
    @classmethod
    def validate_points(cls, points: list[Point]) -> list[Point]:
        if not points:
            raise ValueError("At least one point is required.")
        if len(points) > 5:
            raise ValueError("At most 5 points are supported in v0.1.")
        return points


class PlaceResolution(BaseModel):
    query: str
    resolved_name: str
    lat: float
    lng: float
    confidence: float | None = None
    source: str = "nominatim"


class ViewerResponse(BaseModel):
    viewer_url: str
    session_id: str
    mode: Literal["3d_globe"] = "3d_globe"


class ResolveAndShowResponse(ViewerResponse):
    resolved_points: list[Point]
