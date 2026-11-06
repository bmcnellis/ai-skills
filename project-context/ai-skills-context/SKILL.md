---
name: ai-skills-context
description: "Project-specific -- ai-skills repository only; do not apply to other projects unless explicitly asked. Context for maintaining BEM's public skills repository (github.com/bmcnellis/ai-skills), a sanitized one-way mirror of his live Claude Science skill registry. Covers the repo location and folder layout, which project-context skills are tracked, the scope hierarchy versus folder placement, the registry-to-repo sync and verification recipe, sanitizing tracked copies with sanitize-public-git and the placeholder map in scratch/, the registry publishing rules and gotchas, keeping README.md in step, and the rule that BEM commits and pushes himself. Load before adding, updating, moving, syncing or sanitizing any skill in that repo, editing its .gitignore or README, or answering questions about how the repo is organized."
scope: project-specific
project: ai-skills
---

# ai-skills repository context

> **Scope — project-specific: ai-skills repository only.** Do not apply to other
> projects unless explicitly asked. Load `sanitize-public-git` alongside this
> skill for any change that will be committed.

## What the repository is

- **Location:** `<data-root>/claude/ai-skills` (granted host path, rw).
- **Remote:** `git@github.com:bmcnellis/ai-skills.git`, branch `main`. **Public.**
- **Source of truth:** the live skill registry (`host.skills`). The repository
  is a **sanitized, one-way mirror** of it. Never copy repo files back over a
  live skill: the live copies need their real paths to work.
- **Commits and pushes are BEM's.** Prepare the working tree, verify it, and
  report what changed. Do not commit or push unless BEM asks in that turn.

## Layout

| folder | holds | tracked |
|---|---|---|
| `general/` | general-scope skills | yes |
| `specialized/` | task-oriented skills, whatever their scope | yes |
| `project-context/` | project context skills | only `neon-context/` and `ai-skills-context/` |
| `scratch/` | stray and temporary files, scan reports, `placeholder_map.json` | never |

`.gitignore` uses `project-context/*` with `!` exceptions for the two tracked
context skills. To track another one, add a `!project-context/<name>/` line
and sanitize it first. Untracked context skills are verbatim copies and stay
on disk; never trash them to "clean up".

**Folders are organizational, not a scope map.** `make-metadata-file-usgs` and
`manuscript-prose-voice` are general in scope but live in `specialized/` by
BEM's choice. Ask before moving a skill between folders. Each skill's
directory name equals its registry name, with no timestamp suffix; dated
snapshots are not kept in the repo.

## Scope markers

Every skill carries its scope in three places, which must agree:

1. Frontmatter: `scope: general`, or `scope: project-specific` plus `project: <name>`.
2. The head of the registry description: `General -- applies across all projects.`
   or `Project-specific -- <Project> only; do not apply to other projects unless explicitly asked.`
3. A `> **Scope — ...**` blockquote directly under the H1.

A project-specific skill is a **context** skill (name ends in `-context`) or a
**task** skill. Project-specific skills are not used outside their project
unless BEM asks.

## Syncing a skill from the registry

1. In `repl`: `r = host.skills.read(name)`. The `files` list comes only with
   the default `SKILL.md` read; read every other file with
   `host.skills.read(name, path=...)`.
2. `repl` cannot see host paths. Write the bundle as JSON to
   `handoff/<name>.json` in the workspace, then write the files into the repo
   from `python` (write a temp name and `os.replace` it).
3. Verify every file is byte-identical to the registry before any sanitizing.
4. If the skill is tracked, sanitize it (next section). Untracked
   `project-context/` copies stay verbatim.
5. Update the README's `Current contents` lists if a folder gained or lost a skill.

## Sanitizing tracked copies

Load `sanitize-public-git` and follow its procedure. For this repo:

- **Standing placeholders:** `<data-root>/` and `<data-root>` for the local
  data drive, `C:/Users/<user>` for an old Windows home directory. The real
  values are only in `scratch/placeholder_map.json`, which is never committed;
  read it and pass it to `replace_literals` (inverted, real → placeholder).
  Reuse these placeholders; add new entries rather than inventing a second
  placeholder for the same value.
- **Always removed:** app-internal IDs (`proj_...`, `mem_...`, `skill_...`),
  dollar spending, and per-project usage numbers. Restate a finding as a ratio
  computed from the source values, or drop it.
- **Removed from `neon-context`:** the manuscript's co-author list and target
  journal. Re-check for both whenever `neon-context` is re-synced.
- **Kept on purpose:** project names in the README's skill lists, the two
  reference codebases named in `r-coding-conventions`, published citations,
  public agency URLs, and the ohia1 file layout in `assemble-deliverables`.
- Pass `skip=["general/sanitize-public-git/kernel.py"]` to `scan_public`;
  its pattern table matches itself.
- Write every scan and report into `scratch/`, never the repo root. Remove a
  stray file with `delete_host_files`, never `rm`.

After sanitizing, re-scan, and run `git status --short --untracked-files=all`
to confirm nothing from `scratch/` or an untracked context skill is listed.

## Publishing to the registry

Registry rules that bite:

- `name:` may not contain the word `claude`.
- `description:` is at most 1024 characters, a double-quoted YAML scalar,
  and may not contain anything that looks like an XML tag (`<key>` is
  rejected). These are checked at **publish**, after the edit succeeds.
- `host.skills` has no file delete. Removing or moving a file in a published
  skill means `host.skills.delete(name)`, re-`edit` every file, then
  `publish(name, overwrite=True)`. Keep a backup first, and read every file
  back afterwards.
- A `kernel.py` edit returns `sidecar_gate`; check it rather than loading the
  skill to test.

Publish to the registry first, then mirror into the repo. Never the reverse.

## README

`README.md` describes the layout, the scope hierarchy, the ignore policy, the
current contents of each folder, and how the public copies differ from the
live skills. Update it in the same change as any layout, `.gitignore` or
membership change. The list of untracked context skills may stay in it.
