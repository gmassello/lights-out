# Lights-out — Use cases

Source: `docs/BRIEF.md` · priority from `docs/PLAN.md` Cut line (a requirement takes the highest tier among the units that cover it).

"The system" is the factory: the seats, their mandates and the room. Officially it is proven by the
event harness (`harness check` and the track suites, which we never read) and by the rubric in
`docs/judging.tsv`.

## Features

| IDs | Feature | Actor | Priority | Criterion | In the video |
|---|---|---|---|---|---|
| F1 · R5 | One dispatch starts a run that needs no further human input | A1, A2 | must (U6, U11) | Agent Teamwork | yes: the single human message in the room |
| F2 · R2, R3, R7, R9 | Stage cycle: acceptance checks first, build, blocking verdict, traced repair | A2, A3, A4, A5 | must (U2, U4, U6) | Factory, Agent Teamwork | yes: the REJECT and the repair |
| F3 · R5 | A seat restarts or goes silent and the run recovers on its own | A2 | must (U6) | Agent Teamwork | no |
| F4 · R4, R6, R7, R8 | Handover to judges: stages claimed, cost measured, failures traced, factory reusable | A1, A6 | must (U12, U13) | Factory | yes: the stage reached and the cost |
| R1 | The same mandates run unchanged on three domains | A1 | must (U2, U7) | Factory | yes: identical mandate hashes |
| R10 | The stage-2 interface is coherent, responsive and clear in every named state | A3 | must (U9) | App | yes: the service working |
| R11 | Each stage extends the previous one without erosion or bloat | A3, A4 | must (U9) | App | no |

## Happy paths

### F1. Dispatch — R5
1. Start state: three seats (coordinator, builder, reviewer) bound in a fresh room, fresh repo, no human message yet.
2. The operator posts one message with the brief for all stages and `docs/DESIGN.md`.
3. The coordinator posts the stage-1 goal `brief=v1` and the task list; the run continues to the last stage with no other human message.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE5 | **Covers R5.** Given the judged run's room recording, when its messages are counted by sender type, then there is exactly one human message. | `tools/validate_room.py` (U4) over `room.json` |

### F2. Stage cycle — R2, R3, R7, R9
1. Start state: stage 1 dispatched, coordinator task `#1 stage-1-api` open.
2. The reviewer posts acceptance checks `[C-01]`…`[C-12]` derived from the spec, ending in `STATE working stage=1 task=stage-1-api`.
3. The builder receives the task with the full spec and the checks, commits, and hands off `STATE completed stage=1 sha=a1b2c3d`.
4. The reviewer runs its checks against `a1b2c3d`: `[C-03]` DEVIATES → `STATE REJECT stage=1 sha=a1b2c3d` with the failing check and expected vs actual.
5. The builder answers `[C-03] ACCEPT`, repairs, hands off `sha=e4f5a6b refs=[#1@a1b2c3d]`.
6. The reviewer re-runs `[C-03]` first, then the regression, and posts `STATE ACCEPT stage=1 sha=e4f5a6b`; the coordinator closes the stage.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE1 | **Covers R2.** Given stage N has been dispatched, when the builder makes its first commit for stage N, then the room already holds the reviewer's acceptance checks for stage N, posted earlier. | validator: timestamp of the first `[C-nn]` message vs the first commit of stage N |
| AE2 | **Covers R3.** Given a builder handoff at commit X that violates one acceptance check, when the reviewer verifies it, then the reviewer posts REJECT naming the check, and the stage does not close until a later commit gets ACCEPT. | validator (U4): REJECT with `[C-nn]`, followed by an ACCEPT on a different `sha=` |
| AE3 | **Covers R3.** Given a candidate authored by the builder, when the only ACCEPT for it comes from the builder itself, then the stage stays open. | validator (U4): stage reported open |
| AE9 | **Covers R7.** Given a REJECT at commit X, when `FACTORY.md` is read, then it lists the finding, who found it, commit X and the repairing commit. | `FACTORY.md` recovery table cross-checked with the validator's repair list |
| AE10 | **Covers R9.** Given any handoff or verdict message, when its last line is parsed, then it names a stage and a commit that exists in the repository history. | validator (U4): every `sha=` resolves with git in the delivery repo |

### F3. Recovery — R5
1. Start state: stage 2 in progress, builder working on task `#4`.
2. The builder's seat is restarted.
3. It reattaches under the same identity, announces the reattach, reads the room and resumes `#4`; the round count for `#4` is read from the room, not reset.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE6 | **Covers R5.** Given a seat is restarted mid-stage, when it reattaches, then it keeps its identity and the stage continues without a human message. | `room.json`: same `senderId` before and after the restart; validator: one human message |

### F4. Handover to judges — R4, R6, R7, R8
1. Start state: the judged run has finished.
2. The operator downloads the room recording, redacts credentials and records the redaction.
3. A fresh clone of the delivery repo passes the harness check and every suite in isolated mode.
4. The cost meter produces time and tokens per stage; `FACTORY.md` and `README.md` are written from those figures.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE7 | **Covers R4.** Given the delivered stage folders, when the event harness runs every suite in isolated mode, then each suite 1..N scores at least 0.5 and suite N+1 does not pass completely. | `harness run --all --mode isolated` on a fresh clone |
| AE8 | **Covers R6.** Given a finished stage, when the cost command runs over that stage's window, then its time and token totals match the figures posted in the room and in `FACTORY.md`. | `tools/measure_cost.py` (U5) output diffed against the room message and `FACTORY.md` |
| AE12 | **Covers R8.** Given only `FACTORY.md` and `mandates/`, when another person follows them with a different brief, then they can start the same seats and dispatch without asking. | the medium-case re-run at close (U12) started only from `FACTORY.md` |

