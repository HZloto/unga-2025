# Section 4C — P1 Trends: Internal Alignment (2025 Report)

## Chart Data — P1 World Trend (2000–2025)

Use this table to recreate the world-trend chart for Pillar 1 in the future.
- `average_p1` = raw yearly world average
- `smoothed_3y_rolling` = centered 3-year rolling average from `01_p1_world_avg_trend.csv`
- `trendline_linear` = linear trendline fitted on `average_p1` for 2000–2025
- For charting: plot the smoothed series only where a value is present; 2025 is blank because a centered 3-year rolling average is not available for the endpoint

| Year | average_p1 | smoothed_3y_rolling | trendline_linear |
|------|------------|---------------------|------------------|
| 2000 | 65.99 | 73.47 | 75.51 |
| 2001 | 79.42 | 74.17 | 75.29 |
| 2002 | 77.09 | 79.24 | 75.08 |
| 2003 | 81.21 | 77.74 | 74.86 |
| 2004 | 74.92 | 78.10 | 74.64 |
| 2005 | 78.16 | 73.90 | 74.43 |
| 2006 | 68.61 | 72.89 | 74.21 |
| 2007 | 71.89 | 73.18 | 74.00 |
| 2008 | 79.04 | 76.69 | 73.78 |
| 2009 | 79.14 | 77.14 | 73.57 |
| 2010 | 73.25 | 72.97 | 73.35 |
| 2011 | 66.52 | 67.19 | 73.14 |
| 2012 | 61.81 | 69.39 | 72.92 |
| 2013 | 79.84 | 71.97 | 72.70 |
| 2014 | 74.26 | 75.12 | 72.49 |
| 2015 | 71.25 | 73.64 | 72.27 |
| 2016 | 75.42 | 74.53 | 72.06 |
| 2017 | 76.92 | 75.11 | 71.84 |
| 2018 | 72.98 | 73.48 | 71.63 |
| 2019 | 70.53 | 69.78 | 71.41 |
| 2020 | 65.82 | 62.86 | 71.20 |
| 2021 | 52.24 | 61.70 | 70.98 |
| 2022 | 67.03 | 65.26 | 70.76 |
| 2023 | 76.51 | 73.94 | 70.55 |
| 2024 | 78.29 | 76.59 | 70.33 |
| 2025 | 74.98 |  | 70.12 |

## Data Source & Status

> **Status**: Full descriptive analysis complete from local canonical CSVs. Core headline figures and tables below were checked against the generated output CSVs; causal labels are treated as heuristic screens unless separately sourced.  
> **Date**: 2026-03-25  
> **Script**: `analysis/4C/p1_section4c_analysis.py`  
> **Data sources**: `data/annual_scores (4).csv`, `data/pairwise_similarity_yearly (4).csv`, `data/topic_votes_yearly (4).csv`, `data/un_votes_with_sc (1).csv`  
> **Previous (stale) outputs**: `analysis/4C/legacy/`

---

## 1. Key Metric — World Average P1

**The world average internal alignment declined in 2025, dropping from 78.3 in 2024 to 75.0 in 2025 — a −3.3 point decrease.** This reverses the steady recovery since the 2021 nadir (52.2) and represents the first decline since 2021. The drop is nearly double what the stale data suggested (−1.7), making it the most significant reversal in the post-2021 recovery period.

| Year | World Avg P1 | Change | Countries | Avg Votes/Country |
|------|-------------|--------|-----------|-------------------|
| 2020 | 65.82 | −4.71 | 193 | 92 |
| 2021 | 52.24 | −13.58 | 193 | 79 |
| 2022 | 67.03 | +14.79 | 192 | 81 |
| 2023 | 76.51 | +9.48 | 192 | 80 |
| 2024 | 78.29 | +1.78 | 191 | 88 |
| **2025** | **74.98** | **−3.31** | **191** | **175** |

### Key Metric Box
> **−3.3 points** decrease in world average internal alignment (78.3 → 75.0)

### Critical Context: Resolution Volume Doubled
2025 had 192 GA/ES resolutions vs 95 in 2024 (avg votes per country: 175 vs 88). This is NOT just a participation artifact. Using a transparent high-participation screen for countries with at least 80 votes in 2024 and at least 160 in 2025, the average P1 change is **−3.8 across 158 countries** — still worse than the overall −3.3. The added resolutions exposed more fracture points, but the decline is substantive, not merely mechanical.

