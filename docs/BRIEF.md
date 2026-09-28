# Lights-out — Brief

## Summary
A software factory of three or more coding-agent seats in a BAND room that takes a written spec and,
from a single dispatch, delivers a verified service stage by stage. The seat that verifies commits
its acceptance checks before any code exists, and its verdict can block the work.

## Problem frame
The event asks for a factory, not an app: judges score how generic, effective and reusable it is
(Factory 50%), whether the seats really worked together without a human (Agent Teamwork 25%), and
the quality of what it built (App 25%). A single-agent pipeline with a chat log attached fails
BAND's own "delete test". A reviewer that only looks at finished code tends to approve what it sees,
so the rejection that proves the room matters may never happen in the one run that is judged, and
nothing may be injected into that run. The factory has to make dissent likely by construction.

## Actors
- A1. Operator — writes the brief, starts the seats and sends the one dispatch; does nothing else during the run.
- A2. Coordinator seat — splits the spec into tasks, routes work, keeps the amendment log and closes each stage.
- A3. Builder seat — writes the service code and answers every finding.
- A4. Reviewer seat — publishes acceptance checks from the spec before the build and issues the verdict against them.
- A5. Breaker or auditor seat — optional; probes the running service from outside with veto power.
- A6. Judge — reads the repo, `FACTORY.md`, the mandates, the room recording and the video.

## Requirements
- R1. The same mandates run unchanged on problems from different domains; only the brief changes. [criterion: Factory]
- R2. Before any code for a stage, the verifying seats publish acceptance checks derived from the spec, and every verdict cites them. [criterion: Factory]
- R3. A stage closes only with an ACCEPT from a seat other than the author of the candidate, and a REJECT sends the work back with the failing check. [criterion: Agent Teamwork]
- R4. Each stage folder claims its stage (at least stage 1, target stage 4) with code that meets the spec, including what the shipped checks never ask. [criterion: Factory]
- R5. The judged run takes one human dispatch and no other human input, and survives a seat restart or an unanswered wait on its own. [criterion: Agent Teamwork]
- R6. Time and model spend per stage are measured by a command and published in the room and in `FACTORY.md`. [criterion: Factory]
- R7. Every rejection is traceable from the finding to the rejected commit and to the commit that repaired it. [criterion: Factory]
- R8. `FACTORY.md` and the mandates are enough for another team to stand the factory up and understand its design choices and their cost. [criterion: Factory]
- R9. Every handoff and verdict names the commit it refers to, so each line of code traces to a room message. [criterion: Agent Teamwork]
- R10. The stage-2 interface is coherent, responsive and clear in every state the spec names, following `docs/DESIGN.md`. [criterion: App]
- R11. Each stage extends the previous one without erosion or bloat, in code another developer could maintain. [criterion: App]

## Key flows
- F1. **Dispatch** — the operator starts the seats and sends one message with the brief for all stages → the coordinator sets the stage goal and tasks → the run proceeds with no further human input. (A1, A2; R5)
- F2. **Stage cycle** — the coordinator hands the stage spec to the reviewer and breaker → they publish acceptance checks → the builder receives the task with the full spec and the checks → builds and hands off a commit → the reviewer verifies against its checks → ACCEPT closes the stage, REJECT returns to the builder, who accepts, disputes or asks for clarification → repeat within the round cap. (A2, A3, A4, A5; R2, R3, R7, R9)
- F3. **Recovery** — a seat restarts or stops answering → it reattaches under the same identity, reads the room and resumes its last item, or the coordinator records the wait and retries once → the round count is not reset. (A2; R5)
- F4. **Handover to judges** — after the run, the room recording is downloaded, the event checks pass on a fresh clone, and `FACTORY.md` reports design, cost, caught failures and the stage reached. (A1, A6; R4, R6, R7, R8)

