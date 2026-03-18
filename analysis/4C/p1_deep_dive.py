"""
P1 Deep-Dive — Country shift narratives + theme-level analysis for Section 4C.
Builds on the CSVs produced by p1_data_extraction.py.
"""

import os, json, urllib.request, urllib.parse, ssl
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OUT_DIR = Path(__file__).parent

def separator(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")

def query_supabase(table, select="*", params=None, limit=10000):
    ctx = ssl.create_default_context()
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={urllib.parse.quote(select)}"
    if params:
        for k, v in params.items():
            url += f"&{k}={urllib.parse.quote(str(v))}"
    all_rows = []
    offset = 0
    page_size = 1000
    while True:
        page_url = url + f"&limit={page_size}&offset={offset}"
        req = urllib.request.Request(page_url, headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        })
        with urllib.request.urlopen(req, context=ctx) as resp:
            data = json.loads(resp.read().decode())
            if not data:
                break
            all_rows.extend(data)
            if len(data) < page_size:
                break
            offset += page_size
            if len(all_rows) >= limit:
                break
    return all_rows

# ══════════════════════════════════════════════════════════════════════════
# 1. USA DEEP DIVE — voting pattern shift
# ══════════════════════════════════════════════════════════════════════════
separator("1. USA voting pattern — 2024 vs 2025 by topic")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.USA", "Year": "in.(2024,2025)", "order": "Year.asc,TopicTag.asc"},
    limit=5000
)
df_usa = pd.DataFrame(rows)
df_usa.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_usa[c] = pd.to_numeric(df_usa[c], errors="coerce")

# Compare topic by topic
usa_24 = df_usa[df_usa.Year == 2024].set_index("TopicTag")
usa_25 = df_usa[df_usa.Year == 2025].set_index("TopicTag")

usa_cmp = usa_24[["Yes", "No", "Abstain", "Total"]].rename(
    columns={"Yes": "Yes_24", "No": "No_24", "Abstain": "Abs_24", "Total": "Tot_24"}
).join(
    usa_25[["Yes", "No", "Abstain", "Total"]].rename(
        columns={"Yes": "Yes_25", "No": "No_25", "Abstain": "Abs_25", "Total": "Tot_25"})
, how="outer")

usa_cmp["YesPct_24"] = (usa_cmp["Yes_24"] / usa_cmp["Tot_24"] * 100).round(1)
usa_cmp["YesPct_25"] = (usa_cmp["Yes_25"] / usa_cmp["Tot_25"] * 100).round(1)
usa_cmp["YesPct_Change"] = usa_cmp["YesPct_25"] - usa_cmp["YesPct_24"]
usa_cmp = usa_cmp.sort_values("YesPct_Change")

print("\nUSA topic-level Yes% changes:")
print(usa_cmp[["YesPct_24", "YesPct_25", "YesPct_Change", "Tot_24", "Tot_25"]].dropna().to_string())

# ══════════════════════════════════════════════════════════════════════════
# 2. ARGENTINA DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════
separator("2. Argentina voting pattern — 2024 vs 2025 by topic")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.ARG", "Year": "in.(2023,2024,2025)", "order": "Year.asc,TopicTag.asc"},
    limit=5000
)
df_arg = pd.DataFrame(rows)
df_arg.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_arg[c] = pd.to_numeric(df_arg[c], errors="coerce")

arg_summary = df_arg.groupby("Year")[["Yes", "No", "Abstain", "Total"]].sum()
arg_summary["YesPct"] = (arg_summary["Yes"] / arg_summary["Total"] * 100).round(1)
print("\nArgentina overall votes:")
print(arg_summary.to_string())

# ══════════════════════════════════════════════════════════════════════════
# 3. SYRIA DEEP DIVE — regime change in Dec 2024
# ══════════════════════════════════════════════════════════════════════════
separator("3. Syria voting pattern — 2024 vs 2025 by topic")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.SYR", "Year": "in.(2023,2024,2025)", "order": "Year.asc,TopicTag.asc"},
    limit=5000
)
df_syr = pd.DataFrame(rows)
df_syr.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_syr[c] = pd.to_numeric(df_syr[c], errors="coerce")

