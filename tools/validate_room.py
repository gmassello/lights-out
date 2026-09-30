#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from pathlib import Path

STATES = {"working", "input-required", "completed", "failed", "refused"}
VERDICTS = {"ACCEPT", "REJECT", "INSUFFICIENT_EVIDENCE"}
STATE_LINE = re.compile(r"^STATE (\S+)((?: \w+=(?:\[[^\]]*\]|\S+))*)$")
FIELD = re.compile(r"(\w+)=(\[[^\]]*\]|\S+)")
NEXT_LINE = re.compile(r"^(NEXT @\S+|DONE)$")
USAGE = "usage: validate_room.py <room.json> <repo> | --self-check"


def protocol(content):
    lines = [l.strip() for l in str(content or "").splitlines()]
    lines = [l for l in lines if l and not l.startswith("```")]
    if len(lines) < 2:
        return None
    state, nxt = STATE_LINE.match(lines[-2]), NEXT_LINE.match(lines[-1])
    if not state or not nxt or state.group(1) not in STATES | VERDICTS:
        return None
    return {"state": state.group(1), **dict(FIELD.findall(state.group(2)))}


def commit_exists(repo, sha):
    return subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{sha}^{{commit}}"],
                          capture_output=True).returncode == 0


def validate(room, repo):
    messages = room.get("messages") if isinstance(room, dict) else None
    if not isinstance(messages, list):
        raise ValueError("expected an object whose `messages` is a list")
    seats = {m["senderId"] for m in messages
             if m.get("senderId") and str(m.get("senderType", "")).lower() == "agent"}
    problems, parsed, sender_types = [], [], set()
    humans = 0
    for i, m in enumerate(messages):
        kind = str(m.get("senderType", "")).lower()
        sender_types.add(kind)
        if m.get("messageType") != "text":
            continue
        if kind not in ("agent", "system"):
            humans += 1
            continue
        if kind != "agent":
            continue
        content = str(m.get("content") or "")
        who = m.get("senderName") or m.get("senderId")
        where = f"message #{i} from {who}"
        addresses = any(f"@[[{s}]]" in content for s in seats if s != m.get("senderId"))
        if not addresses and not re.search(r"(?m)^\s*STATE ", content):
            continue
        line = protocol(content)
        if line is None:
            problems.append(f"{where}: handoff or verdict without a valid protocol line")
            continue
        if addresses and content.strip().splitlines()[-1].strip() == "DONE":
            problems.append(f"{where}: mentions a seat but ends with DONE")
        if line.get("task", "").startswith("env-") and line.get("stage"):
            problems.append(f"{where}: environment message with stage=")
            continue
        if line["state"] in VERDICTS and not (line.get("stage") and line.get("sha")):
            problems.append(f"{where}: verdict {line['state']} without stage= and sha=")
            continue
        if line.get("sha") and not commit_exists(repo, line["sha"]):
            problems.append(f"{where}: sha {line['sha']} is not a commit in {repo}")
            continue
        parsed.append((i, m.get("senderId"), who, line))

    authors = {}
    for i, sender, who, line in parsed:
        if line.get("sha") and line["state"] not in VERDICTS:
            authors.setdefault(line["sha"], sender)

    def valid_accept(entry, stage):
        i, sender, who, line = entry
        return (line["state"] == "ACCEPT" and line.get("stage") == stage
                and authors.get(line["sha"]) not in (None, sender))

    stages = sorted({l["stage"] for *_, l in parsed if l.get("stage") not in (None, "0")}, key=str)
    verdicts = [e for e in parsed if e[3]["state"] in VERDICTS]
    details, closed = [], 0
    for stage in stages:
        accepts = [e for e in parsed if valid_accept(e, stage)]
        if accepts:
            closed += 1
            e = accepts[-1]
            details.append(f"stage {stage}: closed by ACCEPT from {e[2]} on {e[3]['sha']}")
        else:
            details.append(f"stage {stage}: open")
            problems.append(f"stage {stage}: open, no ACCEPT from a seat other than the author")

    rejects = [e for e in verdicts if e[3]["state"] == "REJECT"]
    repaired = 0
    for i, sender, who, line in rejects:
        fix = next((e for e in parsed if e[0] > i and e[3].get("sha") not in (None, line["sha"])
                    and valid_accept(e, line["stage"])), None)
        if fix:
            repaired += 1
            details.append(f"stage {line['stage']}: REJECT {line['sha']} (message #{i}, {who})"
                           f" repaired by {fix[3]['sha']}")
        else:
            problems.append(f"message #{i} from {who}: REJECT {line['sha']} has no repair")

    if humans != 1:
        problems.append(f"{humans} human messages; the run allows exactly one")
    details.append(f"sender types seen: {', '.join(sorted(sender_types))}")
    summary = (f"validate_room: stages closed {closed}/{len(stages)}, verdicts {len(verdicts)},"
               f" rejections repaired {repaired}/{len(rejects)}, human messages {humans},"
               f" problems {len(problems)}")
    return [summary] + details + [f"PROBLEM {p}" for p in problems], problems


def self_check():
    import unittest
    root = Path(__file__).resolve().parent.parent
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_validate_room.py", top_level_dir=str(root))
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main(argv):
    if argv == ["--self-check"]:
        return 0 if self_check() else 1
    if len(argv) != 2:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        room = json.loads(Path(argv[0]).read_text())
        out, problems = validate(room, argv[1])
    except (OSError, ValueError) as exc:
        print(f"validate_room: cannot read {argv[0]}: {exc}", file=sys.stderr)
        return 2
    print("\n".join(out))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
