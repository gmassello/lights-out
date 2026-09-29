# Small case — run 2 (29 Sep 2026)

Development run with the mandates amended after run 1 (`cases/small/RUN-1.md`). Same three seats,
moved to a new result repository with `band runtime template set --spawn-cwd`; origin a private
GitHub repo.

## Timeline (UTC)

| Time | Event |
|---|---|
| 00:06:43 | human dispatch: `cases/small/SPEC.md` with the repository path |
| 00:07:03 | coordinator → reviewer: full spec, checks first |
| 00:08:25 | reviewer commits acceptance checks `2a8fc9b` |
| 00:08:57 | coordinator → builder: full handoff with the checks |
| 00:09:48 | builder restarted with `band restart` mid-build |
| 00:10:49 | builder hands off candidate `4c6daf1` once, `completed` |
| 00:11:35 | reviewer ACCEPT on `4c6daf1`, 22/22 |
| 00:12:05 | coordinator pushes `82b0549` (adds a reviewer fix to `run.sh`), closes with `DONE` |

Stage time: 5 min 22 s. Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: 1/1 stage closed by the reviewer on the builder's candidate, 1 human message, 0 problems |
| Checks before code (AE1) | room order and `git log` | checks `2a8fc9b` at 00:08:25, before the builder's first commit `4c6daf1` |
| Small-case checks | `python3 cases/small/checks.py` against the built image | 9/9 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy after 6 s (limit 30 s) |
| Restart (AE6) | `band restart --session lo-builder` | pid 82452 → 84262, same runtime session, presence live, no human message |
| Leftover processes | `pgrep -fl server.py`, `docker ps -q` | none |
| Cost in the stage window | `tools/measure_cost.py 00:06:43 00:12:05 …` | output tokens: coordinator 10,558, builder 10,227, reviewer 15,657 |
| Cost cross-check | whole-session transcript totals against `band usage sessions --json` | equal on all 4 sessions |
| Harness gates 1–2 | `harness check <repo> --track toy` | only README, FACTORY.md and `mandates/` missing (expected) |

## Against run 1

Every run-1 finding is gone: protocol lines parse, the verdict cites the candidate, one
handoff per candidate with `completed`, no status message to the human, nothing left running.

## Still open

- No REJECT: the candidate passed the first review, so the reject-and-repair path (AE2, R7) is
  not exercised yet. The U6 edge test needs a seeded fault.
- The coordinator closed to the reviewer instead of reporting the outcome to the human; the
  mandate asks for one report to the human after the last stage.