syr_summary = df_syr.groupby("Year")[["Yes", "No", "Abstain", "Total"]].sum()
syr_summary["YesPct"] = (syr_summary["Yes"] / syr_summary["Total"] * 100).round(1)
print("\nSyria overall votes:")
print(syr_summary.to_string())

# topic breakdown
syr_24 = df_syr[df_syr.Year == 2024].set_index("TopicTag")
syr_25 = df_syr[df_syr.Year == 2025].set_index("TopicTag")
if len(syr_24) > 0 and len(syr_25) > 0:
    syr_cmp = syr_24[["Yes", "No"]].rename(columns={"Yes":"Y24","No":"N24"}).join(
        syr_25[["Yes", "No"]].rename(columns={"Yes":"Y25","No":"N25"}), how="outer")
    print("\nSyria topic comparison:")
    print(syr_cmp.to_string())

# ══════════════════════════════════════════════════════════════════════════
# 4. P1 MULTI-YEAR TREND for key countries
# ══════════════════════════════════════════════════════════════════════════
separator("4. P1 multi-year trend (2020–2025) for big movers")

key_countries = ["USA", "ARG", "DMA", "MDG", "VCT", "SYR", "STP", "SSD", "PNG", "BRA", "MMR", "ZMB"]
rows = query_supabase(
    "annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Total Votes in Year",
    params={"Year": "gte.2020", "order": "Year.asc"},
    limit=50000
)
df_trend = pd.DataFrame(rows)
df_trend.columns = ["Country", "Year", "P1_Score", "Yes", "No", "Total"]
for c in ["P1_Score", "Yes", "No", "Total"]:
    df_trend[c] = pd.to_numeric(df_trend[c], errors="coerce")

for iso in key_countries:
    country_data = df_trend[df_trend.Country == iso][["Year", "P1_Score", "Yes", "No", "Total"]]
    if len(country_data) > 0:
        print(f"\n{iso}:")
        print(country_data.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 5. PAIRWISE SIMILARITY — who moved closer/further from USA in 2025
# ══════════════════════════════════════════════════════════════════════════
separator("5. Pairwise similarity with USA — 2024 vs 2025")

rows_pw = query_supabase(
    "pairwise_similarity_yearly",
    select="Year,Country1_ISO3,Country2_ISO3,CosineSimilarity",
    params={"Year": "in.(2024,2025)", "order": "Year.asc"},
    limit=100000
)
df_pw = pd.DataFrame(rows_pw)
df_pw.columns = ["Year", "C1", "C2", "Sim"]
df_pw["Sim"] = pd.to_numeric(df_pw["Sim"], errors="coerce")

# Filter for pairs involving USA
usa_pairs = df_pw[(df_pw.C1 == "USA") | (df_pw.C2 == "USA")].copy()
usa_pairs["Other"] = usa_pairs.apply(lambda r: r.C2 if r.C1 == "USA" else r.C1, axis=1)

usa_sim = usa_pairs.pivot_table(index="Other", columns="Year", values="Sim")
usa_sim.columns = ["Sim_2024", "Sim_2025"]
usa_sim["Sim_Change"] = usa_sim["Sim_2025"] - usa_sim["Sim_2024"]
usa_sim = usa_sim.dropna()
usa_sim = usa_sim.sort_values("Sim_Change")

print(f"\nCountries moving AWAY from USA (top 15):")
print(usa_sim.head(15).to_string())
print(f"\nCountries moving CLOSER to USA (top 15):")
print(usa_sim.tail(15).to_string())

# Same for CHN and RUS
for power in ["CHN", "RUS"]:
    separator(f"5b. Pairwise similarity with {power} — 2024 vs 2025")
    p_pairs = df_pw[(df_pw.C1 == power) | (df_pw.C2 == power)].copy()
    p_pairs["Other"] = p_pairs.apply(lambda r: r.C2 if r.C1 == power else r.C1, axis=1)
    p_sim = p_pairs.pivot_table(index="Other", columns="Year", values="Sim")
    p_sim.columns = ["Sim_2024", "Sim_2025"]
    p_sim["Sim_Change"] = p_sim["Sim_2025"] - p_sim["Sim_2024"]
    p_sim = p_sim.dropna()
    p_sim = p_sim.sort_values("Sim_Change")
    print(f"\nCountries moving AWAY from {power} (top 10):")
    print(p_sim.head(10).to_string())
    print(f"\nCountries moving CLOSER to {power} (top 10):")
    print(p_sim.tail(10).to_string())

# ══════════════════════════════════════════════════════════════════════════
# 6. DOMINICA — detailed analysis (biggest dropper)
# ══════════════════════════════════════════════════════════════════════════
separator("6. Dominica (DMA) — detailed vote breakdown")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.DMA", "Year": "in.(2023,2024,2025)", "order": "Year.asc"},
    limit=5000
)
df_dma = pd.DataFrame(rows)
df_dma.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_dma[c] = pd.to_numeric(df_dma[c], errors="coerce")

