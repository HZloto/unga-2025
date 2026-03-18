"""
Validate pairwise_similarity_yearly by replicating the exact pipeline logic
from the scraper's generate_similarity_matrix() function.

Key pipeline details from source code:
  - Source table: un_votes_with_sc (not un_votes_raw)
  - SC resolutions filtered: ~Resolution.str.startswith('S/')
  - Year derived from Date column (not Scrape_Year)
  - Vote encoding: YES=1, NO=-1, ABSTAIN=0, null/NaN=0 (via map_vote + fillna(0))
  - Similarity: sklearn.metrics.pairwise.cosine_similarity on transposed vote matrix
  - Pairs: Country1 < Country2 (alpha sort, unidirectional)
"""
import os, json, urllib.request, urllib.parse, ssl, re
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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
# STEP 1: Load from un_votes_with_sc (the pipeline's actual source)
# ══════════════════════════════════════════════════════════════════════════
separator("1. Loading from un_votes_with_sc (pipeline source)")

# Load 2025 data from un_votes_with_sc
# The pipeline loads ALL data, then filters by year. We'll just get 2025.
# Pipeline derives Year from Date column.
rows_sc = query_supabase("un_votes_with_sc", select="*",
                         params={"order": "Date.asc,Resolution.asc"},
                         limit=15000)
df_sc = pd.DataFrame(rows_sc)
print(f"Total rows in un_votes_with_sc: {len(df_sc)}")

# Filter out SC resolutions (exact pipeline logic)
df_filtered = df_sc[~df_sc['Resolution'].str.startswith('S/', na=False)].copy()
print(f"After filtering SC resolutions: {len(df_filtered)}")

# Create Year from Date (exact pipeline logic)
df_filtered['Date'] = pd.to_datetime(df_filtered['Date'], errors='coerce')
df_filtered.dropna(subset=['Date'], inplace=True)
df_filtered['Year'] = df_filtered['Date'].dt.year

# How many GA resolutions in 2025?
df_2025 = df_filtered[df_filtered['Year'] == 2025].copy()
print(f"GA resolutions in 2025: {len(df_2025)}")

# Also load from un_votes_raw for comparison
rows_raw = query_supabase("un_votes_raw", select="*",
                          params={"Scrape_Year": "eq.2025"},
                          limit=500)
