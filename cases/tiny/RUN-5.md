# Tiny case — run 5 (1 Oct 2026)

Same brief and practice fault as tiny run 4, to measure the nine lessons applied after run 4. First
run with the record amendment (a record that ends with `DONE` mentions a seat because the send
command needs one) and with coordinator step 9 (the coordinator reviews each retro and edits the
seat's `## Lessons` itself). The runtime was stopped before the dispatch. The room was created from
the web app with the human as owner, and the dispatch was posted as the human. No seat was restarted.

## Timeline (UTC)

| Time | Event |
|---|---|
| 22:57:45 | human dispatch; first message checked: repository `tiny-run-5` |
| 22:57:58 | coordinator → environment: ready the runtime, with a bare `@environment` (resent at 22:58:08 with the mention token) |
| 22:58:08 | environment posts its starting-state record (missing in run 4) |
| 22:58:37 | environment → coordinator: `completed` |
| 22:58:48 | coordinator → reviewer: checks first |
| 23:01:02 | reviewer commits checks `b9dc921` (C-01..C-14) |
| 23:01:19 | coordinator → builder, one message |
| 23:02:10 | builder hands off `3c580a1` with the seeded fault, listing the checks it will fail (C-03, C-04, C-09) |
| 23:04:11 | reviewer REJECT on `3c580a1` (C-03, C-04, C-09) |
| 23:04:43 | builder hands off repair `d2f5beb` |
| 23:05:02 | reviewer commits `c5f31c9`, a checks-only change to C-05 |
| 23:06:21 | reviewer ACCEPT on `d2f5beb` |
| 23:06:38 | coordinator closes stage 1, mentioning the reviewer |
| 23:06:43 | coordinator pushes `c5f31c9` and asks environment for the final check |
| 23:07:00 | environment: final check completed, runtime stopped again as found |
| 23:07:06 | coordinator → human: run outcome, `DONE` |
| 23:07:10 | coordinator asks the three seats for their retro |
| 23:07:19 | last retro (builder) |
| 23:07:25–30 | coordinator posts three `retro-apply` records: nothing applied (see findings) |
| 23:07:36 | watchdog exits on the outcome, no restarts |

Run time: 9 min 20 s from the validator (tiny run 4: 9 min 44 s). Human messages: 1.

## Against tiny run 4

| Measure | Run 4 | Run 5 |
|---|---|---|
| Acceptance checks | 17 | 14 |
| Reviewer, request → checks commit | 2:02 | 2:14 |
| Coordinator → builder handoff | two parts, out of order | one message |
| Handoff → REJECT | 2:08 | 2:01 |
| REJECT → repair | 0:21 | 0:32 |
| Repair handoff → ACCEPT | 1:44 | 1:38 |
| Review rounds | 1 REJECT, 1 ACCEPT | 1 REJECT, 1 ACCEPT |
| Run time | 9:44 | 9:20 |
| Validator problems | 5 (0 after the record amendment) | 0 |
| Output tokens, Claude seats | 55,643 | 52,725 |
| Output tokens, Codex | 6,587 | 6,851 |

The lessons removed rework that run 4 had (split handoff out of order, blocked commits, a review
rerun on stale code), but the gain is small against the noise of one run: 24 s. The fixed costs
dominate: the reviewer's checks (over 2 min) and two dual reviews (about 2 min each).

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: stages closed 1/1, verdicts 2, rejections repaired 1/1, 1 human message, run time 0:09:20, 0 problems. Re-run after the push rule: exit 1, 2 problems, both "sha c5f31c9… of task=env-check is not an accepted sha" (#267, #281) |
| Watchdog | `tiny-run-5.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy |
| Retro | `tools/retro.py room.json` | 13 lessons from 4 seats, 2 flagged (both false positives, see findings). Re-run after the fix: 1 flagged, "message id" on the dispatch's `id` |
| Mandates after the retro | `git diff mandates/` | no change |
| Cost in the run window | `tools/measure_cost.py 22:57:45 23:07:06 … codex=<2 rollouts>` | output tokens: coordinator 9,524, builder 9,961, reviewer 29,097 (with its subagents), environment 4,143, Codex 6,851 (43,629 uncached input) |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| Coordinator step 9 cannot work: inside a seat, `band agent instructions show --as <handle> --reveal` fails with "detected Jam agents cannot reveal stored instructions or paths", so the coordinator found no mandate file and applied nothing. It reported the gap and its would-apply / drop decisions, as the mandate asks | the three `retro-apply` records, `git diff mandates/` empty | applied: the dispatch names the mandates directory under `Mandates directory:`, next to `Result repository:`, and step 9 edits `<seat>.md` there |
| The record amendment works: the starting-state record was posted, and the stage close, retros and `retro-apply` records pass the validator | validator exit 0 | resolved |
| The builder's lesson from run 4 held: the handoff listed the checks the seeded fault would fail, and the REJECT matched them exactly | builder handoff, REJECT body | lesson effective |
| The coordinator pushed `c5f31c9`, not the accepted `d2f5beb`: the reviewer committed a checks-only change to C-05 during its review, after Codex flagged unlisted methods, and accepted the product commit below it. The product is the accepted one, but the push is not the named sha | `git log`, coordinator outcome | applied: the reviewer does not commit while a candidate is under review, the coordinator pushes exactly the accepted sha (`<sha>:<branch>`), and the validator flags a `task=env-check` whose sha is not an accepted one |
| The coordinator's first environment request used a bare handle, which the send command skipped; it was resent with the mention token | messages #14, #28; coordinator lesson | lesson proposed |
| `tools/retro.py` flagged two generic lessons with fragments such as " with a ": its backtick pattern pairs a closing backtick with the next opening one across the dispatch | `retro.py` output | applied: fences are removed and spans are single-line; terms match as whole words, which the fix exposed (`id` matched inside "inside") |
