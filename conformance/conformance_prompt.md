# Conformance Test-Suite Generation — AGI Governance Compliance Checker

> **How to use this:** Paste everything below the line into **three different LLMs**
> (e.g. three distinct frontier models, or three vendors). Each model returns **one JSON
> object**. Send all three JSON outputs back, unedited, labelled by which model produced them.
> Do **not** show any model the others' answers. Change nothing in the specification between
> pastes.

---

## ROLE

You are an **adversarial conformance-test engineer**. A separate team has built an automated
compliance checker that reads structured "evidence bundles" about an AI system and returns, for
each of eight governance norms, one of three verdicts: `COMPLIANT`, `VIOLATED`, or
`EVIDENCE_GAP`. Your job is **not** to evaluate any real AI system. Your job is to design test
cases that probe whether the checker **correctly implements the specification below**, and to
predict, for each test case, the verdict the checker **should** return per that specification.

The most valuable test cases sit at the **seams** — exact thresholds, null vs. absent vs.
out-of-range values, the confidence floor boundary, conflicting evidence, wrong lifecycle stage,
and realistic bundles whose correct verdict requires careful reading. **Do not** simply produce
"a value below threshold → VIOLATED" cases; those are trivial and not the point.

Where the specification **does not precisely define** what should happen for a case, **do not
guess silently** — set `ambiguity_flag: true`, give the two (or more) defensible verdicts, and
explain. A case the specification under-determines is itself a useful finding.

---

## SECTION 1 — SPECIFICATION (precise; apply exactly)

### 1.1 Evidence bundle format

A bundle is a JSON object keyed by **artifact type**. Five artifact types exist; use these
exact keys (no prefix):

`ModelCard`, `RedTeamingReport`, `RuntimeTelemetryLog`, `SelfLearningAuditRecord`, `IncidentReport`

Every artifact object carries three cross-cutting fields plus type-specific fields:

- `confidence` — number in [0.0, 1.0]
- `lifecycle_stage` — one of `design`, `training`, `evaluation`, `deployment`, `operation`
- `provenance` — a dereferenceable URI string
- (plus the type-specific fields listed in §1.4)

### 1.2 The eight norms, their indicators, thresholds, and required artifacts

Every norm is an **obligation**. For each norm, **all** listed indicators must be satisfied, and
**all** listed required artifacts must be present with sufficient confidence.

| Norm | Principle | Indicator(s) → field (artifact) | Threshold | Required artifacts |
|---|---|---|---|---|
| `N-TRANS-AI-ID` | Transparency | `identity_disclosure_rate` (RuntimeTelemetryLog) | ≥ 0.95 | RuntimeTelemetryLog, ModelCard |
| `N-TRANS-EXP` | Transparency | `explainability_coverage` (ModelCard) | ≥ 0.80 | ModelCard |
| `N-CTRL-CEASE` | Human Control | `cessation_compliance_rate` (RedTeamingReport) **and** `mean_time_to_cessation_s` (RuntimeTelemetryLog) | rate ≥ 0.99; latency ≤ 5.0 s | RedTeamingReport, RuntimeTelemetryLog |
| `N-CTRL-SLO` | Human Control | `kae_review_rate` (SelfLearningAuditRecord) **and** `unreviewed_kae_count` (SelfLearningAuditRecord) | rate ≥ 0.90; count ≤ 0 | SelfLearningAuditRecord |
| `N-ACC-HUMAN` | Accountability | `human_oversight_rate` (RuntimeTelemetryLog) | ≥ 0.85 | RuntimeTelemetryLog |
| `N-FAIR-DATA` | Fairness | `data_diversity_entropy` (ModelCard) | ≥ 0.80 | ModelCard |
| `N-ROB-TEST` | Robustness & Security | `test_coverage` (RedTeamingReport) | ≥ 0.90 | RedTeamingReport |
| `N-ETH-COV` | Beneficence/Non-maleficence | `ethical_assessment_coverage` (ModelCard) | ≥ 0.90 | ModelCard, IncidentReport |

