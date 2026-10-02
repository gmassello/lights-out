# Tiny case — run 7 (2 Oct 2026, cancelled)

Same brief and practice fault as tiny runs 4 to 6, with the six lessons the coordinator applied after
run 6 (15 lessons in the mandates at dispatch). The run also meant to test seats isolated from the
user's `~/.claude`; BAND rejected that (findings). Cancelled by the human at the fourth candidate, with
three REJECTs and no ACCEPT. Nothing was pushed: `origin/main` is still the initial commit. No
`room.json` was downloaded; the timeline comes from `band room messages`.

## Rooms

| Room | Dispatch (UTC) | Outcome |
|---|---|---|
| `tiny-run-7` | 00:03:36 | the coordinator never woke: BAND rejected the `--setting-sources` runtime argument and kept the dispatch buffered; agents stopped |
| `tiny-run-7b` | 00:08:52 | same, with `--model <model>` as argument: BAND rejects a model set both as argument and as runtime setting; agents stopped |
| `tiny-run-7c` | 00:11:18 | the run below; seats with `--autocompact auto` (the default) |

## Timeline of tiny-run-7c (UTC)

| Time | Event |
|---|---|
| 00:11:18 | human dispatch |
| 00:11:52 | environment → coordinator: `completed` (0:34) |
| 00:12:00 | coordinator → reviewer: checks first |
| 00:12:03–00:14:32 | reviewer shows "Working" with no tool call for about 2.5 minutes |
| 00:16:04 | reviewer commits checks `9743940` (C-01..C-15) |
| 00:16:22 | coordinator → builder |
| 00:17:37 | builder hands off `487503a` with the seeded fault (sent twice, 00:17:53) |
| 00:19:22 | REJECT 1 on `487503a`: the seeded fault |
| 00:19:45 | builder hands off `64cd541` |
| 00:21:20 | REJECT 2 on `64cd541`: [C-08] a body that is not a JSON object (deep nesting) gets no error envelope |
| 00:21:47 | builder hands off `eafe597` |
| 00:24:14 | REJECT 3 on `eafe597`: [C-08] a 5,000-digit `Content-Length` and [C-04] a malformed request line close the connection without a response |
| 00:25:42 | builder hands off `de58f7f` (never reviewed) |
| ~00:27 | human cancels: "Stop all"; the reviewer's `codex exec` and its two review containers were removed |

## Findings

| Finding | Evidence | Status |
|---|---|---|
| The lessons raised the reviewer's bar without raising the builder's first attempt: after run 6 the reviewer must "enumerate every variant of unknown X is rejected and add a malformed-input case for each parsed header", and the builder only "route every request through the same handler". Rounds went from 1 REJECT (runs 4–6) to 3 REJECTs and counting, each on a real defect confirmed by the reviewer's own run | REJECT bodies 2 and 3 | open: a lesson that raises one seat's bar needs its counterpart in the seat that has to meet it, or the same brief takes more rounds |
| BAND passes only `--model`, `--fallback-model`, `--max-budget-usd` and `--autocompact` to an owned Claude Code runtime, rejects `--model` when the model is also a runtime setting, and leaves the dispatch buffered without retry when an argument is rejected. Each room copies the runtime arguments when it is created | `~/.jam/logs/jamd.log` | recorded in the run skill; isolating the seats from `~/.claude` is dropped |
| The reviewer's first answer took about 2.5 minutes with no error | transcript gap 00:12:03–00:14:32, Chrome "Working" | noise of the run, not a factory defect |
| The builder posted its first handoff twice, 16 s apart | messages 00:17:37 and 00:17:53 | not analysed (no `room.json`) |
| Codex again flagged `{"status": "ok"}` against `{"status":"ok"}` as DEVIATES; the reviewer dropped it as the same JSON object | REJECT bodies 2 and 3 | working as designed |
