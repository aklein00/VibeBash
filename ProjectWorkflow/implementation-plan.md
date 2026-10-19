# Project workflow: Cursor, Codex, and Obsidian with Claude

How to run the setup from the Carson James video on whatever you are building. This folder is its own experiment. It does not describe or change the other projects in this repo.

The video is a filing rule, plus three tools that can all read the same files.

1. One folder per business, product, or client.
2. One master note with the same name as the folder. It is an overview, and it wiki-links to the other notes in the folder.
3. A Jobs folder. Each repeating job (a campaign, an email, an ad, a release, a spec) has an index note of about eight steps. Each step links outward.
4. `CLAUDE.md` is "how we operate." The strict rule is anti-bloat: append an existing note, and make a new note only when the thing is actually new.
5. `MEMORY.md` does not hold the memories. It points at the vault.
6. The agent writes the daily note. A short index sits at the top. The detail sits underneath.
7. Cursor, Codex, and Claude Code all read and write that vault, so a second session can see what the first one did.
8. API keys and MCP servers are configured once, outside the notes.

His boot command is one sentence: "We're going to create a campaign. We're going to do this offer." The index note does the rest.

## The vault

The example is already stubbed in this folder. Open `ProjectWorkflow/vault` as an Obsidian vault. Leave the rest of the VibeBash repo outside that vault so Obsidian is not indexing the other projects.

```
ProjectWorkflow/
  vault/
    Home.md
    products/Fieldnote/          # fictional product, one master note plus the notes it links
    jobs/                        # Create-Campaign, Draft-Email, Make-Ads, Write-Spec, Ship-Change
    daily/2026-10-16.md
  claude/CLAUDE.md               # how we operate; not the repo-root CLAUDE.md
  claude/MEMORY.md               # pointer only
  cursor/project-workflow.mdc    # Cursor does not load this until it is copied
  codex/AGENTS.md
```

Fieldnote is a fake membership used so the links resolve. It is not a real product and the numbers in `scoreboard.md` are placeholders.

A master note is short. It says what the product is, who pays, what the current offer is, and then it links. Reading that one note is what sends the agent through the folder. A job note does the same thing one level down, and it links back to the product master note so the agent has the product in hand before it does the task.

### Daily note

```markdown
# 2026-10-16

## Index
- <Product>: campaign drafted for the spring offer; page not approved
- <Repo>: shipping the billing fix; spec is jobs/Ship-Change

## Detail
...
```

The agent writes this at the end of a session, and in the middle of a session when something big landed. The next session, in any tool, reads the index lines before it opens a whole note.

### The three instruction files say the same thing

| Tool | File in this example | What it is for |
| --- | --- | --- |
| Claude Code | `claude/CLAUDE.md` and `claude/MEMORY.md` | How we operate, and a pointer. Memories live in `vault/`. Append notes. Start every job by reading that job's index note, then the product master note it links to. |
| Cursor | `cursor/project-workflow.mdc` | The same pointer and the same anti-bloat rule. When a chat finishes, append the daily note. Cursor only auto-loads rules from the repo-root `.cursor/rules/` directory. |
| Codex | `codex/AGENTS.md` | The same pointer. A job is finished when its steps are done and the daily note has a new index line. Codex reads `AGENTS.md` from the directory it was started in, or from the repo root. |

Keep those three files short. The procedures live in the job notes. A long instruction file is the pile of memory he started with, about 107 files, which he had Claude merge down to about 17.

## Obsidian + Claude Code

This is the setup in the video, and it is the right home for the memory.

Claude Code already looks for `CLAUDE.md` and a memory file. Point the memory file at the vault, and tell it to append instead of spawning notes. Obsidian is what makes the wiki-links, the daily-note list, and the graph something you can read. Claude Code is what walks the links and writes the page, the email, or the log.

Use it when the result is a note, a procedure, a decision, or a handoff. Boot it with one sentence: "We're creating a campaign for this offer. Read the Create-Campaign job." Let it follow the links. At the end, have it append today's daily note, index line first.

It is the better front door for campaign copy, emails, ads briefs, design docs, and anything you will want to reread in six weeks. It is also the better place to consolidate. If Claude has been writing memory files into its default directory, bring them into the vault, merge them once, and delete the duplicates.

Keep API keys and MCP config in Claude's own settings. He mentions them once, as setup. The vault should not contain secrets.

## Cursor

Cursor is the better front door when the result is a change to code you are looking at.

The vault can tell Cursor what the product is and what "done" means. Cursor is the place that edits the files, shows you the diff, and lets you stop a bad change. Obsidian will describe a code change and leave the repo untouched. A project rule should point at the vault and require an index line in the daily note when the session ends, or the next chat starts cold.

Use Cursor for the job whose output is a diff you want to review while you are there: a feature, a bugfix, a migration, a script. Keep the spec in the vault. Do the editing in Cursor.

## Codex

Codex is the better front door when the job is already written down and you want it run without you watching.

