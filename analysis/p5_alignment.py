"""P5 Alignment Analysis — Who does the world vote with?
Computes KPIs around how UNGA member states align with P5 permanent members
(USA, GBR, FRA, RUS, CHN) using pairwise cosine similarity data."""
import pandas as pd
import numpy as np
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent

pw = pd.read_csv(DATA / "pairwise_similarity_yearly (2).csv")

P5 = ['USA', 'GBR', 'FRA', 'RUS', 'CHN']
P5_LABELS = {'USA': 'United States', 'GBR': 'United Kingdom', 'FRA': 'France',
             'RUS': 'Russia', 'CHN': 'China'}

# Pairwise file is unidirectional — need to check both columns
def get_p5_similarities(pw_year, p5_code):
    """Get similarity of every other country with a P5 member."""
    # Rows where P5 is Country1
    a = pw_year[pw_year['Country1_ISO3'] == p5_code][['Country2_ISO3', 'CosineSimilarity']].copy()
    a.columns = ['Country', 'CosineSimilarity']
    # Rows where P5 is Country2
    b = pw_year[pw_year['Country2_ISO3'] == p5_code][['Country1_ISO3', 'CosineSimilarity']].copy()
    b.columns = ['Country', 'CosineSimilarity']
    result = pd.concat([a, b], ignore_index=True)
    # Exclude other P5 members? No — include all member states
    # But exclude self-pairs (shouldn't exist) and zero-sim pre-membership pairs
    result = result[result['Country'] != p5_code]
    return result

# ══════════════════════════════════════════════════════════════
# KPI 1: Average alignment with each P5 member (trend)
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("KPI 1: Global Average Alignment with P5 Members (2020–2025)")
print("=" * 70)

rows = []
for year in range(2020, 2026):
    pw_yr = pw[pw['Year'] == year]
    for p5 in P5:
        sims = get_p5_similarities(pw_yr, p5)
        # Only count countries that actually voted (non-zero similarity)
        active = sims[sims['CosineSimilarity'] != 0]
        rows.append({
            'Year': year, 'P5_Member': p5,
            'Avg_Similarity': active['CosineSimilarity'].mean(),
            'Median_Similarity': active['CosineSimilarity'].median(),
            'Countries_With_Data': len(active),
        })

kpi1 = pd.DataFrame(rows)
pivot = kpi1.pivot(index='Year', columns='P5_Member', values='Avg_Similarity').round(3)
pivot = pivot[P5]  # order
print(pivot.to_string())
print()

# ══════════════════════════════════════════════════════════════
# KPI 2: Which P5 member is each country MOST aligned with? (2025)
# ══════════════════════════════════════════════════════════════
print("=" * 70)
print("KPI 2: Closest P5 Member per Country (2025)")
print("=" * 70)

pw_25 = pw[pw['Year'] == 2025]
all_countries = sorted(set(pw_25['Country1_ISO3'].unique()) | set(pw_25['Country2_ISO3'].unique()))
non_p5 = [c for c in all_countries if c not in P5]

closest_rows = []
for country in non_p5:
    best_p5 = None
    best_sim = -2
    p5_sims = {}
    for p5 in P5:
        sims = get_p5_similarities(pw_25, p5)
        match = sims[sims['Country'] == country]
        if len(match) > 0:
            sim_val = match['CosineSimilarity'].values[0]
            p5_sims[p5] = sim_val
            if sim_val > best_sim:
                best_sim = sim_val
                best_p5 = p5
    closest_rows.append({
        'Country': country, 'Closest_P5': best_p5, 'Closest_Sim': best_sim,
        **{f'Sim_{p}': p5_sims.get(p, np.nan) for p in P5}
    })

closest_df = pd.DataFrame(closest_rows)
# Exclude zero-sim countries (non-members)
closest_active = closest_df[closest_df['Closest_Sim'] > 0]

counts = closest_active['Closest_P5'].value_counts()
print(f"\nHow many countries have each P5 member as their CLOSEST voting partner:")
for p5 in P5:
    n = counts.get(p5, 0)
    pct = n / len(closest_active) * 100
    print(f"  {P5_LABELS[p5]:20s} ({p5}): {n:3d} countries ({pct:.1f}%)")
print(f"  {'TOTAL':20s}      : {len(closest_active):3d}")

# ══════════════════════════════════════════════════════════════
# KPI 3: Trend — closest P5 member counts over time
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("KPI 3: Countries with Each P5 as Closest Voting Partner (2020–2025)")
print("=" * 70)

