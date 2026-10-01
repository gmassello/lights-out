import subprocess
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

from watchdog import due, finished, restart

SEATS = {"coordinator", "builder", "environment"}
T0 = datetime(2026, 9, 29, 22, 0, tzinfo=timezone.utc)
AT = T0 + timedelta(seconds=700)


def msg(mid, sec, sender, kind="text", to=(), content="x"):
    return {"id": mid, "inserted_at": (T0 + timedelta(seconds=sec)).isoformat(),
            "sender_name": sender, "message_type": kind, "content": content,
            "mention_names": {f"id-{n}": n for n in to}}


ASK = msg("m1", 0, "coordinator", to=["environment"])


class Due(unittest.TestCase):
    def test_idle_seat_is_due(self):
        self.assertEqual(due([ASK], AT, 600, SEATS), [("environment", "m1")])

    def test_answered_seat_is_not_due(self):
        reply = msg("r", 30, "environment", to=["coordinator"])
        self.assertNotIn(("environment", "m1"), due([ASK, reply], AT, 600, SEATS))

    def test_busy_seat_is_not_due(self):
        self.assertEqual(due([ASK, msg("t", 400, "environment", kind="tool_call")], AT, 600, SEATS), [])

    def test_early_is_not_due(self):
        self.assertEqual(due([ASK], T0 + timedelta(seconds=300), 600, SEATS), [])

    def test_human_mention_is_not_due(self):
        self.assertEqual(due([msg("h", 0, "coordinator", to=["Germán"])], AT, 600, SEATS), [])

    def test_only_the_next_seat_is_due(self):
        verdict = msg("v", 0, "environment", to=["builder", "coordinator"],
                      content="REJECT\nSTATE REJECT stage=1 sha=a\nNEXT @[[id-builder]]")
        self.assertEqual(due([verdict], AT, 600, SEATS), [("builder", "v")])

    def test_done_with_mention_is_not_due(self):
        closing = msg("d", 0, "environment", to=["coordinator"], content="clean\nSTATE completed\nDONE")
        self.assertEqual(due([closing], AT, 600, SEATS), [])

    def test_done_before_a_fence_is_not_due(self):
        closing = msg("f", 0, "environment", to=["coordinator"], content="clean\nSTATE completed\nDONE\n```")
        self.assertEqual(due([closing], AT, 600, SEATS), [])

    def test_plain_next_handle_is_due(self):
        handoff = msg("p", 0, "coordinator", to=["builder", "environment"],
                      content="go\nSTATE working stage=1\nNEXT @gmassello/builder")
        self.assertEqual(due([handoff], AT, 600, SEATS), [("builder", "p")])

    def test_human_dispatch_is_due(self):
        dispatch = msg("h", 0, "Germán", to=["coordinator"], content="brief\nResult repository: /r")
        self.assertEqual(due([dispatch], AT, 600, SEATS), [("coordinator", "h")])

    def test_answered_dispatch_is_not_due(self):
        dispatch = msg("h", 0, "Germán", to=["coordinator"], content="brief")
        reply = msg("r", 30, "coordinator", to=["environment"])
        self.assertNotIn(("coordinator", "h"), due([dispatch, reply], AT, 600, SEATS))

    def test_reply_after_now_is_ignored(self):
        late = msg("late", 800, "environment", to=["coordinator"])
        self.assertIn(("environment", "m1"), due([ASK, late], AT, 600, SEATS))


class Finished(unittest.TestCase):
    def test_handoff_does_not_finish(self):
        self.assertFalse(finished([ASK], SEATS))

    def test_coordinator_outcome_to_human_finishes(self):
        outcome = msg("o", 5, "coordinator", to=["Germán"], content="done\nSTATE x\nDONE")
        self.assertTrue(finished([outcome], SEATS))

    def test_environment_record_does_not_finish(self):
        record = msg("e", 5, "environment", content="state\nSTATE working task=env-prepare\nDONE")
        self.assertFalse(finished([record], SEATS))

    def test_stage_close_without_mention_does_not_finish(self):
        close = msg("s", 5, "coordinator", content="stage closed\nSTATE completed stage=1\nDONE")
        self.assertFalse(finished([close], SEATS))

    def test_other_seat_done_to_human_does_not_finish(self):
        other = msg("b", 5, "builder", to=["Germán"], content="x\nSTATE x\nDONE")
        self.assertFalse(finished([other], SEATS))


class Restart(unittest.TestCase):
    CMD = ["band", "restart", "--session", "lo-builder"]

    def test_exit_code_is_reported(self):
        with mock.patch("watchdog.subprocess.run", return_value=subprocess.CompletedProcess(self.CMD, 0)):
            self.assertEqual(restart(self.CMD), "exit=0")

    def test_timeout_is_reported(self):
        with mock.patch("watchdog.subprocess.run", side_effect=subprocess.TimeoutExpired(self.CMD, 120)):
            self.assertTrue(restart(self.CMD).startswith("failed:"))

    def test_missing_band_is_reported(self):
        with mock.patch("watchdog.subprocess.run", side_effect=FileNotFoundError("band")):
            self.assertTrue(restart(self.CMD).startswith("failed:"))


if __name__ == "__main__":
    unittest.main()
