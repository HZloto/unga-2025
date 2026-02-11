# Copilot Instructions — UNGA 2025 (3DL Data Driven Decision Lab)

## Project Purpose

This repository holds **extracts from the 3DL (Data Driven Decision Lab) UNGA voting database** — a bias-free, data-driven assessment of how countries vote in the United Nations General Assembly. The three CSV datasets in `data/` are downstream extracts from a scraping pipeline built by 3DL. The codebase focuses on **validating and QC-ing these extracts** before they are used in research or public reporting.

## Core Principle: Thoroughness Over Speed

**Data integrity is the #1 priority.** Every result surfaced from this data must be thoroughly tested and validated. Speed is explicitly *not* important — correctness, traceability, and surfacing discrepancies are.

When working with this data:
- **Always validate before trusting.** Run or write validation checks for any new data operation.
- **Surface every discrepancy** — never silently ignore anomalies. Flag them clearly with context so a human can assess.
- **Traceability is paramount.** Document the steps and reasoning behind every data decision so the chain from raw scrape → extract → result is auditable.
- **Only present results that have been QC'd.** If a check hasn't been run, say so explicitly.

## Upstream Pipeline: UN Digital Library Scraper

The CSVs in this repo are **downstream extracts** from a separate scraping + classification pipeline maintained by 3DL. Understanding this pipeline is essential for traceability.

