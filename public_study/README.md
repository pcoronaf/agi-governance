# Real-evidence bridgeability study (paper §8.5)

Can the norms and indicators of the compliance model be evaluated from the governance
documentation frontier developers actually publish? This folder holds the multi-coder
study that answers that question, and the analysis code that reproduces every statistic
reported in Section 8.5 of the paper.

The study maps **two generations of published model and system cards** to the `agiev`
evidence schema and asks, for each (document × indicator) pair, whether the engine could
compute that indicator's value from what the document reports. It does **not** ask
whether the system would pass the indicator's threshold.

## Design

| | |
|---|---|
| Documents | 6 — 2024: GPT-4o, Claude 3.5 Sonnet, Llama 3.1 · 2025–26: GPT-5.5, Claude Opus 4.6, Gemini 3 |
| Indicators | 10 engine-implemented indicators (5 AGI-specific, 5 generic) |
| Cells | 60 per pass, coded twice (strict, generous-proxy) = 120 judgments per coder |
| Coders | 3, independent, shared written protocol and instrument |

**Two passes.** *Strict*: computable only if the document reports a quantitative metric
matching the indicator's definition. *Generous-proxy*: also computable if the document
reports a documented quantitative proxy from a related metric, recorded per cell with a
justification. A cell computable under strict is computable under generous by construction.

**Coders.** C1 — author-team coding. C2 — external coder A, ISO/IEC 42001 Lead Auditor.
C3 — external coder B, ISO/IEC 42001 Auditor. External coders are identified by role only;
their names are withheld from the public repository. Both
external coders worked blinded to all cell-level judgments and to the study's aggregate
results, and confirmed independence in the sign-off block of their instruments.

## Results

**Strict pass — unanimous.** All three coders judged all 60 cells NOT_COMPUTABLE.
Pairwise raw agreement 100%; PABAK 1.000. Cohen's and Fleiss' κ are undefined here: with
no positive judgments there is no variance for the chance correction to work on, so raw
agreement and PABAK are reported instead.

**Generous pass — substantial agreement.**

| Pair | Raw agreement | Cohen's κ | PABAK |
|---|---:|---:|---:|
| C1–C2 | 58/60 (96.7%) | 0.783 | 0.933 |
| C1–C3 | 57/60 (95.0%) | 0.640 | 0.900 |
| C2–C3 | 57/60 (95.0%) | 0.700 | 0.900 |

Fleiss' κ (three raters) = **0.709**; mean observed agreement 0.956; 56 of 60 cells
unanimous. All four disagreements concerned proxy admissibility, never the meaning of a
structured field or threshold.

**Resulting figures** (after majority resolution of the four split cells — see
`reconciliation_log.md`):

| | 2024 | 2025–26 |
|---|---:|---:|
| Computable indicators, strict | 0/30 | 0/30 |
| Computable indicators, generous | 2/30 | 3/30 |
| Evaluable norms, generous | 2/24 | 3/24 |
| **AGI-specific indicators, either pass** | **0/15** | **0/15** |

Every computable cell falls on the generic robustness-testing indicator (IND-ROB-TEST).
The five AGI-specific indicators — identity disclosure, cessation rate and latency,
self-learning oversight review rate and violation count — were computable from **zero**
cards in either generation, unanimously across the three coders. Current frontier
documentation increasingly *evaluates* these risks but does not *report* them in
machine-checkable form. The gap the compliance model targets is not closing on its own.

## Contents

| File | Description |
|---|---|
| `coder_agreement_matrix.csv` | The 60 cells × 3 coders × 2 passes judgment matrix, plus majority vote |
| `compute_reliability.py` | Reproduces all statistics above from the matrix |
| `reconciliation_log.md` | Majority resolution of the four split cells, with per-cell rationale |
| `coding_protocol.md` | The written protocol issued to every coder |
| `indicator_definitions.md` | The ten indicator definitions and thresholds used |
| `document_list.md` | The six documents, their URLs and the dates each coder coded them |
| `instruments/coder1_labeling_instrument.xlsx` | C1 completed instrument |
| `instruments/coder2_labeling_instrument.xlsx` | C2 completed instrument |
| `instruments/coder3_labeling_instrument.xlsx` | C3 completed instrument |
| `instruments/blank_labeling_instrument.xlsx` | Blank instrument, for replication |

## Reproducing

```bash
python public_study/compute_reliability.py
```

No external dependencies. The script prints per-coder counts, pairwise agreement,
Cohen's κ and PABAK, Fleiss' κ, the split cells, and the majority-vote resolution.

## Replicating on new documentation

The design is deliberately portable: pin a document set, issue `coding_protocol.md` and
`indicator_definitions.md` with the blank instrument to two or more independent coders,
and run `compute_reliability.py` over the resulting matrix. Re-running this study on later
model card generations is the cheapest way to measure whether machine-checkable reporting
of AGI-specific controls is improving.