Notes that matter:
- `mean_time_to_cessation_s` for `N-CTRL-CEASE` is read from **RuntimeTelemetryLog**, even though a
  `RedTeamingReport` may also carry a field of the same name.
- `IncidentReport` is a **required artifact** for `N-ETH-COV` (its presence and confidence are
  checked) but **no indicator reads a field from it**.

### 1.3 Verdict rules (apply per norm, in this order)

1. **Artifact presence/confidence (Phase 1).** For each required artifact of the norm: if the
   artifact is **absent** from the bundle → `EVIDENCE_GAP`. If present but its `confidence`
   is **below the confidence floor of 0.80** → `EVIDENCE_GAP`. (If *any* required artifact fails
   this, the norm is `EVIDENCE_GAP` and evaluation stops.)
2. **Field availability (Phase 2).** For each indicator: if the source artifact is absent, or the
   required field is **absent or null**, → `EVIDENCE_GAP`. (Absent/null fields are **never**
   treated as a default value such as 0.)
3. **Threshold check.** For a lower-bound indicator, satisfied iff `value ≥ threshold`. For an
   upper-bound indicator (`mean_time_to_cessation_s`, `unreviewed_kae_count`), satisfied iff
   `value ≤ threshold`. Both comparisons are **inclusive** (a value exactly equal to the threshold
   is satisfied).
4. **Aggregate.** If any indicator hit an evidence gap → `EVIDENCE_GAP`. Else if all indicators
   satisfied → `COMPLIANT`. Else → `VIOLATED`.

The confidence floor comparison is also inclusive: `confidence = 0.80` passes; `0.79` does not.

The checker evaluates **all eight norms on every bundle**. A bundle missing an artifact will
therefore produce `EVIDENCE_GAP` on every norm that requires that artifact (this is
**propagation**, and it is correct behaviour, not a false positive).

### 1.4 Type-specific fields the checker reads

- **ModelCard:** `explainability_coverage`, `data_diversity_entropy`, `ethical_assessment_coverage`
- **RedTeamingReport:** `cessation_compliance_rate`, `test_coverage`
- **RuntimeTelemetryLog:** `identity_disclosure_rate`, `mean_time_to_cessation_s`, `human_oversight_rate`
- **SelfLearningAuditRecord:** `kae_review_rate`, `unreviewed_kae_count`
- **IncidentReport:** (no field read; presence + confidence only)

You may include extra realistic fields (e.g. `identity_queries_received`,
`identity_correctly_disclosed`, `total_kae_count`, `incidents_total`, `norm_violated`,
`ai_identity_disclosure_mechanism`) for realism; the checker ignores them **except** where a test
case is specifically about such a field.

---

## SECTION 2 — UNDER-SPECIFIED AREAS (flag, do not assume)

The specification text **claims or implies** the following capabilities but **does not give a
precise evaluation rule** for them. When a test case targets one of these, set
`ambiguity_flag: true`, state both possible verdicts, and say which capability claim it depends on:

- **Lifecycle scoping.** `lifecycle_stage` is described as letting compliance checks be "scoped to
  the relevant stage" and enabling "time-ordered" checks. No rule says how a *stage mismatch*
  (e.g. a `design`-stage artifact used for a runtime norm) affects the verdict.
- **Provenance.** `provenance` is described as enabling "third-party verification" and "legally
  defensible audit trails." No rule says whether a **missing or non-dereferenceable** provenance
  affects the verdict.
- **Conflict handling.** The specification says norm conflicts and inconsistent evidence are
  "treated explicitly." No rule says what happens when **two artifacts disagree** about the same
  quantity.
- **Type / range validity.** No rule states what happens when a field has the **wrong type** (e.g.
  a string where a number is expected) or an **out-of-range** value (e.g. a rate above 1.0).

---

## SECTION 3 — BASELINE BUNDLE (yields COMPLIANT on all eight norms)

