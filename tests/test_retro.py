import json
import tempfile
import unittest
from pathlib import Path

from retro import lessons, main, report


def msg(sender, text, kind="agent"):
    return {"senderId": sender, "senderName": sender, "senderType": kind,
            "messageType": "text", "content": text}


DISPATCH = msg("h", "Build it.\n- `GET /items` lists items\n- `item_count` is an integer", "user")
ROOM = {"messages": [
    DISPATCH,
    msg("builder", "work\nSTATE completed stage=1 task=t sha=abc\nNEXT @reviewer"),
    msg("builder", "LESSON Run every acceptance check before handing off (evidence: #4)\n"
                   "LESSON Return `item_count` as an integer (evidence: [C-03])\n"
                   "STATE completed task=retro\nDONE"),
    msg("reviewer", "LESSON none\nSTATE completed task=retro\nDONE"),
    msg("environment", "LESSON Never touch /items or MISSING_FIELD codes (evidence: #9)\n"
                       "STATE completed task=retro\nDONE"),
]}


class Retro(unittest.TestCase):
    def test_lessons_grouped_by_seat_without_none(self):
        found = lessons(ROOM["messages"])
        self.assertEqual(sorted(found), ["builder", "environment"])
        self.assertEqual(len(found["builder"]), 2)

    def test_domain_terms_are_flagged(self):
        out = report(ROOM)
        self.assertEqual(out[0], "retro: 3 lessons from 2 seats, 2 flagged")
        generic = next(l for l in out if "Run every acceptance check" in l)
        self.assertNotIn("[flag:", generic)
        self.assertTrue(any("item_count" in l and "[flag: item_count]" in l for l in out), out)
        self.assertTrue(any("/items" in l and "[flag:" in l and "MISSING_FIELD" in l.split("[flag:")[1] for l in out), out)

    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "room.json"
            path.write_text(json.dumps(ROOM))
            self.assertEqual(main([str(path)]), 0)
            self.assertEqual(main([]), 2)
            self.assertEqual(main([str(Path(tmp) / "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
