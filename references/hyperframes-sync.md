# HyperFrames Sync Pattern

Use this reference when integrating a final narration track into a HyperFrames presentation.

## Audio Track

Always add narration as a separate audio element. Do not play audio from JavaScript.

```html
<div data-composition-id="presentation"
     data-width="1920"
     data-height="1080"
     data-duration="123.04"
     data-start="0"
     data-track-index="0">

  <audio
    id="narration"
    src="dialogue-final.mp3"
    data-start="0"
    data-duration="123.04"
    data-track-index="1"
    data-volume="1">
  </audio>

  <!-- scenes -->
</div>
```

## Cue Map Schema

Save a cue map as JSON so future agents can inspect or regenerate the timeline.

```json
{
  "audio": "dialogue-final.mp3",
  "duration": 123.04,
  "transcript": "dialogue-final.json",
  "method": "Whisper word timestamps, scene starts anchored to transcript phrases.",
  "cues": [
    {
      "id": "title",
      "selector": ".scene-1",
      "start": 0.0,
      "end": 14.4,
      "oldStart": 0,
      "oldEnd": 10,
      "anchor": "opening premise"
    }
  ]
}
```

`oldStart` and `oldEnd` are only needed when remapping an existing storyboard. For a new deck, author directly in audio time and omit them.

## Remapping Existing Storyboards

When a deck already has many GSAP positions in placeholder time, preserve readability by remapping the timeline positions.

```js
const SYNC_CUES = [
  { sel: ".scene-1", oldStart: 0, oldEnd: 10, start: 0.00, end: 14.40 },
  { sel: ".scene-2", oldStart: 10, oldEnd: 22, start: 14.40, end: 27.20 }
];

function syncTime(storyboardSecond) {
  const cue =
    SYNC_CUES.find(c => storyboardSecond >= c.oldStart && storyboardSecond <= c.oldEnd) ||
    SYNC_CUES[storyboardSecond < SYNC_CUES[0].oldStart ? 0 : SYNC_CUES.length - 1];
  const oldSpan = cue.oldEnd - cue.oldStart;
  if (oldSpan <= 0) return cue.start;
  const progress = Math.max(0, Math.min(1, (storyboardSecond - cue.oldStart) / oldSpan));
  return cue.start + progress * (cue.end - cue.start);
}

["set", "to", "from", "fromTo"].forEach(method => {
  const original = tl[method].bind(tl);
  tl[method] = (...args) => {
    const position = args[args.length - 1];
    if (typeof position === "number") args[args.length - 1] = syncTime(position);
    return original(...args);
  };
});
```

Use this only after creating `tl = gsap.timeline({ paused: true })` and before adding tweens.

## Render QA

Run:

```bash
npx hyperframes lint --verbose
npx hyperframes render --output renders/final.mp4 --quality standard --fps 30
ffprobe -v error -show_entries format=duration -show_streams -of json renders/final.mp4
```

Then sample frames near cue boundaries:

```bash
mkdir -p snapshots/sync-check
for t in 0.8 14.8 30.8 86.9 99.8 118.8; do
  safe=${t//./_}
  ffmpeg -y -v error -ss "$t" -i renders/final.mp4 -frames:v 1 "snapshots/sync-check/frame_${safe}.png"
done
```

Inspect the extracted frames. Catch blank slides, missing maps, wrong scene transitions, unreadable text, and layout overlap before delivering.
