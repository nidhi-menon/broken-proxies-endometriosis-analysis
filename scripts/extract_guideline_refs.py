import fitz
import re
import json

doc = fitz.open("data/ESHRE GUIDELINE ENDOMETRIOSIS 2022_1.pdf")

ref_page_idxs = []
for i in range(len(doc)):
    t = doc[i].get_text()
    lines = t.split("\n")
    for l in lines:
        if l.strip() == "References":
            ref_page_idxs.append(i)
            break

print("reference-section start pages:", ref_page_idxs)

# Build one big normalized text blob spanning all reference-bearing pages
# (each ref section runs from its "References" line to the next section
# heading; simplest robust approach is to take full text of the ref-start
# page plus the following page, since ESHRE ref lists here run 0-2 pages).
blob_parts = []
for p in ref_page_idxs:
    for q in (p, p + 1):
        if q < len(doc):
            blob_parts.append(doc[q].get_text())

raw_blob = "\n".join(blob_parts)


def normalize(s):
    s = s.lower()
    s = re.sub(r"[‐-―]", "-", s)  # unicode dashes -> hyphen
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


norm_blob = normalize(raw_blob)

with open("data/guideline_refs_blob.txt", "w") as f:
    f.write(raw_blob)
with open("data/guideline_refs_blob_normalized.txt", "w") as f:
    f.write(norm_blob)

print("raw blob chars:", len(raw_blob), "normalized chars:", len(norm_blob))
