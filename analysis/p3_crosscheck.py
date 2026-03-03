"""Cross-check: validate region mapping using P2 values from 2024 report screenshot,
then compute P3 by region for 2025."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

df_leg = pd.read_csv(DATA / "legacy" / "annual_scores.csv")
df_new = pd.read_csv(DATA / "annual_scores (2).csv")

region_map = {
    'BDI':'Sub-Saharan Africa','COM':'Sub-Saharan Africa','DJI':'Sub-Saharan Africa',
    'ERI':'Sub-Saharan Africa','ETH':'Sub-Saharan Africa','KEN':'Sub-Saharan Africa',
    'MDG':'Sub-Saharan Africa','MWI':'Sub-Saharan Africa','MUS':'Sub-Saharan Africa',
    'MOZ':'Sub-Saharan Africa','RWA':'Sub-Saharan Africa','SYC':'Sub-Saharan Africa',
    'SOM':'Sub-Saharan Africa','SSD':'Sub-Saharan Africa','TZA':'Sub-Saharan Africa',
    'UGA':'Sub-Saharan Africa','ZMB':'Sub-Saharan Africa','ZWE':'Sub-Saharan Africa',
    'AGO':'Sub-Saharan Africa','CMR':'Sub-Saharan Africa','CAF':'Sub-Saharan Africa',
    'TCD':'Sub-Saharan Africa','COG':'Sub-Saharan Africa','COD':'Sub-Saharan Africa',
    'GNQ':'Sub-Saharan Africa','GAB':'Sub-Saharan Africa','STP':'Sub-Saharan Africa',
    'BWA':'Sub-Saharan Africa','SWZ':'Sub-Saharan Africa','LSO':'Sub-Saharan Africa',
    'NAM':'Sub-Saharan Africa','ZAF':'Sub-Saharan Africa',
    'BEN':'Sub-Saharan Africa','BFA':'Sub-Saharan Africa','CPV':'Sub-Saharan Africa',
    'CIV':'Sub-Saharan Africa','GMB':'Sub-Saharan Africa','GHA':'Sub-Saharan Africa',
    'GIN':'Sub-Saharan Africa','GNB':'Sub-Saharan Africa','LBR':'Sub-Saharan Africa',
    'MLI':'Sub-Saharan Africa','MRT':'Sub-Saharan Africa','NER':'Sub-Saharan Africa',
    'NGA':'Sub-Saharan Africa','SEN':'Sub-Saharan Africa','SLE':'Sub-Saharan Africa',
    'TGO':'Sub-Saharan Africa',
    'DZA':'Northern Africa','EGY':'Northern Africa','LBY':'Northern Africa',
    'MAR':'Northern Africa','SDN':'Northern Africa','TUN':'Northern Africa',
    'CHN':'Eastern Asia','JPN':'Eastern Asia','MNG':'Eastern Asia',
    'PRK':'Eastern Asia','KOR':'Eastern Asia',
    'BRN':'South-eastern Asia','KHM':'South-eastern Asia','IDN':'South-eastern Asia',
    'LAO':'South-eastern Asia','MYS':'South-eastern Asia','MMR':'South-eastern Asia',
    'PHL':'South-eastern Asia','SGP':'South-eastern Asia','THA':'South-eastern Asia',
    'TLS':'South-eastern Asia','VNM':'South-eastern Asia',
    'BGD':'Southern Asia','BTN':'Southern Asia','IND':'Southern Asia',
    'IRN':'Southern Asia','MDV':'Southern Asia','NPL':'Southern Asia',
    'PAK':'Southern Asia','LKA':'Southern Asia',
    'KAZ':'Central Asia','KGZ':'Central Asia','TJK':'Central Asia',
    'TKM':'Central Asia','UZB':'Central Asia',
    'ARM':'Western Asia','AZE':'Western Asia','BHR':'Western Asia',
    'CYP':'Western Asia','GEO':'Western Asia','IRQ':'Western Asia',
    'ISR':'Western Asia','JOR':'Western Asia','KWT':'Western Asia',
    'LBN':'Western Asia','OMN':'Western Asia','QAT':'Western Asia',
    'SAU':'Western Asia','SYR':'Western Asia','TUR':'Western Asia',
    'ARE':'Western Asia','YEM':'Western Asia',
    'BLR':'Eastern Europe','BGR':'Eastern Europe','CZE':'Eastern Europe',
    'HUN':'Eastern Europe','POL':'Eastern Europe','MDA':'Eastern Europe',
    'ROU':'Eastern Europe','RUS':'Eastern Europe','SVK':'Eastern Europe',
    'UKR':'Eastern Europe',
    'DNK':'Northern Europe','EST':'Northern Europe','FIN':'Northern Europe',
    'ISL':'Northern Europe','IRL':'Northern Europe','LVA':'Northern Europe',
    'LTU':'Northern Europe','NOR':'Northern Europe','SWE':'Northern Europe',
    'GBR':'Northern Europe',
    'ALB':'Southern Europe','AND':'Southern Europe','BIH':'Southern Europe',
    'HRV':'Southern Europe','GRC':'Southern Europe','ITA':'Southern Europe',
    'MLT':'Southern Europe','MNE':'Southern Europe','MKD':'Southern Europe',
    'PRT':'Southern Europe','SMR':'Southern Europe','SRB':'Southern Europe',
    'SVN':'Southern Europe','ESP':'Southern Europe',
    'AUT':'Western Europe','BEL':'Western Europe','FRA':'Western Europe',
    'DEU':'Western Europe','LIE':'Western Europe','LUX':'Western Europe',
    'MCO':'Western Europe','NLD':'Western Europe','CHE':'Western Europe',
    'ATG':'Latin America & Caribbean','BHS':'Latin America & Caribbean',
    'BRB':'Latin America & Caribbean','CUB':'Latin America & Caribbean',
    'DMA':'Latin America & Caribbean','DOM':'Latin America & Caribbean',
    'GRD':'Latin America & Caribbean','HTI':'Latin America & Caribbean',
    'JAM':'Latin America & Caribbean','KNA':'Latin America & Caribbean',
    'LCA':'Latin America & Caribbean','VCT':'Latin America & Caribbean',
    'TTO':'Latin America & Caribbean',
    'BLZ':'Latin America & Caribbean','CRI':'Latin America & Caribbean',
    'SLV':'Latin America & Caribbean','GTM':'Latin America & Caribbean',
    'HND':'Latin America & Caribbean','MEX':'Latin America & Caribbean',
    'NIC':'Latin America & Caribbean','PAN':'Latin America & Caribbean',
    'ARG':'Latin America & Caribbean','BOL':'Latin America & Caribbean',
    'BRA':'Latin America & Caribbean','CHL':'Latin America & Caribbean',
    'COL':'Latin America & Caribbean','ECU':'Latin America & Caribbean',
    'GUY':'Latin America & Caribbean','PRY':'Latin America & Caribbean',
    'PER':'Latin America & Caribbean','SUR':'Latin America & Caribbean',
    'URY':'Latin America & Caribbean',
    'AUS':'Oceania','NZL':'Oceania','FJI':'Oceania','PNG':'Oceania',
    'SLB':'Oceania','VUT':'Oceania','FSM':'Oceania','KIR':'Oceania',
    'MHL':'Oceania','NRU':'Oceania','PLW':'Oceania','WSM':'Oceania',
    'TON':'Oceania','TUV':'Oceania',
    'CAN':'Northern America','USA':'Northern America',
}

# Screenshot shows P2 regional scores: left = 2023, right = 2024
# Used to VALIDATE the region mapping only
report_p2 = {
    'Latin America & Caribbean': (93.8, 91.2),
    'Oceania': (84.2, 82.4),
    'Eastern Asia': (78.7, 80.5),
    'Sub-Saharan Africa': (92.1, 93.8),
    'Western Asia': (79.6, 81.0),
    'Northern Africa': (94.6, 95.6),
    'Eastern Europe': (85.4, 84.9),
    'Western Europe': (92.4, 92.9),
    'Northern Europe': (94.8, 94.3),
    'Southern Asia': (90.9, 91.2),
    'Southern Europe': (93.3, 93.2),
    'South-eastern Asia': (94.7, 95.7),
    'Central Asia': (96.8, 98.3),
}

# ── STEP 1: Validate region mapping against P2 screenshot values ──
print("=" * 60)
print("STEP 1: Validate region mapping using P2 from 2024 report")
print("=" * 60)

for label, dframe in [('Legacy data', df_leg), ('New (updated) data', df_new)]:
    dframe['Region'] = dframe['Country name'].map(region_map)
    for col in ['Pillar 2 Score', 'Pillar 2 Normalized']:
        p2_23 = dframe[dframe['Year'] == 2023].groupby('Region')[col].mean()
        p2_24 = dframe[dframe['Year'] == 2024].groupby('Region')[col].mean()
        matches = 0
        for r, (rv23, rv24) in report_p2.items():
            v23 = p2_23.get(r, float('nan'))
            v24 = p2_24.get(r, float('nan'))
            if not pd.isna(v23) and abs(v23 - rv23) < 0.5:
                matches += 1
            if not pd.isna(v24) and abs(v24 - rv24) < 0.5:
                matches += 1
        print(f'  {label} + {col}: {matches}/26 values match (<0.5 diff)')
        if matches >= 20:
            print('  ^^^ BEST MATCH — details:')
            for r in sorted(report_p2.keys()):
                rv23, rv24 = report_p2[r]
                v23, v24 = p2_23.get(r, float('nan')), p2_24.get(r, float('nan'))
                s23 = '✓' if abs(v23-rv23)<0.5 else f'✗ (diff={abs(v23-rv23):.1f})'
                s24 = '✓' if abs(v24-rv24)<0.5 else f'✗ (diff={abs(v24-rv24):.1f})'
                print(f'    {r:30s} 2023: rpt={rv23:5.1f} ours={v23:5.1f} {s23} | 2024: rpt={rv24:5.1f} ours={v24:5.1f} {s24}')

# ── STEP 2: If validated, compute P3 by region for 2024 & 2025 ──
print()
print("=" * 60)
print("STEP 2: P3 by Region (using new/updated data)")
print("=" * 60)

df_new['Region'] = df_new['Country name'].map(region_map)
for year in [2023, 2024, 2025]:
    yr = df_new[df_new['Year'] == year]
    reg = yr.groupby('Region').agg(
        P3_Mean=('Pillar 3 Score', 'mean'),
        Count=('Country name', 'count')
    ).round(2).sort_values('P3_Mean', ascending=False)
    print(f'\n  --- {year} ---')
    print(reg.to_string())

print('\n  --- P3 Change: 2024 → 2025 ---')
p3_24 = df_new[df_new['Year']==2024].groupby('Region')['Pillar 3 Score'].mean()
p3_25 = df_new[df_new['Year']==2025].groupby('Region')['Pillar 3 Score'].mean()
chg = pd.DataFrame({'2024': p3_24, '2025': p3_25})
chg['Change'] = chg['2025'] - chg['2024']
chg = chg.sort_values('Change', ascending=False).round(2)
print(chg.to_string())
