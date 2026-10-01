# Tiny case — run 4 (1 Oct 2026)

First run after the project review findings 1-16 and with the per-seat retro: after the run outcome,
the coordinator asks every seat for `LESSON` lines (common rule **Retro**, coordinator step 8). Same
brief and practice fault as tiny run 3. The runtime was stopped before the dispatch. The room was
created from the web app with the human as owner, and the dispatch was posted as the human. No seat
was restarted on purpose this time.

## Timeline (UTC)

| Time | Event |
|---|---|
| 22:08:29 | human dispatch; first message checked: repository `tiny-run-4` |
| 22:08:40 | coordinator → environment: `STATE working task=env-prepare`, no `stage=` |
| 22:09:15 | environment → coordinator: `completed`, `NEXT @coordinator` |
| 22:09:25 | coordinator → reviewer: checks first |
| 22:11:27 | reviewer commits checks `f268317`: `requirements: 17, checks: 17` |
| 22:11:48 | coordinator → builder, handoff in two parts (part 1 posted after part 2: its first send was rejected) |
| 22:12:51 | builder hands off `caab503` with the seeded fault |
| 22:14:59 | reviewer REJECT on `caab503` (C-04, C-13) |
| 22:15:20 | builder hands off repair `7ccdadc` |
| 22:17:04 | reviewer ACCEPT on `7ccdadc` |
| 22:17:29 | coordinator pushes and asks environment for the final check |
| 22:17:32 | coordinator closes stage 1 |
| 22:17:51 | environment: final check completed, `NEXT @coordinator`, runtime stopped again as found |
| 22:18:14 | coordinator → human: run outcome, `DONE` |
| 22:18:17 | coordinator asks builder, reviewer and environment for their retro |
| 22:18:18 | watchdog exits on the outcome, no restarts |
| 22:18:44 | last retro (builder) |

Run time: 9 min 44 s from the validator (tiny run 3: 9 min 53 s). Human messages: 1.

## The two reviews

| Candidate | Claude subagent | Codex | Merged verdict |
|---|---|---|---|
| `caab503` (seeded fault) | 14 CONFORMS, 3 DEVIATES (C-05 not confirmed by the reviewer's run) | 16 CONFORMS, 1 DEVIATES (missed C-04) | REJECT C-04, C-13, each confirmed by running; own run 15 CONFORMS, 2 DEVIATES of 17 |
| `7ccdadc` (repair) | — | — | ACCEPT |

Two Codex rollouts, one per candidate: no relaunch and no Codex subagents this time.

## Against tiny run 3

| Measure | Run 3 | Run 4 |
|---|---|---|
| Acceptance checks | 26 | 17 (one per requirement) |
| Reviewer, request → checks commit | 1:07 | 2:02 |
| Handoff → REJECT | 2:13 | 2:08 |
| Repair handoff → ACCEPT | 2:36 | 1:44 |
| Run time | 9:53 | 9:44 |
| Output tokens, Claude seats | 41,714 | 55,643 |
| Output tokens, Codex | 19,763 | 6,587 |
| Uncached input tokens, Codex | 132,107 | 45,723 |

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 1: stages closed 1/1, verdicts 2, rejections repaired 1/1, 1 human message, run time 0:09:44; 5 problems, all "mentions a seat but ends with DONE" (#246 stage close, #302, #310, #313, #334 retros), one cause (below). Re-run after the record amendment: exit 0, 0 problems |
| Watchdog | `tiny-run-4.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy |
| Retro | `tools/retro.py room.json` | 10 lessons from 4 seats, 0 flagged |
| Cost in the run window | `tools/measure_cost.py 22:08:29 22:18:14 … codex=<2 rollouts>` | output tokens: coordinator 12,367, builder 10,268, reviewer 29,417 (with its subagents), environment 3,591, Codex 6,587 (45,723 uncached input) |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| The `send` command rejects a message without a mention ("message must include at least one @owner/handle mention"), so a message that must name no seat cannot be posted with it. The stage close, the four retros and the environment's starting-state record all hit it: the close and the retros mention a seat and end with `DONE`, and the starting-state record was never posted | validator problems #246, #302, #310, #313, #334; coordinator and builder lessons; no environment message before `env-prepare completed` | applied: the common block says a record that ends with `DONE` (stage close, starting-state record, retro) mentions `@coordinator`, or the coordinator mentions the seat whose work it records; coordinator step 6 and environment step 1 say so too; the validator accepts those records with `record()` and still flags a handoff or a final check that ends with `DONE` |
| The checks rule from run 3 held: one `[C-nn]` per `[R-nn]` | `requirements: 17, checks: 17` | resolved by the run 3 amendment |
| The environment requests carry no `stage=` and the final check ends with `NEXT @coordinator` | messages #13, #244, #268 | resolved by the run 3 amendments |
| The dual review again caught what one model missed: Codex missed C-04, the Claude review and the reviewer's own run found it | REJECT body | working as designed |
| The coordinator's first send of handoff part 1 was rejected and resent after part 2 | message #93 | lesson proposed (coordinator, builder) |
| The reviewer's first review of `7ccdadc` used a prompt built with an unbraced zsh variable and reviewed old code; it was discarded and rerun | reviewer lesson | lesson proposed (reviewer) |

## Lessons applied

Approved by the human after the run and added to `## Lessons` of each mandate. The lessons about the
mention-less `send` were left out: that finding is fixed in the mandates, not learned per seat.

| Seat | Lessons |
|---|---|
| builder | version-control writes without a directory change; wait for every part of a split handoff; list the checks a seeded defect will fail |
| reviewer | braced shell variables and the candidate sha checked in every review prompt; checks on both sides of a state change; commit message checked before committing |
| coordinator | mention and protocol lines on every handoff part; literal repository path and one git command per call |
| environment | no host tools that may be missing, such as GNU `timeout` on macOS |

Tiny run 5 repeats the same brief to measure the effect on run time and rework.
