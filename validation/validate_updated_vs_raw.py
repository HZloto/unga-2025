#!/usr/bin/env python3
"""
Validate updated extract files against un_votes_2025_processed.csv (raw source).

Checks:
1. Country coverage alignment across all files and raw source
2. Vote totals in annual_scores match raw per-country Y/N/A counts
3. Topic vote totals are consistent (sum >= annual due to multi-tagging)
4. Pairwise similarity country coverage
5. Vote arithmetic (Yes + No + Abstain == Total) in all files
6. Comparison with legacy files to quantify improvements
7. Spot-check specific countries across all files
"""

import pandas as pd
import numpy as np
from pathlib import Path

data = Path(__file__).parent.parent / "data"

# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def separator(title):
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")

pass_count = 0
fail_count = 0
warn_count = 0

def check(condition, msg):
    global pass_count, fail_count
    if condition:
        print(f"  ✓ {msg}")
        pass_count += 1
    else:
        print(f"  ❌ {msg}")
        fail_count += 1
    return condition

def warn(msg):
    global warn_count
    print(f"  ⚠️  {msg}")
    warn_count += 1

# ══════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════

separator("Loading data")

annual = pd.read_csv(data / "annual_scores (2).csv")
pairwise = pd.read_csv(data / "pairwise_similarity_yearly (2).csv")
topics = pd.read_csv(data / "topic_votes_yearly (2).csv")
raw = pd.read_csv(data / "un_votes_2025_processed.csv")

# Legacy
annual_leg = pd.read_csv(data / "legacy" / "annual_scores.csv")
pairwise_leg = pd.read_csv(data / "legacy" / "pairwise_similarity_yearly.csv")
topics_leg = pd.read_csv(data / "legacy" / "topic_votes_yearly.csv")

print(f"  Loaded annual_scores (2):           {annual.shape}")
print(f"  Loaded pairwise_similarity (2):     {pairwise.shape}")
print(f"  Loaded topic_votes (2):             {topics.shape}")
print(f"  Loaded un_votes_2025_processed:     {raw.shape}")

# Filter raw to GA only
ga = raw[raw['Council'] == 'General Assembly'].copy()
country_cols = [c for c in raw.columns if c.isupper() and len(c) == 3]
print(f"  GA resolutions in raw: {len(ga)}")
print(f"  Country columns in raw: {len(country_cols)}")

# ══════════════════════════════════════════════════════════════
# 1. Vote totals: annual_scores vs raw source
# ══════════════════════════════════════════════════════════════

separator("1. Annual Scores 2025 — Vote Totals vs Raw Source")

a25 = annual[annual['Year'] == 2025].copy()

# Build expected per-country vote counts from raw
expected_votes = {}
for iso3 in country_cols:
    votes = ga[iso3]
    yes = (votes == 'YES').sum()
    no = (votes == 'NO').sum()
    abstain = (votes == 'ABSTAIN').sum()
    total = yes + no + abstain
    expected_votes[iso3] = {'Yes': yes, 'No': no, 'Abstain': abstain, 'Total': total}

expected_df = pd.DataFrame(expected_votes).T
expected_df.index.name = 'Country'

# Detect the right column names in annual_scores
yes_col = 'Yes Votes'
no_col = 'No Votes'
abs_col = 'Abstain Votes'
tot_col = 'Total Votes in Year'

# Compare
mismatches = []
matched = 0
for _, row in a25.iterrows():
    iso3 = row['Country name']
    if iso3 not in expected_votes:
        warn(f"{iso3} in annual_scores but not in raw country columns")
        continue
    exp = expected_votes[iso3]
    act_y = int(row[yes_col])
    act_n = int(row[no_col])
    act_a = int(row[abs_col])
    act_t = int(row[tot_col])
    if act_y == exp['Yes'] and act_n == exp['No'] and act_a == exp['Abstain'] and act_t == exp['Total']:
        matched += 1
    else:
        mismatches.append({
            'Country': iso3,
            'Expected_Y': exp['Yes'], 'Actual_Y': act_y,
            'Expected_N': exp['No'], 'Actual_N': act_n,
            'Expected_A': exp['Abstain'], 'Actual_A': act_a,
            'Expected_T': exp['Total'], 'Actual_T': act_t,
        })

