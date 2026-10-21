# Author profile: Brandon E. McNellis (BEM)

> **Profile key `mcnellis`.** Loaded from `manuscript-prose-voice`. This is the
> default profile when BEM asks for his own voice or names no other author.
> All file references below are relative to this folder,
> `reference/authors/mcnellis/`.

## What this is, and what it is not

This profile describes how **this author actually writes**, measured rather
than guessed. The corpus is the body prose of two published first-author
papers, confirmed by the author to be his own voice with minimal
copy-editing:

- McNellis, B.E., A.M.S. Smith, A.T. Hudak, E.K. Strand (2021)
  *Ecosphere* 12(5):e03419
- McNellis, B.E. et al. (2023) *Environmental Research Letters* 18:034034

73 paragraphs, 384 sentences, 10,221 words, with captions, tables,
equations, headings and references excluded. Full numbers are in
`measured_features.md`; every example sentence is in
`exemplars.md`, quoted verbatim.

**Not** covered: abstracts (only two in the corpus, and a different
register), and working-notebook prose. Drafts on disk were explicitly
excluded at the author's request -- he does not consider them polished, so
they are not evidence of how he wants to write.

**Use this to write and to revise, not to police.** These are the author's
habits, not laws of grammar. When a sentence reads better against the
pattern, it reads better; say so rather than sanding it down.

## The five rules that do most of the work

1. **Build contrast inside the sentence, not in front of it.** `but` occurs
   28 times in the corpus and *never once opens a sentence*. `however`
   occurs 4 times in 10,000 words; `thus` and `moreover` occur zero times.
   Write `X was important, but Y was not` rather than `X was important.
   However, Y was not.`
2. **Open a paragraph with a noun phrase naming its topic.** 54 of 73
   paragraphs do this; exactly one opens with a connective. The first
   sentence states the claim or names the object, and citations trail it.
3. **Hedge interpretation, never description.** `may` appears 59 times, 56
   of them in the Discussion and *none at all* in the Results. Results
   assert what was measured; the Discussion says what it may mean.
4. **Put the quantity in parentheses and keep it out of the clause.** 45%
   of Results sentences carry a value in parentheses, so the sentence
   stays readable as a sentence: `...had a significant positive effect on
   total spring foliar cover (0.32 ± 0.07, 0.20 ± 0.07)`.
5. **Close a Discussion paragraph by naming what should happen next.** 10 of
   23 Discussion paragraphs end on a forward-looking recommendation, and 13
   of 23 end on a hedge. The closer says who should do what, and usually
   what it would buy.

## Manuscript organization

Organization is deliberate in both papers, and the correspondences between
sections are what make the paper checkable. Each one below is labelled with how
well it actually held up when tested -- two are complete in both papers, one is
only a tendency, and one turned out to run the opposite way from the obvious
guess. Full heading trees, the correspondence tables and the statistics are in
`organization.md`.

### The Introduction ends by handing the paper its spine

The *Ecosphere* Introduction closes with four numbered items, each a question,
then a hypothesis, then the mechanism the hypothesis rests on:

> 1. What environmental and biological factors are significantly related to
> recently observed forest mortality rates? We hypothesize that precipitation
> and temperature variables are most important to recent mortality rates due to
> their relationship to drought, disease, and insect mortality.

The four form a 2x2 of (recent, future) x (rate, cause), and one of them --
that future mortality will rise -- is stated as an expectation rather than a
hypothesis, because it is the premise the other three are tested against. Every
later section is then answerable to that list. When drafting a new paper, write
this list early: it is the object the rest of the structure hangs from.

### Methods run in order of operations

*ERL*: study system, then the response variables, then the explanatory
variables, then how controls were constructed, then how the response was
defined, then how the model was fit. *Ecosphere*: design and input data, then
the sample that survived filtering, then model building, then the statistical
comparisons.

Note what is **not** first in *Ecosphere*: `Study area and initial plot
composition` is the second subsection, and it reports the sample that came out
of the filters (`Data were analyzed from 588,012 and 486,122 trees...`). The
study area is an outcome of the design, not a preamble to it. *ERL* uses the
conventional study-system-first order, so both are available -- but a study
area reported as a result of the design is the more distinctive choice.

### Every result has a method behind it, and model evaluation comes first

This is the strongest measured correspondence: every Results paragraph maps to
a Methods paragraph that produced it, with no orphans in either paper -- 5 of 5
in *Ecosphere*, 7 of 7 in *ERL*. Nothing is reported that the Methods did not
set up, and no procedure is described that yields no reported result. **Protect
this when drafting or cutting**: deleting a Methods paragraph obliges you to
find the result it produced.

