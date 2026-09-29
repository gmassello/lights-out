# Small case — run 1 (28 Sep 2026)

Development run, not judged. Seats: `coordinator` (claude-sonnet-5-5), `builder`
(claude-opus-5-5), `reviewer` (claude-sonnet-5-5), created with `band agent create`
(`claude-code-cli`, subscription, `local_config`, `bypassPermissions`,
`--claude-strict-mcp-config`, `--instructions-file` linked to `mandates/`). Result repository
`~/Documents/band-work/small-run-1`, origin a private GitHub repo.

## Timeline (UTC)

| Time | Event |
|---|---|
| 23:14:56 | human dispatch: `cases/small/SPEC.md` with the repository path |
| 23:15:19 | coordinator → reviewer: full spec, assumptions A1–A9, checks first |
| 23:16:49 | reviewer commits acceptance checks `56db827` (30 items) |
| 23:17:27 | coordinator → builder: full handoff with the checks |
| 23:17:48 | builder restarted with `band restart` mid-build |
| 23:20:20 | builder hands off candidate `8e9f4af`, disputing 4 failures as check defects |
| 23:21:26 | reviewer agrees, fixes its checks (`ca6ef1c`, `329d2f9`), 22/22 CONFORMS, ACCEPT |
| 23:21:46 | coordinator reruns, pushes `329d2f9`, closes stage 1 |

Stage time: 6 min 50 s. Human messages: 1.

## Results

| Check | Command | Result |
|---|---|---|
| Small-case checks | `python3 cases/small/checks.py` against the built image | 9/9 |
| Offline health | `docker run --network none`, `GET /health` inside | `{"status":"ok"}` |
| Restart (AE6) | `band restart --session lo-builder` | same agent and runtime session, new process, turn resumed, no human message |
| Room validator | `tools/validate_room.py room.json <repo>` | exit 1, 4 problems (below) |
| Harness gates 1–2 | `harness check <repo> --track toy` | only README, FACTORY.md and `mandates/` missing (expected for a practice repo) |
| Cost in the stage window | `tools/measure_cost.py 23:14:56 23:21:46 …` | output tokens: coordinator 11,010, builder 14,103, reviewer 19,650 |
| Cost cross-check | whole-session transcript totals against `band usage sessions --json` | equal on all 4 sessions |

## Validator findings and amendments

| Finding | Amendment (common block unless noted) |
|---|---|
| Two coordinator messages ended in `STATE` without a `NEXT`/`DONE` line | the second line is mandatory; a message without it mentions no one |
| Coordinator closed with `NEXT DONE` | `NEXT @<handle>` or the single word `DONE`, never both |
| Stage reported open: the ACCEPT cited `329d2f9`, the reviewer's own check fix, not the candidate | reviewer: `sha=` is always the candidate; own check commits go in the body |
| Coordinator sent the human a "stage started" status | coordinator: report to the human once, after the last stage |
| Builder handed off twice, both with `working` | finished work carries `completed`; each handoff is sent once |
| A seat left `server.py` listening on a host port; the first checks run hit it instead of the container | stop every process you started before ending the turn |

The validator stays strict: the stage-open finding is a real traceability gap (R9), since
the only commit the verdict named was not the builder's.

## Confirmed formats and gotchas

- Downloaded `room.json`: top-level `room`, `exportedAt`, `scope` (`full`), `filters`,
  `messages`; each message has `senderType` `Agent` or `User`, `messageType`, `content`,
  `insertedAt`. The live API (`band room messages --json`) uses snake_case instead.
- Seat transcripts land in `~/.claude/projects/-Users-…-band-work-small-run-1/`. A restart
  opens a new Claude Code session, so one seat can span several transcripts
  (`builder=<id>,<id>` in `measure_cost.py`).
- `band usage` does not attribute these sessions to the agent ("no agent-session UUID");
  sessions are passed explicitly.
- `band agent create` needs `--session`; `--dry-run` cannot take `--instructions-file`;
  `bare` context cannot use the subscription, so seats inherit `~/.claude` (hooks and
  global instructions). `--claude-strict-mcp-config` keeps personal MCP servers out.
- No REJECT happened on its own; the review still changed the work (the builder's dispute
  corrected the checks). The edge test of U6 (a rejected candidate and its repair) stays
  open for run 2.
