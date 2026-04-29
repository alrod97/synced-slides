# Data Showcases

Use this reference when the presentation includes maps, charts, dashboards, or other browser-rendered data surfaces.

## Principle

HTML can render real data surfaces, but they must be visible in the final MP4. Verify rendered frames, not just the browser.

## Maps

- Prefer D3 plus local TopoJSON/GeoJSON assets for deterministic renders.
- Load local geography synchronously before building the GSAP timeline.
- Avoid fetching map data at render time.
- Use separate CSS for global and zoomed/detail map states.
- Keep land, borders, and graticules visibly darker than the card background.
- Confirm labels do not obscure the geography.

Minimum contrast guidance for light decks:

```css
.map-frame { background: #fbfbfd; }
.map-country { fill: #dfe4ea; stroke: #b7c0ca; stroke-width: 0.55; }
.map-boundary { stroke: #8f99a6; stroke-width: 0.85; opacity: 0.92; }
.map-graticule { stroke: #c5ccd6; opacity: 0.58; }
```

## Charts

- Use SVG/canvas generated from local data or inline JSON.
- Animate marks after axes and labels are already readable.
- Keep numeric labels large enough to survive video compression.
- Sample frames at the moment each chart is introduced.

## Timing

Data details should appear when the narration names them. Example:

- "A world sales map" -> global map and region bubbles are visible.
- "Europe opening into country detail" -> begin the world-to-Europe transition.
- "Numbers moving exactly when..." -> country values and mini table are visible.

## QA

For every data slide, extract at least two frames:

```bash
ffmpeg -y -v error -ss 90.5 -i renders/final.mp4 -frames:v 1 snapshots/world-map.png
ffmpeg -y -v error -ss 94.5 -i renders/final.mp4 -frames:v 1 snapshots/europe-detail.png
```

Open the images and check:

- The data surface is not blank.
- Land/chart marks are visible against the background.
- Labels and values are readable.
- No table, callout, or text overlaps the primary data.
