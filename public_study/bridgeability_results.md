# Real-evidence bridgeability study — prior vs current model generations

**What this is.** A coverage analysis over *two generations* of real published
model/system cards: which norm inputs can be sourced from real public governance
evidence, and whether coverage improved from 2024 to 2025-26.

**What this is NOT.** Not auditor-confirmed compliance. Verdicts reflect only what is
*computable* from the documents. Auditor-confirmed accuracy is the separate Component 2
study (`../component2/`).

## Sources (real documents)

| Gen | Developer | Document | URL |
|-----|-----------|----------|-----|
| 2024 | OpenAI | GPT-4o System Card | https://cdn.openai.com/gpt-4o-system-card.pdf |
| 2024 | Anthropic | Claude 3.5 Sonnet Model Card Addendum | https://www-cdn.anthropic.com/fed9cc193a14b84131812372d8d5857f8f304c52/Model_Card_Claude_3_Addendum.pdf |
| 2024 | Meta | Llama 3.1 Model Card | https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md |
| 2026 | OpenAI | GPT-5.5 System Card (Apr 2026) | https://openai.com/index/gpt-5-5-system-card/ |
| 2026 | Anthropic | Claude Opus 4.6 System Card (Feb 2026) | https://www.anthropic.com/claude-opus-4-6-system-card |
| 2025 | Google | Gemini 3 Model Card & Frontier Safety Report (Nov 2025) | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf |

The current cards test far more of the AGI-relevant surface: OpenAI's Preparedness
Framework (autonomy, deception, `not_unsafe` safety metric), Anthropic's ASL-3 RSP
evaluations plus dedicated sabotage, situational-awareness and shutdown-resistance
testing (with UK AISI and Apollo external review), and Google's Frontier Safety
Framework with external sabotage/stealth evaluations. But these are reported as
capability *levels* (ASL, preparedness High/Medium), propensity findings, and bespoke
metrics (`not_unsafe`, `pass@12`), not as the structured rates the norms require.

## Mapping discipline (identical across generations)
Conservative (strict): a field/type is present only when the document reports a
quantitative metric matching the indicator's definition. Generous: adds documented,
flagged proxies from related metrics (reported adversarial-evaluation suite scope →
`test_coverage`). Operational artifacts (RuntimeTelemetryLog, SelfLearningAuditRecord,
IncidentReport) are absent in both generations — pre-deployment cards are not runtime
telemetry, self-learning audits, or incident logs. Proxy numeric values are
illustrative; the finding is *which category of norm* becomes evaluable.

**Coders.** The mapping was performed independently by three coders under the written
protocol in `coding_protocol.md`: the author team and two external ISO/IEC 42001
auditors blinded to each other's cell-level judgments. Strict pass: unanimous (60/60).
Generous pass: Fleiss' κ = 0.709, pairwise Cohen's κ 0.640–0.783, PABAK ≥ 0.900, 56/60
cells unanimous. The four disagreements — all about proxy admissibility — were resolved
by majority vote with author review of each rationale (`reconciliation_log.md`); the
figures below are the resulting
mapping, which `run_public_study.py` reproduces. An earlier single-coder mapping
admitted a risk-category-coverage proxy for `ethical_assessment_coverage` (yielding
3→6 of 30); both external coders rejected it independently and it is not part of the
consensus.

## Results (engine v1.4, consensus mapping)

| Coverage (summed over the 3 cards in each generation) | 2024 cons | 2024 gen. | 2026 cons | 2026 gen. |
|---|---|---|---|---|
| Artifact **types** (of 15) | 3 | 5 | 3 | **6** |
| Indicator cells (of 30) | 0 | 2 | 0 | **3** |
| **AGI-specific** indicator cells (of 15) | **0** | **0** | **0** | **0** |
| Norms evaluable, non-`EVIDENCE_GAP` (of 24) | 0 | 2 | 0 | **3** |

**Delta (current − prior), generous mapping:** artifact-types +1, indicators +1,
norms evaluable +1, **AGI-specific indicators +0**.

## Findings

1. **Coverage is improving, modestly, and only for one generic norm.** Under generous
   proxying, computable indicators rose from 2 to 3 of 30 and evaluable norms from 2 to
   3 of 24 between 2024 and 2025-26. Every computable cell is `IND-ROB-TEST`: the cards
   report a documented adversarial-evaluation suite with quantitative scope for two of
   three 2024 developers and all three 2025-26 developers. No other indicator is
   computable from any card under either pass.
2. **The AGI-specific controls show zero movement: 0/15 in both generations, under
   every mapping, unanimously across the three coders.** The current cards *test*
   cessation-relevant behaviour (shutdown-resistance), self-modification/autonomy, and
   situational awareness extensively — but report them as ASL levels,
   "does-not-cross-threshold" rule-outs, and propensity findings, never as a
   cessation-compliance rate, a knowledge-acquisition-event review rate, or an
   identity-disclosure rate. Topic coverage improved; *structured, machine-checkable*
   coverage did not. The single dissenting judgment on an AGI-specific cell (a
   confirmation-adherence proxy for cessation on one card) was outvoted (2 of 3); on review the authors
   agreed with the majority, because the proxy measures a different behaviour from
   stop-command compliance.
3. **Strict coverage is unchanged at 0/30 across both generations.** Absent a
   deliberate schema, even the most detailed 2025-26 documentation yields no directly
   computable indicator.
4. **Independent corroboration.** An audit of 100 model cards found technical
   categories exceed 90% presence while safety-critical categories fall below 50%
   (AI Transparency Atlas, arXiv:2512.12443) — consistent with the structured-metric
   gap measured here.

The gap is *not closing on its own*. Even frontier documentation that now rigorously
evaluates the exact AGI risks the norms target does not yet report them in
machine-checkable form — which is precisely what the schema specifies. The model tells
evidence producers what to emit; current practice, though improving on one generic
axis, still emits none of it for the AGI-specific controls.

## Limitations
- Interpretive mapping: three coders with substantial (not perfect) agreement on the
  generous pass; the rationale for each split cell and its majority resolution is public.
- Proxy values are illustrative; findings are robust to them (they determine only
  whether a generic norm becomes evaluable, not the AGI-specific result, which is 0
  regardless).
- Model/system cards are developer self-disclosure, not confidential ISO/IEC 42001
  audit evidence packages; the gap could be smaller inside a real audit.
- Verdicts measure computability, not compliance.

## Reproducing
```bash
python public_study/run_public_study.py        # consensus mapping -> public_study_results.json
python public_study/compute_reliability.py     # inter-coder statistics from coder_agreement_matrix.csv
```
