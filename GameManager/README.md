# Game Manager

Centralized dashboard for tracking all game and app projects in the Side folder.

## Quick Start

```bash
cd /Users/arthurklein/Documents/Work/Side/VibeBash/GameManager
python3 server.py          # Start on port 8080
python3 server.py 8090     # Or use a custom port
# Open http://localhost:8080
```

> **Note:** Use `server.py` instead of `python3 -m http.server` — it serves the same static files but also provides the `/api/scan` endpoint needed by the Analyze Projects button.

## How It Works

- **`catalog.json`** is the single source of truth for all project data
- **`index.html`** is a static dashboard that reads catalog.json and renders project cards
- **`scanner.py`** scans the Side folder and reports differences vs the catalog

## Updating the Catalog

Edit `catalog.json` directly when a project's status changes. Key fields to update:

| Field | When to update |
|-------|---------------|
| `status` | Project moves between phases (e.g. prototype -> active-dev) |
| `completion` | Significant progress on a project |
| `completedMilestones` | A milestone is finished |
| `currentMilestone` | Moving to the next milestone |
| `notes` | After any review or when priorities change |
| `lastReviewed` | Every time you update the entry |

### Status Values

| Status | Meaning |
|--------|---------|
| `concept` | Idea only, no code |
| `pre-production` | Design docs but no implementation |
| `prototype` | Playable proof of concept |
| `active-dev` | Regular development work |
| `polished` | Feature-complete, needs minor polish |
| `shipped` | Released and playable |
| `on-hold` | Paused, may resume |
| `template` | Reference/template project |

## Running the Scanner

```bash
python3 scanner.py
```

The scanner walks `/Users/arthurklein/Documents/Work/Side/` and checks each project for:
- `package.json` (tech stack, version)
- `MILESTONES.md` (milestone tracking)
- `PRODUCTION_STATUS.md` (status docs)
- `game.config.json` (run.game deployment)
- `GDD.md` or similar (design docs)
- `.git/` (version control)

It outputs a report showing what it found vs what's in catalog.json. It does **not** auto-update the catalog — you approve changes manually.

## Checking Dependency Versions

First, generate a snapshot of current project dependencies:

```bash
python3 scanner.py --versions
```

This creates `versions.json` with each project's `package.json` dependency versions.

Then open the dashboard and click the **Check Versions** button. It will:
1. Load `versions.json` for current dependency versions
2. Query the npm registry for the latest published version of each package
3. Show an "outdated" badge on project cards with stale dependencies
4. Show a full version comparison table in each project's detail modal

Results are cached in localStorage for 24 hours to avoid repeated API calls.

## Export Progress Prompt

Each project's detail modal includes an **Export progress prompt** (or **Export milestone prompt**) button in the Milestones section.

- **Projects with milestones:** Generates a planning prompt that includes milestone status, project metadata, run.game status, and asks the LLM to ask you questions before planning.
- **Projects without milestones:** Generates a prompt to help create a MILESTONES.md, acknowledging what's already been built.

Click the button to copy the prompt to your clipboard, then paste it into Claude Code within the target project.

## Analyze Projects (Live Scan)

Click the **Analyze Projects** button in the header to scan the filesystem and compare against the catalog. This requires `server.py` to be running (not `python3 -m http.server`).

The scan checks every project in the Side folder and shows:
- Which projects are **in sync** with the catalog
- Which have **changed** (e.g., milestones were added, GDD was created)
- Which are **new** (not in the catalog yet)

## Catalog Schema

See `catalog.json` for the full schema. Each project entry has:

```
slug, name, path, status, completion, genre, techStack, platform,
description, hasMilestones, milestoneFile, totalMilestones,
completedMilestones, currentMilestone, milestones[], hasGDD,
hasProductionStatus, runGameDeployed, gitActive, lastReviewed, notes,
runGame { status, sdk, sdkVersion, gameConfigExists, gameId,
  featuresUsed, featuresMissing, summary, readiness }
```

## Roadmap

See [MILESTONES.md](MILESTONES.md) for the full production milestone plan (7 milestones). Next up: **Automatic Status Detection** — keep catalog.json accurate without manual editing.
