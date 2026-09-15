import json
import time
import urllib.request
import urllib.error

with open("data/s2_crosscheck.json") as f:
    results = json.load(f)

missing = [x for x in results if x["s2_citation_count"] is None]
print(f"retrying {len(missing)} missing")

for x in missing:
    pmid = x["pmid"]
    url = f"https://api.semanticscholar.org/graph/v1/paper/PMID:{pmid}?fields=citationCount"
    val = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-script/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.load(resp)
            val = data.get("citationCount")
            break
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(15)
                continue
            print("http error", pmid, e.code)
            break
        except Exception as e:
            print("error", pmid, e)
            time.sleep(5)
    x["s2_citation_count"] = val
    print(pmid, "->", val)
    time.sleep(3)

with open("data/s2_crosscheck.json", "w") as f:
    json.dump(results, f, indent=2)

resolved = sum(1 for x in results if x["s2_citation_count"] is not None)
print(f"total resolved: {resolved}/{len(results)}")
