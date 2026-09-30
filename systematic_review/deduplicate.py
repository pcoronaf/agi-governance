"""Deduplicate the identified records (no pre-screening, no exclusions).

Usage
    python deduplicate.py [input.csv] [output_dir]

    input.csv   default: data/records_identified.csv
                Also accepts the consolidated file
                (consolidated_AI_governance_references_with_abstracts.csv).
    output_dir  default: the input file's folder

Outputs
    records_unique.csv          one row per unique record (the kept representative of each group),
                                with found_in_sources, n_source_records and duplicate_record_ids
    duplicate_groups.csv        every record that belongs to a group of 2+, with its kept_record_id
    records_with_dedup_ids.csv  all input rows, each with kept_record_id and is_duplicate

Rules
  1. Records are linked when they share a normalised DOI, or when a preprint's peer-reviewed DOI
     (column published_doi_of_preprint, if present) matches another record's DOI.
  2. Title rule: records whose normalised titles (>= 20 characters) are identical are linked
     only if at least one of them has no DOI or only an arXiv DOI (10.48550/...). Two records with
     different publisher DOIs are never merged on title alone.
  3. Linked records form groups (union-find). One record per group is kept: the peer-reviewed
     version over the preprint, then the record with an abstract, then source order
     ACM DL > IEEE Xplore > SpringerLink > Scopus > arXiv > other, then record_id.
"""
import re
import sys
from pathlib import Path

import pandas as pd

SOURCE_ORDER = ["ACM Digital Library", "IEEE Xplore", "SpringerLink", "Scopus", "arXiv",
                "Previous review (included studies)", "Round-2 study dataset",
                "Other: cross-database candidates", "Cross-database candidate",
                "Cross-database candidate (IEEE-related)", "Other: OpenAlex", "OpenAlex"]


def norm_doi(x):
    x = str(x or "").strip().lower()
    x = re.sub(r"^https?://(dx\.)?doi\.org/", "", x)
    return x.rstrip(".") if x.startswith("10.") else ""


def norm_title(x):
    return re.sub(r"[^a-z0-9]", "", str(x or "").lower())


def src_rank(s):
    return SOURCE_ORDER.index(s) if s in SOURCE_ORDER else len(SOURCE_ORDER)


def load(path):
    d = pd.read_csv(path, dtype=str, keep_default_na=False)
    # harmonise the two input layouts
    if "source" not in d.columns:
        d["source"] = d.get("origin", "")
    if "record_id" not in d.columns:
        d.insert(0, "record_id", [f"R{i+1:04d}" for i in range(len(d))])
    doi_col = "lookup_key" if "lookup_key" in d.columns else "DOI"
    d["_doi"] = d[doi_col].map(norm_doi)
    d["_pub_doi"] = d["published_doi_of_preprint"].map(norm_doi) if "published_doi_of_preprint" in d.columns else ""
    d["_title"] = d["title"].map(norm_title)
    if "has_abstract" in d.columns:
        d["_has_abs"] = d["has_abstract"].eq("yes")
    else:
        d["_has_abs"] = d.get("abstract", pd.Series("", index=d.index)).str.strip().ne("")
    d["_preprint"] = d.get("venue_type", "").eq("Preprint") | d.get("journal_or_venue", "").eq("arXiv (preprint)")
    return d


def deduplicate(d):
    parent = list(range(len(d)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        a, b = find(i), find(j)
        if a != b:
            parent[max(a, b)] = min(a, b)

    # rule 1: shared DOI / preprint -> published DOI
    first = {}
    for i, (doi, pub) in enumerate(zip(d["_doi"], d["_pub_doi"])):
        for k in {doi, pub} - {""}:
            if k in first:
                union(i, first[k])
            else:
                first[k] = i

    # rule 2: identical title, only when at least one side has no publisher DOI
    by_title = {}
    for i, t in enumerate(d["_title"]):
        if len(t) >= 20:
            by_title.setdefault(t, []).append(i)
    for idx in by_title.values():
        weak = [i for i in idx if not d["_doi"].iat[i] or d["_doi"].iat[i].startswith("10.48550/")]
        strong = [i for i in idx if i not in weak]
        anchor = strong[0] if strong else (weak[0] if weak else None)
        if anchor is not None:
            for i in weak:
                union(i, anchor)

    d["_group"] = [find(i) for i in range(len(d))]

    # rule 3: representative
    d["_rank"] = list(zip(d["_preprint"], ~d["_has_abs"], d["source"].map(src_rank), d["record_id"]))
    rep = d.sort_values("_rank").groupby("_group").head(1).set_index("_group")["record_id"]
    d["kept_record_id"] = d["_group"].map(rep)
    d["is_duplicate"] = (d["record_id"] != d["kept_record_id"]).map({True: "yes", False: "no"})
    return d


def main(argv):
    inp = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent / "data" / "records_identified.csv"
    out = Path(argv[2]) if len(argv) > 2 else inp.parent
    out.mkdir(parents=True, exist_ok=True)

    d = deduplicate(load(inp))
    helper = [c for c in d.columns if c.startswith("_")]

    g = d.groupby("kept_record_id")
    size = g.size()
    srcs = g["source"].apply(lambda s: "; ".join(sorted(set(s), key=src_rank)))
    dups = g["record_id"].apply(lambda s: "; ".join(sorted(s)))

    u = d[d["is_duplicate"] == "no"].drop(columns=helper + ["is_duplicate", "kept_record_id"]).copy()
    u["found_in_sources"] = u["record_id"].map(srcs)
    u["n_source_records"] = u["record_id"].map(size)
    u["duplicate_record_ids"] = [
        "; ".join(x for x in dups[r].split("; ") if x != r) for r in u["record_id"]
    ]
    u.to_csv(out / "records_unique.csv", index=False)

    multi = d[d["kept_record_id"].map(size) > 1]
    multi[["kept_record_id", "record_id", "source", "title", "DOI", "is_duplicate"]] \
        .sort_values(["kept_record_id", "record_id"]).to_csv(out / "duplicate_groups.csv", index=False)

    d.drop(columns=helper).to_csv(out / "records_with_dedup_ids.csv", index=False)

    n = len(d)
    print(f"records identified : {n}")
    print(f"unique records     : {len(u)}")
    print(f"duplicates removed : {n - len(u)}  (in {multi['kept_record_id'].nunique()} groups)")
    print("\nduplicates removed by source of the removed record:")
    print(d[d["is_duplicate"] == "yes"]["source"].value_counts().to_string())


if __name__ == "__main__":
    main(sys.argv)