### Critical Context: What P1 Actually Measures
**P1 (Pillar 1 Score) is NOT simply Yes%.** P1 uses a **4-year rolling window** that measures how internally consistent a country's voting is over time. Key evidence:
- Global Yes% actually **increased** from 78.9% in 2024 to 88.0% in 2025 — yet P1 went *down*.
- The correlation between P1 change and Yes% change across all countries is **−0.001** (essentially zero).
- 81 countries cast zero "No" votes in 2025 yet their P1 scores range from 43.7 (LBR) to 100.0 (STP).
- **18 of the 24 countries in the profile-shift screen below saw their Yes% INCREASE while their P1 DECREASED** — the "Yes% up / P1 down" paradox.

The mechanism: because the rolling window includes 2022–2025, a country that voted on ~95 resolutions in 2023–2024 now has its 192-resolution 2025 voting record compared against that historical baseline. Even if the country voted "Yes" more in 2025, the *expanded issue mix* can still pull it away from its own recent voting pattern, reducing internal consistency. **The writer should explain this clearly** or the declining P1 scores will appear contradictory given the rising consensus.

**CSV**: `01_p1_world_avg_trend.csv`

---

## 2. Country-Level Drivers of Change

### 2.1 The US Opposition Pivot

The dominant story. The US P1 score plunged from 72.0 to 45.2 (−26.8 points):

| | 2024 | 2025 |
|---|---|---|
| Yes votes | 32 | 10 |
| No votes | 51 | 174 |
| Abstain | 11 | 8 |
| Total resolutions | 94 | 192 |
| P1 Score | 72.0 | 45.2 |
| Yes % | 34.0% | 5.2% |

The US voted "No" on 90.6% of resolutions in 2025 — up from 54.3% in 2024. Every topic category shows a collapse in Yes% (see output 15 for full detail):
- COMPUTER SCIENCE AND TECHNOLOGY: 100% → 0%
- WILDLIFE: 100% → 0%
- WATER: 100% → 0%
- ENERGY RESOURCES: 100% → 0%
- HUMAN RIGHTS: 35% → 10%
- INTERNATIONAL RELATIONS: 36% → 8%
- MAINTENANCE OF PEACE AND SECURITY: 33% → 11%

### 2.2 Argentina's Continued Collapse

P1 dropped from 23.1 to **0.0** (the absolute floor). ARG now votes No on 54% of resolutions it participates in, with 37 absences on top. Its voting profile is now more oppositional than Israel (ISR: P1=59.5, 98 No votes, 47 absent; ARG: P1=0.0, 84 No votes, 37 absent). In P1 terms, ARG is the single least internally consistent country in the 2025 dataset.

### 2.3 Syria's Sharp Voting Reset

P1 dropped from 70.1 to 51.9 (−18.1). The data show a sharp profile reset: only 1 "No" vote in 2025 (vs 13 in 2024), but 99 absences and 7 abstentions. Syria is now less consistently aligned with any established bloc. If the writer wants to connect this to domestic political change, that context should be sourced separately.

### 2.4 Other Notable Decliners

| Country | P1 Change | Key Driver |
|---------|-----------|------------|
| MDG | −30.2 | Participation collapse (81→11 votes) — SPOTTY |
| CMR | −20.7 | Large profile shift in the data; Yes% increased sharply, so the decline is not a simple attendance story |
| VCT | −21.3 | Participation collapse (80→16 votes) — SPOTTY |
| DMA | −22.0 | Small sample amplification (28→48) |
| SWZ | −19.1 | Profile shift with higher participation; interpret cautiously without external sourcing |
| BRN | −15.3 | Full participation both years; clear voting-pattern shift in the data |
| PRY | −11.1 | Lower Yes share plus higher No count; external political framing should be sourced separately |

### 2.5 Gainers

| Country | P1 Change | Key Factor |
|---------|-----------|------------|
| STP | +94.1 | ARTIFACT: only 12 votes cast, all Yes |
| SSD | +36.6 | Tripled participation (19→56) from near-zero base |
| LBR | +16.9 | Doubled participation + maintained high Yes% |
| COM | +14.7 | Major increase (71→165 votes) |
| PNG | +14.4 | Doubled participation (92→181) |
| ZMB | +13.1 | Tripled participation (67→160) |
| BRA | +9.1 | 183 Yes votes out of 192 (95.3%), zero No votes |
| MMR | +8.5 | 186 Yes, 2 abstains, zero No — strong Global South alignment |