## Acceptance examples
- AE1. **Covers R2.** Given stage N has been dispatched, when the builder makes its first commit for stage N, then the room already holds the reviewer's acceptance checks for stage N, posted earlier.
- AE2. **Covers R3.** Given a builder handoff at commit X that violates one acceptance check, when the reviewer verifies it, then the reviewer posts REJECT naming the check, and the stage does not close until a later commit gets ACCEPT.
- AE3. **Covers R3.** Given a candidate authored by the builder, when the only ACCEPT for it comes from the builder itself, then the stage stays open.
- AE4. **Covers R1.** Given the small case, the practice track and the real track, when each run starts, then the mandate files have the same hashes in all three and contain no domain vocabulary from any of them.
- AE5. **Covers R5.** Given the judged run's room recording, when its messages are counted by sender type, then there is exactly one human message.
- AE6. **Covers R5.** Given a seat is restarted mid-stage, when it reattaches, then it keeps its identity and the stage continues without a human message.
- AE7. **Covers R4.** Given the delivered stage folders, when the event harness runs every suite in isolated mode, then each suite 1..N scores at least 0.5 and suite N+1 does not pass completely.
- AE8. **Covers R6.** Given a finished stage, when the cost command runs over that stage's window, then its time and token totals match the figures posted in the room and in `FACTORY.md`.
- AE9. **Covers R7.** Given a REJECT at commit X, when `FACTORY.md` is read, then it lists the finding, who found it, commit X and the repairing commit.
- AE10. **Covers R9.** Given any handoff or verdict message, when its last line is parsed, then it names a stage and a commit that exists in the repository history.
- AE11. **Covers R10.** Given the stage-2 interface at 375 px wide, when each state the spec names is shown, then nothing overflows horizontally and each state is distinguishable.
- AE12. **Covers R8.** Given only `FACTORY.md` and `mandates/`, when another person follows them with a different brief, then they can start the same seats and dispatch without asking.

## Key decisions
- Track: tablekeeper — chosen over pocketful. settled: user-directed
- The central bet is a blocking verdict — chosen over dependent handoffs, BAND-enforced mention limits or a runtime roster as the headline signal, because judges count "a rejection when it changed the work". settled: user-approved
- Acceptance first: verifiers commit their checks from the spec before the build — chosen over build-then-inspect and over two builders reviewing each other, because it makes a rejection likely without injecting faults and without extra seats. settled: user-approved
- The coordinator also plans; no separate planner seat — chosen over a planner seat because review, not planning, is the bottleneck and a fixed role pipeline scores low. settled: user-approved
- All seats on the Claude Max subscription; a paid Gemini seat is plan B and a Featherless seat is plan C — chosen over the free Gemini tier, whose limits can stall a seat mid-run. settled: user-directed
- Three test cases of growing size in different domains: an own trivial case, the practice track, then the real track. settled: user-directed

## Scope boundaries
### Deferred
- Using A2A or AGNTCY as the transport between seats.
- Automatic model tuning from past runs.
- Typed-decision models as guardrails.
- Moving the test cases into a standalone use-cases document.
### Outside this product
- The pocketful track.
- An orchestrator that calls agents in turn outside the room.
- A dashboard as the deliverable.

## Assumptions
- A breaker seat on another provider shows up in the room roster and in the recording; if not, the second verifier runs on Claude Code as an auditor.
- Per-seat token usage can be read from each seat's session transcripts; if not, cost is reported as time plus whatever the tooling shows, labelled as partial.
- The reviewer's model is strong enough to write useful acceptance checks before the build; if not, it moves to the strongest model.

## Outstanding questions
- How seats are created: manual onboarding in the desktop app or a launch script. — blocks: F1 | resolve before planning: no
- Which model runs the reviewer. — blocks: R2 | resolve before planning: no
- Breaker, auditor or both as the extra seat. — blocks: F2 | resolve before planning: no
- Whether seats push at each stage close or the operator pushes at the end. — blocks: R9 | resolve before planning: no
