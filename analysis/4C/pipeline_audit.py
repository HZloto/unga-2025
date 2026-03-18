"""
Pipeline Audit — identify all scraper / pipeline / aggregation issues
for engineer handoff.
"""
import os, json, urllib.request, urllib.parse, ssl, ast
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
# 1. DISARMAMENT TAG — present in raw resolutions but missing from topic_votes
# ══════════════════════════════════════════════════════════════════════════
separator("1. DISARMAMENT tag: raw vs topic_votes for 2025")

# Tags in topic_votes_yearly for 2025
tv_rows = query_supabase("topic_votes_yearly", select="TopicTag",
                         params={"Year": "eq.2025"}, limit=200000)
tv_df = pd.DataFrame(tv_rows)
tags_2025_tv = set(tv_df["TopicTag"].unique())
disarm_tv = [t for t in tags_2025_tv if "DISARM" in t.upper() or "WEAPON" in t.upper()
             or "NUCLEAR" in t.upper() or "ARMS" in t.upper() or "MILITARY" in t.upper()]
print(f"Tags in topic_votes_yearly 2025: {len(tags_2025_tv)}")
print(f"Disarmament-related tags in topic_votes: {disarm_tv if disarm_tv else 'NONE'}")

# Tags in un_votes_raw for 2025
raw_rows = query_supabase("un_votes_raw", select="Title,tags",
                          params={"Scrape_Year": "eq.2025"}, limit=500)
raw_df = pd.DataFrame(raw_rows)

# Parse raw tags
all_raw_tags = set()
for _, r in raw_df.iterrows():
    if pd.notna(r["tags"]):
        t = str(r["tags"])
        try:
            tl = ast.literal_eval(t)
            if isinstance(tl, list):
                for item in tl:
                    all_raw_tags.add(str(item).strip())
                continue
        except:
            pass
        for part in t.split(","):
            all_raw_tags.add(part.strip().strip('"').strip("'"))

disarm_raw = [t for t in all_raw_tags if "DISARM" in t.upper() or "WEAPON" in t.upper()
              or "NUCLEAR" in t.upper() or "ARMS" in t.upper() or "MILITARY" in t.upper()]
print(f"\nTags in un_votes_raw 2025: {len(all_raw_tags)}")
print(f"Disarmament-related tags in raw: {disarm_raw}")

# Resolutions with disarmament-related titles
disarm_titles = raw_df[raw_df["Title"].str.contains(
    "disarm|nuclear|weapon|arms control", case=False, na=False)]
print(f"\nResolutions with disarmament keywords in TITLE: {len(disarm_titles)}")
for _, r in disarm_titles.head(10).iterrows():
    print(f"  • {r['Title'][:90]}")

# Full tag gap analysis
missing_from_tv = all_raw_tags - tags_2025_tv
extra_in_tv = tags_2025_tv - all_raw_tags
print(f"\n--- TAG GAP ANALYSIS ---")
print(f"Tags in raw but MISSING from topic_votes: {len(missing_from_tv)}")
for t in sorted(missing_from_tv):
    # Count how many resolutions have this tag
    count = sum(1 for _, r in raw_df.iterrows() if pd.notna(r["tags"]) and t in str(r["tags"]))
    print(f"  • {t} ({count} resolutions)")
print(f"\nTags in topic_votes but NOT in raw: {len(extra_in_tv)}")
for t in sorted(extra_in_tv):
    print(f"  • {t}")

# ══════════════════════════════════════════════════════════════════════════
# 2. AFG and VEN — missing countries
# ══════════════════════════════════════════════════════════════════════════
separator("2. AFG / VEN — missing from 2025 data")

