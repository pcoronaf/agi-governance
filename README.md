# AGI Governance Compliance Model

**Vocabulary namespace:** `https://w3id.org/agi-governance/evidence/ns/v1.0/`  
**Norm base URI:** `https://w3id.org/agi-governance/norms/`  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (docs & vocabulary); MIT (code)  
**Engine version:** 1.4 · Updated 2026-09-27

This repository is the supplementary resource for:

> Corona Fraga, P., Diab, A.M.E-A., Hwang, S.H., & Diaz, V. (2026).
> *Machine-checkable compliance for AGI Governance: Formalizing principles
> as auditable norms and evidence-linked indicators.* Manuscript under review.

---

## What is in this repository

| Path | Description |
|------|-------------|
| `agi_governance_legalruleml.xml` | AGI Evidence Vocabulary (agiev) and LegalRuleML encoding of three representative AGI-specific norms (N-TRANS-AI-ID, N-CTRL-CEASE, N-CTRL-SLO), with normative-source metadata (LegalSources / Authorities, source class S1–S4) |
| `checker/compliance_engine.py` | Reference compliance checker (v1.4): indicator measurement, two-phase norm verdict aggregation, report generation; every verdict carries the norm's source class, addressee and evidence owner |
| `evidence/evidence_bundles.py` | Evidence-bundle factory for the three case-study domains (legal assistant, incident-response agent, critical infrastructure) |
| `run_validation.py` | Synthetic validation harness over the nine bundles (§8.2–8.3): violation and gap detection, explanation completeness, timing |
| `compute_metrics.py` | Reproducible generator for `results/aggregate_metrics.json` |
| `results/validation_results.json` | Full per-bundle reports from the reference run |
| `results/aggregate_metrics.json` | Aggregate evaluation metrics |
| `conformance/` | Blind conformance evaluation (§8.4): prompt, three model outputs, harness, results |
| `component2/` | Turnkey kit for the deferred auditor-confirmed validation (protocol, rubric, labeling instruments, analysis) |
| `public_study/` | Real-evidence bridgeability study (§8.5): majority-resolved mapping script (`run_public_study.py`), results, three-coder judgment matrix, reliability analysis, reconciliation log, coding protocol, completed instruments |
| `CITATION.cff` | Citation metadata |

---

## The AGI Evidence Vocabulary (agiev)

