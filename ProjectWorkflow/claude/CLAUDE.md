# CLAUDE.md

How we operate when Claude Code is started in `ProjectWorkflow/`. This file does not replace the `CLAUDE.md` at the root of VibeBash. Starting Claude at the repo root will not read this file.

## Memory

All memories live in `../vault` relative to this file (`ProjectWorkflow/vault`). `MEMORY.md` beside this file is only a pointer. Do not create Claude's default memory files for this project.

## Rules

- Read the job's index note, then follow its wiki-links, before doing the job.
- Append an existing note. Make a new note only when the thing is a new product, a new job, or a new day.
- A campaign, an email, and an ad brief are appended to `vault/products/Fieldnote/campaigns.md` while Fieldnote is the sample product.
- End every session by appending today's file in `vault/daily/`. One line in the index, detail only if the index would be unclear without it.
- Do not publish, send, or spend. Drafts stay marked unapproved.
- Do not write API keys, tokens, customer lists, or billing exports into the vault.
- Fieldnote is an example. Do not treat its prices or its zeroed scoreboard as facts about a real business.

## Risks in this tool

Claude Code sees the vault only if this process can read `ProjectWorkflow/vault`. A session on another machine does not share the memory until it has the same files. Two sessions appending the same daily note can overwrite each other. Following every wiki-link is the point of the master note, and it is also how a loose note pulls too much into context. The daily note will contain whatever the agent decides was worth keeping. Read it before you trust the next session.

Cursor and Codex do not read this file. The same rules are in `../cursor/project-workflow.mdc` and `../codex/AGENTS.md`. Change all three together or they drift.
