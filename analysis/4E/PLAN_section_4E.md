# Section 4E - P3 Trends: Global Alignment (2025 Report)

## Chart Data - P3 World Trend (2000-2025)

Use this table to recreate the report's 2000-2025 world-trend chart for Pillar 3.
- `01_p3_world_avg_trend.csv` contains the full 1946-2025 series; the table below is the 2000-2025 slice used in the report chart
- `average_p3` = raw yearly world average from `annual_scores`
- `smoothed_3y_rolling` = centered 3-year rolling average from `01_p3_world_avg_trend.csv`
- `trendline_linear` = linear trendline from `01_p3_world_avg_trend.csv`, fitted on the full 1946-2025 world-average series
- For charting: plot the smoothed series only where a value is present; 2025 is blank because a centered 3-year rolling average is not available for the endpoint

| Year | average_p3 | smoothed_3y_rolling | trendline_linear |
|------|------------|---------------------|------------------|
| 2000 | 90.41 | 87.49 | 85.87 |
| 2001 | 86.56 | 87.90 | 86.07 |
| 2002 | 86.72 | 86.75 | 86.27 |
| 2003 | 86.97 | 87.12 | 86.47 |
| 2004 | 87.67 | 87.49 | 86.67 |
| 2005 | 87.83 | 88.31 | 86.87 |
| 2006 | 89.44 | 88.92 | 87.07 |
| 2007 | 89.47 | 89.09 | 87.26 |
| 2008 | 88.35 | 87.88 | 87.46 |
| 2009 | 85.82 | 87.00 | 87.66 |
| 2010 | 86.82 | 86.34 | 87.86 |
| 2011 | 86.38 | 86.48 | 88.06 |
| 2012 | 86.23 | 85.93 | 88.26 |
| 2013 | 85.17 | 85.62 | 88.46 |
| 2014 | 85.45 | 85.09 | 88.66 |
| 2015 | 84.63 | 85.01 | 88.85 |
| 2016 | 84.95 | 85.41 | 89.05 |
| 2017 | 86.63 | 86.24 | 89.25 |
| 2018 | 87.12 | 86.56 | 89.45 |
| 2019 | 85.92 | 86.68 | 89.65 |
| 2020 | 87.01 | 85.73 | 89.85 |
| 2021 | 84.26 | 83.53 | 90.05 |
| 2022 | 79.33 | 81.85 | 90.25 |
| 2023 | 81.97 | 81.15 | 90.45 |
| 2024 | 82.16 | 85.65 | 90.64 |
| 2025 | 92.84 |  | 90.84 |

## Data Source & Status

> **Status**: Full descriptive analysis complete from local canonical annual scores, with descriptive raw-vote and topic diagnostics added to explain the 2025 shift.  
> **Date**: 2026-03-25  
> **Script**: `analysis/4E/p3_section4e_analysis.py`  
> **Primary data sources**: `data/annual_scores (4).csv`, `data/topic_votes_yearly (4).csv`, `data/un_votes_with_sc (1).csv`

---

## 1. Key Metric - World Average P3

**The world average global alignment surged in 2025, rising from 82.2 in 2024 to 92.8 in 2025 - a +10.7 point increase.** This is the **largest annual increase in the 2000-2025 series** and the **second-largest annual increase in the full 1946-2025 series**. Unlike the 2024 section, which centered on issue-specific divergence, 2025 is a broad reconvergence story.

| Year | World Avg P3 | Change | Countries | Avg Votes/Country |
|------|-------------|--------|-----------|-------------------|
| 2020 | 87.01 | +1.09 | 193 | 92.0 |
| 2021 | 84.26 | -2.75 | 193 | 78.6 |
| 2022 | 79.33 | -4.93 | 192 | 80.8 |
| 2023 | 81.97 | +2.64 | 192 | 80.3 |
| 2024 | 82.16 | +0.19 | 191 | 88.3 |
| **2025** | **92.84** | **+10.68** | **191** | **174.7** |

### Key Metric Box
> **+10.7 points** increase in global alignment (82.2 -> 92.8)

