import json
import statistics

c = json.load(open("data/ranked_corpus.json"))
n = len(c)
n_matched = sum(1 for r in c if r["guideline_matched"])
prevalence = n_matched / n

def pr_at_k(ranked, k):
    top_k = ranked[:k]
    tp = sum(1 for r in top_k if r["guideline_matched"])
    precision = tp / k
    recall = tp / n_matched
    return precision, recall, tp

def average_precision(ranked):
    hits = 0
    ap_sum = 0.0
    for i, r in enumerate(ranked, start=1):
        if r["guideline_matched"]:
            hits += 1
            ap_sum += hits / i
    return ap_sum / n_matched

by_citation = sorted(c, key=lambda r: (-r["citation_count"], r["pmid"]))
valid_rcr = [r for r in c if r.get("rcr") is not None]
by_rcr = sorted(valid_rcr, key=lambda r: (-r["rcr"], r["pmid"]))
n_matched_rcr = sum(1 for r in valid_rcr if r["guideline_matched"])

print(f"N = {n}, guideline-matched = {n_matched} ({prevalence*100:.1f}% prevalence)")
print(f"N with valid RCR = {len(valid_rcr)}, guideline-matched among them = {n_matched_rcr}")
print()

ks = [10, 25, 50, 100, 250]
print("=== Raw citation count ===")
for k in ks:
    p, r, tp = pr_at_k(by_citation, k)
    print(f"k={k:>4}  precision={p*100:5.1f}%  recall={r*100:5.1f}%  (tp={tp})")
ap_citation = average_precision(by_citation)
print(f"Average Precision (raw citation count) = {ap_citation:.4f}")
print()

print("=== RCR ===")
def pr_at_k_rcr(ranked, k, denom):
    top_k = ranked[:k]
    tp = sum(1 for r in top_k if r["guideline_matched"])
    precision = tp / k
    recall = tp / denom
    return precision, recall, tp

for k in ks:
    p, r, tp = pr_at_k_rcr(by_rcr, k, n_matched_rcr)
    print(f"k={k:>4}  precision={p*100:5.1f}%  recall={r*100:5.1f}%  (tp={tp})")

def average_precision_generic(ranked, denom):
    hits = 0
    ap_sum = 0.0
    for i, r in enumerate(ranked, start=1):
        if r["guideline_matched"]:
            hits += 1
            ap_sum += hits / i
    return ap_sum / denom

ap_rcr = average_precision_generic(by_rcr, n_matched_rcr)
print(f"Average Precision (RCR) = {ap_rcr:.4f}")
print()

# Citation-rank distribution among the 124 matched papers
matched_ranks = sorted(r["citation_rank"] for r in by_citation if r["guideline_matched"])
print("=== Citation-rank distribution of the", len(matched_ranks), "guideline-matched papers ===")
print("min:", matched_ranks[0], "max:", matched_ranks[-1])
print("median:", statistics.median(matched_ranks))
q1 = matched_ranks[len(matched_ranks)//4]
q3 = matched_ranks[3*len(matched_ranks)//4]
print("Q1:", q1, "Q3:", q3)
for cutoff in [10, 25, 50, 100, 250, 500]:
    below = sum(1 for x in matched_ranks if x <= cutoff)
    print(f"matched papers with citation-rank <= {cutoff}: {below}/{len(matched_ranks)} ({below/len(matched_ranks)*100:.1f}%)")

# save full curve data for the figure
curve_data = {"ks": list(range(1, 754)), "citation": [], "rcr": []}
tp = 0
for i, r in enumerate(by_citation, start=1):
    if r["guideline_matched"]:
        tp += 1
    curve_data["citation"].append(tp / n_matched)

tp = 0
for i, r in enumerate(by_rcr, start=1):
    if r["guideline_matched"]:
        tp += 1
    curve_data["rcr"].append(tp / n_matched_rcr)

json.dump(curve_data, open("data/recall_curve_data.json", "w"))
print("\nsaved recall_curve_data.json")

results = {
    "n": n, "n_matched": n_matched, "prevalence": prevalence,
    "n_valid_rcr": len(valid_rcr), "n_matched_rcr": n_matched_rcr,
    "pr_at_k_citation": {k: dict(zip(["precision","recall","tp"], pr_at_k(by_citation, k))) for k in ks},
    "pr_at_k_rcr": {k: dict(zip(["precision","recall","tp"], pr_at_k_rcr(by_rcr, k, n_matched_rcr))) for k in ks},
    "ap_citation": ap_citation, "ap_rcr": ap_rcr,
    "matched_rank_min": matched_ranks[0], "matched_rank_max": matched_ranks[-1],
    "matched_rank_median": statistics.median(matched_ranks),
    "matched_rank_q1": q1, "matched_rank_q3": q3,
}
json.dump(results, open("data/precision_recall_results.json", "w"), indent=2)
print("saved precision_recall_results.json")
