# Component 2 — Empirical validation against auditor-confirmed ground truth

Turnkey protocol for a real small study.
 
## Objective
Measure agreement between the reference engine's per-norm verdicts and the
independent judgment of human governance auditors on **real** evidence, and analyze
every disagreement. This is the "auditor-confirmed accuracy" rung the paper's staged
framing (Section 7.1) specifies.

## Materials
- **Evidence packages (N ≥ 3, target 5–8).** Real governance evidence for real AI
  systems: model/system cards, red-teaming reports, monitoring/telemetry extracts,
  change-management/continual-learning records, incident logs. Sources: your own or
  partner organizations' ISO/IEC 42001:2023 audit material (redacted as needed), or
  regulated deployments your co-authors can access. Record provenance per artifact.
- **Labelers (R ≥ 2).** People with audit/AI-governance familiarity who are **not**
  authors of the engine and have **not** seen its output for these packages.

## Roles and blinding
1. **Mapper** (may be an author): converts each raw evidence package into an agiev
   bundle (artifacts + fields), recording a source pointer for every value. Does **not**
   assign verdicts. Publishes the mapping.
2. **Engine operator**: runs `checker/compliance_engine.py` on each mapped bundle and
   **seals** the outputs (e.g., commit a hash) before any labeling.
3. **Labelers** (independent, ≥2): using the rubric (`rubric.md`) and the raw package —
   **not** the engine output — independently assign one verdict per norm
   (`COMPLIANT` / `VIOLATED` / `EVIDENCE_GAP`) with a one-line rationale and an evidence
   pointer, on their own copy of `labeling_sheet_template.csv`.
4. **Analyst**: after all labels are in, unseals engine outputs and runs `analyze.py`.

## Procedure
1. Select and de-identify packages; define inclusion criteria (real system, evidence
   spanning ≥3 of the 5 artifact types, retrievable provenance).
2. Mapper builds bundles; engine operator runs and seals verdicts.
3. Each labeler labels every (package × norm) cell blind and independently.
4. Analyst computes: inter-labeler agreement (Cohen's κ for 2 raters; Fleiss' κ for ≥3),
   labeler↔engine agreement against the labeler consensus, and a full disagreement
   table classified as {engine defect, mapping error, rubric ambiguity, genuine
   judgment difference}.
5. Adjudicate disagreements with a third senior reviewer; report both raw and
   adjudicated agreement.

## Reporting standard (pre-registered)
- Report N packages, R labelers, and the exact cell count (N × 8 norms).
- Report inter-labeler κ **first** (if labelers don't agree, the ground truth is weak).
- Then labeler-consensus↔engine agreement, with the disagreement table.
- Report `EVIDENCE_GAP` rates separately from COMPLIANT/VIOLATED — a high gap rate on
  real evidence is a finding (see the bridgeability study), not a failure.
- State all limitations: small N, labeler pool, mapping subjectivity.

## Ethics / data handling
Obtain permission and redact confidential audit material before use; record a
data-use basis. Keep labelers blind to engine output and to each other until analysis.

## Success/interpretation
There is no pass/fail threshold to hit. A credible result is: labelers agree with each
other (κ substantial), the engine matches the labeler consensus on the cells where
evidence exists, and the disagreements are explained. Even a mostly-`EVIDENCE_GAP`
outcome is publishable and consistent with the bridgeability finding.
