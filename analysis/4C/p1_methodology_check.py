"""
P1 Methodology verification — check whether P1 measures within-topic 
voting consistency (as per methodology description), and explain the 
ARG=0.0 vs ISR=61.8 paradox.
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
# 1. Within-topic voting consistency for ARG, ISR, USA, BRA in 2025
#    P1 = "Does a country vote consistently on similar themes?"
#    Measure: for each topic, what % of votes are in the dominant direction?
# ══════════════════════════════════════════════════════════════════════════
separator("1. Within-topic voting consistency (2025)")

countries = ["ARG", "ISR", "USA", "BRA", "MMR", "STP", "CHL"]

for iso in countries:
    rows = query_supabase(
        "topic_votes_yearly",
        select="TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
        params={"Country": f"eq.{iso}", "Year": "eq.2025"},
        limit=500)
    df = pd.DataFrame(rows)
    if len(df) == 0:
        print(f"\n{iso}: no topic data for 2025")
        continue
    df.columns = ["Topic", "Yes", "No", "Abstain", "Total"]
    for c in ["Yes", "No", "Abstain", "Total"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    
    # For each topic, compute the dominant vote direction and consistency
    df["MaxVote"] = df[["Yes", "No", "Abstain"]].max(axis=1)
    df["Consistency"] = (df["MaxVote"] / df["Total"] * 100).round(1)
    df["Dominant"] = df[["Yes", "No", "Abstain"]].idxmax(axis=1)
    
    # Get P1 score
    p1_rows = query_supabase("annual_scores",
        select="Pillar 1 Score",
        params={"Country name": f"eq.{iso}", "Year": "eq.2025"})
    p1 = p1_rows[0]["Pillar 1 Score"] if p1_rows else "N/A"
    
    # Weighted average consistency
    weighted_cons = (df["MaxVote"].sum() / df["Total"].sum() * 100)
    
    n_topics = df["Topic"].nunique()
    print(f"\n{iso}  (P1={p1})")
    print(f"  Topics: {n_topics}")
    print(f"  Weighted avg consistency (max-vote/total): {weighted_cons:.1f}%")
    
    # Show most inconsistent topics
    inconsistent = df[df.Total > 1].nsmallest(5, "Consistency")
    if len(inconsistent) > 0:
        print(f"  Most inconsistent topics:")
        for _, r in inconsistent.iterrows():
            print(f"    {r['Topic'][:50]:50s} Y={int(r['Yes'])} N={int(r['No'])} A={int(r['Abstain'])} T={int(r['Total'])} Cons={r['Consistency']}%")
    
    # Show most consistent topics
    consistent = df[df.Total > 2].nlargest(3, "Consistency")
    if len(consistent) > 0:
        print(f"  Most consistent topics:")
        for _, r in consistent.iterrows():
            print(f"    {r['Topic'][:50]:50s} Y={int(r['Yes'])} N={int(r['No'])} A={int(r['Abstain'])} T={int(r['Total'])} Cons={r['Consistency']}%")

# ══════════════════════════════════════════════════════════════════════════
# 2. Compare ARG vote patterns across topics: how scattered?
# ══════════════════════════════════════════════════════════════════════════
separator("2. ARG topic-level breakdown: Yes/No/Abstain spread per topic")

rows = query_supabase(
    "topic_votes_yearly",
    select="TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.ARG", "Year": "eq.2025"},
    limit=500)
df_arg = pd.DataFrame(rows)
df_arg.columns = ["Topic", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_arg[c] = pd.to_numeric(df_arg[c], errors="coerce")

# Deduplicate (topic_votes may have hierarchy levels)
df_arg_dedup = df_arg.groupby("Topic").agg({"Yes":"first","No":"first","Abstain":"first","Total":"first"}).reset_index()
df_arg_dedup["YesPct"] = (df_arg_dedup.Yes / df_arg_dedup.Total * 100).round(1)
df_arg_dedup["NoPct"] = (df_arg_dedup.No / df_arg_dedup.Total * 100).round(1)
df_arg_dedup["AbsPct"] = (df_arg_dedup.Abstain / df_arg_dedup.Total * 100).round(1)
print(df_arg_dedup.sort_values("Total", ascending=False).to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 3. Do the same for ISR
# ══════════════════════════════════════════════════════════════════════════
separator("3. ISR topic-level breakdown")

rows = query_supabase(
    "topic_votes_yearly",
    select="TopicTag,YesVotes_Topic,NoVotes_Topic,AbstainVotes_Topic,TotalVotes_Topic",
    params={"Country": "eq.ISR", "Year": "eq.2025"},
    limit=500)
df_isr = pd.DataFrame(rows)
df_isr.columns = ["Topic", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_isr[c] = pd.to_numeric(df_isr[c], errors="coerce")

df_isr_dedup = df_isr.groupby("Topic").agg({"Yes":"first","No":"first","Abstain":"first","Total":"first"}).reset_index()
df_isr_dedup["YesPct"] = (df_isr_dedup.Yes / df_isr_dedup.Total * 100).round(1)
df_isr_dedup["NoPct"] = (df_isr_dedup.No / df_isr_dedup.Total * 100).round(1)
df_isr_dedup["AbsPct"] = (df_isr_dedup.Abstain / df_isr_dedup.Total * 100).round(1)
print(df_isr_dedup.sort_values("Total", ascending=False).to_string(index=False))

# ══════════════════════════════════════════════════════════════════════════
# 4. Raw resolution-level vote breakdown for ARG 2025
#    Do they split within the same topic?
# ══════════════════════════════════════════════════════════════════════════
separator("4. ARG resolution-level votes in 2025 (from un_votes_raw)")

rows = query_supabase(
    "un_votes_raw",
    select="Resolution,Title,tags,ARG",
    params={"Scrape_Year": "eq.2025", "order": "Date.asc"},
    limit=500)
df_raw = pd.DataFrame(rows)
df_raw.columns = ["Resolution", "Title", "Tags", "ARG_Vote"]

# Count vote types
vote_counts = df_raw["ARG_Vote"].value_counts()
print(f"ARG vote distribution in 2025 (resolution-level):")
print(vote_counts.to_string())
print(f"Total resolutions: {len(df_raw)}")

# Show examples where ARG votes differently on same-tag resolutions
# Focus on HUMAN RIGHTS tag
hr_resolutions = df_raw[df_raw.Tags.str.contains("HUMAN RIGHTS", case=False, na=False)]
print(f"\nHUMAN RIGHTS tagged resolutions ({len(hr_resolutions)}):")
for _, r in hr_resolutions.iterrows():
        vote = str(r['ARG_Vote']) if pd.notna(r['ARG_Vote']) else 'NOVOTE'
        print(f"  [{vote:>7s}] {r['Resolution']:15s} {r['Title'][:70]}")
# ══════════════════════════════════════════════════════════════════════════
# 5. Same for ISR
# ══════════════════════════════════════════════════════════════════════════
separator("5. ISR resolution-level votes in 2025")

rows = query_supabase(
    "un_votes_raw",
    select="Resolution,Title,tags,ISR",
    params={"Scrape_Year": "eq.2025", "order": "Date.asc"},
    limit=500)
df_isr_raw = pd.DataFrame(rows)
df_isr_raw.columns = ["Resolution", "Title", "Tags", "ISR_Vote"]

vote_counts_isr = df_isr_raw["ISR_Vote"].value_counts()
print(f"ISR vote distribution in 2025 (resolution-level):")
print(vote_counts_isr.to_string())

# ISR on human rights
hr_isr = df_isr_raw[df_isr_raw.Tags.str.contains("HUMAN RIGHTS", case=False, na=False)]
print(f"\nHUMAN RIGHTS tagged ({len(hr_isr)}):")
for _, r in hr_isr.iterrows():
        vote = str(r['ISR_Vote']) if pd.notna(r['ISR_Vote']) else 'NOVOTE'
        print(f"  [{vote:>7s}] {r['Resolution']:15s} {r['Title'][:70]}")
# ══════════════════════════════════════════════════════════════════════════
# 6. Entropy-based consistency measure: compare ARG vs ISR
# ══════════════════════════════════════════════════════════════════════════
separator("6. Entropy-based consistency per topic")

from math import log2

def topic_entropy(yes, no, abstain, total):
    """Shannon entropy of vote distribution (0 = perfectly consistent, max ~1.58)"""
    if total == 0:
        return 0
    probs = []
    for v in [yes, no, abstain]:
        p = v / total
        if p > 0:
            probs.append(p)
    return -sum(p * log2(p) for p in probs)

for iso, df_country in [("ARG", df_arg), ("ISR", df_isr)]:
    df_c = df_country.copy()
    df_c["Entropy"] = df_c.apply(lambda r: topic_entropy(r["Yes"], r["No"], r["Abstain"], r["Total"]), axis=1)
    avg_entropy = (df_c["Entropy"] * df_c["Total"]).sum() / df_c["Total"].sum()
    print(f"\n{iso}: Weighted avg entropy = {avg_entropy:.3f} (0=consistent, 1.58=max disorder)")
    
    # Show high-entropy topics
    high_e = df_c[df_c.Total > 2].nlargest(5, "Entropy")
    for _, r in high_e.iterrows():
        print(f"  Entropy={r['Entropy']:.2f}  {r['Topic'][:50]:50s} Y={int(r['Yes'])} N={int(r['No'])} A={int(r['Abstain'])}")

# ══════════════════════════════════════════════════════════════════════════
# 7. Quick check: what about resolution-level consistency (not topic)?
#    Maybe P1 is computed from raw vote vectors not topic aggregates
# ══════════════════════════════════════════════════════════════════════════
separator("7. Resolution-level vote distribution check")

for iso in ["ARG", "ISR", "USA", "BRA", "CHL"]:
    rows = query_supabase(
        "un_votes_raw",
        select=f"{iso}",
        params={"Scrape_Year": "eq.2025"},
        limit=500)
    df_v = pd.DataFrame(rows)
    df_v.columns = ["Vote"]
    counts = df_v["Vote"].value_counts()
    total = counts.sum()
    
    # Get P1
    p1_rows = query_supabase("annual_scores",
        select="Pillar 1 Score",
        params={"Country name": f"eq.{iso}", "Year": "eq.2025"})
    p1 = float(p1_rows[0]["Pillar 1 Score"]) if p1_rows else None
    
    yes_n = counts.get("YES", 0)
    no_n = counts.get("NO", 0)
    abs_n = counts.get("ABSTAIN", 0)
    null_n = df_v["Vote"].isna().sum()
    
    print(f"\n{iso} (P1={p1:.1f}): YES={yes_n} NO={no_n} ABS={abs_n} null={null_n} total={total}")
    
    # Compute entropy at resolution level
    voted = yes_n + no_n + abs_n
    if voted > 0:
        e = topic_entropy(yes_n, no_n, abs_n, voted)
        print(f"  Overall entropy: {e:.3f}")
        # Max vote direction %
        max_v = max(yes_n, no_n, abs_n)
        print(f"  Max direction %: {max_v/voted*100:.1f}%")

print("\n\n" + "="*70)
print("  METHODOLOGY VERIFICATION COMPLETE")
print("="*70)