check(matched == len(a25), f"All {matched}/{len(a25)} countries match raw vote counts exactly")
if mismatches:
    mm_df = pd.DataFrame(mismatches)
    print(f"\n  Mismatched countries ({len(mismatches)}):")
    print(mm_df.to_string(index=False))

# Countries in raw but not in annual_scores
raw_countries = set(country_cols)
annual_countries = set(a25['Country name'])
missing_from_annual = raw_countries - annual_countries
missing_from_raw = annual_countries - raw_countries
if missing_from_annual:
    warn(f"Countries in raw but NOT in annual_scores: {sorted(missing_from_annual)}")
else:
    check(True, "No countries missing from annual_scores vs raw")
if missing_from_raw:
    warn(f"Countries in annual_scores but NOT in raw: {sorted(missing_from_raw)}")

# ══════════════════════════════════════════════════════════════
# 2. Vote arithmetic in annual_scores (all years)
# ══════════════════════════════════════════════════════════════

separator("2. Annual Scores — Vote Arithmetic (Yes + No + Abstain == Total)")

annual['calc_total'] = annual[yes_col] + annual[no_col] + annual[abs_col]
arith_fail = annual[annual['calc_total'] != annual[tot_col]]
check(len(arith_fail) == 0, f"Vote arithmetic holds for all {len(annual)} rows")
if len(arith_fail) > 0:
    print(f"  Failed rows: {len(arith_fail)}")
    print(arith_fail[['Country name', 'Year', yes_col, no_col, abs_col, tot_col, 'calc_total']].head(10))

# ══════════════════════════════════════════════════════════════
# 3. Topic Votes 2025 — Consistency with raw source
# ══════════════════════════════════════════════════════════════

separator("3. Topic Votes 2025 — Coverage & Consistency vs Raw Source")

t25 = topics[topics['Year'] == 2025].copy()

# Vote arithmetic per row
t25['calc_total'] = t25['YesVotes_Topic'] + t25['NoVotes_Topic'] + t25['AbstainVotes_Topic']
arith_fail_t = t25[t25['calc_total'] != t25['TotalVotes_Topic']]
check(len(arith_fail_t) == 0, f"Topic vote arithmetic holds for all {len(t25)} rows in 2025")
if len(arith_fail_t) > 0:
    print(f"  Failed rows: {len(arith_fail_t)}")
    print(arith_fail_t.head(10))

# Country coverage
topic_countries = set(t25['Country'].unique())
check(topic_countries == annual_countries,
      f"Topic votes 2025 has same {len(topic_countries)} countries as annual_scores")
if topic_countries != annual_countries:
    diff1 = annual_countries - topic_countries
    diff2 = topic_countries - annual_countries
    if diff1:
        warn(f"In annual but not topics: {sorted(diff1)}")
    if diff2:
        warn(f"In topics but not annual: {sorted(diff2)}")

# Per-country: sum of topic votes should be >= annual total (multi-tagging)
topic_totals = t25.groupby('Country').agg(
    sum_yes=('YesVotes_Topic', 'sum'),
    sum_no=('NoVotes_Topic', 'sum'),
    sum_abs=('AbstainVotes_Topic', 'sum'),
    sum_total=('TotalVotes_Topic', 'sum')
).reset_index()

a25_merged = a25[['Country name', yes_col, no_col, abs_col, tot_col]].rename(
    columns={'Country name': 'Country', yes_col: 'annual_yes', no_col: 'annual_no',
             abs_col: 'annual_abs', tot_col: 'annual_total'})

merged = topic_totals.merge(a25_merged, on='Country', how='outer')

below_annual = merged[merged['sum_total'] < merged['annual_total']]
check(len(below_annual) == 0,
      f"Topic vote sums >= annual totals for all countries (multi-tag expected)")
if len(below_annual) > 0:
    print(f"\n  Countries with topic sum BELOW annual total ({len(below_annual)}):")
    print(below_annual[['Country', 'sum_total', 'annual_total']].to_string(index=False))

# Ratio analysis
merged['ratio'] = merged['sum_total'] / merged['annual_total']
print(f"\n  Topic/Annual vote ratio: min={merged['ratio'].min():.2f}, "
      f"mean={merged['ratio'].mean():.2f}, max={merged['ratio'].max():.2f}")

# Number of topics
print(f"  Number of unique topics in 2025: {t25['TopicTag'].nunique()}")
print(f"  Topics: {sorted(t25['TopicTag'].unique())}")