trend_rows = []
for year in range(2020, 2026):
    pw_yr = pw[pw['Year'] == year]
    all_c = sorted(set(pw_yr['Country1_ISO3'].unique()) | set(pw_yr['Country2_ISO3'].unique()))
    non_p5_yr = [c for c in all_c if c not in P5]
    for country in non_p5_yr:
        best_p5 = None
        best_sim = -2
        for p5 in P5:
            sims = get_p5_similarities(pw_yr, p5)
            match = sims[sims['Country'] == country]
            if len(match) > 0:
                sv = match['CosineSimilarity'].values[0]
                if sv > best_sim:
                    best_sim = sv
                    best_p5 = p5
        if best_sim > 0:
            trend_rows.append({'Year': year, 'Country': country, 'Closest_P5': best_p5})

trend_df = pd.DataFrame(trend_rows)
trend_pivot = trend_df.groupby(['Year', 'Closest_P5']).size().unstack(fill_value=0)
trend_pivot = trend_pivot.reindex(columns=P5, fill_value=0)
print(trend_pivot.to_string())

# ══════════════════════════════════════════════════════════════
# KPI 4: Most/Least aligned countries with each P5 (2025)
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("KPI 4: Top 5 Most & Least Aligned Countries with Each P5 Member (2025)")
print("=" * 70)

for p5 in P5:
    col = f'Sim_{p5}'
    active = closest_active[closest_active[col].notna()].copy()
    active_sorted = active.sort_values(col, ascending=False)
    top5 = active_sorted.head(5)[['Country', col]]
    bot5 = active_sorted.tail(5)[['Country', col]]
    print(f"\n  {P5_LABELS[p5]} ({p5}):")
    print(f"    Most aligned:  {', '.join(f'{r.Country} ({r[col]:.3f})' for _, r in top5.iterrows())}")
    print(f"    Least aligned: {', '.join(f'{r.Country} ({r[col]:.3f})' for _, r in bot5.iterrows())}")

# ══════════════════════════════════════════════════════════════
# KPI 5: P5 inter-alignment (how do P5 members align with each other?)
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("KPI 5: P5 Inter-Alignment Matrix (2025)")
print("=" * 70)

p5_matrix = pd.DataFrame(index=P5, columns=P5, dtype=float)
for i, p5a in enumerate(P5):
    p5_matrix.loc[p5a, p5a] = 1.0
    for p5b in P5[i+1:]:
        sims = get_p5_similarities(pw_25, p5a)
        match = sims[sims['Country'] == p5b]
        if len(match) > 0:
            val = match['CosineSimilarity'].values[0]
            p5_matrix.loc[p5a, p5b] = val
            p5_matrix.loc[p5b, p5a] = val
print(p5_matrix.round(3).to_string())

# ══════════════════════════════════════════════════════════════
# KPI 6: "Swing" countries — similar alignment to multiple P5 blocs
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("KPI 6: Swing Countries — Smallest Gap Between Top 2 P5 Alignments (2025)")
print("=" * 70)

swing_rows = []
for _, row in closest_active.iterrows():
    p5_vals = [(p5, row[f'Sim_{p5}']) for p5 in P5 if row[f'Sim_{p5}'] > 0]
    p5_vals.sort(key=lambda x: x[1], reverse=True)
    if len(p5_vals) >= 2:
        gap = p5_vals[0][1] - p5_vals[1][1]
        swing_rows.append({
            'Country': row['Country'],
            '1st_P5': p5_vals[0][0], '1st_Sim': p5_vals[0][1],
            '2nd_P5': p5_vals[1][0], '2nd_Sim': p5_vals[1][1],
            'Gap': gap,
        })

swing_df = pd.DataFrame(swing_rows).sort_values('Gap')
print("Top 15 swing countries (smallest gap between 1st and 2nd closest P5):")
print(swing_df.head(15).to_string(index=False))

# ══════════════════════════════════════════════════════════════
# Save CSV outputs
# ══════════════════════════════════════════════════════════════
print()
print("=" * 70)
print("Saving CSVs...")
print("=" * 70)

# Main output: per-country P5 alignment for 2025
out_cols = ['Country', 'Closest_P5', 'Closest_Sim'] + [f'Sim_{p}' for p in P5]
closest_active[out_cols].sort_values('Country').round(4).to_csv(
    OUT / 'p5_alignment_2025.csv', index=False)
print(f"  ✓ {OUT / 'p5_alignment_2025.csv'}")

# Trend: avg alignment per P5 member
kpi1.round(4).to_csv(OUT / 'p5_avg_alignment_trend.csv', index=False)
print(f"  ✓ {OUT / 'p5_avg_alignment_trend.csv'}")

# Closest P5 counts trend
trend_pivot.to_csv(OUT / 'p5_closest_counts_trend.csv')
print(f"  ✓ {OUT / 'p5_closest_counts_trend.csv'}")
