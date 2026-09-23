#!/usr/bin/env python3
"""
Inter-coder reliability for the real-evidence bridgeability study (paper Section 8.5).

Reads coder_agreement_matrix.csv (one row per document x indicator cell, with the
strict- and generous-pass judgment of each of the three coders) and reproduces every
statistic reported in Section 8.5:

  * per-coder positive counts and per-generation computability counts
  * pairwise raw agreement, Cohen's kappa, PABAK
  * Fleiss' kappa across the three coders
  * majority-vote consensus counts

Cohen's and Fleiss' kappa are undefined when no coder records a positive judgment
(zero variance); the strict pass is such a case and is reported as raw agreement and
PABAK only, consistent with the paper.

Python 3.9+, no external dependencies.
"""

import csv
import os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, "coder_agreement_matrix.csv")
CODERS = ("C1", "C2", "C3")
POSITIVE = "C"          # COMPUTABLE
NEGATIVE = "NC"         # NOT_COMPUTABLE


def load(path=MATRIX):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit("empty matrix")
    return rows


def positives(rows, coder, pass_name):
    col = f"{coder}_{pass_name}"
    return {r["cell_id"] for r in rows if r[col] == POSITIVE}


def cohen(a_pos, b_pos, n):
    both = len(a_pos & b_pos)
    a_only = len(a_pos - b_pos)
    b_only = len(b_pos - a_pos)
    neither = n - both - a_only - b_only
    po = (both + neither) / n
    pa = (both + a_only) / n
    pb = (both + b_only) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = None if pe >= 1.0 else (po - pe) / (1 - pe)
    return po, kappa, 2 * po - 1, both, a_only, b_only


def fleiss(rows, pass_name):
    n, k = len(rows), len(CODERS)
    pi_sum, pos_total = 0.0, 0
    for r in rows:
        nij = sum(1 for c in CODERS if r[f"{c}_{pass_name}"] == POSITIVE)
        pos_total += nij
        pi_sum += (nij * (nij - 1) + (k - nij) * (k - nij - 1)) / (k * (k - 1))
    p_bar = pi_sum / n
    p1 = pos_total / (n * k)
    pe = p1 * p1 + (1 - p1) * (1 - p1)
    kappa = None if pe >= 1.0 else (p_bar - pe) / (1 - pe)
    return p_bar, kappa


def fmt(x):
    return "undefined (zero variance)" if x is None else f"{x:.3f}"


def report(rows, pass_name):
    n = len(rows)
    print(f"\n=== {pass_name.upper()} PASS (n = {n} cells) ===")
    pos = {c: positives(rows, c, pass_name) for c in CODERS}
    for c in CODERS:
        by_gen = {}
        for r in rows:
            if r["cell_id"] in pos[c]:
                by_gen[r["generation"]] = by_gen.get(r["generation"], 0) + 1
        gens = ", ".join(f"{g}: {by_gen.get(g, 0)}" for g in sorted({r['generation'] for r in rows}))
        print(f"  {c} positives: {len(pos[c])}/{n}   ({gens})")

    print("  pairwise:")
    for a, b in combinations(CODERS, 2):
        po, k, pabak, both, ao, bo = cohen(pos[a], pos[b], n)
        print(f"    {a}-{b}: agreement {round(po * n)}/{n} ({po:.3f}), "
              f"Cohen's kappa {fmt(k)}, PABAK {pabak:.3f} "
              f"[both+ {both}, {a}-only {ao}, {b}-only {bo}]")

    p_bar, fk = fleiss(rows, pass_name)
    print(f"  Fleiss' kappa (3 raters): {fmt(fk)}   (mean observed agreement {p_bar:.3f})")

    unanimous = sum(
        1 for r in rows
        if len({r[f"{c}_{pass_name}"] for c in CODERS}) == 1
    )
    print(f"  unanimous cells: {unanimous}/{n}; split cells: {n - unanimous}")
    for r in rows:
        votes = [c for c in CODERS if r[f"{c}_{pass_name}"] == POSITIVE]
        if 0 < len(votes) < len(CODERS):
            print(f"    split: {r['document']} x {r['indicator']} -> positive by {', '.join(votes)}")

    maj = [r for r in rows
           if sum(1 for c in CODERS if r[f"{c}_{pass_name}"] == POSITIVE) >= 2]
    by_gen = {}
    for r in maj:
        by_gen[r["generation"]] = by_gen.get(r["generation"], 0) + 1
    per_gen_total = {}
    for r in rows:
        per_gen_total[r["generation"]] = per_gen_total.get(r["generation"], 0) + 1
    print("  majority-vote consensus (>= 2 of 3):")
    for g in sorted(per_gen_total):
        print(f"    {g}: {by_gen.get(g, 0)}/{per_gen_total[g]}")

    agi = [r for r in maj if r["indicator_class"] == "agi_specific"]
    print(f"  AGI-specific indicators computable (consensus): {len(agi)}")


def main():
    rows = load()
    print("Inter-coder reliability - real-evidence bridgeability study (paper Section 8.5)")
    print(f"cells: {len(rows)}  coders: {', '.join(CODERS)}")
    for pass_name in ("strict", "generous"):
        report(rows, pass_name)
    print("\nConsensus figures adopted in the paper are recorded in reconciliation_log.md.")


if __name__ == "__main__":
    main()
