# TTS and Transcription

Use this reference when preparing narration and timestamps.

## Multi-Speaker Script

Write the script before generating audio. Keep it close to the target runtime and include delivery tags inline.

```json
{
  "model_id": "eleven_v3",
  "inputs": [
    {
      "speaker": "Female lead",
      "voice_id": "FEMALE_VOICE_ID",
      "text": "[calm, confident] You've built a deck. Now imagine it knows when to speak. [pause]"
    },
    {
      "speaker": "Male cohost",
      "voice_id": "MALE_VOICE_ID",
      "text": "[warmly] Not a screen recording. The slides, narration, and timing are authored together. [pause]"
    }
  ]
}
```

Useful tags:

- `[pause]` for slide handoffs and pacing.
- `[calm]`, `[confident]`, `[excited]`, `[awe]`, `[dramatic tone]` for delivery.
- `[whispers]`, `[rushed]`, `[drawn out]`, `[interrupting]`, `[overlapping]` when the performance needs contrast.

Keep a generated payload file next to the audio, but never include API keys.

## ElevenLabs Generation Notes

Use an environment variable for the API key:

```bash
export ELEVENLABS_API_KEY="..."
```

When using the HTTP API, send the payload to the text-to-dialogue endpoint and write either the returned audio bytes or decoded base64 audio to disk. Version outputs:

```text
dialogue-v1.mp3
dialogue-v1.payload.json
dialogue-v2-selected-voices.mp3
dialogue-v2-selected-voices.payload.json
```

If the selected voice changes the runtime, regenerate or add explicit `[pause]` tags. Do not assume the old cue map still fits.

## Whisper Transcription

Prefer HyperFrames CLI:

```bash
npx hyperframes transcribe dialogue-final.mp3 --model base.en --language en
```

Fallback to Whisper CLI when local wrapper flags are incompatible:

```bash
whisper dialogue-final.mp3 \
  --model base.en \
  --language en \
  --output_format json \
  --word_timestamps True \
  --fp16 False \
  --output_dir .
```

The output JSON should contain `segments[]`, and ideally each segment includes `words[]` with `start` and `end` times.

## Cue Anchoring

Create scene boundaries from transcript phrases:

- First scene starts at `0`.
- A scene can start slightly before the transcript phrase that introduces it.
- A scene should end at the next scene start unless there is a deliberate hold.
- For data showcase slides, align the visual proof point to the phrase that names it, for example "a world sales map" or "Europe opening into country detail."