### Distribution Shift: 2025 Was Broad-Based, Not Marginal
The rise is visible across almost the entire distribution, not just in a few cases:
- Median P3 rose from **90.1** in 2024 to **96.8** in 2025
- Countries scoring **95 or above** increased from **40** to **112**
- Countries scoring **80 or above** increased from **121** to **185**
- **183 of 191** countries improved; only **7** declined; **1** was flat
- **73** countries gained more than **10 points**
- Only **one** country declined by more than **10 points**: **USA**

This is the clearest summary of the 2025 P3 story: **the global voting center became much more concentrated, and most countries moved toward it at the same time.**

### Critical Context: What P3 Measures
In the report framework, **P3 is the global-alignment pillar**. High P3 means a country is voting relatively close to the world's majority and overall world vote mix; low P3 means it is diverging from the global center.

**Writer note**: Do not frame the 2025 rise as universal agreement. The average rose because most countries converged upward, but three major outliers remained far outside the global center:
- **USA** at **0.0**
- **ISR** at **12.9**
- **ARG** at **32.8**

### Descriptive Proxy: Why the 2025 Jump Is So Large
Raw-vote diagnostics point to a much more Yes-heavy global center in 2025:
- The world vote mix shifted from **78.9% Yes / 8.6% No / 12.5% Abstain** in 2024 to **88.0% Yes / 5.0% No / 7.0% Abstain** in 2025
- The average country-level majority-alignment proxy rose from **79.4** to **88.0**
- The median majority-alignment proxy rose from **86.8** to **93.8**

These are descriptive proxies, not a recomputation of P3, but they explain why so many countries rose together in 2025.

**CSVs**: `01_p3_world_avg_trend.csv`, `05_p3_majority_alignment_proxy.csv`, `10_p3_distribution_summary_2024_2025.csv`

---

## 2. Regional Scores

Unlike Section 4D, where the regional story was mixed, **P3 in 2025 moved upward in every broad region**. There are **no regional decliners** and no stability cases. The strongest movement is heavily concentrated in Europe, but the shift is genuinely global.

| Region | Avg P3 2024 | Avg P3 2025 | Change |
|--------|-------------|-------------|--------|
| Latin America & Caribbean | 91.54 | 95.39 | +3.85 |
| Sub-Saharan Africa | 92.09 | 96.68 | +4.59 |
| South-eastern Asia | 92.99 | 98.19 | +5.19 |
| Central Asia | 91.98 | 97.61 | +5.63 |
| Northern America | 37.12 | 43.68 | +6.56 |
| Africa (Northern Africa) | 88.53 | 96.69 | +8.17 |
| Southern Asia | 86.66 | 95.88 | +9.22 |
| Western Asia | 78.66 | 90.18 | +11.53 |
| Oceania | 78.72 | 91.48 | +12.76 |
| Eastern Asia | 73.66 | 91.15 | +17.49 |
| Southern Europe | 67.69 | 88.32 | +20.64 |
| Western Europe | 65.07 | 88.58 | +23.52 |
| Northern Europe | 63.28 | 87.34 | +24.07 |
| Eastern Europe | 58.76 | 85.90 | **+27.14** |

### Significant Shifts
#### Eastern Europe
**+27.1**  
**58.8 -> 85.9**

The largest regional increase in the entire dataset. This is not a one-country shock. The biggest contributions came from:
- **UKR** +32.0
- **CZE** +31.2
- **ROU** +30.0
- **RUS** +29.8
- **HUN** +29.6
- **POL** +28.6

Even after the jump, Eastern Europe still sits below the 2025 world average of 92.8, so the right framing is **sharp reconvergence, not full normalization**.

#### Northern Europe
**+24.1**  
**63.3 -> 87.3**

The standout case is **GBR** at **+32.1**, but the rise is broad-based:
- **LTU** +29.8
- **EST** +26.6
- **LVA** +26.2
- **FIN** +24.4
- **DNK** +24.3

#### Western Europe
**+23.5**  
**65.1 -> 88.6**

Again, this is collective rather than isolated:
- **FRA** +29.2
- **DEU** +25.8
- **MCO** +25.8
- **NLD** +25.1
- **CHE** +24.1
- **LUX** +23.5

#### Southern Europe
**+20.6**  
**67.7 -> 88.3**

Key contributors:
- **HRV** +27.5
- **ALB** +23.2
- **PRT** +22.9
- **ITA** +22.6
- **ESP** +22.6
- **MNE** +22.3

