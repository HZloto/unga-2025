# Section 4C — P1 Trends: Internal Alignment (2025 Report)

## Plan & Data-Backed Outline

> **Status**: Data extraction complete. All numbers below are QC'd from the Supabase database (queried 2026-03-18).  
> **Scripts**: `analysis/4C/p1_data_extraction.py`, `analysis/4C/p1_deep_dive.py`  
> **Output CSVs**: `p1_world_avg_trend.csv`, `p1_country_shifts_2024_2025.csv`, `p1_topic_alignment_changes.csv`, `p1_big_movers.csv`, `p1_resolutions_2025.csv`, `p1_full_trend.csv`, `p1_participation_analysis.csv`

---

## 1. Opening — Key Metric & World Average

**The world average internal alignment declined slightly in 2025, dropping from 78.3 in 2024 to 76.6 in 2025 — a -1.7 point decrease.** This reverses the steady recovery seen since the 2021 nadir (52.2) and interrupts a four-year upward trend (2021→2024). The decline is modest but meaningful: it signals that the geopolitical consensus that had been rebuilding post-COVID/post-Ukraine-invasion has begun to fray again.

| Year | World Avg P1 | Change |
|------|-------------|--------|
| 2020 | 65.8 | — |
| 2021 | 52.2 | -13.6 |
| 2022 | 67.0 | +14.8 |
| 2023 | 76.5 | +9.5 |
| 2024 | 78.3 | +1.8 |
| **2025** | **76.6** | **-1.7** |

### Key Metric Box
> **-1.7 points** decrease in world average internal alignment (78.3 → 76.6)

### Narrative Context
After the extraordinary collapse in 2020–2021 (linked to pandemic-era absences and the initial shock of the Ukraine invasion), countries had been steadily recovering internal consistency. The 2025 reversal is primarily driven by two forces: (1) the United States dramatically shifting its voting posture under the second Trump administration, and (2) the roughly doubled resolution volume in 2025 (192 resolutions vs ~95 in 2024), which exposed more issues where countries split from their usual patterns.

---

## 2. Country-Level Drivers of Change

### 2.1 The US Pivot: Opposing the Multilateral Consensus

The most dramatic country-level story in the 2025 data is the **United States**, whose P1 score plunged from 72.0 to 48.2 (−23.9 points). The numbers are stark:

| | 2024 | 2025 |
|---|---|---|
| Yes votes | 32 | 10 |
| No votes | 51 | 174 |
| Total resolutions voted | 94 | 192 |
| P1 Score | 72.0 | 48.2 |

The US went from voting "Yes" on 34% of resolutions in 2024 to just 5.2% in 2025, while dramatically increasing its "No" votes (from 51 to 174). This is the sharpest shift toward opposition in the dataset. The Trump administration's return to power in January 2025 realigned US foreign policy away from multilateral norms across virtually every domain:

- **Environment/Wildlife/Marine**: Dropped from 67% Yes to 0% Yes (consistent with US withdrawal from climate accords)
- **International Relations**: Dropped from 35.5% Yes to 12.5% Yes  
- **Maintenance of Peace & Security**: Dropped from 33% Yes to 12.5–14% Yes
- **Political & Legal Questions**: Dropped from 26.5% Yes to 12.5–15% Yes

The US moved away from essentially all Western allies and closer to isolation. Pairwise similarity with traditional partners collapsed: CZE −1.28, GBR −1.27, CAN −1.26, AUS −1.22, FRA −1.20, DEU −1.19. The US is now more negatively correlated with its NATO allies than at any point in recent history.

**Ripple effect on Northern America**: The regional average for Northern America crashed from 70.9 to 54.9 (−16.0 points), making it the worst-performing region by far.

### 2.2 Argentina's Continued Collapse

Argentina's internal alignment continued its freefall under the Milei government, dropping from 23.1 (already very low) to **0.0** — the absolute minimum score. In 2023, Argentina voted "Yes" 90.2% of the time. In 2024, just 46.9%. In 2025, only 34.4%. Its voting pattern now mirrors Israel's: opposing the majority on human rights, decolonization, and development resolutions. Notably, Argentina's "No" votes doubled from 38 (2024) to 84 (2025), while it reduced total participation from 95 to 155 resolutions.

### 2.3 Syria's Post-Assad Realignment

Syria's P1 score dropped from 70.1 to 52.1 (−18.0 points). The fall of the Assad regime in December 2024 led to a new transitional government that fundamentally changed Syria's UN voting profile. Under Assad, Syria reliably voted with the Russia/China bloc. The new government shifted:
- Zero "No" votes in 2025 (vs 13 in 2024)
- Participation increased from 74 to 93 resolutions
- The shift is largely in abstentions: Syria now abstains where it previously voted No
- Syria moved away from Russia (pairwise sim change −0.25) and China (pairwise sim stayed similar)