**Note**: COD (Congo DR) appears as a gainer in the CSV but has **NaN P1 in 2024** (not in the annual_scores that year), so it cannot be compared year-over-year. Its 2025 P1 of 75.6 is a new entry, not a gain.

**CSVs**: `02_p1_country_shifts_2024_2025.csv`, `03_p1_big_movers.csv`, `12_p1_leadership_change_candidates.csv`, `13_p1_spotty_voting_candidates.csv`

---

## 3. Heuristic Classification: Profile Shift vs. Spotty vs. External Context

### 3.1 Use This as a Heuristic Screen, Not a Causal Model
`12_p1_leadership_change_candidates.csv` is a **screening file**, not proof of leadership change. It flags countries with:
- `|P1 change| > 10`
- `|Yes% change| > 5pp`
- at least `30` votes in both years

This identifies **24 countries with major voting-profile shifts**. It is useful for writers because it narrows the set of countries that changed most, but any reference to elections, leadership change, or diplomatic realignment should be sourced separately.

### 3.1a Large Profile-Shift Cases (24 flagged countries)
Most useful examples for writers:
- **USA** (−26.8): the clearest case of abrupt movement into wholesale opposition; both Yes% and P1 collapsed
- **ARG** (−23.1): continued movement into a highly oppositional voting profile; both Yes% and P1 fell again
- **SYR** (−18.1): Yes% rose sharply (+18.4pp) while P1 fell, showing a strong reset relative to Syria's own recent pattern
- **PRY** (−11.1): Yes% fell (−6.8pp) and No votes rose substantially, marking a clear profile shift
- **BRA** (+9.1): not in the >10pt screen, but still a useful counterexample because both Yes% and P1 rose

### 3.1b The "Yes% UP / P1 DOWN" Paradox (18 countries)
**This is the most critical pattern a writer must explain.** 18 of the 24 profile-shift candidates *increased* their Yes% but saw P1 *decline*. Examples:

| Country | P1 Change | Yes% Change | Interpretation |
|---------|-----------|-------------|----------------|
| CHN | −11.7 | +14.7pp | Voted Yes more in 2025 but on topics where it historically voted No/Abstain |
| CHE | −10.5 | +22.2pp | Switzerland voted Yes much more but broke from its usually cautious historical pattern |
| BLR | −14.2 | +14.1pp | Belarus voted Yes more but on topics where its historical record was different |
| PAK | −13.8 | +13.4pp | Same mechanism — new resolutions exposed historical inconsistency |
| EGY | −12.6 | +9.0pp | Egypt's Yes% rose but not on the same topic mix |
| PRK | −12.9 | +19.2pp | North Korea voted Yes far more but its historical opposition baseline dragged P1 down |
| CUB | −12.3 | +12.0pp | Same pattern — Cuba's increased Yes broke from historical norms |
| FSM | −10.6 | +22.6pp | Micronesia shifted dramatically toward Yes but historically voted with the US |

**Root cause**: P1's 4-year rolling window penalizes countries that changed voting behavior, even if they became more **Yes-heavy** in 2025. The doubled resolution volume amplified this by introducing many more topic tags and testing countries against a broader issue mix than in 2024.

**Writer note**: This paradox explains why the global P1 declined despite rising consensus. It is NOT a data error — it is a feature of the internal consistency metric.

### 3.2 Spotty Voting (6 candidates)
Countries with <50 votes in either year AND >5pt P1 change:
- **MDG**: 81→11 votes (−30.2 P1) — delegation barely present
- **VCT**: 80→16 votes (−21.3 P1) — severely reduced attendance
- **DMA**: 28→48 votes (−22.0 P1) — small sample noise
- **STP**: 35→12 votes (+94.1 P1) — "perfect" score artifact
- **SSD**: 19→56 votes (+36.6 P1) — improved from zero base
- **BOL**: 91→40 votes (−14.5 P1) — sharply reduced participation; despite appearing in the profile-shift screen, this case should be treated as participation-sensitive first

