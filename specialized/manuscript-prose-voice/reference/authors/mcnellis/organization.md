# Manuscript organization

The skeletons of both papers, and what could and could not be verified about the
correspondence between sections. Heading trees and the hypothesis list are read
directly from the PDFs. The paragraph-to-paragraph correspondence tables are a
model's judgement of subject matter, checked against the headings but softer
evidence than the rest of this profile -- read them as a sketch, not a measurement.


## Ecosphere 2021 -- the enumerated spine

The Introduction's final paragraph hands the rest of the paper its structure. Each
item is a question, then a hypothesis, then the mechanism the hypothesis rests on
(`due to their relationship to drought, disease, and insect mortality`). Verbatim:


> 1. What environmental and biological factors are significantly related to recently observed forest mortality rates? We hypothesize that precipitation and temperature variables are most important to recent mortality rates due to their relationship to drought, disease, and insect mortality.

> 2. What explains the cause of tree death for recent data? We hypothesize that cause of tree death is also driven by precipitation and temperature variables due to their relationship to drought and insect mortality.

> 3. How do mortality rates change under future emissions scenarios? Future mortality rates are expected to increase under future climates in accordance with previous work on mortality in western U.S. forests.

> 4. How does cause of tree death change under future climates? We hypothesize insect mortality will increase through the previously documented direct influence of increased temperature on insect life cycles.

The four questions are a 2x2: (recent, future) x (rate, cause). Note that Q3 is the
one item stated as an expectation rather than a hypothesis (`Future mortality rates
are expected to increase`) -- it is the premise the other three are tested against.


## Heading trees

### Ecosphere 2021

```
INTRODUCTION
MATERIALS AND METHODS
  Experimental design, climate, and soil data
  Study area and initial plot composition
  Random Forest model building
  Other comparisons between groups
RESULTS
  Recent mortality rates and model performance        <- Q1
  Agent mortality and model performance               <- Q2
  Tree mortality across the western USA under future climates   <- Q3, Q4
DISCUSSION
  Factors most important to recent and future forest mortality  <- Q1, Q3
  Other factors driving recent tree mortality and mortality agents across the western USA  <- Q2, Q4
  Implications for future work examining forest mortality
  Methodological caveats and considerations
CONCLUSIONS
```

Two things to copy here. The Results subsections answer the four questions in the
order they were asked, three subsections covering four questions because the two
future questions share one. The Discussion then *regroups* rather than re-walking:
it collapses the 2x2 along its other axis (factors, then causes), and adds two
subsections the Results had no counterpart for -- implications, then caveats.


Also note what is *not* first: `Study area and initial plot composition` is the
second Methods subsection, not the first, and it reports the sample that survived
filtering (`Data were analyzed from 588,012 and 486,122 trees...`). The study area
is presented as an outcome of the design, not as a preamble to it.


### Environmental Research Letters 2023

```
1. Introduction
2. Methods
  2.1 Study system
  2.2 Land cover responses          (the y variables)
  2.3 Explanatory variables of interest   (the x variables: climate, edaphic, grazing)
  2.4 Counterfactual analysis       (how controls were constructed)
  2.5 Landscape response to livestock removal   (how the response was defined)
  2.6 Model building
3. Results
  3.1 Regression model evaluation             <- 2.6
  3.2 Landscape response to soil geomorphic setting   <- 2.3, edaphic
  3.3 Impacts of past grazing intensity              <- 2.3, grazing
  3.4 Interactions between soils, years since intervention, and past grazing intensity
4. Discussion
5. Conclusions
```

This is the cleaner template of the two, and the order is strict order of
operations: where -> what was measured -> what explains it -> how controls were
built -> how the response was defined -> how it was fit. The Results then invert
one step: 3.1 establishes the models are usable (from 2.6, the *last* Methods
subsection) before any substantive result is reported, after which the
explanatory variables appear in the order 2.3 introduced them, with interactions
last.

## Correspondence, and how well it holds up

### Every result has a method behind it

The strongest and cleanest finding. Each Results paragraph maps onto a Methods
paragraph describing the procedure that produced it, with no orphans in either
paper: 5 of 5 in *Ecosphere*, 7 of 7 in *ERL*. Nothing is reported that the
Methods did not set up, and no procedure is described that produces no reported
result. This is the correspondence to protect when drafting.


**Ecosphere 2021**

| Results paragraph | maps to Methods paragraph |
|---|---|
| RESU1. Mortality variation across ecosystems | METH10. Tree and plot sample sizes |
| RESU2. Model prediction accuracy results | METH12. Model cross-validation approach |
| RESU3. Variable importance contributions | METH13. Variable importance assessment method |
| RESU4. Recent mortality rates by agent | METH5. Mortality agent classification codes |
| RESU5. Future species-specific mortality rates | METH15. Future mortality projection method |

**ERL 2023**

| Results paragraph | maps to Methods paragraph |
|---|---|
| RESU1. model convergence diagnostics | METH9. Bayesian model fitting details |
| RESU2. climate covariate coefficient estimates | METH3. explanatory variable construction |
| RESU3. soil geomorphic unit associations | METH3. explanatory variable construction |
| RESU4. CDW intercept significance | METH4. cost-distance to water surrogate |
| RESU5. fSCA slopes across CDW | METH4. cost-distance to water surrogate |
| RESU6. SGU by YSI interaction | METH6. years since intervention modeling |
| RESU7. SGU by CDW interaction | METH4. cost-distance to water surrogate |

