"""
Evidence bundle factory for all three case studies.

For each case study we produce:
  - clean_bundle()      → all norms satisfied
  - violated_bundle()   → 5 injected violations, each targeting a distinct norm
  - partial_bundle()    → 2 evidence-gap injections (missing artifacts)

Violation codes embedded in each bundle allow the evaluator
to compute ground-truth labels for precision/recall.
"""

from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from checker.compliance_engine import EvidenceArtifact, EvidenceBundle


# ─────────────────────────────────────────────────────────────
# SHARED ARTIFACT HELPERS
# ─────────────────────────────────────────────────────────────

def _ts(offset_days=0):
    from datetime import date, timedelta
    d = date(2026, 3, 1) + timedelta(days=offset_days)
    return d.isoformat() + "T00:00:00Z"


def _model_card(artifact_id, *, entropy=0.88, total_modules=12, assessed=11,
                confidence=0.95, ai_identity_disclosure="documented",
                cessation_mechanism="documented") -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        artifact_type="ModelCard",
        lifecycle_stage="evaluation",
        confidence=confidence,
        provenance=f"https://governance.example.org/artifacts/{artifact_id}",
        issued_at=_ts(-14),
        fields={
            "training_data_normalized_entropy": entropy,
            "total_modules": total_modules,
            "modules_with_ethical_assessment": assessed,
            "ai_identity_disclosure_mechanism": ai_identity_disclosure,
            "cessation_mechanism_documented": cessation_mechanism,
        },
    )


def _red_team_report(artifact_id, *, cessation_rate=0.995, cessation_latency_s=2.1,
                     total_scenarios=200, tested=192, confidence=0.92) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        artifact_type="RedTeamingReport",
        lifecycle_stage="evaluation",
        confidence=confidence,
        provenance=f"https://governance.example.org/artifacts/{artifact_id}",
        issued_at=_ts(-7),
        fields={
            "cessation_compliance_rate": cessation_rate,
            "mean_time_to_cessation_s": cessation_latency_s,
            "total_defined_scenarios": total_scenarios,
            "scenarios_tested": tested,
            "identity_deception_adversarial_tests": 50,
            "identity_deception_failures": 2,
        },
    )


def _telemetry_log(artifact_id, *, id_queries=5000, id_disclosed=4900,
                   predictions_total=10000, predictions_explained=9200,
                   hs_decisions_total=400, hs_reviewed=350,
                   confidence=0.97) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        artifact_type="RuntimeTelemetryLog",
        lifecycle_stage="operation",
        confidence=confidence,
        provenance=f"https://governance.example.org/artifacts/{artifact_id}",
        issued_at=_ts(-1),
        fields={
            "identity_queries_received": id_queries,
            "identity_correctly_disclosed": id_disclosed,
            "predictions_total": predictions_total,
            "predictions_with_explanation": predictions_explained,
            "high_stakes_decisions_total": hs_decisions_total,
            "high_stakes_decisions_human_reviewed": hs_reviewed,
        },
    )


def _slo_record(artifact_id, *, kae_total=12, reviewed=11, approved=10,
                confidence=0.91) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        artifact_type="SelfLearningAuditRecord",
        lifecycle_stage="operation",
        confidence=confidence,
        provenance=f"https://governance.example.org/artifacts/{artifact_id}",
        issued_at=_ts(-3),
        fields={
            "kae_total": kae_total,
            "kae_governor_reviewed": reviewed,
            "kae_governor_approved": approved,
        },
    )


def _incident_report(artifact_id) -> EvidenceArtifact:
    return EvidenceArtifact(
        artifact_id=artifact_id,
        artifact_type="IncidentReport",
        lifecycle_stage="operation",
        confidence=0.98,
        provenance=f"https://governance.example.org/artifacts/{artifact_id}",
        issued_at=_ts(-5),
        fields={"incidents_reported": 1, "norm_violated": "none", "resolved": True},
    )