for iso in ["AFG", "VEN"]:
    # Check annual_scores
    rows_a = query_supabase("annual_scores",
        select="Country name,Year,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
        params={"Country name": f"eq.{iso}", "Year": "in.(2024,2025)"})
    print(f"\n{iso} in annual_scores:")
    for r in rows_a:
        print(f"  {r}")

    # Check un_votes_raw for their column
    try:
        raw_v = query_supabase("un_votes_raw", select=iso,
                               params={"Scrape_Year": "eq.2025"}, limit=200)
        rdf = pd.DataFrame(raw_v)
        if len(rdf) > 0:
            vc = rdf[iso].value_counts(dropna=False)
            print(f"  In un_votes_raw 2025: {dict(vc)}")
        else:
            print(f"  ???: 0 rows returned from un_votes_raw")
    except Exception as e:
        print(f"  Column {iso} not found in un_votes_raw: {e}")

# ══════════════════════════════════════════════════════════════════════════
# 3. Resolution count discrepancy across years
# ══════════════════════════════════════════════════════════════════════════
separator("3. Resolution counts: un_votes_raw vs annual_scores max total")

for year in [2022, 2023, 2024, 2025]:
    raw_count = len(query_supabase("un_votes_raw", select="Resolution",
                                    params={"Scrape_Year": f"eq.{year}"}, limit=500))
    ann_rows = query_supabase("annual_scores",
        select="Total Votes in Year",
        params={"Year": f"eq.{year}"}, limit=200)
    ann_df = pd.DataFrame(ann_rows)
    ann_df.columns = ["Total"]
    ann_df["Total"] = pd.to_numeric(ann_df["Total"], errors="coerce")
    max_total = ann_df["Total"].max()
    median_total = ann_df["Total"].median()
    print(f"  {year}: un_votes_raw={raw_count} resolutions | "
          f"annual_scores max Total={max_total} | median={median_total}")

# ══════════════════════════════════════════════════════════════════════════
# 4. P1 Score methodology — check for anomalous P1=0 countries
# ══════════════════════════════════════════════════════════════════════════
separator("4. P1 = 0.0 countries in 2025 — is this computed or default?")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2025", "Pillar 1 Score": "eq.0"}, limit=50)
print(f"Countries with P1=0.0 in 2025: {len(rows)}")
for r in rows:
    print(f"  {r['Country name']}: P1={r['Pillar 1 Score']}, "
          f"Y={r['Yes Votes']}, N={r['No Votes']}, A={r['Abstain Votes']}, "
          f"T={r['Total Votes in Year']}")

# Same for 2024
rows24 = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2024", "Pillar 1 Score": "eq.0"}, limit=50)
print(f"\nCountries with P1=0.0 in 2024: {len(rows24)}")
for r in rows24:
    print(f"  {r['Country name']}: P1={r['Pillar 1 Score']}, "
          f"Y={r['Yes Votes']}, N={r['No Votes']}, A={r['Abstain Votes']}, "
          f"T={r['Total Votes in Year']}")

# ══════════════════════════════════════════════════════════════════════════
# 5. P1 = null countries in 2025
# ══════════════════════════════════════════════════════════════════════════
separator("5. P1 = NULL countries in 2025")

rows_all = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Total Votes in Year",
    params={"Year": "eq.2025"}, limit=200)
null_p1 = [r for r in rows_all if r["Pillar 1 Score"] is None]
print(f"Countries with P1=NULL in 2025: {len(null_p1)}")
for r in null_p1:
    print(f"  {r['Country name']}: Total={r['Total Votes in Year']}")

# ══════════════════════════════════════════════════════════════════════════
# 6. STP P1=100 on 12 votes — small sample artifact
# ══════════════════════════════════════════════════════════════════════════
separator("6. P1=100 countries — small sample check")

rows = query_supabase("annual_scores",
    select="Country name,Year,Pillar 1 Score,Total Votes in Year",
    params={"Year": "eq.2025", "Pillar 1 Score": "eq.100"}, limit=50)
print(f"Countries with P1=100 in 2025: {len(rows)}")
for r in rows:
    print(f"  {r['Country name']}: Total Votes={r['Total Votes in Year']}")