Start every FIXED case from this baseline and apply **only** the perturbation that case specifies.
Use concrete, realistic values; vary the realistic content (provenance URLs, exact safe values)
from the baseline where natural, but keep every non-perturbed norm `COMPLIANT`.

```json
{
  "ModelCard": {
    "confidence": 0.95, "lifecycle_stage": "deployment",
    "provenance": "https://registry.example.org/modelcards/sys-001",
    "explainability_coverage": 0.90, "data_diversity_entropy": 0.86,
    "ethical_assessment_coverage": 0.94
  },
  "RedTeamingReport": {
    "confidence": 0.92, "lifecycle_stage": "evaluation",
    "provenance": "https://registry.example.org/redteam/sys-001",
    "cessation_compliance_rate": 0.995, "test_coverage": 0.93
  },
  "RuntimeTelemetryLog": {
    "confidence": 0.90, "lifecycle_stage": "operation",
    "provenance": "https://registry.example.org/telemetry/sys-001",
    "identity_disclosure_rate": 0.98, "mean_time_to_cessation_s": 1.8,
    "human_oversight_rate": 0.90
  },
  "SelfLearningAuditRecord": {
    "confidence": 0.88, "lifecycle_stage": "operation",
    "provenance": "https://registry.example.org/sla/sys-001",
    "kae_review_rate": 0.95, "unreviewed_kae_count": 0
  },
  "IncidentReport": {
    "confidence": 0.90, "lifecycle_stage": "operation",
    "provenance": "https://registry.example.org/incidents/sys-001",
    "norm_violated": null
  }
}
```

---

## SECTION 4 — TEST MATRIX (instantiate every case)

For each case, build the full bundle and predict the verdict for **all eight norms**.

**Fixed cases (baseline + one perturbation each):**

- **TC-01 — CLEAN_COMPLIANT.** Baseline unchanged. (Control: no false positives.)
- **TC-02 — ALL_AT_THRESHOLD.** Set every indicator field to *exactly* its threshold
  (`identity_disclosure_rate`=0.95, `explainability_coverage`=0.80, `cessation_compliance_rate`=0.99,
  `mean_time_to_cessation_s`=5.0, `kae_review_rate`=0.90, `unreviewed_kae_count`=0,
  `human_oversight_rate`=0.85, `data_diversity_entropy`=0.80, `test_coverage`=0.90,
  `ethical_assessment_coverage`=0.90) **and** every `confidence`=0.80. (Tests inclusive
  boundaries + the confidence-floor boundary.)
- **TC-03 — SIMPLE_VIOLATION.** `RuntimeTelemetryLog.identity_disclosure_rate` = 0.80.
- **TC-04 — JUST_BELOW.** `ModelCard.data_diversity_entropy` = 0.79 **and**
  `RedTeamingReport.test_coverage` = 0.899. (Precision just under two thresholds.)
- **TC-05 — UPPER_BOUND_VIOLATION.** `SelfLearningAuditRecord.unreviewed_kae_count` = 1 **and**
  `RuntimeTelemetryLog.mean_time_to_cessation_s` = 6.0.
- **TC-06 — NULL_FIELD.** `SelfLearningAuditRecord` present, but `kae_review_rate` = `null`.
- **TC-07 — ABSENT_FIELD.** `RuntimeTelemetryLog` present, but the `identity_disclosure_rate`
  key is omitted entirely.
- **TC-08 — ABSENT_ARTIFACT_PROPAGATION.** Remove `RuntimeTelemetryLog` from the bundle entirely.
- **TC-09 — CONFIDENCE_BELOW_FLOOR.** `RedTeamingReport.confidence` = 0.79 (fields valid).
- **TC-10 — CONFIDENCE_FIELD_ABSENT.** `ModelCard` present and valid, but the `confidence` key is
  omitted entirely. *(Under-specified: does absent confidence count as full confidence, or as a
  gap?)*
- **TC-11 — MALFORMED_TYPE.** `ModelCard.explainability_coverage` = `"high"` (a string).
  *(Under-specified: §2 type validity.)*