dma_summary = df_dma.groupby("Year")[["Yes", "No", "Abstain", "Total"]].sum()
dma_summary["YesPct"] = (dma_summary["Yes"] / dma_summary["Total"] * 100).round(1)
print("Dominica vote summary by year:")
print(dma_summary.to_string())

# ══════════════════════════════════════════════════════════════════════════
# 7. BRAZIL — consistent gainer
# ══════════════════════════════════════════════════════════════════════════
separator("7. Brazil (BRA) — multi-year P1 and vote pattern")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.BRA", "Year": "in.(2023,2024,2025)", "order": "Year.asc"},
    limit=5000
)
df_bra = pd.DataFrame(rows)
df_bra.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_bra[c] = pd.to_numeric(df_bra[c], errors="coerce")

bra_summary = df_bra.groupby("Year")[["Yes", "No", "Abstain", "Total"]].sum()
bra_summary["YesPct"] = (bra_summary["Yes"] / bra_summary["Total"] * 100).round(1)
print("Brazil vote summary by year:")
print(bra_summary.to_string())

# ══════════════════════════════════════════════════════════════════════════
# 8. NORTHERN AMERICA deep dive (USA + CAN)
# ══════════════════════════════════════════════════════════════════════════
separator("8. Northern America (USA + CAN) — P1 trend 2020-2025")

na_data = df_trend[df_trend.Country.isin(["USA", "CAN"])]
print(na_data.pivot(index="Year", columns="Country", values="P1_Score").to_string())

# ══════════════════════════════════════════════════════════════════════════
# 9. Cross-check: topic tag volumes — how many resolutions per topic in 2025
# ══════════════════════════════════════════════════════════════════════════
separator("9. Resolution count per topic tag in 2025")

rows = query_supabase(
    "topic_votes_yearly",
    select="Year,TopicTag,TotalVotes_Topic",
    params={"Year": "eq.2025", "order": "TopicTag.asc"},
    limit=200000
)
df_t25 = pd.DataFrame(rows)
df_t25.columns = ["Year", "TopicTag", "Total"]
df_t25["Total"] = pd.to_numeric(df_t25["Total"], errors="coerce")

# Each row is one country. Total / ~191 countries ≈ resolutions tagged with that topic
topic_counts = df_t25.groupby("TopicTag").agg(
    Countries=("Total", "count"),
    TotalVotes=("Total", "sum"),
    MaxPerCountry=("Total", "max")
).sort_values("TotalVotes", ascending=False)
print(topic_counts.to_string())

print("\n\n" + "="*70)
print("  DEEP-DIVE EXTRACTION COMPLETE")
print("="*70)
