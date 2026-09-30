# Tiny case — run 3 (30 Sep 2026)

First run with the reviewer's dual review: for each candidate, the reviewer seat gets two independent
reviews in parallel, one from a `claude-sonnet-5-5` subagent and one from `codex exec` on
`gpt-5.6-terra` (ChatGPT subscription). It then merges them and confirms every `DEVIATES` itself. The
other seats, the room setup and the practice fault are the same as tiny run 2. The runtime was
stopped before the dispatch. The room was created from the web app with the human as owner, and the
dispatch was posted as the human.

## Timeline (UTC)

| Time | Event |
|---|---|
| 21:27:19 | human dispatch; first message checked: repository `tiny-run-3` |
| 21:27:32 | coordinator → environment: ready the runtime |
| 21:28:10 | environment → coordinator: `completed` |
| 21:28:21 | coordinator → reviewer: checks first |
| 21:29:28 | reviewer commits checks `2e30203` (C-01..C-26) |
| 21:29:47 | coordinator → builder |
| 21:30:05 | builder restarted with `band restart` mid-build |
| 21:31:18 | builder hands off `d98ee90` with the seeded fault |
| 21:31:31 | reviewer launches the Codex review and the Claude subagent |
| 21:33:31 | reviewer REJECT on `d98ee90` (C-12, C-16, C-18) |
| 21:34:00 | builder hands off repair `3ba2af8` |
| 21:36:36 | reviewer ACCEPT on `3ba2af8` |
| 21:36:52 | coordinator pushes and asks environment for the final check |
| 21:37:06 | environment: final check completed, runtime stopped again as found |
| 21:37:12 | coordinator → human: run outcome, `DONE` |
| 21:37:37 | watchdog exits on the outcome, no restarts |

Run time: 9 min 53 s (tiny run 2: 5 min 42 s). Human messages: 1.

## The two reviews

| Candidate | Claude subagent | Codex | Merged verdict |
|---|---|---|---|
| `d98ee90` (seeded fault) | 23 CONFORMS, 3 DEVIATES | 24 CONFORMS, 2 DEVIATES (missed C-18) | REJECT C-12, C-16, C-18, each confirmed by running |
| `3ba2af8` (repair) | 26 CONFORMS | 26 CONFORMS, static only (no Docker in `read-only`) | ACCEPT |

The dual review caught what one model missed: C-18 (an id from before a reset must return 404) came
only from the Claude review and the reviewer's own run. The Codex runs had no reasoning effort (see
findings), so this measures a weaker configuration than intended.

## Against tiny run 2

| Measure | Run 2 | Run 3 |
|---|---|---|
| Acceptance checks | 16 | 26 |
| Reviewer, request → checks commit | 1:27 | 1:07 |
| Handoff → REJECT | 0:16 | 2:13 |
| Repair handoff → ACCEPT | 0:12 | 2:36 |
| Run time | 5:42 | 9:53 |
| Output tokens, Claude seats | 37,349 | 41,714 |
| Output tokens, Codex | — | 19,763 |

## Results

| Check | Command | Result |
|---|---|---|
| Room validator | `tools/validate_room.py room.json <repo>` | exit 0: stages closed 1/1, rejections repaired 1/1, 1 human message, 0 problems |
| Restart (AE6) | `band restart --session lo-builder` | pid 29984, presence live, resumed |
| Watchdog | `tiny-run-3.watchdog.log` | no restart needed; exited on the outcome |
| Tiny-case checks | `python3 cases/tiny/checks.py` against the built image | 5/5 |
| Offline health | `docker run --network none`, `GET /health` inside | healthy |
| Leftovers | `pgrep`, `git status`, runtime | no `codex exec` left; repository clean and pushed; runtime stopped as found |
| Cost in the run window | `tools/measure_cost.py 21:27:19 21:37:12 … codex=<5 rollouts>` | output tokens: coordinator 8,188, builder 12,294, reviewer 16,743 (with its subagents), environment 4,489, Codex 19,763 (132,107 uncached input) |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| `codex exec` with `--ignore-user-config` ran with `reasoning effort: none` | Codex log header | applied: `-c model_reasoning_effort=medium` in the reviewer mandate |
| The first background `codex exec` waited on stdin ("Reading additional input from stdin"); the reviewer relaunched it with `</dev/null` without stopping the first, so two Codex reviews ran for `d98ee90` | reviewer transcript 21:31:30 and 21:31:41; two rollouts | applied: `</dev/null` in the command and "launch each review once" |
| In the second round Codex spawned two subagents of its own | rollouts with `thread_spawn` | applied: `--disable multi_agent` in the command |
| The Codex review in `read-only` cannot reach Docker or the network, so it is static | ACCEPT body | applied: the reviewer starts one container per review on its own port and puts its URL in the prompt; Codex runs with `workspace-write`, network on and a temp working directory, so it probes the service without writing in the repository. Manual test against `3ba2af8`: `200` on `/health` and `404 not_found` on an unknown id in 9 s |
| Each verdict took over 2 minutes instead of under 20 s, nearly doubling the run: the Claude subagent took about 40 s, but Codex explored the repository (132,107 uncached input tokens) for 2:00 to 2:11 while the reviewer waited | timeline, reviewer transcript | applied: both reviews get the candidate's diff and "do not explore beyond the diff"; Codex runs without subagents and each review is capped at 3 minutes. Manual rerun on `d98ee90` with reasoning `medium`: 23 s, 4,033 tokens, C-12, C-16 and C-18 all found |
| 26 checks instead of 16 with the same rule | commit `2e30203` | open: the one-check-per-requirement rule is not stable across runs |
| The coordinator marked the environment requests `stage=0` and `stage=1`, and wrote `NEXT @[[<id>]]` instead of `NEXT @<handle>` | room | harmless: the validator accepts both |
