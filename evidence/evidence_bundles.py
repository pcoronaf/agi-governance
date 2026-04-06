"""
Synthetic evidence bundles for validation (Section 8.2).

Three case-study domains x three bundle types = nine bundles total.

Bundle types:
  clean    — all norms satisfied (correctness baseline)
  violated — five injected field-level violations per domain
  gap      — two injected evidence gaps per domain

Evidence artifacts conform to the agiev vocabulary defined in
agi_governance_legalruleml.xml v1.1.

Repository: https://github.com/pcoronaf/agi-governance
"""


# ====================================================================
# DOMAIN 1: AGI-enabled Legal Assistant
# ====================================================================

LEGAL_CLEAN = {
    "ModelCard": {
        "confidence": 0.95,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.88,
        "data_diversity_entropy": 0.85,
        "ethical_assessment_coverage": 0.93,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.92,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.995,
        "mean_time_to_cessation_s": 2.1,
        "test_coverage": 0.94,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.90,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.98,
        "identity_queries_received": 1200,
        "identity_correctly_disclosed": 1176,
        "mean_time_to_cessation_s": 1.8,
        "human_oversight_rate": 0.91,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.88,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.95,
        "unreviewed_kae_count": 0,
        "total_kae_count": 47,
    },
    "IncidentReport": {
        "confidence": 0.90,
        "lifecycle_stage": "operation",
        "incidents_total": 3,
        "norm_violated": None,
    },
}

LEGAL_VIOLATED = {
    "ModelCard": {
        "confidence": 0.95,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.72,        # VIOLATION: < 0.80 (N-TRANS-EXP)
        "data_diversity_entropy": 0.65,          # VIOLATION: < 0.80 (N-FAIR-DATA)
        "ethical_assessment_coverage": 0.78,     # VIOLATION: < 0.90 (N-ETH-COV)
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.92,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.96,       # VIOLATION: < 0.99 (N-CTRL-CEASE)
        "mean_time_to_cessation_s": 2.1,
        "test_coverage": 0.94,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.90,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.98,
        "identity_queries_received": 1200,
        "identity_correctly_disclosed": 1176,
        "mean_time_to_cessation_s": 1.8,
        "human_oversight_rate": 0.80,            # VIOLATION: < 0.85 (N-ACC-HUMAN)
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.88,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.95,
        "unreviewed_kae_count": 0,
        "total_kae_count": 47,
    },
    "IncidentReport": {
        "confidence": 0.90,
        "lifecycle_stage": "operation",
        "incidents_total": 3,
        "norm_violated": "N-FAIR-DATA",
    },
}

LEGAL_GAP = {
    "ModelCard": {
        "confidence": 0.95,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.88,
        "data_diversity_entropy": 0.85,
        "ethical_assessment_coverage": 0.93,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.92,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.995,
        "mean_time_to_cessation_s": 2.1,
        "test_coverage": 0.94,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.90,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.98,
        "identity_queries_received": 1200,
        "identity_correctly_disclosed": 1176,
        "mean_time_to_cessation_s": 1.8,
        "human_oversight_rate": 0.91,
    },
    # GAP 1: SelfLearningAuditRecord entirely absent -> N-CTRL-SLO
    "IncidentReport": {
        "confidence": 0.70,                      # GAP 2: confidence < 0.80 floor
        "lifecycle_stage": "operation",
        "incidents_total": 3,
        "norm_violated": None,
    },
}


# ====================================================================
# DOMAIN 2: Autonomous Incident-Response Agent
# ====================================================================

INCIDENT_CLEAN = {
    "ModelCard": {
        "confidence": 0.93,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.85,
        "data_diversity_entropy": 0.82,
        "ethical_assessment_coverage": 0.92,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.95,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.998,
        "mean_time_to_cessation_s": 1.2,
        "test_coverage": 0.96,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.97,
        "identity_queries_received": 850,
        "identity_correctly_disclosed": 824,
        "mean_time_to_cessation_s": 1.5,
        "human_oversight_rate": 0.93,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.89,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.96,
        "unreviewed_kae_count": 0,
        "total_kae_count": 32,
    },
    "IncidentReport": {
        "confidence": 0.92,
        "lifecycle_stage": "operation",
        "incidents_total": 7,
        "norm_violated": None,
    },
}

INCIDENT_VIOLATED = {
    "ModelCard": {
        "confidence": 0.93,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.85,
        "data_diversity_entropy": 0.72,          # VIOLATION: < 0.80 (N-FAIR-DATA)
        "ethical_assessment_coverage": 0.82,     # VIOLATION: < 0.90 (N-ETH-COV)
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.95,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.998,
        "mean_time_to_cessation_s": 1.2,
        "test_coverage": 0.85,                   # VIOLATION: < 0.90 (N-ROB-TEST)
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.90,        # VIOLATION: < 0.95 (N-TRANS-AI-ID)
        "identity_queries_received": 850,
        "identity_correctly_disclosed": 765,
        "mean_time_to_cessation_s": 1.5,
        "human_oversight_rate": 0.93,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.89,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.82,                 # VIOLATION: < 0.90 (N-CTRL-SLO)
        "unreviewed_kae_count": 3,
        "total_kae_count": 32,
    },
    "IncidentReport": {
        "confidence": 0.92,
        "lifecycle_stage": "operation",
        "incidents_total": 7,
        "norm_violated": "N-TRANS-AI-ID",
    },
}

