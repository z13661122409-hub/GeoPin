# API Notes

## MCP tools

### resolve_place
Input:

```json
{"place_text": "Tokyo"}
```

Output:

```json
{
  "query": "Tokyo",
  "resolved_name": "Tokyo, Japan",
  "lat": 35.6762,
  "lng": 139.6503,
  "confidence": 0.99,
  "source": "nominatim"
}
```

### show_pin
Input:

```json
{
  "points": [
    {"label": "Tokyo", "lat": 35.6762, "lng": 139.6503}
  ]
}
```

Output:

```json
{
  "viewer_url": "http://127.0.0.1:4173/viewer?session=abc123",
  "session_id": "abc123",
  "mode": "3d_globe"
}
```

### resolve_and_show
Input:

```json
{"places": ["Tokyo", "Columbus, Ohio"]}
```

Output:

```json
{
  "resolved_points": [...],
  "viewer_url": "http://127.0.0.1:4173/viewer?session=abc123",
  "session_id": "abc123",
  "mode": "3d_globe"
}
```

## Viewer HTTP endpoints

### GET /healthz
Health check.

### GET /viewer
Serves the globe viewer page.

### GET /api/sessions/{session_id}
Returns a stored viewer session.


## Desktop window mode

Both `show_pin` and `resolve_and_show` accept an optional `open_in_window: boolean` flag. When true, GeoPin opens the local viewer in a native desktop window using pywebview.
