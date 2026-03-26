"""
Evaluation harness for the AGI Governance Compliance Engine.

Metrics reported (per case study and aggregated):
  - Violation detection: precision, recall, F1, specificity
  - Evidence-gap detection: precision, recall, F1
  - Explanation quality: completeness score (0/1 per verdict)
  - Operational effort: time to generate compliance report vs.
    estimated manual audit baseline
  - Compliance rate on clean bundles (should be 1.0)

Manual audit baseline: estimated at 480 minutes (8 person-hours)
for a comprehensive compliance review, based on audit cost literature
(Stahl et al., 2023; ISO/IEC 42001 implementation guides).
"""

from __future__ import annotations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from checker.compliance_engine import check_compliance, ComplianceReport
from evidence.bundles import LegalAssistantBundles, IncidentResponseBundles, CriticalInfraBundles

MANUAL_AUDIT_MINUTES = 480   # 8-hour expert audit baseline


# ─────────────────────────────────────────────────────────────
# EVALUATION PRIMITIVES
# ─────────────────────────────────────────────────────────────

def precision_recall_f1(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    recall    = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    f1 = (2 * precision * recall / (precision + recall)
          if (precision + float("nan") != float("nan") and precision + recall > 0)
          else float("nan"))
    # Simpler:
    if (tp + fp) > 0:
        precision = tp / (tp + fp)
    else:
        precision = 0.0
    if (tp + fn) > 0:
        recall = tp / (tp + fn)
    else:
        recall = 0.0
    if (precision + recall) > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0
    return precision, recall, f1


def specificity(tn, fp):
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0


def explanation_completeness(report: ComplianceReport) -> float:
    """Score 1 if every non-compliant verdict has a non-None remediation, else 0."""
    non_compliant = [v for v in report.verdicts if v.status != "COMPLIANT"]
    if not non_compliant:
        return 1.0
    return sum(1 for v in non_compliant if v.remediation) / len(non_compliant)


# ─────────────────────────────────────────────────────────────
# PER-CASE-STUDY EVALUATOR
# ─────────────────────────────────────────────────────────────

ALL_NORM_IDS = [
    "N-TRANS-AI-ID", "N-TRANS-EXP", "N-CTRL-CEASE", "N-CTRL-SLO",
    "N-ACC-HUMAN",   "N-FAIR-DATA", "N-ROB-TEST",    "N-ETH-COV",
]

def evaluate_case_study(factory_cls) -> dict:
    name = factory_cls.SYSTEM_NAME
    print(f"\n{'='*70}")
    print(f"  CASE STUDY: {name}")
    print(f"{'='*70}")

    # ── 1. Clean bundle: all norms must be COMPLIANT ──────────────────
    clean = factory_cls.clean_bundle()
    clean_report = check_compliance(clean)
    print(f"\n[1] Clean bundle — expected: all COMPLIANT")
    for v in clean_report.verdicts:
        mark = "✓" if v.status == "COMPLIANT" else "✗"
        print(f"    {mark} {v.norm_id:20s} → {v.status}")
    assert clean_report.summary["norms_violated"] == 0, \
        f"Clean bundle has unexpected violations: {clean_report.summary}"
    print(f"    → Overall: {clean_report.overall_status}  "
          f"(generated in {clean_report.generation_time_s*1000:.1f} ms)")

    # ── 2. Violated bundle: precision/recall on injected violations ────
    violated = factory_cls.violated_bundle()
    viol_report = check_compliance(violated)
    gt_violated = set(factory_cls.INJECTED_VIOLATIONS)
    detected_violated = {v.norm_id for v in viol_report.verdicts if v.status == "VIOLATED"}
    detected_gap      = {v.norm_id for v in viol_report.verdicts if v.status == "EVIDENCE_GAP"}
    detected_compliant= {v.norm_id for v in viol_report.verdicts if v.status == "COMPLIANT"}

    tp_v = len(gt_violated & detected_violated)
    fp_v = len(detected_violated - gt_violated)
    fn_v = len(gt_violated - detected_violated)
    tn_v = len(set(ALL_NORM_IDS) - gt_violated - detected_violated)
    prec_v, rec_v, f1_v = precision_recall_f1(tp_v, fp_v, fn_v)
    spec_v = specificity(tn_v, fp_v)

    print(f"\n[2] Violated bundle — {len(gt_violated)} injected violations")
    print(f"    Ground truth violated : {sorted(gt_violated)}")
    print(f"    Detected as VIOLATED  : {sorted(detected_violated)}")
    missed = sorted(gt_violated - detected_violated)
    false_alarms = sorted(detected_violated - gt_violated)
    if missed:       print(f"    ⚠ Missed violations   : {missed}")
    if false_alarms: print(f"    ⚠ False alarms        : {false_alarms}")
    print(f"    Precision={prec_v:.3f}  Recall={rec_v:.3f}  F1={f1_v:.3f}  Specificity={spec_v:.3f}")

    # ── 3. Gap bundle: precision/recall on evidence gaps ──────────────
    gap_bundle = factory_cls.gap_bundle()
    gap_report = check_compliance(gap_bundle)
    gt_gaps = set(factory_cls.INJECTED_GAPS)
    detected_gaps = {v.norm_id for v in gap_report.verdicts if v.status == "EVIDENCE_GAP"}

    tp_g = len(gt_gaps & detected_gaps)
    fp_g = len(detected_gaps - gt_gaps)
    fn_g = len(gt_gaps - detected_gaps)
    prec_g, rec_g, f1_g = precision_recall_f1(tp_g, fp_g, fn_g)

    print(f"\n[3] Gap bundle — {len(gt_gaps)} injected evidence gaps")
    print(f"    Ground truth gaps     : {sorted(gt_gaps)}")
    print(f"    Detected as GAPS      : {sorted(detected_gaps)}")
    print(f"    Precision={prec_g:.3f}  Recall={rec_g:.3f}  F1={f1_g:.3f}")

    # ── 4. Explanation completeness ────────────────────────────────────
    exp_score_v = explanation_completeness(viol_report)
    exp_score_g = explanation_completeness(gap_report)
    print(f"\n[4] Explanation completeness")
    print(f"    Violated bundle : {exp_score_v:.2f}  (1.0 = all violations have remediation text)")
    print(f"    Gap bundle      : {exp_score_g:.2f}")

    # ── 5. Operational effort ──────────────────────────────────────────
    tool_time_ms = viol_report.generation_time_s * 1000
    speedup = (MANUAL_AUDIT_MINUTES * 60 * 1000) / tool_time_ms
    print(f"\n[5] Operational effort")
    print(f"    Tool report generation : {tool_time_ms:.1f} ms")
    print(f"    Manual audit baseline  : {MANUAL_AUDIT_MINUTES} min ({MANUAL_AUDIT_MINUTES*60*1000:.0f} ms)")
    print(f"    Speedup factor         : {speedup:.0f}×")

    return {
        "case_study": factory_cls.CASE_TYPE,
        "system_name": name,
        "clean_norms_compliant": clean_report.summary["norms_compliant"],
        "clean_norms_total": clean_report.summary["norms_total"],
        "violation_detection": {
            "injected": len(gt_violated),
            "detected": len(detected_violated),
            "TP": tp_v, "FP": fp_v, "FN": fn_v, "TN": tn_v,
            "precision": round(prec_v, 4),
            "recall": round(rec_v, 4),
            "f1": round(f1_v, 4),
            "specificity": round(spec_v, 4),
        },
        "gap_detection": {
            "injected": len(gt_gaps),
            "detected": len(detected_gaps),
            "TP": tp_g, "FP": fp_g, "FN": fn_g,
            "precision": round(prec_g, 4),
            "recall": round(rec_g, 4),
            "f1": round(f1_g, 4),
        },
        "explanation_completeness_violated": round(exp_score_v, 4),
        "explanation_completeness_gap": round(exp_score_g, 4),
        "tool_report_generation_ms": round(tool_time_ms, 2),
        "manual_audit_baseline_ms": MANUAL_AUDIT_MINUTES * 60 * 1000,
        "speedup_factor": round(speedup, 0),
        "violated_report": viol_report.to_dict(),
    }


# ─────────────────────────────────────────────────────────────
# AGGREGATE METRICS
# ─────────────────────────────────────────────────────────────

def aggregate(results: list[dict]) -> dict:
    def mean(key, subkey=None):
        vals = [r[key][subkey] if subkey else r[key] for r in results]
        return round(sum(vals) / len(vals), 4)

    return {
        "n_case_studies": len(results),
        "violation_detection": {
            "mean_precision": mean("violation_detection", "precision"),
            "mean_recall":    mean("violation_detection", "recall"),
            "mean_f1":        mean("violation_detection", "f1"),
            "mean_specificity": mean("violation_detection", "specificity"),
            "total_TP": sum(r["violation_detection"]["TP"] for r in results),
            "total_FP": sum(r["violation_detection"]["FP"] for r in results),
            "total_FN": sum(r["violation_detection"]["FN"] for r in results),
        },
        "gap_detection": {
            "mean_precision": mean("gap_detection", "precision"),
            "mean_recall":    mean("gap_detection", "recall"),
            "mean_f1":        mean("gap_detection", "f1"),
            "total_TP": sum(r["gap_detection"]["TP"] for r in results),
            "total_FP": sum(r["gap_detection"]["FP"] for r in results),
            "total_FN": sum(r["gap_detection"]["FN"] for r in results),
        },
        "mean_explanation_completeness": mean("explanation_completeness_violated"),
        "mean_tool_report_ms": mean("tool_report_generation_ms"),
        "mean_speedup_factor": round(
            sum(r["speedup_factor"] for r in results) / len(results), 0
        ),
    }


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    results = []
    for factory in [LegalAssistantBundles, IncidentResponseBundles, CriticalInfraBundles]:
        results.append(evaluate_case_study(factory))

    agg = aggregate(results)

    print(f"\n{'='*70}")
    print("  AGGREGATE RESULTS ACROSS ALL THREE CASE STUDIES")
    print(f"{'='*70}")
    print(f"\nViolation detection (15 injected violations, 3 case studies)")
    vd = agg["violation_detection"]
    print(f"  Total TP={vd['total_TP']}  FP={vd['total_FP']}  FN={vd['total_FN']}")
    print(f"  Mean precision : {vd['mean_precision']:.3f}")
    print(f"  Mean recall    : {vd['mean_recall']:.3f}")
    print(f"  Mean F1        : {vd['mean_f1']:.3f}")
    print(f"  Mean specificity: {vd['mean_specificity']:.3f}")

    print(f"\nEvidence-gap detection (6 injected gaps, 3 case studies)")
    gd = agg["gap_detection"]
    print(f"  Total TP={gd['total_TP']}  FP={gd['total_FP']}  FN={gd['total_FN']}")
    print(f"  Mean precision : {gd['mean_precision']:.3f}")
    print(f"  Mean recall    : {gd['mean_recall']:.3f}")
    print(f"  Mean F1        : {gd['mean_f1']:.3f}")

    print(f"\nExplanation completeness (mean): {agg['mean_explanation_completeness']:.3f}")
    print(f"Mean report generation time    : {agg['mean_tool_report_ms']:.1f} ms")
    print(f"Mean speedup vs manual audit   : {agg['mean_speedup_factor']:.0f}×")

    # Save results
    out_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "aggregate_metrics.json"), "w") as f:
        json.dump({"aggregate": agg, "per_case_study": [
            {k: v for k, v in r.items() if k != "violated_report"}
            for r in results
        ]}, f, indent=2)

    for r in results:
        fname = f"compliance_report_{r['case_study']}_violated.json"
        with open(os.path.join(out_dir, fname), "w") as f:
            json.dump(r["violated_report"], f, indent=2)

    print(f"\nResults saved to {out_dir}/")
    print("Done.")
