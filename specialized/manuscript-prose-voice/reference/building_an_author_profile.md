# Building an author profile

How to measure a new author and write the five files of the profile contract
(see `SKILL.md`). This is the method behind the `mcnellis` profile; that folder
is the worked example to copy.

## 1. Choose the corpus with the author

- Use **published papers the author wrote as lead author** and confirms are in
  their own voice, with minimal copy-editing by co-authors or editors. Record
  that confirmation in `profile.md`.
- Ask the author which papers qualify. Do not infer voice from authorship
  order alone.
- **Exclude drafts** unless the author says they represent how they want to
  write. Unpolished prose is not evidence of the target voice.
- **Exclude abstracts** from the main measurement. They are a different
  register. Treat any abstract measurement as separate.
- Two papers is the floor. Prefer papers from different years or journals,
  and note when every paper shares one study type.

## 2. Extract the body prose

- Keep running prose only. Exclude figure and table captions, table cells and
  footnotes, displayed equations, section headings, title, affiliations,
  keywords, acknowledgements, data-availability statements and reference lists.
- Keep paragraph boundaries and each paragraph's section.
- **Verify every sentence verbatim** against the source text, for example with
  an n-gram check. Drop sentences that fail, and record how many were dropped
  and what they have in common. Symbol-heavy numeric sentences fail most
  often, which biases quantity-reporting rates low.

## 3. Assign sections against the source, not by tone

- Assign each paragraph to Introduction, Methods, Results, Discussion or
  Conclusions **from the heading page boundaries** in the source PDF.
- Do not trust a segmenter's guess. A Discussion subsection on methodological
  caveats reads like Methods prose but belongs to the Discussion. In the
  `mcnellis` corpus, misfiling one such subsection moved 19 sentences and
  changed a finding. Record any correction in `measured_features.md`.

## 4. Measure, by section

Report every measure per section and overall, and fill each top-level key of
`measured_features.json`:

- `corpus`: documents, paragraph, sentence and word counts, exclusions, corrections.
- `sentence_length`: median, p25-p75, share over 35 words.
- `voice`: share of sentences with a passive; `we`/`our` as subject; any first person.
- `punctuation`: semicolons, parentheses, em-dashes and similar, as share of sentences.
- `citations`: share of sentences cited, parenthetical vs author-as-subject,
  sources per parenthesis.
- `numeric`: share of sentences carrying quantities, and how many are in
  parentheses. Exclude citation years.
- `hedges`: raw counts of each hedge word.
- `markers_initial_vs_internal`: each discourse marker counted sentence-initial
  vs internal. The position is the finding, not the total.
- `paragraphs`: sentences and words per paragraph; how paragraphs open.
- `discussion_closers`: how Discussion paragraphs end (forward-looking, hedged).
- `may_by_section`: the main hedge's counts by section. Rename the key's
  meaning in the `.md` if the author's main hedge is not `may`, but keep the key.
- `organization`: see step 5.

Report shares of sentences unless a column says otherwise. Count words the
author **never** uses as findings in their own right; "what is absent" is
usually most of what revision consists of.

## 5. Analyse the organization

- Read each paper's heading tree and any enumerated question or hypothesis
  list straight from the source.
- Map each Results paragraph to the Methods paragraph that produced it, and
  each Discussion paragraph to the Introduction paragraph it answers. Count
  orphans in both directions.
- Test whether Results order follows Methods order, and Discussion order
  follows Results order, with rank correlations. Report n and p.
- Label the paragraph mappings as a model's reading of subject matter. They are
  softer evidence than the counts.

## 6. Write the profile

- `exemplars.md`: verbatim sentences only, grouped by move, each with its
  source. Exemplars outrank rules when the two disagree.
- `profile.md`: open with the corpus, the author's confirmation and the
  exclusions. Distil the rules that do most of the work, each tied to a count.
  Then the per-section tables, the moves, what is absent, a revision checklist
  of yes/no questions, the file list and the caveats.
- Keep the section order of the profile contract so profiles stay comparable.

## 7. Record the caveats

Every profile must state:

- corpus size, and the study types and registers it does not cover;
- that counts for rare features are single observations, not rates;
- how many sentences the verbatim check dropped, and the direction of the bias;
- which organization findings are solid enough to draft against, and which
  rest on model judgement or small n;
- any section-assignment correction.

## 8. Register the profile

Add the author to the `Author profiles on file` table in `SKILL.md`, and add
the key to the `Profiles:` sentence of the description, keeping the
description under 1024 characters. Republish the skill.
