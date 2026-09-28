#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

FIELDS = (("input", "input_tokens", "inputTokens"),
          ("output", "output_tokens", "outputTokens"),
          ("cache_read", "cache_read_input_tokens", "cacheReadTokens"),
          ("cache_creation", "cache_creation_input_tokens", "cacheCreationTokens"))
PROJECTS = Path.home() / ".claude" / "projects"
USAGE = "usage: measure_cost.py <start> <end> <seat|seat=sessionId|seat=path.jsonl>... | --self-check"


class UsageError(Exception):
    pass


def when(text):
    try:
        value = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    except ValueError:
        raise UsageError(f"not an ISO 8601 time: {text}")
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def transcripts(session):
    path = Path(session)
    if path.suffix == ".jsonl":
        if not path.is_file():
            raise UsageError(f"no transcript at {path}")
        return [path]
    found = sorted(PROJECTS.glob(f"*/{session}.jsonl")) + sorted(PROJECTS.glob(f"*/{session}/subagents/*.jsonl"))
    if not found:
        raise UsageError(f"no transcript for session {session} under {PROJECTS}")
    return found


def band_sessions(seat):
    try:
        out = subprocess.run(["band", "usage", "sessions", "--agent", seat, "--json"],
                             capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UsageError(f"band usage failed for {seat}: {exc}")
    if out.returncode != 0:
        raise UsageError(f"band usage failed for {seat}: {out.stderr.strip() or out.stdout.strip()}")
    sessions = json.loads(out.stdout).get("sessions", [])
    if not sessions:
        raise UsageError(f"band has no sessions for agent {seat}")
    return sessions


def read(paths):
    seen, has_usage = {}, False
    for path in paths:
        for raw in path.read_text(errors="replace").splitlines():
            try:
                entry = json.loads(raw)
            except ValueError:
                continue
            message = entry.get("message")
            if not isinstance(message, dict) or not entry.get("timestamp"):
                continue
            usage = message.get("usage")
            if isinstance(usage, dict):
                has_usage = True
            key = message.get("id") or f"{path}:{entry.get('uuid')}"
            if key not in seen:
                seen[key] = (when(entry["timestamp"]), usage if isinstance(usage, dict) else {})
    return list(seen.values()), has_usage


def totals(items, start=None, end=None):
    sums = dict.fromkeys((f[0] for f in FIELDS), 0)
    stamps = []
    for stamp, usage in items:
        if start and not (start <= stamp <= end):
            continue
        stamps.append(stamp)
        for name, key, _ in FIELDS:
            sums[name] += int(usage.get(key) or 0)
    active = (max(stamps) - min(stamps)) if stamps else None
    return sums, active


def fmt(sums):
    return " ".join(f"{k}={v}" for k, v in sums.items())


def measure(start, end, seats):
    start, end = when(start), when(end)
    if end < start:
        raise UsageError("end is before start")
    rows, checks, grand, partial = [], [], dict.fromkeys((f[0] for f in FIELDS), 0), False
    for spec in seats:
        name, _, source = spec.partition("=")
        band = None if source else band_sessions(name)
        ids = [source] if source else [s["sessionId"] for s in band]
        paths = [p for sid in ids for p in transcripts(sid)]
        items, has_usage = read(paths)
        sums, active = totals(items, start, end)
        for k in grand:
            grand[k] += sums[k]
        flag = "" if has_usage else " partial"
        partial = partial or not has_usage
        rows.append(f"{name}: {fmt(sums)} active={active or '0:00:00'}{flag}")
        for session in band or []:
            whole, _ = totals(read(transcripts(session["sessionId"]))[0])
            theirs = {n: int(session.get(b) or 0) for n, _, b in FIELDS}
            verdict = "match" if whole == theirs else "mismatch"
            checks.append(f"band {name} {session['sessionId']}: {verdict}"
                          f" transcript[{fmt(whole)}] band[{fmt(theirs)}]")
    summary = (f"measure_cost: window {start.isoformat()} .. {end.isoformat()} ({end - start}),"
               f" {fmt(grand)}{' partial' if partial else ''}")
    return [summary] + rows + checks


def self_check():
    with tempfile.TemporaryDirectory() as tmp:
        def write(name, lines):
            path = Path(tmp) / f"{name}.jsonl"
            path.write_text("\n".join(json.dumps(l) for l in lines))
            return f"{name}={path}"

        def line(mid, ts, out=10):
            return {"timestamp": ts, "message": {"id": mid, "usage": {
                "input_tokens": 1, "output_tokens": out,
                "cache_read_input_tokens": 100, "cache_creation_input_tokens": 5}}}

        split = write("builder", [line("m1", "2026-09-28T10:01:00Z"),
                                  line("m1", "2026-09-28T10:01:01Z"),
                                  line("m1", "2026-09-28T10:01:02Z"),
                                  line("m2", "2026-09-28T10:30:00Z", 20),
                                  line("m3", "2026-09-28T12:00:00Z", 999)])
        idle = write("reviewer", [line("r1", "2026-09-28T09:00:00Z")])
        bare = write("coordinator", [{"timestamp": "2026-09-28T10:05:00Z",
                                      "message": {"id": "c1", "content": "x"}}])
        out = measure("2026-09-28T10:00:00Z", "2026-09-28T11:00:00Z", [split, idle, bare])
        assert out[0].startswith("measure_cost:") and out[0].endswith("partial"), out
        assert "builder: input=2 output=30 cache_read=200 cache_creation=10 active=0:29:00" in out[1], out
        assert out[2].startswith("reviewer: input=0 output=0 cache_read=0 cache_creation=0 active=0:00:00"), out
        assert out[3].endswith("partial"), out
        assert main(["2026-09-28T10:00:00Z", "2026-09-28T11:00:00Z", bare]) == 0
        assert main(["nope", "2026-09-28T11:00:00Z", bare]) == 2
    print("self-check ok: split id once, idle seat zero, no usage partial, outside window excluded")


def main(argv):
    if argv == ["--self-check"]:
        self_check()
        return 0
    if len(argv) < 3:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        print("\n".join(measure(argv[0], argv[1], argv[2:])))
    except (UsageError, OSError, ValueError) as exc:
        print(f"measure_cost: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
