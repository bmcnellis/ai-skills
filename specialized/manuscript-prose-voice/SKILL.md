---
name: manuscript-prose-voice
description: "General -- applies across all projects. Write and revise scientific manuscript prose in a named author's own measured voice and manuscript organization. Each author has a profile folder in reference/authors/, measured from published papers the author confirms as their own voice: per-section sentence, paragraph, voice and person targets; contrast, hedging, citation and quantity habits; words the author avoids; and how Introduction, Methods, Results and Discussion correspond. Profiles: mcnellis (Brandon E. McNellis, BEM; default when BEM asks for his own voice or names no author). Load before drafting, outlining or revising manuscript prose -- introduction, methods, results, discussion, abstract, cover letter, review response -- or .Rmd prose bound for a manuscript, and before building a profile for a new author. House R style is in r-coding-conventions."
scope: general
---

# Manuscript prose voice

> **Scope — general.** This skill is not tied to any one project. Apply it to any
> project whose work falls under the description above.

## What this is

This skill writes and revises scientific manuscript prose in the voice of a
**specific, named author**, measured from that author's published work rather
than guessed. The skill itself is author-neutral. Everything that describes how
one person writes lives in that person's **author profile** under
`reference/authors/<key>/`.

**Use a profile to write and to revise, not to police.** A profile records an
author's habits, not laws of grammar. When a sentence reads better against the
pattern, it reads better; say so rather than sanding it down.

## Author profiles on file

| key | author | corpus | default when |
|---|---|---|---|
| `mcnellis` | Brandon E. McNellis (BEM) | 2 first-author papers, 2021 *Ecosphere*, 2023 *ERL*; 384 sentences | BEM asks for his own voice, or no author is named |

## Choosing a profile

1. If the user names an author, use that author's profile.
2. If BEM asks for "my voice", "my style", or names no author, use `mcnellis`.
3. If the named author has no profile, say so. Do not borrow another author's
   profile as a stand-in. Offer to build one (see below), or write without a
   profile.
4. For a co-authored draft, use the profile of the author leading the writing.
   Do not blend two profiles in one document.

## Using a profile

1. Read `reference/authors/<key>/profile.md` before drafting or revising. It
   holds the rules that do most of the work, the organization of a manuscript,
   the per-section targets, the moves, what is absent, the revision checklist
   and the caveats.
2. Read the other files in the profile folder on demand:
   - `exemplars.md` when a rule needs a model sentence. When a rule and an
     exemplar disagree, the exemplar wins.
   - `measured_features.md` (and `.json`) when a number is needed.
   - `organization.md` when outlining or restructuring a whole paper.
3. Run the profile's revision checklist over a draft before handing it back.
4. Respect the profile's caveats: register limits, sample sizes, and which
   findings are solid enough to draft against.

## Profile contract

Every profile folder holds the same five files, so profiles stay comparable and
the instructions above work for any author:

| file | content |
|---|---|
| `profile.md` | Corpus and exclusions; the rules that do most of the work; manuscript organization; sentence length by section; voice and person by section; the moves; what is absent; revision checklist; files in this profile; caveats |
| `measured_features.md` | Every measured number, by section, with the corpus definition, exclusions and any corrections |
| `measured_features.json` | The same numbers, machine-readable, with the top-level keys `corpus`, `sentence_length`, `voice`, `punctuation`, `citations`, `numeric`, `hedges`, `markers_initial_vs_internal`, `paragraphs`, `discussion_closers`, `may_by_section`, `organization` |
| `exemplars.md` | Verbatim sentences from the corpus, grouped by move, with sources |
| `organization.md` | Heading trees, the question-and-hypothesis list, the section-correspondence tables and the statistics behind them |

A profile may add files, but not drop one. The section headings in
`profile.md` should follow the order above. A missing finding is stated as
"not measured" rather than left out.

## Adding an author

Follow `reference/building_an_author_profile.md`. It covers corpus selection,
extraction, the verbatim check, section assignment, measurement, organization
analysis and the caveats every profile must record. Then add the author to the
table above, and add its key to the `Profiles:` sentence in the description.
The description is capped at 1024 characters, so list each new author as
`key (full name)` only.
