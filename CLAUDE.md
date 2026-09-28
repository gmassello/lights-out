@~/Documents/dotfiles/projects/hackathon/CLAUDE.md

Canonical docs: `docs/BRIEF.md` (product contract, R/F/AE), `docs/PLAN.md` (units U1…, cut line),
`docs/USE-CASES.md` (how each AE is proven), `docs/FACTORY-DESIGN.md` (design reference, in Spanish).
The service is built by the factory: never write code in a `stage-N/` folder by hand, and never read
the track tests (`*/test/` in the kickoff repo).

## Commands

The event harness lives in the kickoff clone at `~/Documents/dark-factory-wearedevs` and must run
from there. `<result>` is the absolute path of the factory's result repo.

```bash
# install (harness venv in the kickoff clone; Docker daemon must be running: `colima start`)
cd ~/Documents/dark-factory-wearedevs && python3 -m venv .venv && .venv/bin/python -m pip install -r harness/requirements.txt && .venv/bin/python -m playwright install chromium
# run in dev: not applicable — the seats build and run the service
# full suite of a track against a result repo
cd ~/Documents/dark-factory-wearedevs && .venv/bin/python -m harness run --track toy --repo <result> --all --mode isolated --out ../band-work/checks/all
# a single test: one stage (runs suites 1..N plus the overshoot check on N+1)
cd ~/Documents/dark-factory-wearedevs && .venv/bin/python -m harness run --track toy --repo <result> --stage 1 --out ../band-work/checks/s1
# small case (own checks, against a running service)
python3 cases/small/checks.py http://localhost:8080
# room validator: protocol lines, commits, non-author ACCEPT, repairs, one human message
python3 tools/validate_room.py <result>/room.json <result>
python3 tools/validate_room.py --self-check
# cost meter: tokens per seat inside a stage window (seat alone resolves its sessions via band usage)
python3 tools/measure_cost.py <start-iso> <end-iso> coordinator builder reviewer
python3 tools/measure_cost.py --self-check
# gate before submitting: package check, offline
cd ~/Documents/dark-factory-wearedevs && .venv/bin/python -m harness check <result> --track tablekeeper
# docs gate: brief, plan and use-cases traceability
python3 ~/.claude/skills/hackathon-plan/scripts/check_docs.py . && python3 ~/.claude/skills/hackathon-plan/scripts/check_docs.py . --use-cases
# lint / type-check / deploy: not applicable
```
