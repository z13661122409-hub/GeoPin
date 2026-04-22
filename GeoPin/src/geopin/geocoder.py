from __future__ import annotations

from dataclasses import dataclass

import httpx

from .config import GeoPinConfig
from .models import PlaceResolution


class GeoPinError(RuntimeError):
    """Base error for GeoPin."""


class PlaceNotFoundError(GeoPinError):
    pass


class AmbiguousPlaceError(GeoPinError):
    def __init__(self, query: str, candidates: list[str]) -> None:
        self.query = query
        self.candidates = candidates
        super().__init__(f"Ambiguous place for query '{query}'")


@dataclass(slots=True)
class Geocoder:
    config: GeoPinConfig

    async def resolve(self, place_text: str) -> PlaceResolution:
        place_text = place_text.strip()
        if not place_text:
            raise PlaceNotFoundError("Empty place text.")

        params = {
            "q": place_text,
            "format": "jsonv2",
            "limit": 3,
            "addressdetails": 1,
        }
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.config.geocode_timeout_seconds) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            results = response.json()

        if not results:
            raise PlaceNotFoundError(f"Could not resolve '{place_text}' to a real-world location.")

        top = results[0]
        candidates = [item.get("display_name", "") for item in results if item.get("display_name")]

        # A lightweight ambiguity rule: if multiple candidates have the same leading token and
        # the best score is weakly distinguished, surface the ambiguity.
        # Nominatim does not always return an explicit score, so this stays intentionally simple.
        if len(candidates) > 1 and place_text.lower() in {c.split(",")[0].strip().lower() for c in candidates}:
            first_tokens = {c.split(",")[0].strip().lower() for c in candidates}
            if len(first_tokens) == 1 and len({c.lower() for c in candidates}) > 1:
                raise AmbiguousPlaceError(place_text, candidates)

        try:
            lat = float(top["lat"])
            lng = float(top["lon"])
        except (KeyError, TypeError, ValueError) as exc:
            raise PlaceNotFoundError(f"Could not parse coordinates for '{place_text}'.") from exc

        return PlaceResolution(
            query=place_text,
            resolved_name=top.get("display_name", place_text),
            lat=lat,
            lng=lng,
            confidence=0.99 if len(results) == 1 else 0.9,
            source="nominatim",
        )
