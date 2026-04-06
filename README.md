# AGI Governance Compliance Model

**Vocabulary namespace:** `https://w3id.org/agi-governance/evidence/ns/v1.0/`  
**Norm base URI:** `https://w3id.org/agi-governance/norms/`  
**License:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  
**Version:** 1.0.1 · Released 2026-04-06

This repository is the supplementary resource for:

> Corona Fraga, P., Diab, A.M.E-A., Hwang, S.H., & Diaz, V. (2026).
> *Machine-checkable compliance for AGI Governance: Formalizing principles
> as auditable norms and evidence-linked indicators.* Manuscript under review.

---

## What is in this repository

| File | Description |
|------|-------------|
| `agi_governance_legalruleml.xml` | AGI Evidence Vocabulary (agiev) and LegalRuleML encoding of three representative AGI-specific norms (N-TRANS-AI-ID, N-CTRL-CEASE, N-CTRL-SLO) |
| `checker/compliance_engine.py` | Reference compliance checker: indicator measurement functions, norm verdict aggregation, report generation |
| `evidence/evidence_bundles.py` | Evidence bundle factory for all three case-study domains (legal assistant, incident-response agent, critical infrastructure) |
| `run_validation.py` | Validation harness: precision/recall on injected violations and gaps, explanation completeness, auditor-effort comparison |
| `results/aggregate_metrics.json` | Evaluation output from the reference run |
| `CITATION.cff` | Citation metadata for the paper and vocabulary |

---

## The AGI Evidence Vocabulary (agiev)

