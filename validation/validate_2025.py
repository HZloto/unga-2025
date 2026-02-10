#!/usr/bin/env python3
"""Focused validation on 2025 data only."""
import pandas as pd
from pathlib import Path

# Load all three files
data_dir = Path(__file__).parent.parent / "data"
annual = pd.read_csv(data_dir / 'annual_scores.csv')
pairwise = pd.read_csv(data_dir / 'pairwise_similarity_yearly.csv')
topics = pd.read_csv(data_dir / 'topic_votes_yearly.csv')

# Filter to 2025 only
a25 = annual[annual['Year'] == 2025]
p25 = pairwise[pairwise['Year'] == 2025]
t25 = topics[topics['Year'] == 2025]

print('=' * 50)
print('         2025 DATA VALIDATION REPORT')
print('=' * 50)

print(f'\n1. ANNUAL SCORES (2025):')
print(f'   Countries: {len(a25)}')
print(f'   Score range: {a25["Total Index Average"].min():.3f} - {a25["Total Index Average"].max():.3f}')
print(f'\n   Top 5 (highest score):')
for _, r in a25.nlargest(5, 'Total Index Average')[['Country name', 'Total Index Average', 'Overall Rank']].iterrows():
    print(f'      {r["Country name"]}: {r["Total Index Average"]:.3f} (Rank {int(r["Overall Rank"])})')
print(f'\n   Bottom 5 (lowest score):')
for _, r in a25.nsmallest(5, 'Total Index Average')[['Country name', 'Total Index Average', 'Overall Rank']].iterrows():
    print(f'      {r["Country name"]}: {r["Total Index Average"]:.3f} (Rank {int(r["Overall Rank"])})')

print(f'\n2. PAIRWISE SIMILARITY (2025):')
print(f'   Country pairs: {len(p25):,}')
print(f'   Unique countries: {p25["Country1_ISO3"].nunique()}')
print(f'   Similarity range: {p25["CosineSimilarity"].min():.3f} - {p25["CosineSimilarity"].max():.3f}')
print(f'   Mean similarity: {p25["CosineSimilarity"].mean():.3f}')

# Most aligned pairs in 2025
print(f'\n   Most aligned pairs:')
top_pairs = p25[p25['Country1_ISO3'] < p25['Country2_ISO3']].nlargest(5, 'CosineSimilarity')
for _, r in top_pairs.iterrows():
    print(f'      {r["Country1_ISO3"]} - {r["Country2_ISO3"]}: {r["CosineSimilarity"]:.3f}')

# Least aligned pairs in 2025
print(f'\n   Least aligned pairs:')
bot_pairs = p25[p25['Country1_ISO3'] < p25['Country2_ISO3']].nsmallest(5, 'CosineSimilarity')
for _, r in bot_pairs.iterrows():
    print(f'      {r["Country1_ISO3"]} - {r["Country2_ISO3"]}: {r["CosineSimilarity"]:.3f}')

print(f'\n3. TOPIC VOTES (2025):')
print(f'   Records: {len(t25):,}')
print(f'   Countries: {t25["Country"].nunique()}')
print(f'   Topics: {t25["TopicTag"].nunique()}')
print(f'\n   Topics covered:')
for t in sorted(t25["TopicTag"].unique()):
    count = len(t25[t25["TopicTag"] == t])
    print(f'      {t}: {count} country records')

print(f'\n4. VOTE TOTALS CHECK (2025):')
sample = a25.sample(5, random_state=42)
print('   Checking vote arithmetic (Y + N + A should match total participation):')
for _, r in sample.iterrows():
    calc_total = r['Yes Votes'] + r['No Votes'] + r['Abstain Votes']
    status = '✓' if calc_total <= r['Total Votes in Year'] else '✗'
    print(f'   {status} {r["Country name"]}: {int(r["Yes Votes"])}+{int(r["No Votes"])}+{int(r["Abstain Votes"])}={int(calc_total)} (Total resolutions: {int(r["Total Votes in Year"])})')

print(f'\n5. DATA QUALITY (2025):')
print(f'   Annual missing values: {a25.isnull().sum().sum()}')
print(f'   Pairwise missing values: {p25.isnull().sum().sum()}')
print(f'   Topics missing values: {t25.isnull().sum().sum()}')

# Check consistency
a25_countries = set(a25['Country name'])
p25_countries = set(p25['Country1_ISO3'].unique()) | set(p25['Country2_ISO3'].unique())
t25_countries = set(t25['Country'])

print(f'\n6. COUNTRY CONSISTENCY (2025):')
print(f'   Annual scores: {len(a25_countries)} countries')
print(f'   Pairwise: {len(p25_countries)} countries')
print(f'   Topics: {len(t25_countries)} countries')

in_annual_not_pairwise = a25_countries - p25_countries
in_pairwise_not_annual = p25_countries - a25_countries
if in_annual_not_pairwise:
    print(f'   Note: In annual but not pairwise: {in_annual_not_pairwise}')
if in_pairwise_not_annual:
    print(f'   Note: In pairwise but not annual: {in_pairwise_not_annual}')
if not in_annual_not_pairwise and not in_pairwise_not_annual:
    print(f'   All countries match across files')

print('\n' + '=' * 50)
print('         2025 VALIDATION COMPLETE')
print('=' * 50)
