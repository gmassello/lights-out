# Tiny case — run 2 (30 Sep 2026)

Rerun of tiny run 1 after the reviewer amendment "one check per requirement". Same four seats,
runtime stopped before the dispatch, room created from the web app with the human as owner, dispatch
posted as the human at the user's request, room downloaded from the web app.

## Timeline (UTC)

| Time | Event |
|---|---|
| 00:23:22 | human dispatch; first message checked: repository `tiny-run-2` |
| 00:23:36 | coordinator → environment: ready the runtime (no `stage=`) |
| 00:24:29 | environment → coordinator: `completed`, starting state included in the same message |
| 00:24:39 | coordinator → reviewer: checks first |
| 00:26:06 | reviewer commits checks `4c7df97` (C-01..C-16) |
| 00:26:21 | coordinator → builder |
| 00:26:39 | builder restarted with `band restart` mid-build |
| 00:27:27 | builder hands off `53497a8` with the seeded fault |
| 00:27:43 | reviewer REJECT on `53497a8` |
| 00:28:07 | builder hands off repair `6e9b715` |
| 00:28:19 | reviewer ACCEPT on `6e9b715` |
| 00:28:37 | coordinator pushes and asks environment for the final check |
| 00:28:57 | environment: final check completed, runtime stopped again as found |
| 00:29:04 | coordinator → human: run outcome, `DONE` |
| 00:29:28 | watchdog exits on the outcome, no restarts |

Run time: 5 min 42 s. Human messages: 1.

## Against tiny run 1

| Measure | Run 1 | Run 2 |
|---|---|---|
| Acceptance checks | 32 | 16 |
| Reviewer, request → checks commit | 1:46 | 1:27 |
| Run time | 6:08 | 5:42 |
| Output tokens, total | 40,553 | 37,349 |
| Output tokens, reviewer | 18,097 | 15,208 |
| Seeded fault rejected | yes | yes |

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: stages closed 1/1, rejections repaired 1/1, 1 human message, 0 problems |
| Restart (AE6) | `band restart --session lo-builder` | pid 25240 → 26852, presence live, resumed |
| Watchdog | `tiny-run-2.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy on the first probe |
| Leftovers | `pgrep -fl server.py`, `git status`, runtime | none; repository clean and pushed; runtime stopped as found |
| Cost in the run window | `tools/measure_cost.py 00:23:22 00:29:04 …` | output tokens: coordinator 7,815, builder 9,297, reviewer 15,208, environment 5,029 |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| The coordinator dropped `stage=0` from the environment request | room | fixed on its own |
| environment could not post the starting state on its own: the send command rejected a message naming no seat, so the state went into its `completed` reply, still recorded before any change | message at 00:24:29 | accepted: the state is in the room before the runtime is used |
