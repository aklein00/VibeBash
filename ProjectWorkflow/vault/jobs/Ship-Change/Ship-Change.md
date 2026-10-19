# Ship-Change

Index note for a change that should become a diff. Cursor is the better tool when a person is watching. Codex is the better tool when this note is already specific and nobody needs to steer.

1. Read [[Write-Spec]]'s latest section, or the spec in today's daily note. If there is no spec, stop and say so.
2. Read [[codebase]]. If it still says the repo is unnamed, stop. Do not search the machine for credentials.
3. Read today's daily index. If another session already shipped this, stop.
4. Edit only the files the spec names.
5. Do not edit `vault/` except to append the daily note. Do not reorganize the product notes.
6. Do not add a new dependency, a new service, or a secret.
7. Show the diff, or describe the files changed, before calling it done.
8. Append the daily index: what changed, and that a person still has to look.

Risk: an unattended Codex run that is allowed to write the whole vault will "clean up" notes. This job allows a daily-note append and the code the spec named.
