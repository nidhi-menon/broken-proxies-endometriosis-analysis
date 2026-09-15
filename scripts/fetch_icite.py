import json
import time
import urllib.request

with open("data/pmids.txt") as f:
    pmids = [line.strip() for line in f if line.strip()]

BATCH = 100
results = {}
for i in range(0, len(pmids), BATCH):
    batch = pmids[i:i+BATCH]
    url = "https://icite.od.nih.gov/api/pubs?pmids=" + ",".join(batch)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.load(resp)
            break
        except Exception as e:
            print("retry", i, e)
            time.sleep(2)
    else:
        raise RuntimeError(f"failed batch at {i}")
    for rec in data["data"]:
        results[str(rec["pmid"])] = rec
    print(f"fetched {i+len(batch)}/{len(pmids)}")
    time.sleep(0.5)

missing = [p for p in pmids if p not in results]
print("missing:", len(missing), missing[:20])

with open("data/icite_data.json", "w") as f:
    json.dump(results, f)
print("saved", len(results), "records")