### 3.3 Volume Effect
The ~2× resolution increase is NOT the primary cause of P1 declines *through participation mechanics*. Using the transparent high-participation screen above (`>=80` votes in 2024 and `>=160` in 2025), the average P1 change is `−3.8` across `158` countries, still worse than the overall `−3.3`. However, **the larger 2025 agenda does matter through the consistency mechanism**: the additional resolutions and 40 new topic tags expanded the issue mix and increased the number of ways countries could diverge from their own recent voting pattern. That is the deeper explanation for the paradox above.

**CSVs**: `12_p1_leadership_change_candidates.csv`, `13_p1_spotty_voting_candidates.csv`, `04_p1_participation_analysis.csv`

---

## 4. External Drivers — Theme-Level Shifts

### 4.1 Topics with Declining Consensus

| Theme | Yes% 2024 | Yes% 2025 | Change |
|-------|-----------|-----------|--------|
| PUBLIC FINANCE | 95.7% | 83.8% | −11.9pp |
| POLLUTION | 95.3% | 85.5% | −9.8pp |
| MINERAL RESOURCES | 99.5% | 89.7% | −9.8pp |
| WATER | 98.8% | 93.8% | −5.0pp |
| TRADE RELATED FINANCE | 98.4% | 94.0% | −4.4pp |

### 4.2 Topics with Growing Consensus

| Theme | Yes% 2024 | Yes% 2025 | Change |
|-------|-----------|-----------|--------|
| ENERGY RESOURCES | 58.9% | 95.5% | +36.6pp |
| DEVELOPMENT AND TRANSFER OF TECHNOLOGY AND PROMOTION OF SCIENCE | 57.7% | 94.1% | +36.4pp |
| SOCIAL CONDITIONS AND EQUITY | 71.1% | 91.6% | +20.4pp |
| ECONOMIC THEORY | 71.5% | 91.4% | +19.9pp |
| SOCIAL DEVELOPMENT | 75.3% | 93.6% | +18.3pp |

### 4.3 Topic Landscape Change
- **40 new topics in 2025** (vs. only 1 dropped from 2024: INTERNATIONAL TRADE LAW)
- **81 total topics in 2025** vs. 42 in 2024 — reflecting the doubled resolution volume and finer-grained LLM tagging
- **Highest-vote new topics**: CULTURE (1,332 votes, 90.8% Yes), HEALTH (1,189 votes, 98.2% Yes), AGRICULTURAL ECONOMICS (1,081 votes, 90.5% Yes)
- **Most divisive new topic**: CRIME AND CRIMINAL JUSTICE (77.2% Yes), SETTLEMENT PLANNING (83.0% Yes)

### 4.4 Corrections from 2024 Report Context
The 2024 report highlighted these topics — here's how they changed in the fresh data:
- **DISARMAMENT AND MILITARY QUESTIONS**: Still present in 2025 (7,411 votes, 83.8% Yes, +3.2pp from 2024). NOT absent as the stale analysis suggested.
- **PROTECTION OF REFUGEES AND DISPLACED PERSONS**: Went UP slightly (+1.6pp, 82.9% → 84.5%), NOT down −18pp as stale data claimed.
- **DISCRIMINATION**: +16.6pp (69.5% → 86.1%) — a much larger consensus gain than the stale analysis suggested.
- **HUMAN RIGHTS**: +17.9pp (69.6% → 87.5%) — one of the largest high-volume gains in the entire file.
- **INTERNATIONAL RELATIONS**: +8.3pp (75.9% → 84.2%) — another large-volume gain rather than a flat result.

**Writer note**: The declining topics (PUBLIC FINANCE −11.9pp, POLLUTION −9.8pp, MINERAL RESOURCES −9.8pp) are all relatively small-volume tags. But the largest-volume topics did **not** stay flat: HUMAN RIGHTS (+17.9pp), INTERNATIONAL RELATIONS (+8.3pp), and MAINTENANCE OF PEACE AND SECURITY (+4.1pp) all rose. The right framing is therefore: **global Yes-consensus strengthened across many major themes even as countries became less internally consistent relative to their own recent voting history.**

**CSVs**: `05_p1_topic_alignment_changes.csv`, `06_p1_topic_new_dropped.csv`

---

## 5. Most Divisive Resolutions in 2025

