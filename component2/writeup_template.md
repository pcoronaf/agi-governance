# Component 2 — write-up template (fill from analyze.py output)

> We validated the reference engine against auditor-confirmed ground truth on
> {N_PACKAGES} real evidence packages spanning {N_TYPES} of the five artifact types.
> {R_LABELERS} governance auditors, blind to the engine output and to one another,
> independently labeled each of the {N_CELLS} (package × norm) cells. Inter-labeler
> agreement was {INTER_KAPPA} ({KAPPA_METHOD}), indicating {AGREEMENT_STRENGTH}
> ground truth. Against the labeler consensus, the engine agreed on {ENGINE_AGREEMENT}
> of cells; the {N_DISAGREEMENTS} disagreements were {DISAGREEMENT_SUMMARY} and are
> classified in Table X. {GAP_RATE} of consensus cells were EVIDENCE_GAP, consistent
> with the bridgeability analysis: real packages frequently lack the structured
> indicators the AGI-specific norms require. These results establish {CLAIM}, subject
> to the limitations of a small sample ({N_PACKAGES} packages, {R_LABELERS} labelers).

Fields to fill: N_PACKAGES, N_TYPES, R_LABELERS, N_CELLS, INTER_KAPPA, KAPPA_METHOD,
AGREEMENT_STRENGTH (e.g., "substantial"), ENGINE_AGREEMENT (%), N_DISAGREEMENTS,
DISAGREEMENT_SUMMARY, GAP_RATE (%), CLAIM (state only what the numbers support).
