# Small case — run 3 (29 Sep 2026)

Development run for the reject-and-repair path (AE2, R7). The brief is `cases/small/SPEC.md`
plus one practice line under Constraints that makes the builder's first candidate return `201`
instead of `409 idempotency_conflict` for a reused key with a different body, fixed only after a
REJECT. Same seats and mandates as run 2, moved with `band runtime template set --spawn-cwd`.

## Timeline (UTC)

| Time | Event |
|---|---|
| 21:52:07 | human dispatch |
| 21:52:26 | coordinator → reviewer: full spec, assumptions, checks first |
| 21:53:45 | reviewer commits acceptance checks `d6a6bb6` (24 HTTP, 6 docker) |
| 21:54:13 | coordinator → builder: handoff in three parts |
| 21:54:31 | builder restarted with `band restart` mid-build |
| 21:56:15 | builder hands off candidate `73e64cf` |
| 21:56:36 | reviewer REJECT on `73e64cf`: [C-18] and [C-22] deviate (201 instead of 409) |
| 21:56:44 | coordinator confirms round 1 of 5 and offers to run the docker checks |
| 21:57:25 | builder hands off repair `2eeee08`, ACCEPT on both findings |
| 21:57:42 | reviewer INSUFFICIENT_EVIDENCE on `2eeee08`: HTTP 24/24, no docker daemon in its seat |
| 21:58:16 | coordinator posts its docker run at `2eeee08` |
| 21:58:27 | reviewer ACCEPT on `2eeee08` |
| 21:58:53 | coordinator pushes `2eeee08`, closes with `DONE` |

Stage time: 6 min 46 s. Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: 1/1 stage closed by the reviewer on `2eeee08`, 3 verdicts, rejections repaired 1/1, 1 human message, 0 problems. Re-run with the validator at `a3c465b` (1 Oct): exit 1, 1 problem (mentions a seat but ends with DONE: #229), from rules added after this run; stages, verdicts and repairs unchanged |
| Reject and repair (AE2) | room order and `git log` | REJECT on `73e64cf`, repair `2eeee08` with parent `73e64cf`, ACCEPT on `2eeee08` |
| Checks before code (AE1) | `git log` | `d6a6bb6` before the builder's first commit |
| Small-case checks | `python3 cases/small/checks.py` against the built image | 9/9 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy on the first probe |
| Restart (AE6) | `band restart --session lo-builder` | pid 37634 → 39355, same runtime session, presence live, no human message |
| Leftover processes | `pgrep -fl server.py`, `docker ps -q` | none |
| Cost in the stage window | `tools/measure_cost.py 21:52:07 21:58:53 …` | output tokens: coordinator 11,424, builder 12,787, reviewer 17,380 |
| Cost cross-check | whole-session transcript totals against `band usage sessions --json` | equal on all 4 sessions |
| Harness gates 1–2 | `harness check <repo> --track toy` | only README, FACTORY.md and `mandates/` missing (expected) |

## Findings

- The builder started the shared Docker VM (`colima start`) for its own check and stopped it
  when done, reading "leave nothing running" as covering it. The reviewer then had no daemon and
  returned INSUFFICIENT_EVIDENCE; the coordinator ran the docker checks instead. Candidate
  amendment: stop only what you started in this turn, never a shared machine service.
- The coordinator again closed to the reviewer instead of reporting the outcome to the human.
- The seeded fault was caught by the reviewer's own checks ([C-18], [C-22]) with file and line,
  and the repair touched only the lines named.
