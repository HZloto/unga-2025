"""P3 (Global Alignment) by Region — matching UN M49 sub-regions from the 2024 report."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
df = pd.read_csv(DATA / "annual_scores (2).csv")

# UN M49 sub-region mapping for all 193 UN member states (191 in 2025 data)
region_map = {
    # Sub-Saharan Africa — Eastern Africa
    'BDI': 'Sub-Saharan Africa', 'COM': 'Sub-Saharan Africa', 'DJI': 'Sub-Saharan Africa',
    'ERI': 'Sub-Saharan Africa', 'ETH': 'Sub-Saharan Africa', 'KEN': 'Sub-Saharan Africa',
    'MDG': 'Sub-Saharan Africa', 'MWI': 'Sub-Saharan Africa', 'MUS': 'Sub-Saharan Africa',
    'MOZ': 'Sub-Saharan Africa', 'RWA': 'Sub-Saharan Africa', 'SYC': 'Sub-Saharan Africa',
    'SOM': 'Sub-Saharan Africa', 'SSD': 'Sub-Saharan Africa', 'TZA': 'Sub-Saharan Africa',
    'UGA': 'Sub-Saharan Africa', 'ZMB': 'Sub-Saharan Africa', 'ZWE': 'Sub-Saharan Africa',
    # Sub-Saharan Africa — Middle Africa
    'AGO': 'Sub-Saharan Africa', 'CMR': 'Sub-Saharan Africa', 'CAF': 'Sub-Saharan Africa',
    'TCD': 'Sub-Saharan Africa', 'COG': 'Sub-Saharan Africa', 'COD': 'Sub-Saharan Africa',
    'GNQ': 'Sub-Saharan Africa', 'GAB': 'Sub-Saharan Africa', 'STP': 'Sub-Saharan Africa',
    # Sub-Saharan Africa — Southern Africa
    'BWA': 'Sub-Saharan Africa', 'SWZ': 'Sub-Saharan Africa', 'LSO': 'Sub-Saharan Africa',
    'NAM': 'Sub-Saharan Africa', 'ZAF': 'Sub-Saharan Africa',
    # Sub-Saharan Africa — Western Africa
    'BEN': 'Sub-Saharan Africa', 'BFA': 'Sub-Saharan Africa', 'CPV': 'Sub-Saharan Africa',
    'CIV': 'Sub-Saharan Africa', 'GMB': 'Sub-Saharan Africa', 'GHA': 'Sub-Saharan Africa',
    'GIN': 'Sub-Saharan Africa', 'GNB': 'Sub-Saharan Africa', 'LBR': 'Sub-Saharan Africa',
    'MLI': 'Sub-Saharan Africa', 'MRT': 'Sub-Saharan Africa', 'NER': 'Sub-Saharan Africa',
    'NGA': 'Sub-Saharan Africa', 'SEN': 'Sub-Saharan Africa', 'SLE': 'Sub-Saharan Africa',
    'TGO': 'Sub-Saharan Africa',
    # Northern Africa
    'DZA': 'Northern Africa', 'EGY': 'Northern Africa', 'LBY': 'Northern Africa',
    'MAR': 'Northern Africa', 'SDN': 'Northern Africa', 'TUN': 'Northern Africa',
    # Eastern Asia
    'CHN': 'Eastern Asia', 'JPN': 'Eastern Asia', 'MNG': 'Eastern Asia',
    'PRK': 'Eastern Asia', 'KOR': 'Eastern Asia',
    # South-eastern Asia
    'BRN': 'South-eastern Asia', 'KHM': 'South-eastern Asia', 'IDN': 'South-eastern Asia',
    'LAO': 'South-eastern Asia', 'MYS': 'South-eastern Asia', 'MMR': 'South-eastern Asia',
    'PHL': 'South-eastern Asia', 'SGP': 'South-eastern Asia', 'THA': 'South-eastern Asia',
    'TLS': 'South-eastern Asia', 'VNM': 'South-eastern Asia',
    # Southern Asia
    'BGD': 'Southern Asia', 'BTN': 'Southern Asia', 'IND': 'Southern Asia',
    'IRN': 'Southern Asia', 'MDV': 'Southern Asia', 'NPL': 'Southern Asia',
    'PAK': 'Southern Asia', 'LKA': 'Southern Asia',
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
    # Latin America & Caribbean — Caribbean
    'ATG': 'Latin America & Caribbean', 'BHS': 'Latin America & Caribbean',
    'BRB': 'Latin America & Caribbean', 'CUB': 'Latin America & Caribbean',
    'DMA': 'Latin America & Caribbean', 'DOM': 'Latin America & Caribbean',
    'GRD': 'Latin America & Caribbean', 'HTI': 'Latin America & Caribbean',
    'JAM': 'Latin America & Caribbean', 'KNA': 'Latin America & Caribbean',
    'LCA': 'Latin America & Caribbean', 'VCT': 'Latin America & Caribbean',
    'TTO': 'Latin America & Caribbean',
    # Latin America & Caribbean — Central America
    'BLZ': 'Latin America & Caribbean', 'CRI': 'Latin America & Caribbean',
    'SLV': 'Latin America & Caribbean', 'GTM': 'Latin America & Caribbean',
    'HND': 'Latin America & Caribbean', 'MEX': 'Latin America & Caribbean',
    'NIC': 'Latin America & Caribbean', 'PAN': 'Latin America & Caribbean',
    # Latin America & Caribbean — South America
    'ARG': 'Latin America & Caribbean', 'BOL': 'Latin America & Caribbean',
    'BRA': 'Latin America & Caribbean', 'CHL': 'Latin America & Caribbean',
    'COL': 'Latin America & Caribbean', 'ECU': 'Latin America & Caribbean',
    'GUY': 'Latin America & Caribbean', 'PRY': 'Latin America & Caribbean',
    'PER': 'Latin America & Caribbean', 'SUR': 'Latin America & Caribbean',
    'URY': 'Latin America & Caribbean',
    # Oceania
    'AUS': 'Oceania', 'NZL': 'Oceania', 'FJI': 'Oceania', 'PNG': 'Oceania',
    'SLB': 'Oceania', 'VUT': 'Oceania', 'FSM': 'Oceania', 'KIR': 'Oceania',
    'MHL': 'Oceania', 'NRU': 'Oceania', 'PLW': 'Oceania', 'WSM': 'Oceania',
    'TON': 'Oceania', 'TUV': 'Oceania',
    # Northern America
    'CAN': 'Northern America', 'USA': 'Northern America',
}

df['Region'] = df['Country name'].map(region_map)

# Validate: check for unmapped countries in 2025
unmapped = df[(df['Year'] == 2025) & (df['Region'].isna())]['Country name'].unique()
print(f"Unmapped countries in 2025: {list(unmapped)} ({len(unmapped)} total)")
print(f"Mapped: {191 - len(unmapped)}/191\n")

# ── P3 by Region for 2023, 2024, 2025 ──
for year in [2023, 2024, 2025]:
    yr = df[df['Year'] == year]
    reg = yr.groupby('Region').agg(
        P3_Mean=('Pillar 3 Score', 'mean'),
        P3_Median=('Pillar 3 Score', 'median'),
        Count=('Country name', 'count')
    ).round(2).sort_values('P3_Mean', ascending=False)
    print(f'=== P3 (Global Alignment) by Region — {year} ===')
    print(reg.to_string())
    print()

# ── Year-over-year change 2024 → 2025 ──
print('=== P3 Regional Change: 2024 → 2025 ===')
p3_24 = df[df['Year'] == 2024].groupby('Region')['Pillar 3 Score'].mean()
p3_25 = df[df['Year'] == 2025].groupby('Region')['Pillar 3 Score'].mean()
chg = pd.DataFrame({'2024': p3_24, '2025': p3_25})
chg['Change'] = chg['2025'] - chg['2024']
chg = chg.sort_values('Change', ascending=False).round(2)
print(chg.to_string())

# ── Cross-check against 2024 report screenshot values ──
print('\n=== Cross-check vs. 2024 Report Values ===')
report_2024_vals = {
    'Latin America & Caribbean': 93.8,
    'Oceania': 84.2,
    'Eastern Asia': 78.7,
    'Sub-Saharan Africa': 92.1,
    'Western Asia': 79.6,
    'Northern Africa': 94.6,
    'Eastern Europe': 85.4,
    'Western Europe': 92.4,
    'Northern Europe': 94.8,
    'Southern Europe': 90.9,  # listed as 93.3 in screenshot but that's "Southern Europe" row
    'Southern Asia': 90.9,    # from screenshot
    'South-eastern Asia': 94.7,
    'Central Asia': 96.8,
}
for region, report_val in sorted(report_2024_vals.items()):
    our_val = p3_24.get(region, float('nan'))
    diff = abs(our_val - report_val) if not pd.isna(our_val) else float('nan')
    status = '✓' if diff < 1.0 else '⚠️'
    print(f"  {status} {region}: report={report_val}, ours={our_val:.1f}, diff={diff:.1f}")
