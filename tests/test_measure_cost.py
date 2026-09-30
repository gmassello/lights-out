import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import measure_cost
from measure_cost import main, measure

START, END = "2026-09-28T10:00:00Z", "2026-09-28T11:00:00Z"


def line(mid, ts, out=10):
    return {"timestamp": ts, "message": {"id": mid, "usage": {
        "input_tokens": 1, "output_tokens": out,
        "cache_read_input_tokens": 100, "cache_creation_input_tokens": 5}}}


class MeasureCost(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, lines):
        path = Path(self.tmp.name) / f"{name}.jsonl"
        path.write_text("\n".join(json.dumps(l) for l in lines))
        return path

    def test_split_message_counted_once_and_outside_window_excluded(self):
        path = self.write("builder", [line("m1", "2026-09-28T10:01:00Z"),
                                      line("m1", "2026-09-28T10:01:01Z"),
                                      line("m1", "2026-09-28T10:01:02Z"),
                                      line("m2", "2026-09-28T10:30:00Z", 20),
                                      line("m3", "2026-09-28T12:00:00Z", 999)])
        out = measure(START, END, [f"builder={path}"])
        self.assertIn("builder: input=2 output=30 cache_read=200 cache_creation=10 active=0:29:00", out[1])

    def test_idle_seat_is_zero_without_partial(self):
        path = self.write("reviewer", [line("r1", "2026-09-28T09:00:00Z")])
        out = measure(START, END, [f"reviewer={path}"])
        self.assertEqual(out[1], "reviewer: input=0 output=0 cache_read=0 cache_creation=0 active=0:00:00")

    def test_transcript_without_usage_is_partial(self):
        path = self.write("coordinator", [{"timestamp": "2026-09-28T10:05:00Z",
                                           "message": {"id": "c1", "content": "x"}}])
        out = measure(START, END, [f"coordinator={path}"])
        self.assertTrue(out[1].endswith("partial"), out)
        self.assertTrue(out[0].endswith("partial"), out)

    def test_codex_rollout_adds_uncached_input(self):
        claude = self.write("verifier", [line("v1", "2026-09-28T10:02:00Z")])
        codex = self.write("rollout", [
            {"timestamp": "2026-09-28T10:10:00Z", "ordinal": 0, "type": "session_meta", "payload": {"cwd": "/r"}},
            {"timestamp": "2026-09-28T10:10:05Z", "ordinal": 7, "type": "event_msg",
             "payload": {"type": "token_count", "info": {"last_token_usage": {
                 "input_tokens": 300, "cached_input_tokens": 100, "cache_write_input_tokens": 0,
                 "output_tokens": 40}}}},
            {"timestamp": "2026-09-28T10:10:06Z", "ordinal": 8, "type": "event_msg",
             "payload": {"type": "token_count", "info": None}}])
        out = measure(START, END, [f"verifier={claude},{codex}"])
        self.assertIn("verifier: input=201 output=50 cache_read=200 cache_creation=5 active=0:08:05", out[1])

    def test_band_seat_without_session_in_window_is_partial(self):
        stale = self.write("stale", [line("s1", "2026-09-27T10:00:00Z")])
        with mock.patch.object(measure_cost, "band_sessions", lambda seat: [{"sessionId": str(stale)}]):
            out = measure(START, END, ["reviewer"])
        self.assertTrue(out[1].endswith("partial: no band session in the window"), out)
        self.assertTrue(out[0].endswith("partial"), out)

    def test_exit_codes(self):
        path = self.write("coordinator", [line("c1", "2026-09-28T10:05:00Z")])
        self.assertEqual(main([START, END, f"coordinator={path}"]), 0)
        self.assertEqual(main(["nope", END, f"coordinator={path}"]), 2)


if __name__ == "__main__":
    unittest.main()
