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
| `conformance_results.json` | Committed results (inter-model κ, per-cell engine outputs, divergences) |

## Reproduce
```bash
python conformance/run_conformance.py
```

## Result summary
- **Inter-model agreement (controlled cases TC-01..TC-15, 120 cells): 120/120 unanimous, Fleiss' κ = 1.00.**
- **Engine vs resolved specification: 428/432 cells.**
- Two implementation defects surfaced and fixed in engine **v1.2** (TC-10 confidence-floor bypass; TC-11 malformed-type crash + fault isolation).
- Two vocabulary fields shown inert and then enforced in engine **v1.3** (TC-13 lifecycle-stage scoping; TC-14 provenance presence).

## Notes on scoring
- **Resolved specification.** For three under-specified cases the models' recorded primary verdict was resolved to the safe reading they unanimously recommended: TC-12 (out-of-range → `EVIDENCE_GAP`, v1.2), TC-13 (stale lifecycle → `EVIDENCE_GAP`, v1.3), TC-14 (missing provenance → `EVIDENCE_GAP`, v1.3).
- **The 4 red cells** are all `gemini-1.5-pro`, `TC-15`: that bundle incidentally omits `provenance` on one artifact, which the v1.3 provenance rule correctly flags as `EVIDENCE_GAP` although the model predicted `COMPLIANT`. This is an inconsistency in the generated bundle that the enforcement caught, not an engine error.
- **Model identifiers** are the models' self-reports; confirm against the actual versions used before publication.