### R1. Same mandates, three domains
1. Start state: mandates frozen with their SHA-256 hashes.
2. The small case, the practice track and the real track are dispatched with only the brief changed.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE4 | **Covers R1.** Given the small case, the practice track and the real track, when each run starts, then the mandate files have the same hashes in all three and contain no domain vocabulary from any of them. | `shasum -a 256 mandates/*.md` recorded per run; vocabulary grep over `mandates/` returns nothing |

### R10. Stage-2 interface
1. Start state: stage-2 folder running on port 8080 after a reset.
2. Each state the stage-2 spec names is reached through the UI at 375 px and at desktop width.

| AE | Given / When / Then | How it is proven |
|---|---|---|
| AE11 | **Covers R10.** Given the stage-2 interface at 375 px wide, when each state the spec names is shown, then nothing overflows horizontally and each state is distinguishable. | `screenshot` per state, plus `scrollWidth` equal to the viewport width measured in an iframe (headless Chrome cannot render below 500 px) |

### R11. Extension without bloat
1. Start state: stage N accepted and frozen.
2. Stage N+1 starts as a copy of stage N and adds only what the new spec asks.

| Criterion | How it is proven |
|---|---|
| proposed: earlier stage folders keep their tree hash after the next stage starts | `git rev-parse HEAD:stage-N` recorded at freeze and at the end of the run |
| proposed: the line count growth per stage is reported next to the features added | `git diff --stat` between stage folders, published in `FACTORY.md` |

## Test cases

### Small — own notes API (phase F1, PLAN U6)
Spec in `cases/small/SPEC.md`; checks in `cases/small/checks.py`, written from the spec. One stage, no UI, three base seats.

| Layer | Criterion | How it is proven |
|---|---|---|
| Product | Every check passes | `python3 cases/small/checks.py http://localhost:8080` exits 0 |
| Product | The container is healthy within 30 s, also without network | image build from the stage folder, then run with `--network none` and poll `/health` |
| System | Every seat speaks at least once and there are reciprocal mentions | harness check over `room.json` |
| System | One dispatch, no other human message (AE5) | validator |
| System | A full cycle coordinator → builder → reviewer → verdict, with a REJECT and its repair (AE2); a fault is injected if none happens on its own | validator |
| System | A seat restart survived without new identities (AE6) | `senderId` before and after the restart |
| System | Every handoff and verdict ends with a parseable protocol line (AE10) | validator |
| System | Time and tokens measured: the factory's baseline cost (AE8) | cost meter |

### Medium — practice track `toy` (phase F1, PLAN U7; re-run at close, U12)
The kickoff repo's shared counter; unscored, ships its full suite. Stages come from its spec; its tests are not read.

| Layer | Criterion | How it is proven |
|---|---|---|
| Product | Every suite passes in isolated mode | `harness run --all --mode isolated` |
| Product | The package is valid | `harness check` clean |
| System | Same mandate hashes as the small case; only the brief changes (AE4) | `shasum` per run + amendment log |
| System | Every handoff carries the full spec, in numbered parts if long | `room.json` read |
| System | All stages from one dispatch; cost per stage posted in the room (AE8) | validator + cost meter |
| System | The extra verifier seat, if chosen, posts a verdict that the validator counts (PLAN U8) | validator |
| System | At close, another person starts the factory from `FACTORY.md` alone with this brief (AE12) | the U12 re-run |

### Large — real track `tablekeeper` (phases F2 and F3, PLAN U9 and U11)
The judged delivery; iterated in U9, run once clean in U11.

| Layer | Criterion | How it is proven |
|---|---|---|
| Product | Each suite 1..N at 0.5 or more, target stage 4, no overshoot (AE7) | `harness run --all --mode isolated` on a fresh clone |
| Product | Package checks: health within 30 s in isolated mode, no network, reset 204 under 10 s, no local-only binds, no symlinks | the package checks in `docs/FACTORY-DESIGN.md` › Contrato del runner |
| Product | Stage-2 UI at 375 px with no horizontal overflow (AE11) | `screenshot` + iframe measurement |
| System | Exactly one human message (AE5) | validator |
| System | At least one finding with its ACCEPT/DISPUTE trail and repair (AE2, AE9) | validator + `FACTORY.md` |
| System | The recording passes the harness check | `harness check` |
| System | Every delivery checklist item | checklist in `docs/FACTORY-DESIGN.md` |

## Out of scope
- Using A2A or AGNTCY as the transport between seats.
- Automatic model tuning from past runs.
- Typed-decision models as guardrails.
- The pocketful track, an orchestrator that calls agents in turn, a dashboard as the deliverable.
- Cut in the plan: the seat launch script (U15) and the genericity metric with the verdict hash chain (U16).
- Own checks for the practice and real tracks: both ship their own suites.
