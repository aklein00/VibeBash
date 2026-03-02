# Prompt for Claude Code: Install BMad Game Dev Studio

Copy everything below the line into Claude Code.

---

## Context

I have BMad Method v6 (with Game Dev Studio module) already installed in my VibeBash workspace at `/Users/arthurklein/Documents/Work/Side/VibeBash`. The installation was done targeting Cursor (`.cursor/commands/` slash commands), but I primarily use Claude Code. I need you to re-install BMad properly targeting Claude Code.

## What BMad Is

BMad Method (https://github.com/bmad-code-org/BMAD-METHOD) is an AI-driven agile development framework. It installs specialized AI agent personas and guided workflows into a project. The Game Dev Studio (GDS) module adds game-specific agents. It installs via `npx bmad-method install` (interactive installer, Node.js v20+ required).

The installer creates:
- A `_bmad/` directory with agents (markdown persona files), workflows (yaml + markdown), config files, and manifests
- IDE-specific integration files (for Cursor: `.cursor/commands/`, for Claude Code: `.claude/` commands or CLAUDE.md rules)

## What I Need You To Do

### Step 1: Re-run the BMad installer targeting Claude Code

Run the interactive installer from my VibeBash workspace:

```bash
cd /Users/arthurklein/Documents/Work/Side/VibeBash
npx bmad-method install
```

The existing `_bmad/` folder from the Cursor install is already there. The installer should detect it and offer an update/modify flow.

During the interactive prompts, make these selections:
- **Installation directory**: Accept default (VibeBash)
- **Action**: Update/modify the existing installation (to add Claude Code as a tool)
- **Modules**: Keep BMad Method (BMM) and Game Dev Studio (GDS) selected -- they're already installed
- **Tools/IDEs**: Select **Claude Code** (in addition to or instead of Cursor)
- **Module config**: Accept all defaults (project name: VibeBash, experience: intermediate, etc.)
- For any "Accept Defaults?" prompts: Yes
- For any game engine selection: Select "other" (my games are HTML5, not Unity/Unreal/Godot)

If the installer asks about custom modules/agents/workflows: No.

### Step 2: Verify the Claude Code integration was created

After the installer completes, verify that Claude Code integration files were created. BMad for Claude Code typically creates one or more of:
- `.claude/commands/` directory with command files (similar to `.cursor/commands/`)  
- A `CLAUDE.md` or additions to the project's `CLAUDE.md` with BMad rules
- `.claude/skills/` with BMad skills
- Or some other Claude Code-specific integration

Check what new files were created and confirm they exist.

### Step 3: If the installer doesn't support Claude Code well, do a manual integration

If the installer doesn't create proper Claude Code integration, or if it only partially works, create the integration manually. Here's what needs to happen:

The existing `_bmad/` folder at `/Users/arthurklein/Documents/Work/Side/VibeBash/_bmad/` contains everything -- the agents, workflows, configs, and help catalog. The Claude Code integration just needs to make these accessible via slash commands.

**Option A: Create `.claude/commands/` files**

For each command that exists in `.cursor/commands/`, create an equivalent in `.claude/commands/` (or wherever Claude Code reads custom commands from). The key commands to create are:

Game Dev Studio (GDS) commands:
- `/bmad-help` -- Reads `_bmad/core/tasks/help.md` and follows instructions
- `/bmad-gds-quick-dev` -- Loads `_bmad/gds/workflows/gds-quick-flow/quick-dev/workflow.md`
- `/bmad-gds-quick-spec` -- Loads `_bmad/gds/workflows/gds-quick-flow/quick-spec/workflow.yaml`
- `/bmad-gds-brainstorm-game` -- Loads `_bmad/gds/workflows/1-preproduction/brainstorm-game/workflow.yaml` via the workflow executor at `_bmad/core/tasks/workflow.xml`
- `/bmad-gds-game-brief` -- Loads `_bmad/gds/workflows/1-preproduction/game-brief/workflow.yaml` via workflow.xml
- `/bmad-gds-gdd` -- Loads `_bmad/gds/workflows/2-design/gdd/workflow.yaml` via workflow.xml
- `/bmad-gds-narrative` -- Loads `_bmad/gds/workflows/2-design/narrative/workflow.yaml` via workflow.xml
- `/bmad-gds-game-architecture` -- Loads `_bmad/gds/workflows/3-technical/game-architecture/workflow.yaml` via workflow.xml
- `/bmad-gds-sprint-planning` -- Loads `_bmad/gds/workflows/4-production/sprint-planning/workflow.yaml` via workflow.xml
- `/bmad-gds-create-story` -- Loads `_bmad/gds/workflows/4-production/create-story/workflow.yaml` via workflow.xml
- `/bmad-gds-dev-story` -- Loads `_bmad/gds/workflows/4-production/dev-story/workflow.yaml` via workflow.xml
- `/bmad-gds-code-review` -- Loads `_bmad/gds/workflows/4-production/code-review/workflow.yaml` via workflow.xml

Agent loading commands:
- `/bmad-agent-gds-game-designer` -- Loads `_bmad/gds/agents/game-designer.md` persona
- `/bmad-agent-gds-game-architect` -- Loads `_bmad/gds/agents/game-architect.md` persona
- `/bmad-agent-gds-game-dev` -- Loads `_bmad/gds/agents/game-dev.md` persona
- `/bmad-agent-gds-game-solo-dev` -- Loads `_bmad/gds/agents/game-solo-dev.md` persona
- `/bmad-agent-gds-game-scrum-master` -- Loads `_bmad/gds/agents/game-scrum-master.md` persona
- `/bmad-agent-gds-game-qa` -- Loads `_bmad/gds/agents/game-qa.md` persona
- `/bmad-party-mode` -- Loads `_bmad/core/workflows/party-mode/workflow.md`

The pattern for workflow commands is:
1. Load `_bmad/core/tasks/workflow.xml` 
2. Read its entire contents (this is the workflow execution engine)
3. Pass the specific workflow YAML path as the 'workflow-config' parameter
4. Follow workflow.xml instructions exactly
5. Save outputs after each section

The pattern for agent commands is:
1. Load the agent's `.md` file
2. Follow the activation sequence in it (load config.yaml, greet user, show menu, wait for input)

The pattern for help is:
1. Load `_bmad/core/tasks/help.md`
2. Follow all instructions (it reads `_bmad/_config/bmad-help.csv` catalog and routes the user)

**Option B: Add to CLAUDE.md**

If `.claude/commands/` isn't supported, add a section to the project's `CLAUDE.md` at `/Users/arthurklein/Documents/Work/Side/VibeBash/CLAUDE.md` that documents all the BMad commands and how to invoke them. Add it as a new section called "## BMad Game Dev Studio" near the top.

### Step 4: Update the VibeBash CLAUDE.md

Regardless of which integration method worked, add a brief section to `/Users/arthurklein/Documents/Work/Side/VibeBash/CLAUDE.md` documenting:
- That BMad is installed in this workspace (`_bmad/` folder)
- The key slash commands available
- That `/bmad-help` is the starting point
- That games are HTML5 for mobile (not Unity/Unreal/Godot)

Keep it concise -- just enough for Claude Code to know BMad exists and how to invoke it. The detailed guide is already at `Brainstorming/BMAD_GUIDE.md`.

### Step 5: Confirm everything works

After setup, run `/bmad-help` to verify the integration works. It should:
1. Read `_bmad/_config/bmad-help.csv`
2. Detect available modules (BMM and GDS)
3. Show you what workflows are available and what to do next

## Important Details

- My games are **HTML5 for mobile** (Venus/run.game platform). Not Unity, not Unreal, not Godot.
- I already have a global `~/.claude/claude.md` with development standards, Venus publishing instructions, and image generation setup
- I already have global skills at `~/.claude/skills/` (generate-image, setup-image-style, new-venus-game)
- Node.js v24.13.0 and npm 11.6.2 are installed
- The existing `_bmad/` folder has: core module, BMM module (v6.0.0-Beta.7), GDS module (v0.1.5)
- The existing `.cursor/commands/` has 72 slash command files that can serve as reference for the Claude Code equivalents
- The `_bmad/_config/bmad-help.csv` contains the full catalog of all workflows, agents, and commands

## Success Criteria

When done, I should be able to:
1. Open VibeBash in Claude Code
2. Type `/bmad-help` and get guided workflow recommendations
3. Type `/bmad-gds-quick-dev` and have the solo-dev agent guide me through prototyping
4. Type `/bmad-agent-gds-game-designer` and have Samus Shepard load with her menu
5. All workflow outputs should save to the configured folders (`bmad-output/planning-artifacts/`, `bmad-output/implementation-artifacts/`, `docs/`)
