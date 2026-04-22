# GeoPin v0.1 Design

GeoPin v0.1 is a narrow tool for AI assistants that need location visualization.

Its job is simple:

1. accept a place name
2. resolve it to coordinates
3. show it on a 3D globe with a pin

## Design goals

- very small surface area
- low token usage
- readable JSON results
- compatible with MCP-first agent workflows
- easy to adapt to OpenClaw and Hermes

## Core components

- **Geocoder**: resolve natural-language place names to coordinates
- **Session store**: write and read tiny viewer sessions
- **Viewer server**: local HTTP server for a 3D globe page
- **MCP server**: exposes narrow tools to agents
- **Adapters**: OpenClaw skill and Hermes config example

## Out of scope

- GPS device tracking
- route planning
- weather
- population/history lookup
- advanced GIS analysis

## Tool surface

- `resolve_place(place_text)`
- `show_pin(points)`
- `resolve_and_show(places)`

This is intentionally small so the agent can auto-select the correct tool easily.
