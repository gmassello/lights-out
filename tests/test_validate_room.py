import subprocess
import tempfile
import unittest

from validate_room import validate


def msg(sender, text, kind="agent"):
    return {"senderId": sender, "senderName": sender, "senderType": kind,
            "messageType": "text", "content": text}


def line(state, sha, nxt):
    return f"body\nSTATE {state} stage=1 task=t sha={sha}\n{nxt}"


class ValidateRoom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        repo = cls.tmp.name
        git = ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", repo], check=True)
        shas = []
        for n in range(3):
            subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", str(n)], check=True)
            shas.append(subprocess.run(git + ["rev-parse", "HEAD"], capture_output=True,
                                       text=True, check=True).stdout.strip())
        cls.checks, cls.bad, cls.good = shas
        cls.base = [msg("h", "brief", "user"),
                    msg("c", "@[[r]] checks please\nSTATE working stage=1 task=t\nNEXT @[[r]]"),
                    msg("r", line("completed", cls.checks, "NEXT @[[c]]")),
                    msg("b", line("completed", cls.bad, "NEXT @[[r]]")),
                    msg("r", "@[[b]] " + line("REJECT", cls.bad, "NEXT @[[b]]")),
                    msg("b", line("completed", cls.good, "NEXT @[[r]]")),
                    msg("r", "@[[c]] " + line("ACCEPT", cls.good, "NEXT @[[c]]"))]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_room(self, messages):
        return validate({"messages": messages}, self.tmp.name)

    def test_happy(self):
        out, problems = self.run_room(self.base)
        self.assertEqual(problems, [])
        self.assertIn("stages closed 1/1", out[0])
        self.assertTrue(any(f"REJECT {self.bad}" in x and self.good in x for x in out), out)

    def test_self_accept(self):
        messages = self.base[:4] + [msg("b", "@[[c]] " + line("ACCEPT", self.bad, "NEXT @[[c]]"))]
        _, problems = self.run_room(messages)
        self.assertTrue(any("stage 1: open" in x for x in problems), problems)

    def test_missing_sha(self):
        messages = self.base[:-1] + [msg("r", "@[[c]] " + line("ACCEPT", "f" * 40, "NEXT @[[c]]"))]
        _, problems = self.run_room(messages)
        self.assertTrue(any("message #6 from r" in x and "is not a commit" in x for x in problems), problems)

    def test_two_humans(self):
        _, problems = self.run_room(self.base + [msg("h", "go on", "user")])
        self.assertEqual(problems, ["2 human messages; the run allows exactly one"])

    def test_env_with_stage(self):
        messages = [self.base[0],
                    msg("c", "@[[e]] ready\nSTATE working stage=0 task=env-prepare\nNEXT @[[e]]"),
                    msg("e", "@[[c]] ok\nSTATE completed task=env-prepare\nNEXT @[[c]]")] + self.base[1:]
        _, problems = self.run_room(messages)
        self.assertEqual(problems, ["message #1 from c: environment message with stage="])

    def test_env_without_stage(self):
        messages = [self.base[0],
                    msg("c", "@[[e]] ready\nSTATE working task=env-prepare\nNEXT @[[e]]"),
                    msg("e", "@[[c]] ok\nSTATE completed task=env-prepare\nNEXT @[[c]]")] + self.base[1:]
        _, problems = self.run_room(messages)
        self.assertEqual(problems, [])

    def test_mention_with_done(self):
        messages = self.base[:-1] + [msg("r", "@[[c]] " + line("ACCEPT", self.good, "DONE"))]
        out, problems = self.run_room(messages)
        self.assertEqual(problems, ["message #6 from r: mentions a seat but ends with DONE"])
        self.assertIn("stages closed 1/1", out[0])
        self.assertIn("rejections repaired 1/1", out[0])

    def test_done_without_mention(self):
        messages = self.base + [msg("e", "state recorded\nSTATE working task=env-prepare\nDONE")]
        _, problems = self.run_room(messages)
        self.assertEqual(problems, [])

    def test_env_stage_with_done(self):
        messages = self.base + [msg("e", "@[[c]] clean\nSTATE completed stage=1 task=env-check\nDONE")]
        _, problems = self.run_room(messages)
        self.assertTrue(any("ends with DONE" in x for x in problems), problems)
        self.assertTrue(any("with stage=" in x for x in problems), problems)

    def test_short_and_full_sha_match(self):
        messages = self.base[:5] + [msg("b", line("completed", self.good[:7], "NEXT @[[r]]")), self.base[6]]
        out, problems = self.run_room(messages)
        self.assertEqual(problems, [])
        self.assertIn("stages closed 1/1", out[0])

    def test_same_commit_is_not_a_repair(self):
        messages = (self.base[:3] + [msg("b", line("completed", self.bad[:7], "NEXT @[[r]]")),
                                     msg("r", "@[[b]] " + line("REJECT", self.bad[:7], "NEXT @[[b]]")),
                                     msg("r", "@[[c]] " + line("ACCEPT", self.bad, "NEXT @[[c]]"))])
        out, problems = self.run_room(messages)
        self.assertIn("rejections repaired 0/1", out[0])
        self.assertTrue(any("has no repair" in x for x in problems), problems)

    def test_update_without_sha(self):
        messages = (self.base[:5] + [msg("b", "@[[r]] still working\nSTATE working stage=1 task=t\nNEXT @[[r]]")]
                    + self.base[5:])
        out, problems = self.run_room(messages)
        self.assertEqual(problems, [])
        self.assertIn("rejections repaired 1/1", out[0])


if __name__ == "__main__":
    unittest.main()
