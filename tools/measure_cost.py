#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FIELDS = (("input", "input_tokens", "inputTokens"),
          ("output", "output_tokens", "outputTokens"),
          ("cache_read", "cache_read_input_tokens", "cacheReadTokens"),
          ("cache_creation", "cache_creation_input_tokens", "cacheCreationTokens"))
PROJECTS = Path.home() / ".claude" / "projects"
USAGE = "usage: measure_cost.py <start> <end> <seat|seat=sessionId[,sessionId]|seat=path.jsonl>... | --self-check"


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


def codex_usage(entry):
    payload = entry.get("payload")
    if not isinstance(payload, dict) or payload.get("type") != "token_count" or not entry.get("timestamp"):
        return None
    last = (payload.get("info") or {}).get("last_token_usage")
    if not isinstance(last, dict):
        return None
    cached = int(last.get("cached_input_tokens") or 0)
    return {"input_tokens": int(last.get("input_tokens") or 0) - cached,
            "output_tokens": int(last.get("output_tokens") or 0),
            "cache_read_input_tokens": cached,
            "cache_creation_input_tokens": int(last.get("cache_write_input_tokens") or 0)}


def read(paths):
    seen, has_usage = {}, False
    for path in paths:
        for raw in path.read_text(errors="replace").splitlines():
            try:
                entry = json.loads(raw)
            except ValueError:
                continue
            codex = codex_usage(entry)
            if codex is not None:
                has_usage = True
                seen[f"{path}:{entry.get('ordinal')}"] = (when(entry["timestamp"]), codex)
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
    return seen, has_usage


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
        ids = source.split(",") if source else [s["sessionId"] for s in band]
        reads = {sid: read(transcripts(sid)) for sid in ids}
        merged = {}
        for seen, _ in reads.values():
            for key, item in seen.items():
                merged.setdefault(key, item)
        has_usage = any(h for _, h in reads.values())
        sums, active = totals(merged.values(), start, end)
        for k in grand:
            grand[k] += sums[k]
        flag = "" if has_usage else " partial"
        partial = partial or not has_usage
        if band is not None and active is None:
            flag, partial = " partial: no band session in the window", True
            print(f"measure_cost: no {name} session in band usage covers the window;"
                  f" pass {name}=<session-id>", file=sys.stderr)
        rows.append(f"{name}: {fmt(sums)} active={active or '0:00:00'}{flag}")
        for session in band or []:
            whole, _ = totals(reads[session["sessionId"]][0].values())
            theirs = {n: int(session.get(b) or 0) for n, _, b in FIELDS}
            verdict = "match" if whole == theirs else "mismatch"
            checks.append(f"band {name} {session['sessionId']}: {verdict}"
                          f" transcript[{fmt(whole)}] band[{fmt(theirs)}]")
    summary = (f"measure_cost: window {start.isoformat()} .. {end.isoformat()} ({end - start}),"
               f" {fmt(grand)}{' partial' if partial else ''}")
    return [summary] + rows + checks


def self_check():
    import unittest
    root = Path(__file__).resolve().parent.parent
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_measure_cost.py", top_level_dir=str(root))
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main(argv):
    if argv == ["--self-check"]:
        return 0 if self_check() else 1
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
