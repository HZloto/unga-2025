# Section 4D — P2 Trends: Regional Alignment (2025 Report)

## Chart Data — P2 World Trend (2000–2025)

Use this table to recreate the report's 2000–2025 world-trend chart for Pillar 2.
- `01_p2_world_avg_trend.csv` contains the full 1946–2025 series; the table below is the 2000–2025 slice used in the report chart
- `average_p2` = raw yearly world average from `annual_scores`
- `smoothed_3y_rolling` = centered 3-year rolling average from `01_p2_world_avg_trend.csv`
- `trendline_linear` = linear trendline from `01_p2_world_avg_trend.csv`, fitted on the full 1946–2025 world-average series
- For charting: plot the smoothed series only where a value is present; 2025 is blank because a centered 3-year rolling average is not available for the endpoint

| Year | average_p2 | smoothed_3y_rolling | trendline_linear |
|------|------------|---------------------|------------------|
| 2000 | 94.72 | 94.00 | 91.82 |
| 2001 | 94.06 | 94.01 | 91.96 |
| 2002 | 93.24 | 93.49 | 92.09 |
| 2003 | 93.16 | 93.34 | 92.22 |
| 2004 | 93.62 | 93.28 | 92.35 |
| 2005 | 93.07 | 93.63 | 92.48 |
| 2006 | 94.21 | 93.89 | 92.62 |
| 2007 | 94.38 | 93.84 | 92.75 |
| 2008 | 92.93 | 93.66 | 92.88 |
| 2009 | 93.69 | 93.23 | 93.01 |
| 2010 | 93.09 | 93.27 | 93.14 |
| 2011 | 93.04 | 92.91 | 93.28 |
| 2012 | 92.59 | 92.76 | 93.41 |
| 2013 | 92.66 | 92.47 | 93.54 |
| 2014 | 92.15 | 92.47 | 93.67 |
| 2015 | 92.61 | 92.11 | 93.80 |
| 2016 | 91.56 | 92.42 | 93.94 |
| 2017 | 93.10 | 92.29 | 94.07 |
| 2018 | 92.21 | 92.70 | 94.20 |
| 2019 | 92.79 | 92.56 | 94.33 |
| 2020 | 92.67 | 92.50 | 94.46 |
| 2021 | 92.04 | 91.20 | 94.60 |
| 2022 | 88.87 | 90.50 | 94.73 |
| 2023 | 90.58 | 90.04 | 94.86 |
| 2024 | 90.68 | 92.19 | 94.99 |
| 2025 | 95.31 |  | 95.12 |

## Data Source & Status

> **Status**: Full descriptive analysis complete from local canonical annual scores. All figures below were derived from `data/annual_scores (4).csv` using the same region mapping used in Section 4C.  
> **Date**: 2026-03-25  
> **Script**: `analysis/4D/p2_section4d_analysis.py`  
> **Primary data source**: `data/annual_scores (4).csv`

---

## 1. Key Metric — World Average P2

**The world average regional alignment increased sharply in 2025, rising from 90.7 in 2024 to 95.3 in 2025 — a +4.6 point increase.** This is not a marginal continuation of the 2024 uptick; it is the **largest annual increase in the 2000–2025 series**. Unlike Pillar 1, which declined in 2025, Pillar 2 strengthened markedly.

| Year | World Avg P2 | Change | Countries | Avg Votes/Country |
|------|-------------|--------|-----------|-------------------|
| 2020 | 92.67 | +0.58 | 193 | 92 |
| 2021 | 92.04 | −0.63 | 193 | 79 |
| 2022 | 88.87 | −3.17 | 192 | 81 |
| 2023 | 90.58 | +1.70 | 192 | 80 |
| 2024 | 90.68 | +0.10 | 191 | 88 |
| **2025** | **95.31** | **+4.63** | **191** | **175** |

### Key Metric Box
> **+4.6 points** increase in regional alignment (90.7 → 95.3)

### Distribution Shift: 2025 Was Broad-Based, Not Marginal
The rise is visible across the whole global distribution, not just in a handful of countries:
- Median P2 rose from **94.9** in 2024 to **98.0** in 2025
- Countries scoring **95 or above** increased from **94** to **148**
- Countries scoring **below 80** fell from **21** to **7**

