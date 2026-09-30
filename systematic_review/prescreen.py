"""Deterministic pre-screening of the deduplicated records (before topical screening).

Usage
    python prescreen.py data/records_unique.csv data/

Codes, applied in order:
  PS1  not an individual study (proceedings volume, front matter)
  PS2  published before 2015, or no publication year
  PS3  publication type other than a peer-reviewed journal article or conference paper
       (arXiv-only preprints, book chapters, books, reports, ...). Records typed as book
       chapters but published in a conference-proceedings series (LNCS, CCIS, LNNS, IFIP AICT,
       Springer Proceedings, Frontiers in AI and Applications, ...) are conference papers and
       are kept.
  PS4  no abstract available
Outputs: records_prescreened.csv (all records, with prescreen_decision / prescreen_code)
         records_for_topical_screening.csv (records passing all four rules)
"""
import re
import sys
from pathlib import Path
import pandas as pd

NON_STUDY = {"Proceedings volume", "Front matter"}
KEEP_TYPES = {"Journal article", "Conference paper", "Article", "Congress/conference paper",
              "Conference paper (also on arXiv)", "Journal article (also on arXiv)",
              "Published version (also on arXiv)"}


PROC_SERIES = re.compile(
    r"lecture notes|lncs|lnai|lnbip|communications in computer and information science|"
    r"proceedings|conference|symposium|workshop|congress|forum|advances in intelligent systems|"
    r"smart innovation|ifip advances|frontiers in artificial intelligence and applications", re.I)


def classify(r, year):
    if r["venue_type"] in NON_STUDY: return "PS1 not an individual study"
    if pd.isna(year) or year < 2015: return "PS2 published before 2015 / no year"
    proc_chapter = r["venue_type"] == "Book chapter" and bool(PROC_SERIES.search(r["journal_or_venue"]))
    if r["venue_type"] not in KEEP_TYPES and not proc_chapter: return f"PS3 publication type: {r['venue_type'] or 'unknown'}"
    if not r["abstract"].strip(): return "PS4 no abstract available"
    return ""


def main(inp, outdir):
    u = pd.read_csv(inp, dtype=str, keep_default_na=False)
    years = pd.to_numeric(u["year"], errors="coerce")
    u["prescreen_code"] = [classify(r, years[i]) for i, r in u.iterrows()]
    u["prescreen_decision"] = u["prescreen_code"].map(lambda c: "exclude" if c else "to_topical_screening")
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    u.to_csv(out / "records_prescreened.csv", index=False)
    u[u["prescreen_decision"] == "to_topical_screening"].to_csv(out / "records_for_topical_screening.csv", index=False)
    print(f"unique records: {len(u)}")
    print(u["prescreen_code"].str.split(":").str[0].replace("", "(passes)").value_counts().to_string())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