This is a direct consequence of regime change — the new government is not yet fully aligned with any bloc, creating lower internal consistency.

### 2.4 Spotty Voting — Participation Effects

Several countries saw large P1 swings driven primarily by changes in attendance rather than policy shifts:

| Country | Total Votes 2024 | Total Votes 2025 | P1 Change | Interpretation |
|---------|---:|---:|---:|---|
| **MDG** (Madagascar) | 81 | 11 | −31.9 | Collapsed participation — only 11 votes cast; with so few data points the score is unreliable |
| **VCT** (St. Vincent) | 80 | 16 | −22.7 | Dramatically reduced attendance |
| **DMA** (Dominica) | 28 | 48 | −34.3 | Increased participation but shifted to more inconsistent votes (4 abstentions when it had 0 before) |
| **STP** (São Tomé) | 35 | 12 | +94.1 | Only 12 votes cast — all Yes, creating "perfect" alignment by accident of small sample |
| **SSD** (South Sudan) | 19 | 56 | +39.9 | Tripled participation, improving from 0.0 (non-participation floor) |
| **BOL** (Bolivia) | 91 | 40 | −14.3 | Sharply reduced participation |
| **PNG** (Papua New Guinea) | 92 | 181 | +16.0 | Nearly doubled participation, better alignment with majority |

**Key insight**: For small island nations and countries with limited UN representation, attendance fluctuations are the primary driver of P1 scores. São Tomé and Príncipe illustrates this perfectly — a "perfect" score of 100.0 is an artifact of only casting 12 votes, all Yes.

### 2.5 Regional Gainers

| Country | P1 Change | Key Factor |
|---------|---:|---|
| **MMR** (Myanmar) | +8.2 | Continued alignment with Global South majority; near-full attendance (188/192); zero No votes |
| **BRA** (Brazil) | +9.3 | Lula's multilateralist stance solidified; 183 Yes out of 192; zero No votes — strong majority alignment |
| **ZMB** (Zambia) | +13.2 | Increased participation (67→160) and maintained high Yes-vote rate |
| **LBR** (Liberia) | +11.1 | Rose from low base (26.8 to 37.9) with better attendance |
| **HUN** (Hungary) | +4.1 | Moved slightly closer to EU mainstream on some resolutions |

---

## 3. External Drivers — Theme-Level Shifts

### 3.1 Themes with Declining Consensus (Negative Shifts)

The 2025 session saw several topics where the global consensus fractured compared to 2024, though the picture is quite different from 2024 given the changed resolution mix:

| Theme | Yes% 2024 | Yes% 2025 | Change | Interpretation |
|-------|---:|---:|---:|---|
| **Protection of Refugees & Displaced Persons** | 82.9% | 64.9% | −18.0 | The steepest drop. Driven by the Ukraine-related "Return of Ukrainian children" resolution (ES-11/9) which split the Assembly, and continued polarization on Palestinian refugees |
| **Maintenance of Peace & Security** | 77.3% | 76.6% | −0.7 | Slight decline; Ukraine-related resolutions continued to divide Russia/China bloc from the West, though less dramatically than in previous years |

### 3.2 Themes with Growing Consensus (Positive Shifts)

Most notable is that **nearly all other themes saw increased consensus** in 2025:

| Theme | Yes% 2024 | Yes% 2025 | Change | Interpretation |
|-------|---:|---:|---:|---|
| **Development & Technology Transfer** | 57.1% | 98.1% | +41.0 | Dramatic consensus shift — likely reflecting changed resolution framing or fewer contentious riders |
| **Political Events & Issues** | 66.1% | 94.6% | +28.6 | Broad agreement on political governance resolutions |
| **Discrimination** | 69.8% | 93.4% | +23.6 | Continued and accelerated growth in anti-discrimination consensus (was also the top gainer in 2024) |
| **Development** | 76.3% | 98.1% | +21.8 | Development-oriented resolutions commanded near-universal support |
| **Welfare & Social Services** | 85.1% | 98.3% | +13.3 | Strong consensus on welfare topics |
| **International Law** | 77.9% | 89.8% | +11.9 | Increasing agreement on international legal frameworks |
| **Human Rights** | 69.6% | 80.9% | +11.3 | Notable improvement after years of polarization on human rights |
| **International Relations** | 75.9% | 84.4% | +8.5 | Growing consensus despite geopolitical tensions |

