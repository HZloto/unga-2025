# Section 4C — P1 Trends: Internal Alignment (2025 Report)

## Data Source & Status

> **Status**: Full analysis complete from local canonical CSVs. All numbers QC'd.  
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
2025 had ~192 GA resolutions vs ~95 in 2024 (avg votes per country: 175 vs 88). This is NOT the primary driver of the decline: among 143 countries with high participation in both years, the average P1 change was −4.0 — actually worse than the overall −3.3. The additional resolutions exposed more fracture points but the decline is substantive, not mechanical.

### Critical Context: What P1 Actually Measures
**P1 (Pillar 1 Score) is NOT simply Yes%.** P1 uses a **4-year rolling window** that measures how internally consistent a country's voting is over time. Key evidence:
- Global Yes% actually **increased** from 78.8% in 2024 to 88.0% in 2025 — yet P1 went *down*.
- The correlation between P1 change and Yes% change across all countries is **−0.001** (essentially zero).
- 81 countries cast zero "No" votes in 2025 yet their P1 scores range from 43.7 (LBR) to 100.0 (STP).
- **18 of 24 "big mover" countries saw their Yes% INCREASE while their P1 DECREASED** — the "Yes% up / P1 down" paradox.

The mechanism: because the rolling window includes 2022–2025, a country that voted on ~95 resolutions in 2023–2024 now has its 192-resolution 2025 voting record compared against that historical baseline. Even if the country voted "Yes" more in 2025, the *new resolutions* introduced topics where its voting pattern differs from its historical norm, reducing internal consistency. **The writer must explain this to readers** or the declining P1 scores will appear contradictory given the rising consensus.

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

P1 dropped from 23.1 to **0.0** (the absolute floor). ARG now votes No on 54% of resolutions it participates in, with 37 absences on top. Its voting profile is now more oppositional than Israel (ISR: P1=59.5, 98 No votes, 47 absent; ARG: P1=0.0, 84 No votes, 37 absent). ARG's zero score means it is the single least internally consistent country in the entire dataset.

### 2.3 Syria's Post-Assad Transition

P1 dropped from 70.1 to 51.9 (−18.1). The regime change shifted voting: only 1 "No" vote in 2025 (vs 13 in 2024), but 99 absences and 7 abstentions. Syria is now less consistently aligned with any established bloc.

### 2.4 Other Notable Decliners

| Country | P1 Change | Key Driver |
|---------|-----------|------------|
| MDG | −30.2 | Participation collapse (81→11 votes) — SPOTTY |
| CMR | −20.7 | Yes% actually increased; P1 decline likely from changed resolution mix |
| VCT | −21.3 | Participation collapse (80→16 votes) — SPOTTY |
| DMA | −22.0 | Small sample amplification (28→48) |
| SWZ | −19.1 | Increased participation + more abstentions |
| BRN | −15.3 | Full participation both years; genuine shift |
| PRY | −11.1 | Continued rightward foreign policy shift |

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

## 3. Driver Classification: Leadership vs. Spotty vs. External

### 3.1 Leadership / Policy Shifts (24 candidates)
Countries with >10pt P1 change AND >5pp Yes% change while maintaining >30 votes in both years. Most significant:
- **USA** (−26.8): Trump administration opposition stance — Yes% and P1 both collapsed
- **ARG** (−23.1): Milei continuation of anti-multilateral pivot — Yes% and P1 both collapsed
- **SYR** (−18.1): Post-Assad regime change — Yes% UP (+18.4pp) but P1 DOWN (paradox: new government votes Yes more but inconsistently vs. historical pattern)
- **PRY** (−11.1): Continued Paraguay rightward shift — Yes% DOWN (−6.8pp) and P1 DOWN
- **BRA** (+9.1): Lula multilateralism solidified — both Yes% and P1 rose

### 3.1b The "Yes% UP / P1 DOWN" Paradox (18 countries)
**This is the most critical pattern a writer must explain.** 18 of the 24 big-mover countries *increased* their Yes% but saw P1 *decline*. Examples:

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

**Root cause**: P1's 4-year rolling window penalizes countries that changed voting behavior, even if they changed *toward* the majority. The doubled resolution volume in 2025 amplified this by introducing many topics where even traditionally pro-majority countries (CHN, PAK, CUB) had historical No/Abstain records.

**Writer note**: This paradox explains why the global P1 declined despite rising consensus. It is NOT a data error — it is a feature of the internal consistency metric.

### 3.2 Spotty Voting (6 candidates)
Countries with <50 votes in either year AND >5pt P1 change:
- **MDG**: 81→11 votes (−30.2 P1) — delegation barely present
- **VCT**: 80→16 votes (−21.3 P1) — severely reduced attendance
- **DMA**: 28→48 votes (−22.0 P1) — small sample noise
- **STP**: 35→12 votes (+94.1 P1) — "perfect" score artifact
- **SSD**: 19→56 votes (+36.6 P1) — improved from zero base
- **BOL**: 91→40 votes (−14.5 P1) — sharply reduced participation

