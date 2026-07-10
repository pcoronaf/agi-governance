# Component 2 — auditor-confirmed empirical validation (turnkey kit)



1. Select real evidence packages and two+ blind labelers (`protocol.md`).
2. Mapper builds agiev bundles; operator runs `../checker/compliance_engine.py` and
   records verdicts into `engine_outputs.json` (see `engine_outputs_template.json`).
3. Each labeler fills a copy of `labeling_sheet_template.csv` using `rubric.md`.
4. Combine labels into one CSV and run:
   ```bash
   python component2/analyze.py --labels labels.csv --engine engine_outputs.json
   ```
5. Fill `writeup_template.md` from the printed metrics.

`analyze.py` computes Cohen's κ (2 labelers) or Fleiss' κ (≥3), engine-vs-consensus
agreement, and a classified disagreement table.
