# Tiny case — run 6 (1 Oct 2026)

Same brief and practice fault as tiny runs 4 and 5, plus the new `Mandates directory:` line, so
coordinator step 9 can edit each seat's `## Lessons`. First run with the push rule (the coordinator
pushes exactly the accepted sha, the reviewer does not commit during a review). The runtime was
stopped before the dispatch. The room was created from the web app with the human as owner, and
the dispatch was posted as the human. No seat was restarted.

## Timeline (UTC)

| Time | Event |
|---|---|
| 23:16:48 | human dispatch; first message checked: repository `tiny-run-6`, mandates directory of this repository |
| 23:17:03 | coordinator → environment, one send with the full mention token |
| 23:17:15 | environment posts its starting-state record |
| 23:17:39 | environment → coordinator: `completed` |
| 23:17:50 | coordinator → reviewer: checks first |
| 23:19:42 | reviewer commits checks `141a69f` |
| 23:19:56 | coordinator → builder, one message |
| 23:20:41 | builder hands off `093e4dd` with the seeded fault |
| 23:22:27 | reviewer REJECT on `093e4dd` (C-03, C-04, C-11) |
| 23:23:15 | builder hands off repair `0bbce61` |
| 23:25:10 | reviewer ACCEPT on `0bbce61` |
| 23:25:25 | coordinator closes stage 1 and pushes `0bbce61` (`origin/main` is the accepted sha) |
| 23:25:47 | environment: final check on `0bbce61` completed, runtime stopped again as found |
| 23:25:58 | coordinator → human: run outcome, `DONE`; retro requests to the three seats |
| 23:26:04–08 | the four retros |
| 23:26:09–25 | coordinator posts three `retro-apply` records and edits the mandates |
| watchdog | exits on the outcome, no restarts |

Run time: 9 min 8 s from the validator. Human messages: 1.

## Runs with the same brief

| Measure | Run 4 | Run 5 | Run 6 |
|---|---|---|---|
| Lessons in the mandates at dispatch | 0 | 9 | 9 |
| Reviewer, request → checks commit | 2:02 | 2:14 | 1:52 |
| Handoff → REJECT | 2:08 | 2:01 | 1:46 |
| REJECT → repair | 0:21 | 0:32 | 0:48 |
| Repair handoff → ACCEPT | 1:44 | 1:38 | 1:55 |
| Review rounds | 1 REJECT, 1 ACCEPT | 1 REJECT, 1 ACCEPT | 1 REJECT, 1 ACCEPT |
| Run time | 9:44 | 9:20 | 9:08 |
| Validator problems (current validator) | 0 | 2 (push) | 0 |
| Output tokens, Claude seats | 55,643 | 52,725 | 52,407 |
| Output tokens, Codex | 6,587 | 6,851 | 11,041 |

Run time went down by 36 s over three runs with the same brief. Each step moves by tens of seconds
in both directions between runs, so a single step is noise; the trend is in the total, and the
fixed costs (checks over 1:50, two dual reviews near 2 min each) still dominate.

## The two reviews

| Candidate | Claude subagent | Codex | Merged verdict |
|---|---|---|---|
| `093e4dd` (seeded fault) | 13 CONFORMS, 3 DEVIATES | 14 CONFORMS, 2 DEVIATES (missed C-03) | REJECT C-03, C-04, C-11; own run 13 CONFORMS, 3 DEVIATES |
| `0bbce61` (repair) | — | — | ACCEPT |

Three Codex rollouts for two candidates: the first review was launched twice four seconds apart (the
reviewer's lesson on background launches comes from it).

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: stages closed 1/1, verdicts 2, rejections repaired 1/1, 1 human message, run time 0:09:08, 0 problems |
| Push | `git ls-remote origin main` | `0bbce61`, the accepted sha |
| Watchdog | `tiny-run-6.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy |
| Retro | `tools/retro.py room.json` | 7 lessons from 3 seats (environment: none), 0 flagged |
| Lessons applied by the coordinator | `git diff mandates/` | 6 new lines, all inside `## Lessons`: builder 1, coordinator 1, reviewer 4; one builder lesson merged with an existing one; common block shasum unchanged; mandate gate clean |
| Cost in the run window | `tools/measure_cost.py 23:16:48 23:25:58 … codex=<3 rollouts>` | output tokens: coordinator 8,830, builder 11,076, reviewer 29,189 (with its subagents), environment 3,312, Codex 11,041 (73,660 uncached input) |

## Lessons applied by the coordinator

| Seat | Applied | Merged or dropped |
|---|---|---|
| builder | one handler and error format for every request the framework can receive, unlisted methods and malformed headers included | the "list the checks a seeded defect will fail" lesson was already there: merged |
| coordinator | full `@<owner>/<handle>` mention from the first send | — |
| reviewer | full mention form; the tool's own background mode for long reviews; every variant of "unknown X is rejected" plus malformed input; merge all reviews and confirm every DEVIATES | — |
| environment | — (`LESSON none`) | — |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| Coordinator step 9 works: with the mandates directory in the dispatch, it edited only `## Lessons`, wrote generic rules and posted one `retro-apply` per seat | `git diff mandates/`, records #306, #334, #336 | resolved by the run 5 amendment |
| The push rule works: `origin/main` is the accepted sha and the final check names it | `git ls-remote`, message #250 | resolved by the run 5 amendment |
| The reviewer launched the first Codex review twice | three rollouts for two candidates | lesson applied by the coordinator (reviewer) |