# ══════════════════════════════════════════════════════════════════════════
# 7. Topic vote totals vs annual totals — quantify the multi-tag inflation
# ══════════════════════════════════════════════════════════════════════════
separator("7. Multi-tag inflation: topic_votes sum vs annual_scores total (2025)")

# Get annual totals for a sample of countries
sample_countries = ["USA", "GBR", "BRA", "CHN", "ARG", "ISR", "FRA", "IND"]
for iso in sample_countries:
    ann = query_supabase("annual_scores",
        select="Total Votes in Year",
        params={"Country name": f"eq.{iso}", "Year": "eq.2025"})
    tv = query_supabase("topic_votes_yearly",
        select="TotalVotes_Topic",
        params={"Country": f"eq.{iso}", "Year": "eq.2025"}, limit=200)
    ann_total = int(ann[0]["Total Votes in Year"]) if ann else 0
    tv_sum = sum(int(r["TotalVotes_Topic"]) for r in tv)
    ratio = tv_sum / ann_total if ann_total > 0 else 0
    print(f"  {iso}: annual={ann_total}, topic_sum={tv_sum}, ratio={ratio:.1f}x")

# ══════════════════════════════════════════════════════════════════════════
# 8. Scrape_Year vs Date discrepancies
# ══════════════════════════════════════════════════════════════════════════
separator("8. Scrape_Year vs actual Date — are resolutions assigned to correct year?")

rows = query_supabase("un_votes_raw", select="Date,Scrape_Year,Resolution,Title",
                      params={"Scrape_Year": "eq.2025"}, limit=500)
df_dates = pd.DataFrame(rows)
df_dates["Date_parsed"] = pd.to_datetime(df_dates["Date"])
df_dates["ActualYear"] = df_dates["Date_parsed"].dt.year

mismatch = df_dates[df_dates["ActualYear"] != df_dates["Scrape_Year"]]
print(f"Total 2025 resolutions: {len(df_dates)}")
print(f"Where Date year != Scrape_Year: {len(mismatch)}")
if len(mismatch) > 0:
    for _, r in mismatch.iterrows():
        print(f"  {r['Resolution']}: Date={r['Date'][:10]}, Scrape_Year={r['Scrape_Year']}")

# Date range
print(f"\nDate range of '2025' resolutions:")
print(f"  Earliest: {df_dates['Date_parsed'].min().strftime('%Y-%m-%d')}")
print(f"  Latest: {df_dates['Date_parsed'].max().strftime('%Y-%m-%d')}")
monthly = df_dates.groupby(df_dates["Date_parsed"].dt.to_period("M")).size()
print(f"  Monthly distribution:")
for m, c in monthly.items():
    print(f"    {m}: {c} resolutions")

# ══════════════════════════════════════════════════════════════════════════
# 9. Vote arithmetic check on annual_scores 2025
# ══════════════════════════════════════════════════════════════════════════
separator("9. Vote arithmetic: Yes + No + Abstain == Total (2025)")

rows = query_supabase("annual_scores",
    select="Country name,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2025"}, limit=200)