An eight-step index note is a Codex task. `AGENTS.md` points at the job note and at the product master note. You hand it the same sentence he uses, and it returns a diff. That beats sitting in Cursor when you have several of those jobs and you do not need to steer each one. It beats Claude-in-Obsidian when the output has to be code that actually runs, because the vault does not execute the repo.

Codex will follow links if `AGENTS.md` tells it to, and it will forget the shape of the vault when the task ends unless it wrote the daily note. Give an unattended run write access to `vault/daily/` and read access to the rest, so it appends the log and does not reorganize the graph.

## Which one is better where

| You are doing this | Better tool | Why it wins |
| --- | --- | --- |
| Holding the product knowledge, the SOPs, and the daily log | Obsidian + Claude Code | Wiki-links are the loop he uses. You can read the graph. Claude's memory file can be pointed at it. Sessions share the files. |
| Writing or consolidating a procedure, a campaign, an email, a spec | Obsidian + Claude Code | The output is markdown you will reread. Bloat control matters more than a diff view. |
| Editing the repo with you in the loop | Cursor | You see the diff and stop a bad change before it lands. The vault remembers why. Cursor does the edit. |
| A specified job that should finish as a diff while you are away | Codex | The index note is the spec. Codex takes a spec and returns a change. |
| Several of those jobs at once | Codex | Unattended runs. Cursor wants you present. Obsidian will not execute the script. |
| Two agents on the same product the same day | The vault, read by all three | The daily note is the message bus. Whichever tool does the task, it appends an index line or the others will redo the work. |

Obsidian is the memory. Cursor is the bench. Codex is the night shift. The failure mode is letting each one keep a private memory. His fix is the pointer: the memories live in the vault.

## Sequence

The folders are already here. Turning the example on is a copy, not a rewrite of the rest of this repo.

1. Open `vault/` as its own Obsidian vault and read `Home.md`, then `products/Fieldnote/Fieldnote.md`. Follow the links once so you can see the chase he describes.
2. Run Claude Code with `ProjectWorkflow/` as the working directory so it reads `claude/CLAUDE.md` from that directory. Do not replace the `CLAUDE.md` at the root of VibeBash. That file is the game-studio guide.
3. Copy `cursor/project-workflow.mdc` into `.cursor/rules/` only when you want Cursor to follow it. Until that copy exists, Cursor will not see the rule.
4. Start Codex in `ProjectWorkflow/` so it reads `codex/AGENTS.md`, or copy that file to the repo root when you want every Codex task to see it. A root copy applies to every project in the repo.
5. Run one job in Claude Code ("create a campaign for Fieldnote"), one in Cursor (a real code edit whose spec is `jobs/Ship-Change`), and one in Codex (the same ship-change, unattended). Each appends `vault/daily/`.
6. Start the next session in a different tool by reading that daily note's index. If it knows what the others did, the workflow is working.

## Risks, and how the three places differ

The same notes behave differently depending on which program is reading them and where the files actually are.

**This repo is public.** Anything committed under `vault/` can be cloned by anyone. The Fieldnote notes are fiction for that reason. A live business vault (real offers, customer notes, revenue, ad accounts) belongs in a private repo or a private Obsidian sync. This folder is the pattern, not the place to keep the real memory.

**The instruction files are not interchangeable just because they say the same words.**

- Obsidian plus Claude Code is the better memory. Claude Code reads `CLAUDE.md` in the directory you started it in, and `MEMORY.md` only works if it points at a vault that this process can see. A Claude session on your laptop and a Claude session in the cloud share a memory only when both have the same checkout. Two sessions appending one daily note can overwrite each other. The wiki-link chase is the feature, and it is also how one sloppy master note drags the whole product into context and the run gets slow or confidently wrong. Claude will write the daily note, including things you did not mean to keep. Read it.
- Cursor is the better bench for a diff you want to watch. It is the worse system of record. A chat ends, and the next chat is empty unless the rule wrote the daily note. Cursor loads rules from `.cursor/rules/` at the repo root, not from `ProjectWorkflow/cursor/`. Copying the rule to the root makes it apply while you are in GameManager or MayaScripts too, and it can fight the root `CLAUDE.md`. A Cursor cloud agent sees git. It does not see an Obsidian vault that exists only on your computer.
- Codex is the better night shift once a job note is a real spec. It is the worse place to let loose on the vault. An unattended run edits whatever `AGENTS.md` allows, including reorganizing notes you meant to keep stable. `AGENTS.md` at the repo root governs every task in the repo. `AGENTS.md` inside `ProjectWorkflow/` governs a run that was started there. Codex in the cloud clones git. It will not see a vault that lives only in the Obsidian app, and it will not send the email or publish the ad. Those jobs stop at a draft in the vault.
- Keeping three copies of the rules means they drift. When you change the anti-bloat rule, change `claude/CLAUDE.md`, `cursor/project-workflow.mdc`, and `codex/AGENTS.md` together.
- Keys and MCP servers stay in each tool's own settings. A key written into a note so "the agent can find it" is now in git history.
- The folder does not produce the business in the video. It produces a shared memory and a short list of jobs. The offer is still yours to choose, and a page the agent calls finished still needs a person.