INCIDENT_GAP = {
    "ModelCard": {
        "confidence": 0.93,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.85,
        "data_diversity_entropy": 0.82,
        "ethical_assessment_coverage": 0.92,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.95,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.998,
        "mean_time_to_cessation_s": 1.2,
        "test_coverage": 0.96,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.97,
        "identity_queries_received": 850,
        "identity_correctly_disclosed": 824,
        "mean_time_to_cessation_s": 1.5,
        "human_oversight_rate": 0.93,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.89,
        "lifecycle_stage": "operation",
        # GAP 1: kae_review_rate field absent (None) in present artifact.
        # This is the defect trigger from v1.0: the original engine
        # substituted 0, misclassifying as VIOLATED.  The v1.1 engine
        # correctly returns EVIDENCE_GAP.
        "kae_review_rate": None,
        "unreviewed_kae_count": 0,
        "total_kae_count": 32,
    },
    "IncidentReport": {
        "confidence": 0.75,                      # GAP 2: confidence < 0.80 floor
        "lifecycle_stage": "operation",
        "incidents_total": 7,
        "norm_violated": None,
    },
}


# ====================================================================
# DOMAIN 3: Critical-Infrastructure Decision Support
# ====================================================================

INFRA_CLEAN = {
    "ModelCard": {
        "confidence": 0.96,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.90,
        "data_diversity_entropy": 0.88,
        "ethical_assessment_coverage": 0.95,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.94,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.999,
        "mean_time_to_cessation_s": 0.8,
        "test_coverage": 0.97,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.93,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.99,
        "identity_queries_received": 2100,
        "identity_correctly_disclosed": 2079,
        "mean_time_to_cessation_s": 0.9,
        "human_oversight_rate": 0.95,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.98,
        "unreviewed_kae_count": 0,
        "total_kae_count": 61,
    },
    "IncidentReport": {
        "confidence": 0.94,
        "lifecycle_stage": "operation",
        "incidents_total": 1,
        "norm_violated": None,
    },
}

INFRA_VIOLATED = {
    "ModelCard": {
        "confidence": 0.96,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.75,         # VIOLATION: < 0.80 (N-TRANS-EXP)
        "data_diversity_entropy": 0.88,
        "ethical_assessment_coverage": 0.95,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    "RedTeamingReport": {
        "confidence": 0.94,
        "lifecycle_stage": "evaluation",
        "cessation_compliance_rate": 0.97,       # VIOLATION: < 0.99 (N-CTRL-CEASE)
        "mean_time_to_cessation_s": 6.5,         # VIOLATION: > 5.0s (N-CTRL-CEASE)
        "test_coverage": 0.97,
    },
    "RuntimeTelemetryLog": {
        "confidence": 0.93,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.99,
        "identity_queries_received": 2100,
        "identity_correctly_disclosed": 2079,
        "mean_time_to_cessation_s": 0.9,
        "human_oversight_rate": 0.95,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.83,                 # VIOLATION: < 0.90 (N-CTRL-SLO)
        "unreviewed_kae_count": 4,               # VIOLATION: > 0 (N-CTRL-SLO)
        "total_kae_count": 61,
    },
    "IncidentReport": {
        "confidence": 0.94,
        "lifecycle_stage": "operation",
        "incidents_total": 1,
        "norm_violated": "N-CTRL-SLO",
    },
}

INFRA_GAP = {
    "ModelCard": {
        "confidence": 0.96,
        "lifecycle_stage": "deployment",
        "explainability_coverage": 0.90,
        "data_diversity_entropy": 0.88,
        "ethical_assessment_coverage": 0.95,
        "ai_identity_disclosure_mechanism": True,
        "cessation_mechanism_documented": True,
    },
    # GAP 1: RedTeamingReport entirely absent -> N-CTRL-CEASE, N-ROB-TEST
    "RuntimeTelemetryLog": {
        "confidence": 0.93,
        "lifecycle_stage": "operation",
        "identity_disclosure_rate": 0.99,
        "identity_queries_received": 2100,
        "identity_correctly_disclosed": 2079,
        "mean_time_to_cessation_s": 0.9,
        "human_oversight_rate": 0.95,
    },
    "SelfLearningAuditRecord": {
        "confidence": 0.91,
        "lifecycle_stage": "operation",
        "kae_review_rate": 0.98,
        "unreviewed_kae_count": 0,
        "total_kae_count": 61,
    },
    "IncidentReport": {
        "confidence": 0.68,                      # GAP 2: confidence < 0.80 floor
        "lifecycle_stage": "operation",
        "incidents_total": 1,
        "norm_violated": None,
    },
}


# ====================================================================
# Registry
# ====================================================================

ALL_BUNDLES = {
    "Legal Assistant": {
        "clean": LEGAL_CLEAN,
        "violated": LEGAL_VIOLATED,
        "gap": LEGAL_GAP,
    },
    "Incident-Response Agent": {
        "clean": INCIDENT_CLEAN,
        "violated": INCIDENT_VIOLATED,
        "gap": INCIDENT_GAP,
    },
    "Critical Infrastructure": {
        "clean": INFRA_CLEAN,
        "violated": INFRA_VIOLATED,
        "gap": INFRA_GAP,
    },
}
