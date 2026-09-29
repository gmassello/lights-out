# Small case — run 4 (29 Sep 2026, contaminated)

First run with four seats: `environment` (claude-sonnet-5-5, `mandates/environment.md`) owns the
shared container runtime, and the coordinator reports the outcome to the human. The container
runtime was stopped before the dispatch so that `@environment` had to act.

**Contaminated:** the dispatch pasted named the run-3 repository (`small-run-3`), so the run built
on top of run 3's accepted code and pushed there. The product and cost figures below are not a
clean build; the run is kept for what it shows about the new seat and the close.

## Timeline (UTC)

| Time | Event |
|---|---|
| 22:26:40 | human dispatch (naming `small-run-3`) |
| 22:26:51 | coordinator → environment: ready the runtime (`stage=0 task=env-prepare`) |
| 22:27:25 | environment starts the runtime, records the starting state and replies with `jam_reply_to_message`; the reply is staged and the turn ends with a BAND error, so it never reaches the room |
| 22:39:22 | environment restarted with `band restart` after 12 minutes with no message |
| 22:39:43 | environment's reply reaches the coordinator |
| 22:39:54 | coordinator → reviewer: checks first |
| 22:43:45 | reviewer commits checks `2846630` |
| 22:44:04 | coordinator → builder |
| 22:44:18 | builder restarted with `band restart` mid-build |
| 22:44:41 | builder finds two repositories and asks which one (`input-required`); coordinator: the dispatched one |
| 22:45:31 | builder hands off `2bdf19a` with the seeded fault |
| 22:45:49 | reviewer REJECT on `2bdf19a`: [C-18] |
| 22:46:19 | builder hands off repair `430e7ce` |
| 22:46:38 | reviewer ACCEPT on `430e7ce` |
| 22:46:58 | coordinator pushes and asks environment for the final check |
| 22:47:12 | environment: nothing from the run left, ports free |
| 22:47:18 | coordinator → human: run outcome, `DONE` |

Run time: 20 min 38 s, 12 min of them stalled on the lost reply. Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json small-run-3` | exit 1: stage 1 closed by the reviewer on `430e7ce`, rejections repaired 1/1, 1 human message; 2 problems (below) |
| Outcome to the human | room | the coordinator's last message mentions the human only, with sha, verdicts, environment check, assumptions and open items, ending in `DONE` |
| Environment seat | room | readied the runtime before stage 1 and checked containers, images, ports and processes at the end |
| Restart (AE6) | `band restart --session lo-builder` | pid 71138 → 72928, same runtime session, resumed |
| Small-case checks | `python3 cases/small/checks.py` against the built image | 9/9 (same code as run 3) |
| Cost in the run window | `tools/measure_cost.py 22:26:40 22:47:18 …` | output tokens: coordinator 10,440, builder 10,229, reviewer 21,186, environment 4,515 |

## Findings

| Finding | Evidence | Amendment or action |
|---|---|---|
| A staged reply can be lost, and nothing wakes a waiting seat: the 10-minute wait rule cannot fire on its own | environment's `jam_reply_to_message` returned `staged: true`, then the turn ended with "Runtime status is available in local diagnostics"; the coordinator stayed idle for 12 minutes | applied: seats post with an immediate `send` and confirm the message is in the room (common block); `tools/watchdog.py` restarts a mentioned seat that is idle and silent for 10 minutes, without writing to the room. Replayed on this room it flags `environment` at 22:37:30 and nothing at 22:30, 22:41, 22:45:30 or 22:47:20 |
| The environment's starting state lived only in the lost reply; after the restart it recorded the runtime it had started as "already running" and left it running | final check: "the Docker daemon was already running at the start" | applied: environment posts the starting state in the room, naming no seat, before it starts anything, and takes it from the room in the final check; if it is missing, it says so and leaves the runtime running |
| `stage=0` for the environment request is reported as an open stage | validator: "stage 0: open" | applied: environment requests and answers carry no `stage=` (`task=env-prepare`, `task=env-check`) |
| environment closed with `NEXT DONE` | validator: message #234 | the common block already forbids it; recheck in the next run |
| The dispatch named the previous repository | first message | applied: skill §3.4 reads the first message and compares the repository with `$R`; old briefs are closed before opening the new one |
