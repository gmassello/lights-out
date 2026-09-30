#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

CLOSER = "coordinator"
USAGE = ("usage: watchdog.py <room-id> --seats a,b,c [--wait 600] [--interval 30] [--dry-run [--now ISO]]"
         " | --self-check")


def when(text):
    value = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def last_line(content):
    lines = [l.strip() for l in str(content or "").splitlines() if l.strip()]
    return lines[-1] if lines else ""


def mentioned(m, seats):
    names = (m.get("mention_names") or {}).values()
    return [n for n in names if n in seats and n != m.get("sender_name")]


def expected(m, seats):
    last = last_line(m.get("content"))
    if last == "DONE":
        return []
    found = re.fullmatch(r"NEXT @(?:\[\[(.+)\]\]|(?:\S+/)?(\S+))", last)
    if not found:
        return mentioned(m, seats)
    name = (m.get("mention_names") or {}).get(found.group(1)) if found.group(1) else found.group(2)
    return [name] if name in seats and name != m.get("sender_name") else []


def due(messages, now, wait, seats):
    msgs = sorted((m for m in messages if when(m["inserted_at"]) <= now),
                  key=lambda m: m["inserted_at"])
    out = []
    for i, m in enumerate(msgs):
        if m.get("message_type") != "text" or m.get("sender_name") not in seats:
            continue
        for seat in expected(m, seats):
            later = [x for x in msgs[i + 1:] if x.get("sender_name") == seat
                     and x.get("message_type") != "participant"]
            if any(x.get("message_type") == "text" for x in later):
                continue
            last = when(later[-1]["inserted_at"]) if later else when(m["inserted_at"])
            if now - last > timedelta(seconds=wait):
                out.append((seat, m["id"]))
    return out


def finished(messages, seats):
    return any(m.get("message_type") == "text" and m.get("sender_name") == CLOSER
               and last_line(m.get("content")) == "DONE" and m.get("mention_names")
               and not mentioned(m, seats)
               for m in messages)


def fetch(room, since):
    messages, page = [], 1
    while True:
        out = subprocess.run(["band", "room", "messages", room, "--json", "--page", str(page)],
                             capture_output=True, text=True, timeout=60)
        data = json.loads(out.stdout)
        batch = data.get("messages", [])
        messages += batch
        if not data.get("has_more") or not batch or min(when(m["inserted_at"]) for m in batch) < since:
            return messages
        page += 1


def log(text):
    print(f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} {text}", flush=True)


def run(args):
    seats = set(args.seats.split(","))
    done = set()
    log(f"watching room {args.room} seats={','.join(sorted(seats))} wait={args.wait}s"
        f"{' dry-run' if args.dry_run else ''}")
    while True:
        now = when(args.now) if args.now else datetime.now(timezone.utc)
        try:
            messages = fetch(args.room, now - timedelta(seconds=3 * args.wait))
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            log(f"poll failed: {exc}")
            time.sleep(args.interval)
            continue
        for seat, mid in due(messages, now, args.wait, seats):
            if (seat, mid) in done:
                continue
            done.add((seat, mid))
            cmd = ["band", "restart", "--session", f"lo-{seat}", "--host-session", f"default-{args.room}"]
            if args.dry_run:
                log(f"due {seat} message {mid}: would run {' '.join(cmd)}")
                continue
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            log(f"due {seat} message {mid}: ran {' '.join(cmd)} exit={res.returncode}")
        if args.dry_run:
            return 0
        if finished(messages, seats):
            log("run outcome posted; exiting")
            return 0
        time.sleep(args.interval)


def self_check():
    import unittest
    root = Path(__file__).resolve().parent.parent
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_watchdog.py", top_level_dir=str(root))
    return unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()


def main(argv):
    if argv == ["--self-check"]:
        return 0 if self_check() else 1
    p = argparse.ArgumentParser(usage=USAGE)
    p.add_argument("room")
    p.add_argument("--seats", required=True)
    p.add_argument("--wait", type=int, default=600)
    p.add_argument("--interval", type=int, default=30)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--now")
    args = p.parse_args(argv)
    if args.now and not args.dry_run:
        p.error("--now only with --dry-run")
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