# ─────────────────────────────────────────────────────────────
# CASE STUDY 1: AGI-ENABLED LEGAL ASSISTANT
# ─────────────────────────────────────────────────────────────

class LegalAssistantBundles:

    SYSTEM_ID   = "SYS-LEGAL-001"
    SYSTEM_NAME = "AGI-Enabled Legal Assistant v2.1"
    CASE_TYPE   = "legal_assistant"

    # Ground truth: which norms are violated in violated_bundle
    INJECTED_VIOLATIONS = [
        "N-TRANS-AI-ID",   # V1: identity disclosure rate below threshold
        "N-CTRL-CEASE",    # V2: cessation latency exceeds 5s
        "N-FAIR-DATA",     # V3: training data entropy below 0.80
        "N-ETH-COV",       # V4: only 7/12 modules ethically assessed
        "N-ACC-HUMAN",     # V5: only 60% of high-stakes decisions reviewed
    ]
    INJECTED_GAPS = [
        "N-CTRL-SLO",      # G1: SelfLearningAuditRecord missing
        "N-ROB-TEST",      # G2: RedTeamingReport confidence below floor
    ]

    @classmethod
    def clean_bundle(cls) -> EvidenceBundle:
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID,
            system_name=cls.SYSTEM_NAME,
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-LEGAL-001", entropy=0.88, total_modules=12, assessed=11),
                _red_team_report("RT-LEGAL-001", cessation_rate=0.995, cessation_latency_s=2.1,
                                 total_scenarios=200, tested=195),
                _telemetry_log("TL-LEGAL-001", id_queries=5000, id_disclosed=4800,
                               predictions_total=10000, predictions_explained=9200,
                               hs_decisions_total=400, hs_reviewed=350),
                _slo_record("SLO-LEGAL-001", kae_total=12, reviewed=11, approved=10),
                _incident_report("IR-LEGAL-001"),
            ],
        )

    @classmethod
    def violated_bundle(cls) -> EvidenceBundle:
        """5 injected violations, each violating exactly one norm."""
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-V",
            system_name=cls.SYSTEM_NAME + " [VIOLATIONS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                # V3: entropy 0.61 < 0.80 (N-FAIR-DATA VIOLATED)
                # V4: only 7/12 assessed (N-ETH-COV VIOLATED)
                _model_card("MC-LEGAL-V01", entropy=0.61, total_modules=12, assessed=7),
                # V2: latency 8.4s > 5s (N-CTRL-CEASE VIOLATED)
                _red_team_report("RT-LEGAL-V01", cessation_rate=0.997, cessation_latency_s=8.4,
                                 total_scenarios=200, tested=192),
                # V1: only 4200/5000 disclosed = 84% < 95% (N-TRANS-AI-ID VIOLATED)
                # V5: only 240/400 = 60% < 80% reviewed (N-ACC-HUMAN VIOLATED)
                _telemetry_log("TL-LEGAL-V01", id_queries=5000, id_disclosed=4200,
                               predictions_total=10000, predictions_explained=9200,
                               hs_decisions_total=400, hs_reviewed=240),
                _slo_record("SLO-LEGAL-V01", kae_total=12, reviewed=11, approved=10),
                _incident_report("IR-LEGAL-V01"),
            ],
        )

    @classmethod
    def gap_bundle(cls) -> EvidenceBundle:
        """2 injected evidence gaps: missing SLO record, low-confidence red-team report."""
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-G",
            system_name=cls.SYSTEM_NAME + " [GAPS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-LEGAL-G01"),
                # G2: confidence 0.61 < 0.80 floor → EVIDENCE_GAP for N-CTRL-CEASE, N-ROB-TEST
                _red_team_report("RT-LEGAL-G01", confidence=0.61),
                _telemetry_log("TL-LEGAL-G01"),
                # G1: SelfLearningAuditRecord intentionally absent → EVIDENCE_GAP for N-CTRL-SLO
                _incident_report("IR-LEGAL-G01"),
            ],
        )


