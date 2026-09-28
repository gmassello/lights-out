# Lights-out — Plan

Source: `docs/BRIEF.md` · Design reference: `docs/FACTORY-DESIGN.md` · Deadline: Mon Oct 5 23:59 PDT (Tue Oct 6 03:59 ART) · Hours left at writing: 177.5

## Summary
At the end of this plan a three-seat factory with an acceptance-first reviewer has run once, clean,
on tablekeeper from a single dispatch; the delivery repo passes the event checks on a fresh clone,
and `FACTORY.md`, the room recording, the deck and the video are submitted. The unit that unlocks
the demo is U6: the small case proves the seats hand off, block and recover before any real track
is attempted.

Two repositories are involved: this workspace (`lights-out`: plan, cases, tools) and a fresh public
delivery repo created for the judged run (U11). Nothing in `stage-N/` is written by hand.

## Key technical decisions
- Acceptance first: verifiers commit their checks from the spec before the build. settled: inherited from BRIEF
- The central signal is a blocking verdict; a stage closes only with an ACCEPT from a non-author seat. settled: inherited from BRIEF
- Coordinator plans; no planner seat. settled: inherited from BRIEF
- All seats on the Claude Max subscription; Gemini plan B, Featherless plan C. settled: inherited from BRIEF
- Test cases grow in size across domains: own small case, practice track, real track. settled: inherited from BRIEF
- One protocol line closes every handoff and verdict, with one verdict vocabulary per level (`docs/FACTORY-DESIGN.md`, "Vocabulario único y última línea"). settled: user-approved
- The room validator and the cost meter are Python scripts using only the standard library, over `room.json` and the seats' session transcripts — chosen over shell pipelines because both parse JSON and a pipe hides exit codes. settled: plan-time
- The small case runs with the three base seats only; the extra seat is first tried on the practice track. settled: plan-time
- `docs/DESIGN.md` travels with the brief as a dispatch input and is declared in `FACTORY.md`; the factory, not us, builds the UI. settled: user-approved

## Units
### U1. Setup and commands
- **Goal:** BAND account, desktop app, CLI and seat plugin installed with the readiness check green; the lablab team exists with Discord linked; the kickoff repo and its harness run locally; the real `band` subcommands are recorded; `CLAUDE.md` has a `## Commands` block with the harness, the small-case checks and the validator.
- **Covers:** — (enables every unit)
- **Files:** `CLAUDE.md`, `docs/FACTORY-DESIGN.md` (verified CLI commands)
- **Depends on:** —
- **Status:** todo
- **Tests:**
  - happy: the harness check runs against the kickoff repo's toy example → exits cleanly.
  - edge: the lablab project page → *Submit Project* is enabled for our team.
  - error: a `band` subcommand listed in the design doc does not exist → it is marked unverified and nothing depends on it.

### U2. Mandates v1 and protocol
- **Goal:** three generic mandates (coordinator, builder, reviewer) that start with `Harness:` and `Model:`, follow the role template, carry the anti-loop rules, the acceptance-first rule, the protocol line and the single verdict vocabulary, and name no domain.
- **Covers:** R1, R2, R3, R9 · F2
- **Files:** `mandates/coordinator.md`, `mandates/builder.md`, `mandates/reviewer.md` (workspace copies, frozen in U9)
- **Depends on:** U1
- **Status:** todo
- **Tests:**
  - happy: the harness check on a repo with the three mandates → mandate gate passes. Covers AE4.
  - edge: the mandates are scanned for the vocabulary of notes, counters and reservations → no match.
  - error: a mandate with `Model:` inside a heading → the harness check fails, and the fix is recorded.

### U3. Brief template and small-case brief
- **Goal:** a reusable brief template (goal, spec, milestones, constraints, done state, escalation) and the small-case brief filled from it; the brief is the only thing that changes between cases.
- **Covers:** R1
- **Files:** `cases/BRIEF-TEMPLATE.md`, `cases/small/SPEC.md`
- **Depends on:** —
- **Status:** todo
- **Tests:**
  - happy: the small-case spec follows every section of the template → no section missing.
  - edge: the template read without any case → contains no domain term.
  - error: a brief section left empty → the coordinator records an assumption instead of asking the human.

### U4. Room validator v1
- **Goal:** a command that reads a `room.json` and the repo history and fails when a verdict names a commit that does not exist, a rejection has no repair, a stage closed without a non-author ACCEPT, a protocol line does not parse, or more than one human message exists.
- **Covers:** R3, R5, R7, R9
- **Files:** `tools/validate_room.py`
- **Depends on:** U2
- **Status:** todo
- **Tests:**
  - happy: the small-case recording → exits 0 and prints stages, verdicts and repairs first. Covers AE2.
  - edge: a stage whose only ACCEPT comes from the candidate's author → reported as open. Covers AE3.
  - error: a verdict citing a commit missing from history → exits non-zero naming the message. Covers AE10.
  - error: a recording with two human messages → exits non-zero. Covers AE5.

