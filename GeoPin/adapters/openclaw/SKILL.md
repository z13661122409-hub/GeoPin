---
name: geopin
description: Show places on a 3D globe by resolving place names into coordinates and opening a local viewer with pins.
metadata:
  openclaw:
    requires:
      bins: []
      config: []
---

# GeoPin Skill

Use GeoPin when the user asks where a place is, asks to mark a place on a globe, or would clearly benefit from a visual location display.

## Use this skill when

- the user asks where a city, country, landmark, school, or named place is
- the user asks to show a place on a globe or map
- the user asks to compare the positions of two or more places
- a visual location display would make the answer more intuitive

## Prefer this tool

Use `resolve_and_show` first.

It is the default path because it keeps token usage low and returns both the resolved coordinates and the local viewer URL in one step.

## Example prompts that should trigger GeoPin

- Where is Tokyo?
- Show Ohio State University on a globe.
- Mark Beijing and Columbus for me.
- Give me a visual for where Brazil is.

## Example prompts that should not trigger GeoPin by default

- What is the population of Tokyo?
- What is the weather in Japan?
- How do I drive from Beijing to Shanghai?

## Tool guidance

### resolve_and_show
Use this for almost all normal place-visualization requests.

Input shape:

```json
{
  "places": ["Tokyo"]
}
```

### resolve_place
Use this when you need to inspect or confirm the resolved place before showing it.

### show_pin
Use this only when you already have coordinates.

## Ambiguity handling

If a place is ambiguous, do not pretend the first result is certainly correct.

Instead:

1. inspect the result
2. if the tool signals ambiguity, ask the user which candidate they mean
3. once clarified, call `resolve_and_show` again

## Response style

After using GeoPin, keep the text response brief.

Example:

- I marked it on the globe for you.
- I pinned both places and returned the local viewer link.
- I found an ambiguous result, so I need you to pick the correct Springfield.
