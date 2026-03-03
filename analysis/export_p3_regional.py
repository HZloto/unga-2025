"""Export P3 regional scores for 2025 (and 2024 for comparison) to CSV."""
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
OUT = Path(__file__).parent

df = pd.read_csv(DATA / "annual_scores (2).csv")

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

df['Region'] = df['Country name'].map(region_map)

p3_24 = df[df['Year']==2024].groupby('Region')['Pillar 3 Score'].mean()
p3_25 = df[df['Year']==2025].groupby('Region')['Pillar 3 Score'].mean()
counts = df[df['Year']==2025].groupby('Region')['Country name'].count()

out = pd.DataFrame({
    'Region': p3_25.index,
    'P3_2024': p3_24.values,
    'P3_2025': p3_25.values,
    'Change': (p3_25 - p3_24).values,
    'Countries': counts.values,
}).round(2).sort_values('P3_2025', ascending=False)

out.to_csv(OUT / 'p3_regional_scores_2025.csv', index=False)
print(f"Saved to {OUT / 'p3_regional_scores_2025.csv'}")
print(out.to_string(index=False))