#### Eastern Asia
**+17.5**  
**73.7 -> 91.2**

All five members improved, led by:
- **PRK** +25.3
- **KOR** +24.1
- **JPN** +18.9
- **CHN** +15.9
- **MNG** +3.2

#### Oceania
**+12.8**  
**78.7 -> 91.5**

The largest contributors were:
- **FSM** +31.6
- **AUS** +24.0
- **PLW** +22.4
- **TON** +19.2
- **NZL** +16.3
- **PNG** +16.1

#### Western Asia
**+11.5**  
**78.7 -> 90.2**

The region improved sharply, especially:
- **GEO** +38.9
- **ARM** +21.1
- **SYR** +18.5
- **TUR** +17.4
- **CYP** +14.8

But the region still contains one of the core global outliers:
- **ISR** remains at **12.9**

#### Northern America
**+6.6**  
**37.1 -> 43.7**

This is a two-country story:
- **CAN** +29.3
- **USA** -16.2

Canada improved enough to lift the regional average, but Northern America still remains the **lowest-scoring broad region in 2025** because the United States is at 0.0.

### Broad Conclusion
All 14 broad regions improved, and even the smallest regional gain was still **+3.85**. So the 2025 P3 rise is not a narrow bloc phenomenon; it is **system-wide**.

**CSVs**: `04_p3_regional_summary.csv`, `04b_p3_subregional_summary.csv`, `13_p3_region_change_contributors.csv`

---

## 3. Voting Dynamics: Broad Yes-Majority Consolidation

The 2024 section was built around two clusters of votes. **For 2025, that framing is too narrow.** The descriptive vote diagnostics show a much broader consolidation into large Yes majorities across high-volume issue areas.

### High-Volume Topics Moving Toward Large Yes Majorities
The biggest shifts are not confined to one file family:
- **Development**: **76.3% -> 93.7% Yes**
- **Economic Development and Development Finance**: **79.8% -> 93.1% Yes**
- **Social Development**: **75.3% -> 93.6% Yes**
- **Social Conditions and Equity**: **71.1% -> 91.6% Yes**
- **Human Rights**: **69.6% -> 87.5% Yes**
- **International Relations**: **75.9% -> 84.2% Yes**
- **International Law**: **79.0% -> 85.8% Yes**
- **Maintenance of Peace and Security**: **77.3% -> 81.3% Yes**
- **Disarmament and Military Questions**: **80.6% -> 83.8% Yes**
- **Political and Legal Questions** overall: **78.5% -> 84.4% Yes**

This is the main quantitative reason P3 rises so much in 2025: **the world center becomes more Yes-heavy across development, social, legal, and institutional agendas at the same time.**

### Divisive Resolutions Still Matter, But They Are No Longer the Whole Story
The most divisive 2025 resolutions remained concentrated in hard political and human-rights files:
- **A/RES/80/222** on human rights in Iran
- **A/RES/80/223** on human rights in the occupied territories of Ukraine
- **A/RES/80/80** on Israeli practices in the occupied territories
- **A/RES/ES-11/7**, **ES-11/8**, and **ES-11/9** on Ukraine peace questions

But those highly visible splits are outweighed numerically by a much larger body of near-consensus Yes votes, especially on:
- **South-South cooperation**
- **Small island developing States**
- **Landlocked developing countries**
- **Climate**
- **Desertification**
- **Disaster risk reduction**
- **Outer space**
- **Humanitarian assistance in natural disasters**

### Topics Moving Away From Yes Majorities
The main declining Yes-share topics are narrower and generally lower-volume:
- **Public Finance**: **-11.9 points**
- **Pollution**: **-9.8**
- **Mineral Resources**: **-9.8**
- **Water**: **-5.0**
- **Trade Related Finance**: **-4.4**

These declines matter, but they do not offset the much larger number of high-volume topics moving toward broader Yes majorities.

**Writer note**: The 2025 P3 story is best framed as **broad Yes-majority consolidation plus a smaller set of still-divisive political resolutions**, not as a single-issue story.

**CSVs**: `05_p3_majority_alignment_proxy.csv`, `06_p3_topic_vote_shifts_2024_2025.csv`, `07_p3_resolution_majority_summary_2025.csv`

