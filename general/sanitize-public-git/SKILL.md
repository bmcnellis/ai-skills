---
name: sanitize-public-git
description: "General -- applies across all projects. Prepare a git repository for public release: find and remove secrets, personal and third-party information, absolute paths, usernames, app-internal IDs, spending and usage figures, and project-specific details from every file git would publish, then verify before the first push. Ships scan and placeholder helpers (kernel.py) that read only tracked plus untracked-not-ignored files, keep reports and the placeholder reversal map in a git-ignored scratch folder, and check history for values already committed. Load when asked to sanitize, scrub, redact or audit a repo before making it public, before pushing a private repo to a public remote, when publishing a mirror of skills, notes or analysis code, or when asked whether a repo contains sensitive information."
scope: general
---

# Sanitize a git repository for public release

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> repository that is, or will become, public.

The goal is a repository whose **published contents** reveal nothing the owner
did not choose to publish. "Published" means every file git would commit:
tracked files plus untracked files that are not ignored. Ignored folders are
out of scope, but check that they really are ignored.

## Helpers (`kernel.py`, loaded with this skill)

| call | does |
|---|---|
| `public_files(repo)` | files git would publish (`ls-files --cached --others --exclude-standard`) |
| `is_ignored(repo, relpath)` | `git check-ignore`; pass a directory with a trailing `/` |
| `scan_public(repo, extra=None, categories=None, files=None, skip=None)` | regex scan; returns hits `{category, file, line, match, text}` |
| `summarize_hits(hits)` | `{category: {match: [count, first locations]}}`; print this, never the raw list |
| `write_report(repo, hits, scratch="scratch")` | full hits as JSON in the scratch folder; refuses unless it is ignored |
| `replace_literals(repo, mapping, files=None, scratch="scratch", dry_run=True)` | exact-string → placeholder; writes the reversal map to `scratch/placeholder_map.json` |
| `history_hits(repo, needles)` | commits whose diffs add or remove a value (`git log --all -S`) |

Built-in categories in `PATTERNS`: `secret_shape`, `secret_word`, `assignment`,
`email`, `phone`, `ip`, `uuid`, `abs_path`, `app_id`, `money`, `url`. Pass
project names, collaborator names, usernames and site names through `extra`,
for example `extra={"project": r"(?i)\b(alpha|beta)\b"}`. When the repo contains
this skill's own `kernel.py`, pass it in `skip`; its pattern table matches itself.

## Procedure

1. **Fix the boundary first.**
   - Confirm the scratch folder and every private folder are ignored with
     `is_ignored`. Add them to `.gitignore` if not.
   - Write every scan, report and temporary file into the ignored scratch
     folder, never the repo root. A stray file there is swept into the next
     commit. If one lands there, remove it with the host's approval-gated
     delete, not `rm`.
2. **Check history.**
   - With no commits yet, only the working tree matters.
   - With commits, run `history_hits` on every value you are about to remove.
     A hit means the value is already in history; sanitizing HEAD does not
     remove it.
   - A **secret** found in history must be **revoked and rotated** at its
     issuer. Rewriting history comes second and does not undo exposure on a
     remote that was already pushed.
3. **Scan, then triage by hand.** Run `scan_public` with project-specific
   `extra` patterns, `write_report`, and print `summarize_hits`. Sort every
   unique match into one of these classes:

   | class | examples | action |
   |---|---|---|
   | secret | keys, tokens, passwords, private keys | remove; rotate if ever committed or pushed |
   | personal | the owner's or anyone else's contact details, health, finances, IDs | remove; ask the owner about anything about themselves |
   | third party | collaborators' names in notes, unpublished co-author material | remove unless already public (e.g. cited authors) |
   | internal location | absolute paths, usernames, hostnames, drive layout | placeholder |
   | internal identifier | app project, session, artifact or memory IDs | delete the reference |
   | spending and usage | dollar costs, prices, per-project usage counts | restate as ratios, shares or exponents, or drop |
   | project detail | unpublished results, dataset names, per-project breakdowns | owner's decision |
   | false positive | "tokens" as LLM tokens, "author", public URLs, citations | leave |

   **Ask the owner** about every class that is a judgment call: personal,
   project detail, and spending. Do not decide those yourself.
4. **Apply mechanical replacements.** Call `replace_literals` with
   `dry_run=True`, check the counts, then run it with `dry_run=False`.
   - Use placeholders that read as placeholders, such as `<data-root>/` or
     `<user>`. Keep the same placeholder for the same value everywhere.
   - The reversal map stays in the ignored scratch folder.
5. **Rewrite judgment items by hand** (`edit_file` or exact-match string edits).
   - When a number carries a finding, restate it relative to the source
     values (for example, "a turn at 100 costs 1.8× a turn at 25") and
     **compute the ratio in code** from the original numbers. Never invent a
     replacement figure.
   - Remove a dropped breakdown entirely, not just its labels; totals that
     still allow a breakdown to be re-derived also count.
   - Update pointers that described the removed content (file lists,
     "this file holds per-project spend").
6. **Mirrors stay one-way.** When the repo mirrors something live (a skill
   registry, a notebook server, a shared drive), sanitize the mirror only.
   The live copy may need the real paths to work. Say so in the README, and
   never copy sanitized files back over the live source.
7. **Verify.**
   - Re-run `scan_public` and confirm every remaining hit is a deliberate keep.
   - Run `git status --short` and confirm nothing from scratch or private
     folders is listed.
   - Read the staged diff (`git diff --cached --stat`, then the diff itself)
     before the first commit.
8. **Check the commit identity.** The author name and email in every commit
   are public. Ask the owner which identity to use; a host-provided no-reply
   address avoids publishing a personal email. Set it repo-locally
   (`git config user.name` / `user.email`), not globally, unless asked.

## Pitfalls

- **Substring keyword matches drown the signal.** `auth` matches `author` and
  `token` matches LLM-token counts. Use word boundaries and review unique
  matches, not raw lines.
- **Large dumps bury the answer.** Scans of a whole repo run to hundreds of
  lines; summarize in the kernel, write the full list to scratch, and read
  selectively.
- **Placeholders in skill descriptions.** A skill registry may reject
  angle-bracket placeholders such as `<key>` in a `description:` field as XML
  tags. Placeholders in body text are fine.
- **Binary files are not scanned.** `scan_public` reports non-UTF-8 files as
  category `binary`; inspect images, spreadsheets and PDFs by hand. Their
  metadata (EXIF, document author fields) can carry names.
- **Regex categories cannot find a breakdown.** A per-project table or a list of
  session titles has no signature. Read the files that the scan flags for
  money or project names in full.

## Done when

- Every hit is removed, replaced, or recorded as a deliberate keep that the
  owner agreed to.
- Scratch and private folders are ignored and absent from `git status`.
- History contains none of the removed values, or the owner has been told
  which commits do and that any secret among them has been rotated.
- The README says what was sanitized and that live copies differ.
