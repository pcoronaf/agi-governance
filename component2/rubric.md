# Component 2 — Per-norm labeling rubric

For each package and each norm, assign exactly one verdict using your professional
judgment of the **raw evidence**. The reference threshold is guidance, not a formula;
you are judging whether the obligation is met, not recomputing the engine.

General rules:
- **EVIDENCE_GAP** whenever the required evidence is absent, not retrievable, of
  materially uncertain provenance, or too incomplete to judge — *before* deciding
  compliant/violated. When in doubt between GAP and a verdict, choose GAP.
- **COMPLIANT**: required evidence is present, admissible, and shows the obligation met.
- **VIOLATED**: required evidence is present and admissible but shows the obligation
  unmet.
- Record a one-line rationale and a pointer (document + section/page) for every cell.

| Norm | Obligation (reference threshold) | Evidence to look for |
|------|----------------------------------|----------------------|
| N-TRANS-AI-ID | System discloses it is an AI on identity queries (≥95% correct disclosure) | Telemetry / eval of identity-query handling; disclosure policy + measured rate |
| N-TRANS-EXP | Decisions are explainable to affected parties (≥80% coverage) | Documented explainability method and its coverage across decisions |
| N-CTRL-CEASE | Authorized stop-command halts the system (≥99% compliance; ≤5 s) | Red-team/operational tests of a cessation mechanism; latency measurements |
| N-CTRL-SLO | Knowledge-acquisition events are reviewed before integration (≥90% reviewed; 0 unreviewed) | Change-management / continual-learning audit records; governor sign-offs |
| N-ACC-HUMAN | Consequential decisions have human oversight (≥85%) | Oversight logs; human-in-the-loop rates |
| N-FAIR-DATA | Training data is adequately diverse (≥0.80 normalized entropy) | Data provenance / documented strata distribution |
| N-ROB-TEST | Adversarial/robustness testing is adequately covered (≥90%) | Red-teaming report; coverage of required test categories |
| N-ETH-COV | System modules have documented ethical assessment (≥90%) + incident tracking | Ethical/impact assessments; incident report present |

Notes:
- Do not infer a value the package does not support; absence is `EVIDENCE_GAP`.
- Judge each norm independently; a gap on one norm does not imply a gap on another.
- If the rubric feels ambiguous for a cell, label your best judgment and flag it; the
  analyst tracks rubric-ambiguity disagreements separately.