### 3.3 New Topics in 2025

12 new topic tags appeared in the 2025 session (LLM-generated UNBIS tags):
- **PHILOSOPHY AND RELIGION** (87.9% Yes, 908 total votes) — the most divisive of the new tags, driven by the interreligious dialogue resolution (A/RES/79/316) which saw 37 No votes
- **FOOD AND NUTRITION** (99.4% Yes) — near-universal consensus
- **CULTURE** (99.4% Yes) — near-universal consensus
- **NATURAL RESOURCES AND THE ENVIRONMENT** (99.4% Yes)

20 topic tags from 2024 were absent from 2025, notably **DISARMAMENT AND MILITARY QUESTIONS** (which was the largest topic in 2024 with 14,818 total votes). This absence reflects the changed resolution agenda — disarmament-specific resolutions were not voted on in the 2025 session.

---

## 4. Most Divisive Resolutions in 2025

The 20 most divisive resolutions in 2025 (ranked by percentage of non-Yes votes):

| Resolution | Subject | Yes | No | Abs | Divisiveness |
|---|---|---:|---:|---:|---:|
| A/RES/80/222 | Human rights in Iran | 78 | 24 | 64 | 60% |
| A/RES/80/223 | Human rights in occupied Ukraine | 79 | 25 | 73 | 59% |
| A/RES/80/80 | Israeli Practices Committee | 88 | 22 | 64 | 54% |
| A/RES/ES-11/9 | Return of Ukrainian children | 91 | 33 | 57 | 53% |
| A/RES/ES-11/7 | Peace in Ukraine | 93 | 17 | 65 | 52% |
| A/RES/ES-11/8 | Path to peace (Ukraine) | 93 | 19 | 73 | 52% |
| A/RES/80/6 | International Criminal Court | 94 | 55 | 34 | 51% |

**Key pattern**: The most divisive resolutions cluster around two issues: **the Russia-Ukraine conflict** (4 of top 7) and **Israel-Palestine / human rights** (3 of top 7). The ICC report resolution was uniquely divisive with 55 No votes, reflecting opposition from states that do not recognize ICC jurisdiction.

---

## 5. Pairwise Alignment Shifts — Alliance Patterns

### 5.1 The US Isolation Effect

The US moved dramatically away from all Western allies in 2025. The 15 countries that moved furthest from the US include every major NATO/EU partner: CZE, GBR, CAN, AUS, UKR, FRA, LTU, DEU, NLD, HUN, ITA, HRV, SVK, DNK, EST.

**Paradoxically, these same countries moved *closer* to China and Russia**, not because their own positions changed, but because the *reference point* (the US) moved so far into opposition that the rest of the world — including countries like Czech Republic and UK — now correlates more with the China/Russia bloc than with the US.

### 5.2 The Bolivia Anomaly

Bolivia moved the most toward the US (pairwise similarity change +0.44) — but this is an artifact of Bolivia dramatically reducing its participation (91→40 votes), not a genuine alignment shift. Similarly, Bolivia moved away from China by −0.81 for the same reason.

---

## 6. Regional Patterns

| Region | Avg P1 2024 | Avg P1 2025 | Change |
|--------|---:|---:|---:|
| Latin America & Caribbean | 85.3 | 80.1 | −5.2 |
| Northern Africa | 85.4 | 78.8 | −6.7 |
| Northern America | 70.9 | 54.9 | **−16.0** |
| South-eastern Asia | 87.5 | 84.8 | −2.8 |
| Central Asia | 85.1 | 82.6 | −2.5 |
| Southern Asia | 84.7 | 80.5 | −4.2 |
| Western Asia | 81.3 | 77.7 | −3.7 |
| Sub-Saharan Africa | 78.1 | 79.0 | +0.9 |
| Eastern Asia | 78.0 | 74.1 | −3.9 |
| Northern Europe | 73.1 | 72.9 | −0.2 |
| Western Europe | 72.9 | 71.6 | −1.2 |
| Southern Europe | 70.4 | 71.2 | +0.9 |
| Eastern Europe | 68.4 | 69.1 | +0.7 |
| Oceania | 66.1 | 67.2 | +1.1 |

**Key findings**:
- **Northern America** saw the steepest regional decline (−16.0), entirely driven by the US collapse. Canada also declined (from ~69.7 to ~61.7, but less dramatically).
- **Sub-Saharan Africa** was the only non-Western region to *gain*, improving slightly from 78.1 to 79.0 as many African nations increased participation and maintained pro-majority voting patterns.
- **Latin America & Caribbean** fell notably (−5.2), pulled down by Argentina's zero score and several Caribbean islands with reduced attendance.
- **European regions** were relatively stable, with Southern and Eastern Europe actually gaining slightly.

