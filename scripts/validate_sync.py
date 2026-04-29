#!/usr/bin/env python3
"""Validate a synced-slides cue map."""

import argparse
import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARN: {message}", file=sys.stderr)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not read {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a synced-slides cue map.")
    parser.add_argument("cue_map", type=Path, help="Path to sync-cues.json")
    parser.add_argument("--max-gap", type=float, default=0.75, help="Maximum allowed gap between cues in seconds")
    parser.add_argument("--max-overlap", type=float, default=0.25, help="Maximum allowed cue overlap in seconds")
    args = parser.parse_args()

    path = args.cue_map
    data = load_json(path)
    duration = data.get("duration")
    cues = data.get("cues")

    if not isinstance(duration, (int, float)) or duration <= 0:
        fail("Cue map must include a positive numeric duration")
    if not isinstance(cues, list) or not cues:
        fail("Cue map must include a non-empty cues array")

    base = path.parent
    for key in ("audio", "transcript"):
        value = data.get(key)
        if value and not (base / value).exists():
            warn(f"{key} file does not exist relative to cue map: {value}")

    previous_end = None
    ids = set()
    for index, cue in enumerate(cues):
        label = cue.get("id", f"cue[{index}]")
        if label in ids:
            fail(f"Duplicate cue id: {label}")
        ids.add(label)

        start = cue.get("start")
        end = cue.get("end")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            fail(f"{label} must include numeric start and end")
        if start < 0:
            fail(f"{label} starts before zero")
        if end <= start:
            fail(f"{label} end must be after start")
        if end > duration + 0.1:
            fail(f"{label} ends after duration ({end} > {duration})")

        if previous_end is not None:
            gap = start - previous_end
            if gap > args.max_gap:
                warn(f"Gap before {label}: {gap:.2f}s")
            if gap < -args.max_overlap:
                fail(f"Overlap before {label}: {-gap:.2f}s")
        previous_end = end

        for old_key in ("oldStart", "oldEnd"):
            if old_key in cue and not isinstance(cue[old_key], (int, float)):
                fail(f"{label}.{old_key} must be numeric when present")
        if "oldStart" in cue and "oldEnd" in cue and cue["oldEnd"] <= cue["oldStart"]:
            fail(f"{label} oldEnd must be after oldStart")

    final_gap = duration - previous_end
    if final_gap > args.max_gap:
        warn(f"Final cue ends {final_gap:.2f}s before duration")

    print(f"OK: {len(cues)} cues, duration {duration:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
