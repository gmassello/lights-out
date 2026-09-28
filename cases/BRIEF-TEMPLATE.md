# <Product name> — <case name>

The brief is the only thing that changes between cases; the mandates stay the same. The human
pastes the filled brief, whole, as the single dispatch message. Keep each section to what the
section asks for; how the seats work is in the mandates, not here.

## Goal

<One or two sentences: what the service is and who it is for. Say if the case exists to exercise
the factory rather than to challenge the implementation.>

## Spec

<The complete contract of what gets built, per stage if it changes: runtime contract (bind address,
port variable and default, health and reset routes, error shape), data shapes, routes or screens,
and every rule with its error. Paste the source spec whole; never summarise or point to a file the
seats cannot read.>

## Milestones

<One stage per folder `stage-N/`, each extending the previous one. All stages go in this one
dispatch. For each stage: what it adds and which part of the Spec it covers.>

## Constraints

- Result repository: `<absolute path, filled at dispatch>`
- <Build rule: each `stage-N/` builds from its own folder alone.>
- <Runtime limits: architecture, network, resources, time to healthy.>
- <What is out of bounds: files not to read, folders not to touch.>

## Done state

<Observable conditions that close each stage: what builds, what answers, what a reader of the
folder finds. Each one checkable by a command.>

## Escalation

Anything the spec leaves open is decided by the coordinator with the simplest option consistent
with this brief, and recorded as an assumption in the room. No question goes to the human during
the run.