This is the clearest summary of the 2025 P2 story: **countries became much more clustered around their regional voting patterns**, even while a small set of extreme outliers remained.

### Critical Context: What P2 Measures
In the report framework, **P2 is the regional-alignment pillar**. High P2 means a country is voting relatively close to its geographic peers; low P2 means it is diverging from them.

**Writer note**: Do not frame the 2025 rise as universal harmony. The average rose because most countries converged upward, but some highly visible outliers remained far from their regional blocs, especially:
- **ISR** at **0.0** in Western Asia
- **ARG** at **21.2** in Latin America & Caribbean
- **RUS** at **77.9** and **BLR** at **79.0** in Eastern Europe

**CSV**: `01_p2_world_avg_trend.csv`, `09_p2_distribution_summary_2024_2025.csv`

---

## 2. Regional Scores

Some regions are structurally diverse and therefore more informative in motion than in static level terms. Eastern Asia, Western Asia, and Oceania remain especially heterogeneous. In 2025, however, those heterogeneous regions show the **largest gains**, indicating reduced fragmentation rather than simple stability.

| Region | Avg P2 2024 | Avg P2 2025 | Change |
|--------|-------------|-------------|--------|
| Northern America | 96.5 | 86.2 | **−10.4** |
| Central Asia | 98.3 | 99.4 | +1.2 |
| South-eastern Asia | 95.7 | 98.4 | +2.7 |
| Africa (Northern Africa) | 95.6 | 98.4 | +2.8 |
| Sub-Saharan Africa | 93.7 | 96.8 | +3.1 |
| Northern Europe | 94.3 | 97.6 | +3.3 |
| Latin America & Caribbean | 91.2 | 94.5 | +3.3 |
| Southern Europe | 93.2 | 97.0 | +3.8 |
| Western Europe | 92.9 | 96.8 | +3.9 |
| Southern Asia | 91.2 | 97.2 | +6.0 |
| Eastern Europe | 84.9 | 93.0 | +8.1 |
| Western Asia | 81.0 | 89.8 | +8.8 |
| Oceania | 82.4 | 92.2 | +9.9 |
| Eastern Asia | 80.5 | 93.0 | **+12.5** |

### Significant Shifts (±1.5+)
2025 is unusually one-sided: **13 of 14 broad regions moved by at least 1.5 points**, and all but one moved upward.

#### Northern America
**−10.4**
**96.5 → 86.2**

The only broad region to decline, and by far the sharpest move in either direction. This is entirely a two-country story:
- **CAN** fell **−12.5**
- **USA** fell **−8.2**

Northern America still contains only two members, so the regional average is mechanically sensitive, but the decline is real in both countries.

#### Eastern Asia
**+12.5**
**80.5 → 93.0**

The strongest gain of any broad region. All five members improved:
- **KOR** +18.7
- **JPN** +13.9
- **PRK** +12.8
- **CHN** +10.0
- **MNG** +7.0

This is the cleanest example of a structurally diverse region becoming much less fragmented.

#### Oceania
**+9.9**
**82.4 → 92.2**

A major reversal from the 2024 decline. The gain is broad-based across subregions:
- **Australia and New Zealand** subregion: **+13.1**
- **Micronesia**: **+12.0**
- **Polynesia**: **+7.5**
- **Melanesia**: **+7.3**

Both **AUS** (+15.5) and **NZL** (+10.7) rose strongly, so 2025 is not a simple island-states story.

#### Western Asia
**+8.8**
**81.0 → 89.8**

Most of the region clustered much more tightly in 2025. The strongest gains came from:
- **GEO** +39.6
- **TUR** +19.8
- **ARM** +19.4
- **SYR** +18.1
- **CYP** +17.2

But Western Asia still contains the single most important structural outlier in the entire dataset:
- **ISR** remains at **0.0**

So the region improved sharply while still remaining one of the lowest-scoring broad regions overall.

#### Eastern Europe
**+8.1**
**84.9 → 93.0**

This rise is driven above all by very large gains in:
- **BLR** +33.3
- **RUS** +30.0

But those two remain below the regional average even after the jump:
- **RUS** = 77.9 vs regional avg 93.0
- **BLR** = 79.0 vs regional avg 93.0