---

## 4. Country-Level Drivers and Outliers

### 4.1 Biggest Decliners

There are very few genuine decliners in 2025. Only **7 countries** fell at all, and only **USA** fell by more than 10 points.

| Country | P3 Change | 2024 -> 2025 | Writer Interpretation |
|---------|-----------|-------------|-----------------------|
| USA | -16.2 | 16.2 -> 0.0 | The central outlier case. Vote mix shifted from **34% Yes / 54% No** to **5% Yes / 91% No**, leaving it almost entirely outside the 2025 global center |
| MDG | -7.5 | 90.7 -> 83.1 | Needs caution: participation dropped from **81** to **11** votes |
| ARG | -7.2 | 40.0 -> 32.8 | Deepened divergence from the global center; majority-alignment proxy fell from **45.3** to **27.1** |
| STP | -5.1 | 95.8 -> 90.7 | Participation-sensitive decline; votes fell from **35** to **12** |
| WSM | -4.1 | 96.7 -> 92.6 | Still relatively high, but moved away from the expanded 2025 Yes-heavy center |

### 4.2 Biggest Gainers

| Country | P3 Change | 2024 -> 2025 | Region |
|---------|-----------|-------------|--------|
| GEO | +38.9 | 45.2 -> 84.1 | Western Asia |
| GBR | +32.1 | 52.8 -> 84.9 | Northern Europe |
| UKR | +32.0 | 52.0 -> 84.0 | Eastern Europe |
| FSM | +31.6 | 54.8 -> 86.4 | Oceania |
| CZE | +31.2 | 53.1 -> 84.4 | Eastern Europe |
| ROU | +30.0 | 55.8 -> 85.7 | Eastern Europe |
| RUS | +29.8 | 55.5 -> 85.3 | Eastern Europe |
| LTU | +29.8 | 55.6 -> 85.4 | Northern Europe |
| HUN | +29.6 | 51.9 -> 81.5 | Eastern Europe |
| CAN | +29.3 | 58.0 -> 87.4 | Northern America |

These are best read as **reconvergence with world majorities**, not as standalone political explanations. In country after country, the common pattern is a move away from mixed Yes/No/Abstain profiles and toward a more Yes-heavy yearly vote mix.

### 4.3 Structural Global Outliers in 2025

| Country | P3 2025 | World Avg | Gap vs World Avg |
|---------|---------|-----------|------------------|
| USA | 0.0 | 92.8 | -92.8 |
| ISR | 12.9 | 92.8 | -80.0 |
| ARG | 32.8 | 92.8 | -60.1 |
| PRY | 74.2 | 92.8 | -18.6 |
| SSD | 76.2 | 92.8 | -16.6 |
| NRU | 78.8 | 92.8 | -14.1 |

These are the clearest cases for the writer if the section needs examples of what low P3 looks like in practice.

### 4.4 Country Patterns Worth Citing
- **Canada, the UK, France, Germany, and Georgia** closed especially large gaps on development, social-development, economic-development, and welfare/service topics.
- **Ukraine** also improved sharply through broad reconvergence on development and finance files, not just through one issue area.
- **Russia** improved strongly overall, but still diverged on some humanitarian-aid and refugee-related topics even while moving closer on many other high-consensus files.
- **China** moved into the low 90s, largely because its yearly vote mix shifted much closer to the more Yes-heavy global center.
- **Argentina and Israel** remained far outside the center across many high-volume topics, while the **United States** became the single most extreme case in the dataset.

**CSVs**: `02_p3_country_shifts_2024_2025.csv`, `03_p3_big_movers.csv`, `05_p3_majority_alignment_proxy.csv`, `08_p3_key_country_topic_gap_changes.csv`, `09_p3_country_profile_2025.csv`, `12_p3_global_outliers_2025.csv`

---

## 5. Continuity with the 2024 Section