### How the Data Is Produced
1. **Scraping** — Selenium + BeautifulSoup scrapes resolution voting records from the [UN Digital Library](https://digitallibrary.un.org). Each resolution yields per-country YES/NO/ABSTAIN votes, a title, date, and source link.
2. **Topic Tagging** — Resolution titles are classified using OpenAI GPT-4o-mini against the [UNBIS Thesaurus](https://metadata.un.org/thesaurus/?lang=en) hierarchy (Main Category → Subcategory → Specific Item). A resolution can receive **multiple tags** — this is why topic vote sums exceed annual totals.
3. **Geographic Tagging** — A dual-method approach: regex pattern matching for explicit country/region mentions, then LLM verification for implicit references. Countries are standardized to ISO 3166-1 alpha-2 in the scraper, but this repo's extracts use **ISO3 (alpha-3)** codes.
4. **Aggregation** — Raw per-resolution votes are aggregated into the three extract files: annual scores/ranks, pairwise cosine similarity, and per-topic vote breakdowns.

### Key Implications for This Repo
- **Tags are LLM-generated** — topic classifications come from GPT-4o-mini, not from official UN metadata. Keep this in mind when interpreting topic-level analysis.
- **Multi-tagging is by design** — a single resolution can map to multiple UNBIS tags at three hierarchy levels, causing intentional "double-counting" in topic vote totals.
- **Raw data has a different schema** — the upstream CSV (`UN_VOTING_DATA_RAW_WITH_TAGS_YYYY-MM-DD.csv`) has per-country vote columns, link URLs, and tag fields. The three files in this repo are pre-aggregated summaries.
- **The scraper repo also exposes a FastAPI `/report/{country_iso}` endpoint** that produces country reports (scores, allies, enemies, regional context) — our extracts feed into this.

## Repository Structure

```
data/                # Canonical input CSVs — read-only source of truth
validation/          # QC scripts and validation plan
analysis/            # Analysis scripts and outputs
.github/             # Copilot instructions (this file)
```

## Dataset Schemas

All data lives in `data/`.

| File | Rows | Key Columns | Grain |
|---|---|---|---|
| `annual_scores.csv` | 11,568 | `Country name`, `Year`, Pillar 1/2/3 Scores & Ranks, `Total Index Average`, `Overall Rank`, Yes/No/Abstain/Total Votes | One row per country per year |
| `pairwise_similarity_yearly.csv` | 1,463,712 | `Year`, `Country1_ISO3`, `Country2_ISO3`, `CosineSimilarity` | One row per **unidirectional** country pair per year |
| `topic_votes_yearly.csv` | 328,535 | `Year`, `Country`, `TopicTag`, `YesVotes_Topic`, `NoVotes_Topic`, `AbstainVotes_Topic`, `TotalVotes_Topic` | One row per country per topic per year |

### Known Data Characteristics (do not flag these as bugs)
- **Year 1964 is missing** from all three files — this is correct (UNGA Article 19 crisis; no recorded votes).
- **Topic vote totals exceed annual totals** — resolutions are tagged with multiple topics, so summing topic votes double-counts.
- **Pairwise pairs are unidirectional** — each pair (A, B) appears once, not as both (A, B) and (B, A).
- **37% of pairwise rows have zero similarity** — caused by countries not yet being UN members; not a data error.
- **Pillar 1 Rank has ~11% nulls**; Pillar 1 Score/Normalized have ~5% nulls.

## Validation Architecture

Validation scripts live in `validation/` and load CSVs from `data/` via `Path(__file__).parent.parent / "data"`.

| Script | Validates |
|---|---|
| `validation/validate_annual_scores.py` | Schema, completeness, score ranges, vote arithmetic (`Yes+No+Abstain == Total`), outliers (3σ), rank consistency |
| `validation/validate_pairwise_similarity.py` | ISO3 format, cosine similarity in [-1, 1], symmetry checks, zero-similarity analysis |
| `validation/validate_topic_votes.py` | Schema, topic tag consistency, vote arithmetic, per-topic distribution |
| `validation/validate_cross_files.py` | Year/country alignment across all three files, vote total reconciliation |
| `validation/validate_2025.py` | Focused validation on the latest year (2025) across all files |

Run any validator from the repo root:
```bash
python3 validation/validate_annual_scores.py
```

### Validation Script Conventions
- Each script uses a `separator(title)` helper for section headers.
- Checks print `✓` for pass, `❌` for fail, `⚠️` for warnings.
- Vote arithmetic identity: `Yes + No + Abstain == Total` must hold in every file that has vote columns.
- Outlier analysis uses 3σ bounds but only flags; values within valid domain ranges are acceptable.
- Random samples are seeded (`random_state=42`) for reproducibility.
- All scripts are standalone — they load CSVs via `Path(__file__).parent.parent / "data"` relative paths.

## Writing New Validation or Analysis Code

1. **Use pandas + numpy** — these are the only data dependencies.
2. **Load CSVs with `Path(__file__).parent.parent / "data"`** to keep scripts runnable from any working directory. Validation scripts go in `validation/`, analysis scripts go in `analysis/`.
3. **Always check vote arithmetic** (`Yes + No + Abstain == Total`) when touching vote data.
4. **Cross-reference country identifiers carefully**: `annual_scores` uses ISO3 codes in the `Country name` column; `pairwise_similarity` uses `Country1_ISO3`/`Country2_ISO3`; `topic_votes` uses `Country` (also ISO3). All files share 193 countries.
5. **Document findings inline** — print clear pass/fail/warning output. Follow the existing `separator()` + emoji pattern.
6. **When a discrepancy is found**, do not skip it. Print the affected rows, the expected vs. actual values, and a human-readable explanation.
7. **Update `validation/DATA_VALIDATION_PLAN.md`** after running new checks — mark items `[x]` (pass), `[!]` (pass with caveats), or `[ ]` (pending), and paste key results.

## Common Pitfalls
- Do not attempt to reconcile topic vote sums with annual totals and call it a bug — the multi-tagging of resolutions makes this expected.
- Pairwise similarity is not symmetric in the file — don't expect to find both (A→B) and (B→A).
- Web verification of votes against UN Digital Library is blocked by JS/CAPTCHA — note this limitation rather than failing silently.

## Agent Memory Log

**Every AI agent that works on this codebase must maintain this section.** It serves as shared persistent memory so any agent — current or future — has immediate access to (a) essential context and (b) the latest state of the project.

### Rules for Updating
1. **After any significant action** (new script, data finding, schema change, bug fix, failed approach), append an entry to the log below.
2. **Each entry** must include: date, a short summary, and files affected.
3. **Keep entries concise** — one to three lines each. Link to files or validation plan sections where details live.
4. **Never delete old entries** — they form an audit trail. Mark superseded entries with `[SUPERSEDED]` if a later entry replaces them.
5. **Read this log first** before starting work to avoid duplicating effort or re-investigating resolved issues.

### Log

| Date | Agent | Summary | Files / References |
|---|---|---|---|
| 2026-02-08 | AI Validation Agent | Initial validation of all three CSVs completed. All vote arithmetic passes. Year 1964 confirmed missing (Article 19 crisis). Pillar 1 Rank has ~11% nulls. 37% pairwise zero-similarity explained by pre-membership. No critical blocking issues. | `validation/validate_*.py`, `validation/DATA_VALIDATION_PLAN.md` |
| 2026-02-08 | AI Validation Agent | Cross-file consistency verified: 193 countries, 79 years (1946–2025 minus 1964) align across all files. Topic vote sums intentionally exceed annual totals due to multi-topic tagging. | `validation/validate_cross_files.py` |
| 2026-02-08 | AI Validation Agent | Web verification of random vote samples blocked by JS/CAPTCHA on UN Digital Library and Harvard Dataverse. Manual verification recommended for high-stakes publications. | `validation/DATA_VALIDATION_PLAN.md` §4 |
| 2026-02-10 | AI Agent | Created `.github/copilot-instructions.md` with project context, data schemas, validation architecture, conventions, and this agent memory log. | `.github/copilot-instructions.md` |
| 2026-02-10 | AI Agent | Added upstream pipeline section documenting scraper → LLM tagging → aggregation flow, UNBIS Thesaurus basis for topic tags, and implications (multi-tagging, LLM-generated classifications, ISO2→ISO3 conversion). | `.github/copilot-instructions.md` |
| 2026-02-10 | AI Agent | Restructured repo: CSVs renamed (dropped ` (1)` suffix) and kept in `data/`, validation scripts moved to `validation/`, empty `analysis/` created. All script paths updated and verified. | All files |
| 2026-02-11 | AI Agent | [SUPERSEDED by next entry] Generated `unga_2025_resolutions.csv` (33 resolutions) from sibling scraper repo raw data. | `analysis/generate_2025_resolutions_csv.py`, `analysis/unga_2025_resolutions.csv` |
| 2026-02-11 | AI Agent | Regenerated `unga_2025_resolutions.csv` from canonical source `data/un_votes_2025_processed.csv`. Now 192 GA resolutions × 200 cols (9 meta + 191 countries). AFG & VEN absent from source (zero-vote countries). Two-header-row format (ISO3 + full names). All vote arithmetic passes. 7 resolutions independently verified against UN press releases (GA/12693, GA/12686). | `analysis/generate_2025_resolutions_csv.py`, `analysis/unga_2025_resolutions.csv` |
| 2026-02-11 | AI Agent | Created `validate_online_crosscheck.py` — verifies 7 resolutions against 2 UN press releases (tallies + named country votes). All pass. Also updated `validate_2025_resolutions.py` for 191-country / 192-resolution CSV shape. | `validation/validate_online_crosscheck.py`, `validation/validate_2025_resolutions.py` |
| 2026-02-11 | AI Agent | Validated updated extracts (`annual_scores (2).csv`, `pairwise_similarity_yearly (2).csv`, `topic_votes_yearly (2).csv`) against `un_votes_2025_processed.csv`. All 18 critical checks pass. Key findings: (1) all 191 country vote counts match raw source exactly, (2) topic coverage increased from 39→64 topics vs legacy, (3) vote totals roughly doubled (legacy had ~half the 192 GA resolutions), (4) 18,130/18,528 pairwise similarity values changed accordingly, (5) vote arithmetic holds across all files. Legacy files confirmed as partial coverage. | `validation/validate_updated_vs_raw.py` |