So the region became more aligned overall, but its main internal cleavage did not disappear.

#### Southern Asia
**+6.0**
**91.2 → 97.2**

This is a broad upward move rather than a single-country shock. Largest gains:
- **IRN** +14.1
- **IND** +10.9
- **PAK** +10.5

By 2025, six of the eight Southern Asian countries scored **95+**.

#### Broad But Smaller Gains
Several regions rose by roughly three to four points, indicating widespread reconvergence rather than isolated volatility:
- **Western Europe**: +3.9
- **Southern Europe**: +3.8
- **Latin America & Caribbean**: +3.3
- **Northern Europe**: +3.3
- **Sub-Saharan Africa**: +3.1
- **Northern Africa / Africa**: +2.8
- **South-eastern Asia**: +2.7

### Moderate Movement (±1.0 to ±1.4)
#### Central Asia
**+1.2**
**98.3 → 99.4**

This is the only broad region in the moderate bucket. This pattern is consistent with a ceiling effect: Central Asia was already the highest-scoring broad region in 2024 and had limited room to move upward.

### Broadly Stable Regions (Less than ±1.0)
**None.** There are no broad regions in the stability bucket for 2025.

**CSVs**: `04_p2_regional_summary.csv`, `04b_p2_subregional_summary.csv`

---

## 3. Country-Level Drivers and Outliers

### 3.1 Biggest Decliners

| Country | P2 Change | 2024 → 2025 | Writer Interpretation |
|---------|-----------|-------------|-----------------------|
| MDG | −17.6 | 95.9 → 78.3 | Likely participation-sensitive; total votes collapsed from 81 to 11 |
| ARG | −15.3 | 36.5 → 21.2 | Deepened divergence from Latin American regional patterns |
| CAN | −12.5 | 96.4 → 83.9 | Major driver of Northern America's drop |
| USA | −8.2 | 96.6 → 88.4 | Also pulled Northern America downward, though it remains above Canada |

**Writer note**: `ARG` is the major continuity case from 2024. It remains the single largest regional outlier in Latin America & Caribbean by a wide margin.

### 3.2 Biggest Gainers

| Country | P2 Change | 2024 → 2025 | Region |
|---------|-----------|-------------|--------|
| GEO | +39.6 | 40.5 → 80.1 | Western Asia |
| BLR | +33.3 | 45.7 → 79.0 | Eastern Europe |
| RUS | +30.0 | 47.9 → 77.9 | Eastern Europe |
| FSM | +20.2 | 69.2 → 89.4 | Oceania |
| TUR | +19.8 | 66.2 → 86.0 | Western Asia |
| ARM | +19.4 | 71.5 → 90.9 | Western Asia |
| KOR | +18.7 | 68.8 → 87.5 | Eastern Asia |
| SYR | +18.1 | 80.5 → 98.6 | Western Asia |
| LBR | +18.1 | 79.5 → 97.6 | Sub-Saharan Africa |
| CMR | +17.2 | 76.0 → 93.1 | Sub-Saharan Africa |

These are best read as **reconvergence with regional peers**, not as self-contained political stories. If the writer wants to explain *why* a country moved closer to its region, that context should be sourced separately.

### 3.3 Structural Regional Outliers in 2025

| Country | P2 2025 | Broad Region Avg | Gap vs Region Avg |
|---------|---------|------------------|-------------------|
| ISR | 0.0 | 89.8 | −89.8 |
| ARG | 21.2 | 94.5 | −73.3 |
| PRY | 69.3 | 94.5 | −25.2 |
| SSD | 71.8 | 96.8 | −24.9 |
| RUS | 77.9 | 93.0 | −15.1 |
| BLR | 79.0 | 93.0 | −14.0 |
| GEO | 80.1 | 89.8 | −9.7 |

These are the clearest country examples for the writer if the section needs to illustrate what low P2 looks like in practice.

### 3.4 Region-Specific Country Drivers Worth Citing
- **Latin America & Caribbean** improved despite Argentina because almost the whole rest of the region clustered high in 2025: **27 of 32 countries scored 95+**.
- **Western Asia** improved sharply even with Israel at 0.0 because most other members clustered in the high 90s.
- **Eastern Europe** improved because Russia and Belarus rose a lot from a very low 2024 base, even though both remained below regional norms.
- **Sub-Saharan Africa** reached very high regional cohesion overall: **42 of 48 countries scored 95+**, with only **SSD** and **MDG** below 80.

