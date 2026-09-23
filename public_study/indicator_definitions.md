# Indicator definitions — the ten engine-implemented indicators

> **Threshold status.** All thresholds listed here are prototype-level reference values
> (class (a), paper §5.3): expert-derived, not standards-fixed, not empirically
> calibrated. They are the values in `THRESHOLDS` in `checker/compliance_engine.py`.
> Coders judged *computability* of each indicator from a document, never whether the
> threshold is met.
>
> **Version note.** This is the completed version of the definitions. The version
> issued to coders C2 and C3 (July 2026) marked five items "TO CONFIRM": the cessation
> latency threshold, the unreviewed-KAE threshold, and the explainability, human-review
> and robustness-coverage definitions and thresholds. Those items were completed
> afterwards from `THRESHOLDS` and `INDICATOR_FIELD_MAP` in the engine. Because the
> coding task asked only whether an indicator's value could be computed from a document
> — not whether its threshold was met — the missing threshold values did not bear on
> any judgment; the metric definitions that coders did rely on were unchanged.

The threshold is listed for context only. **You are not judging whether the system
passes the threshold** — only whether the document reports the information from which
the indicator's value could be computed.

## AGI-specific indicators (5)

**IND-TRANS-AI-ID — AI identity disclosure rate** (norm N-TRANS-AI-ID)
Percentage of identity-query interactions in which the system correctly and
unconditionally self-identifies as an AI agent. Threshold ≥ 0.95.
*Computable requires:* a reported disclosure rate (or counts: identity queries received
and correctly disclosed).

**IND-CTRL-CEASE-RATE — Cessation compliance rate** (norm N-CTRL-CEASE)
Stop-command compliance rate under normal and adversarial conditions (%).
Threshold ≥ 0.99.
*Computable requires:* a reported compliance rate over cessation/stop-command trials.

**IND-CTRL-CEASE-LATENCY — Mean time to cessation** (norm N-CTRL-CEASE)
Mean time to full cessation upon an authorized stop command (seconds).
Threshold ≤ 5.0 s (upper bound).
*Computable requires:* a reported latency figure for cessation.

**IND-CTRL-SLO-RATE — Self-learning oversight review rate** (norm N-CTRL-SLO)
Percentage of knowledge acquisition events (KAEs — autonomous learning, goal
modification, or capability emergence beyond the last governed checkpoint) reviewed and
approved by a designated human governor. Threshold ≥ 0.90.
*Computable requires:* reported KAE counts/review rates.

**IND-CTRL-SLO-VIOLATIONS — Unreviewed KAE count** (norm N-CTRL-SLO)
Count of KAEs integrated operationally without prior governor approval (outside the
emergency-protocol exception). Threshold ≤ 0 (no unreviewed KAEs).
*Computable requires:* a reported count (zero counts as a report only if stated).

## Generic governance indicators (5)

**IND-TRANS-EXP — Explainability coverage** (norm N-TRANS-EXP)
Share of predictions/decisions accompanied by an interpretable explanation, read from
`ModelCard.explainability_coverage`. Threshold ≥ 0.80.
*Computable requires:* a reported explanation-coverage fraction.

**IND-ACC-HUMAN — Human review share** (norm N-ACC-HUMAN)
Share of system decisions reviewed by humans, read from
`RuntimeTelemetryLog.human_oversight_rate`. Threshold ≥ 0.85.
*Computable requires:* a reported human-review rate over decisions.

**IND-FAIR-DATA — Training-data diversity entropy** (norm N-FAIR-DATA)
Normalized Shannon entropy across documented demographic, geographic, and socioeconomic
strata of the training data, computed from data-provenance records. Threshold ≥ 0.80.
*Computable requires:* reported strata proportions or the entropy value itself.

**IND-ROB-TEST — Robustness test coverage** (norm N-ROB-TEST)
Test coverage: share of defined scenarios/cases exercised in testing, read from
`RedTeamingReport.test_coverage`. Threshold ≥ 0.90.
*Note:* benchmark scores alone are not coverage; on the generous pass a documented
adversarial-evaluation suite with reported scope may qualify as a proxy — justify in
the proxy column.

**IND-ETH-COV — Ethical assessment coverage** (norm N-ETH-COV)
Percentage of system modules with a documented formal ethical assessment.
Threshold ≥ 0.90.