# ══════════════════════════════════════════════════════════════
# 4. Pairwise Similarity 2025 — Country coverage
# ══════════════════════════════════════════════════════════════

separator("4. Pairwise Similarity 2025 — Country Coverage")

p25 = pairwise[pairwise['Year'] == 2025].copy()
pw_countries = set(p25['Country1_ISO3'].unique()) | set(p25['Country2_ISO3'].unique())

print(f"  Countries in pairwise 2025: {len(pw_countries)}")
print(f"  Countries in raw source:    {len(raw_countries)}")
print(f"  Countries in annual_scores: {len(annual_countries)}")

# Pairwise may include 2 extra (AFG, VEN appear in pairwise but not in raw because they have zero votes)
extra_in_pw = pw_countries - raw_countries
missing_in_pw = raw_countries - pw_countries
if extra_in_pw:
    warn(f"Countries in pairwise but NOT in raw: {sorted(extra_in_pw)}")
if missing_in_pw:
    warn(f"Countries in raw but NOT in pairwise: {sorted(missing_in_pw)}")

# Expected pairs (unidirectional): n*(n-1)/2
n = len(pw_countries)
expected_pairs = n * (n - 1) // 2
check(len(p25) == expected_pairs,
      f"Pair count matches n*(n-1)/2: {len(p25)} == {expected_pairs} (n={n})")

# Cosine similarity range
check(p25['CosineSimilarity'].min() >= -1.0001,
      f"Min cosine similarity >= -1: {p25['CosineSimilarity'].min():.4f}")
check(p25['CosineSimilarity'].max() <= 1.0001,
      f"Max cosine similarity <= 1: {p25['CosineSimilarity'].max():.4f}")

# Zero similarity analysis
zero_sim = (p25['CosineSimilarity'] == 0).sum()
print(f"\n  Zero-similarity pairs in 2025: {zero_sim} ({zero_sim/len(p25)*100:.1f}%)")

# ══════════════════════════════════════════════════════════════
# 5. Spot-check specific countries
# ══════════════════════════════════════════════════════════════

separator("5. Spot-Check: Specific Countries vs Raw Source")

spot_countries = ['USA', 'GBR', 'CHN', 'RUS', 'BRA', 'IND', 'ISR', 'ZAF', 'JPN', 'FRA']
spot_countries = [c for c in spot_countries if c in country_cols]

for iso3 in spot_countries:
    raw_yes = (ga[iso3] == 'YES').sum()
    raw_no = (ga[iso3] == 'NO').sum()
    raw_abs = (ga[iso3] == 'ABSTAIN').sum()
    raw_total = raw_yes + raw_no + raw_abs

    a_row = a25[a25['Country name'] == iso3]
    if len(a_row) == 0:
        warn(f"{iso3}: Not found in annual_scores")
        continue
    a_row = a_row.iloc[0]
    a_yes = int(a_row[yes_col])
    a_no = int(a_row[no_col])
    a_abs = int(a_row[abs_col])
    a_total = int(a_row[tot_col])

    match = (a_yes == raw_yes and a_no == raw_no and a_abs == raw_abs and a_total == raw_total)
    
    # Topic totals for this country
    tc = t25[t25['Country'] == iso3]
    t_total = tc['TotalVotes_Topic'].sum()
    t_topics = len(tc)

    status = "✓" if match else "❌"
    print(f"  {status} {iso3}: raw(Y={raw_yes},N={raw_no},A={raw_abs},T={raw_total}) "
          f"annual(Y={a_yes},N={a_no},A={a_abs},T={a_total}) "
          f"topics({t_topics} tags, sum={t_total})")

# ══════════════════════════════════════════════════════════════
# 6. Legacy vs Updated comparison detail
# ══════════════════════════════════════════════════════════════

separator("6. Legacy vs Updated — Detailed Comparison")

# Annual scores: compare 2025 rows
a_leg25 = annual_leg[annual_leg['Year'] == 2025]

# Detect column names in legacy
leg_yes_col = 'Yes Votes' if 'Yes Votes' in annual_leg.columns else None
leg_tot_col = 'Total Votes in Year' if 'Total Votes in Year' in annual_leg.columns else ('Total Votes' if 'Total Votes' in annual_leg.columns else None)