| Resolution | Subject | Yes | No | Abs | Non-Yes% |
|---|---|---:|---:|---:|---:|
| A/RES/80/222 | Human rights in Iran | 78 | 27 | 64 | 53.8% |
| A/RES/80/223 | Human rights in occupied Ukraine | 79 | 16 | 73 | 53.0% |
| A/RES/80/80 | Israeli Practices Committee | 88 | 19 | 64 | 48.5% |
| A/RES/ES-11/7 | Peace in Ukraine | 93 | 18 | 65 | 47.2% |
| A/RES/ES-11/8 | Path to peace (Ukraine) | 93 | 8 | 73 | 46.6% |
| A/RES/ES-11/9 | Return of Ukrainian children | 91 | 12 | 57 | 43.1% |
| A/RES/80/189 | Human Rights Council report | 114 | 7 | 59 | 36.7% |
| A/RES/80/45 | Nuclear disarmament follow-up | 112 | 45 | 18 | 36.0% |
| A/RES/80/24 | Nuclear disarmament | 114 | 44 | 19 | 35.6% |
| A/RES/79/292 | IDPs from Abkhazia, Georgia | 107 | 9 | 49 | 35.2% |

**Key patterns**: The top 6 most divisive resolutions (by non-Yes%) are split between Ukraine (3) and Israel-Palestine/Iran (3). Nuclear disarmament resolutions feature at positions 8–9.

However, **a different pattern emerges when ranked by absolute No votes** — the North-South divide:

| Resolution | No Votes | Subject |
|---|---:|---|
| A/RES/80/209 | 56 | Human rights and unilateral coercive measures |
| A/RES/80/208 | 55 | Promotion of a democratic and equitable international order |
| A/RES/80/205 | 55 | Human rights and cultural diversity |
| A/RES/80/194 | 53 | Use of mercenaries |
| A/RES/80/206 | 53 | Equitable geographical distribution in treaty bodies |
| A/RES/80/20 | 52 | No first placement of weapons in outer space |
| A/RES/80/154 | 52 | Eradicating rural poverty / 2030 Agenda |
| A/RES/80/192 | 51 | Combating glorification of Nazism |
| A/RES/79/293 | 51 | International Day against Unilateral Coercive Measures |

These are best read as **North-South divide issues** where Western states often vote No as a bloc (~50-56 countries) against Global South majorities (116-125 Yes). This is a different kind of divisiveness than Ukraine/Iran: less crisis-driven and more reflective of recurring ideological cleavage. None of these are Ukraine or Israel resolutions.

**CSV**: `10_p1_divisive_resolutions_2025.csv`

---

## 6. Pairwise Alignment / Alliance Patterns

### 6.1 The US Isolation Effect

The US moved *dramatically away from almost every partner* in the dataset. All top 10 most-diverging country pairs involve the USA:

| Partner | Sim Change | 2024→2025 |
|---------|-----------|-----------|
| USA-CAN | −1.111 | 0.536 → −0.575 |
| USA-CZE | −1.095 | 0.583 → −0.512 |
| USA-AUS | −1.062 | 0.472 → −0.590 |
| USA-GBR | −1.051 | 0.573 → −0.478 |
| USA-NLD | −1.050 | 0.447 → −0.603 |
| USA-DEU | −1.021 | 0.469 → −0.552 |
| USA-JPN | −1.000 | 0.340 → −0.660 |
| USA-UKR | −1.000 | 0.493 → −0.507 |
| USA-FRA | −0.987 | 0.478 → −0.509 |
| USA-ISR | −0.174 | 0.833 → 0.658 |

Even Israel (the closest remaining partner) saw a −0.174 decline. The US is now *negatively correlated* with every single NATO ally. The only positive shifts versus the US are small and concentrated in low-confidence or unusual cases discussed below.

### 6.2 Paradoxical Convergence with Adversaries

Because the US moved into wholesale opposition while many other countries stayed closer to their prior patterns, several Western countries now show *increased pairwise similarity with China, Russia, Iran, and North Korea*:

| Pair | Sim Change | Note |
|------|-----------|------|
| FSM-PRK | +0.773 | FSM moved from US orbit |
| GBR-IRN | +0.699 | GBR didn't change; US reference point shifted |
| CZE-IRN | +0.698 | Same mechanism |
| CAN-PRK | +0.692 | Structural artifact |
| GBR-PRK | +0.666 | Structural artifact |