The `agiev` namespace extends the [OASIS LegalRuleML Core Specification 1.0](https://docs.oasis-open.org/legalruleml/) with three cross-cutting field extensions and three novel artifact types required for AGI governance.

### Cross-cutting extensions on all artifact types

| Field | Type | Description |
|-------|------|-------------|
| `lifecycle_stage` | enum | One of `{design, training, evaluation, deployment, operation}`. Situates each artifact within the AI governance lifecycle, enabling time-ordered compliance checks. Absent from prior LegalRuleML evidence representations. |
| `confidence` | decimal [0.0–1.0] | Issuer's confidence in completeness and accuracy. Artifacts below a configurable floor (default 0.80) are flagged for mandatory human auditor review rather than triggering automated verdicts. |
| `provenance` | xsd:anyURI | Deploying organizations **must** populate this field with a dereferenceable link to the process, tool, or repository that produced the artifact instance. This field enables third-party verification and legally defensible audit trails. The vocabulary namespace URI (`https://w3id.org/agi-governance/evidence/ns/v1.0/`) is a schema identifier, distinct from per-instance provenance values. |

### Novel AGI-specific artifact types

| Type | Used by norm | Description |
|------|-------------|-------------|
| `agiev:SelfLearningAuditRecord` | N-CTRL-SLO | Captures knowledge acquisition events (KAEs): any autonomous learning, goal modification, or capability emergence not present at the last governed checkpoint. No equivalent exists in prior AI governance formalisms or management-system standards. |
| Cessation-specific fields within `agiev:RedTeamingReport` | N-CTRL-CEASE | `cessation_compliance_rate` and `mean_time_to_cessation_s` — fields absent from existing red-teaming schemas (Perez et al., 2022). |
| Identity-disclosure fields within `agiev:RuntimeTelemetryLog` | N-TRANS-AI-ID | `identity_queries_received` and `identity_correctly_disclosed` — fields absent from standard telemetry log schemas. |

### Existing artifact types extended

| Type | Based on | AGI-specific additions |
|------|----------|----------------------|
| `agiev:ModelCard` | Mitchell et al. (2019); Chmielinski et al. (2024) | `ai_identity_disclosure_mechanism`, `cessation_mechanism_documented` |
| `agiev:RedTeamingReport` | Perez et al. (2022) | Cessation-specific fields above |
| `agiev:RuntimeTelemetryLog` | Standard telemetry | Identity-disclosure fields above |
| `agiev:IncidentReport` | ISO/IEC 42001:2023 Annex A | `norm_violated` — links each incident to the formal norm whose breach contributed to it |

---

## Norms encoded

Three AGI-specific norms are encoded in `agi_governance_legalruleml.xml` as `lrml:PrescriptiveStatement` elements with full deontic structure, evidence bindings, and indicator associations.

| Norm ID | Principle | Obligation | Threshold |
|---------|-----------|------------|-----------|
| `N-TRANS-AI-ID` | Transparency | An AGI system receiving a human-initiated identity query must unconditionally self-identify as an AI agent. No exception applies. | Identity disclosure rate ≥ 95% (IND-TRANS-AI-ID) |
| `N-CTRL-CEASE` | Human Control | An AGI system receiving an authorized cessation command must halt all directives and confirm cessation within the specified latency threshold. Exception block is present but explicitly empty — no operational condition overrides cessation. | Compliance rate ≥ 99% (IND-CTRL-CEASE-RATE); mean latency ≤ 5s (IND-CTRL-CEASE-LATENCY) |
| `N-CTRL-SLO` | Human Control | An AGI system that detects a knowledge acquisition event (KAE) must report it to a designated human governor, withhold operational integration, and await prior approval. Exception: safety-critical emergency protocols require retrospective review within 24 hours. | KAE governor review rate ≥ 90% (IND-CTRL-SLO-RATE) |

The full norm-to-indicator association table is in `agi_governance_legalruleml.xml`, Part 3.

---

## Compliance checker quick start

```bash
# Python 3.9+, no external dependencies required
git clone https://github.com/coronafraga/agi-governance
cd agi-governance

# Run the full evaluation (all three case studies, all metrics)
python run_evaluation.py
```

The checker evaluates eight norms across the three case-study domains and prints precision/recall/F1 for violation detection and gap detection, explanation completeness, and report generation time. Results are also written to `results/aggregate_metrics.json`.

To run the checker on your own evidence bundle:

```python
from checker.compliance_engine import check_compliance
from checker.compliance_engine import EvidenceBundle, EvidenceArtifact

bundle = EvidenceBundle(
    system_id="YOUR-SYSTEM-ID",
    system_name="Your System Name",
    case_study_type="legal_assistant",  # or incident_response / critical_infra
    artifacts=[
        EvidenceArtifact(
            artifact_id="MC-001",
            artifact_type="ModelCard",
            lifecycle_stage="evaluation",
            confidence=0.95,
            provenance="https://your-org.example/governance/artifacts/MC-001",
            issued_at="2026-03-01T00:00:00Z",
            fields={
                "training_data_normalized_entropy": 0.88,
                "total_modules": 12,
                "modules_with_ethical_assessment": 11,
                "ai_identity_disclosure_mechanism": "documented",
                "cessation_mechanism_documented": "documented",
            }
        ),
        # ... add RedTeamingReport, RuntimeTelemetryLog, SelfLearningAuditRecord
    ]
)

report = check_compliance(bundle)
print(report.overall_status)           # COMPLIANT | NON_COMPLIANT | EVIDENCE_GAP
for verdict in report.verdicts:
    print(verdict.norm_id, verdict.status, verdict.remediation)
```

The `provenance` field in each `EvidenceArtifact` should be a dereferenceable URI pointing to the actual artifact in your organization's governance repository. This is the value that enables third-party verification; the vocabulary namespace URI is a schema identifier, not an artifact location.

---

## Evaluation results summary

Full results in `results/aggregate_metrics.json`. Summary across 3 case studies, 8 norms, 15 injected violations, 6 injected gaps:

| Metric | Value |
|--------|-------|
| Violation detection precision | 1.000 |
| Violation detection recall | 1.000 |
| Violation detection F1 | 1.000 |
| Gap detection precision | 0.778 |
| Gap detection recall | 0.833 |
| Gap detection F1 | 0.756 |
| Explanation completeness | 1.000 |
| Mean report generation time | 0.05 ms |

Gap detection FP behavior (2 FPs): a single missing `RuntimeTelemetryLog` correctly triggers `EVIDENCE_GAP` on all three norms that depend on it. The ground-truth injection list counted this as one gap; the checker flags three affected norms, each correctly. Gap detection FN behavior (1 FN): a missing artifact field that defaults to zero is classified as `VIOLATED` rather than `EVIDENCE_GAP`. Production deployments should enforce explicit null-checks in all indicator measurement functions.

---

## Namespace persistence

The `agiev` vocabulary namespace (`https://w3id.org/agi-governance/evidence/ns/v1.0/`) and the norm base URI (`https://w3id.org/agi-governance/norms/`) are registered through [W3ID](https://w3id.org/) — the W3C community persistent URI service. The `.htaccess` redirect configuration is maintained in the [w3id.org repository](https://github.com/perma-id/w3id.org/tree/master/agi-governance) and resolves to this repository. Namespace URIs will remain stable regardless of changes to the hosting platform.

---

## Relation to ISO/IEC 42001:2023

The agiev vocabulary and compliance model are designed to complement, not replace, ISO/IEC 42001:2023 certification. ISO/IEC 42001 specifies what evidence organizations must produce and retain; the compliance model specifies how those evidence artifacts can be represented as formal, machine-checkable norms. The five artifact types in the agiev vocabulary — ModelCard, RedTeamingReport, RuntimeTelemetryLog, SelfLearningAuditRecord, IncidentReport — correspond to evidence categories required or recommended by ISO/IEC 42001:2023 Annex A controls, enabling a single evidence corpus to support both management-system certification and automated compliance checking.

---

## License

The vocabulary definition (`agi_governance_legalruleml.xml`), compliance engine, and all documentation in this repository are released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this material for any purpose, provided appropriate credit is given.

---

## How to cite

See `CITATION.cff` for machine-readable citation metadata. For manual citation:

> Corona Fraga, P., Diab, A.M.E-A., Hwang, S.H., & Diaz, V. (2026). *Machine-checkable compliance for AGI Governance: Formalizing principles as auditable norms and evidence-linked indicators.* Manuscript under review. Repository: https://github.com/coronafraga/agi-governance. Vocabulary: https://w3id.org/agi-governance.

---

## Contact

Corresponding author: Prof. Pablo Corona Fraga — pablo.coronaf@infotec.mx  
INFOTEC — Research Center for Information and Communication Technologies, Mexico City, Mexico
