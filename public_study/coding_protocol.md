# Coding protocol — real-evidence bridgeability study (paper §8.5)

## Unit of analysis

One **cell** = one *(document, indicator)* pair.
6 documents × 10 indicators = **60 cells**. Each cell receives **two judgments**
(strict pass and generous-proxy pass), recorded on the same row of the instrument.

## The judgment

For each cell, answer: *"Could the compliance engine compute this indicator's value
from what this document reports?"*

- **COMPUTABLE** — the document reports the information needed to evaluate the
  indicator against its threshold.
- **NOT_COMPUTABLE** — it does not.

There is no middle category. If you find yourself wanting one, the cell is
NOT_COMPUTABLE on the strict pass; consider whether it is COMPUTABLE on the generous
pass, and use the Notes column.

## Pass 1 — STRICT

Mark COMPUTABLE **only** if the document reports a quantitative metric **matching the
indicator's definition** in `03_indicator_definitions.md`:

- The reported metric measures the same quantity the indicator defines (same numerator
  and denominator concept, same units or trivially convertible ones).
- A **number is actually stated** (a rate, count, latency, coverage figure). A metric
  that is named but whose value is withheld is NOT_COMPUTABLE.
- Qualitative discussion of the topic — however extensive — is NOT_COMPUTABLE.
  *Example: a card that describes shutdown-resistance evaluations at length but reports
  no compliance rate is NOT_COMPUTABLE for IND-CTRL-CEASE-RATE on the strict pass.*

## Pass 2 — GENEROUS-PROXY

Mark COMPUTABLE if the strict criterion is met, **or** if the document reports a
**documented quantitative proxy from a related metric**:

- The proxy must itself be a reported number (not a promise, plan, or qualitative claim).
- The proxy must plausibly bound or estimate the indicator's quantity. Record in the
  instrument **which reported metric** you are treating as the proxy and one line on why.
- Logical constraint: a cell COMPUTABLE on strict is automatically COMPUTABLE on
  generous. The instrument flags violations of this automatically.

## Evidence pointers (mandatory for every COMPUTABLE judgment)

For each COMPUTABLE cell (either pass), record:
1. **Location** — section heading and page number (or nearest anchor) in the pinned document.
2. **Paraphrase** — one line stating the reported metric and its value, in your own words.

Cells judged NOT_COMPUTABLE need no pointer, but if the document *discusses* the topic
without reporting a metric, a brief note (e.g., "shutdown evals described §4.2, no rate
reported") is valuable for adjudication.

## Scope rules

- Judge **only the pinned document** in `04_document_list.md`. Do not consult the
  developer's blog posts, papers, appendices hosted elsewhere, or newer card revisions —
  even when the card links to them — unless the linked material is listed in `04` as
  part of the pinned document set.
- Judge what is **reported**, not what you believe the developer measured internally.
- If the same indicator is addressed in two places with different numbers, use the more
  specific/final one and note the conflict.

## Procedure

1. Read `03_indicator_definitions.md` in full, once, before opening any card.
2. Code **document-by-document** (all 10 indicators for card 1, then card 2, ...).
   This mirrors Coder 1's procedure and reduces definition drift.
3. Fill both passes for each cell before moving to the next.
4. When all 60 rows are complete, check the instrument's `Check` column shows no flags,
   complete the sign-off block, and submit.

## After submission

Reliability statistics are computed on your raw sheet (pre-reconciliation). You and
Coder 1 will then jointly adjudicate disagreeing cells using both sets of evidence
pointers; consensus and rationale go into the reconciliation log. Do not amend your
sheet after submission — disagreements are expected and are the point of the exercise.