### 3.3 Volume Effect
The ~2× resolution increase is NOT the primary cause of P1 declines *through participation mechanics*. Among 143 high-participation countries, avg P1 change = −4.0 (worse than overall −3.3). However, **the volume increase IS the primary driver through the consistency mechanism**: the additional 97 resolutions introduced new topic areas (40 new topic tags!) where countries had no historical voting record, mechanically reducing their rolling-window consistency score. This is the deeper explanation for the paradox above.

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
| DEV. & TRANSFER OF TECHNOLOGY | 57.7% | 94.1% | +36.4pp |
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
- **DISCRIMINATION**: +0.9pp (92.1% → 93.0%) — continued mild consensus growth, consistent with the 2024 report's observation that this was a gaining category.

**Writer note**: The declining topics (PUBLIC FINANCE −11.9pp, POLLUTION −9.8pp, MINERAL RESOURCES −9.8pp) are all relatively small-volume tags. The largest-volume topics (HUMAN RIGHTS, INTERNATIONAL RELATIONS, MAINTENANCE OF PEACE AND SECURITY) all show modest changes within ±3pp, suggesting the broad thematic consensus held steady while niche topics fragmented.

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

These are all **North-South divide issues** where Western states vote No as a bloc (~50-56 countries) against Global South majorities (116-125 Yes). This is a structurally different kind of divisiveness than Ukraine/Iran — it reflects a permanent ideological cleavage rather than crisis-driven polarization. None of these are Ukraine or Israel resolutions.

**CSV**: `10_p1_divisive_resolutions_2025.csv`

---

## 6. Pairwise Alignment / Alliance Patterns

### 6.1 The US Isolation Effect

The US moved *dramatically away from every partner* in the dataset. All top 10 most-diverging country pairs involve the USA:

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

Even Israel (the closest remaining partner) saw a −0.174 decline. The US is now *negatively correlated* with every single NATO ally.

### 6.2 Paradoxical Convergence with Adversaries

Because Western allies maintained similar positions while the US moved into wholesale opposition, these allies now show *increased similarity with China, Russia, Iran, and North Korea*:

| Pair | Sim Change | Note |
|------|-----------|------|
| FSM-PRK | +0.773 | FSM moved from US orbit |
| GBR-IRN | +0.699 | GBR didn't change; US reference point shifted |
| CZE-IRN | +0.698 | Same mechanism |
| CAN-PRK | +0.692 | Structural artifact |
| GBR-PRK | +0.666 | Structural artifact |

**This is a measurement artifact**: the allies didn't move; the US moved so far that the math now shows convergence with the opposite bloc.

### 6.3 Argentina and Israel Cluster

The only countries that moved *toward* the US (or at least diverged less) are MDG (+0.169, but spotty), VCT (+0.114, spotty), STP (+0.082, artifact), and SYR (+0.034). Argentina still diverged from the US (−0.235) due to its own unique posture.

**CSVs**: `07_p1_pairwise_biggest_shifts.csv`, `08_p1_us_alliance_shifts.csv`, `08b_p1_bloc_alliance_shifts.csv`, `14_p1_alliance_pattern_shifts.csv`

---

## 7. Regional Patterns

| Region | Avg P1 2024 | Avg P1 2025 | Change |
|--------|-------------|-------------|--------|
| Northern America | 70.8 | 52.9 | **−17.9** |
| Africa (Northern) | 85.4 | 77.8 | −7.6 |
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
- **Northern America** (−17.9): Entirely driven by USA's collapse. Canada also declined modestly.
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
| 12 | `12_p1_leadership_change_candidates.csv` | 24 countries flagged as policy-driven shifts |
| 13 | `13_p1_spotty_voting_candidates.csv` | 6 countries flagged as participation-driven |
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
2. **Resolution volume doubled**: 192 vs ~95. This is controlled for in the analysis — high-participation countries show the same (or worse) decline.
3. **Topic tags are LLM-generated**: 40 new topics appeared from GPT-4o-mini tagging. Only 1 topic dropped. Tag proliferation may reflect finer grain rather than substantive change.
4. **STP P1=100.0**: Artifact of 12 votes, all Yes. Flag as footnote.
5. **ARG P1=0.0**: Genuine — reflects voting against the majority on every dimension. ISR P1=59.5 (not 15.2 as in stale data).
6. **2026 data exists** (180 countries, 4 resolutions) — excluded from all analysis as partial year.
7. **Pairwise convergence artifacts**: Western allies appearing to converge with China/Russia is a structural effect of the US moving, not actual alliance shifts.
8. **P1 rolling window**: The 4-year rolling mechanism means P1 measures *consistency with historical self*, not alignment with majority. This causes the counterintuitive "Yes% up / P1 down" pattern seen in 18 countries. The writer MUST explain this or the numbers will confuse readers.

---

## 11. Chart Recommendations

1. **Line chart**: P1 world average 2000–2025 with 3yr rolling and trend (update existing chart style)
2. **Bar chart**: Top 15 biggest P1 drops AND gains (label spotty/policy/artifact)
3. **Scatter**: Participation change % vs P1 change (with labeled outliers)
4. **Grouped bar**: Topic Yes% shifts — top 5 declining + top 5 growing
5. **Dot plot / dumbbell**: US pairwise similarity with 15 key partners (2024 vs 2025)
6. **Regional bar chart**: P1 by region, 2024 vs 2025
7. **Heatmap**: Resolution × country vote for top 10 divisive resolutions
8. **Small multiples / sparklines**: P1 history 2015–2025 for USA, ARG, SYR, BRA, ISR, GBR, CHN