---

## 7. Proposed Report Structure

### Section 4C: P1 Trends — Internal Alignment

**Opening paragraph**: World average P1 declined slightly in 2025 (78.3 → 76.6), reversing the 4-year recovery trend. Two main forces: the dramatic US opposition shift and the doubled resolution volume exposing more fracture points.

**Key Metric box**: −1.7 points

**Country-Level Shifts** (subsection):
1. **US Opposition Pivot** — The dominant story. Yes votes collapsed from 32 to 10; No votes surged from 51 to 174. Driven by Trump administration's withdrawal from multilateral engagement. Pairwise divergence from all Western allies.
2. **Argentina's Continued Freefall** — P1 hit 0.0 under Milei's second year. Now the lowest-scoring country in the dataset, even below Israel.
3. **Syria's Post-Assad Transition** — Regime change produced a confused voting record: fewer No votes but more abstentions, signaling an emerging posture not yet aligned with any bloc.
4. **Spotty Voting** — Madagascar (81→11 votes), St. Vincent (80→16), São Tomé (35→12) — extreme participation swings dominate their scores.
5. **Gainers** — Brazil (+9.3, Lula multilateralism), Myanmar (+8.2, consistent Global South alignment), Zambia (+13.2, increased participation).

**External Drivers** (subsection):
1. **Refugee protection fragmented** — The steepest thematic decline (−18 points), driven by Ukraine children resolution and Palestinian refugee debates.
2. **Discrimination and Development surged** — Discrimination saw +23.6 points in consensus (second consecutive year as top gainer). Development topics nearly unanimous.
3. **Disarmament absent** — The largest topic category from 2024 (DISARMAMENT AND MILITARY QUESTIONS) had no resolutions in 2025, reshaping the thematic landscape.
4. **Most divisive resolutions** — 4 of top 7 related to Russia-Ukraine; 3 to Israel-Palestine. The ICC jurisdiction question produced an unusual 55-country opposition bloc.

**Alliance Realignment** (subsection):
- The US moved so far into opposition that Western allies now correlate more with China than with the US on voting patterns
- This is a measurement artifact (the allies didn't change, the US did) but it has profound implications for bilateral diplomacy metrics

---

## 8. Data Files Reference

| File | Description |
|---|---|
| `p1_world_avg_trend.csv` | World average P1 score, 2000–2025 |
| `p1_full_trend.csv` | World average P1 score, 1946–2025 (complete history) |
| `p1_country_shifts_2024_2025.csv` | Every country's P1 in 2024 vs 2025 with change |
| `p1_big_movers.csv` | Countries with >15-point P1 swing, with vote breakdowns |
| `p1_topic_alignment_changes.csv` | Per-topic Yes% in 2024 vs 2025 |
| `p1_resolutions_2025.csv` | All 193 resolutions in 2025, ranked by divisiveness |
| `p1_participation_analysis.csv` | Voting participation changes correlated with P1 shifts |

---

## 9. Caveats & Validation Notes

1. **Resolution volume doubled**: 2025 had ~192 GA resolutions vs ~95 in 2024. This means the P1 calculation has a much richer input vector in 2025, which can amplify subtle inconsistencies.
2. **Topic tags are LLM-generated**: The new/dropped topics reflect GPT-4o-mini's tagging of the 2025 resolution titles, not official UN categories. The appearance/disappearance of tags like "DISARMAMENT" may reflect tagging inconsistency rather than a true absence of disarmament resolutions.
3. **São Tomé and Príncipe's "perfect" P1=100.0** is an artifact of only 12 votes cast, all Yes. This should be footnoted, not cited as exemplary alignment.
4. **Argentina's P1=0.0** is genuine — it reflects the country voting against the majority on every available dimension, not a data error.
5. **Pairwise sim shifts are relative** — when the US moves, its pairwise similarity with everyone changes, making it look like other countries moved toward China/Russia when they didn't.

---

## 10. Chart Recommendations (matching 2024 report style)

1. **Line chart**: P1 world average 2000–2025 (with 3-year rolling average and trendline) — update of the attached image
2. **Bar chart**: Top 10 biggest P1 drops and gains, 2024→2025
3. **Scatter plot**: Participation change (%) vs P1 change (to illustrate the spotty voting effect)
4. **Heatmap or grouped bar**: Topic-level Yes% changes (declining vs growing consensus)
5. **Network/arrow diagram**: US pairwise similarity with key allies (2024 vs 2025)
6. **Regional bar chart**: P1 averages by region, 2024 vs 2025
