---
name: synced-slides
description: Create narrated HyperFrames slide videos synced to voiceover audio using TTS, Whisper transcripts, cue maps, and rendered-video QA.
---

# Synced Slides

## Purpose

Build presentation videos where the HTML slide timeline follows the narration. The deliverable is usually a HyperFrames composition, a generated or provided audio track, a Whisper transcript, a cue map, and a rendered MP4.

Use the existing HyperFrames skill for composition rules and the HyperFrames CLI skill for lint, preview, transcribe, and render commands.

## Workflow

1. Define the narrative.
   - Read any existing `DESIGN.md`, slide HTML, script, transcript, or rendered video.
   - Write or update `DESIGN.md` with style, scene list, target runtime, and timing assumptions.
   - Keep the first screen the actual presentation, not a landing page.

2. Build or inspect the HyperFrames deck.
   - Keep `index.html` as a standalone composition with `data-composition-id`, `data-width`, `data-height`, `data-duration`, `data-start`, and `data-track-index`.
   - Build layout first, then add GSAP entrances and exits.
   - Register the timeline synchronously: `window.__timelines["<composition-id>"] = tl`.

3. Prepare the narration.
   - If generating speech, write a reviewable script first.
   - For ElevenLabs dialogue, use inline performance tags such as `[pause]`, `[calm]`, `[excited]`, `[whispers]`, and `[dramatic tone]`.
   - Store generated payloads as `*-payload.json`, but never store API keys.
   - Keep generated audio filenames versioned, for example `dialogue-v3-final.mp3`.

4. Transcribe the final audio.
   - Prefer `npx hyperframes transcribe audio.mp3 --model base.en --language en`.
   - If the wrapper fails because of a local Whisper binary mismatch, use the Whisper CLI directly with JSON and word timestamps.
   - Save the transcript beside the audio, for example `dialogue-v3-final.json`.

5. Build the sync cue map.
   - Map each scene to transcript phrases, not just proportional duration.
   - Save `sync-cues.json` with the audio filename, total duration, transcript filename, and ordered scene cues.
   - Validate with `scripts/validate_sync.py`.

6. Integrate sync into the composition.
   - Add the narration as a separate `<audio>` element with its own track index.
   - Set the root composition duration to the final audio duration.
   - For an existing deck with hardcoded storyboard times, add a `syncTime()` mapper from old storyboard seconds to Whisper cue seconds.
   - For a new deck, author animation positions directly in audio time.

7. Render and verify.
   - Run `npx hyperframes lint --verbose`.
   - Render a draft first, then standard/high quality.
   - Run `ffprobe` to confirm video and audio durations match.
   - Extract sample frames at cue boundaries and inspect them for blank scenes, tiny maps, overlaps, cropped text, and missing assets.

## Required Artifacts

For a finished synced deck, leave these files in the project:

- `index.html` - HyperFrames composition.
- `DESIGN.md` - style, narrative arc, and actual cue timings.
- `audio-name.mp3` - final narration, unless the repo intentionally excludes generated media.
- `audio-name.json` - Whisper transcript.
- `sync-cues.json` - scene cue map.
- `renders/final.mp4` - rendered output when requested.

## References

- Read `references/hyperframes-sync.md` for the audio tag, cue-map schema, and `syncTime()` pattern.
- Read `references/tts-and-transcription.md` for multi-speaker script generation, ElevenLabs tags, and Whisper commands.
- Read `references/data-showcases.md` when the deck includes interactive maps, charts, or browser-rendered data surfaces.

## Guardrails

- Do not commit API keys, `.env` files, or account-specific voice secrets.
- Do not trust old placeholder timings after audio changes; re-transcribe or rebuild the cue map.
- Do not leave a render session running after the MP4 has completed.
- Do not rely on remote data at render time when a local asset can be bundled.
- Do not make the map or chart too subtle; verify rendered frames, not just the browser preview.
