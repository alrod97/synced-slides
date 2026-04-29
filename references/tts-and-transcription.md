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

## Gemini Multi-Speaker

`gemini-3.1-flash-tts-preview` is the production multi-speaker model. `gemini-2.5-flash-preview-tts` and `gemini-2.5-pro-preview-tts` are also supported. Pass the dialogue as a single prompt with speaker turns inline; voices are bound by speaker name in `speechConfig.multiSpeakerVoiceConfig`.

```json
{
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "multiSpeakerVoiceConfig": {
        "speakerVoiceConfigs": [
          { "speaker": "Joe",  "voiceConfig": { "prebuiltVoiceConfig": { "voiceName": "Charon" } } },
          { "speaker": "Jane", "voiceConfig": { "prebuiltVoiceConfig": { "voiceName": "Kore" } } }
        ]
      }
    }
  }
}
```

### Emotion and delivery

Gemini interprets natural-language directives in the prompt — there is no fixed tag schema. Three layers, combinable:

- Director-style preamble before the transcript: `Read warmly, like a podcast intro.`
- Inline stage directions: `Joe: [whispers] We need to talk.`
- Inline performance cues: `[calm]`, `[excited]`, `[laughs]`, `[shouting]`, `[sighs]`. Many work; treat the list as open-ended and verify on render.

For longer scripts, include an Audio Profile / Scene / Director's Notes preamble before the transcript.

### Prebuilt voices (30)

Zephyr · Puck · Charon · Kore · Fenrir · Leda · Orus · Aoede · Callirrhoe · Autonoe · Enceladus · Iapetus · Umbriel · Algieba · Despina · Erinome · Algenib · Rasalgethi · Laomedeia · Achernar · Alnilam · Schedar · Gacrux · Pulcherrima · Achird · Zubenelgenubi · Vindemiatrix · Sadachbia · Sadaltager · Sulafat

### Python (`google-genai`) example

```python
from google import genai
from google.genai import types
import wave

def write_wave(path, pcm, rate=24000):
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate)
        wf.writeframes(pcm)

client = genai.Client()  # reads GEMINI_API_KEY from env

prompt = """TTS the following conversation between Joe and Jane.
Read warmly, like a podcast intro.
Joe: [calm] You've built a deck. Now imagine it knows when to speak.
Jane: [excited] Slides that present themselves."""

response = client.models.generate_content(
    model="gemini-3.1-flash-tts-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=[
                    types.SpeakerVoiceConfig(
                        speaker="Joe",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon"),
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker="Jane",
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore"),
                        ),
                    ),
                ]
            )
        ),
    ),
)

pcm = response.candidates[0].content.parts[0].inline_data.data
write_wave("dialogue-v1.wav", pcm)
```

### Output format and limits

- Returns 16-bit signed PCM, mono, 24 kHz, base64 under `inline_data.data`. Wrap in WAV (above) or convert with `ffmpeg -f s16le -ar 24000 -ac 1 -i dialogue.pcm dialogue.mp3`.
- 32k-token context per call; no streaming.
- Quality drifts past a few minutes — split long scripts at scene boundaries, then concatenate.
- The model occasionally returns text tokens instead of audio (HTTP 500). Implement retry with backoff.
- Use `GEMINI_API_KEY` from the environment. Never commit keys or generated `*.payload.json` containing voice IDs.

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
