import csv
import json
import re
import difflib

with open("data/guideline_refs_blob_normalized.txt") as f:
    blob = f.read()


def normalize(s):
    s = s.lower()
    s = re.sub(r"[‐-―]", "-", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


with open("data/csv-endometrio-set.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

results = []
exact_hits = 0
fuzzy_hits = 0

for row in rows:
    title = row["Title"].rstrip(".")
    norm_title = normalize(title)
    hit = False
    method = None
    # guard against short/generic titles (e.g. bare "Endometriosis") trivially
    # substring-matching anywhere in a document about endometriosis
    if len(norm_title) < 25:
        results.append({
            "pmid": row["PMID"],
            "title": row["Title"],
            "year": row["Publication Year"],
            "doi": row["DOI"],
            "guideline_matched": False,
            "match_method": "skipped_title_too_short",
        })
        continue
    if norm_title and norm_title in blob:
        hit = True
        method = "exact_substring"
        exact_hits += 1
    else:
        # fuzzy fallback: slide a window across the blob roughly the length
        # of the title and take the best ratio; expensive if done naively
        # over 753 papers x 215k chars, so first gate on a distinctive
        # long word from the title to narrow candidate windows.
        words = [w for w in norm_title.split() if len(w) >= 7]
        candidate_found = False
        best_ratio = 0.0
        if words:
            anchor = max(words, key=len)
            for m in re.finditer(re.escape(anchor), blob):
                start = max(0, m.start() - len(norm_title))
                end = min(len(blob), m.end() + len(norm_title))
                window = blob[start:end]
                ratio = difflib.SequenceMatcher(None, norm_title, window).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                if ratio > 0.6:
                    candidate_found = True
        if candidate_found:
            hit = True
            method = f"fuzzy_{best_ratio:.2f}"
            fuzzy_hits += 1

    results.append({
        "pmid": row["PMID"],
        "title": row["Title"],
        "year": row["Publication Year"],
        "doi": row["DOI"],
        "guideline_matched": hit,
        "match_method": method,
    })

print("total:", len(results), "exact:", exact_hits, "fuzzy:", fuzzy_hits,
      "total matched:", sum(1 for r in results if r["guideline_matched"]))

with open("data/guideline_match_results.json", "w") as f:
    json.dump(results, f, indent=2)
