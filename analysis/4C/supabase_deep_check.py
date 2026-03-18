"""
Deep investigation of the two issues found in supabase_audit.py:
1. CHN/RUS/USA vote count mismatch (193 vs 192 — one extra resolution)
2. Pairwise cosine similarity doesn't match recomputation from raw votes
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
# ISSUE 1: CHN/RUS/USA have 193 votes in raw but 192 in annual_scores
# ══════════════════════════════════════════════════════════════════════════
separator("ISSUE 1: Vote count mismatch — which resolution is the extra one?")

# Get all 2025 resolutions
raw = query_supabase("un_votes_raw", select="*",
                     params={"Scrape_Year": "eq.2025"}, limit=500)
df_raw = pd.DataFrame(raw)
print(f"Total resolutions in un_votes_raw for 2025: {len(df_raw)}")

# For each of CHN, RUS, USA, find which resolution(s) they voted on
# that don't count in annual_scores
import re
country_cols = [c for c in df_raw.columns if re.match(r'^[A-Z]{3}$', c)
                and c not in {"YES", "NO"}]

# Get annual_scores totals
ann = query_supabase("annual_scores",
    select="Country name,Yes Votes,No Votes,Abstain Votes,Total Votes in Year",
    params={"Year": "eq.2025"}, limit=200)
df_ann = pd.DataFrame(ann)
df_ann.columns = ["Country", "Yes", "No", "Abstain", "Total"]
for c in ["Yes", "No", "Abstain", "Total"]:
    df_ann[c] = pd.to_numeric(df_ann[c], errors="coerce")

# Check how many countries have 193 votes in raw (voted on all resolutions)
votes_per_country = {}
for col in country_cols:
    voted = df_raw[col].notna() & (df_raw[col] != "")
    voted_count = voted.sum()
    yes_c = (df_raw[col] == "YES").sum()
    no_c = (df_raw[col] == "NO").sum()
    abs_c = (df_raw[col] == "ABSTAIN").sum()
    total_c = yes_c + no_c + abs_c
    votes_per_country[col] = {"voted": voted_count, "Y": yes_c, "N": no_c, "A": abs_c, "total": total_c}

# Countries that voted on all 193
voted_all = {c: v for c, v in votes_per_country.items() if v["total"] == 193}
print(f"\nCountries that voted on all 193 resolutions: {len(voted_all)}")
for c in sorted(voted_all):
    ann_row = df_ann[df_ann["Country"] == c]
    ann_total = int(ann_row["Total"].iloc[0]) if len(ann_row) > 0 else "N/A"
    print(f"  {c}: raw_total=193, annual_total={ann_total}")

# For countries with mismatch, find which specific resolution(s) differ
print("\n--- Identifying the mystery resolution ---")
# The simplest approach: for CHN which has raw=193 but annual=192,
# there must be 1 resolution where either:
# (a) annual_scores doesn't count it, or
# (b) the vote is counted differently

# Let's check: which resolution has the fewest non-null votes?
df_raw["nonull_count"] = df_raw[country_cols].apply(
    lambda row: sum(1 for v in row if pd.notna(v) and v in ("YES", "NO", "ABSTAIN")), axis=1)
df_raw_sorted = df_raw.sort_values("nonull_count")
print(f"\nResolution with fewest voters:")
for _, r in df_raw_sorted.head(5).iterrows():
    print(f"  {r['Resolution']:20s} voters={r['nonull_count']}  date={str(r.get('Date',''))[:10]}  "
          f"title={str(r.get('Title',''))[:70]}")

# Check: is there a resolution where annual_scores max Total is 192 
# but raw has 193 total resolutions?
# This means annual_scores counts 192 resolutions for countries that voted on all
# So 1 resolution is being excluded from the annual count
# Find which one by checking: which resolution does CHN vote on that
# might not be in the annual count?

# Actually the annual_scores Total = number of resolutions a country voted on
# If CHN voted YES/NO/ABSTAIN on 193 resolutions but annual Total=192,
# then the aggregation excludes 1 resolution
# Let's find: for CHN, what does it vote on each resolution?
print("\n--- CHN vote on each resolution ---")
mismatched_countries = ["CHN", "RUS", "USA"]
for iso in mismatched_countries:
    ann_row = df_ann[df_ann["Country"] == iso]
    if len(ann_row) == 0:
        continue
    ann_yes = int(ann_row["Yes"].iloc[0])
    ann_no = int(ann_row["No"].iloc[0])
    ann_abs = int(ann_row["Abstain"].iloc[0])
    ann_total = int(ann_row["Total"].iloc[0])
    
    raw_yes = (df_raw[iso] == "YES").sum()
    raw_no = (df_raw[iso] == "NO").sum()
    raw_abs = (df_raw[iso] == "ABSTAIN").sum()
    raw_total = raw_yes + raw_no + raw_abs
    
    diff_yes = raw_yes - ann_yes
    diff_no = raw_no - ann_no
    diff_abs = raw_abs - ann_abs
    
    print(f"\n  {iso}: raw=({raw_yes}/{raw_no}/{raw_abs}/{raw_total}) "
          f"ann=({ann_yes}/{ann_no}/{ann_abs}/{ann_total})")
    print(f"  Diff: Y={diff_yes:+d}, N={diff_no:+d}, A={diff_abs:+d}")

# The difference pattern:
# CHN: raw 167Y/8N/18A=193, ann 167Y/7N/18A=192 → 1 extra NO
# RUS: raw 142Y/31N/20A=193, ann 142Y/31N/19A=192 → 1 extra ABSTAIN
# USA: raw 11Y/174N/8A=193, ann 10Y/174N/8A=192 → 1 extra YES
# So there's 1 resolution that's being excluded from annual_scores
# For CHN it's a NO, for RUS it's an ABSTAIN, for USA it's a YES

# Find the resolution that causes each mismatch
# If we exclude 1 resolution at a time, which one makes raw match annual?
print("\n--- Finding the excluded resolution ---")
# For each of the 193 resolutions, remove it and check if counts match
for iso in mismatched_countries:
    ann_row = df_ann[df_ann["Country"] == iso]
    ann_yes = int(ann_row["Yes"].iloc[0])
    ann_no = int(ann_row["No"].iloc[0])
    ann_abs = int(ann_row["Abstain"].iloc[0])
    
    found = []
    for idx, r in df_raw.iterrows():
        vote = r[iso]
        # If we exclude this resolution, do counts match?
        raw_yes = (df_raw[iso] == "YES").sum()
        raw_no = (df_raw[iso] == "NO").sum()
        raw_abs = (df_raw[iso] == "ABSTAIN").sum()
        
        if vote == "YES":
            test_yes, test_no, test_abs = raw_yes - 1, raw_no, raw_abs
        elif vote == "NO":
            test_yes, test_no, test_abs = raw_yes, raw_no - 1, raw_abs
        elif vote == "ABSTAIN":
            test_yes, test_no, test_abs = raw_yes, raw_no, raw_abs - 1
        else:
            continue
        
        if test_yes == ann_yes and test_no == ann_no and test_abs == ann_abs:
            found.append({
                "Resolution": r.get("Resolution", ""),
                "Title": str(r.get("Title", ""))[:70],
                "Date": str(r.get("Date", ""))[:10],
                "Vote": vote,
            })
    
    if found:
        print(f"\n  {iso}: Excluding any of these {len(found)} resolution(s) matches annual_scores:")
        for f in found:
            print(f"    {f['Resolution']:20s} vote={f['Vote']:>7s} date={f['Date']} {f['Title']}")
    else:
        print(f"\n  {iso}: No single resolution exclusion fixes the mismatch")


# ══════════════════════════════════════════════════════════════════════════
# ISSUE 2: Pairwise cosine similarity mismatch
# ══════════════════════════════════════════════════════════════════════════
separator("ISSUE 2: Pairwise cosine — why don't spot-checks match?")

def vote_to_num(v):
    if v == "YES": return 1
    if v == "NO": return -1
    if v == "ABSTAIN": return 0
    return None

# Hypothesis 1: The pipeline uses a different encoding (e.g., YES=1, NO=0, ABSTAIN=0.5)
# Hypothesis 2: The pipeline excludes non-votes differently
# Hypothesis 3: The pipeline uses the 192 resolutions (excluding the mystery one)

# Let's test multiple encodings
print("\nTesting different vote encodings for USA-GBR pair:")

usa_raw = [df_raw.iloc[i]["USA"] for i in range(len(df_raw))]
gbr_raw = [df_raw.iloc[i]["GBR"] for i in range(len(df_raw))]

# Get stored value
pw_data = query_supabase("pairwise_similarity_yearly",
    select="CosineSimilarity",
    params={"Year": "eq.2025", "Country1_ISO3": "eq.GBR", "Country2_ISO3": "eq.USA"})
if not pw_data:
    pw_data = query_supabase("pairwise_similarity_yearly",
        select="CosineSimilarity",
        params={"Year": "eq.2025", "Country1_ISO3": "eq.USA", "Country2_ISO3": "eq.GBR"})
stored = float(pw_data[0]["CosineSimilarity"]) if pw_data else None
print(f"Stored GBR-USA: {stored}")

# Encoding A: YES=1, NO=-1, ABSTAIN=0, null=excluded
def compute_cosine(c1_votes, c2_votes, encode_fn, include_null=False, null_val=0):
    v1, v2 = [], []
    for a, b in zip(c1_votes, c2_votes):
        a_enc = encode_fn(a)
        b_enc = encode_fn(b)
        if not include_null:
            if a_enc is None or b_enc is None:
                continue
        else:
            if a_enc is None: a_enc = null_val
            if b_enc is None: b_enc = null_val
        v1.append(a_enc)
        v2.append(b_enc)
    if not v1:
        return 0
    v1, v2 = np.array(v1, dtype=float), np.array(v2, dtype=float)
    dot = np.dot(v1, v2)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0
    return dot / (n1 * n2)

enc_a = lambda v: {  "YES": 1, "NO": -1, "ABSTAIN": 0}.get(v, None)
enc_b = lambda v: {"YES": 1, "NO": 0, "ABSTAIN": 0.5}.get(v, None)
enc_c = lambda v: {"YES": 1, "NO": -1, "ABSTAIN": 0.5}.get(v, None)
enc_d = lambda v: {"YES": 1, "NO": 0, "ABSTAIN": 0}.get(v, None)

test_pairs = [
    ("USA", "GBR"), ("USA", "ISR"), ("USA", "CUB"),
    ("BRA", "IND"), ("CHN", "RUS"), ("FRA", "DEU")
]

# Get all stored values
stored_vals = {}
for c1, c2 in test_pairs:
    pw = query_supabase("pairwise_similarity_yearly",
        select="Country1_ISO3,Country2_ISO3,CosineSimilarity",
        params={"Year": "eq.2025"})
    break  # Just get all for 2025

pw_all = query_supabase("pairwise_similarity_yearly",
    select="Country1_ISO3,Country2_ISO3,CosineSimilarity",
    params={"Year": "eq.2025"}, limit=50000)
df_pw = pd.DataFrame(pw_all)
df_pw["CosineSimilarity"] = pd.to_numeric(df_pw["CosineSimilarity"], errors="coerce")

for c1, c2 in test_pairs:
    row = df_pw[((df_pw["Country1_ISO3"]==c1)&(df_pw["Country2_ISO3"]==c2)) |
                ((df_pw["Country1_ISO3"]==c2)&(df_pw["Country2_ISO3"]==c1))]
    stored_vals[(c1,c2)] = float(row.iloc[0]["CosineSimilarity"]) if len(row) > 0 else None

encodings = {
    "YES=1 NO=-1 ABS=0 null=skip": (enc_a, False, 0),
    "YES=1 NO=0 ABS=0.5 null=skip": (enc_b, False, 0),
    "YES=1 NO=-1 ABS=0.5 null=skip": (enc_c, False, 0),
    "YES=1 NO=0 ABS=0 null=skip": (enc_d, False, 0),
    "YES=1 NO=-1 ABS=0 null=0": (enc_a, True, 0),
    "YES=1 NO=0 ABS=0.5 null=0": (enc_b, True, 0),
    "YES=1 NO=-1 ABS=0 null=-1": (enc_a, True, -1),
}

print(f"\n{'Encoding':<40s}", end="")
for c1, c2 in test_pairs:
    print(f" {c1}-{c2:>3s}", end="")
print("  Avg|Diff|")

for enc_name, (enc_fn, inc_null, null_v) in encodings.items():
    diffs = []
    print(f"{enc_name:<40s}", end="")
    for c1, c2 in test_pairs:
        v1 = [df_raw.iloc[i][c1] for i in range(len(df_raw))]
        v2 = [df_raw.iloc[i][c2] for i in range(len(df_raw))]
        computed = compute_cosine(v1, v2, enc_fn, inc_null, null_v)
        stored = stored_vals.get((c1, c2))
        if stored is not None:
            diff = abs(computed - stored)
            diffs.append(diff)
            print(f" {diff:7.4f}", end="")
        else:
            print(f"    N/A", end="")
    if diffs:
        print(f"  {np.mean(diffs):.4f}")
    else:
        print()

# Also try: what if pairwise was computed on a SUBSET of resolutions?
# Check if the stored values match when we use only the first 192 resolutions
print("\n\nTrying: exclude last resolution (193rd)")
# Sort by date to find which is the "extra" one
df_raw_sorted = df_raw.sort_values("Date")
for n_exclude in [0, 1]:
    df_subset = df_raw_sorted.iloc[:-1] if n_exclude else df_raw_sorted
    diffs = []
    for c1, c2 in test_pairs:
        v1 = df_subset[c1].tolist()
        v2 = df_subset[c2].tolist()
        computed = compute_cosine(v1, v2, enc_a, False, 0)
        stored = stored_vals.get((c1, c2))
        if stored is not None:
            diffs.append(abs(computed - stored))
    tag = f"n={len(df_subset)} resolutions"
    print(f"  {tag}: avg diff = {np.mean(diffs):.4f}")

# Final hypothesis: maybe they exclude ABSTAIN from the vector entirely
# (treat it like null/no-vote)
print("\nTrying: ABSTAIN treated as non-vote (excluded)")
enc_noabs = lambda v: {"YES": 1, "NO": -1}.get(v, None)
diffs = []
for c1, c2 in test_pairs:
    v1 = [df_raw.iloc[i][c1] for i in range(len(df_raw))]
    v2 = [df_raw.iloc[i][c2] for i in range(len(df_raw))]
    computed = compute_cosine(v1, v2, enc_noabs, False, 0)
    stored = stored_vals.get((c1, c2))
    if stored is not None:
        diff = abs(computed - stored)
        diffs.append(diff)
        print(f"  {c1}-{c2}: computed={computed:.6f} stored={stored:.6f} diff={diff:.4f}")
print(f"  Avg diff: {np.mean(diffs):.4f}")

# What if they use YES=1, NO=-1 and ABSTAIN as a SEPARATE dimension?
# i.e., 3D vector per resolution: (yes, no, abstain)
print("\nTrying: 3D one-hot encoding (YES=[1,0,0] NO=[0,1,0] ABS=[0,0,1] null=excluded)")
def compute_cosine_3d(c1_votes, c2_votes):
    v1, v2 = [], []
    for a, b in zip(c1_votes, c2_votes):
        a_enc = {"YES": [1,0,0], "NO": [0,1,0], "ABSTAIN": [0,0,1]}.get(a)
        b_enc = {"YES": [1,0,0], "NO": [0,1,0], "ABSTAIN": [0,0,1]}.get(b)
        if a_enc is None or b_enc is None:
            continue
        v1.extend(a_enc)
        v2.extend(b_enc)
    if not v1:
        return 0
    v1, v2 = np.array(v1, dtype=float), np.array(v2, dtype=float)
    dot = np.dot(v1, v2)
    n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
    if n1 == 0 or n2 == 0:
        return 0
    return dot / (n1 * n2)

diffs = []
for c1, c2 in test_pairs:
    v1 = [df_raw.iloc[i][c1] for i in range(len(df_raw))]
    v2 = [df_raw.iloc[i][c2] for i in range(len(df_raw))]
    computed = compute_cosine_3d(v1, v2)
    stored = stored_vals.get((c1, c2))
    if stored is not None:
        diff = abs(computed - stored)
        diffs.append(diff)
        print(f"  {c1}-{c2}: computed={computed:.6f} stored={stored:.6f} diff={diff:.4f}")
print(f"  Avg diff: {np.mean(diffs):.4f}")

print("\n\n" + "="*70)
print("  INVESTIGATION COMPLETE")
print("="*70)
