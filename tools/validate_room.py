#!/usr/bin/env python3
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

STATES = {"working", "input-required", "completed", "failed", "refused"}
VERDICTS = {"ACCEPT", "REJECT", "INSUFFICIENT_EVIDENCE"}
REPLIES = {"CONFORMS", "DEVIATES", "DISPUTE", "CLARIFY"}
STATE_LINE = re.compile(r"^STATE (\S+)((?: \w+=(?:\[[^\]]*\]|\S+))*)$")
FIELD = re.compile(r"(\w+)=(\[[^\]]*\]|\S+)")
NEXT_LINE = re.compile(r"^(NEXT @\S+|DONE)$")
USAGE = "usage: validate_room.py <room.json> <repo> | --self-check"


def protocol_lines(content):
    lines = [l.strip() for l in str(content or "").splitlines()]
    return [l for l in lines if l and not l.startswith("```")]


def protocol(content):
    lines = protocol_lines(content)
    if len(lines) < 2:
        return None
    state, nxt = STATE_LINE.match(lines[-2]), NEXT_LINE.match(lines[-1])
    if not state or not nxt or state.group(1) not in STATES | VERDICTS | REPLIES:
        return None
    return {"state": state.group(1), **dict(FIELD.findall(state.group(2))), "next": lines[-1]}


def record(line, sender):
    task, state = line.get("task", ""), line["state"]
    return (task.startswith("retro") or (task == "env-prepare" and state == "working")
            or (sender == "coordinator" and state == "completed" and bool(line.get("stage"))))


def resolve(repo, sha):
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def run_time(messages):
    def at(m):
        return datetime.fromisoformat(str(m["insertedAt"]).replace("Z", "+00:00"))
    texts = [m for m in messages if m.get("messageType") == "text"]
    human = next((m for m in texts if str(m.get("senderType", "")).lower() not in ("agent", "system")), None)
    work = [m for m in texts if str(m.get("senderType", "")).lower() == "agent"
            and not (protocol(m.get("content")) or {}).get("task", "").startswith("retro")]
    if not human or not work or not all(m.get("insertedAt") for m in work + [human]):
        return None
    took = max(at(m) for m in work) - at(human)
    return took - timedelta(microseconds=took.microseconds)


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
        if addresses and line["next"] == "DONE" and not record(line, m.get("senderName")):
            problems.append(f"{where}: mentions a seat but ends with DONE")
        if line.get("task", "").startswith("env-") and line.get("stage"):
            problems.append(f"{where}: environment message with stage=")
            continue
        if line["state"] in VERDICTS and not (line.get("stage") and line.get("sha")):
            problems.append(f"{where}: verdict {line['state']} without stage= and sha=")
            continue
        if line.get("sha"):
            full = resolve(repo, line["sha"])
            if not full:
                problems.append(f"{where}: sha {line['sha']} is not a commit in {repo}")
                continue
            line["sha"] = full
        parsed.append((i, m.get("senderId"), who, line))

    authors = {}
    for i, sender, who, line in parsed:
        sha = line.get("sha")
        if sha and (line["state"] not in VERDICTS or (line["state"] == "ACCEPT" and sha not in authors)):
            authors.setdefault(sha, sender)

    def valid_accept(entry, stage):
        i, sender, who, line = entry
        return (line["state"] == "ACCEPT" and line.get("stage") == stage
                and authors.get(line["sha"]) not in (None, sender))

    stages = sorted({l["stage"] for *_, l in parsed if l.get("stage") not in (None, "0")}, key=str)
    verdicts = [e for e in parsed if e[3]["state"] in VERDICTS and authors.get(e[3]["sha"]) != e[1]]
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

    accepted = {e[3]["sha"] for e in parsed if valid_accept(e, e[3].get("stage"))}
    for i, sender, who, line in parsed:
        if line.get("task") == "env-check" and line.get("sha") and line["sha"] not in accepted:
            problems.append(f"message #{i} from {who}: sha {line['sha']} of task=env-check is not an accepted sha")

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

    timing = run_time(messages)
    if timing:
        details.append(f"run time {timing} (dispatch to outcome)")
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
    if subprocess.run(["git", "-C", argv[1], "rev-parse", "--git-dir"], capture_output=True).returncode != 0:
        print(f"validate_room: {argv[1]} is not a git repository", file=sys.stderr)
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