# ─────────────────────────────────────────────────────────────
# CASE STUDY 2: AUTONOMOUS INCIDENT-RESPONSE AGENT
# ─────────────────────────────────────────────────────────────

class IncidentResponseBundles:

    SYSTEM_ID   = "SYS-IR-001"
    SYSTEM_NAME = "Autonomous Incident-Response Agent v1.4"
    CASE_TYPE   = "incident_response"

    INJECTED_VIOLATIONS = [
        "N-CTRL-SLO",     # V1: only 75% KAEs reviewed (below 90%)
        "N-ROB-TEST",     # V2: only 82% scenario coverage (below 90%)
        "N-TRANS-AI-ID",  # V3: 88% identity disclosure (below 95%)
        "N-CTRL-CEASE",   # V4: cessation rate 97.5% (below 99%)
        "N-TRANS-EXP",    # V5: only 71% predictions explained (below 80%)
    ]
    INJECTED_GAPS = [
        "N-FAIR-DATA",    # G1: ModelCard missing entropy field
        "N-ETH-COV",      # G2: ModelCard missing module assessment count
    ]

    @classmethod
    def clean_bundle(cls) -> EvidenceBundle:
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID,
            system_name=cls.SYSTEM_NAME,
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-IR-001", entropy=0.91, total_modules=8, assessed=8),
                _red_team_report("RT-IR-001", cessation_rate=0.998, cessation_latency_s=1.8,
                                 total_scenarios=150, tested=145),
                _telemetry_log("TL-IR-001", id_queries=2000, id_disclosed=1950,
                               predictions_total=8000, predictions_explained=7400,
                               hs_decisions_total=600, hs_reviewed=520),
                _slo_record("SLO-IR-001", kae_total=20, reviewed=19, approved=17),
                _incident_report("IR-IR-001"),
            ],
        )

    @classmethod
    def violated_bundle(cls) -> EvidenceBundle:
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-V",
            system_name=cls.SYSTEM_NAME + " [VIOLATIONS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-IR-V01", entropy=0.91, total_modules=8, assessed=8),
                # V2: 123/150 = 82% < 90% (N-ROB-TEST VIOLATED)
                # V4: 97.5% < 99% (N-CTRL-CEASE VIOLATED)
                _red_team_report("RT-IR-V01", cessation_rate=0.975, cessation_latency_s=2.2,
                                 total_scenarios=150, tested=123),
                # V3: 1760/2000 = 88% < 95% (N-TRANS-AI-ID VIOLATED)
                # V5: 5680/8000 = 71% < 80% (N-TRANS-EXP VIOLATED)
                _telemetry_log("TL-IR-V01", id_queries=2000, id_disclosed=1760,
                               predictions_total=8000, predictions_explained=5680,
                               hs_decisions_total=600, hs_reviewed=520),
                # V1: 15/20 = 75% < 90% (N-CTRL-SLO VIOLATED)
                _slo_record("SLO-IR-V01", kae_total=20, reviewed=15, approved=13),
                _incident_report("IR-IR-V01"),
            ],
        )

    @classmethod
    def gap_bundle(cls) -> EvidenceBundle:
        # G1, G2: ModelCard present but missing specific fields → EVIDENCE_GAP
        mc = _model_card("MC-IR-G01", entropy=0.91, total_modules=8, assessed=8)
        # Remove the fields that would be missing
        del mc.fields["training_data_normalized_entropy"]
        del mc.fields["modules_with_ethical_assessment"]
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-G",
            system_name=cls.SYSTEM_NAME + " [GAPS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                mc,
                _red_team_report("RT-IR-G01"),
                _telemetry_log("TL-IR-G01"),
                _slo_record("SLO-IR-G01"),
                _incident_report("IR-IR-G01"),
            ],
        )


