# Supabase Database — bilateral-countries-index

## Connection
- **URL**: stored in `.env` as `SUPABASE_URL`
- **Key**: stored in `.env` as `SUPABASE_KEY` (service_role key)
- Accessed via Supabase REST API (`/rest/v1/`)

## Tables Overview (12 tables, 2 RPC functions)

### 1. `annual_scores` — **11,568 rows**
The **core index table**. One row per country per year (1946–2025). 193 countries (ISO3 codes).
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| Country name | text | ISO3 code (e.g. "AFG", "USA") |
| Year | int | 1946–2025 |
| Pillar 1 Score | float | Raw score (0–100) |
| Pillar 2 Score | float | Raw score (0–100) |
| Pillar 3 Score | float | Raw score (0–100) |
| Total Index Average | float | Avg of 3 pillars |
| Overall Rank | int | Rank within year (1=best, ~191=worst) |
| Overall Rank Rolling Avg (3y) | float | 3-year rolling average of rank |
| Total Index Normalized | float | Same as Total Index Average currently |
| Pillar 1 Normalized | float | Normalized pillar 1 |
| Pillar 1 Rank | int | Rank for pillar 1 (nullable) |
| Pillar 2 Normalized | float | Normalized pillar 2 |
| Pillar 2 Rank | int | Rank for pillar 2 |
| Pillar 3 Normalized | float | Normalized pillar 3 |
| Pillar 3 Rank | int | Rank for pillar 3 |
| Yes Votes | int | Total yes votes that year |
| No Votes | int | Total no votes that year |
| Abstain Votes | int | Total abstentions that year |
| Total Votes in Year | int | Total resolutions voted on |
| created_at, updated_at | timestamp | |

**Interpretation**: Higher score = more aligned with UN General Assembly majority. Rank 1 = most aligned. Top-ranked countries tend to be small states that vote with the majority. Bottom-ranked include ISR, USA, RUS.

### 2. `pairwise_similarity_yearly` — **1,463,712 rows**
Cosine similarity of voting vectors between every country pair, per year (1946–2025).
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| Year | int | 1946–2025 |
| Country1_ISO3 | text | ISO3 code |
| Country2_ISO3 | text | ISO3 code |
| CosineSimilarity | float | Range: roughly -0.5 to 1.0 |
| created_at, updated_at | timestamp | |

**Key for dyad comparisons and "most aligned / most opposed" rankings.**

### 3. `topic_votes_yearly` — **652,288 rows**
Votes broken down by topic tag, per country per year (1946–2025). 100 unique topic tags.
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| Year | int | |
| Country | text | ISO3 code |
| TopicTag | text | e.g. "HUMAN RIGHTS", "DISARMAMENT AND MILITARY QUESTIONS" |
| YesVotes_Topic | int | |
| NoVotes_Topic | int | |
| AbstainVotes_Topic | int | |
| TotalVotes_Topic | int | |
| created_at, updated_at | timestamp | |

### 4. `un_votes_raw` — **7,327 rows** (GA only)
Raw resolution-level vote data. Each row = one resolution. Wide format with ~195 country columns.
| Column | Type | Notes |
|--------|------|-------|
| Council | text | Always "General Assembly" |
| Date | timestamp | Resolution date |
| Title | text | Full resolution title |
| Resolution | text | e.g. "A/RES/79/330" |
| tags | text | Comma-separated topic tags |
| TOTAL VOTES, NO-VOTE COUNT, ABSTAIN COUNT, NO COUNT, YES COUNT | int | Aggregate counts |
| Link | text | URL to UN Digital Library |
| token | text | Digital Library record ID |
| Scrape_Year | int | 1946–2026 |
| [country ISO3 columns] | text | Vote value: "YES", "NO", "ABSTAIN", null (no vote) |
| created_at, updated_at | timestamp | |

### 5. `un_votes_with_sc` — **10,107 rows** (GA + Security Council)
Same wide format as `un_votes_raw` but includes Security Council resolutions in addition to GA.
Same 211 columns as `un_votes_raw`. Date range: 1946–present.

### 6. `country_classifications_2023` — **190 rows**
Country metadata / group memberships.
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| country_code | text | ISO3 |
| country_name | text | Full name |
| is_oecd | bool | OECD member |
| is_g20 | bool | G20 member |
| is_top_50_gdp | bool | Top 50 by GDP |
| is_bottom_50_gdp | bool | Bottom 50 by GDP |
| is_top_50_population | bool | Top 50 by population |
| is_bottom_50_population | bool | Bottom 50 by population |
| created_at, updated_at | timestamp | |

### 7. `un_country_region_mapping` — **246 rows**
Maps ISO3 country codes to UN regions. 14 regions.
| Column | Type | Notes |
|--------|------|-------|
| id | int | PK |
| ISO-alpha3 code | text | ISO3 |
| UN Region | text | e.g. "Northern Africa", "Western Europe", "Eastern Asia" |

**Regions**: Central Asia, Eastern Asia, Eastern Europe, Latin America and the Caribbean, Northern Africa, Northern America, Northern Europe, Oceania, South-eastern Asia, Southern Asia, Southern Europe, Sub-Saharan Africa, Western Asia, Western Europe.

### 8. `sc_items` — **399 rows**
Security Council agenda items / resolutions (1946–1968 so far).
| Column | Type | Notes |
|--------|------|-------|
| sc_item_id | uuid | PK |
| symbol_final | text | e.g. "S/RES/1(1946)" |
| symbol_draft | text | Draft symbol (nullable) |
| meeting_symbol | text | Meeting reference |
| meeting_date | date | 1946–1968 |
| agenda_item | text | Full agenda item text |
| is_substantive | bool | |
| outcome | text | |
| undl_record_ids | jsonb | Links to UN Digital Library |
| links | jsonb | Additional links |
| provenance_note | text | |
| created_at, updated_at | timestamp | |

### 9. `sc_votes` — **empty**
Placeholder for individual Security Council votes (not yet populated).

### 10. `sc_vetoes` — **empty**
Placeholder for Security Council veto records (not yet populated).

### 11. `model_sc_votes` — **empty**
Placeholder for modeled/predicted SC votes (not yet populated).

### 12. `scraper_logs` — **47 rows**
Logs for the data scraping pipeline. Tracks run status, records found/processed, errors.

## RPC Functions
- `add_country_column` — Adds a new country column to vote tables
- `remove_country_column` — Removes a country column from vote tables

## Key Relationships
- `annual_scores."Country name"` → ISO3 code → joins to all other tables
- `pairwise_similarity_yearly.Country1_ISO3 / Country2_ISO3` → ISO3
- `country_classifications_2023.country_code` → ISO3
- `un_country_region_mapping."ISO-alpha3 code"` → ISO3
- Vote encoding in raw tables: "YES" / "NO" / "ABSTAIN" / null

## Data Pipeline
- Data is scraped from the UN Digital Library (tracked in `scraper_logs`)
- Raw votes stored in `un_votes_raw` (GA only) and `un_votes_with_sc` (GA+SC)
- Aggregated into `annual_scores`, `pairwise_similarity_yearly`, and `topic_votes_yearly`
- Country metadata in `country_classifications_2023` and `un_country_region_mapping`