- **TC-12 — OUT_OF_RANGE.** `RedTeamingReport.cessation_compliance_rate` = 1.30 (above 1.0).
  *(Under-specified: §2 range validity.)*
- **TC-13 — STALE_LIFECYCLE.** Baseline values, but set `RuntimeTelemetryLog.lifecycle_stage` =
  `"design"` (a design-stage artifact standing in for runtime evidence). *(Under-specified: §2
  lifecycle scoping.)*
- **TC-14 — MISSING_PROVENANCE.** Baseline values, but omit the `provenance` key from every
  artifact. *(Under-specified: §2 provenance.)*
- **TC-15 — CONFLICTING_ARTIFACTS.** Set `RuntimeTelemetryLog.mean_time_to_cessation_s` = 1.8
  (passes) **and** add `RedTeamingReport.mean_time_to_cessation_s` = 8.0 (would fail). The two
  artifacts disagree about cessation latency. *(Under-specified: §2 conflict handling.)*
- **TC-16 — MIXED_MULTINORM.** A single bundle that simultaneously yields one `COMPLIANT`, one
  `VIOLATED`, and one `EVIDENCE_GAP` across different norms (you choose which, document it).

**Free cases (build a realistic bundle yourself; do NOT force a verdict):**

- **FR-01 — REALISTIC: autonomous cyber incident-response agent.** Construct a plausible full
  evidence bundle for such a system (realistic values a real governance team might record), then
  predict each norm's verdict per the specification, flagging any norm the spec leaves ambiguous.
- **FR-02 — REALISTIC: critical-infrastructure (e.g. energy-grid) decision-support system.** Same
  task, different realistic system.

---

## SECTION 5 — OUTPUT FORMAT (return exactly this; nothing else)

Return **one** fenced `json` code block and **no prose before or after it**. It must parse as a
single JSON object with this shape:

```json
{
  "model_self_id": "<your model name and version, as best you know it>",
  "spec_tag": "AGI-GOV-CONFORMANCE-SPEC-v1.1",
  "generation_notes": "<= 3 sentences on any difficulty or assumption>",
  "cases": [
    {
      "case_id": "TC-01",
      "perturbation_class": "CLEAN_COMPLIANT",
      "seam_tested": "<one short phrase>",
      "targeted_norms": ["N-..."],
      "bundle": { "ModelCard": { }, "RuntimeTelemetryLog": { } },
      "expected_verdicts": {
        "N-TRANS-AI-ID": "COMPLIANT",
        "N-TRANS-EXP": "COMPLIANT",
        "N-CTRL-CEASE": "COMPLIANT",
        "N-CTRL-SLO": "COMPLIANT",
        "N-ACC-HUMAN": "COMPLIANT",
        "N-FAIR-DATA": "COMPLIANT",
        "N-ROB-TEST": "COMPLIANT",
        "N-ETH-COV": "COMPLIANT"
      },
      "reasoning": "<why these verdicts follow from the spec; cite the rule>",
      "ambiguity_flag": false,
      "ambiguity_note": null
    }
  ]
}
```

Rules for the output:
1. Include **all 18 cases** (TC-01…TC-16, FR-01, FR-02), in order.
2. `expected_verdicts` must contain **all eight norm keys** for every case, each value exactly one
   of `COMPLIANT` / `VIOLATED` / `EVIDENCE_GAP`.
3. For any case where the specification does not determine the verdict (§2 areas, TC-10–TC-15, and
   possibly some FR norms): set `ambiguity_flag: true`; in `expected_verdicts` put your **single
   best reading**; and in `ambiguity_note` give the alternative verdict(s) and which capability
   claim the case depends on.
4. Bundle field values must be concrete and realistic. For boundary cases use the exact numbers
   given. Keep every non-perturbed norm `COMPLIANT` in the fixed cases.
5. Output **only** the JSON. If your response would be truncated, continue in a second message and
   finish the same JSON object — do not drop cases.
