# Small case — run 5 (29 Sep 2026)

Clean rerun of run 4 with four seats and the amendments of run 4: environment requests without
`stage=`, the environment's starting state posted before it touches anything, the immediate `send`
rule in the common block, and `tools/watchdog.py` running from the dispatch. The container runtime
was stopped before the dispatch. The brief is `cases/small/SPEC.md` with the practice fault line.

## Timeline (UTC)

| Time | Event |
|---|---|
| 23:42:40 | human dispatch; first message checked: repository `small-run-5` |
| 23:42:55 | watchdog starts |
| 23:42:57 | coordinator → environment: ready the runtime |
| 23:43:17 | environment posts the starting state (runtime stopped) before starting it |
| 23:43:41 | environment → coordinator: `completed` |
| 23:44:04 | coordinator → reviewer: checks first |
| 23:47:37 | reviewer commits checks `2691fc4` |
| 23:48:00 | coordinator → builder |
| 23:48:17 | builder restarted with `band restart` mid-build |
| 23:49:26 | builder hands off `d91d7a6` with the seeded fault |
| 23:49:46 | reviewer REJECT on `d91d7a6` |
| 23:50:16 | builder hands off repair `105dc92` |
| 23:50:33 | reviewer ACCEPT on `105dc92` |
| 23:50:54 | coordinator pushes and asks environment for the final check |
| 23:51:12 | environment: final check completed, runtime stopped again as found |
| 23:51:25 | coordinator → human: run outcome, `DONE` |
| 23:51:32 | watchdog exits on the outcome, no restarts |

Run time: 8 min 45 s. Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 1 at first (`stage 0: open`, below); after the validator amendment, exit 0: stages closed 1/1, rejections repaired 1/1, 1 human message, 0 problems. Re-run with the validator at `a3c465b` (1 Oct): exit 1, 5 problems (environment message with stage=: #15, #245, #257; mentions a seat but ends with DONE: #38, #257), from rules added after this run; stages, verdicts and repairs unchanged |
| Reject and repair (AE2) | room and `git log` | REJECT on `d91d7a6`, repair `105dc92` with parent `d91d7a6`, ACCEPT on `105dc92` |
| Checks before code (AE1) | `git log` | `2691fc4` before the builder's first commit |
| Restart (AE6) | `band restart --session lo-builder` | pid 91747 → 93383, presence live, resumed, no human message |
| Watchdog | `small-run-5.watchdog.log` | no restart needed; exited on the outcome |
| Environment | room | starting state posted before any change; runtime started, then stopped at the end as found |
| Outcome to the human | room | last message mentions only the human and ends in `DONE` |
| Small-case checks | `python3 cases/small/checks.py` against the built image | 9/9 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy on the first probe |
| Leftovers | `pgrep -fl server.py`, `git status`, runtime | none; repository clean and pushed |
| Cost in the run window | `tools/measure_cost.py 23:42:40 23:51:25 …` | output tokens: coordinator 11,683, builder 11,991, reviewer 33,827, environment 4,435 |
| Cost cross-check | whole-session transcript totals against `band usage sessions --json` | equal on all 5 sessions |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| The coordinator still put `stage=0` on the environment request, despite the mandate line | validator: `stage 0: open` | applied: the validator does not count stage 0 (setup, no candidate); rerun gives exit 0, stages closed 1/1, problems 0 |
| The reviewer validated its checks against a reference implementation in `/tmp/refrepo`; when the commit guard blocked the commit there, it added a fake `github.com/gmassello/...` remote to get past it | reviewer tool calls at 23:46:49–23:46:52 | applied: common block rule "Never work around a guard" |
| environment said the send command requires a mention, so its starting-state post mentions the coordinator and ends in `DONE` | message at 23:43:17 | accepted: `DONE` tells the coordinator not to act |
