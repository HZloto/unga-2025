"""
P1 Internal Alignment — Data Extraction for Section 4C (2025 Report)
Queries the Supabase database for all Pillar 1 related data needed to write
the 2025 version of the "P1 Trends – Internal Alignment" section.
"""

import os
import json
import urllib.request
import urllib.parse
import ssl
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# ── Load credentials ──────────────────────────────────────────────────────
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

OUT_DIR = Path(__file__).parent
DATA_DIR = Path(__file__).parent.parent.parent / "data"

def separator(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")

# ── Query helper ──────────────────────────────────────────────────────────
def query_supabase(table, select="*", params=None, limit=10000):
    """Query Supabase REST API. Returns list of dicts."""
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
            "Prefer": "count=exact"
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
# 1. WORLD AVERAGE P1 TREND (2000-2025)
# ══════════════════════════════════════════════════════════════════════════
separator("1. World Average P1 Score Trend (2000–2025)")

rows = query_supabase(
    "annual_scores",
    select="Year,Pillar 1 Score",
    params={"Year": "gte.2000", "order": "Year.asc"}
)
df_p1 = pd.DataFrame(rows)
df_p1.columns = ["Year", "P1_Score"]
df_p1["P1_Score"] = pd.to_numeric(df_p1["P1_Score"], errors="coerce")

world_avg = df_p1.groupby("Year")["P1_Score"].mean().reset_index()
world_avg.columns = ["Year", "Avg_P1"]
world_avg["Avg_P1"] = world_avg["Avg_P1"].round(2)
print(world_avg.to_string(index=False))

# Key metric: 2024 → 2025 change
avg_2024 = world_avg.loc[world_avg.Year == 2024, "Avg_P1"].values[0]
avg_2025 = world_avg.loc[world_avg.Year == 2025, "Avg_P1"].values[0]
change = avg_2025 - avg_2024
print(f"\n  ★ 2024 world average P1: {avg_2024:.1f}")
print(f"  ★ 2025 world average P1: {avg_2025:.1f}")
print(f"  ★ Change: {change:+.1f} points")

world_avg.to_csv(OUT_DIR / "p1_world_avg_trend.csv", index=False)

# ══════════════════════════════════════════════════════════════════════════
# 2. COUNTRY-LEVEL P1 SCORES FOR 2024 AND 2025
# ══════════════════════════════════════════════════════════════════════════
separator("2. Country-level P1 scores: 2024 vs 2025")

rows = query_supabase(
    "annual_scores",
    select="Country name,Year,Pillar 1 Score,Pillar 1 Rank,Pillar 1 Normalized,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "in.(2024,2025)", "order": "Country name.asc,Year.asc"}
)
df_country = pd.DataFrame(rows)
df_country.columns = ["Country", "Year", "P1_Score", "P1_Rank", "P1_Norm", "Yes", "No", "Abstain", "Total"]
for c in ["P1_Score", "P1_Norm", "Yes", "No", "Abstain", "Total"]:
    df_country[c] = pd.to_numeric(df_country[c], errors="coerce")
df_country["P1_Rank"] = pd.to_numeric(df_country["P1_Rank"], errors="coerce")

# Pivot to compare side by side
df_2024 = df_country[df_country.Year == 2024].set_index("Country")
df_2025 = df_country[df_country.Year == 2025].set_index("Country")

compare = df_2024[["P1_Score"]].rename(columns={"P1_Score": "P1_2024"}).join(
    df_2025[["P1_Score"]].rename(columns={"P1_Score": "P1_2025"}),
    how="outer"
)
compare["Change"] = compare["P1_2025"] - compare["P1_2024"]
compare = compare.dropna(subset=["Change"])
compare = compare.sort_values("Change")

print(f"\nCountries with data in both years: {len(compare)}")
print(f"\n--- 20 BIGGEST DROPS ---")
print(compare.head(20).to_string())
print(f"\n--- 20 BIGGEST GAINS ---")
print(compare.tail(20).to_string())

compare.to_csv(OUT_DIR / "p1_country_shifts_2024_2025.csv")

# ══════════════════════════════════════════════════════════════════════════
# 3. VOTING PARTICIPATION CHANGES (spotty voting analysis)
# ══════════════════════════════════════════════════════════════════════════
separator("3. Voting participation changes 2024 → 2025")

part_2024 = df_country[df_country.Year == 2024][["Country", "Total"]].set_index("Country").rename(columns={"Total": "Total_2024"})
part_2025 = df_country[df_country.Year == 2025][["Country", "Total"]].set_index("Country").rename(columns={"Total": "Total_2025"})
participation = part_2024.join(part_2025, how="outer")
participation["Vote_Change"] = participation["Total_2025"] - participation["Total_2024"]
participation["Vote_Pct_Change"] = ((participation["Total_2025"] - participation["Total_2024"]) / participation["Total_2024"] * 100).round(1)

# Merge with P1 change
participation = participation.join(compare[["Change"]].rename(columns={"Change": "P1_Change"}))
participation = participation.dropna()

# Countries with >20% change in voting volume
big_vote_changes = participation[participation["Vote_Pct_Change"].abs() > 20].sort_values("Vote_Pct_Change")
print(f"\nCountries with >20% change in voting volume:")
print(big_vote_changes.to_string())

# Correlation between participation change and P1 change
corr = participation[["Vote_Pct_Change", "P1_Change"]].corr().iloc[0, 1]
print(f"\nCorrelation (voting volume change % vs P1 change): {corr:.3f}")

participation.to_csv(OUT_DIR / "p1_participation_analysis.csv")

# ══════════════════════════════════════════════════════════════════════════
# 4. TOPIC-LEVEL ALIGNMENT CHANGES (2024 vs 2025)
# ══════════════════════════════════════════════════════════════════════════
separator("4. Topic-level alignment changes 2024 → 2025")

rows_topic = query_supabase(
    "topic_votes_yearly",
    select="Year,Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Year": "in.(2024,2025)", "order": "Year.asc,TopicTag.asc"},
    limit=200000
)
df_topic = pd.DataFrame(rows_topic)
df_topic.columns = ["Year", "Country", "TopicTag", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_topic[c] = pd.to_numeric(df_topic[c], errors="coerce")

# Compute per-topic "alignment" = % Yes out of total (higher = more consensus)
# Better metric: compute per-topic world average Yes%
topic_summary = df_topic.groupby(["Year", "TopicTag"]).agg(
    TotalYes=("Yes", "sum"),
    TotalNo=("No", "sum"),
    TotalAbstain=("Abstain", "sum"),
    TotalVotes=("Total", "sum"),
    CountryCount=("Country", "nunique")
).reset_index()
topic_summary["YesPct"] = (topic_summary["TotalYes"] / topic_summary["TotalVotes"] * 100).round(2)
topic_summary["NoPct"] = (topic_summary["TotalNo"] / topic_summary["TotalVotes"] * 100).round(2)
topic_summary["AbstainPct"] = (topic_summary["TotalAbstain"] / topic_summary["TotalVotes"] * 100).round(2)

# Pivot by year
t2024 = topic_summary[topic_summary.Year == 2024].set_index("TopicTag")
t2025 = topic_summary[topic_summary.Year == 2025].set_index("TopicTag")

topic_compare = t2024[["YesPct", "NoPct", "AbstainPct", "TotalVotes"]].rename(
    columns={"YesPct": "YesPct_2024", "NoPct": "NoPct_2024", "AbstainPct": "AbstainPct_2024", "TotalVotes": "TotalVotes_2024"}
).join(
    t2025[["YesPct", "NoPct", "AbstainPct", "TotalVotes"]].rename(
        columns={"YesPct": "YesPct_2025", "NoPct": "NoPct_2025", "AbstainPct": "AbstainPct_2025", "TotalVotes": "TotalVotes_2025"}),
    how="outer"
)
topic_compare["YesPct_Change"] = topic_compare["YesPct_2025"] - topic_compare["YesPct_2024"]
topic_compare = topic_compare.dropna(subset=["YesPct_Change"])
topic_compare = topic_compare.sort_values("YesPct_Change")

print("\n--- Topics with DECLINING consensus (biggest drops in Yes%) ---")
print(topic_compare.head(15)[["YesPct_2024", "YesPct_2025", "YesPct_Change", "TotalVotes_2024", "TotalVotes_2025"]].to_string())

print("\n--- Topics with GROWING consensus (biggest gains in Yes%) ---")
print(topic_compare.tail(15)[["YesPct_2024", "YesPct_2025", "YesPct_Change", "TotalVotes_2024", "TotalVotes_2025"]].to_string())

topic_compare.to_csv(OUT_DIR / "p1_topic_alignment_changes.csv")

# ══════════════════════════════════════════════════════════════════════════
# 5. TOP / BOTTOM P1 COUNTRIES IN 2025
# ══════════════════════════════════════════════════════════════════════════
separator("5. Top / Bottom P1 ranked countries in 2025")

top_bottom = df_2025.dropna(subset=["P1_Score"]).sort_values("P1_Score", ascending=False)
print(f"\nTop 15 countries by P1 Score (2025):")
print(top_bottom.head(15)[["P1_Score", "P1_Rank"]].to_string())
print(f"\nBottom 15 countries by P1 Score (2025):")
print(top_bottom.tail(15)[["P1_Score", "P1_Rank"]].to_string())

# ══════════════════════════════════════════════════════════════════════════
# 6. P1 BY REGION (2024 vs 2025)
# ══════════════════════════════════════════════════════════════════════════
separator("6. P1 Scores by Region (2024 vs 2025)")

# Fetch region mapping from DB
region_rows = query_supabase(
    "un_country_region_mapping",
    select="ISO-alpha3 code,UN Region"
)
df_region = pd.DataFrame(region_rows)
df_region.columns = ["Country", "Region"]

# Merge with P1 data
for year_label, df_yr in [("2024", df_2024), ("2025", df_2025)]:
    merged = df_yr.reset_index().merge(df_region, on="Country", how="left")
    region_avg = merged.groupby("Region")["P1_Score"].agg(["mean", "median", "count"]).round(2)
    print(f"\nRegion averages — {year_label}:")
    print(region_avg.sort_values("mean", ascending=False).to_string())

# ══════════════════════════════════════════════════════════════════════════
# 7. NEW TOPICS IN 2025 (not in 2024)
# ══════════════════════════════════════════════════════════════════════════
separator("7. New topic tags in 2025 vs 2024")

topics_2024 = set(t2024.index)
topics_2025 = set(t2025.index)
new_topics = topics_2025 - topics_2024
dropped_topics = topics_2024 - topics_2025

print(f"\nNew topics in 2025 ({len(new_topics)}):")
for t in sorted(new_topics):
    row = t2025.loc[t]
    print(f"  • {t}  (Yes%={row['YesPct']:.1f}, Total votes={int(row['TotalVotes'])})")

print(f"\nDropped topics from 2024 ({len(dropped_topics)}):")
for t in sorted(dropped_topics):
    row = t2024.loc[t]
    print(f"  • {t}  (Yes%={row['YesPct']:.1f}, Total votes={int(row['TotalVotes'])})")

# ══════════════════════════════════════════════════════════════════════════
# 8. RESOLUTION-LEVEL ANALYSIS — Most divisive resolutions in 2025
# ══════════════════════════════════════════════════════════════════════════
separator("8. Most divisive resolutions in 2025")

res_rows = query_supabase(
    "un_votes_raw",
    select="Title,Resolution,Date,YES COUNT,NO-VOTE COUNT,ABSTAIN COUNT,TOTAL VOTES,tags",
    params={"Scrape_Year": "eq.2025", "order": "Date.asc"},
    limit=500
)
df_res = pd.DataFrame(res_rows)
if len(df_res) > 0:
    df_res.columns = ["Title", "Resolution", "Date", "Yes", "NoVote", "Abstain", "Total", "Tags"]
    for c in ["Yes", "NoVote", "Abstain", "Total"]:
        df_res[c] = pd.to_numeric(df_res[c], errors="coerce")
    
    # "Divisiveness" = how far from unanimous — higher No+Abstain = more divisive
    df_res["ConsensusPct"] = ((df_res["Yes"] / df_res["Total"]) * 100).round(1)
    df_res["DivisiveScore"] = (100 - df_res["ConsensusPct"]).round(1)
    df_res = df_res.sort_values("DivisiveScore", ascending=False)
    
    print(f"\nTotal resolutions in 2025: {len(df_res)}")
    print(f"\n--- 20 Most Divisive Resolutions ---")
    for _, r in df_res.head(20).iterrows():
        print(f"  [{r['Resolution']}] DivScore={r['DivisiveScore']:.0f}  Yes={int(r['Yes'])} No={int(r['NoVote'])} Abs={int(r['Abstain'])}  |  {r['Title'][:80]}")
        if pd.notna(r['Tags']):
            print(f"     Tags: {r['Tags'][:120]}")
    
    print(f"\n--- 10 Most Consensual Resolutions ---")
    for _, r in df_res.tail(10).iterrows():
        print(f"  [{r['Resolution']}] Yes%={r['ConsensusPct']:.0f}  Yes={int(r['Yes'])} No={int(r['NoVote'])} Abs={int(r['Abstain'])}  |  {r['Title'][:80]}")

    df_res.to_csv(OUT_DIR / "p1_resolutions_2025.csv", index=False)
else:
    print("  ⚠️ No resolution data found for 2025 in un_votes_raw.")

# ══════════════════════════════════════════════════════════════════════════
# 9. LONG-TERM P1 TREND (full history from 1946)
# ══════════════════════════════════════════════════════════════════════════
separator("9. Long-term P1 World Average (1946-2025)")

rows_all = query_supabase(
    "annual_scores",
    select="Year,Pillar 1 Score",
    params={"order": "Year.asc"},
    limit=50000
)
df_all = pd.DataFrame(rows_all)
df_all.columns = ["Year", "P1_Score"]
df_all["P1_Score"] = pd.to_numeric(df_all["P1_Score"], errors="coerce")
full_trend = df_all.groupby("Year")["P1_Score"].mean().reset_index()
full_trend.columns = ["Year", "Avg_P1"]
full_trend["Avg_P1"] = full_trend["Avg_P1"].round(2)
full_trend.to_csv(OUT_DIR / "p1_full_trend.csv", index=False)
print(f"Saved {len(full_trend)} years to p1_full_trend.csv")
print(full_trend.tail(10).to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 10. LEADERSHIP CHANGE ANALYSIS — countries with big P1 shifts & context
# ══════════════════════════════════════════════════════════════════════════
separator("10. Countries with >15-point P1 swings (potential leadership/policy changes)")

big_movers = compare[compare["Change"].abs() > 15].copy()
big_movers = big_movers.sort_values("Change")

# Add their voting patterns
for iso in big_movers.index:
    if iso in df_2024.index and iso in df_2025.index:
        row24 = df_2024.loc[iso]
        row25 = df_2025.loc[iso]
        big_movers.loc[iso, "Yes24"] = row24.get("Yes", None) 
        big_movers.loc[iso, "No24"] = row24.get("No", None)
        big_movers.loc[iso, "Abs24"] = row24.get("Abstain", None)
        big_movers.loc[iso, "Tot24"] = row24.get("Total", None)
        big_movers.loc[iso, "Yes25"] = row25.get("Yes", None)
        big_movers.loc[iso, "No25"] = row25.get("No", None)
        big_movers.loc[iso, "Abs25"] = row25.get("Abstain", None)
        big_movers.loc[iso, "Tot25"] = row25.get("Total", None)

print(f"\n{len(big_movers)} countries with >15-point P1 swing:")
print(big_movers.to_string())
big_movers.to_csv(OUT_DIR / "p1_big_movers.csv")

print("\n\n" + "="*70)
print("  DATA EXTRACTION COMPLETE")
print("="*70)
print(f"\nOutput files in {OUT_DIR}:")
for f in sorted(OUT_DIR.glob("p1_*.csv")):
    print(f"  • {f.name}")
