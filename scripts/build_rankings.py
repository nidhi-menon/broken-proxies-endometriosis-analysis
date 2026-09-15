import csv
import json
from scipy.stats import spearmanr

with open("data/icite_data.json") as f:
    icite = json.load(f)

with open("data/guideline_match_results.json") as f:
    guideline = {r["pmid"]: r for r in json.load(f)}

with open("data/csv-endometrio-set.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

corpus = []
for row in rows:
    pmid = row["PMID"]
    ic = icite.get(pmid, {})
    corpus.append({
        "pmid": pmid,
        "title": row["Title"],
        "journal": row["Journal/Book"],
        "year": row["Publication Year"],
        "doi": row["DOI"],
        "citation_count": ic.get("citation_count", 0) or 0,
        "rcr": ic.get("relative_citation_ratio"),
        "nih_percentile": ic.get("nih_percentile"),
        "guideline_matched": guideline[pmid]["guideline_matched"],
    })

# Rank 1 = most highly ranked (best) in each scheme.
by_citation = sorted(corpus, key=lambda r: (-r["citation_count"], r["pmid"]))
for i, r in enumerate(by_citation):
    r["citation_rank"] = i + 1

# Guideline-adoption ranking: matched papers first (the independent signal),
# then non-matched papers. Ties are broken by recency (year), NOT citation
# count -- reusing citation count as the tie-break would silently preserve
# the citation-based order for the ~83% of the corpus that is unmatched,
# artificially inflating the correlation between the two rankings.
def year_key(r):
    try:
        return -int(r["year"])
    except (ValueError, TypeError):
        return 0

by_guideline = sorted(
    corpus,
    key=lambda r: (0 if r["guideline_matched"] else 1, year_key(r), r["pmid"]),
)
for i, r in enumerate(by_guideline):
    r["guideline_rank"] = i + 1

pmid_index = {r["pmid"]: r for r in corpus}

citation_ranks = [pmid_index[p]["citation_rank"] for p in pmid_index]
guideline_ranks = [pmid_index[p]["guideline_rank"] for p in pmid_index]
rho, pval = spearmanr(citation_ranks, guideline_ranks)

print(f"N = {len(corpus)}")
print(f"Guideline-matched: {sum(1 for r in corpus if r['guideline_matched'])}")
print(f"Spearman's rho (citation_rank vs guideline_rank) = {rho:.4f}, p = {pval:.3e}")

# Top-10 overlap
top10_citation = set(r["pmid"] for r in by_citation[:10])
top10_guideline = set(r["pmid"] for r in by_guideline[:10])
overlap = top10_citation & top10_guideline
print(f"Top-10 overlap: {len(overlap)}/10 -> {sorted(overlap)}")

with open("data/ranked_corpus.json", "w") as f:
    json.dump(corpus, f, indent=2)

with open("data/rankings_summary.json", "w") as f:
    json.dump({
        "n": len(corpus),
        "guideline_matched_count": sum(1 for r in corpus if r["guideline_matched"]),
        "spearman_rho": rho,
        "spearman_pvalue": pval,
        "top10_overlap_count": len(overlap),
        "top10_overlap_pmids": sorted(overlap),
        "top10_citation": [{"pmid": r["pmid"], "title": r["title"], "citation_count": r["citation_count"], "guideline_matched": r["guideline_matched"]} for r in by_citation[:10]],
        "top10_guideline": [{"pmid": r["pmid"], "title": r["title"], "citation_count": r["citation_count"], "guideline_matched": r["guideline_matched"]} for r in by_guideline[:10]],
    }, f, indent=2)

print("saved ranked_corpus.json and rankings_summary.json")