**This is mostly a measurement artifact**: it does not necessarily mean those allies moved toward adversaries in substantive geopolitical terms. Much of the effect comes from the US moving sharply away from its previous alignment pattern.

### 6.3 Limited Movement Toward the US

The only countries that moved *toward* the US (or at least diverged less) are MDG (+0.169, but spotty), VCT (+0.114, spotty), STP (+0.082, artifact), and SYR (+0.034). Three of the four are low-confidence cases because they are spotty-voting or artifact-driven. Argentina still diverged from the US (−0.235) despite its highly oppositional posture.

**CSVs**: `07_p1_pairwise_biggest_shifts.csv`, `08_p1_us_alliance_shifts.csv`, `08b_p1_bloc_alliance_shifts.csv`, `14_p1_alliance_pattern_shifts.csv`

---

## 7. Regional Patterns

| Region | Avg P1 2024 | Avg P1 2025 | Change |
|--------|-------------|-------------|--------|
| Northern America | 70.8 | 52.9 | **−17.9** |
| Africa (Northern Africa) | 85.4 | 77.8 | −7.6 |
| Eastern Asia | 78.0 | 70.6 | −7.4 |
| Western Asia | 81.3 | 75.4 | −5.9 |
| Southern Asia | 84.7 | 78.9 | −5.8 |
| Latin America & Caribbean | 85.3 | 79.7 | −5.6 |
| South-eastern Asia | 87.5 | 82.5 | −5.1 |
| Central Asia | 85.1 | 80.8 | −4.3 |
| Western Europe | 72.8 | 69.4 | −3.4 |
| Northern Europe | 73.1 | 70.4 | −2.7 |
| Eastern Europe | 68.4 | 65.7 | −2.6 |
| Southern Europe | 70.4 | 68.9 | −1.5 |
| Oceania | 66.1 | 65.5 | −0.6 |
| Sub-Saharan Africa | 78.1 | 78.2 | **+0.0** |

**Key findings**:
- **Northern America** (−17.9): Primarily driven by the USA's collapse. Canada also declined moderately.
- **Every region except Sub-Saharan Africa declined.** This is a much more broad-based downturn than the stale data suggested.
- **Sub-Saharan Africa** was the only stable region (+0.0), but this masks a subregional bright spot: **Middle Africa** surged +10.7 (67.7 → 78.4), driven by COD (new entrant at 75.6), CAF (+7.6), TCD (+4.4). STP's +94.1 artifact is also in this group. This was partially offset by CMR's −20.7 decline.
- **Caribbean** was the worst-performing subregion in Latin America (−8.7), driven by spotty-voting island nations.
- **Northern Africa** dropped −7.6, driven by Algeria (−12.0), Libya (−12.2), and Egypt (−12.6) — all part of the "Yes% up / P1 down" paradox group.
- **European regions** showed relatively modest declines (−1.5 to −3.4), suggesting European voting blocs held together.
- **Southern Africa** dropped notably (−6.9), largely from SWZ's −19.1.

**CSVs**: `09_p1_regional_summary.csv`, `09b_p1_subregional_summary.csv`

---

## 8. Output Files Reference

| # | File | Description |
|---|---|---|
| 01 | `01_p1_world_avg_trend.csv` | World avg P1, 1946–2025, with YoY change and 3yr rolling |
| 02 | `02_p1_country_shifts_2024_2025.csv` | Every country's P1 2024 vs 2025 + vote breakdowns |
| 03 | `03_p1_big_movers.csv` | 32 countries with >10pt P1 swing |
| 04 | `04_p1_participation_analysis.csv` | Participation changes vs P1 changes |
| 05 | `05_p1_topic_alignment_changes.csv` | 82 topics: Yes% 2024 vs 2025 |
| 06 | `06_p1_topic_new_dropped.csv` | 40 new + 1 dropped topic |
| 07 | `07_p1_pairwise_biggest_shifts.csv` | Top 50 diverging + 50 converging pairs |
| 08 | `08_p1_us_alliance_shifts.csv` | USA pairwise with all 190 partners |
| 08b | `08b_p1_bloc_alliance_shifts.csv` | USA + CHN + RUS pairwise shifts |
| 09 | `09_p1_regional_summary.csv` | Broad region P1 summary |
| 09b | `09b_p1_subregional_summary.csv` | Subregion P1 summary |
| 10 | `10_p1_divisive_resolutions_2025.csv` | All 192 resolutions ranked by divisiveness |
| 11 | `11_p1_country_vote_profile_2025.csv` | Full 2025 profile for all 191 countries |
| 12 | `12_p1_leadership_change_candidates.csv` | 24 countries flagged by a heuristic profile-shift screen |
| 13 | `13_p1_spotty_voting_candidates.csv` | 6 countries flagged by a participation-sensitive screen |
| 14 | `14_p1_alliance_pattern_shifts.csv` | Per-country sim change vs USA, CHN, RUS, ISR |
| 15 | `15_p1_key_movers_topic_detail.csv` | Topic-level Yes% for 44 key countries |
| 16 | `16_p1_key_country_history.csv` | P1 history 2015–2025 for 23 key countries |
| 17 | `17_p1_resolution_vote_detail_2025.csv` | Per-resolution vote for 10 key countries |

