# GeoPin

**GeoPin** is a tiny open-source location visualization tool for AI agents.

When a user asks where a place is, GeoPin lets an agent automatically open a **3D globe** and drop a **pin** on the exact location.

GeoPin is intentionally narrow:

- lightweight
- low-token
- safe by design
- easy to adapt to different agents
- built around **MCP** for broad compatibility

It is a great fit for:

- OpenClaw skills
- Hermes Agent MCP integrations
- other MCP-capable assistants
- local AI setups that need a simple place visualizer

## What GeoPin does

Given a place like:

- `Tokyo`
- `Ohio State University`
- `Columbus, Ohio`
- `Beijing, China`

GeoPin will:

1. resolve the place into coordinates
2. start or reuse a lightweight local viewer
3. open a **3D globe**
4. place one or more pins on the globe
5. return a structured result the agent can use in chat

## What GeoPin does not do

GeoPin v0.1 is deliberately small. It does **not**:

- read local files
- access emails, contacts, or passwords
- request device GPS permissions
- plan routes
- do advanced GIS analysis
- replace full map software

## Features

- **MCP server** with a narrow, safe tool surface
- **Local 3D viewer** served from the same process
- **Native desktop window mode** via pywebview
- **OpenStreetMap / Nominatim geocoding** by default
- **Single-place and multi-place pinning**
- **OpenClaw skill adapter** with `SKILL.md`
- **Hermes config example**
- **Structured JSON responses** to keep token usage low

## Tools exposed by the MCP server

### `resolve_place`
Resolve one place name into a normalized name and coordinates.

### `show_pin`
Render one or more coordinates on the local 3D globe viewer.

### `resolve_and_show`
Resolve place names and immediately show them on the globe.

This is the most useful tool for agent auto-triggering.

## Quick start

### 1. Install

Using `uv`:

```bash
uv venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
uv pip install -e .
```

Or with plain pip:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -e .
```

### 2. Run the MCP server

```bash
geopin mcp
```

This starts:

- the MCP server on stdio
- a lightweight local viewer on `http://127.0.0.1:4173`

You can change the port:

```bash
geopin mcp --viewer-port 5173
```

### 3. Open GeoPin in a native window

```bash
geopin window
```

This opens the viewer inside a real desktop window instead of your browser.

If you already have a session id, you can open it directly:

```bash
geopin window --session-id demo
```

### 4. Run the viewer only

```bash
geopin viewer
```

### 5. Test the REST API locally

```bash
geopin viewer --viewer-port 4173
```

Then visit:

- `http://127.0.0.1:4173/healthz`
- `http://127.0.0.1:4173/viewer`

## OpenClaw

See `adapters/openclaw/SKILL.md`.

OpenClaw skills are directories containing a `SKILL.md` file with YAML frontmatter and markdown instructions. GeoPin ships one adapter folder you can copy into your OpenClaw skills directory.

## Hermes Agent

Hermes supports MCP servers and `uvx`/stdio-based server setups, which fits GeoPin well.

A config example is included in `adapters/hermes/config.example.yaml`.

## Why MCP first

GeoPin uses the official Python MCP SDK and keeps stdout clean in stdio mode.

## Example workflow

User asks:

> Show me Tokyo on a globe.

Agent calls:

```json
{
  "places": ["Tokyo"]
}
```

GeoPin returns:

```json
{
  "resolved_points": [
    {
      "label": "Tokyo, Japan",
      "lat": 35.6762,
      "lng": 139.6503,
      "confidence": 0.99
    }
  ],
  "viewer_url": "http://127.0.0.1:4173/viewer?session=...",
  "session_id": "...",
  "mode": "3d_globe"
}
```

## Repository layout

```text
geopin/
  src/geopin/
    cli.py
    config.py
    geocoder.py
    mcp_server.py
    models.py
    session_store.py
    viewer_server.py
    static/
      viewer.html
  adapters/
    openclaw/
      SKILL.md
    hermes/
      config.example.yaml
  docs/
    design-v0.1.md
    api.md
    security.md
```

## Security posture

GeoPin is built to be easy to trust.

By default it only:

- resolves place names with a geocoding service
- stores lightweight local viewer sessions
- serves a local visualization page

It does not expose file access or destructive tool behavior.

## Development notes

The default viewer uses **globe.gl** from a CDN to stay small and easy to hack on. If you want an entirely offline stack or more advanced globe features later, you can swap the viewer for Cesium or a bundled Three.js build.

## License

MIT


## Native window behavior

If you want the tool to open a desktop window instead of returning only a browser URL, the MCP tools support an `open_in_window` flag. For example, an agent can call `resolve_and_show` with:

```json
{
  "places": ["Tokyo"],
  "open_in_window": true
}
```

GeoPin will spawn a separate native window that loads the local 3D globe view.