Both papers also lift the model-evaluation step out of its Methods position and
report it *first* in the Results. Nothing substantive is claimed until the model
has been shown fit for use.

Results order does follow Methods order, but loosely: rho = 0.40 (n = 5,
p = 0.51) in *Ecosphere*, and rho = 0.09 (n = 7, p = 0.84) in *ERL* rising to
rho = 0.80 (n = 6, p = 0.055) once the opening model-evaluation paragraph is set
aside. Obvious at heading level, noisy at paragraph level. Use it as the
drafting default, not as a rule to enforce.

### The Discussion is organized against the Introduction, not the Results

This is the correspondence most likely to be got wrong, so it is worth stating
plainly. Discussion order does **not** track Results order -- rho = -0.05
(n = 17) and rho = -0.21 (n = 5), both flat. The Discussion instead returns to
the Introduction, and it does so completely: **17 of 17** *Ecosphere* Discussion
paragraphs and **6 of 6** *ERL* Discussion paragraphs answer back to a specific
Introduction paragraph.

So a Discussion paragraph is allowed to revisit a result already discussed --
six of the seventeen *Ecosphere* paragraphs interpret the same
variable-importance result from different angles -- but it is not allowed to
raise something the Introduction never set up. The test to apply when drafting:
*which Introduction paragraph is this one answering?* If there is no answer,
either the paragraph does not belong or the Introduction is missing a paragraph.

The methodological caveats follow the same rule. In *Ecosphere* the four
paragraphs closing the Discussion carry no result of their own, and three of
them answer the Introduction paragraph that introduced and justified the FIA
dataset. The caveats are not a disclaimer appended at the end; they settle a
debt the Introduction opened.

### Drafting order that follows from this

1. Write the question-and-hypothesis list first, with a mechanism attached to
   each hypothesis.
2. Order the Methods as the operations actually ran.
3. Give each Methods procedure its Results paragraph, and open the Results with
   the model-evaluation paragraph regardless of where fitting sat in the
   Methods.
4. Organize the Discussion by theme, then check every paragraph against the
   Introduction -- each one should be answering a specific paragraph there.
5. Close the Discussion with the caveats, pointed back at the Introduction
   paragraphs that justified the data and design.

## Sentence length, by section

Aim at the median and let the spread happen; do not write to the mean.

| section | median | typical range (p25-p75) | over 35 words |
|---|---|---|---|
| Introduction | 31 | 25-38 | 36% |
| Methods | 23 | 17-30 | 15% |
| Results | 21 | 16-26 | 6% |
| Discussion | 29 | 22-35 | 23% |
| Conclusions | 23 | 20-25 | 13% |

Overall median 25 words, s.d. 10.8, longest sentence in either paper 68
words. The gradient is the point: Results sentences are the shortest in
the paper and the Introduction's the longest. A 35-word Results sentence
is out of register even though it would be unremarkable in the Discussion.

Paragraphs run 5 sentences and about 130 words on average; Discussion
paragraphs are the longest at 5.7 sentences and 169 words. Six paragraphs
in the corpus exceed 8 sentences, so a long paragraph is allowed, but it
should be carrying an argument rather than a list.

## Voice and person, by section

| section | sentences with a passive | subject is `we`/`our` | any first person |
|---|---|---|---|
| Introduction | 14% | 6% | 14% |
| Methods | 43% | 10% | 28% |
| Results | 24% | 0% | 1.5% |
| Discussion | 19% | 14% | 40% |

Two disciplines are worth stating explicitly, because they are the easiest
things to get wrong:

**Results are impersonal.** One Results sentence in the whole corpus
contains a first-person pronoun, and none makes `we` the subject. The
measured thing is the subject: `Varying slopes fit to fSCA for each level
of CDW were significant for 20 out of 24 levels (figure 4).` Not "we found
that...".

**`we` marks a decision, not an action.** In the Methods, first person
attaches to choices a reader could have made differently -- what was
included, excluded, defined, assumed (`We limited consideration to the 53
most common tree species due to restrictions imposed by our analysis
software.`). Routine procedure takes the passive and
drops the agent (`Climate variables were calculated for each plot...`).
The distinction is doing real work: it tells a reviewer which steps are
defensible judgment calls.

## The moves

**Concession uses `Nonetheless`.** It opens 6 sentences; `however` opens 3
in the whole corpus. The shape is: concede the limitation, then reassert
what survives it. `Nonetheless, tree size alone was not enough to account
for observed mortality rates...`

**`While` carries the subordinate contrast.** 13 of its 24 uses open a
sentence, setting up a concessive clause before the main claim: `While
variable importance measures can be a useful assessment of overall
variable performance, they can be biased toward certain classes of
variables...`