---

## 9. Comparison with Stale Data

| Metric | Stale (old) | Fresh (new) | Difference |
|--------|-------------|-------------|------------|
| World avg P1 2025 | 76.6 | 75.0 | −1.6 |
| P1 change 2024→2025 | −1.7 | −3.3 | Nearly 2× worse |
| USA P1 2025 | 48.2 | 45.2 | −3.0 |
| USA P1 change | −23.9 | −26.8 | More extreme |
| Big movers (>10pt) | ~20 | 32 | More countries affected |
| Topics 2025 | 64 | 81 | More granular tagging |

**The stale data underestimated the severity of the 2025 decline.** The fresh data shows:
1. A more dramatic US collapse (−26.8 vs. −23.9)
2. A broader global decline affecting essentially all regions
3. More countries with large P1 shifts
4. Richer thematic coverage with 81 topics

---

## 10. Caveats & Validation Notes

1. **Vote arithmetic validated**: Yes + No + Abstain = Total holds for all 2024 and 2025 rows.
2. **Resolution volume doubled**: 192 vs 95. This is controlled for in the analysis — under a transparent high-participation screen (`>=80` votes in 2024; `>=160` in 2025), countries still show a similarly large average decline.
3. **Topic tags are LLM-generated**: 40 new topics appeared from GPT-4o-mini tagging. Only 1 topic dropped. Tag proliferation may reflect finer grain rather than substantive change.
4. **STP P1=100.0**: Artifact of 12 votes, all Yes. Flag as footnote.
5. **ARG P1=0.0**: Genuine in the dataset, but interpret it correctly: it means Argentina is maximally inconsistent relative to its own recent voting history, not that it voted "against the majority on every dimension." ISR P1=59.5 (not 15.2 as in stale data).
6. **2026 data exists** (180 countries, 4 resolutions) — excluded from all analysis as partial year.
7. **Pairwise convergence artifacts**: Western allies appearing to converge with China/Russia is a structural effect of the US moving, not actual alliance shifts.
8. **P1 rolling window**: The 4-year rolling mechanism means P1 measures *consistency with historical self*, not alignment with majority. This causes the counterintuitive "Yes% up / P1 down" pattern seen in 18 of the 24 profile-shift cases.
9. **Output 12 is heuristic**: `12_p1_leadership_change_candidates.csv` is a screening file for major voting-profile changes. It should not be cited as proof of leadership change unless supplemented with external reporting.

---

## 11. Chart Recommendations

1. **Line chart**: P1 world average 2000–2025 with 3yr rolling and trend (update existing chart style)
2. **Bar chart**: Top 15 biggest P1 drops AND gains (label spotty/profile-shift/artifact)
3. **Scatter**: Participation change % vs P1 change (with labeled outliers)
4. **Grouped bar**: Topic Yes% shifts — top 5 declining + top 5 growing
5. **Dot plot / dumbbell**: US pairwise similarity with 15 key partners (2024 vs 2025)
6. **Regional bar chart**: P1 by region, 2024 vs 2025
7. **Heatmap**: Resolution × country vote for top 10 divisive resolutions
8. **Small multiples / sparklines**: P1 history 2015–2025 for USA, ARG, SYR, BRA, ISR, GBR, CHN
