# Broken Proxies: Endometriosis Corpus Analysis

Analysis code and derived data for the empirical demonstration (Section 5) of:

> Nidhi Menon, "Broken Proxies: Rethinking Scientometric Ranking Signals for Patient-Facing Research Discovery," in *Research Discovery by Integrating Recommenders with Scientometrics* (Springer Nature, edited volume, forthcoming).

The chapter evaluates how well citation-based ranking recovers evidence referenced by a current clinical practice guideline, using a 753-paper endometriosis literature corpus and the ESHRE 2022 endometriosis management guideline. This repository contains the scripts and derived data needed to reproduce that analysis, and it is the code-availability reference cited in the chapter's Acknowledgements.

## What's here

```
scripts/
  fetch_icite.py               retrieves citation count + RCR for each PMID from the NIH iCite API
  extract_guideline_refs.py    extracts and normalizes reference-list text from the ESHRE guideline PDF
  match_guideline.py           matches corpus paper titles against the guideline reference text
  build_rankings.py            an earlier, abandoned full-ranking construction (binary match + recency
                                tie-break); kept for transparency since Sect. 5.3 of the chapter explains
                                why this approach was rejected in favor of the precision/recall framing
  precision_recall_analysis.py computes precision@k, recall@k, and Average Precision (the chapter's
                                core empirical result)
  make_recall_figure.py        generates the recall-at-k figure (Fig. 1 in the chapter)
  s2_crosscheck.py             Semantic Scholar citation-count cross-validation (robustness check)
  s2_retry.py                  retry pass for rate-limited Semantic Scholar API calls

data/
  pmids.txt                    the 753 PMIDs constituting the corpus
  csv-endometrio-set.csv       PubMed export metadata for the corpus (title, authors, journal, year, DOI)
  icite_data.json              raw iCite API responses (citation count, RCR) for all 753 papers
  guideline_match_results.json binary guideline-reference-inclusion match results per paper
  ranked_corpus.json           the full corpus with citation ranks and match status merged
  rankings_summary.json        top-10 lists and summary statistics
  precision_recall_results.json  precision/recall/AP at each cutoff (raw citation count and RCR)
  recall_curve_data.json       data underlying the recall-at-k figure
  s2_crosscheck.json           Semantic Scholar cross-validation results

figures/
  recall_at_k.pdf / .png       the recall-at-k figure as it appears in the chapter
```

## What's not here, and why

The ESHRE 2022 guideline PDF, and any extracted verbatim text from it, are **not included** in this repository. ESHRE's copyright notice restricts its guidelines to personal and educational use and prohibits reproduction. To reproduce the guideline-matching step:

1. Download the ESHRE 2022 "Guideline on the management of women with endometriosis" from [eshre.eu](https://www.eshre.eu/guidelines) (search: Endometriosis Guideline 2022).
2. Save it as `data/ESHRE GUIDELINE ENDOMETRIOSIS 2022_1.pdf` (or update the filename in `extract_guideline_refs.py`).
3. Run `python scripts/extract_guideline_refs.py` to regenerate the reference-text blob used by `match_guideline.py`.

## Reproducing the analysis

1. The PubMed corpus (`data/csv-endometrio-set.csv`, `data/pmids.txt`) was obtained by running the following query on [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/) and exporting all 753 results (Save → All results → CSV):

   ```
   (endometriosis[MeSH Major Topic]) AND
   (diagnosis[tiab] OR treatment[tiab] OR management[tiab] OR therapy[tiab] OR surgery[tiab] OR "hormonal treatment"[tiab]) AND
   ("2000/01/01"[PDAT] : "2024/12/31"[PDAT]) AND
   English[lang] AND humans[MeSH Terms] AND
   ("systematic review"[Publication Type] OR "meta-analysis"[Publication Type] OR "randomized controlled trial"[Publication Type])
   ```

2. `python scripts/fetch_icite.py` — retrieves citation counts and RCR from the [NIH iCite API](https://icite.od.nih.gov/) for all PMIDs.
3. Obtain the ESHRE guideline PDF as described above, then `python scripts/extract_guideline_refs.py` and `python scripts/match_guideline.py` to produce the guideline-reference-inclusion labels.
4. `python scripts/precision_recall_analysis.py` — computes the chapter's core empirical results (Table 2, rank-distribution statistics).
5. `python scripts/make_recall_figure.py` — generates Fig. 1.
6. `python scripts/s2_crosscheck.py` (and `s2_retry.py` for rate-limited entries) — the Semantic Scholar robustness check.

All derived JSON/CSV outputs in `data/` are already included, so steps 2–5 can be skipped if you just want to inspect or reuse the results directly.

## Requirements

See `requirements.txt`. Python 3.9+; uses only the standard library plus `scipy`, `matplotlib`, and `pymupdf` (for PDF text extraction, only needed if regenerating the guideline match from a freshly downloaded ESHRE PDF).

## License

Code and derived data in this repository are released under the MIT License (see `LICENSE`). This does not extend to the ESHRE guideline document itself, which remains subject to ESHRE's own copyright terms and is not redistributed here.

## Citation

If you use this code or data, please cite the chapter:

> Menon, N. "Broken Proxies: Rethinking Scientometric Ranking Signals for Patient-Facing Research Discovery." In *Research Discovery by Integrating Recommenders with Scientometrics*. Springer Nature (forthcoming).
