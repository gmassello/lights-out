import unittest
from datetime import datetime, timedelta, timezone

from watchdog import due, finished

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


if __name__ == "__main__":
    unittest.main()
