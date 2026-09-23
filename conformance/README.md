# Blind conformance evaluation (paper §8.4)

Independent, blind test of the reference engine. Three LLMs each generated 18
evidence bundles spanning a fixed perturbation taxonomy and predicted the verdict
for all eight norms, without access to the engine or to one another. The engine
was then run on all 54 bundles and compared to those predictions.

## Contents
| Path | Description |
|------|-------------|
| `conformance_prompt.md` | The exact generation prompt given to each model |
| `model_outputs/` | The three raw model outputs (18 cases each) |
| `run_conformance.py` | Harness: runs the engine, computes agreement, scores vs the resolved spec |
| `conformance_results.json` | Committed results (inter-model agreement, per-cell engine outputs, divergences) |

## Reproduce
```bash
python conformance/run_conformance.py
```

## Result summary
- **Inter-model agreement (controlled cases TC-01..TC-15, 120 cells): 120/120 unanimous (raw agreement).** Fleiss' κ is not reported: with unanimous agreement the chance correction is uninformative.
- **Engine vs resolved specification: 428/432 cells.**
- Two implementation defects surfaced and fixed in engine **v1.2** (TC-10 confidence-floor bypass; TC-11 malformed-type crash + fault isolation).
- Two vocabulary fields shown inert and then enforced in engine **v1.3** (TC-13 lifecycle-stage scoping; TC-14 provenance presence).

## Notes on scoring
- **Resolved specification.** For three under-specified cases the models' recorded primary verdict was resolved to the safe reading they unanimously recommended: TC-12 (out-of-range → `EVIDENCE_GAP`, v1.2), TC-13 (stale lifecycle → `EVIDENCE_GAP`, v1.3), TC-14 (missing provenance → `EVIDENCE_GAP`, v1.3).
- **The 4 red cells** are all `gemini-3.5-flash`, `TC-15`: that bundle incidentally omits `provenance` on one artifact, which the v1.3 provenance rule correctly flags as `EVIDENCE_GAP` although the model predicted `COMPLIANT`. This is an inconsistency in the generated bundle that the enforcement caught, not an engine error.
## Models used

| File | Model (confirmed from the provider's usage history) | Self-reported `model_self_id` |
|------|------|------|
| `gpt-5.5.json` | GPT-5.5 (OpenAI) | GPT-5.5 Thinking |
| `claude-sonnet-5.json` | Claude Sonnet 5 (Anthropic) | Claude Sonnet 5 (claude-sonnet-5) |
| `gemini-3.5-flash.json` | Gemini 3.5 Flash (Google) | **Gemini 1.5 Pro (2026-07-01)** — incorrect |

The Gemini run **self-identified as "Gemini 1.5 Pro"**, a model Google retired in 2025;
the provider's usage history shows the model actually used was **Gemini 3.5 Flash**.
Language models do not reliably know their own identity, so model self-reports are not
evidence of which model produced an output. The raw outputs are published unedited —
including that incorrect self-report — and the file was renamed from
`gemini-1.5-pro.json` to reflect the confirmed model. The GPT-5.5 output also contains a
`:contentReference[oaicite:…]` string, an artifact of copying from the ChatGPT interface;
it is left as generated.
