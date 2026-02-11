"""
UNGA 2025 Comprehensive Insights Analysis
==========================================
Replicates key analyses from the 2024 3DL report on 2025 data:
  1. Overall voting statistics
  2. Alignment shift (% countries rising/falling)
  3. Top movers across all 3 pillars
  4. Countries that never voted "No" / perfect record
  5. Pillar trend analysis (P1/P2/P3 world averages)
  6. Regional alignment scores & movements
  7. Topic analysis — biggest thematic shifts
  8. P5 alignment analysis
  9. Country spotlights (Argentina, Syria, Bolivia — 2024 watch items)
 10. Isolation detection (scores < 50)
 11. Pairwise similarity — biggest bilateral shifts
 12. Outlier & insight detection

Data integrity checks: vote arithmetic validated throughout.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

# ── Helpers ──────────────────────────────────────────────────────────────

def sep(title):
    print()
    print("=" * 78)
    print(f"  {title}")
    print("=" * 78)

def subsep(title):
    print(f"\n  ── {title} {'─' * max(1, 60 - len(title))}")

# ISO3 → UN M49 subregion mapping (193 UN members)
# Built from UN Statistics Division standard country or area codes
REGION_MAP = {
    # Northern Africa
    'DZA': 'Northern Africa', 'EGY': 'Northern Africa', 'LBY': 'Northern Africa',
    'MAR': 'Northern Africa', 'SDN': 'Northern Africa', 'TUN': 'Northern Africa',
    # Sub-Saharan / Eastern Africa
    'BDI': 'Sub-Saharan Africa', 'COM': 'Sub-Saharan Africa', 'DJI': 'Sub-Saharan Africa',
    'ERI': 'Sub-Saharan Africa', 'ETH': 'Sub-Saharan Africa', 'KEN': 'Sub-Saharan Africa',
    'MDG': 'Sub-Saharan Africa', 'MWI': 'Sub-Saharan Africa', 'MUS': 'Sub-Saharan Africa',
    'MOZ': 'Sub-Saharan Africa', 'RWA': 'Sub-Saharan Africa', 'SYC': 'Sub-Saharan Africa',
    'SOM': 'Sub-Saharan Africa', 'SSD': 'Sub-Saharan Africa', 'TZA': 'Sub-Saharan Africa',
    'UGA': 'Sub-Saharan Africa', 'ZMB': 'Sub-Saharan Africa', 'ZWE': 'Sub-Saharan Africa',
    # Middle Africa
    'AGO': 'Sub-Saharan Africa', 'CMR': 'Sub-Saharan Africa', 'CAF': 'Sub-Saharan Africa',
    'TCD': 'Sub-Saharan Africa', 'COD': 'Sub-Saharan Africa', 'COG': 'Sub-Saharan Africa',
    'GNQ': 'Sub-Saharan Africa', 'GAB': 'Sub-Saharan Africa', 'STP': 'Sub-Saharan Africa',
    # Southern Africa
    'BWA': 'Sub-Saharan Africa', 'SWZ': 'Sub-Saharan Africa', 'LSO': 'Sub-Saharan Africa',
    'NAM': 'Sub-Saharan Africa', 'ZAF': 'Sub-Saharan Africa',
    # Western Africa
    'BEN': 'Sub-Saharan Africa', 'BFA': 'Sub-Saharan Africa', 'CPV': 'Sub-Saharan Africa',
    'CIV': 'Sub-Saharan Africa', 'GMB': 'Sub-Saharan Africa', 'GHA': 'Sub-Saharan Africa',
    'GIN': 'Sub-Saharan Africa', 'GNB': 'Sub-Saharan Africa', 'LBR': 'Sub-Saharan Africa',
    'MLI': 'Sub-Saharan Africa', 'MRT': 'Sub-Saharan Africa', 'NER': 'Sub-Saharan Africa',
    'NGA': 'Sub-Saharan Africa', 'SEN': 'Sub-Saharan Africa', 'SLE': 'Sub-Saharan Africa',
    'TGO': 'Sub-Saharan Africa',
    # Eastern Asia
    'CHN': 'Eastern Asia', 'PRK': 'Eastern Asia', 'JPN': 'Eastern Asia',
    'MNG': 'Eastern Asia', 'KOR': 'Eastern Asia',
    # South-eastern Asia
    'BRN': 'South-eastern Asia', 'KHM': 'South-eastern Asia', 'IDN': 'South-eastern Asia',
    'LAO': 'South-eastern Asia', 'MYS': 'South-eastern Asia', 'MMR': 'South-eastern Asia',
    'PHL': 'South-eastern Asia', 'SGP': 'South-eastern Asia', 'THA': 'South-eastern Asia',
    'TLS': 'South-eastern Asia', 'VNM': 'South-eastern Asia',
    # Southern Asia
    'AFG': 'Southern Asia', 'BGD': 'Southern Asia', 'BTN': 'Southern Asia',
    'IND': 'Southern Asia', 'IRN': 'Southern Asia', 'MDV': 'Southern Asia',
    'NPL': 'Southern Asia', 'PAK': 'Southern Asia', 'LKA': 'Southern Asia',
    # Central Asia
    'KAZ': 'Central Asia', 'KGZ': 'Central Asia', 'TJK': 'Central Asia',
    'TKM': 'Central Asia', 'UZB': 'Central Asia',
    # Western Asia
    'ARM': 'Western Asia', 'AZE': 'Western Asia', 'BHR': 'Western Asia',
    'CYP': 'Western Asia', 'GEO': 'Western Asia', 'IRQ': 'Western Asia',
    'ISR': 'Western Asia', 'JOR': 'Western Asia', 'KWT': 'Western Asia',
    'LBN': 'Western Asia', 'OMN': 'Western Asia', 'QAT': 'Western Asia',
    'SAU': 'Western Asia', 'SYR': 'Western Asia', 'TUR': 'Western Asia',
    'ARE': 'Western Asia', 'YEM': 'Western Asia',
    # Eastern Europe
    'BLR': 'Eastern Europe', 'BGR': 'Eastern Europe', 'CZE': 'Eastern Europe',
    'HUN': 'Eastern Europe', 'POL': 'Eastern Europe', 'MDA': 'Eastern Europe',
    'ROU': 'Eastern Europe', 'RUS': 'Eastern Europe', 'SVK': 'Eastern Europe',
    'UKR': 'Eastern Europe',
    # Northern Europe
    'DNK': 'Northern Europe', 'EST': 'Northern Europe', 'FIN': 'Northern Europe',
    'ISL': 'Northern Europe', 'IRL': 'Northern Europe', 'LVA': 'Northern Europe',
    'LTU': 'Northern Europe', 'NOR': 'Northern Europe', 'SWE': 'Northern Europe',
    'GBR': 'Northern Europe',
    # Southern Europe
    'ALB': 'Southern Europe', 'AND': 'Southern Europe', 'BIH': 'Southern Europe',
    'HRV': 'Southern Europe', 'GRC': 'Southern Europe', 'ITA': 'Southern Europe',
    'MLT': 'Southern Europe', 'MNE': 'Southern Europe', 'MKD': 'Southern Europe',
    'PRT': 'Southern Europe', 'SMR': 'Southern Europe', 'SRB': 'Southern Europe',
    'SVN': 'Southern Europe', 'ESP': 'Southern Europe',
    # Western Europe
    'AUT': 'Western Europe', 'BEL': 'Western Europe', 'FRA': 'Western Europe',
    'DEU': 'Western Europe', 'LIE': 'Western Europe', 'LUX': 'Western Europe',
    'MCO': 'Western Europe', 'NLD': 'Western Europe', 'CHE': 'Western Europe',
    # Caribbean
    'ATG': 'Latin America & Caribbean', 'BHS': 'Latin America & Caribbean',
    'BRB': 'Latin America & Caribbean', 'CUB': 'Latin America & Caribbean',
    'DMA': 'Latin America & Caribbean', 'DOM': 'Latin America & Caribbean',
    'GRD': 'Latin America & Caribbean', 'HTI': 'Latin America & Caribbean',
    'JAM': 'Latin America & Caribbean', 'KNA': 'Latin America & Caribbean',
    'LCA': 'Latin America & Caribbean', 'VCT': 'Latin America & Caribbean',
    'TTO': 'Latin America & Caribbean', 'BLZ': 'Latin America & Caribbean',
    # Central America
    'CRI': 'Latin America & Caribbean', 'SLV': 'Latin America & Caribbean',
    'GTM': 'Latin America & Caribbean', 'HND': 'Latin America & Caribbean',
    'MEX': 'Latin America & Caribbean', 'NIC': 'Latin America & Caribbean',
    'PAN': 'Latin America & Caribbean',
    # South America
    'ARG': 'Latin America & Caribbean', 'BOL': 'Latin America & Caribbean',
    'BRA': 'Latin America & Caribbean', 'CHL': 'Latin America & Caribbean',
    'COL': 'Latin America & Caribbean', 'ECU': 'Latin America & Caribbean',
    'GUY': 'Latin America & Caribbean', 'PRY': 'Latin America & Caribbean',
    'PER': 'Latin America & Caribbean', 'SUR': 'Latin America & Caribbean',
    'URY': 'Latin America & Caribbean', 'VEN': 'Latin America & Caribbean',
    # Northern America
    'CAN': 'Northern America', 'USA': 'Northern America',
    # Oceania
    'AUS': 'Oceania', 'FJI': 'Oceania', 'KIR': 'Oceania', 'MHL': 'Oceania',
    'FSM': 'Oceania', 'NRU': 'Oceania', 'NZL': 'Oceania', 'PLW': 'Oceania',
    'PNG': 'Oceania', 'WSM': 'Oceania', 'SLB': 'Oceania', 'TON': 'Oceania',
    'TUV': 'Oceania', 'VUT': 'Oceania',
}

# ── Load data ────────────────────────────────────────────────────────────

sep("LOADING DATA")

annual  = pd.read_csv(DATA / "annual_scores (2).csv")
pairwise = pd.read_csv(DATA / "pairwise_similarity_yearly (2).csv")
topics   = pd.read_csv(DATA / "topic_votes_yearly (2).csv")
source   = pd.read_csv(DATA / "un_votes_2025_processed.csv")

a25 = annual[annual["Year"] == 2025].copy()
a24 = annual[annual["Year"] == 2024].copy()
a23 = annual[annual["Year"] == 2023].copy()
p25 = pairwise[pairwise["Year"] == 2025].copy()
p24 = pairwise[pairwise["Year"] == 2024].copy()
t25 = topics[topics["Year"] == 2025].copy()
t24 = topics[topics["Year"] == 2024].copy()

ga25 = source[source["Council"] == "General Assembly"]

print(f"  ✓ annual_scores: {len(annual)} rows, {a25.shape[0]} for 2025, {a24.shape[0]} for 2024")
print(f"  ✓ pairwise_similarity: {len(pairwise)} rows, {p25.shape[0]} for 2025")
print(f"  ✓ topic_votes: {len(topics)} rows, {t25.shape[0]} for 2025")
print(f"  ✓ source (raw): {len(source)} rows, {len(ga25)} GA resolutions")

# ── Vote arithmetic check ───────────────────────────────────────────────
check = a25["Yes Votes"] + a25["No Votes"] + a25["Abstain Votes"]
mismatch = (check != a25["Total Votes in Year"]).sum()
print(f"  ✓ Vote arithmetic (Y+N+A==T): {'PASS' if mismatch==0 else f'FAIL ({mismatch} mismatches)'}")

# ═══════════════════════════════════════════════════════════════════════
# 1. OVERALL 2025 VOTING STATISTICS
# ═══════════════════════════════════════════════════════════════════════
sep("1. OVERALL 2025 VOTING STATISTICS")

total_res_voted = len(ga25)
total_yes   = a25["Yes Votes"].sum()
total_no    = a25["No Votes"].sum()
total_abs   = a25["Abstain Votes"].sum()
total_votes = a25["Total Votes in Year"].sum()

print(f"  GA Resolutions put to a vote in 2025: {total_res_voted}")
print(f"  (2024 had 95 resolutions voted on)")
print()
print(f"  Overall voting record across all countries:")
print(f"    YES:     {total_yes:,}  ({100*total_yes/total_votes:.1f}%)")
print(f"    NO:      {total_no:,}  ({100*total_no/total_votes:.1f}%)")
print(f"    ABSTAIN: {total_abs:,}  ({100*total_abs/total_votes:.1f}%)")
print(f"    TOTAL:   {total_votes:,}")

# Compare to 2024
total_yes24   = a24["Yes Votes"].sum()
total_no24    = a24["No Votes"].sum()
total_abs24   = a24["Abstain Votes"].sum()
total_votes24 = a24["Total Votes in Year"].sum()

print(f"\n  Comparison to 2024:")
print(f"    YES:     {100*total_yes24/total_votes24:.1f}% → {100*total_yes/total_votes:.1f}%  ({100*total_yes/total_votes - 100*total_yes24/total_votes24:+.1f}pp)")
print(f"    NO:      {100*total_no24/total_votes24:.1f}% → {100*total_no/total_votes:.1f}%  ({100*total_no/total_votes - 100*total_no24/total_votes24:+.1f}pp)")
print(f"    ABSTAIN: {100*total_abs24/total_votes24:.1f}% → {100*total_abs/total_votes:.1f}%  ({100*total_abs/total_votes - 100*total_abs24/total_votes24:+.1f}pp)")

# ═══════════════════════════════════════════════════════════════════════
# 2. ALIGNMENT SHIFTS: % OF COUNTRIES RISING / FALLING
# ═══════════════════════════════════════════════════════════════════════
sep("2. ALIGNMENT SHIFTS — % OF COUNTRIES RISING vs FALLING (2024→2025)")

merged = a25.merge(a24, on="Country name", suffixes=("_25", "_24"))

for pillar, col in [("Overall (Total Index)", "Total Index Average"),
                     ("Pillar 1 — Internal", "Pillar 1 Score"),
                     ("Pillar 2 — Regional", "Pillar 2 Score"),
                     ("Pillar 3 — Global", "Pillar 3 Score")]:
    diff = merged[f"{col}_25"] - merged[f"{col}_24"]
    fell  = (diff < 0).sum()
    rose  = (diff > 0).sum()
    flat  = (diff == 0).sum()
    pct_fell = 100 * fell / len(diff)
    subsep(pillar)
    print(f"    Rose:  {rose}  ({100*rose/len(diff):.0f}%)")
    print(f"    Fell:  {fell}  ({pct_fell:.0f}%)")
    print(f"    Flat:  {flat}")
    print(f"    (In 2024 report: 44% of countries saw alignment fall)")

# Compare to historical: 2023→2024 vs 2024→2025
merged_prev = a24.merge(a23, on="Country name", suffixes=("_24", "_23"))
diff_prev = merged_prev["Total Index Average_24"] - merged_prev["Total Index Average_23"]
fell_prev = (diff_prev < 0).sum()
print(f"\n  Historical comparison — % fell overall:")
print(f"    2023→2024: {100*fell_prev/len(diff_prev):.0f}%")
fell_cur = (merged["Total Index Average_25"] - merged["Total Index Average_24"] < 0).sum()
print(f"    2024→2025: {100*fell_cur/len(merged):.0f}%")

# ═══════════════════════════════════════════════════════════════════════
# 3. TOP MOVERS — BIGGEST RISES AND DROPS (ALL PILLARS + OVERALL)
# ═══════════════════════════════════════════════════════════════════════
sep("3. TOP MOVERS — BIGGEST RISES & DROPS (2024→2025)")

for pillar_name, score_col, rank_col in [
    ("OVERALL", "Total Index Average", "Overall Rank"),
    ("PILLAR 1 — INTERNAL", "Pillar 1 Score", "Pillar 1 Rank"),
    ("PILLAR 2 — REGIONAL", "Pillar 2 Score", "Pillar 2 Rank"),
    ("PILLAR 3 — GLOBAL", "Pillar 3 Score", "Pillar 3 Rank"),
]:
    subsep(f"Top Movers: {pillar_name}")
    
    score_diff = merged[f"{score_col}_25"] - merged[f"{score_col}_24"]
    merged["_diff"] = score_diff
    
    # Rank diff (lower rank = better, so negative rank change = improvement)
    if rank_col in merged.columns.str.replace("_25", "").tolist():
        rank_d = merged[f"{rank_col}_25"] - merged[f"{rank_col}_24"]
        merged["_rank_diff"] = rank_d
    
    # Top 10 risers
    top_rise = merged.nlargest(10, "_diff")[["Country name", f"{score_col}_24", f"{score_col}_25", "_diff"]]
    print(f"\n    Top 10 RISERS ({pillar_name}):")
    print(f"    {'Country':<8} {'2024':>8} {'2025':>8} {'Change':>8}")
    print(f"    {'─'*36}")
    for _, r in top_rise.iterrows():
        print(f"    {r['Country name']:<8} {r[f'{score_col}_24']:>8.1f} {r[f'{score_col}_25']:>8.1f} {r['_diff']:>+8.1f}")
    
    # Top 10 fallers
    top_fall = merged.nsmallest(10, "_diff")[["Country name", f"{score_col}_24", f"{score_col}_25", "_diff"]]
    print(f"\n    Top 10 FALLERS ({pillar_name}):")
    print(f"    {'Country':<8} {'2024':>8} {'2025':>8} {'Change':>8}")
    print(f"    {'─'*36}")
    for _, r in top_fall.iterrows():
        print(f"    {r['Country name']:<8} {r[f'{score_col}_24']:>8.1f} {r[f'{score_col}_25']:>8.1f} {r['_diff']:>+8.1f}")

# ═══════════════════════════════════════════════════════════════════════
# 4. COUNTRIES THAT NEVER VOTED "NO" / PERFECT RECORD
# ═══════════════════════════════════════════════════════════════════════
sep("4. COUNTRIES THAT NEVER VOTED 'NO' IN 2025")

no_zero = a25[a25["No Votes"] == 0].sort_values("Country name")
print(f"  {len(no_zero)} countries cast zero 'No' votes in 2025")
print(f"  (2024: 60 countries)")
print()
print(f"  Countries: {', '.join(no_zero['Country name'].tolist())}")

# Perfect record: only YES (no No, no Abstain)
perfect = a25[(a25["No Votes"] == 0) & (a25["Abstain Votes"] == 0)]
print(f"\n  Perfect record (ONLY Yes): {len(perfect)} countries")
if len(perfect) > 0:
    print(f"  Countries: {', '.join(perfect['Country name'].tolist())}")

# Only YES votes (allowing some abstain but checking vote proportions)
subsep("Highest YES rates")
a25_c = a25.copy()
a25_c["yes_pct"] = 100 * a25_c["Yes Votes"] / a25_c["Total Votes in Year"]
top_yes = a25_c.nlargest(10, "yes_pct")[["Country name", "Yes Votes", "No Votes", "Abstain Votes", "Total Votes in Year", "yes_pct"]]
for _, r in top_yes.iterrows():
    print(f"    {r['Country name']:<8}: {r['yes_pct']:.1f}% YES ({int(r['Yes Votes'])}/{int(r['Total Votes in Year'])}), {int(r['No Votes'])} No, {int(r['Abstain Votes'])} Abstain")

# Countries that voted No the most
subsep("Highest 'No' vote counts in 2025")
top_no = a25.nlargest(15, "No Votes")[["Country name", "Yes Votes", "No Votes", "Abstain Votes", "Total Votes in Year"]]
for _, r in top_no.iterrows():
    no_pct = 100 * r["No Votes"] / r["Total Votes in Year"]
    print(f"    {r['Country name']:<8}: {int(r['No Votes'])} No votes ({no_pct:.1f}% of total), {int(r['Yes Votes'])} Yes, {int(r['Abstain Votes'])} Abstain")

# ═══════════════════════════════════════════════════════════════════════
# 5. PILLAR TRENDS — WORLD AVERAGES
# ═══════════════════════════════════════════════════════════════════════
sep("5. PILLAR TRENDS — WORLD AVERAGES (2020–2025)")

for yr_label, adf in [("2020", annual[annual["Year"]==2020]),
                       ("2021", annual[annual["Year"]==2021]),
                       ("2022", annual[annual["Year"]==2022]),
                       ("2023", annual[annual["Year"]==2023]),
                       ("2024", a24),
                       ("2025", a25)]:
    p1 = adf["Pillar 1 Score"].mean()
    p2 = adf["Pillar 2 Score"].mean()
    p3 = adf["Pillar 3 Score"].mean()
    ti = adf["Total Index Average"].mean()
    print(f"  {yr_label}:  P1={p1:.1f}  P2={p2:.1f}  P3={p3:.1f}  Overall={ti:.1f}")

subsep("Year-over-year changes (2024→2025)")
for pillar, col in [("Pillar 1 (Internal)", "Pillar 1 Score"),
                     ("Pillar 2 (Regional)", "Pillar 2 Score"),
                     ("Pillar 3 (Global)", "Pillar 3 Score"),
                     ("Overall", "Total Index Average")]:
    avg24 = a24[col].mean()
    avg25 = a25[col].mean()
    print(f"    {pillar}: {avg24:.1f} → {avg25:.1f}  ({avg25-avg24:+.1f})")

# ═══════════════════════════════════════════════════════════════════════
# 6. REGIONAL ALIGNMENT SCORES & MOVEMENTS
# ═══════════════════════════════════════════════════════════════════════
sep("6. REGIONAL ALIGNMENT ANALYSIS")

a25_r = a25.copy()
a25_r["Region"] = a25_r["Country name"].map(REGION_MAP)
a24_r = a24.copy()
a24_r["Region"] = a24_r["Country name"].map(REGION_MAP)

unmapped_25 = a25_r[a25_r["Region"].isna()]["Country name"].tolist()
if unmapped_25:
    print(f"  ⚠️ Unmapped countries: {unmapped_25}")

# Regional averages for P3 (Global Alignment — most comparable to report)
subsep("Regional Pillar 3 (Global Alignment) — 2024 vs 2025")
reg_p3_25 = a25_r.groupby("Region")["Pillar 3 Score"].mean()
reg_p3_24 = a24_r.groupby("Region")["Pillar 3 Score"].mean()
reg_diff = (reg_p3_25 - reg_p3_24).sort_values(ascending=False)

print(f"    {'Region':<28} {'2024':>7} {'2025':>7} {'Change':>8}")
print(f"    {'─'*54}")
for region in reg_diff.index:
    v24 = reg_p3_24.get(region, np.nan)
    v25 = reg_p3_25.get(region, np.nan)
    d = reg_diff[region]
    print(f"    {region:<28} {v24:>7.1f} {v25:>7.1f} {d:>+8.1f}")

# Regional averages for Overall score
subsep("Regional Overall Score — 2024 vs 2025")
reg_ov_25 = a25_r.groupby("Region")["Total Index Average"].mean()
reg_ov_24 = a24_r.groupby("Region")["Total Index Average"].mean()
reg_ov_diff = (reg_ov_25 - reg_ov_24).sort_values(ascending=False)

print(f"    {'Region':<28} {'2024':>7} {'2025':>7} {'Change':>8}")
print(f"    {'─'*54}")
for region in reg_ov_diff.index:
    v24 = reg_ov_24.get(region, np.nan)
    v25 = reg_ov_25.get(region, np.nan)
    d = reg_ov_diff[region]
    print(f"    {region:<28} {v24:>7.1f} {v25:>7.1f} {d:>+8.1f}")

# Regional best/worst performers in 2025
subsep("Regional extremes — highest & lowest scoring countries per region")
for region in sorted(a25_r["Region"].dropna().unique()):
    rdf = a25_r[a25_r["Region"] == region].sort_values("Total Index Average", ascending=False)
    best = rdf.iloc[0]
    worst = rdf.iloc[-1]
    print(f"    {region}: Best={best['Country name']} ({best['Total Index Average']:.1f}), "
          f"Worst={worst['Country name']} ({worst['Total Index Average']:.1f})")

# ═══════════════════════════════════════════════════════════════════════
# 7. TOPIC ANALYSIS — BIGGEST THEMATIC SHIFTS
# ═══════════════════════════════════════════════════════════════════════
sep("7. TOPIC ANALYSIS — BIGGEST THEMATIC SHIFTS (2024→2025)")

# Aggregate topic-level yes rate across all countries
def topic_yes_rate(tdf):
    g = tdf.groupby("TopicTag").agg(
        total_yes=("YesVotes_Topic", "sum"),
        total_all=("TotalVotes_Topic", "sum"),
    )
    g["yes_rate"] = 100 * g["total_yes"] / g["total_all"]
    return g

tr25 = topic_yes_rate(t25)
tr24 = topic_yes_rate(t24)

# Merge and compute change
tr_merged = tr25[["yes_rate"]].join(tr24[["yes_rate"]], lsuffix="_25", rsuffix="_24", how="outer")
tr_merged["change"] = tr_merged["yes_rate_25"] - tr_merged["yes_rate_24"]
tr_merged = tr_merged.dropna(subset=["change"])

subsep("Topics with LARGEST DECLINE in Yes-vote rate")
top_decline = tr_merged.nsmallest(15, "change")
print(f"    {'Topic':<55} {'2024':>6} {'2025':>6} {'Chg':>7}")
print(f"    {'─'*76}")
for topic, r in top_decline.iterrows():
    print(f"    {topic:<55} {r['yes_rate_24']:>5.1f}% {r['yes_rate_25']:>5.1f}% {r['change']:>+6.1f}")

subsep("Topics with LARGEST INCREASE in Yes-vote rate")
top_increase = tr_merged.nlargest(15, "change")
print(f"    {'Topic':<55} {'2024':>6} {'2025':>6} {'Chg':>7}")
print(f"    {'─'*76}")
for topic, r in top_increase.iterrows():
    print(f"    {topic:<55} {r['yes_rate_24']:>5.1f}% {r['yes_rate_25']:>5.1f}% {r['change']:>+6.1f}")

# New and disappeared topics
new_topics = set(t25["TopicTag"].unique()) - set(t24["TopicTag"].unique())
gone_topics = set(t24["TopicTag"].unique()) - set(t25["TopicTag"].unique())
if new_topics:
    subsep("NEW topics in 2025 (not in 2024)")
    for t in sorted(new_topics):
        count = t25[t25["TopicTag"]==t]["TotalVotes_Topic"].sum()
        print(f"    • {t}  (total votes cast: {count})")
if gone_topics:
    subsep("DROPPED topics (in 2024 but not in 2025)")
    for t in sorted(gone_topics):
        print(f"    • {t}")

# ═══════════════════════════════════════════════════════════════════════
# 8. P5 ALIGNMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════════════
sep("8. P5 ALIGNMENT ANALYSIS (2025)")

p5_codes = {"CHN": "China", "RUS": "Russia", "GBR": "United Kingdom",
            "FRA": "France", "USA": "United States"}

subsep("P5 Rankings in 2025")
for iso, name in p5_codes.items():
    row = a25[a25["Country name"] == iso]
    if row.empty:
        print(f"    {name} ({iso}): NOT FOUND")
        continue
    r = row.iloc[0]
    print(f"    {name:<18} Overall Rank: #{int(r['Overall Rank']):<4} "
          f"Score: {r['Total Index Average']:.1f}  "
          f"P1={r['Pillar 1 Score']:.1f}  P2={r['Pillar 2 Score']:.1f}  P3={r['Pillar 3 Score']:.1f}")

# P5 rank changes 2024→2025
subsep("P5 Rank Changes (2024→2025)")
for iso, name in p5_codes.items():
    r25 = a25[a25["Country name"] == iso]
    r24 = a24[a24["Country name"] == iso]
    if r25.empty or r24.empty:
        continue
    rank_25 = int(r25.iloc[0]["Overall Rank"])
    rank_24 = int(r24.iloc[0]["Overall Rank"])
    score_25 = r25.iloc[0]["Total Index Average"]
    score_24 = r24.iloc[0]["Total Index Average"]
    print(f"    {name:<18} Rank: #{rank_24} → #{rank_25} ({rank_25-rank_24:+d})  "
          f"Score: {score_24:.1f} → {score_25:.1f} ({score_25-score_24:+.1f})")

# Which P5 member is most aligned with each country? (via pairwise similarity)
subsep("P5 most-aligned-with analysis (pairwise cosine similarity, 2025)")
p5_iso = list(p5_codes.keys())
p5_pairs = p25[
    (p25["Country1_ISO3"].isin(p5_iso)) | (p25["Country2_ISO3"].isin(p5_iso))
].copy()

# For each non-P5 country, find which P5 has highest similarity
all_countries_25 = set(a25["Country name"].tolist())
non_p5 = all_countries_25 - set(p5_iso)

best_p5 = {}
for c in non_p5:
    sims = {}
    for p5 in p5_iso:
        # Check both directions
        pair = p25[
            ((p25["Country1_ISO3"]==c) & (p25["Country2_ISO3"]==p5)) |
            ((p25["Country1_ISO3"]==p5) & (p25["Country2_ISO3"]==c))
        ]
        if not pair.empty:
            sims[p5] = pair.iloc[0]["CosineSimilarity"]
    if sims:
        best_p5[c] = max(sims, key=sims.get)

p5_counts = pd.Series(best_p5).value_counts()
print(f"    Countries most aligned with each P5 member:")
for p5, cnt in p5_counts.items():
    pct = 100 * cnt / len(best_p5)
    print(f"      {p5_codes[p5]:<18}: {cnt} countries ({pct:.1f}%)")

# Compare to 2024 (same analysis)
non_p5_24_countries = set(a24["Country name"].tolist()) - set(p5_iso)
best_p5_24 = {}
for c in non_p5_24_countries:
    sims = {}
    for p5 in p5_iso:
        pair = p24[
            ((p24["Country1_ISO3"]==c) & (p24["Country2_ISO3"]==p5)) |
            ((p24["Country1_ISO3"]==p5) & (p24["Country2_ISO3"]==c))
        ]
        if not pair.empty:
            sims[p5] = pair.iloc[0]["CosineSimilarity"]
    if sims:
        best_p5_24[c] = max(sims, key=sims.get)

p5_counts_24 = pd.Series(best_p5_24).value_counts()
print(f"\n    Change compared to 2024:")
for p5 in p5_iso:
    c24 = p5_counts_24.get(p5, 0)
    c25 = p5_counts.get(p5, 0)
    print(f"      {p5_codes[p5]:<18}: {c24} → {c25} ({c25-c24:+d})")

# ═══════════════════════════════════════════════════════════════════════
# 9. COUNTRY SPOTLIGHTS
# ═══════════════════════════════════════════════════════════════════════
sep("9. COUNTRY SPOTLIGHTS")

spotlight_countries = {
    "ARG": "Argentina — 2024 biggest drop; continue/reverse?",
    "SYR": "Syria — 2024 watch item (post-Assad shift?)",
    "BOL": "Bolivia — 2024 watch item (elections, ideology shift?)",
    "GTM": "Guatemala — 2024 2nd biggest riser",
    "VUT": "Vanuatu — 2024 biggest riser",
    "ISR": "Israel — historically most isolated",
    "USA": "United States — perennial bottom dweller",
    "UKR": "Ukraine — geopolitical focal point",
    "RUS": "Russia — geopolitical focal point",
    "PRY": "Paraguay — 2024 notable faller",
}

for iso, desc in spotlight_countries.items():
    subsep(desc)
    for yr in [2022, 2023, 2024, 2025]:
        row = annual[(annual["Country name"]==iso) & (annual["Year"]==yr)]
        if row.empty:
            print(f"    {yr}: no data")
            continue
        r = row.iloc[0]
        p1r = f"#{int(r['Pillar 1 Rank'])}" if pd.notna(r.get('Pillar 1 Rank')) else "N/A"
        p2r = f"#{int(r['Pillar 2 Rank'])}" if pd.notna(r.get('Pillar 2 Rank')) else "N/A"
        p3r = f"#{int(r['Pillar 3 Rank'])}" if pd.notna(r.get('Pillar 3 Rank')) else "N/A"
        ov_r = f"#{int(r['Overall Rank'])}" if pd.notna(r.get('Overall Rank')) else "N/A"
        print(f"    {yr}: Overall={r['Total Index Average']:.1f} (Rank {ov_r})  "
              f"P1={r['Pillar 1 Score']:.1f} ({p1r})  P2={r['Pillar 2 Score']:.1f} ({p2r})  "
              f"P3={r['Pillar 3 Score']:.1f} ({p3r})  "
              f"Y={int(r['Yes Votes'])} N={int(r['No Votes'])} A={int(r['Abstain Votes'])}")

# ═══════════════════════════════════════════════════════════════════════
# 10. ISOLATION DETECTION — SCORES BELOW 50
# ═══════════════════════════════════════════════════════════════════════
sep("10. ISOLATION DETECTION — OVERALL SCORE < 50")

isolated = a25[a25["Total Index Average"] < 50].sort_values("Total Index Average")
print(f"  {len(isolated)} countries with Overall Score < 50 in 2025:")
print(f"  (Scores <50 indicate extreme isolation or strong multilateral defiance)")
print()
for _, r in isolated.iterrows():
    region = REGION_MAP.get(r["Country name"], "?")
    print(f"    {r['Country name']:<6} Score={r['Total Index Average']:.1f}  "
          f"Rank=#{int(r['Overall Rank'])}  Region={region}  "
          f"Y={int(r['Yes Votes'])} N={int(r['No Votes'])} A={int(r['Abstain Votes'])}")

# Compare to 2024
isolated_24 = a24[a24["Total Index Average"] < 50].sort_values("Total Index Average")
print(f"\n  2024 had {len(isolated_24)} countries below 50:")
for _, r in isolated_24.iterrows():
    print(f"    {r['Country name']:<6} Score={r['Total Index Average']:.1f}")

# ═══════════════════════════════════════════════════════════════════════
# 11. PAIRWISE SIMILARITY — BIGGEST BILATERAL SHIFTS
# ═══════════════════════════════════════════════════════════════════════
sep("11. PAIRWISE SIMILARITY — BIGGEST BILATERAL SHIFTS (2024→2025)")

pw_merged = p25.merge(p24, on=["Country1_ISO3", "Country2_ISO3"], suffixes=("_25", "_24"))
pw_merged["sim_change"] = pw_merged["CosineSimilarity_25"] - pw_merged["CosineSimilarity_24"]

# Filter to pairs where both countries existed (non-zero similarity in at least one year)
pw_active = pw_merged[
    (pw_merged["CosineSimilarity_25"] > 0) | (pw_merged["CosineSimilarity_24"] > 0)
].copy()

subsep("Top 20 CONVERGENCES (became MORE similar)")
top_converge = pw_active.nlargest(20, "sim_change")
print(f"    {'Country1':<8} {'Country2':<8} {'2024':>7} {'2025':>7} {'Change':>8}")
print(f"    {'─'*42}")
for _, r in top_converge.iterrows():
    print(f"    {r['Country1_ISO3']:<8} {r['Country2_ISO3']:<8} {r['CosineSimilarity_24']:>7.3f} {r['CosineSimilarity_25']:>7.3f} {r['sim_change']:>+8.3f}")

subsep("Top 20 DIVERGENCES (became LESS similar)")
top_diverge = pw_active.nsmallest(20, "sim_change")
print(f"    {'Country1':<8} {'Country2':<8} {'2024':>7} {'2025':>7} {'Change':>8}")
print(f"    {'─'*42}")
for _, r in top_diverge.iterrows():
    print(f"    {r['Country1_ISO3']:<8} {r['Country2_ISO3']:<8} {r['CosineSimilarity_24']:>7.3f} {r['CosineSimilarity_25']:>7.3f} {r['sim_change']:>+8.3f}")

# ═══════════════════════════════════════════════════════════════════════
# 12. OUTLIER & INSIGHT DETECTION
# ═══════════════════════════════════════════════════════════════════════
sep("12. OUTLIER & INSIGHT DETECTION")

# 12a. Biggest single-year rank jumps
subsep("12a. Biggest Overall Rank Jumps (2024→2025)")
merged["rank_change"] = merged["Overall Rank_25"] - merged["Overall Rank_24"]
top_rank_rise = merged.nsmallest(10, "rank_change")  # negative = improvement
top_rank_fall = merged.nlargest(10, "rank_change")  # positive = worsening

print("    BIGGEST RANK IMPROVEMENTS:")
for _, r in top_rank_rise.iterrows():
    print(f"    {r['Country name']:<8}: #{int(r['Overall Rank_24'])} → #{int(r['Overall Rank_25'])}  ({int(r['rank_change']):+d})")

print("\n    BIGGEST RANK DECLINES:")
for _, r in top_rank_fall.iterrows():
    print(f"    {r['Country name']:<8}: #{int(r['Overall Rank_24'])} → #{int(r['Overall Rank_25'])}  ({int(r['rank_change']):+d})")

# 12b. Countries that flipped from zero No votes to many, or vice versa
subsep("12b. No-vote Flips (countries that started or stopped voting No)")
merged_votes = a25.merge(a24, on="Country name", suffixes=("_25", "_24"))
merged_votes["no_change"] = merged_votes["No Votes_25"] - merged_votes["No Votes_24"]

# Started voting No (had 0 in 2024, >0 in 2025)
started_no = merged_votes[(merged_votes["No Votes_24"] == 0) & (merged_votes["No Votes_25"] > 0)]
started_no = started_no.sort_values("No Votes_25", ascending=False)
print(f"    Countries that started voting No (0 in 2024 → >0 in 2025): {len(started_no)}")
for _, r in started_no.head(15).iterrows():
    print(f"      {r['Country name']:<8}: 0 → {int(r['No Votes_25'])} No votes")

# Stopped voting No (had >0 in 2024, 0 in 2025)
stopped_no = merged_votes[(merged_votes["No Votes_24"] > 0) & (merged_votes["No Votes_25"] == 0)]
stopped_no = stopped_no.sort_values("No Votes_24", ascending=False)
print(f"\n    Countries that stopped voting No (>0 in 2024 → 0 in 2025): {len(stopped_no)}")
for _, r in stopped_no.head(15).iterrows():
    print(f"      {r['Country name']:<8}: {int(r['No Votes_24'])} → 0 No votes")

# Biggest increases in No voting
print(f"\n    Biggest INCREASE in No votes:")
for _, r in merged_votes.nlargest(10, "no_change").iterrows():
    print(f"      {r['Country name']:<8}: {int(r['No Votes_24'])} → {int(r['No Votes_25'])} ({int(r['no_change']):+d})")

# Biggest decreases in No voting
print(f"\n    Biggest DECREASE in No votes:")
for _, r in merged_votes.nsmallest(10, "no_change").iterrows():
    print(f"      {r['Country name']:<8}: {int(r['No Votes_24'])} → {int(r['No Votes_25'])} ({int(r['no_change']):+d})")

# 12c. 3-sigma outliers on score changes
subsep("12c. 3-sigma Outliers in Score Changes")
for col_name, col in [("Overall", "Total Index Average"),
                       ("Pillar 1", "Pillar 1 Score"),
                       ("Pillar 2", "Pillar 2 Score"),
                       ("Pillar 3", "Pillar 3 Score")]:
    diff = merged[f"{col}_25"] - merged[f"{col}_24"]
    mu, sigma = diff.mean(), diff.std()
    outliers = merged[abs(diff - mu) > 3 * sigma]
    if len(outliers) > 0:
        print(f"    {col_name} — {len(outliers)} outlier(s) beyond 3σ (mean={mu:.1f}, σ={sigma:.1f}):")
        for _, r in outliers.iterrows():
            chg = r[f"{col}_25"] - r[f"{col}_24"]
            print(f"      {r['Country name']:<8}: {r[f'{col}_24']:.1f} → {r[f'{col}_25']:.1f} ({chg:+.1f})")
    else:
        print(f"    {col_name} — no 3σ outliers (mean={mu:.1f}, σ={sigma:.1f})")

# 12d. Country-topic deep dive: biggest per-country topic shifts
subsep("12d. Biggest Per-Country Topic Shifts (2024→2025)")
t_merged = t25.merge(t24, on=["Country", "TopicTag"], suffixes=("_25", "_24"), how="inner")
t_merged["yes_rate_25"] = 100 * t_merged["YesVotes_Topic_25"] / t_merged["TotalVotes_Topic_25"]
t_merged["yes_rate_24"] = 100 * t_merged["YesVotes_Topic_24"] / t_merged["TotalVotes_Topic_24"]
t_merged["topic_shift"] = t_merged["yes_rate_25"] - t_merged["yes_rate_24"]
# Filter to topics with at least 3 votes in both years for significance
t_sig = t_merged[(t_merged["TotalVotes_Topic_25"] >= 3) & (t_merged["TotalVotes_Topic_24"] >= 3)]

print("    Top 20 biggest POSITIVE topic shifts (country went from No→Yes on a topic):")
for _, r in t_sig.nlargest(20, "topic_shift").iterrows():
    print(f"      {r['Country']:<6} | {r['TopicTag']:<40} | {r['yes_rate_24']:.0f}% → {r['yes_rate_25']:.0f}% ({r['topic_shift']:+.0f})")

print("\n    Top 20 biggest NEGATIVE topic shifts (country went from Yes→No on a topic):")
for _, r in t_sig.nsmallest(20, "topic_shift").iterrows():
    print(f"      {r['Country']:<6} | {r['TopicTag']:<40} | {r['yes_rate_24']:.0f}% → {r['yes_rate_25']:.0f}% ({r['topic_shift']:+.0f})")

# 12e. NATO alignment analysis
subsep("12e. NATO Alignment in 2025")
nato_codes = [
    "USA", "GBR", "FRA", "DEU", "CAN", "ITA", "ESP", "NLD", "BEL", "TUR",
    "POL", "NOR", "DNK", "PRT", "CZE", "HUN", "GRC", "ISL", "LUX", "BGR",
    "ROU", "SVK", "SVN", "HRV", "ALB", "MNE", "MKD", "LTU", "LVA", "EST",
    "FIN", "SWE"
]
nato_25 = a25[a25["Country name"].isin(nato_codes)].sort_values("Overall Rank")
print(f"    NATO members in 2025 rankings (n={len(nato_25)}):")
print(f"    {'Country':<8} {'Rank':>6} {'Score':>7} {'P3':>7} {'Yes%':>6}")
print(f"    {'─'*38}")
for _, r in nato_25.iterrows():
    yes_pct = 100 * r["Yes Votes"] / r["Total Votes in Year"] if r["Total Votes in Year"] > 0 else 0
    print(f"    {r['Country name']:<8} #{int(r['Overall Rank']):>4}  {r['Total Index Average']:>6.1f} {r['Pillar 3 Score']:>6.1f} {yes_pct:>5.1f}%")

# 12f. Top/Bottom 10 overall
subsep("12f. COMPLETE TOP 10 and BOTTOM 10 (Overall Score, 2025)")
top10 = a25.nlargest(10, "Total Index Average")
bot10 = a25.nsmallest(10, "Total Index Average")

print("    TOP 10:")
for _, r in top10.iterrows():
    region = REGION_MAP.get(r["Country name"], "?")
    print(f"    #{int(r['Overall Rank']):<4} {r['Country name']:<6} {r['Total Index Average']:>6.1f}  "
          f"P1={r['Pillar 1 Score']:.1f} P2={r['Pillar 2 Score']:.1f} P3={r['Pillar 3 Score']:.1f}  "
          f"[{region}]")

print("\n    BOTTOM 10:")
for _, r in bot10.iterrows():
    region = REGION_MAP.get(r["Country name"], "?")
    print(f"    #{int(r['Overall Rank']):<4} {r['Country name']:<6} {r['Total Index Average']:>6.1f}  "
          f"P1={r['Pillar 1 Score']:.1f} P2={r['Pillar 2 Score']:.1f} P3={r['Pillar 3 Score']:.1f}  "
          f"[{region}]")

# 12g. "Three Coalitions" analysis from 2024 report
subsep("12g. Coalition Analysis (US/Israel bloc vs Russia bloc vs majority)")
us_israel = ["USA", "ISR"]
russia_bloc = ["RUS", "BLR", "PRK", "SYR", "NIC"]  # traditional allies
rest = [c for c in a25["Country name"].tolist() if c not in us_israel + russia_bloc]

for label, codes in [("US/Israel bloc", us_israel),
                      ("Russia & allies", russia_bloc),
                      ("Rest of world", rest)]:
    sub = a25[a25["Country name"].isin(codes)]
    avg_score = sub["Total Index Average"].mean()
    avg_p3 = sub["Pillar 3 Score"].mean()
    avg_yes_pct = 100 * sub["Yes Votes"].sum() / sub["Total Votes in Year"].sum()
    print(f"    {label:<22}: Avg Score={avg_score:.1f}, Avg P3={avg_p3:.1f}, Yes%={avg_yes_pct:.1f}%  (n={len(sub)})")

# ═══════════════════════════════════════════════════════════════════════
# 13. SYNTHESIS / KEY FINDINGS SUMMARY
# ═══════════════════════════════════════════════════════════════════════
sep("13. KEY FINDINGS SUMMARY")

print("""
  This section summarizes the most notable insights from the 2025 analysis.
  Refer to numbered sections above for detailed data.
