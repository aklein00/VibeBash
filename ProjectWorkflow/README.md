# ProjectWorkflow

An example of the agent setup in the Carson James video. It sits inside VibeBash so it can be cloned, and it does not change the other projects in this repo.

Read in this order:

1. `implementation-plan.md` — the workflow, which tool is better where, and the risks.
2. `business-setup.md` — what his business actually is, and how a membership in that shape gets stood up.
3. `transcript.md` — what he says in the video.
4. `vault/Home.md` — the stub you can click through.

## What is stubbed

```
vault/                  Obsidian vault. Open this folder, not the whole repo.
  products/Fieldnote/   One fictional product and its master note.
  jobs/                 The repeating jobs. Each index note is about eight steps.
  daily/                One sample daily note with an index on top.
claude/                 CLAUDE.md and MEMORY.md for a Claude Code session started here.
cursor/                 A Cursor rule. Cursor will not load it from this path.
codex/                  AGENTS.md for a Codex run started here.
```

Fieldnote is not a real product. The scoreboard numbers are placeholders.

## Turn it on without wrecking the rest of the repo

- Obsidian: open `ProjectWorkflow/vault` as a vault.
- Claude Code: start it in `ProjectWorkflow/` so it reads `claude/CLAUDE.md`. Leave the `CLAUDE.md` at the root of VibeBash alone. That file is the game-studio guide.
- Cursor: copy `cursor/project-workflow.mdc` to `.cursor/rules/` only when you want it active. A root rule applies to every project in the repo.
- Codex: start it in `ProjectWorkflow/` so it reads `codex/AGENTS.md`. A copy at the repo root applies to every Codex task.

VibeBash is public. Use this tree as the pattern. Keep a live business vault in a private repo.
