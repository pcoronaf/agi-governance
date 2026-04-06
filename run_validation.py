"""
Synthetic validation runner (Section 8.3).

Executes the compliance engine against all nine evidence bundles and
verifies correctness against known ground truth.

Usage:
    python run_validation.py

Repository: https://github.com/pcoronaf/agi-governance
"""

import json
import sys
from compliance_engine import run_compliance_check, report_to_dict, Verdict
from evidence_bundles import ALL_BUNDLES


# ─────────────────────────────────────────────────────────────────────
# Ground truth: expected violated norms per domain
# ─────────────────────────────────────────────────────────────────────

EXPECTED_VIOLATIONS = {
    "Legal Assistant": {
        "N-TRANS-EXP", "N-FAIR-DATA", "N-ETH-COV",
        "N-CTRL-CEASE", "N-ACC-HUMAN",
    },
    "Incident-Response Agent": {
        "N-FAIR-DATA", "N-ETH-COV", "N-ROB-TEST",
        "N-TRANS-AI-ID", "N-CTRL-SLO",
    },
    "Critical Infrastructure": {
        "N-TRANS-EXP", "N-CTRL-CEASE", "N-CTRL-SLO",
    },
}


def run_validation():
    """Run all nine bundles, verify against ground truth, print report."""
    print("=" * 72)
    print("  AGI GOVERNANCE COMPLIANCE — SYNTHETIC VALIDATION (v1.1)")
    print("=" * 72)

    all_reports = []
    for domain, bundles in ALL_BUNDLES.items():
        for btype, bundle in bundles.items():
            r = run_compliance_check(
                system_id=f"{domain}|{btype}",
                case_study=domain,
                bundle_type=btype,
                evidence_bundle=bundle,
            )
            all_reports.append(r)

    passed = True

    # ── 1. Clean bundles ──────────────────────────────────────────────
    print("\n[1] CLEAN BUNDLES — correctness baseline")
    for r in (r for r in all_reports if r.bundle_type == "clean"):
        non_compliant = [
            nv for nv in r.norms if nv.verdict != Verdict.COMPLIANT
        ]
        ok = len(non_compliant) == 0
        if not ok:
            passed = False
        print(
            f"  {r.case_study:35s} "
            f"{'PASS' if ok else 'FAIL'} "
            f"({8 - len(non_compliant)}/8 COMPLIANT)"
        )

    # ── 2. Violated bundles ───────────────────────────────────────────
    print("\n[2] VIOLATED BUNDLES — violation detection")
    total_tp = total_fp = total_fn = total_ind = 0

    for r in (r for r in all_reports if r.bundle_type == "violated"):
        expected = EXPECTED_VIOLATIONS[r.case_study]
        detected = {
            nv.norm_id for nv in r.norms
            if nv.verdict == Verdict.VIOLATED
        }
        tp = len(expected & detected)
        fp = len(detected - expected)
        fn = len(expected - detected)
        ind = sum(
            1 for nv in r.norms for ir in nv.indicators
            if not ir.satisfied and not ir.evidence_gap
        )
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_ind += ind

        if fp or fn:
            passed = False
        print(
            f"  {r.case_study:35s} "
            f"norms TP={tp} FP={fp} FN={fn}  "
            f"indicator-violations={ind}"
        )

    p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0
    rc = total_tp / (total_tp + total_fn) if (total_tp + total_fn) else 0
    f1 = 2 * p * rc / (p + rc) if (p + rc) else 0
    print(
        f"\n  AGGREGATE: TP={total_tp} FP={total_fp} FN={total_fn}  "
        f"P={p:.3f} R={rc:.3f} F1={f1:.3f}"
    )
    print(f"  Indicator-level violations: {total_ind}")

    # ── 3. Gap bundles ────────────────────────────────────────────────
    print("\n[3] GAP BUNDLES — evidence-gap detection")
    injection_detected = 0
    injection_total = 6

    for r in (r for r in all_reports if r.bundle_type == "gap"):
        gap_norms = [
            (nv.norm_id, nv.explanation)
            for nv in r.norms if nv.verdict == Verdict.EVIDENCE_GAP
        ]
        viol_norms = [
            nv.norm_id for nv in r.norms if nv.verdict == Verdict.VIOLATED
        ]
        print(f"  {r.case_study}:")
        print(f"    EVIDENCE_GAP ({len(gap_norms)}): "
              f"{[g[0] for g in gap_norms]}")
        if viol_norms:
            print(f"    VIOLATED     ({len(viol_norms)}): {viol_norms}")
            passed = False

        # Injection-level verification
        if r.case_study == "Legal Assistant":
            if any("SelfLearningAuditRecord" in e for _, e in gap_norms):
                injection_detected += 1
            if any("IncidentReport" in e for _, e in gap_norms):
                injection_detected += 1
        elif r.case_study == "Incident-Response Agent":
            slo = next(
                (nv for nv in r.norms if nv.norm_id == "N-CTRL-SLO"), None
            )
            if slo and slo.verdict == Verdict.EVIDENCE_GAP:
                injection_detected += 1
            else:
                passed = False
            if any("IncidentReport" in e for _, e in gap_norms):
                injection_detected += 1
        elif r.case_study == "Critical Infrastructure":
            if any("RedTeamingReport" in e for _, e in gap_norms):
                injection_detected += 1
            if any("IncidentReport" in e for _, e in gap_norms):
                injection_detected += 1

    total_gap_verdicts = sum(
        1 for r in all_reports if r.bundle_type == "gap"
        for nv in r.norms if nv.verdict == Verdict.EVIDENCE_GAP
    )
    gap_recall = injection_detected / injection_total
    print(
        f"\n  Injection-level: {injection_detected}/{injection_total}  "
        f"Recall={gap_recall:.3f}"
    )
    print(
        f"  Total EVIDENCE_GAP verdicts: {total_gap_verdicts}  "
        f"(propagated: {total_gap_verdicts - injection_detected})"
    )
    if injection_detected < injection_total:
        passed = False

    # ── 4. Timing ─────────────────────────────────────────────────────
    times = [r.generation_time_ms for r in all_reports]
    print(
        f"\n[4] TIMING: mean={sum(times)/len(times):.4f} ms  "
        f"range={min(times):.4f}-{max(times):.4f} ms"
    )

    # ── 5. Explanation completeness ───────────────────────────────────
    nc = [
        nv for r in all_reports for nv in r.norms
        if nv.verdict != Verdict.COMPLIANT
    ]
    has_rem = sum(1 for nv in nc if nv.remediation)
    completeness = has_rem / len(nc) if nc else 1.0
    print(
        f"\n[5] EXPLANATION COMPLETENESS: "
        f"{has_rem}/{len(nc)} = {completeness:.3f}"
    )
    if completeness < 1.0:
        passed = False

    # ── Summary ───────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    if passed:
        print("  RESULT: ALL CHECKS PASSED")
    else:
        print("  RESULT: SOME CHECKS FAILED")
    print("=" * 72)

    # ── Export full reports as JSON ────────────────────────────────────
    output = [report_to_dict(r) for r in all_reports]
    with open("validation_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull reports written to validation_results.json")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(run_validation())