""")

# Auto-generate key stats
total_fell = (merged["Total Index Average_25"] < merged["Total Index Average_24"]).sum()
pct_fell = 100 * total_fell / len(merged)
biggest_riser = merged.loc[merged["_diff"].idxmax()]
biggest_faller = merged.loc[merged["_diff"].idxmin()]
no_vote_countries_25 = len(no_zero)
isolated_count = len(isolated)

print(f"  1. {pct_fell:.0f}% of countries saw their overall alignment fall in 2025")
print(f"     (vs 44% in 2024, 30% in 2023)")
print(f"  2. {total_res_voted} GA resolutions put to vote in 2025 (vs 95 in 2024)")
print(f"  3. Overall voting: {100*total_yes/total_votes:.1f}% Yes, {100*total_no/total_votes:.1f}% No, {100*total_abs/total_votes:.1f}% Abstain")
print(f"  4. {no_vote_countries_25} countries never voted No (vs 60 in 2024)")
print(f"  5. Biggest overall riser: {biggest_riser['Country name']} ({biggest_riser['_diff']:+.1f})")
print(f"  6. Biggest overall faller: {biggest_faller['Country name']} ({biggest_faller['_diff']:+.1f})")
print(f"  7. {isolated_count} countries scored below 50 (isolation threshold)")

# P5 summary
for iso, name in p5_codes.items():
    r = a25[a25["Country name"]==iso].iloc[0]
    print(f"  8. {name}: Rank #{int(r['Overall Rank'])}, Score {r['Total Index Average']:.1f}")

print("\n  ── See sections 1-12 for full details ──")
print()
