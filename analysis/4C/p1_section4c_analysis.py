"""
Section 4C — P1 Internal Alignment: Full Analysis from Local CSVs
=================================================================
Produces all CSV outputs needed for a writer to compose the 2025 report's
Section 4C ("P1 Trends – Internal Alignment").

Canonical data sources (data/ folder):
  - annual_scores (4).csv
  - pairwise_similarity_yearly (4).csv
  - topic_votes_yearly (4).csv
  - un_votes_with_sc (1).csv

Outputs (analysis/4C/):
  01_p1_world_avg_trend.csv           — World avg P1, 1946–2025
  02_p1_country_shifts_2024_2025.csv  — Per-country P1 change (2024 → 2025)
  03_p1_big_movers.csv                — Countries with >10-pt P1 swing + vote detail
  04_p1_participation_analysis.csv    — Participation changes correlated with P1
  05_p1_topic_alignment_changes.csv   — Per-topic Yes% shift 2024 → 2025
  06_p1_topic_new_dropped.csv         — Topics that appeared / disappeared
  07_p1_pairwise_biggest_shifts.csv   — Largest pairwise similarity changes
  08_p1_us_alliance_shifts.csv        — USA pairwise similarity with key partners
  09_p1_regional_summary.csv          — Regional avg P1, 2024 vs 2025
  10_p1_divisive_resolutions_2025.csv — Most divisive 2025 resolutions
  11_p1_country_vote_profile_2025.csv — Full vote breakdown per country (2025)
  12_p1_leadership_change_candidates.csv — Countries w/ known leadership changes
  13_p1_spotty_voting_candidates.csv  — Countries w/ large participation swings
  14_p1_alliance_pattern_shifts.csv   — Countries that moved toward/away from blocs
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent.parent / "data"
OUT_DIR = Path(__file__).parent

def separator(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")

# ── ISO3 → Region mapping ────────────────────────────────────────────────
# Flat mapping from ISO3 to sub-region (matching UN M49 classification)
ISO3_TO_REGION = {
    # Northern Africa
    'DZA': 'Northern Africa', 'EGY': 'Northern Africa', 'LBY': 'Northern Africa',
    'MAR': 'Northern Africa', 'SDN': 'Northern Africa', 'TUN': 'Northern Africa',
    # Eastern Africa
    'BDI': 'Eastern Africa', 'COM': 'Eastern Africa', 'DJI': 'Eastern Africa',
    'ERI': 'Eastern Africa', 'ETH': 'Eastern Africa', 'KEN': 'Eastern Africa',
    'MDG': 'Eastern Africa', 'MWI': 'Eastern Africa', 'MUS': 'Eastern Africa',
    'MOZ': 'Eastern Africa', 'RWA': 'Eastern Africa', 'SYC': 'Eastern Africa',
    'SOM': 'Eastern Africa', 'SSD': 'Eastern Africa', 'UGA': 'Eastern Africa',
    'TZA': 'Eastern Africa', 'ZMB': 'Eastern Africa', 'ZWE': 'Eastern Africa',
    # Middle Africa
    'AGO': 'Middle Africa', 'CMR': 'Middle Africa', 'CAF': 'Middle Africa',
    'TCD': 'Middle Africa', 'COG': 'Middle Africa', 'COD': 'Middle Africa',
    'GNQ': 'Middle Africa', 'GAB': 'Middle Africa', 'STP': 'Middle Africa',
    # Southern Africa
    'BWA': 'Southern Africa', 'SWZ': 'Southern Africa', 'LSO': 'Southern Africa',
    'NAM': 'Southern Africa', 'ZAF': 'Southern Africa',
    # Western Africa
    'BEN': 'Western Africa', 'BFA': 'Western Africa', 'CPV': 'Western Africa',
    'CIV': 'Western Africa', 'GMB': 'Western Africa', 'GHA': 'Western Africa',
    'GIN': 'Western Africa', 'GNB': 'Western Africa', 'LBR': 'Western Africa',
    'MLI': 'Western Africa', 'MRT': 'Western Africa', 'NER': 'Western Africa',
    'NGA': 'Western Africa', 'SEN': 'Western Africa', 'SLE': 'Western Africa',
    'TGO': 'Western Africa',
    # Caribbean
    'ATG': 'Caribbean', 'BHS': 'Caribbean', 'BRB': 'Caribbean',
    'CUB': 'Caribbean', 'DMA': 'Caribbean', 'DOM': 'Caribbean',
    'GRD': 'Caribbean', 'HTI': 'Caribbean', 'JAM': 'Caribbean',
    'KNA': 'Caribbean', 'LCA': 'Caribbean', 'VCT': 'Caribbean',
    'TTO': 'Caribbean',
    # Central America
    'BLZ': 'Central America', 'CRI': 'Central America', 'SLV': 'Central America',
    'GTM': 'Central America', 'HND': 'Central America', 'MEX': 'Central America',
    'NIC': 'Central America', 'PAN': 'Central America',
    # South America
    'ARG': 'South America', 'BOL': 'South America', 'BRA': 'South America',
    'CHL': 'South America', 'COL': 'South America', 'ECU': 'South America',
    'GUY': 'South America', 'PRY': 'South America', 'PER': 'South America',
    'SUR': 'South America', 'URY': 'South America', 'VEN': 'South America',
    # Northern America
    'CAN': 'Northern America', 'USA': 'Northern America',
    # Central Asia
    'KAZ': 'Central Asia', 'KGZ': 'Central Asia', 'TJK': 'Central Asia',
    'TKM': 'Central Asia', 'UZB': 'Central Asia',
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
    # Oceania — Australia/New Zealand
    'AUS': 'Australia and New Zealand', 'NZL': 'Australia and New Zealand',
    # Melanesia
    'FJI': 'Melanesia', 'PNG': 'Melanesia', 'SLB': 'Melanesia', 'VUT': 'Melanesia',
    # Micronesia
    'KIR': 'Micronesia', 'MHL': 'Micronesia', 'FSM': 'Micronesia',
    'NRU': 'Micronesia', 'PLW': 'Micronesia',
    # Polynesia
    'WSM': 'Polynesia', 'TON': 'Polynesia', 'TUV': 'Polynesia',
}

# Broader region grouping for summary
SUBREGION_TO_BROAD = {
    'Northern Africa': 'Africa',
    'Eastern Africa': 'Sub-Saharan Africa', 'Middle Africa': 'Sub-Saharan Africa',
    'Southern Africa': 'Sub-Saharan Africa', 'Western Africa': 'Sub-Saharan Africa',
    'Caribbean': 'Latin America & Caribbean',
    'Central America': 'Latin America & Caribbean',
    'South America': 'Latin America & Caribbean',
    'Northern America': 'Northern America',
    'Central Asia': 'Central Asia',
    'Eastern Asia': 'Eastern Asia',
    'South-eastern Asia': 'South-eastern Asia',
    'Southern Asia': 'Southern Asia',
    'Western Asia': 'Western Asia',
    'Eastern Europe': 'Eastern Europe',
    'Northern Europe': 'Northern Europe',
    'Southern Europe': 'Southern Europe',
    'Western Europe': 'Western Europe',
    'Australia and New Zealand': 'Oceania',
    'Melanesia': 'Oceania', 'Micronesia': 'Oceania', 'Polynesia': 'Oceania',
}


def load_data():
    """Load all four canonical CSVs."""
    separator("Loading data")
    annual = pd.read_csv(DATA_DIR / "annual_scores (4).csv")
    pairwise = pd.read_csv(DATA_DIR / "pairwise_similarity_yearly (4).csv")
    topics = pd.read_csv(DATA_DIR / "topic_votes_yearly (4).csv")
    raw_votes = pd.read_csv(DATA_DIR / "un_votes_with_sc (1).csv")
    print(f"  annual_scores:  {len(annual):,} rows, years {annual['Year'].min()}–{annual['Year'].max()}")
    print(f"  pairwise:       {len(pairwise):,} rows")
    print(f"  topic_votes:    {len(topics):,} rows")
    print(f"  un_votes_raw:   {len(raw_votes):,} rows")
    return annual, pairwise, topics, raw_votes


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 01: World Average P1 Trend
# ═══════════════════════════════════════════════════════════════════════════
def output_01_world_avg_trend(annual):
    separator("01 — World Average P1 Trend")
    # Exclude 2026 (partial year with only 4 resolutions)
    df = annual[annual['Year'] <= 2025].copy()
    trend = df.groupby('Year').agg(
        world_avg_p1=('Pillar 1 Score', 'mean'),
        median_p1=('Pillar 1 Score', 'median'),
        std_p1=('Pillar 1 Score', 'std'),
        num_countries=('Country name', 'nunique'),
        avg_total_votes=('Total Votes in Year', 'mean'),
    ).reset_index()
    trend['world_avg_p1'] = trend['world_avg_p1'].round(2)
    trend['median_p1'] = trend['median_p1'].round(2)
    trend['std_p1'] = trend['std_p1'].round(2)
    trend['avg_total_votes'] = trend['avg_total_votes'].round(1)
    trend['yoy_change'] = trend['world_avg_p1'].diff().round(2)
    trend['rolling_3y'] = trend['world_avg_p1'].rolling(3, center=True).mean().round(2)

    out = OUT_DIR / "01_p1_world_avg_trend.csv"
    trend.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(trend)} years)")

    # Print recent years
    recent = trend[trend['Year'] >= 2020]
    for _, r in recent.iterrows():
        chg = f"{r['yoy_change']:+.2f}" if pd.notna(r['yoy_change']) else "—"
        print(f"    {int(r['Year'])}: avg={r['world_avg_p1']:.2f}  change={chg}  countries={int(r['num_countries'])}  avg_votes={r['avg_total_votes']:.0f}")

    # Key metric
    p1_24 = trend.loc[trend['Year'] == 2024, 'world_avg_p1'].values[0]
    p1_25 = trend.loc[trend['Year'] == 2025, 'world_avg_p1'].values[0]
    print(f"\n  KEY METRIC: {p1_25 - p1_24:+.2f} points (2024 {p1_24:.2f} → 2025 {p1_25:.2f})")
    return trend


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 02: Country-Level P1 Shifts (2024 → 2025)
# ═══════════════════════════════════════════════════════════════════════════
def output_02_country_shifts(annual):
    separator("02 — Country-Level P1 Shifts (2024 → 2025)")
    d24 = annual[annual['Year'] == 2024][['Country name', 'Pillar 1 Score',
        'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']].copy()
    d24.columns = ['iso3', 'p1_2024', 'yes_2024', 'no_2024', 'abstain_2024', 'total_2024']

    d25 = annual[annual['Year'] == 2025][['Country name', 'Pillar 1 Score',
        'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']].copy()
    d25.columns = ['iso3', 'p1_2025', 'yes_2025', 'no_2025', 'abstain_2025', 'total_2025']

    merged = pd.merge(d24, d25, on='iso3', how='outer')
    merged['p1_change'] = (merged['p1_2025'] - merged['p1_2024']).round(2)
    merged['total_change'] = merged['total_2025'] - merged['total_2024']
    merged['yes_pct_2024'] = (merged['yes_2024'] / merged['total_2024'] * 100).round(1)
    merged['yes_pct_2025'] = (merged['yes_2025'] / merged['total_2025'] * 100).round(1)
    merged['yes_pct_change'] = (merged['yes_pct_2025'] - merged['yes_pct_2024']).round(1)
    merged['region'] = merged['iso3'].map(ISO3_TO_REGION)
    merged['broad_region'] = merged['region'].map(SUBREGION_TO_BROAD)
    merged = merged.sort_values('p1_change', ascending=True)

    out = OUT_DIR / "02_p1_country_shifts_2024_2025.csv"
    merged.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(merged)} countries)")

    # Show top decliners and gainers
    print("\n  Top 10 DECLINERS:")
    for _, r in merged.head(10).iterrows():
        print(f"    {r['iso3']}: {r['p1_change']:+.1f} ({r['p1_2024']:.1f} → {r['p1_2025']:.1f}) "
              f"votes: {int(r['total_2024']) if pd.notna(r['total_2024']) else '?'} → {int(r['total_2025']) if pd.notna(r['total_2025']) else '?'}")
    print("\n  Top 10 GAINERS:")
    for _, r in merged.tail(10).iloc[::-1].iterrows():
        print(f"    {r['iso3']}: {r['p1_change']:+.1f} ({r['p1_2024']:.1f} → {r['p1_2025']:.1f}) "
              f"votes: {int(r['total_2024']) if pd.notna(r['total_2024']) else '?'} → {int(r['total_2025']) if pd.notna(r['total_2025']) else '?'}")
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 03: Big Movers (>10pt P1 swing) with vote detail
# ═══════════════════════════════════════════════════════════════════════════
def output_03_big_movers(shifts):
    separator("03 — Big Movers (>10pt P1 swing)")
    big = shifts[shifts['p1_change'].abs() > 10].copy()
    big['direction'] = np.where(big['p1_change'] > 0, 'GAINER', 'DECLINER')
    big = big.sort_values('p1_change')

    out = OUT_DIR / "03_p1_big_movers.csv"
    big.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(big)} countries)")
    print(f"    Decliners: {(big['direction'] == 'DECLINER').sum()}")
    print(f"    Gainers:   {(big['direction'] == 'GAINER').sum()}")
    return big


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 04: Participation Analysis
# ═══════════════════════════════════════════════════════════════════════════
def output_04_participation(shifts):
    separator("04 — Participation Analysis")
    df = shifts.dropna(subset=['total_2024', 'total_2025']).copy()
    df['participation_change_pct'] = ((df['total_2025'] - df['total_2024']) / df['total_2024'] * 100).round(1)
    df = df.sort_values('participation_change_pct')

    out = OUT_DIR / "04_p1_participation_analysis.csv"
    df[['iso3', 'total_2024', 'total_2025', 'total_change',
        'participation_change_pct', 'p1_2024', 'p1_2025', 'p1_change',
        'region', 'broad_region']].to_csv(out, index=False)
    print(f"  ✓ Saved {out.name}")

    # Flag spotty voters: large participation change AND small sample in one year
    spotty = df[(df['total_2025'] < 50) | (df['total_2024'] < 50) |
                (df['participation_change_pct'].abs() > 50)]
    print(f"  Spotty voting candidates: {len(spotty)} countries")
    for _, r in spotty.sort_values('p1_change').head(10).iterrows():
        print(f"    {r['iso3']}: votes {int(r['total_2024'])}→{int(r['total_2025'])} "
              f"({r['participation_change_pct']:+.0f}%), P1 change {r['p1_change']:+.1f}")
    return df


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 05: Topic-Level Alignment Changes (Yes% by topic, 2024 → 2025)
# ═══════════════════════════════════════════════════════════════════════════
def output_05_topic_changes(topics):
    separator("05 — Topic-Level Alignment Changes")
    for year in [2024, 2025]:
        sub = topics[topics['Year'] == year]
        print(f"  {year}: {sub['TopicTag'].nunique()} topics, {len(sub)} rows")

    # Aggregate per topic per year
    agg = topics[topics['Year'].isin([2024, 2025])].groupby(['Year', 'TopicTag']).agg(
        total_yes=('YesVotes_Topic', 'sum'),
        total_no=('NoVotes_Topic', 'sum'),
        total_abstain=('AbstainVotes_Topic', 'sum'),
        total_votes=('TotalVotes_Topic', 'sum'),
        num_countries=('Country', 'nunique')
    ).reset_index()
    agg['yes_pct'] = (agg['total_yes'] / agg['total_votes'] * 100).round(2)

    # Pivot for comparison
    p24 = agg[agg['Year'] == 2024][['TopicTag', 'yes_pct', 'total_votes', 'num_countries']].copy()
    p24.columns = ['TopicTag', 'yes_pct_2024', 'total_votes_2024', 'num_countries_2024']
    p25 = agg[agg['Year'] == 2025][['TopicTag', 'yes_pct', 'total_votes', 'num_countries']].copy()
    p25.columns = ['TopicTag', 'yes_pct_2025', 'total_votes_2025', 'num_countries_2025']

    compare = pd.merge(p24, p25, on='TopicTag', how='outer')
    compare['yes_pct_change'] = (compare['yes_pct_2025'] - compare['yes_pct_2024']).round(2)
    compare = compare.sort_values('yes_pct_change', ascending=True)

    out = OUT_DIR / "05_p1_topic_alignment_changes.csv"
    compare.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(compare)} topics)")

    # Show biggest shifts
    both = compare.dropna(subset=['yes_pct_2024', 'yes_pct_2025'])
    print(f"\n  Top 5 DECLINING topics (present in both years):")
    for _, r in both.head(5).iterrows():
        print(f"    {r['TopicTag']}: {r['yes_pct_change']:+.1f}pp ({r['yes_pct_2024']:.1f}% → {r['yes_pct_2025']:.1f}%)")
    print(f"\n  Top 5 GROWING topics:")
    for _, r in both.tail(5).iloc[::-1].iterrows():
        print(f"    {r['TopicTag']}: {r['yes_pct_change']:+.1f}pp ({r['yes_pct_2024']:.1f}% → {r['yes_pct_2025']:.1f}%)")
    return compare


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 06: New & Dropped Topics
# ═══════════════════════════════════════════════════════════════════════════
def output_06_topic_new_dropped(topics):
    separator("06 — New & Dropped Topics")
    tags_24 = set(topics[topics['Year'] == 2024]['TopicTag'].unique())
    tags_25 = set(topics[topics['Year'] == 2025]['TopicTag'].unique())

    new_tags = tags_25 - tags_24
    dropped_tags = tags_24 - tags_25

    # Get vote data for new tags
    rows = []
    for tag in sorted(new_tags):
        sub = topics[(topics['Year'] == 2025) & (topics['TopicTag'] == tag)]
        rows.append({
            'TopicTag': tag, 'status': 'NEW_IN_2025',
            'total_votes': sub['TotalVotes_Topic'].sum(),
            'yes_pct': round(sub['YesVotes_Topic'].sum() / sub['TotalVotes_Topic'].sum() * 100, 1) if sub['TotalVotes_Topic'].sum() > 0 else None,
            'num_countries': sub['Country'].nunique()
        })
    for tag in sorted(dropped_tags):
        sub = topics[(topics['Year'] == 2024) & (topics['TopicTag'] == tag)]
        rows.append({
            'TopicTag': tag, 'status': 'DROPPED_FROM_2024',
            'total_votes': sub['TotalVotes_Topic'].sum(),
            'yes_pct': round(sub['YesVotes_Topic'].sum() / sub['TotalVotes_Topic'].sum() * 100, 1) if sub['TotalVotes_Topic'].sum() > 0 else None,
            'num_countries': sub['Country'].nunique()
        })

    out_df = pd.DataFrame(rows)
    out = OUT_DIR / "06_p1_topic_new_dropped.csv"
    out_df.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name}")
    print(f"    New in 2025: {len(new_tags)} topics")
    for tag in sorted(new_tags):
        r = out_df[out_df['TopicTag'] == tag].iloc[0]
        print(f"      {tag} (Yes%={r['yes_pct']}%, votes={int(r['total_votes'])})")
    print(f"    Dropped from 2024: {len(dropped_tags)} topics")
    for tag in sorted(dropped_tags):
        print(f"      {tag}")
    return out_df


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 07: Pairwise Similarity Biggest Shifts
# ═══════════════════════════════════════════════════════════════════════════
def output_07_pairwise_shifts(pairwise):
    separator("07 — Pairwise Similarity Biggest Shifts")
    pw24 = pairwise[pairwise['Year'] == 2024][['Country1_ISO3', 'Country2_ISO3', 'CosineSimilarity']].copy()
    pw24.columns = ['c1', 'c2', 'sim_2024']
    pw25 = pairwise[pairwise['Year'] == 2025][['Country1_ISO3', 'Country2_ISO3', 'CosineSimilarity']].copy()
    pw25.columns = ['c1', 'c2', 'sim_2025']

    merged = pd.merge(pw24, pw25, on=['c1', 'c2'], how='inner')
    merged['sim_change'] = (merged['sim_2025'] - merged['sim_2024']).round(4)

    # Top diverging and converging pairs
    merged_sorted = merged.sort_values('sim_change')
    top_diverging = merged_sorted.head(50)
    top_converging = merged_sorted.tail(50).iloc[::-1]
    combined = pd.concat([top_diverging, top_converging])

    out = OUT_DIR / "07_p1_pairwise_biggest_shifts.csv"
    combined.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} (top 50 diverging + top 50 converging)")

    print("\n  Top 10 DIVERGING pairs:")
    for _, r in top_diverging.head(10).iterrows():
        print(f"    {r['c1']}-{r['c2']}: {r['sim_change']:+.3f} ({r['sim_2024']:.3f} → {r['sim_2025']:.3f})")
    print("\n  Top 10 CONVERGING pairs:")
    for _, r in top_converging.head(10).iterrows():
        print(f"    {r['c1']}-{r['c2']}: {r['sim_change']:+.3f} ({r['sim_2024']:.3f} → {r['sim_2025']:.3f})")
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 08: USA Alliance Shifts
# ═══════════════════════════════════════════════════════════════════════════
def output_08_us_alliance_shifts(pairwise):
    separator("08 — USA Alliance Shifts")
    KEY_PARTNERS = ['GBR', 'CAN', 'AUS', 'FRA', 'DEU', 'JPN', 'KOR', 'ITA',
                    'NLD', 'ESP', 'POL', 'CZE', 'ISR', 'IND', 'BRA', 'MEX',
                    'SAU', 'ARE', 'TUR', 'UKR', 'CHN', 'RUS', 'ARG', 'NGA',
                    'ZAF', 'EGY', 'IDN', 'NOR', 'SWE', 'DNK', 'HUN', 'SVK']

    # Get US rows (US can be c1 or c2)
    us_24 = pairwise[(pairwise['Year'] == 2024) &
                      ((pairwise['Country1_ISO3'] == 'USA') | (pairwise['Country2_ISO3'] == 'USA'))].copy()
    us_25 = pairwise[(pairwise['Year'] == 2025) &
                      ((pairwise['Country1_ISO3'] == 'USA') | (pairwise['Country2_ISO3'] == 'USA'))].copy()

    def normalize_us(row):
        if row['Country1_ISO3'] == 'USA':
            return row['Country2_ISO3']
        return row['Country1_ISO3']

    us_24['partner'] = us_24.apply(normalize_us, axis=1)
    us_25['partner'] = us_25.apply(normalize_us, axis=1)

    us_24_s = us_24[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': 'sim_2024'})
    us_25_s = us_25[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': 'sim_2025'})

    us_merged = pd.merge(us_24_s, us_25_s, on='partner', how='outer')
    us_merged['sim_change'] = (us_merged['sim_2025'] - us_merged['sim_2024']).round(4)
    us_merged['is_key_partner'] = us_merged['partner'].isin(KEY_PARTNERS)
    us_merged['region'] = us_merged['partner'].map(ISO3_TO_REGION)
    us_merged = us_merged.sort_values('sim_change')

    out = OUT_DIR / "08_p1_us_alliance_shifts.csv"
    us_merged.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(us_merged)} partners)")

    print("\n  US key partner shifts:")
    key = us_merged[us_merged['is_key_partner']].sort_values('sim_change')
    for _, r in key.iterrows():
        print(f"    USA-{r['partner']}: {r['sim_change']:+.4f} ({r['sim_2024']:.3f} → {r['sim_2025']:.3f})")

    # Also do the same for CHN and RUS to see bloc dynamics
    for anchor in ['CHN', 'RUS']:
        a24 = pairwise[(pairwise['Year'] == 2024) &
                        ((pairwise['Country1_ISO3'] == anchor) | (pairwise['Country2_ISO3'] == anchor))].copy()
        a25 = pairwise[(pairwise['Year'] == 2025) &
                        ((pairwise['Country1_ISO3'] == anchor) | (pairwise['Country2_ISO3'] == anchor))].copy()
        def normalize_a(row):
            if row['Country1_ISO3'] == anchor:
                return row['Country2_ISO3']
            return row['Country1_ISO3']
        a24['partner'] = a24.apply(normalize_a, axis=1)
        a25['partner'] = a25.apply(normalize_a, axis=1)
        a24_s = a24[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': f'sim_{anchor}_2024'})
        a25_s = a25[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': f'sim_{anchor}_2025'})
        am = pd.merge(a24_s, a25_s, on='partner', how='outer')
        am[f'sim_{anchor}_change'] = (am[f'sim_{anchor}_2025'] - am[f'sim_{anchor}_2024']).round(4)
        # Merge into us_merged
        us_merged = pd.merge(us_merged, am[['partner', f'sim_{anchor}_2024', f'sim_{anchor}_2025', f'sim_{anchor}_change']],
                             on='partner', how='left')

    out2 = OUT_DIR / "08b_p1_bloc_alliance_shifts.csv"
    us_merged.to_csv(out2, index=False)
    print(f"  ✓ Saved {out2.name} (USA + CHN + RUS pairwise shifts)")
    return us_merged


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 09: Regional Summary
# ═══════════════════════════════════════════════════════════════════════════
def output_09_regional(annual):
    separator("09 — Regional Summary")
    d24 = annual[annual['Year'] == 2024].copy()
    d25 = annual[annual['Year'] == 2025].copy()

    for df in [d24, d25]:
        df['subregion'] = df['Country name'].map(ISO3_TO_REGION)
        df['broad_region'] = df['subregion'].map(SUBREGION_TO_BROAD)

    unmapped_24 = d24[d24['broad_region'].isna()]['Country name'].unique()
    unmapped_25 = d25[d25['broad_region'].isna()]['Country name'].unique()
    if len(unmapped_24) > 0 or len(unmapped_25) > 0:
        print(f"  ⚠️ Unmapped countries 2024: {list(unmapped_24)}")
        print(f"  ⚠️ Unmapped countries 2025: {list(unmapped_25)}")

    # Broad region summary
    r24 = d24.groupby('broad_region').agg(
        avg_p1_2024=('Pillar 1 Score', 'mean'),
        median_p1_2024=('Pillar 1 Score', 'median'),
        n_countries_2024=('Country name', 'nunique')
    ).reset_index()
    r25 = d25.groupby('broad_region').agg(
        avg_p1_2025=('Pillar 1 Score', 'mean'),
        median_p1_2025=('Pillar 1 Score', 'median'),
        n_countries_2025=('Country name', 'nunique')
    ).reset_index()

    reg = pd.merge(r24, r25, on='broad_region', how='outer')
    reg['avg_p1_change'] = (reg['avg_p1_2025'] - reg['avg_p1_2024']).round(2)
    reg['median_p1_change'] = (reg['median_p1_2025'] - reg['median_p1_2024']).round(2)
    reg = reg.sort_values('avg_p1_change')
    reg['avg_p1_2024'] = reg['avg_p1_2024'].round(2)
    reg['avg_p1_2025'] = reg['avg_p1_2025'].round(2)
    reg['median_p1_2024'] = reg['median_p1_2024'].round(2)
    reg['median_p1_2025'] = reg['median_p1_2025'].round(2)

    out = OUT_DIR / "09_p1_regional_summary.csv"
    reg.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name}")
    for _, r in reg.iterrows():
        print(f"    {r['broad_region']}: {r['avg_p1_2024']:.1f} → {r['avg_p1_2025']:.1f} ({r['avg_p1_change']:+.1f})")

    # Also subregion level
    sr24 = d24.groupby('subregion').agg(
        avg_p1_2024=('Pillar 1 Score', 'mean'),
        n_countries_2024=('Country name', 'nunique')
    ).reset_index()
    sr25 = d25.groupby('subregion').agg(
        avg_p1_2025=('Pillar 1 Score', 'mean'),
        n_countries_2025=('Country name', 'nunique')
    ).reset_index()
    sreg = pd.merge(sr24, sr25, on='subregion', how='outer')
    sreg['avg_p1_change'] = (sreg['avg_p1_2025'] - sreg['avg_p1_2024']).round(2)
    sreg = sreg.sort_values('avg_p1_change')

    out2 = OUT_DIR / "09b_p1_subregional_summary.csv"
    sreg.to_csv(out2, index=False)
    print(f"  ✓ Saved {out2.name}")
    return reg


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 10: Most Divisive Resolutions in 2025
# ═══════════════════════════════════════════════════════════════════════════
def output_10_divisive_resolutions(raw_votes):
    separator("10 — Most Divisive Resolutions (2025)")
    # Filter to 2025 GA resolutions (sc_flag == 0)
    df = raw_votes.copy()
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', utc=True)
    df['Year'] = df['Date'].dt.year

    # Get 2025 resolutions that are GA (sc_flag=0)
    ga25 = df[(df['Year'] == 2025) & (df['sc_flag'] == 0)].copy()
    # Also include ES- (emergency special session) resolutions from 2025
    es = df[df['Resolution'].str.contains('ES-', na=False) & (df['Year'] == 2025)]
    ga25 = pd.concat([ga25, es]).drop_duplicates(subset='id')

    print(f"  Total 2025-era GA resolutions: {len(ga25)}")

    rows = []
    for _, res in ga25.iterrows():
        try:
            votes = json.loads(res['vote_data'])
        except (json.JSONDecodeError, TypeError):
            continue
        yes = sum(1 for v in votes.values() if v == 'YES')
        no = sum(1 for v in votes.values() if v == 'NO')
        abstain = sum(1 for v in votes.values() if v == 'ABSTAIN')
        total = yes + no + abstain
        if total == 0:
            continue
        non_yes_pct = round((no + abstain) / total * 100, 1)
        rows.append({
            'resolution': res['Resolution'],
            'title': res['Title'],
            'date': res['Date'].strftime('%Y-%m-%d'),
            'yes': yes, 'no': no, 'abstain': abstain, 'total': total,
            'non_yes_pct': non_yes_pct,
            'no_pct': round(no / total * 100, 1),
            'tags': res['tags']
        })

    res_df = pd.DataFrame(rows).sort_values('non_yes_pct', ascending=False)

    out = OUT_DIR / "10_p1_divisive_resolutions_2025.csv"
    res_df.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(res_df)} resolutions)")

    print("\n  Top 20 most divisive:")
    for _, r in res_df.head(20).iterrows():
        print(f"    {r['resolution']}: Yes={r['yes']} No={r['no']} Abs={r['abstain']} "
              f"NonYes={r['non_yes_pct']}% — {r['title'][:80]}")
    return res_df


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 11: Full Country Vote Profile 2025
# ═══════════════════════════════════════════════════════════════════════════
def output_11_country_vote_profile(annual):
    separator("11 — Country Vote Profile 2025")
    d25 = annual[annual['Year'] == 2025].copy()
    d25['yes_pct'] = (d25['Yes Votes'] / d25['Total Votes in Year'] * 100).round(1)
    d25['no_pct'] = (d25['No Votes'] / d25['Total Votes in Year'] * 100).round(1)
    d25['abstain_pct'] = (d25['Abstain Votes'] / d25['Total Votes in Year'] * 100).round(1)
    d25['region'] = d25['Country name'].map(ISO3_TO_REGION)
    d25['broad_region'] = d25['region'].map(SUBREGION_TO_BROAD)
    d25 = d25.sort_values('Pillar 1 Score', ascending=False)

    out = OUT_DIR / "11_p1_country_vote_profile_2025.csv"
    d25.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(d25)} countries)")

    # Notable outliers
    print(f"\n  P1=100 countries: {list(d25[d25['Pillar 1 Score'] == 100]['Country name'].values)}")
    print(f"  P1=0 countries:   {list(d25[d25['Pillar 1 Score'] == 0]['Country name'].values)}")
    print(f"  P1<20 countries:  {list(d25[d25['Pillar 1 Score'] < 20]['Country name'].values)}")
    return d25


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 12: Leadership Change Candidates
# ═══════════════════════════════════════════════════════════════════════════
def output_12_leadership_candidates(shifts):
    separator("12 — Leadership Change Candidates")
    # Flag countries with large P1 change AND significant yes_pct change
    # (not just participation-driven)
    df = shifts.dropna(subset=['p1_change', 'total_2024', 'total_2025']).copy()
    # Filter to countries with reasonable participation in both years (>30 votes)
    df = df[(df['total_2024'] >= 30) & (df['total_2025'] >= 30)]
    # Large P1 change AND yes_pct changed significantly
    candidates = df[(df['p1_change'].abs() > 10) & (df['yes_pct_change'].abs() > 5)].copy()
    candidates['likely_driver'] = 'POLICY_SHIFT'
    candidates = candidates.sort_values('p1_change')

    out = OUT_DIR / "12_p1_leadership_change_candidates.csv"
    candidates.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(candidates)} candidates)")
    for _, r in candidates.iterrows():
        print(f"    {r['iso3']}: P1 {r['p1_change']:+.1f}, Yes% {r['yes_pct_change']:+.1f}pp "
              f"(votes: {int(r['total_2024'])}→{int(r['total_2025'])})")
    return candidates


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 13: Spotty Voting Candidates
# ═══════════════════════════════════════════════════════════════════════════
def output_13_spotty_voting(shifts):
    separator("13 — Spotty Voting Candidates")
    df = shifts.dropna(subset=['total_2024', 'total_2025']).copy()
    df['participation_change_pct'] = ((df['total_2025'] - df['total_2024']) / df['total_2024'] * 100).round(1)
    # Countries where participation drove P1 change — low votes or big swing
    spotty = df[((df['total_2025'] < 50) | (df['total_2024'] < 50)) &
                (df['p1_change'].abs() > 5)].copy()
    spotty['driver'] = 'PARTICIPATION'
    spotty = spotty.sort_values('p1_change')

    out = OUT_DIR / "13_p1_spotty_voting_candidates.csv"
    spotty.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(spotty)} candidates)")
    for _, r in spotty.iterrows():
        print(f"    {r['iso3']}: P1 {r['p1_change']:+.1f}, votes {int(r['total_2024'])}→{int(r['total_2025'])} "
              f"({r['participation_change_pct']:+.0f}%)")
    return spotty


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT 14: Alliance Pattern Shifts (who moved toward/away from blocs)
# ═══════════════════════════════════════════════════════════════════════════
def output_14_alliance_patterns(pairwise, shifts):
    separator("14 — Alliance Pattern Shifts")
    BLOCS = {
        'USA': 'Western',
        'CHN': 'China',
        'RUS': 'Russia',
        'ISR': 'Israel',
    }

    results = []
    for anchor, bloc_name in BLOCS.items():
        a24 = pairwise[(pairwise['Year'] == 2024) &
                        ((pairwise['Country1_ISO3'] == anchor) | (pairwise['Country2_ISO3'] == anchor))].copy()
        a25 = pairwise[(pairwise['Year'] == 2025) &
                        ((pairwise['Country1_ISO3'] == anchor) | (pairwise['Country2_ISO3'] == anchor))].copy()

        def get_partner(row):
            return row['Country2_ISO3'] if row['Country1_ISO3'] == anchor else row['Country1_ISO3']

        a24['partner'] = a24.apply(get_partner, axis=1)
        a25['partner'] = a25.apply(get_partner, axis=1)
        a24_s = a24[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': 'sim_2024'})
        a25_s = a25[['partner', 'CosineSimilarity']].rename(columns={'CosineSimilarity': 'sim_2025'})
        am = pd.merge(a24_s, a25_s, on='partner', how='inner')
        am['sim_change'] = (am['sim_2025'] - am['sim_2024']).round(4)
        am['bloc'] = bloc_name
        am['anchor'] = anchor
        results.append(am)

    all_blocs = pd.concat(results)

    # Pivot to wide format: one row per country, columns for each bloc's sim change
    pivot = all_blocs.pivot_table(index='partner', columns='anchor',
                                   values='sim_change', aggfunc='first').reset_index()
    pivot.columns.name = None
    pivot.columns = ['iso3'] + [f'sim_change_vs_{c}' for c in pivot.columns[1:]]

    # Add p1 change
    p1_chg = shifts[['iso3', 'p1_change', 'region', 'broad_region']].copy()
    pivot = pd.merge(pivot, p1_chg, on='iso3', how='left')
    pivot = pivot.sort_values('sim_change_vs_USA', ascending=True)

    out = OUT_DIR / "14_p1_alliance_pattern_shifts.csv"
    pivot.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(pivot)} countries)")

    # Summary: who moved TOWARD USA
    print("\n  Top 10 moved TOWARD USA:")
    toward = pivot.sort_values('sim_change_vs_USA', ascending=False).head(10)
    for _, r in toward.iterrows():
        usa_chg = r.get('sim_change_vs_USA', float('nan'))
        chn_chg = r.get('sim_change_vs_CHN', float('nan'))
        print(f"    {r['iso3']}: USA {usa_chg:+.3f}, CHN {chn_chg:+.3f}" if pd.notna(chn_chg) else f"    {r['iso3']}: USA {usa_chg:+.3f}")

    print("\n  Top 10 moved AWAY from USA:")
    away = pivot.sort_values('sim_change_vs_USA', ascending=True).head(10)
    for _, r in away.iterrows():
        usa_chg = r.get('sim_change_vs_USA', float('nan'))
        chn_chg = r.get('sim_change_vs_CHN', float('nan'))
        print(f"    {r['iso3']}: USA {usa_chg:+.3f}, CHN {chn_chg:+.3f}" if pd.notna(chn_chg) else f"    {r['iso3']}: USA {usa_chg:+.3f}")
    return pivot


# ═══════════════════════════════════════════════════════════════════════════
# SECOND-ORDER: Country-topic deep dive for key movers
# ═══════════════════════════════════════════════════════════════════════════
def output_15_key_movers_topic_detail(topics, big_movers):
    separator("15 — Key Movers: Topic-Level Detail")
    KEY_COUNTRIES = ['USA', 'ARG', 'SYR', 'ISR', 'BRA', 'UKR', 'MMR', 'PRY', 'HUN',
                     'GBR', 'FRA', 'DEU', 'CAN', 'AUS', 'CHN', 'RUS', 'IND']
    # Also add all big movers
    big_isos = list(big_movers['iso3'].unique())
    all_targets = list(set(KEY_COUNTRIES + big_isos))

    t24 = topics[(topics['Year'] == 2024) & (topics['Country'].isin(all_targets))].copy()
    t25 = topics[(topics['Year'] == 2025) & (topics['Country'].isin(all_targets))].copy()

    t24['yes_pct'] = (t24['YesVotes_Topic'] / t24['TotalVotes_Topic'] * 100).round(1)
    t25['yes_pct'] = (t25['YesVotes_Topic'] / t25['TotalVotes_Topic'] * 100).round(1)

    t24_s = t24[['Country', 'TopicTag', 'yes_pct', 'TotalVotes_Topic']].rename(
        columns={'yes_pct': 'yes_pct_2024', 'TotalVotes_Topic': 'votes_2024'})
    t25_s = t25[['Country', 'TopicTag', 'yes_pct', 'TotalVotes_Topic']].rename(
        columns={'yes_pct': 'yes_pct_2025', 'TotalVotes_Topic': 'votes_2025'})

    merged = pd.merge(t24_s, t25_s, on=['Country', 'TopicTag'], how='outer')
    merged['yes_pct_change'] = (merged['yes_pct_2025'] - merged['yes_pct_2024']).round(1)
    merged = merged.sort_values(['Country', 'yes_pct_change'])

    out = OUT_DIR / "15_p1_key_movers_topic_detail.csv"
    merged.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(merged)} rows, {merged['Country'].nunique()} countries)")

    # Show USA specifically
    usa = merged[merged['Country'] == 'USA'].dropna(subset=['yes_pct_2024', 'yes_pct_2025'])
    print("\n  USA topic shifts (present in both years):")
    for _, r in usa.sort_values('yes_pct_change').iterrows():
        print(f"    {r['TopicTag']}: {r['yes_pct_change']:+.1f}pp ({r['yes_pct_2024']:.0f}% → {r['yes_pct_2025']:.0f}%)")
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# SECOND-ORDER: Historical P1 for key countries (for sparklines)
# ═══════════════════════════════════════════════════════════════════════════
def output_16_key_country_p1_history(annual):
    separator("16 — Key Country P1 History (2015–2025)")
    KEY = ['USA', 'ARG', 'SYR', 'ISR', 'BRA', 'UKR', 'GBR', 'CHN', 'RUS',
           'IND', 'FRA', 'DEU', 'JPN', 'AUS', 'CAN', 'ZAF', 'NGA', 'EGY',
           'SAU', 'TUR', 'MEX', 'PRY', 'HUN']
    df = annual[(annual['Year'] >= 2015) & (annual['Year'] <= 2025) &
                (annual['Country name'].isin(KEY))].copy()
    df = df[['Country name', 'Year', 'Pillar 1 Score', 'Yes Votes', 'No Votes',
             'Abstain Votes', 'Total Votes in Year']].copy()
    df.columns = ['iso3', 'year', 'p1_score', 'yes', 'no', 'abstain', 'total']
    df = df.sort_values(['iso3', 'year'])

    out = OUT_DIR / "16_p1_key_country_history.csv"
    df.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(df)} rows)")
    return df


# ═══════════════════════════════════════════════════════════════════════════
# SECOND-ORDER: Resolution-level vote detail for key countries
# ═══════════════════════════════════════════════════════════════════════════
def output_17_resolution_vote_detail(raw_votes):
    separator("17 — Resolution-Level Vote Detail for Key Countries (2025)")
    KEY = ['USA', 'ARG', 'ISR', 'SYR', 'PRY', 'BRA', 'GBR', 'CHN', 'RUS', 'UKR']

    df = raw_votes.copy()
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', utc=True)
    df['Year'] = df['Date'].dt.year
    ga25 = df[(df['Year'] == 2025) & (df['sc_flag'] == 0)]

    rows = []
    for _, res in ga25.iterrows():
        try:
            votes = json.loads(res['vote_data'])
        except (json.JSONDecodeError, TypeError):
            continue
        for iso3 in KEY:
            vote = votes.get(iso3)
            rows.append({
                'resolution': res['Resolution'],
                'title': res['Title'][:100],
                'date': res['Date'].strftime('%Y-%m-%d'),
                'iso3': iso3,
                'vote': vote if vote else 'ABSENT',
                'tags': res['tags']
            })

    detail = pd.DataFrame(rows)
    out = OUT_DIR / "17_p1_resolution_vote_detail_2025.csv"
    detail.to_csv(out, index=False)
    print(f"  ✓ Saved {out.name} ({len(detail)} rows)")

    # Summary per country
    for iso3 in KEY:
        sub = detail[detail['iso3'] == iso3]
        counts = sub['vote'].value_counts()
        print(f"    {iso3}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return detail


# ═══════════════════════════════════════════════════════════════════════════
# VOTE ARITHMETIC VALIDATION
# ═══════════════════════════════════════════════════════════════════════════
def validate_vote_arithmetic(annual):
    separator("VALIDATION — Vote Arithmetic")
    d25 = annual[annual['Year'] == 2025].copy()
    d25['sum'] = d25['Yes Votes'] + d25['No Votes'] + d25['Abstain Votes']
    mismatches = d25[d25['sum'] != d25['Total Votes in Year']]
    if len(mismatches) == 0:
        print("  ✓ Vote arithmetic (Yes + No + Abstain == Total) passes for all 2025 rows")
    else:
        print(f"  ❌ {len(mismatches)} rows fail vote arithmetic!")
        print(mismatches[['Country name', 'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year', 'sum']])

    # Check 2024 too
    d24 = annual[annual['Year'] == 2024].copy()
    d24['sum'] = d24['Yes Votes'] + d24['No Votes'] + d24['Abstain Votes']
    mismatches24 = d24[d24['sum'] != d24['Total Votes in Year']]
    if len(mismatches24) == 0:
        print("  ✓ Vote arithmetic passes for all 2024 rows")
    else:
        print(f"  ❌ {len(mismatches24)} rows fail vote arithmetic for 2024!")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    annual, pairwise, topics, raw_votes = load_data()

    # Validate first
    validate_vote_arithmetic(annual)

    # Core outputs
    trend = output_01_world_avg_trend(annual)
    shifts = output_02_country_shifts(annual)
    big_movers = output_03_big_movers(shifts)
    participation = output_04_participation(shifts)
    topic_changes = output_05_topic_changes(topics)
    new_dropped = output_06_topic_new_dropped(topics)
    pairwise_shifts = output_07_pairwise_shifts(pairwise)
    us_alliances = output_08_us_alliance_shifts(pairwise)
    regional = output_09_regional(annual)
    divisive = output_10_divisive_resolutions(raw_votes)
    profile = output_11_country_vote_profile(annual)
    leadership = output_12_leadership_candidates(shifts)
    spotty = output_13_spotty_voting(shifts)
    alliance_patterns = output_14_alliance_patterns(pairwise, shifts)

    # Second-order analysis
    topic_detail = output_15_key_movers_topic_detail(topics, big_movers)
    history = output_16_key_country_p1_history(annual)
    res_detail = output_17_resolution_vote_detail(raw_votes)

    separator("SUMMARY")
    print("  All outputs written to:", OUT_DIR)
    print("  Total output files: 19")
    print()
    print("  KEY FINDINGS (NEW DATA):")
    p1_24 = trend.loc[trend['Year'] == 2024, 'world_avg_p1'].values[0]
    p1_25 = trend.loc[trend['Year'] == 2025, 'world_avg_p1'].values[0]
    print(f"  • World avg P1: {p1_24:.2f} → {p1_25:.2f} ({p1_25-p1_24:+.2f})")
    print(f"  • Big movers (>10pt): {len(big_movers)} countries")
    print(f"  • Topics in 2025: {topics[topics['Year']==2025]['TopicTag'].nunique()} (vs {topics[topics['Year']==2024]['TopicTag'].nunique()} in 2024)")


if __name__ == "__main__":
    main()
