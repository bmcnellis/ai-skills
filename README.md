# Claude skills repository

Version-controlled copies of BEM's personal Claude Science skills. Each skill is a directory named exactly as its registry name. It holds a `SKILL.md` and, where present, `reference/` files and a `kernel.py` or `kernel.R` sidecar. Directory names carry no timestamps.

## Scoping hierarchy

Each skill carries a scope, recorded in its `SKILL.md` frontmatter and in a scope blockquote under its title:

1. **General** skills apply across all projects.
2. **Project-specific** skills apply to one project only and are not used elsewhere unless explicitly requested. A project-specific skill is either:
   - a **context** skill (name ending in `-context`), which carries standing project knowledge, or
   - a **task** skill, which performs a defined procedure for that project.

The repository folders are an organizational choice and do not map one-to-one onto this hierarchy. A general-scope skill can sit in `specialized/`, as two currently do.

## Layout

- `general/` holds general-scope skills.
- `specialized/` holds task-oriented skills.
- `project-context/` holds project-specific context skills. This folder is listed in `.gitignore`, so its contents stay on disk but are not tracked by git.

## Current contents

`general/`:
- `ai-disclosure-statement`
- `r-coding-conventions`
- `sanitize-public-git`
- `use-compute-efficiently`

`specialized/`:
- `assemble-deliverables`
- `make-metadata-file-usgs`
- `manuscript-prose-voice`

`project-context/` (untracked):
- `aidapt-context`
- `ecohydro2-context`
- `neon-context`
- `ohia1-context`
- `restoredart-context`

## Version control

- The repository is a git repository on branch `main`.
- `.gitignore` excludes `.DS_Store`, `*.swp`, `__pycache__/`, the entire `project-context/` folder, and `scratch/`.
- `scratch/` holds stray and temporary files, including scan reports and the placeholder map. It is never committed.

## Public copies differ from the live skills

This repository is public, and its files are sanitized copies of the live skills:

- Absolute local paths are replaced with placeholders, such as `<data-root>/` for the local data drive.
- App-internal identifiers are removed.
- Spending figures and per-project usage numbers are removed, or restated as ratios and shares.

The live skills keep their real paths, so do not copy files from this repository back over them. The `sanitize-public-git` skill holds the procedure and helpers used for this.

## Adding or changing a skill

1. Choose a folder for the skill. Record its scope in `SKILL.md` frontmatter and in the scope blockquote, as described above.
2. Keep the directory name equal to the registry name, with no timestamp suffix.
3. Commit the change with a message that names the skill.
