# Dark Factory (WeAreDevelopers × BAND) — event brief

Sources, read 2026-09-26: the lablab event page (HTML sections 01–10) and the official
participant guide, `docs/participant-guide.md` in
[band-ai/dark-factory-wearedevs](https://github.com/band-ai/dark-factory-wearedevs). The guide calls
itself "the authoritative rules". Anything neither source states is marked `not published`.
The project's own setup, plan and checklist live in `docs/PLAN.md`.

## Event

| | |
|---|---|
| Name | WeAreDevelopers x BAND present: Dark Factory (hackathon edition) |
| URL | https://lablab.ai/ai-hackathons/wearedevelopers-hackathon |
| Platform / organizer | lablab.ai (NativelyAI Inc.), official hackathon of WeAreDevelopers World Congress North America |
| Presented by | BAND (funds the $6,000 prize pool) |
| Technology partners | Docker (Docker Sandboxes), Featherless AI |
| Format | Fully online, open worldwide, one week. No on-site coding room |
| Team size | 1–6 people (solo allowed) |
| Kickoff repo | https://github.com/band-ai/dark-factory-wearedevs (specs, partial tests, harness, toy track) |
| Judges (page) | Andrii Stetsenko, Dharmendra Singh, Hardik Nahata, Amit Kumar Singh, Harshit Gupta, Rahul Nambiar, and others listed on the page |
| Sign-ups | 3,056 (2026-09-26) |
| Sign-up perk | Free ticket to WWC North America, San Jose, Sep 23–25 (already past) |

What gets built: a software factory in BAND Desktop — at least three coding-agent seats that plan,
implement, hand off evidence and independently check their own results — and the service that
factory builds, in four cumulative stages. "What you submit is the factory, the run that produced
the result, and the result."

## Timeline

Event zone PDT (America/Los_Angeles); local zone ART (America/Argentina/Cordoba). Converted with
`zoneinfo` from the page's `startAt`/`endAt` UTC values.

| Milestone | PDT | ART | UTC |
|---|---|---|---|
| Kickoff (all specs and tracks released at once) | Sat Sep 26, 09:00 | Sat Sep 26, 13:00 | 2026-09-26T16:00Z |
| **Submissions close** | **Mon Oct 5, 23:59** | **Tue Oct 6, 03:59** | 2026-10-06T06:59Z |
| Judging window | not published | not published | — |
| Winners announcement | not published | not published | — |

A commented-out block in the page source says "The judging window and the winners announcement
date are to be announced." Prize payout "may take up to 90 days".

## Prizes and tracks

Pool: $6,000 cash, split across the two tracks. You compete only against your own track.

| Track | Builds | "The hard part" | 1st | 2nd | 3rd |
|---|---|---|---|---|---|
| `tablekeeper` | Restaurant reservations, like OpenTable | a table must never be double-booked, under concurrency, retries and time zones | $1,500 | $1,000 | $500 |
| `pocketful` | Wallet and payments app, like Venmo | money must never be created, destroyed or spent twice, under concurrent transfers, retries and rounding | $1,500 | $1,000 | $500 |
| `toy` | Shared counter | Practice only, unscored; ships its full suite | — | — | — |

- **Award thresholds:** "A place is awarded only if the track has enough eligible entries: at least
  one for first, four for second, six for third. Unawarded prizes are not redistributed."
- **Featherless prize:** $300 in Featherless credits for the first winning team; which track is
  not published yet ("will be announced").
- **Featherless participant credits:** $25 of per-request credits per participant, first 1,000,
  promo code emailed before kickoff; signup takes a card.
- Winners are published as case studies (with permission): task, band, key design decision,
  verified result, cost and limitation.

### What each stage asks for (both tracks)

| Stage | Builds | Graded by |
|---|---|---|
| 1 | JSON API: idempotent writes, atomic multi-item operations, state export/import | API conformance |
| 2 | Browser UI, richer resource model, recovery from stale state and lost responses | API and Playwright, plus stage 1 |
| 3 | State over time: effective-dated rules or corrections with truthful history | API conformance, upgrades and concurrent writes, plus stages 1–2 |
| 4 | Changes to many existing records at once, atomically, without breaking history | Own suite and populated-state upgrades, plus stages 1–3 |

To qualify:
- **Minimum to be eligible: a complete stage 1.**
- A folder `stage-N/` claims its stage only if it passes **at least half of each suite 1..N**. It
  claims nothing if it also passes the whole suite N+1.
- The chain scores: a folder counts only if every earlier folder counts.

Share of the graded checks shipped with the kickoff repo (the rest is held back for judging):

| Stage | tablekeeper | pocketful |
|---|---:|---:|
| 1 | 83% | 79% |
| 2 | 41% | 35% |
| 3 | 11% | 9% |
| 4 | 21% | 16% |

## Judging criteria

Entries that pass the four gates (see Disqualifiers) are scored on:

| Criterion | Weight | Rule text (participant guide) |
|---|---:|---|
| Factory | 50% | "**Generic:** another team could point your mandates at a different problem. **Effective:** how far through the four stages it got with code that meets the spec, including what the shipped checks never asked. **Reusable:** `FACTORY.md` and `mandates/` are enough to stand it up, and explain your design choices and what they cost, measured time and model spend, and how the factory catches and recovers from bad work" |
| App | 25% | "What your factory built: a UI that is coherent, presentation-ready, responsive and clear in the states the stage-2 spec identifies, over code another developer could maintain" |
| Agent Teamwork | 25% | "Your seats did the work together, and without you. **Collaboration:** the seats really shared the work — more than one seat did it, review changed something, handoffs carried the whole task, and the code traces to the room. **Autonomy:** in the run you submit, the task you dispatch for each stage is the only human input — no steering, approvals, debugging hints or reruns until it passed." |

"We do not score chat volume, seat count or prompt length." One seat carrying 90% of the work reads
the same however many messages it sent; "a rejection counts when it changed the work".

## Required tech

| Required | How it is proven |
|---|---|
| **BAND Desktop**, ≥3 distinct seat identities you configured | `room.json` (full-session download from the Band console) lists the seats; `mandates/<seat>.md` per seat |
| A coding-agent harness per seat (Claude Code, Codex, GitHub Copilot, Cursor, OpenCode, or a BAND SDK runtime) | Each mandate starts with `Harness: <name as Band shows it>` and `Model: <exact model id>` |
| Docker | Each `stage-N/` has a `Dockerfile`; judges build it and talk to it over HTTP only, in isolated mode (internal network, no outbound access, 2 vCPU, 2 GiB) |
| Event harness (Python 3.12+) | Not submitted; `python -m harness check` / `run` are the local proof. Any language is allowed for the service |

Optional, no gate depends on them: Docker Sandboxes per seat, Featherless models via OpenCode.

## Submission requirements

**lablab form** (fields listed on the event page; character limits and file formats come from the
generic lablab form, not from this event's page — re-check when the form opens):

| Step | Field | Limit / format |
|---|---|---|
| Basic | Project title | 5–50 chars |
| Basic | Short description | 50–255 chars |
| Basic | Long description | 600–2000 chars |
| Basic | Technology & category tags | closed catalog |
| Media | Cover image | image |
| Media | Video presentation | uploaded `mp4`/`mov`; max duration not published |
| Media | Slide presentation | uploaded PDF |
| Repository | Public GitHub repository URL | cloneable without BAND membership |

Demo platform and application URL appear commented out on the page, so this event does not ask
for them.

**Video:** must include "a recording of the BAND Desktop room that generated your solution, and a
walkthrough"; the guide adds "the room, a handoff between seats, and the result it produced. A
slideshow about the factory is not the same as the factory."

**Presentation and video content:** factory design, what it cost, a bad result it caught, and the
stage reached.

**Repository layout:**

```text
README.md     team, track, how to read the repo (written by hand)
FACTORY.md    seats, design choices, what failed, measured cost and time, how bad work is caught (by hand)
mandates/     one .md per seat, named after the seat as the room shows it, ≥3
room.json     Band console → Download full session, renamed, contents unchanged except redacted credentials
stage-1/ … stage-4/   Dockerfile + RUN.md + source; each a copy of the previous stage, extended; no nested .git
```

Submit only completed stage folders. Push the seats' history without amending, rebasing or
squashing.

## Disqualifiers

**Four gates — fail any one and the entry is not ranked:**
1. Three or more distinct BAND Desktop seat identities you configured, each with a mandate file
   named after it that names harness and model.
2. The room log shows `@handle` messages between at least two of your seats, with a reply in each
   direction.
3. `stage-1/` builds and serves from a clean container by following its `RUN.md`.
4. Mandates are generic and the code is written to the spec, not to the tests.

**Rules that void an entry or a stage:**

| Rule | Effect |
|---|---|
| "A mandate naming track-specific detail disqualifies the entry" (endpoint paths, field names, error codes) | Entry disqualified |
| "Code written to the tests disqualifies the entry" — enforced after submissions close | Entry disqualified |
| "A video without the room recording disqualifies your team" | Entry disqualified |
| "A service that does not start from a clean container" | Scores zero (gate 3 for stage 1) |
| "Code you wrote by hand does not count" | That stage does not count (and the chain above it stops) |
| Human input after dispatch in the submitted run (steering, approvals, hints, reruns) | Effect not published; the run must be in a fresh room and repo, and only it is judged for Agent Teamwork |
| Stage folder that is its own git repo | Arrives empty in a clone |
| Credentials in the repo or `room.json` | Must be rotated and redacted; nothing redacts `room.json` automatically |
| "Submissions must be original and MIT-compliant" | Eligibility (page, prizes section) |
| Age and country | 18+; US-sanctioned countries excluded (lablab terms) |

## Blockers

Prerequisites only the user can clear, before the form can be submitted:

1. **Sign up on the event page** — the page still shows "Sign up".
2. **Connect Discord and join the lablab server** (OAuth on the user's account).
3. **Create a team and be its admin** — a closed team of one is enough. Until then *Submit Project*
   stays disabled.
4. **BAND account + BAND Desktop** installed, CLI and coding-agent plugin, readiness check passing.
5. **Model access for every seat** (own subscription/API key, or Featherless credits if the promo
   email arrives).
6. **`room.json` download** from the Band console — manual, no harness command fetches it.
