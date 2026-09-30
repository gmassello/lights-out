# Tiny case — run 1 (30 Sep 2026)

First run of the iteration case (`cases/tiny/SPEC.md`, two endpoints) with the four seats and the
mandates of small run 5 plus the guard rule. The container runtime was stopped before the dispatch.
The room was created from the web app with the human as owner, renamed with `band room rename`,
and the dispatch was posted as the human with `band room send` at the user's request.

## Timeline (UTC)

| Time | Event |
|---|---|
| 00:10:45 | human dispatch; first message checked: repository `tiny-run-1` |
| 00:10:52 | watchdog starts |
| 00:10:57 | coordinator → environment: ready the runtime |
| 00:11:12 | environment posts the starting state before any change |
| 00:11:37 | environment → coordinator: `completed` |
| 00:11:48 | coordinator → reviewer: checks first |
| 00:13:34 | reviewer commits checks `4717523` (C-01..C-32) |
| 00:14:01 | coordinator → builder |
| 00:14:19 | builder restarted with `band restart` mid-build |
| 00:15:06 | builder hands off `0ae15df` with the seeded fault |
| 00:15:27 | reviewer REJECT on `0ae15df` |
| 00:15:50 | builder hands off repair `f300e4f` |
| 00:16:13 | reviewer ACCEPT on `f300e4f` |
| 00:16:31 | coordinator pushes and asks environment for the final check |
| 00:16:45 | environment: final check completed, runtime stopped again as found |
| 00:16:53 | coordinator → human: run outcome, `DONE` |
| 00:16:57 | watchdog exits on the outcome, no restarts |

Run time: 6 min 8 s (small run 5: 8 min 45 s). Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: stages closed 1/1, rejections repaired 1/1, 1 human message, 0 problems |
| Reject and repair (AE2) | room and `git log` | REJECT on `0ae15df`, repair `f300e4f`, ACCEPT on `f300e4f` |
| Checks before code (AE1) | `git log` | `4717523` before the builder's first commit |
| Restart (AE6) | `band restart --session lo-builder` | pid 10702 → 12300, presence live, resumed |
| Watchdog | `tiny-run-1.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy on the first probe |
| Leftovers | `pgrep -fl server.py`, `git status`, runtime | none; repository clean and pushed; runtime stopped as found |
| Cost in the run window | `tools/measure_cost.py 00:10:45 00:16:53 …` | output tokens: coordinator 10,120, builder 8,119, reviewer 18,097, environment 4,217; total 40,553 (small run 5: 61,936) |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| The reviewer wrote 32 checks for a two-endpoint spec (36 for the small case): the check count barely follows the spec size, and writing them is still the longest step (1 min 46 s) | commit `4717523` | applied: reviewer mandate, one check per requirement (a bullet, a table row or a named error code), several assertions allowed, no checks for unstated behaviour |
| The coordinator still marks the environment request `stage=0` | room | harmless: the validator skips stage 0 |