### Results order follows Methods order, but loosely

Rank correlation between a Results paragraph's position and the position of the
Methods paragraph it draws on: rho = 0.40 (n = 5, p = 0.51) in *Ecosphere*;
rho = 0.09 (n = 7, p = 0.84) in *ERL*, rising to rho = 0.80 (n = 6, p = 0.055)
once the opening model-evaluation paragraph is set aside. The intent is legible
but is **not** statistically established at paragraph level on two papers. At
heading level it is unmistakable; at paragraph level it is noisy. Treat
'Results follow Methods order' as the drafting default, not as a rule these
papers obey strictly.


The one systematic departure is worth copying deliberately: both papers lift the
model-evaluation step out of its Methods position and report it **first** in the
Results. Nothing substantive is claimed until the model has been shown fit for
use.


### The Discussion is not a re-walk of the Results

Discussion order against the order of the results each paragraph interprets:
rho = -0.05 (n = 17, p = 0.86) in *Ecosphere*, rho = -0.21 (n = 5, p = 0.74) in
*ERL*. Both flat. The Discussion is organised by theme and returns to the same
result from several angles where the argument needs it -- six of the seventeen
*Ecosphere* Discussion paragraphs interpret the same variable-importance result.


### Every Discussion paragraph answers back to the Introduction

This is the correspondence that actually governs Discussion order, and it is
complete in both papers: **17 of 17** *Ecosphere* Discussion paragraphs and
**6 of 6** *ERL* Discussion paragraphs return to a specific Introduction
paragraph. Three of the four results-free paragraphs -- the methodological
caveats -- are still answerable to the Introduction; they just answer the
paragraph that justified the dataset rather than one that framed the science.


**Ecosphere 2021** -- 17 of 17 paragraphs return to the Introduction

| Discussion paragraph | interprets result | answers Introduction |
|---|---|---|
| DISC1. Overview of mortality drivers | RESU1. Mortality variation across ecosystems | INTR1. Significance of tree mortality |
| DISC2. Future mortality acceleration | RESU5. Future species-specific mortality rates | INTR3. Causes of tree mortality |
| DISC3. Species mortality rate novelty | RESU4. Recent mortality rates by agent | INTR2. Gap in empirical mortality prediction |
| DISC4. Aspen decline literature | RESU5. Future species-specific mortality rates | INTR3. Causes of tree mortality |
| DISC5. Comparing mortality rates to literature | RESU4. Recent mortality rates by agent | INTR3. Causes of tree mortality |
| DISC6. Climate-resilient species | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC7. Juniper mortality robustness | RESU5. Future species-specific mortality rates | INTR3. Causes of tree mortality |
| DISC8. Tree diameter importance | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC9. Ecological section importance | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC10. Winter temperature variables | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC11. Snowpack and frost link | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC12. Belowground competition effects | RESU3. Variable importance contributions | INTR3. Causes of tree mortality |
| DISC13. Species-level model parameterization | RESU5. Future species-specific mortality rates | INTR2. Gap in empirical mortality prediction |
| DISC14. FIA data timeframe choice | -- | INTR4. FIA inventory program overview |
| DISC15. Plot coordinate fuzzing error | -- | INTR4. FIA inventory program overview |
| DISC16. Mortality agent data limitations | RESU4. Recent mortality rates by agent | INTR4. FIA inventory program overview |
| DISC17. Excluding harvest and fire | -- | INTR3. Causes of tree mortality |

**ERL 2023** -- 6 of 6 paragraphs return to the Introduction

| Discussion paragraph | interprets result | answers Introduction |
|---|---|---|
| DISC1. grazing as complex disturbance | -- | INTR1. livestock grazing in drylands |
| DISC2. livestock removal cover increase | RESU2. climate covariate coefficient estimates | INTR3. study goal: land cover change |
| DISC3. grazing intensity and resilience | RESU4. CDW intercept significance | INTR1. livestock grazing in drylands |
| DISC4. modest climate effects | RESU2. climate covariate coefficient estimates | INTR2. new data/analytical frameworks |
| DISC5. soil system complexity | RESU6. SGU by YSI interaction | INTR1. livestock grazing in drylands |
| DISC6. novel synthetic control approach | RESU1. model convergence diagnostics | INTR2. new data/analytical frameworks |

In *Ecosphere* the four caveat paragraphs that close the Discussion (`Methodological caveats and considerations`) carry no result of their own, and
three of them answer INTR4 -- the Introduction paragraph that introduced and
justified the FIA dataset. The caveats are not a disclaimer appended at the end;
they are the settling of a debt the Introduction opened.


In *ERL* the Discussion opens on the framing paragraph (grazing as a complex
dryland disturbance) and closes on the methodological one (what the new data
products and frameworks make possible). The Introduction's promise is what the
Discussion is answerable to.


## Caveat

Two papers, both model-centred quantitative studies with a single analysis at
their core. The heading trees and the hypothesis list are solid evidence; the
correspondence tables are a model's reading of subject matter, and the rank
correlations rest on n = 5 to 17. A synthesis, a review, or a multi-experiment
paper would likely need a different skeleton.
