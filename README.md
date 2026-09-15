# Broken Proxies: Endometriosis Corpus Analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22778879.svg)](https://doi.org/10.5281/zenodo.22778879)

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
  pmids.txt                       the 753 PMIDs constituting the corpus
  csv-endometrio-set.csv          PubMed export metadata for the corpus (title, authors, journal, year, DOI)
  icite_data.json                 raw iCite API responses (citation count, RCR) for all 753 papers
  fuzzy_match_overrides.json      manual adjudications for every fuzzy title-match candidate (see below)
  guideline_match_results.json    binary guideline-reference-inclusion match results per paper
  ranked_corpus.json              the full corpus with citation ranks and match status merged
  rankings_summary.json           top-10 lists and summary statistics
  precision_recall_results.json   precision/recall/AP at each cutoff (raw citation count and RCR)
  recall_curve_data.json          data underlying the recall-at-k figure
  s2_crosscheck.json              Semantic Scholar cross-validation results

figures/
  recall_at_k.pdf / .png       the recall-at-k figure as it appears in the chapter
```

## What's not here, and why

The ESHRE 2022 guideline PDF, and any extracted verbatim text from it (the intermediate `guideline_refs_blob*.txt` files `extract_guideline_refs.py` produces), are **not included** in this repository. ESHRE's copyright notice restricts its guidelines to personal and educational use and prohibits reproduction. To reproduce the guideline-matching step:

1. Download the ESHRE 2022 "Guideline on the management of women with endometriosis" from [eshre.eu](https://www.eshre.eu/guidelines) (search: Endometriosis Guideline 2022).
2. Save it as `data/ESHRE GUIDELINE ENDOMETRIOSIS 2022_1.pdf` (or update the filename in `extract_guideline_refs.py`).
3. Run `python scripts/extract_guideline_refs.py` to regenerate the reference-text blob used by `match_guideline.py`.

### Guideline text extraction heuristic

The ESHRE guideline does not have one consolidated bibliography; it has 36 separate reference lists, one per clinically scoped subsection. `extract_guideline_refs.py` locates every page whose text contains a line reading exactly `References`, then concatenates that page and the page immediately following it into the reference-text corpus. This heuristic was verified by hand against the ESHRE 2022 PDF's specific layout (each reference list runs one to two pages) and is not guaranteed to generalize to a guideline document with a different structure — adapting this script to a different guideline should start by checking whether that same one-heading-plus-next-page assumption holds.

### Fuzzy-match adjudication

`match_guideline.py` matches corpus paper titles against the guideline reference text by exact substring containment first, then by sequence-similarity ("fuzzy") matching for titles with no exact match. **No fuzzy candidate is ever auto-accepted or auto-rejected by the script.** Every fuzzy candidate (similarity ratio > 0.6) must have a corresponding manually-reviewed entry in `data/fuzzy_match_overrides.json`; any fuzzy candidate without one is left as `needs_review` and printed as a warning rather than silently matched. This makes the one manual-review step in the pipeline fully auditable and reproducible: re-running the script against the same inputs applies the same checked-in decisions rather than re-guessing.

In the analysis reported in the chapter, there were exactly 4 fuzzy candidates. 3 were manually accepted (in each case, the only difference from an exact match was a citation-format suffix such as "Cochrane Database Syst Rev" appended in the guideline's reference text). 1 was manually rejected as a false positive after inspection showed the matched text window actually belonged to a different paper's reference entry that happened to share most of its title text. The reasoning for each decision is recorded in `data/fuzzy_match_overrides.json`.

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
3. Obtain the ESHRE guideline PDF as described above, then `python scripts/extract_guideline_refs.py` and `python scripts/match_guideline.py` to produce the guideline-reference-inclusion labels (see "Fuzzy-match adjudication" above — this step will warn if it encounters any new fuzzy candidate not already adjudicated in `data/fuzzy_match_overrides.json`).
4. `python scripts/precision_recall_analysis.py` — computes the chapter's core empirical results (Table 2, rank-distribution statistics).
5. `python scripts/make_recall_figure.py` — generates Fig. 1.
6. `python scripts/s2_crosscheck.py` (and `s2_retry.py` for rate-limited entries) — the Semantic Scholar robustness check.

All derived JSON/CSV outputs in `data/` are already included, so steps 2–6 can be skipped if you just want to inspect or reuse the results directly.

## Requirements

Python 3.9 (as used for the reported run; later 3.x versions likely work but are untested). Exact package versions used are pinned in `requirements.txt`:

```
pip install -r requirements.txt
```

`scipy` and `matplotlib` are needed for the statistics and figure; `pymupdf` is only needed if regenerating the guideline match from a freshly downloaded ESHRE PDF (step 3 above).

## License

**Code** (everything in `scripts/`) is released under the MIT License — see `LICENSE`.

**Derived data** (everything in `data/` and `figures/`) is provided as-is for reproducibility, but is not blanket-licensed under MIT, since it is derived from third-party sources subject to their own terms:
- PubMed metadata (`csv-endometrio-set.csv`, `pmids.txt`) is sourced from NCBI/NLM, a work of the US federal government.
- iCite data (`icite_data.json`) is produced by the NIH Office of Portfolio Analysis.
- Semantic Scholar data (`s2_crosscheck.json`) is licensed by Semantic Scholar/AI2 under [ODC-BY 1.0](https://www.semanticscholar.org/product/api/license); if you reuse it, attribute Semantic Scholar and cite their Open Data Platform paper per their terms.
- The ESHRE guideline itself is not redistributed here at all (see above).

If you plan to redistribute the derived data further, check the current terms of each upstream source rather than relying on this repository's MIT license to cover it.

## Citation

If you use this code or data, please cite the chapter, and optionally this repository's archived release:

> Menon, N. "Broken Proxies: Rethinking Scientometric Ranking Signals for Patient-Facing Research Discovery." In *Research Discovery by Integrating Recommenders with Scientometrics*. Springer Nature (forthcoming).

> Menon, N. (2026). broken-proxies-endometriosis-analysis (v1.0.0) [Data set and code]. Zenodo. https://doi.org/10.5281/zenodo.22778879