### U5. Cost meter
- **Goal:** a command that sums time and tokens per seat and per stage window from the seats' session transcripts, or reports time only and labels the result partial when tokens are unavailable. Verified on this machine: each transcript line carries `timestamp`, and assistant lines carry `message.usage` (input, output, cache read, cache creation), but one message spans several lines with the same `message.id`, so usage is counted once per id. Still to confirm in U6: that seats launched from the desktop app write transcripts in the same place.
- **Covers:** R6
- **Files:** `tools/measure_cost.py`
- **Depends on:** U1
- **Status:** todo
- **Tests:**
  - happy: the small-case transcripts and the stage window → totals that match what the tool shows for the same sessions. Covers AE8.
  - edge: a message split across several transcript lines with one id → counted once, not per line.
  - edge: a seat with no messages inside the window → zero, not missing.
  - error: transcripts without usage fields → output labelled partial, exit 0.

### U6. Small-case run
- **Goal:** the small case built end to end from one dispatch, meeting every criterion of the small case in `docs/FACTORY-DESIGN.md`.
- **Covers:** R2, R3, R5 · F1, F2, F3
- **Files:** `cases/small/` (run notes), a throwaway delivery repo
- **Depends on:** U2, U3, U4, U5
- **Status:** todo
- **Tests:**
  - happy: the delivered service against the small-case checks → 100%, and the validator → exits 0. Covers AE1.
  - edge: no rejection happens on its own → one fault is injected in this practice run and the REJECT and repair appear in the room.
  - error: a seat is restarted mid-stage → it keeps its identity and the stage finishes with no human message. Covers AE6.

### U7. Practice-track run
- **Goal:** the practice track built from one dispatch with the same mandate hashes as U6; every suite passes in isolated mode.
- **Covers:** R1, R4
- **Files:** a throwaway delivery repo
- **Depends on:** U6
- **Status:** todo
- **Tests:**
  - happy: mandate hashes in U6 and U7 → identical. Covers AE4.
  - edge: a mandate change forced by a generic defect → logged as an amendment and the U6 run is not invalidated.
  - error: a suite of the practice track fails → the failure is traced to a room verdict or a missing check, not fixed by hand.

### U8. Extra verifier seat
- **Goal:** the breaker (other provider) or the auditor (Claude Code) chosen by Decision 4, with its mandate, appearing in the roster and the recording, whose veto can block a stage.
- **Covers:** R3
- **Files:** `mandates/breaker.md` or `mandates/auditor.md`
- **Depends on:** U7
- **Status:** todo
- **Tests:**
  - happy: the extra seat posts a verdict on the practice track → the validator counts it.
  - edge: a seat on another provider does not appear in the recording → fall back to an auditor on Claude Code.
  - error: the extra seat and the reviewer disagree → the stage stays open until both accept.

### U9. Real-track iteration and freeze
- **Goal:** runs on tablekeeper until one reaches the target stage with every suite at 0.5 or more and no overshoot; the stage-2 UI follows `docs/DESIGN.md`; mandates and brief are frozen with their SHA-256 hashes.
- **Covers:** R4, R10, R11
- **Files:** `mandates/`, the tablekeeper brief, `docs/FACTORY-DESIGN.md` (amendment log)
- **Depends on:** U7
- **Status:** todo
- **Tests:**
  - happy: an iteration run's stage folders under the harness in isolated mode → each suite 1..N at 0.5 or more. Covers AE7.
  - edge: the stage-2 UI at 375 px in every state the spec names → no horizontal overflow. Covers AE11.
  - error: suite N+1 passes completely → the folder is flagged as overshoot before the freeze.

### U10. Room validator v2
- **Goal:** the validator also compares the observed mention graph with the declared routing, counts ping-pong cycles against repair cycles, and separates errors from warnings.
- **Covers:** R3, R9
- **Files:** `tools/validate_room.py`
- **Depends on:** U4
- **Status:** todo
- **Tests:**
  - happy: an iteration recording → prints the mention matrix and cycle counts.
  - edge: an undeclared mention edge → reported as an error.
  - error: a slow handoff → reported as a warning, exit 0.

### U11. Judged run
- **Goal:** one clean run on tablekeeper in a fresh room and a fresh public repo, from one dispatch, with the frozen mandates and brief, and the machine awake throughout.
- **Covers:** R4, R5 · F1
- **Files:** the delivery repo
- **Depends on:** U9
- **Status:** todo
- **Tests:**
  - happy: the judged recording → exactly one human message and the validator exits 0. Covers AE5.
  - edge: the run ends below the target stage → the reached stage is reported as is, with no rerun steering.
  - error: a gate fails mid-run → the run is repeated once in a new usage window.