**Stacked hedges are normal in interpretation.** 20 sentences carry two or
more hedges, and doubling `may` within one sentence is characteristic:
`...long-lived tree species such as P. menzeisii or members of Juniperus
may live more than 1000 yr and may not die for some time after the onset
of lethal environmental or biotic stress`. Do not "fix" this to a single
hedge -- the two hedges are qualifying two different things.

**Citations are parenthetical, bundled, and chronological.** 36% of
sentences carry a parenthetical citation; only 1.8% make an author the
grammatical subject, and that is reserved for a source being *used* rather
than *cited* (`Tinkham et al. (2018) provide a thorough overview of FIA
data...`). 40% of parentheses hold more than one source, up to seven, with
a corpus-wide mean of 1.75. Introduction sentences are the most heavily
cited (61% of sentences, 2.3 sources per parenthesis).

**Define terms in single quotes at first use, inline.** 11 sentences do
this, inside the sentence that first needs the term, never as a standalone
definition: `...semi-arid and arid landscapes ('drylands' hereafter;
Maestre et al 2016)`.

**Results reference their own figures.** 29% of Results sentences name a
figure or table, usually in the same parenthesis as the value. The
Discussion does this much less (8%), and the Introduction never.

## What is absent

Deleting these is most of what revision consists of.

- **`thus`, `moreover`, `in summary`, `taken together`, `nevertheless`,
  `for instance`, `indeed`, `whereas`** -- zero occurrences each.
- **Sentence-initial `but` and `also`** -- zero occurrences, despite 28 and
  11 internal uses.
- **Em-dashes** -- one sentence in 384. If you reach for a dash, the author
  would use a comma, a semicolon (6% of sentences) or parentheses (58%).
- **Author-as-subject citation** -- 1.8% of sentences. Prefer the
  parenthetical.
- **Hedged Results** -- no `may` anywhere in the Results.
- **Rhetorical questions, exclamations, second person** -- none.

Boosters are used sparingly and are mostly `very` (13), `significantly`
(11), `especially` (9) and `strongly` (6). Note that `significant` carries
a statistical sense in Results and a plain-English sense elsewhere
(`significant limitations`, `significant landscape heterogeneity`); keep
the statistical sense out of sentences that report no test.

## Revision checklist

Run this over a draft before handing it back:

1. Does any sentence open with `However`, `Thus`, `Moreover`,
   `Additionally`, `Furthermore`, `But` or `Also`? Rebuild it with an
   internal `but`/`while`, or open on the noun phrase.
2. Does every paragraph open on a noun phrase naming its topic?
3. Does any Results sentence hedge, cite, or say `we`? Remove all three.
4. Is any Results sentence over ~32 words? Split it, or move the value
   into parentheses.
5. Does each Discussion paragraph end on a hedge or a recommendation
   rather than trailing off mid-evidence?
6. Are quantities in parentheses rather than inside the clause?
7. Are multi-source citations bundled into one chronological parenthesis?
8. Any em-dashes? Convert to comma, semicolon or parentheses.
9. Is `significant` used statistically in a sentence that reports no test?

## Files in this profile

- `measured_features.md` -- every measured number, by section,
  with the corpus definition and its exclusions.
- `measured_features.json` -- the same, machine-readable.
- `exemplars.md` -- verbatim example sentences grouped by move.
  When a rule here and an exemplar disagree, the exemplar wins.
- `organization.md` -- heading trees of both papers, the verbatim
  question-and-hypothesis list, the Results-to-Methods and
  Discussion-to-Introduction correspondence tables, and the rank
  correlations behind the organization section.

## Caveats

Two papers is a small corpus, and both are quantitative
ecology/remote-sensing papers with a modelling core; the register may not
transfer to a synthesis, a review, or a short-format letter. The counts
for rare features (`conversely` at 1, em-dash at 1) are single
observations, not rates. 31 sentences were dropped from the corpus because
they failed a verbatim check against the source PDF, and those drops skew
toward symbol-heavy numeric sentences, so the quantity-reporting
percentages are mild underestimates.

The organization findings rest on less evidence than the sentence-level
ones. The heading trees and the question-and-hypothesis list are read
straight off the papers; the paragraph-to-paragraph correspondences are a
model's reading of subject matter, and the rank correlations rest on n = 5
to 17. The Results-to-Methods completeness (5 of 5, 7 of 7) and the
Discussion-to-Introduction completeness (17 of 17, 6 of 6) are the two
findings solid enough to draft against.

One correction is recorded in `measured_features.md`: the four
paragraphs of the *Ecosphere* subsection `Methodological caveats and
considerations` were first filed as Methods, since they read like Methods
prose. They sit inside the Discussion and were reassigned, which moved 19
sentences. That is why forward-looking closers are now a Discussion device
exclusively, with none in the Methods.