The 2024 4E section focused on Gaza-related resolutions versus a set of more consensual system files. For 2025, that framing needs to be updated:
- **The headline is no longer two vote clusters driving modest movement.** 2025 shows a system-wide rise in global alignment.
- **Gaza/Palestine and Ukraine still matter.** They remain among the most divisive resolutions in the file.
- **But those divisive texts no longer explain the main yearly shift by themselves.** The larger quantitative story is broad Yes-majority consolidation across development, social, environmental, legal, and cooperation agendas.
- **Western movement is no longer uniform.** Canada and much of Europe move sharply upward, while the United States becomes even more isolated.
- **Argentina remains a continuity outlier.** It stays far from the global center and continues to depress the low end of the P3 distribution.
- **Israel remains a structural outlier.** It improves slightly from 0.0 but remains far outside both the world and Western Asia averages.

---

## 6. Output Files Reference

| # | File | Description |
|---|---|---|
| 01 | `01_p3_world_avg_trend.csv` | World avg P3, 1946-2025, with YoY change, 3yr rolling, and trendline |
| 02 | `02_p3_country_shifts_2024_2025.csv` | Every country's P3 in 2024 vs 2025 with vote breakdowns |
| 03 | `03_p3_big_movers.csv` | Countries with >10-point P3 swing |
| 04 | `04_p3_regional_summary.csv` | Broad-region P3 summary |
| 04b | `04b_p3_subregional_summary.csv` | Subregion P3 summary |
| 05 | `05_p3_majority_alignment_proxy.csv` | Descriptive majority-alignment and vote-mix proxy metrics for 2024 vs 2025 |
| 06 | `06_p3_topic_vote_shifts_2024_2025.csv` | World topic-level vote-share shifts, 2024 vs 2025 |
| 07 | `07_p3_resolution_majority_summary_2025.csv` | All 2025 resolutions with majority type, majority share, and vote totals |
| 08 | `08_p3_key_country_topic_gap_changes.csv` | Topic-level gap-to-world changes for key countries and big movers |
| 09 | `09_p3_country_profile_2025.csv` | Full 2025 P3 profile for all 191 countries |
| 10 | `10_p3_distribution_summary_2024_2025.csv` | Distribution summary: mean, median, percentiles, threshold counts |
| 11 | `11_p3_key_country_history.csv` | P3 history 2015-2025 for key countries |
| 12 | `12_p3_global_outliers_2025.csv` | Countries ranked by distance from the 2025 world average |
| 13 | `13_p3_region_change_contributors.csv` | Country contributions to broad-region average change |

---

## 7. Caveats & Validation Notes

1. **P3 values come from `annual_scores`**: this section uses the published annual pillar scores already present in the canonical table; it does not recompute Pillar 3 from lower-level votes.
2. **The majority-alignment metrics are descriptive proxies**: `05_p3_majority_alignment_proxy.csv` is meant to explain the observed shift, not replace the canonical P3 measure.
3. **2025 contains many more counted votes than 2024**: average votes per country rise from **88.3** to **174.7**, and the raw-vote file contains **192** counted 2025 resolutions versus **95** in 2024. Topic volume changes therefore reflect both agenda expansion and voting behavior.
4. **Topic totals are not unique-resolution counts**: `topic_votes_yearly` maps resolutions into topic buckets, so the same resolution can contribute to multiple topic totals.
5. **Low-vote cases need caution**: especially **MDG** (11 votes), **STP** (12), **SSD** (56), **NRU** (56), and **DMA** (48) if used as narrative examples.
6. **P3 tells you that a country moved closer to or further from the global center, not why**: external political explanations should be sourced separately.

---

## 8. Chart Recommendations

1. **Line chart**: P3 world average 2000-2025 with 3yr rolling and trend
2. **Regional bar chart**: Broad-region P3, 2024 vs 2025
3. **Ranked bar chart**: Region changes from Latin America & Caribbean to Eastern Europe
4. **Bar chart**: Top 10 P3 gainers plus the handful of decliners
5. **Dot plot**: Structural global outliers vs world average in 2025 (`USA`, `ISR`, `ARG`, `PRY`, `SSD`, `NRU`)
6. **Slope chart**: World vote mix shift in the raw-vote proxy (`Yes`, `No`, `Abstain`) from 2024 to 2025
7. **Bar chart**: High-volume topic Yes-share changes (`Development`, `Economic Development and Development Finance`, `Social Development`, `Human Rights`, `International Law`, `Maintenance of Peace and Security`)
8. **Scatter or ranked bar**: 2025 resolution majority share, highlighting the most divisive texts and the strongest majorities