### U12. Packaging
- **Goal:** the recording downloaded and redacted with the redaction recorded, the event checks and the package checks green on a fresh clone, and the practice track re-run with the frozen mandates as evidence of genericity.
- **Covers:** R4, R7 · F4
- **Files:** `room.json`, `evidence/`, the delivery repo
- **Depends on:** U11
- **Status:** todo
- **Tests:**
  - happy: a fresh clone under the harness check and the isolated run → both clean. Covers AE7.
  - edge: a credential found in the recording → replaced and listed in the packaging record.
  - error: a stage takes more than 30 s to report healthy in isolated mode → flagged before submission.

### U13. FACTORY.md and README
- **Goal:** hand-written `FACTORY.md` and `README.md` with the design, the seat table, the measured cost, the caught failures and the stage reached, every figure taken from a command; enough for another team to run the factory with a different brief.
- **Covers:** R6, R7, R8
- **Files:** `FACTORY.md`, `README.md` (delivery repo)
- **Depends on:** U12
- **Status:** todo
- **Tests:**
  - happy: each rejection in the recording → listed with finder, rejected commit and repairing commit. Covers AE9.
  - edge: someone follows only `FACTORY.md` and `mandates/` with the small-case brief → starts the seats and dispatches without asking. Covers AE12.
  - error: a figure in `FACTORY.md` differs from the cost command's output → fixed before submission.

### U14. Submission, deck and video
- **Goal:** the form text within limits, the PDF deck and a 3 to 4:30 min video that includes the room recording, a handoff, the blocking verdict and the running service; the form submitted.
- **Covers:** — (delivery)
- **Files:** `docs/submission.md`, `docs/deck.pdf`, the video file
- **Depends on:** U13
- **Status:** todo
- **Tests:**
  - happy: the video → shows the room, one REJECT and the service working, and lasts 3 to 4:30 min.
  - edge: a form field over its limit → trimmed before pasting.
  - error: the video lacks the room recording → not submitted until it is added.

### U15. Seat launch script
- **Goal:** an idempotent script that creates the seats, the room and the participants from the mandates and fails if a declared model does not match the real one.
- **Covers:** R8
- **Files:** `tools/launch.sh`
- **Depends on:** U1
- **Status:** todo
- **Tests:**
  - happy: run twice → the second run creates nothing new.
  - edge: the force-new-room flag → a fresh room for the judged run.
  - error: a mandate declares a model the seat does not run → exits non-zero.

### U16. Genericity metric and verdict hash chain
- **Goal:** the distance between the mention graphs of the practice-track and judged runs as a published figure, and each verdict citing the hash of the previous one.
- **Covers:** R1, R7
- **Files:** `tools/validate_room.py`
- **Depends on:** U10, U12
- **Status:** todo
- **Tests:**
  - happy: two recordings with the same mandates → a small, reproducible distance.
  - edge: a stage with a single verdict → no previous hash required.
  - error: a missing verdict in the chain → reported by position.

## Cut line
| Tier | Units | Why |
|---|---|---|
| must | U1, U2, U3, U4, U5, U6, U7, U9, U11, U12, U13, U14 | eligibility, the blocking verdict, the measured cost and the submission; without them there is no entry |
| should | U8, U10 | a second verifier and the mention audit strengthen Teamwork but the three base seats already meet the gates |
| cut | U15, U16 | seats can be created by hand; the genericity figure and the hash chain add evidence but no requirement is left uncovered |

## Risks
- No rejection happens in the judged run — likelihood: media — mitigation: acceptance-first checks written before the build (U2), rehearsed on U6 and U7 — fallback: the video shows the rejection from the practice-track run, labelled as such, and `FACTORY.md` reports the judged run honestly.
- Shared Max usage runs out mid-run — likelihood: media — mitigation: measure U6 and U7 cost with U5 and start U11 at the beginning of a clean window — fallback: plan B seat on paid Gemini for a verifier.
- A seat stalls on a permission prompt or a dead peer — likelihood: media — mitigation: preflight with no manual approvals and a bounded wait rule in the mandates — fallback: the stall is recorded as the stage result, no human input.
- Token usage cannot be read per seat — likelihood: baja (transcripts carry usage; only the desktop-launched location is unconfirmed) — mitigation: U5 reads the transcripts, deduplicated by message id — fallback: time plus partial tokens, labelled partial.
- The `band` CLI subcommands in the design doc do not exist — likelihood: alta — mitigation: U1 verifies them before anything depends on them — fallback: manual seat creation from the desktop app (U15 is cut).
- A credential ends up in the recording — likelihood: media — mitigation: no seat prints auth headers — fallback: redaction recorded in U12.

## Out of scope
- Using A2A or AGNTCY as the transport between seats.
- Automatic model tuning from past runs.
- Typed-decision models as guardrails.
- Moving the test cases into a standalone use-cases document.
- The pocketful track, an orchestrator that calls agents in turn, a dashboard as the deliverable.
- Cut in this plan: the seat launch script (U15) and the genericity metric with the hash chain (U16).