**CSVs**: `02_p2_country_shifts_2024_2025.csv`, `03_p2_big_movers.csv`, `05_p2_region_outliers_2025.csv`, `06_p2_region_change_contributors.csv`, `08_p2_country_profile_2025.csv`

---

## 4. Continuity with the 2024 Section

The 2024 4D section focused on modest regional movement masked by sharper country-level changes. For 2025, that framing needs updating:
- **The headline is no longer modest movement.** 2025 shows a broad-based global rise in regional alignment, not a small uptick.
- **Argentina remains central.** It still strongly depresses Latin America & Caribbean, but unlike 2024 the wider region now rebounds sharply because almost everyone else sits near the top of the P2 distribution.
- **Oceania reverses direction.** Instead of confirming volatility through decline, 2025 shows broad improvement across both Australia/New Zealand and Pacific island subregions.
- **Western Asia still combines high cohesion with a major outlier.** The region rises substantially, but Israel remains completely detached from regional voting patterns in the P2 metric.
- **Eastern Europe still has a Russia/Belarus cleavage.** But the 2025 data show much higher regional scores overall than in 2024, so the right framing is “improved but still internally split,” not “continued deterioration.”

---

## 5. Output Files Reference

| # | File | Description |
|---|---|---|
| 01 | `01_p2_world_avg_trend.csv` | World avg P2, 1946–2025, with YoY change, 3yr rolling, and trendline |
| 02 | `02_p2_country_shifts_2024_2025.csv` | Every country's P2 in 2024 vs 2025 with vote breakdowns |
| 03 | `03_p2_big_movers.csv` | Countries with >10-point P2 swing |
| 04 | `04_p2_regional_summary.csv` | Broad region P2 summary |
| 04b | `04b_p2_subregional_summary.csv` | Subregion P2 summary |
| 05 | `05_p2_region_outliers_2025.csv` | Countries ranked by distance from region averages in 2025 |
| 06 | `06_p2_region_change_contributors.csv` | Country contributions to broad-region average change |
| 07 | `07_p2_key_country_history.csv` | P2 history 2015–2025 for key countries |
| 08 | `08_p2_country_profile_2025.csv` | Full 2025 profile for all 191 countries |
| 09 | `09_p2_distribution_summary_2024_2025.csv` | Distribution summary: mean, median, percentiles, counts |

---

## 6. Caveats & Validation Notes

1. **P2 values come from `annual_scores`**: this section uses the published annual pillar scores already present in the canonical table; it does not recompute Pillar 2 from lower-level vote data.
2. **Scores are best read comparatively**: the annual pillar columns in `annual_scores` are normalized project scores, so absolute levels are less informative than rank position, regional gaps, and year-to-year movement.
3. **Small regions are mechanically sensitive**: Northern America has only 2 members; Eastern Asia has 5; Central Asia has 5. A single country's move can shift the regional average materially.
4. **Large outliers can dominate broad-region means**: Israel in Western Asia and Argentina in Latin America & Caribbean are the clearest examples.
5. **Low-vote cases need caution**: MDG (11 votes), STP (12), SSD (56), and NRU (56) should be treated carefully if used as narrative examples.
6. **P2 tells you that a country moved closer to or further from regional peers, not why**: external political explanations should be sourced separately.

---

## 7. Chart Recommendations

1. **Line chart**: P2 world average 2000–2025 with 3yr rolling and trend
2. **Regional bar chart**: Broad-region P2, 2024 vs 2025
3. **Waterfall or ranked bar**: Region changes sorted from Northern America decline to Eastern Asia gain
4. **Bar chart**: Top 10 P2 gainers and top 10 decliners
5. **Dot plot**: Structural outliers vs regional averages in 2025 (`ISR`, `ARG`, `PRY`, `RUS`, `BLR`, `SSD`)
6. **Small multiples / sparklines**: P2 histories for USA, CAN, ARG, BRA, GEO, RUS, BLR, AUS, NZL, ISR
