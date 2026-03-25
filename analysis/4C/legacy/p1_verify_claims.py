"""
Critical review — verify claims in PLAN_section_4C.md against actual data.
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

def separator(title):
    print(f"\n{'='*70}\n  {title}\n{'='*70}")

def query_supabase(table, select="*", params=None, limit=10000):
    ctx = ssl.create_default_context()
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={urllib.parse.quote(select)}"
    if params:
        for k, v in params.items():
            url += f"&{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}"
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
# 1. VERIFY: Argentina vote counts — annual_scores vs topic_votes
# ══════════════════════════════════════════════════════════════════════════
separator("1. Argentina vote counts: annual_scores vs topic_votes")

# From annual_scores
rows = query_supabase("annual_scores",
    select="Country name,Year,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Country name": "eq.ARG", "Year": "in.(2023,2024,2025)"})
df = pd.DataFrame(rows)
df.columns = ["Country", "Year", "Yes", "No", "Abstain", "Total"]
print("annual_scores:")
print(df.to_string(index=False))

# From topic_votes (summed — will double-count)
rows2 = query_supabase("topic_votes_yearly",
    select="Year,Country,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.ARG", "Year": "in.(2023,2024,2025)"},
    limit=5000)
df2 = pd.DataFrame(rows2)
df2.columns = ["Year", "Country", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df2[c] = pd.to_numeric(df2[c], errors="coerce")
t_sum = df2.groupby("Year")[["Yes", "No", "Abstain", "Total"]].sum()
print("\ntopic_votes (summed across topics — multi-counted):")
print(t_sum.to_string())
print("\n⚠️  The plan §2.2 cites Yes%=90.2%, 46.9%, 34.4% — these come from topic_votes")
print("  The CORRECT source is annual_scores.")

# ══════════════════════════════════════════════════════════════════════════
# 2. VERIFY: Canada P1 exact numbers
# ══════════════════════════════════════════════════════════════════════════
separator("2. Canada P1 — 2024 vs 2025")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Country name": "eq.CAN", "Year": "in.(2024,2025)"})
df_can = pd.DataFrame(rows)
df_can.columns = ["Country", "Year", "P1", "Yes", "No", "Abstain", "Total"]
print(df_can.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 3. CHECK: Resolution count per year — is 2024 really ~95?
# ══════════════════════════════════════════════════════════════════════════
separator("3. Resolution counts in un_votes_raw by year")

for year in [2023, 2024, 2025]:
    rows = query_supabase("un_votes_raw",
        select="Scrape_Year",
        params={"Scrape_Year": f"eq.{year}"},
        limit=500)
    print(f"  {year}: {len(rows)} resolutions in un_votes_raw")

# Also check from annual_scores what the max Total Votes was
rows = query_supabase("annual_scores",
    select="Year,Total Votes in Year",
    params={"Year": "in.(2023,2024,2025)"},
    limit=1000)
df_tv = pd.DataFrame(rows)
df_tv.columns = ["Year", "Total"]
df_tv["Total"] = pd.to_numeric(df_tv["Total"], errors="coerce")
print("\nMax total votes per year (from annual_scores):")
print(df_tv.groupby("Year")["Total"].max().to_string())
print("\nMedian total votes per year:")
print(df_tv.groupby("Year")["Total"].median().to_string())

# ══════════════════════════════════════════════════════════════════════════
# 4. CHECK: "DISARMAMENT" tag — was it really absent or tagging artifact?
# ══════════════════════════════════════════════════════════════════════════
separator("4. Disarmament tag check — is it in 2025 resolutions?")

rows = query_supabase("un_votes_raw",
    select="Title,tags",
    params={"Scrape_Year": "eq.2025"},
    limit=500)
df_tags = pd.DataFrame(rows)
df_tags.columns = ["Title", "Tags"]

# Search for disarmament-related titles
disarm_titles = df_tags[df_tags.Title.str.contains("disarm|nuclear|weapon|arms", case=False, na=False)]
print(f"Resolutions in 2025 with disarmament-related titles: {len(disarm_titles)}")
for _, r in disarm_titles.iterrows():
    tags = r['Tags'][:100] if pd.notna(r['Tags']) else 'None'
    print(f"  • {r['Title'][:80]}")
    print(f"    Tags: {tags}")

# Also check if DISARMAMENT tag exists in topic_votes for 2025
rows_d = query_supabase("topic_votes_yearly",
    select="TopicTag,TotalVotes_Topic",
    params={"Year": "eq.2025", "TopicTag": "like.*DISARMAMENT*"},
    limit=100)
print(f"\ntopic_votes_yearly rows with 'DISARMAMENT' tag in 2025: {len(rows_d)}")

# ══════════════════════════════════════════════════════════════════════════
# 5. CHECK: USA yes% from annual_scores (not topic_votes)
# ══════════════════════════════════════════════════════════════════════════
separator("5. USA vote breakdown from annual_scores")

rows = query_supabase("annual_scores",
    select="Country name,Year,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Country name": "eq.USA", "Year": "in.(2023,2024,2025)"})
df_usa = pd.DataFrame(rows)
df_usa.columns = ["Country", "Year", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_usa[c] = pd.to_numeric(df_usa[c], errors="coerce")
df_usa["YesPct"] = (df_usa["Yes"] / df_usa["Total"] * 100).round(1)
df_usa["NoPct"] = (df_usa["No"] / df_usa["Total"] * 100).round(1)
print(df_usa.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 6. CHECK: What drives the -1.7 world avg decline?
# ══════════════════════════════════════════════════════════════════════════
separator("6. Decomposing the -1.7 world avg P1 decline")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score",
    params={"Year": "in.(2024,2025)"},
    limit=1000)
df_all = pd.DataFrame(rows)
df_all.columns = ["Country", "Year", "P1"]
df_all["P1"] = pd.to_numeric(df_all["P1"], errors="coerce")

d24 = df_all[df_all.Year == 2024].set_index("Country")["P1"]
d25 = df_all[df_all.Year == 2025].set_index("Country")["P1"]
both = pd.DataFrame({"P1_24": d24, "P1_25": d25}).dropna()
both["Change"] = both["P1_25"] - both["P1_24"]

avg_24 = d24.mean()
avg_25 = d25.mean()
print(f"Countries in 2024: {len(d24)}, in 2025: {len(d25)}, in both: {len(both)}")
print(f"Avg P1 2024 (all): {avg_24:.2f}")
print(f"Avg P1 2025 (all): {avg_25:.2f}")
print(f"Change (all): {avg_25 - avg_24:.2f}")

# What if we exclude USA?
both_no_usa = both.drop("USA", errors='ignore')
print(f"\nAvg change EXCLUDING USA: {both_no_usa['Change'].mean():.2f}")
print(f"Avg P1 2024 excl USA: {both_no_usa['P1_24'].mean():.2f}")
print(f"Avg P1 2025 excl USA: {both_no_usa['P1_25'].mean():.2f}")

# Exclude USA + ARG
both_no_ua = both.drop(["USA", "ARG"], errors='ignore')
print(f"\nAvg change EXCLUDING USA + ARG: {both_no_ua['Change'].mean():.2f}")

# How much does USA alone account for?
n = len(both)
usa_contribution = both.loc["USA", "Change"] / n if "USA" in both.index else 0
arg_contribution = both.loc["ARG", "Change"] / n if "ARG" in both.index else 0
print(f"\nUSA's contribution to world avg change: {usa_contribution:.2f} points")
print(f"ARG's contribution to world avg change: {arg_contribution:.2f} points")
print(f"Combined USA+ARG contribution: {usa_contribution + arg_contribution:.2f} points")
total_change = avg_25 - avg_24
remaining = total_change - usa_contribution - arg_contribution
print(f"Remaining (all other countries): {remaining:.2f} points")

# Countries that declined vs improved
decliners = both[both.Change < 0]
improvers = both[both.Change > 0]
print(f"\nCountries that declined: {len(decliners)} (avg change: {decliners['Change'].mean():.2f})")
print(f"Countries that improved: {len(improvers)} (avg change: {improvers['Change'].mean():.2f})")

# ══════════════════════════════════════════════════════════════════════════
# 7. CHECK: P1 methodology — what does SSD P1=0 mean with 19 votes?
# ══════════════════════════════════════════════════════════════════════════
separator("7. Countries with P1 = 0 — what does it actually mean?")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2025", "order": "Pillar 1 Score.asc"},
    limit=10)
df_low = pd.DataFrame(rows)
df_low.columns = ["Country", "Year", "P1", "Yes", "No", "Abstain", "Total"]
print(df_low.to_string(index=False))

# Same for 2024 — who had 0?
rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2024", "order": "Pillar 1 Score.asc"},
    limit=10)
df_low24 = pd.DataFrame(rows)
df_low24.columns = ["Country", "Year", "P1", "Yes", "No", "Abstain", "Total"]
print("\n2024 lowest P1:")
print(df_low24.to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 8. Resolution dating — when were 2025 resolutions actually voted?
# ══════════════════════════════════════════════════════════════════════════
separator("8. Date range of 2025 resolutions")

rows = query_supabase("un_votes_raw",
    select="Date,Resolution,Title",
    params={"Scrape_Year": "eq.2025", "order": "Date.asc"},
    limit=500)
df_dates = pd.DataFrame(rows)
df_dates.columns = ["Date", "Resolution", "Title"]
print(f"First resolution: {df_dates.iloc[0]['Date']} — {df_dates.iloc[0]['Resolution']}")
print(f"Last resolution: {df_dates.iloc[-1]['Date']} — {df_dates.iloc[-1]['Resolution']}")
print(f"Date distribution:")
df_dates["Month"] = pd.to_datetime(df_dates.Date).dt.to_period("M")
print(df_dates.groupby("Month").size().to_string())

# ══════════════════════════════════════════════════════════════════════════
# 9. Verify: topic Yes% is NOT the same as P1
# ══════════════════════════════════════════════════════════════════════════
separator("9. Methodology check — topic Yes% vs P1")
print("The plan's 'External Drivers' section reports topic-level Yes% changes.")
print("This is NOT the same as P1 (Internal Alignment). P1 is computed at the")
print("COUNTRY level. Topic Yes% is a GLOBAL aggregate — what % of all country")
print("votes on a topic were Yes.")
print()
print("These metrics answer different questions:")
print("  P1: 'How internally consistent is country X's voting pattern?'")
print("  Topic Yes%: 'How much global consensus exists on topic Y?'")
print()
print("The 2024 report discusses themes as 'areas of agreement/disagreement'")
print("which aligns with Topic Yes%, but calls the section 'External Drivers'")
print("of internal alignment — implying these are CAUSES of P1 changes.")
print("This conflation should be addressed clearly.")

# ══════════════════════════════════════════════════════════════════════════
# 10. Verify: ISR P1 vs ARG P1 — is ARG really below ISR?
# ══════════════════════════════════════════════════════════════════════════
separator("10. Israel vs Argentina P1 in 2025")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Total Votes in Year",
    params={"Country name": "in.(ISR,ARG)", "Year": "in.(2024,2025)"})
df_ia = pd.DataFrame(rows)
df_ia.columns = ["Country", "Year", "P1", "Yes", "No", "Total"]
print(df_ia.to_string(index=False))

print("\n\n" + "="*70)
print("  VERIFICATION COMPLETE")
print("="*70)