df_arith = pd.DataFrame(rows)
df_arith.columns = ["Country", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_arith[c] = pd.to_numeric(df_arith[c], errors="coerce")
df_arith["Sum"] = df_arith["Yes"] + df_arith["No"] + df_arith["Abstain"]
bad_arith = df_arith[df_arith["Sum"] != df_arith["Total"]]
print(f"Countries where Yes+No+Abstain != Total: {len(bad_arith)}")
if len(bad_arith) > 0:
    print(bad_arith.to_string(index=False))
else:
    print("✓ All pass")

# ══════════════════════════════════════════════════════════════════════════
# 10. Pairwise similarity: check for self-pairs or negative values
# ══════════════════════════════════════════════════════════════════════════
separator("10. Pairwise anomalies in 2025")

# Self-pairs
pw_self = query_supabase("pairwise_similarity_yearly",
    select="Country1_ISO3,Country2_ISO3,CosineSimilarity",
    params={"Year": "eq.2025", "Country1_ISO3": "eq.Country2_ISO3"}, limit=10)
print(f"Self-pairs (Country1==Country2): {len(pw_self)}")

# Extreme negatives
pw_neg = query_supabase("pairwise_similarity_yearly",
    select="Country1_ISO3,Country2_ISO3,CosineSimilarity",
    params={"Year": "eq.2025", "CosineSimilarity": "lt.-0.5",
            "order": "CosineSimilarity.asc"}, limit=10)
print(f"Pairs with similarity < -0.5: {len(pw_neg)}")
for r in pw_neg:
    print(f"  {r['Country1_ISO3']}-{r['Country2_ISO3']}: {r['CosineSimilarity']}")

# Total pairs in 2025
pw_count = query_supabase("pairwise_similarity_yearly",
    select="id",
    params={"Year": "eq.2025"}, limit=50000)
print(f"Total pairs in 2025: {len(pw_count)}")
expected = 193 * 192 / 2  # unidirectional
print(f"Expected (193C2): {int(expected)}")

# ══════════════════════════════════════════════════════════════════════════
# 11. duplicate rows in topic_votes_yearly for 2025
# ══════════════════════════════════════════════════════════════════════════
separator("11. Duplicate rows in topic_votes_yearly (2025)")

tv_all = query_supabase("topic_votes_yearly",
    select="Country,TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Year": "eq.2025"}, limit=200000)
tv_all_df = pd.DataFrame(tv_all)
dupes = tv_all_df.duplicated(subset=["Country", "TopicTag"], keep=False)
dupe_count = dupes.sum()
print(f"Total rows in topic_votes 2025: {len(tv_all_df)}")
print(f"Duplicate (Country, TopicTag) pairs: {dupe_count}")
if dupe_count > 0:
    dupe_df = tv_all_df[dupes].sort_values(["Country", "TopicTag"])
    print(f"Sample duplicates:")
    print(dupe_df.head(20).to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 12. Countries in annual_scores but not in pairwise (2025) and vice versa
# ══════════════════════════════════════════════════════════════════════════
separator("12. Country coverage mismatch across tables (2025)")

# annual_scores countries
ann_c = set(r["Country name"] for r in query_supabase("annual_scores",
    select="Country name", params={"Year": "eq.2025"}, limit=200))

# pairwise countries
pw_c1 = set(r["Country1_ISO3"] for r in query_supabase("pairwise_similarity_yearly",
    select="Country1_ISO3", params={"Year": "eq.2025"}, limit=50000))
pw_c2 = set(r["Country2_ISO3"] for r in query_supabase("pairwise_similarity_yearly",
    select="Country2_ISO3", params={"Year": "eq.2025"}, limit=50000))
pw_c = pw_c1 | pw_c2

# topic_votes countries
tv_c = set(r["Country"] for r in query_supabase("topic_votes_yearly",
    select="Country", params={"Year": "eq.2025"}, limit=200000))

print(f"annual_scores: {len(ann_c)} countries")
print(f"pairwise: {len(pw_c)} countries")
print(f"topic_votes: {len(tv_c)} countries")

in_ann_not_pw = ann_c - pw_c
in_ann_not_tv = ann_c - tv_c
in_pw_not_ann = pw_c - ann_c
in_tv_not_ann = tv_c - ann_c

if in_ann_not_pw:
    print(f"\nIn annual but NOT pairwise: {sorted(in_ann_not_pw)}")
if in_ann_not_tv:
    print(f"In annual but NOT topic_votes: {sorted(in_ann_not_tv)}")
if in_pw_not_ann:
    print(f"In pairwise but NOT annual: {sorted(in_pw_not_ann)}")
if in_tv_not_ann:
    print(f"In topic_votes but NOT annual: {sorted(in_tv_not_ann)}")
if not (in_ann_not_pw or in_ann_not_tv or in_pw_not_ann or in_tv_not_ann):
    print("✓ All tables cover the same 193 countries")

print("\n\n" + "=" * 70)
print("  PIPELINE AUDIT COMPLETE")
print("=" * 70)
