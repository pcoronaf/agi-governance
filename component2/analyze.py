"""
Component 2 analysis: inter-labeler agreement + engine-vs-consensus agreement.

Inputs (real data you provide):
  --labels labels.csv        columns: package_id,labeler_id,norm_id,verdict[,...]
  --engine engine_outputs.json   {package_id: {norm_id: verdict}}
Outputs: prints metrics and writes component2_results.json.


"""
import argparse, csv, json, itertools
from collections import defaultdict

CATS = ["COMPLIANT","VIOLATED","EVIDENCE_GAP"]

def cohen_kappa(a, b):
    items = [(x,y) for x,y in zip(a,b) if x and y]
    if not items: return None
    n = len(items)
    po = sum(1 for x,y in items if x==y)/n
    pa = {c: sum(1 for x,_ in items if x==c)/n for c in CATS}
    pb = {c: sum(1 for _,y in items if y==c)/n for c in CATS}
    pe = sum(pa[c]*pb[c] for c in CATS)
    return round((po-pe)/(1-pe),4) if pe!=1 else 1.0

def fleiss_kappa(rows):  # rows: list of dicts cat->count (equal rater count per row)
    rows = [r for r in rows if sum(r.values())>1]
    if not rows: return None
    n = sum(rows[0].values()); N = len(rows)
    p = {c: sum(r.get(c,0) for r in rows)/(N*n) for c in CATS}
    Pe = sum(v*v for v in p.values())
    Pbar = sum((sum(r.get(c,0)**2 for c in CATS)-n)/(n*(n-1)) for r in rows)/N
    return round((Pbar-Pe)/(1-Pe),4) if Pe!=1 else 1.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", required=True)
    ap.add_argument("--engine", required=True)
    a = ap.parse_args()

    labels = defaultdict(dict)   # (package,norm) -> {labeler: verdict}
    labelers = set()
    with open(a.labels) as f:
        for row in csv.DictReader(f):
            v = (row.get("verdict") or "").strip().upper()
            if not v: continue
            assert v in CATS, f"bad verdict {v!r} in labels"
            labels[(row["package_id"], row["norm_id"])][row["labeler_id"]] = v
            labelers.add(row["labeler_id"])
    if not labels:
        print("No labels found. Fill labeling_sheet_template.csv first."); return
    engine = json.load(open(a.engine))
    labelers = sorted(labelers)

    # inter-labeler agreement
    inter = None
    if len(labelers) == 2:
        cells = sorted(labels)
        a1 = [labels[c].get(labelers[0]) for c in cells]
        a2 = [labels[c].get(labelers[1]) for c in cells]
        inter = {"method":"cohen_kappa","raters":labelers,"kappa":cohen_kappa(a1,a2)}
    elif len(labelers) >= 3:
        rows = []
        for c in labels:
            cnt = {k:0 for k in CATS}
            for lb in labelers:
                if labels[c].get(lb): cnt[labels[c][lb]] += 1
            if sum(cnt.values())==len(labelers): rows.append(cnt)
        inter = {"method":"fleiss_kappa","raters":labelers,"kappa":fleiss_kappa(rows)}

    # consensus + engine agreement
    agree = total = 0; disagreements = []; gap_cells = 0
    for (pkg,norm), lab in labels.items():
        votes = defaultdict(int)
        for v in lab.values(): votes[v]+=1
        top = max(votes.values())
        cons = [c for c in CATS if votes.get(c,0)==top]
        consensus = cons[0] if len(cons)==1 else "NO_CONSENSUS"
        eng = engine.get(pkg,{}).get(norm)
        if consensus=="EVIDENCE_GAP": gap_cells += 1
        if eng is None: continue
        total += 1
        if eng==consensus: agree += 1
        else:
            disagreements.append({"package":pkg,"norm":norm,
                "labeler_consensus":consensus,"engine":eng,"labels":lab})

    out = {
      "n_packages": len({p for p,_ in labels}),
      "n_labelers": len(labelers), "n_cells": len(labels),
      "inter_labeler_agreement": inter,
      "engine_vs_consensus": {"agreement": round(agree/total,4) if total else None,
                              "agree": agree, "total": total},
      "evidence_gap_consensus_cells": gap_cells,
      "disagreements": disagreements,
    }
    json.dump(out, open("component2_results.json","w"), indent=2)
    print(json.dumps({k:v for k,v in out.items() if k!="disagreements"}, indent=2))
    print(f"\n{len(disagreements)} disagreement(s) written to component2_results.json")

if __name__ == "__main__":
    main()