The `agiev` namespace extends the [OASIS LegalRuleML Core Specification 1.0](https://docs.oasis-open.org/legalruleml/) with three cross-cutting field extensions and three novel artifact types required for AGI governance. The reference engine (v1.4) **enforces** the three cross-cutting fields as admissibility rules.

| Field | Type | Enforcement |
|-------|------|-------------|
| `lifecycle_stage` | enum `{design, training, evaluation, deployment, operation}` | Situates each artifact in the AI governance lifecycle and scopes checks to the relevant stage: evidence carrying a stage inadmissible for a norm yields `EVIDENCE_GAP`. Aligned with the lifecycle-oriented controls of ISO/IEC 42001:2023. |
| `confidence` | decimal [0.0–1.0] | Artifacts below the floor (default 0.80), **or with no confidence field**, yield `EVIDENCE_GAP` (flagged for human auditor review) rather than an automated verdict. |
| `provenance` | xsd:anyURI | Presence of a well-formed provenance URI is required for admissible evidence; a missing or malformed value yields `EVIDENCE_GAP`. Consistent with the technical-documentation and record-keeping obligations of the EU AI Act (Arts. 11 and 12) and the W3C PROV model. Cryptographic verification (dereferencing, signatures) is future work. |

### Novel AGI-specific artifact types

| Type | Used by norm | Description |
|------|-------------|-------------|
| `agiev:SelfLearningAuditRecord` | N-CTRL-SLO | Knowledge acquisition events (KAEs): autonomous learning, goal modification, or capability emergence not present at the last governed checkpoint. |
| Cessation fields in `agiev:RedTeamingReport` / `agiev:RuntimeTelemetryLog` | N-CTRL-CEASE | `cessation_compliance_rate`, `mean_time_to_cessation_s` — time to reach the governed **safe state** defined for the deployment (which may be a staged degradation or a fallback handover, not necessarily an instantaneous halt; cf. EU AI Act Art. 14(4)(e)). |
| Identity-disclosure fields in `agiev:RuntimeTelemetryLog` | N-TRANS-AI-ID | `identity_disclosure_rate` (with raw `identity_queries_received` / `identity_correctly_disclosed`). |

---

## Norm sources and binding force

The instruments the norms come from are not of one kind, and the model records the difference rather than flattening it (paper §5.1). Each norm carries a **source class**, stored in the LegalRuleML encoding through `lrml:LegalSources` / `lrml:Authorities` and carried by the engine into every verdict together with the norm's addressee and evidence owner.

| Class | Meaning | Example | Consequence of a `VIOLATED` verdict |
|-------|---------|---------|-------------------------------------|
| S1 | Binding law; binds providers and deployers; enforced by market surveillance and fines | EU AI Act | Evidence relevant to a legal determination that only an authority or court can make |
| S2 | Voluntary consensus standard; binds adopting organizations; conformity attested by certification — **not** compliance with the AI Act, and no presumption of conformity unless adopted as a harmonised standard (Art. 40) | ISO/IEC 42001:2023 | Nonconformity in the sense of the standard |
| S3 | Soft-law principle; addressed to governments; no direct legal effect on operators | OECD AI Principles | Departure from an adopted commitment |
| S4 | Author-proposed control objective; no binding force of its own | N-TRANS-AI-ID, N-CTRL-CEASE, N-CTRL-SLO | Departure from an adopted commitment |

Implemented norms: N-TRANS-AI-ID, N-CTRL-CEASE and N-CTRL-SLO are S4 (closest binding analogues: Arts. 50(1), 14(4)(e) and 72 of the AI Act, from each of which the norm differs in scope); N-ACC-HUMAN, N-FAIR-DATA, N-ROB-TEST and N-TRANS-EXP are S2 with S1 analogues confined to high-risk systems (Arts. 14, 10, 15, 13); N-ETH-COV is S2 with an S3 basis. See `NORM_SOURCE` in `checker/compliance_engine.py`.

*An engine verdict is an evidentiary record, not a legal determination; its weight follows the norm's source class. Missing evidence is never classified as compliance or as violation — `EVIDENCE_GAP` escalates to human review, and the duty to produce the evidence stays with the operating organization.*

---

## Compliance checker quick start

```bash
# Python 3.9+, no external dependencies
git clone https://github.com/pcoronaf/agi-governance
cd agi-governance

python run_validation.py                 # synthetic validation over the 9 bundles (§8.2–8.3)
python compute_metrics.py                # regenerate results/aggregate_metrics.json
python conformance/run_conformance.py    # blind conformance evaluation (§8.4)
python public_study/run_public_study.py     # real-evidence bridgeability, majority-resolved mapping (§8.5)
python public_study/compute_reliability.py  # inter-coder reliability, bridgeability study (§8.5)
```

### Run the checker on your own evidence bundle

A bundle is a plain `dict` keyed by artifact type; each artifact is a `dict` with
`confidence`, `lifecycle_stage`, `provenance`, and the type-specific fields the
indicators read. The entry point is `run_compliance_check`.

```python
import sys; sys.path.insert(0, "checker")
from compliance_engine import run_compliance_check

bundle = {
    "ModelCard": {
        "confidence": 0.95, "lifecycle_stage": "deployment",
        "provenance": "https://your-org.example/governance/MC-001",
        "explainability_coverage": 0.90, "data_diversity_entropy": 0.86,
        "ethical_assessment_coverage": 0.94,
    },
    "RedTeamingReport": {
        "confidence": 0.92, "lifecycle_stage": "evaluation",
        "provenance": "https://your-org.example/governance/RT-001",
        "cessation_compliance_rate": 0.995, "test_coverage": 0.93,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.90, "lifecycle_stage": "operation",
        "provenance": "https://your-org.example/governance/TL-001",
        "identity_disclosure_rate": 0.98, "mean_time_to_cessation_s": 1.8,
        "human_oversight_rate": 0.90,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.88, "lifecycle_stage": "operation",
        "provenance": "https://your-org.example/governance/SL-001",
        "kae_review_rate": 0.95, "unreviewed_kae_count": 0,
    },
    "IncidentReport": {
        "confidence": 0.90, "lifecycle_stage": "operation",
        "provenance": "https://your-org.example/governance/IN-001",
    },
}

report = run_compliance_check(
    system_id="YOUR-SYSTEM-ID", case_study="legal_assistant",
    bundle_type="live", evidence_bundle=bundle,
)
for nv in report.norms:
    print(nv.norm_id, nv.verdict.value, "—", nv.remediation or "")
```

Each verdict is `COMPLIANT`, `VIOLATED`, or `EVIDENCE_GAP`. The `provenance` value
should point to the actual artifact in your governance repository; the vocabulary
namespace URI is a schema identifier, not an artifact location.

---

## Evaluation results summary

Across 3 case studies and 8 norms. Violation detection is reported at two units:
the **indicator level** (individual out-of-threshold fields; 15 injected) and the
**norm level** (`VIOLATED` verdicts; 13, because in Critical Infrastructure five
injected indicator violations fall on three norms). Full data in
`results/aggregate_metrics.json`.

| Metric | Value |
|--------|-------|
| Violation detection — indicator level (recall) | 15/15 = 1.000 |
| Violation detection — norm level (P / R / F1) | 1.000 / 1.000 / 1.000 (TP=13, FP=0, FN=0) |
| Gap detection — injection-level recall | 6/6 = 1.000 |
| Total `EVIDENCE_GAP` verdicts (incl. 1 propagated) | 7 |
| Explanation completeness | 1.000 |
| Mean report generation time | ~0.15 ms |

**On propagation.** A single missing `RuntimeTelemetryLog` correctly triggers
`EVIDENCE_GAP` on every norm that depends on it; these propagated verdicts are
correct behaviour and are reported separately from injection-level detection, not
counted as false positives.

**Evaluation semantics (Global Evaluation Precondition).** Absent or null fields,
missing artifacts, non-numeric or out-of-range values, and artifacts below the
confidence floor (or with no confidence field) all yield `EVIDENCE_GAP` before any
threshold comparison — never a spurious `VIOLATED`. See the changelog below.

**Threshold status (§5.3).** Every numeric threshold the engine applies — ≥0.95
identity disclosure, ≥0.99 cessation compliance, ≤5 s cessation latency, ≥0.90
self-learning-oversight review, 0 unreviewed KAEs, ≥0.80 explainability coverage,
≥0.85 human oversight, ≥0.80 training-data diversity entropy, ≥0.90 test coverage,
≥0.90 ethical assessment coverage, and the 0.80 evidence-confidence floor — is a
**prototype-level reference value** (class (a) in the paper's typology): an
expert-derived reference point that makes the indicator executable and exercises the
verdict logic. None is fixed by an external standard or regulation (class (b)) and none
has been empirically calibrated on real evidence packages (class (c)); the obligations
that motivate the indicators (EU AI Act Art. 50, ISO/IEC 42001:2023 Annex A) are
qualitative and set no numeric rate. Thresholds are configuration parameters
(`THRESHOLDS` in `checker/compliance_engine.py`), reported with their class alongside
every verdict, and are expected to be recalibrated by the deferred auditor-confirmed
study in `component2/`.

**Blind conformance (§8.4).** Independent of the synthetic run above, three LLMs
(GPT-5.5, Claude Sonnet 5, Gemini 3.5 Flash) generated 18 test cases each; on the 15 controlled cases the models agreed on all
120 verdict cells (raw agreement 120/120; κ is uninformative under zero variance),
and the engine matched the resolved specification on 428 of 432 cells; the four
exceptions come from one generated bundle that omits a provenance field, which the
engine correctly flags as `EVIDENCE_GAP`. Generation prompts, all 54
bundles and the predicted-verdict records are in `conformance/`. Model identities are confirmed from provider usage history, not from the models' self-reports (the Gemini run self-identified as "Gemini 1.5 Pro"); see `conformance/README.md`.

**Real-evidence bridgeability (§8.5).** Two generations of published frontier
model/system cards (2024: GPT-4o, Claude 3.5 Sonnet, Llama 3.1; 2025–26: GPT-5.5,
Claude Opus 4.6, Gemini 3) were mapped to the schema by **three independent coders** —
the author team and two external ISO/IEC 42001 auditors blinded to each other's
cell-level judgments. On the strict pass the coders agreed on all 60 cells: no
indicator was computable from any card. On the generous, flagged-proxy pass agreement
was substantial (Fleiss' κ = 0.709; pairwise Cohen's κ 0.640–0.783; PABAK ≥ 0.900;
56/60 cells unanimous), and the four disagreements — all about proxy admissibility —
were resolved by majority vote (≥2 of 3) with author review of each rationale. Resulting figures: computable indicators
2→3 of 30 and evaluable norms 2→3 of 24 across generations, every one of them on the
generic robustness-testing indicator — while the five AGI-specific indicators were
computable from **zero** cards in either generation (0/15 → 0/15), unanimously across
all three coders. The gap the model targets is not closing on its own. Matrix,
analysis code, reconciliation log and completed instruments in `public_study/`.

**Deferred: auditor-confirmed validation (Component 2).** Accuracy against
auditor-confirmed ground truth on real ISO/IEC 42001:2023 evidence packages is the
fourth evaluation rung; it is deliberately deferred (the AGI-specific evidence it
needs is not yet produced, per §8.5) with a complete turnkey protocol provided in
`component2/`.

---

## Engine changelog

| Version | Change |
|---------|--------|
| 1.1 | Corrected evaluation precondition: mandatory null/absent-field checking before threshold evaluation (paper §8.3). |
| 1.2 | Type-and-range guard (non-numeric or out-of-range field → `EVIDENCE_GAP`); per-norm fault isolation (one malformed field no longer aborts the whole report); absent `confidence` field treated as unverified → `EVIDENCE_GAP`. Surfaced by the blind conformance suite (§8.4). |
| 1.3 | Lifecycle-stage scoping and provenance-presence enforced as admissibility rules. |
| 1.4 | Source class (S1–S4), source instrument, addressee and evidence owner carried in every norm verdict; threshold class carried in every indicator result (paper §5.1, §5.3, §5.5). Cessation relation renamed `entersPredefinedSafeStateOrHalts` in the XML. Additive metadata only — no verdict changes; `run_validation.py` now runs from the repository root and writes to `results/`. |

---

## Relation to ISO/IEC 42001:2023

The agiev vocabulary and compliance model complement, not replace, ISO/IEC
42001:2023 certification. ISO/IEC 42001 specifies what evidence organizations must
produce and retain; the compliance model specifies how those artifacts can be
represented as formal, machine-checkable norms. The five artifact types
(ModelCard, RedTeamingReport, RuntimeTelemetryLog, SelfLearningAuditRecord,
IncidentReport) correspond to evidence categories under ISO/IEC 42001:2023 Annex A
controls, so a single evidence corpus supports both management-system certification
and automated compliance checking.

ISO/IEC 42001:2023 is a **voluntary** standard: it binds only organizations that adopt
it, certification attests conformity with the standard's own requirements (not
compliance with the EU AI Act or any other law), and it is not, at the time of writing,
a harmonised standard under Art. 40 of the Act, so it confers no presumption of legal
conformity. The model uses it as a source of evidence types and organizational controls,
never as a proxy for legal compliance (source class S2 above).

---

## Namespace persistence

The `agiev` vocabulary namespace and norm base URI are registered through
[W3ID](https://w3id.org/); the `.htaccess` redirect is maintained in the
[w3id.org repository](https://github.com/perma-id/w3id.org/tree/master/agi-governance)
and resolves to this repository.

---

## How to cite

See `CITATION.cff`. For manual citation:

> Corona Fraga, P., Diab, A.M.E-A., Hwang, S.H., & Diaz, V. (2026). *Machine-checkable compliance for AGI Governance: Formalizing principles as auditable norms and evidence-linked indicators.* Manuscript under review. Repository: https://github.com/pcoronaf/agi-governance. Vocabulary: https://w3id.org/agi-governance.

---

## Contact

Corresponding author: Prof. Pablo Corona Fraga — pablo.coronaf@infotec.mx  
INFOTEC — Research Center for Information and Communication Technologies, Mexico City, Mexico