df_raw = pd.DataFrame(rows_raw)
print(f"Resolutions in un_votes_raw for 2025: {len(df_raw)}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 2: Compare resolution sets between the two tables
# ══════════════════════════════════════════════════════════════════════════
separator("2. Comparing resolution sets")

res_sc = set(df_2025['Resolution'].tolist())
res_raw = set(df_raw['Resolution'].tolist())
print(f"Resolutions in un_votes_with_sc (2025 GA): {len(res_sc)}")
print(f"Resolutions in un_votes_raw (2025): {len(res_raw)}")
print(f"In sc but not raw: {res_sc - res_raw}")
print(f"In raw but not sc: {res_raw - res_sc}")
print(f"Intersection: {len(res_sc & res_raw)}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 3: Identify country columns (exact pipeline logic)
# ══════════════════════════════════════════════════════════════════════════
separator("3. Identifying country columns")

def identify_country_columns(df_columns):
    """Exact copy from pipeline."""
    potential_countries = [col for col in df_columns if isinstance(col, str)
                          and len(col) == 3 and col.isupper()]
    known_non_countries = {'YES', 'NO'}
    return sorted([col for col in potential_countries if col not in known_non_countries])

country_cols_sc = identify_country_columns(df_2025.columns)
country_cols_raw = identify_country_columns(df_raw.columns)
print(f"Country columns in un_votes_with_sc: {len(country_cols_sc)}")
print(f"Country columns in un_votes_raw: {len(country_cols_raw)}")

diff_cols = set(country_cols_sc) ^ set(country_cols_raw)
if diff_cols:
    print(f"⚠️  Column differences: {sorted(diff_cols)}")
else:
    print("✓ Same country columns in both tables")

# ══════════════════════════════════════════════════════════════════════════
# STEP 4: Replicate exact pipeline similarity computation
# ══════════════════════════════════════════════════════════════════════════
separator("4. Replicating pipeline similarity computation")

def map_vote(vote):
    """Exact copy from pipeline."""
    if pd.isna(vote): return 0
    vote_str = str(vote).upper().strip()
    if vote_str == 'YES': return 1
    if vote_str == 'NO': return -1
    return 0

# Use un_votes_with_sc data (pipeline source) for 2025
country_cols = country_cols_sc
df_year = df_2025[country_cols]
print(f"Vote matrix shape (resolutions x countries): {df_year.shape}")

# Apply exact pipeline encoding
vote_matrix_numeric = df_year.apply(lambda col: col.map(map_vote)).fillna(0).astype(np.int8)
print(f"Numeric matrix shape: {vote_matrix_numeric.shape}")
print(f"Unique values: {sorted(vote_matrix_numeric.stack().unique())}")

# Compute cosine similarity (exact pipeline method)
similarity_matrix = cosine_similarity(vote_matrix_numeric.T)
df_sim = pd.DataFrame(similarity_matrix, index=country_cols, columns=country_cols)

# Convert to long format with Country1 < Country2 (exact pipeline logic)
df_sim_long = df_sim.stack().reset_index()
df_sim_long.columns = ['Country1_ISO3', 'Country2_ISO3', 'CosineSimilarity']
df_sim_long = df_sim_long[df_sim_long['Country1_ISO3'] < df_sim_long['Country2_ISO3']]
print(f"Computed pairs: {len(df_sim_long)}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 5: Compare with stored values in pairwise_similarity_yearly
# ══════════════════════════════════════════════════════════════════════════
separator("5. Comparing computed vs stored similarity values")

# Load stored values
stored_rows = query_supabase("pairwise_similarity_yearly",
    select="Country1_ISO3,Country2_ISO3,CosineSimilarity",
    params={"Year": "eq.2025"}, limit=50000)
df_stored = pd.DataFrame(stored_rows)
df_stored["CosineSimilarity"] = pd.to_numeric(df_stored["CosineSimilarity"], errors="coerce")
print(f"Stored pairs: {len(df_stored)}")

# Merge on country pair
df_compare = pd.merge(
    df_sim_long, df_stored,
    on=["Country1_ISO3", "Country2_ISO3"],
    suffixes=("_computed", "_stored"),
    how="outer"
)
print(f"Merged pairs: {len(df_compare)}")
print(f"Only in computed: {df_compare['CosineSimilarity_stored'].isna().sum()}")
print(f"Only in stored: {df_compare['CosineSimilarity_computed'].isna().sum()}")

# Calculate differences
both = df_compare.dropna(subset=["CosineSimilarity_computed", "CosineSimilarity_stored"])
both["diff"] = abs(both["CosineSimilarity_computed"] - both["CosineSimilarity_stored"])
print(f"\nPairs in both: {len(both)}")
print(f"Mean absolute diff: {both['diff'].mean():.6f}")
print(f"Max absolute diff: {both['diff'].max():.6f}")
print(f"Median absolute diff: {both['diff'].median():.6f}")
print(f"Pairs with diff < 0.0001: {(both['diff'] < 0.0001).sum()} ({(both['diff'] < 0.0001).mean()*100:.1f}%)")
print(f"Pairs with diff < 0.001: {(both['diff'] < 0.001).sum()} ({(both['diff'] < 0.001).mean()*100:.1f}%)")
print(f"Pairs with diff < 0.01: {(both['diff'] < 0.01).sum()} ({(both['diff'] < 0.01).mean()*100:.1f}%)")
print(f"Pairs with diff > 0.1: {(both['diff'] > 0.1).sum()}")

# Spot-check specific pairs
spot_pairs = [("GBR", "USA"), ("ISR", "USA"), ("CUB", "USA"),
              ("BRA", "IND"), ("CHN", "RUS"), ("DEU", "FRA"), ("ARG", "ISR")]
print("\nSpot-check pairs:")
for c1, c2 in spot_pairs:
    # Ensure c1 < c2 for lookup
    a, b = min(c1, c2), max(c1, c2)
    row = both[(both["Country1_ISO3"] == a) & (both["Country2_ISO3"] == b)]
    if len(row) > 0:
        r = row.iloc[0]
        status = "✓" if r["diff"] < 0.001 else f"❌ DIFF={r['diff']:.6f}"
        print(f"  {c1}-{c2}: computed={r['CosineSimilarity_computed']:.6f}  "
              f"stored={r['CosineSimilarity_stored']:.6f}  {status}")
    else:
        print(f"  {c1}-{c2}: NOT FOUND in merged data")

# Show worst mismatches
if (both["diff"] > 0.001).any():
    print("\nWorst mismatches (top 10):")
    worst = both.nlargest(10, "diff")
    for _, r in worst.iterrows():
        print(f"  {r['Country1_ISO3']}-{r['Country2_ISO3']}: "
              f"computed={r['CosineSimilarity_computed']:.6f}  "
              f"stored={r['CosineSimilarity_stored']:.6f}  "
              f"diff={r['diff']:.6f}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 6: If mismatch, try with un_votes_raw instead
# ══════════════════════════════════════════════════════════════════════════
if both["diff"].mean() > 0.001:
    separator("6. Trying with un_votes_raw instead")

    country_cols_r = identify_country_columns(df_raw.columns)
    df_year_raw = df_raw[country_cols_r]
    vote_matrix_raw = df_year_raw.apply(lambda col: col.map(map_vote)).fillna(0).astype(np.int8)
    sim_raw = cosine_similarity(vote_matrix_raw.T)
    df_sim_raw = pd.DataFrame(sim_raw, index=country_cols_r, columns=country_cols_r)
    df_sim_raw_long = df_sim_raw.stack().reset_index()
    df_sim_raw_long.columns = ['Country1_ISO3', 'Country2_ISO3', 'CosineSimilarity']
    df_sim_raw_long = df_sim_raw_long[
        df_sim_raw_long['Country1_ISO3'] < df_sim_raw_long['Country2_ISO3']]

    df_compare_raw = pd.merge(
        df_sim_raw_long, df_stored,
        on=["Country1_ISO3", "Country2_ISO3"],
        suffixes=("_computed", "_stored"),
        how="inner"
    )
    df_compare_raw["diff"] = abs(
        df_compare_raw["CosineSimilarity_computed"] - df_compare_raw["CosineSimilarity_stored"])

    print(f"Using un_votes_raw: mean diff = {df_compare_raw['diff'].mean():.6f}")
    print(f"  Pairs with diff < 0.001: {(df_compare_raw['diff'] < 0.001).sum()} "
          f"({(df_compare_raw['diff'] < 0.001).mean()*100:.1f}%)")

    # Also try excluding the test resolution
    df_raw_no_test = df_raw[df_raw['Resolution'] != 'A/RES/79/125']
    df_year_nt = df_raw_no_test[country_cols_r]
    vote_matrix_nt = df_year_nt.apply(lambda col: col.map(map_vote)).fillna(0).astype(np.int8)
    sim_nt = cosine_similarity(vote_matrix_nt.T)
    df_sim_nt = pd.DataFrame(sim_nt, index=country_cols_r, columns=country_cols_r)
    df_sim_nt_long = df_sim_nt.stack().reset_index()
    df_sim_nt_long.columns = ['Country1_ISO3', 'Country2_ISO3', 'CosineSimilarity']
    df_sim_nt_long = df_sim_nt_long[
        df_sim_nt_long['Country1_ISO3'] < df_sim_nt_long['Country2_ISO3']]

    df_compare_nt = pd.merge(
        df_sim_nt_long, df_stored,
        on=["Country1_ISO3", "Country2_ISO3"],
        suffixes=("_computed", "_stored"),
        how="inner"
    )
    df_compare_nt["diff"] = abs(
        df_compare_nt["CosineSimilarity_computed"] - df_compare_nt["CosineSimilarity_stored"])

    print(f"\nExcluding test resolution: mean diff = {df_compare_nt['diff'].mean():.6f}")
    print(f"  Pairs with diff < 0.001: {(df_compare_nt['diff'] < 0.001).sum()} "
          f"({(df_compare_nt['diff'] < 0.001).mean()*100:.1f}%)")

# ══════════════════════════════════════════════════════════════════════════
# STEP 7: Check if save_data_to_supabase rounds values
# ══════════════════════════════════════════════════════════════════════════
separator("7. Checking stored value precision")

# Get sample stored values and check decimal places
sample = df_stored.head(10)
for _, r in sample.iterrows():
    val = r["CosineSimilarity"]
    # Count significant decimal digits
    val_str = f"{val:.20f}".rstrip('0')
    dec_places = len(val_str.split('.')[-1]) if '.' in val_str else 0
    print(f"  {r['Country1_ISO3']}-{r['Country2_ISO3']}: {val} ({dec_places} decimal digits)")

# The pipeline's save function rounds to 4 decimal places.
# If stored values have >4 decimal places, the data was NOT saved through
# that save function (or the code was different when data was uploaded).

print("\n\n" + "="*70)
print("  PAIRWISE VALIDATION COMPLETE")
print("="*70)
