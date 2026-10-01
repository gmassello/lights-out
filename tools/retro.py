#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

from validate_room import REPLIES, STATES, VERDICTS

USAGE = "usage: retro.py <room.json> | --self-check"
PATH = re.compile(r"(?<![\w/])/[\w{}.-]+(?:/[\w{}.-]+)*")
IDENT = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b|\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b")
PROTOCOL = {w for w in STATES | VERDICTS | REPLIES}


def kind(m):
    return str(m.get("senderType", "")).lower()


def lessons(messages):
    found = {}
    for m in messages:
        if m.get("messageType") != "text" or kind(m) != "agent":
            continue
        for raw in str(m.get("content") or "").splitlines():
            line = raw.strip()
            if line.startswith("LESSON ") and line != "LESSON none":
                found.setdefault(m.get("senderName") or m.get("senderId"), []).append(line)
    return found


def suspects(lesson, dispatch):
    text = lesson.split(" (evidence:")[0]
    terms = set(re.findall(r"`([^`]+)`", dispatch)) | set(PATH.findall(dispatch))
    hits = [t for t in sorted(terms) if t in text]
    hits += [t for t in PATH.findall(text) + IDENT.findall(text) if t not in PROTOCOL and t not in hits]
    return hits


def report(room):
    messages = room.get("messages") if isinstance(room, dict) else None
    if not isinstance(messages, list):
        raise ValueError("expected an object whose `messages` is a list")
    dispatch = next((str(m.get("content") or "") for m in messages
                     if m.get("messageType") == "text" and kind(m) not in ("agent", "system")), "")
    found = lessons(messages)
    rows, total, flagged = [], 0, 0
    for seat, items in found.items():
        rows.append(f"{seat}:")
        for lesson in items:
            hits = suspects(lesson, dispatch)
            total += 1
            flagged += bool(hits)
            rows.append(f"  {lesson}" + (f" [flag: {', '.join(hits)}]" if hits else ""))
    return [f"retro: {total} lessons from {len(found)} seats, {flagged} flagged"] + rows


def self_check():
    import unittest
    root = Path(__file__).resolve().parent.parent
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_retro.py", top_level_dir=str(root))
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main(argv):
    if argv == ["--self-check"]:
        return 0 if self_check() else 1
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        out = report(json.loads(Path(argv[0]).read_text()))
    except (OSError, ValueError) as exc:
        print(f"retro: cannot read {argv[0]}: {exc}", file=sys.stderr)
        return 2
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