if leg_yes_col and leg_tot_col:
    # Compare vote totals
    leg_merged = a_leg25[['Country name', leg_yes_col, 'No Votes', 'Abstain Votes', leg_tot_col]].rename(
        columns={'Country name': 'Country', leg_yes_col: 'leg_yes', 'No Votes': 'leg_no',
                 'Abstain Votes': 'leg_abs', leg_tot_col: 'leg_total'})
    upd_merged = a25[['Country name', yes_col, no_col, abs_col, tot_col]].rename(
        columns={'Country name': 'Country', yes_col: 'upd_yes', no_col: 'upd_no',
                 abs_col: 'upd_abs', tot_col: 'upd_total'})
    cmp = leg_merged.merge(upd_merged, on='Country', how='outer')

    changed = cmp[(cmp['leg_yes'] != cmp['upd_yes']) |
                  (cmp['leg_no'] != cmp['upd_no']) |
                  (cmp['leg_abs'] != cmp['upd_abs']) |
                  (cmp['leg_total'] != cmp['upd_total'])]
    
    if len(changed) == 0:
        print("  Annual scores 2025: No vote count changes between legacy and updated")
    else:
        print(f"  Annual scores 2025: {len(changed)} countries have different vote counts")
        print(changed.head(20).to_string(index=False))
else:
    warn("Could not compare legacy annual vote columns — column names differ")

# Topic votes: compare coverage
t_leg25 = topics_leg[topics_leg['Year'] == 2025]
leg_topics = set(t_leg25['TopicTag'].unique())
upd_topics = set(t25['TopicTag'].unique())
new_topics = upd_topics - leg_topics
removed_topics = leg_topics - upd_topics

print(f"\n  Topic coverage comparison:")
print(f"    Legacy topics:  {len(leg_topics)}")
print(f"    Updated topics: {len(upd_topics)}")
print(f"    New topics:     {len(new_topics)}")
if new_topics:
    for t_name in sorted(new_topics):
        rows = t25[t25['TopicTag'] == t_name]
        print(f"      + {t_name} ({len(rows)} country rows, sum_total={rows['TotalVotes_Topic'].sum()})")
if removed_topics:
    print(f"    Removed topics: {sorted(removed_topics)}")

# For shared topics, check if vote counts changed
shared = leg_topics & upd_topics
if shared:
    leg_topic_agg = t_leg25.groupby('TopicTag')['TotalVotes_Topic'].sum().rename('leg_sum')
    upd_topic_agg = t25.groupby('TopicTag')['TotalVotes_Topic'].sum().rename('upd_sum')
    topic_cmp = pd.concat([leg_topic_agg, upd_topic_agg], axis=1).dropna()
    topic_changed = topic_cmp[topic_cmp['leg_sum'] != topic_cmp['upd_sum']]
    if len(topic_changed) == 0:
        check(True, f"All {len(shared)} shared topics have identical vote sums")
    else:
        warn(f"{len(topic_changed)} shared topics have different vote sums:")
        print(topic_changed)

# Pairwise: compare
p_leg25 = pairwise_leg[pairwise_leg['Year'] == 2025]
pw_leg_countries = set(p_leg25['Country1_ISO3'].unique()) | set(p_leg25['Country2_ISO3'].unique())
pw_upd_countries = set(p25['Country1_ISO3'].unique()) | set(p25['Country2_ISO3'].unique())
new_pw_c = pw_upd_countries - pw_leg_countries
lost_pw_c = pw_leg_countries - pw_upd_countries
print(f"\n  Pairwise country comparison:")
print(f"    Legacy: {len(pw_leg_countries)} countries, {len(p_leg25)} pairs")
print(f"    Updated: {len(pw_upd_countries)} countries, {len(p25)} pairs")
if new_pw_c:
    print(f"    New countries: {sorted(new_pw_c)}")
if lost_pw_c:
    print(f"    Lost countries: {sorted(lost_pw_c)}")

