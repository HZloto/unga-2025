# Largest rank movements in the 2025 cycle — actual data (Pillar 3)

Drop-in replacement for the placeholder section. **Metric is Pillar 3 — Global
Alignment** (alignment with the prevailing UNGA majority), confirmed by exact
matches against the placeholder numbers.

All values computed from
[data/annual_scores (4).csv](../../data/annual_scores%20%284%29.csv) on the 191
countries with non-null `Pillar 3 Rank` in both 2024 and 2025 (AFG and VEN
excluded — no recorded 2025 votes).

Outputs:

- [top_movers_2025.json](top_movers_2025.json) — drop-in copy & numbers for the cards, spotlight, and regional pulse.
- [top_movers_2025.csv](top_movers_2025.csv) — top 10 Pillar 3 risers + top 10 Pillar 3 fallers, with 2024/2025 ranks and scores.
- [regional_pulse_2025.csv](regional_pulse_2025.csv) — 2025 mean Pillar 3 per continent, 2024 baseline, and YoY delta.

## The four placeholder cards check out

| Country | Placeholder | Pillar 3 actual | Match |
|---|---|---|---|
| URY | +73, rank #1, perfect 2025 global score | +73, rank **1** (tied), score **100.00** | ✅ |
| MDG | −94 | **−94** (rank 90 → 184) | ✅ |
| PRY | −48 | **−48** (rank 140 → 188) | ✅ |
| GTM | +46, top ten, 99.47 global alignment | +46, rank **8**, score **99.47** | ✅ |

Uruguay's "shared first-place group" is also accurate: BRB, CPV, URY all score
100.0 on Pillar 3 in 2025.

## What still needs replacing

The **Regional Pulse** numbers in the placeholder (Africa 74.1 / Americas 68.5 /
Asia 63.4 / Europe 79.3 / Middle East 58.9) do **not** match Pillar 3 — or any
other pillar/total — averages for 2025 under any sensible grouping. They appear
to be fabricated.

### Actual 2025 Pillar 3 averages by region

| Region | Avg Pillar 3 (2025) | Δ vs 2024 | Countries | Stdev |
|---|---:|---:|---:|---:|
| Africa      | 96.7 |  +4.9 | 53 |  3.9 |
| Americas    | 92.4 |  +4.0 | 34 | 20.3 |
| Asia        | 95.7 |  +9.8 | 33 |  3.9 |
| Europe      | 87.6 | +23.6 | 43 |  2.4 |
| Middle East | 90.0 |  +9.3 | 14 | 22.3 |

Continent groupings follow UN M49, with Middle East carved out of Western Asia
(BHR, EGY, IRQ, ISR, JOR, KWT, LBN, OMN, QAT, SAU, SYR, TUR, UAE, YEM). Oceania
(91.5, 14 countries) is in the CSV but not in the 5-card layout.

## For reference: largest absolute Pillar 3 movements in 2025

If you want a stronger "extremes" framing instead of the editorial card mix:

**Top risers**

1. LBR Liberia ↑ **+100** (115 → 15), score 84.66 → 99.35
2. URY Uruguay ↑ **+73** (74 → 1), score 92.09 → 100.00
3. MWI Malawi ↑ **+68** (94 → 26)
4. BOL Bolivia ↑ **+61** (96 → 35)
5. MEX Mexico ↑ **+57** (84 → 27)

**Top fallers**

1. STP São Tomé and Príncipe ↓ **−107** (29 → 136)
2. WSM Samoa ↓ **−100** (24 → 124)
3. MDG Madagascar ↓ **−94** (90 → 184)
4. DMA Dominica ↓ **−92** (16 → 108)
5. SLV El Salvador ↓ **−66** (27 → 93)