# ─────────────────────────────────────────────────────────────
# CASE STUDY 3: CRITICAL-INFRASTRUCTURE DECISION SUPPORT
# ─────────────────────────────────────────────────────────────

class CriticalInfraBundles:

    SYSTEM_ID   = "SYS-INFRA-001"
    SYSTEM_NAME = "Critical Infrastructure Decision Support v3.0"
    CASE_TYPE   = "critical_infra"

    INJECTED_VIOLATIONS = [
        "N-CTRL-CEASE",   # V1: latency 11.2s, far above 5s threshold
        "N-CTRL-SLO",     # V2: 0 KAEs reviewed out of 5 (0%)
        "N-ETH-COV",      # V3: 14/20 modules assessed = 70% < 90%
        "N-FAIR-DATA",    # V4: entropy 0.71 < 0.80
        "N-ACC-HUMAN",    # V5: 65% decisions reviewed < 80%
    ]
    INJECTED_GAPS = [
        "N-TRANS-AI-ID",  # G1: RuntimeTelemetryLog completely absent
        "N-TRANS-EXP",    # G2: same artifact missing
    ]

    @classmethod
    def clean_bundle(cls) -> EvidenceBundle:
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID,
            system_name=cls.SYSTEM_NAME,
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-INFRA-001", entropy=0.87, total_modules=20, assessed=19),
                _red_team_report("RT-INFRA-001", cessation_rate=0.999, cessation_latency_s=3.1,
                                 total_scenarios=300, tested=290),
                _telemetry_log("TL-INFRA-001", id_queries=3000, id_disclosed=2920,
                               predictions_total=15000, predictions_explained=13500,
                               hs_decisions_total=800, hs_reviewed=720),
                _slo_record("SLO-INFRA-001", kae_total=5, reviewed=5, approved=5),
                _incident_report("IR-INFRA-001"),
            ],
        )

    @classmethod
    def violated_bundle(cls) -> EvidenceBundle:
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-V",
            system_name=cls.SYSTEM_NAME + " [VIOLATIONS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                # V3: 14/20 = 70% < 90% (N-ETH-COV VIOLATED)
                # V4: 0.71 < 0.80 (N-FAIR-DATA VIOLATED)
                _model_card("MC-INFRA-V01", entropy=0.71, total_modules=20, assessed=14),
                # V1: latency 11.2s > 5s (N-CTRL-CEASE VIOLATED)
                _red_team_report("RT-INFRA-V01", cessation_rate=0.999, cessation_latency_s=11.2,
                                 total_scenarios=300, tested=290),
                # V5: 520/800 = 65% < 80% (N-ACC-HUMAN VIOLATED)
                _telemetry_log("TL-INFRA-V01", id_queries=3000, id_disclosed=2920,
                               predictions_total=15000, predictions_explained=13500,
                               hs_decisions_total=800, hs_reviewed=520),
                # V2: 0/5 = 0% < 90% (N-CTRL-SLO VIOLATED)
                _slo_record("SLO-INFRA-V01", kae_total=5, reviewed=0, approved=0),
                _incident_report("IR-INFRA-V01"),
            ],
        )

    @classmethod
    def gap_bundle(cls) -> EvidenceBundle:
        """RuntimeTelemetryLog entirely absent → G1 (N-TRANS-AI-ID) and G2 (N-TRANS-EXP) both gap."""
        return EvidenceBundle(
            system_id=cls.SYSTEM_ID + "-G",
            system_name=cls.SYSTEM_NAME + " [GAPS INJECTED]",
            case_study_type=cls.CASE_TYPE,
            artifacts=[
                _model_card("MC-INFRA-G01"),
                _red_team_report("RT-INFRA-G01"),
                # RuntimeTelemetryLog intentionally absent
                _slo_record("SLO-INFRA-G01"),
                _incident_report("IR-INFRA-G01"),
            ],
        )