# Compare similarity values for shared pairs
if len(p_leg25) > 0 and len(p25) > 0:
    p_leg_keyed = p_leg25.set_index(['Country1_ISO3', 'Country2_ISO3'])['CosineSimilarity'].rename('leg_sim')
    p_upd_keyed = p25.set_index(['Country1_ISO3', 'Country2_ISO3'])['CosineSimilarity'].rename('upd_sim')
    pw_cmp = pd.concat([p_leg_keyed, p_upd_keyed], axis=1).dropna()
    pw_cmp['diff'] = (pw_cmp['upd_sim'] - pw_cmp['leg_sim']).abs()
    changed_pairs = (pw_cmp['diff'] > 1e-6).sum()
    if changed_pairs == 0:
        check(True, f"All {len(pw_cmp)} shared pairwise values unchanged")
    else:
        warn(f"{changed_pairs} pairwise values changed (out of {len(pw_cmp)} shared pairs)")
        print(f"    Mean abs diff: {pw_cmp['diff'].mean():.6f}, Max diff: {pw_cmp['diff'].max():.6f}")
        top_diffs = pw_cmp.nlargest(5, 'diff')
        print(top_diffs)

# ══════════════════════════════════════════════════════════════
# 7. Non-2025 data integrity check
# ══════════════════════════════════════════════════════════════

separator("7. Non-2025 Data Integrity — Schema & Year Coverage")

# Year 1964 should be missing
years_annual = set(annual['Year'].unique())
years_pw = set(pairwise['Year'].unique())
years_topics = set(topics['Year'].unique())
check(1964 not in years_annual, "Year 1964 correctly absent from annual_scores")
check(1964 not in years_pw, "Year 1964 correctly absent from pairwise")
check(1964 not in years_topics, "Year 1964 correctly absent from topic_votes")

expected_years = set(range(1946, 2026)) - {1964}
check(years_annual == expected_years, f"Annual years: {min(years_annual)}-{max(years_annual)}, {len(years_annual)} years")
check(years_pw == expected_years, f"Pairwise years: {min(years_pw)}-{max(years_pw)}, {len(years_pw)} years")
check(years_topics == expected_years, f"Topic years: {min(years_topics)}-{max(years_topics)}, {len(years_topics)} years")

# 193 countries per year in annual_scores
countries_per_year = annual.groupby('Year')['Country name'].nunique()
non_193 = countries_per_year[countries_per_year != 193]
if len(non_193) > 0:
    # Early years may have fewer countries
    post_1990 = non_193[non_193.index >= 1990]
    if len(post_1990) > 0:
        warn(f"Some post-1990 years don't have 193 countries: {dict(post_1990)}")
    else:
        check(True, "All post-1990 years have 193 countries in annual_scores")

# ══════════════════════════════════════════════════════════════
# 8. Completeness: are there countries in raw that voted but are missing?
# ══════════════════════════════════════════════════════════════

separator("8. Missing Country Analysis — Who Voted But Isn't in Extracts?")

# Countries in raw that had at least one vote
voting_countries = []
for iso3 in country_cols:
    votes = ga[iso3]
    if votes.isin(['YES', 'NO', 'ABSTAIN']).any():
        voting_countries.append(iso3)

print(f"  Countries that cast at least 1 vote in raw: {len(voting_countries)}")

missing_in_annual = set(voting_countries) - annual_countries
missing_in_topics = set(voting_countries) - topic_countries
missing_in_pairwise = set(voting_countries) - pw_countries

if missing_in_annual:
    warn(f"Voted in raw but missing from annual_scores: {sorted(missing_in_annual)}")
    for iso3 in sorted(missing_in_annual):
        raw_total = (ga[iso3].isin(['YES', 'NO', 'ABSTAIN'])).sum()
        print(f"      {iso3}: {raw_total} votes in raw")
else:
    check(True, "All voting countries in raw appear in annual_scores")

if missing_in_topics:
    warn(f"Voted in raw but missing from topic_votes: {sorted(missing_in_topics)}")
else:
    check(True, "All voting countries in raw appear in topic_votes")

if missing_in_pairwise:
    warn(f"Voted in raw but missing from pairwise: {sorted(missing_in_pairwise)}")
else:
    check(True, "All voting countries in raw appear in pairwise")

# Non-voting countries (in raw col but zero votes)
non_voting = set(country_cols) - set(voting_countries)
if non_voting:
    print(f"\n  Non-voting countries in raw (no Y/N/A): {sorted(non_voting)}")

# ══════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════

separator("SUMMARY")
print(f"  ✓ Passed:   {pass_count}")
print(f"  ❌ Failed:   {fail_count}")
print(f"  ⚠️  Warnings: {warn_count}")
print()
if fail_count == 0:
    print("  All critical checks passed. Updated data is consistent with raw source.")
else:
    print(f"  {fail_count} critical check(s) FAILED — review required.")
print()
