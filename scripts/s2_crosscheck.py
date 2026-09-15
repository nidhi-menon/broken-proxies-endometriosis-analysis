import json
import time
import urllib.request
import urllib.error

with open("data/ranked_corpus.json") as f:
    corpus = json.load(f)

# Stratified sample across the citation-count distribution: every Nth paper
# by citation rank, ~30 papers total, spanning high/mid/low citation counts.
by_citation = sorted(corpus, key=lambda r: -r["citation_count"])
n = len(by_citation)
step = max(1, n // 30)
sample = by_citation[::step][:30]

results = []
for r in sample:
    pmid = r["pmid"]
    url = f"https://api.semanticscholar.org/graph/v1/paper/PMID:{pmid}?fields=citationCount,title"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.load(resp)
            s2_count = data.get("citationCount")
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5)
                continue
            s2_count = None
            break
        except Exception as e:
            print("error", pmid, e)
            s2_count = None
            time.sleep(2)
    else:
        s2_count = None
    results.append({
        "pmid": pmid,
        "title": r["title"],
        "icite_citation_count": r["citation_count"],
        "s2_citation_count": s2_count,
    })
    print(pmid, "icite=", r["citation_count"], "s2=", s2_count)
    time.sleep(1.2)

with open("data/s2_crosscheck.json", "w") as f:
    json.dump(results, f, indent=2)

valid = [x for x in results if x["s2_citation_count"] is not None]
if valid:
    diffs = [(x["s2_citation_count"] - x["icite_citation_count"]) for x in valid]
    ratios = [x["s2_citation_count"] / x["icite_citation_count"] for x in valid if x["icite_citation_count"] > 0]
    print(f"\nn={len(valid)}/{len(results)} resolved")
    print(f"mean diff (s2 - icite) = {sum(diffs)/len(diffs):.1f}")
    print(f"mean ratio (s2/icite) = {sum(ratios)/len(ratios):.2f}")
