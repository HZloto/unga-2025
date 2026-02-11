#!/usr/bin/env python3
"""
Thorough validation of analysis/unga_2025_resolutions.csv

Checks:
  1. Structural / schema integrity
  2. Vote arithmetic (per-country counts match aggregate totals)
  3. Cross-reference against annual_scores.csv
  4. Cross-reference against topic_votes_yearly.csv
  5. Data completeness & anomaly detection
"""

import csv
import re
from pathlib import Path
from collections import Counter

import pandas as pd
import numpy as np

REPO = Path(__file__).parent.parent
CSV_PATH = REPO / "analysis" / "unga_2025_resolutions.csv"
ANNUAL_PATH = REPO / "data" / "annual_scores.csv"
TOPIC_PATH = REPO / "data" / "topic_votes_yearly.csv"

def separator(title):
    print(f"\n{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}\n")


# ── Load CSV ──────────────────────────────────────────────────────────────────
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

header1 = rows[0]
header2 = rows[1]
data = rows[2:]

meta_headers = header1[:9]
country_iso3 = header1[9:]
country_names = header2[9:]

# ══════════════════════════════════════════════════════════════════════════════
separator("1. STRUCTURAL VALIDATION")

# 1a. Shape
print(f"Rows: {len(rows)} total (2 header + {len(data)} data)")
print(f"Columns: {len(header1)} ({len(meta_headers)} meta + {len(country_iso3)} countries)")

# 1b. Consistent column count
lengths = set(len(r) for r in rows)
if len(lengths) == 1:
    print(f"✓ All rows have consistent column count: {lengths.pop()}")
else:
    print(f"❌ Inconsistent column counts: {lengths}")

# 1c. ISO3 format
bad_iso = [c for c in country_iso3 if not re.match(r'^[A-Z]{3}$', c)]
if not bad_iso:
    print(f"✓ All {len(country_iso3)} country headers are valid 3-letter ISO3 codes")
else:
    print(f"❌ Invalid ISO3 headers: {bad_iso}")

# 1d. Alphabetical order
if country_iso3 == sorted(country_iso3):
    print("✓ Country columns in alphabetical order")
else:
    print("❌ Country columns NOT alphabetical")

# 1e. No duplicates
if len(country_iso3) == len(set(country_iso3)):
    print("✓ No duplicate country columns")
else:
    dupes = {k: v for k, v in Counter(country_iso3).items() if v > 1}
    print(f"❌ Duplicate columns: {dupes}")

# 1f. Country name row
empty_names = [country_iso3[i] for i, n in enumerate(country_names) if not n.strip()]
if not empty_names:
    print(f"✓ All {len(country_names)} country names populated in row 2")
else:
    print(f"❌ Missing country names for: {empty_names}")

# 1g. Meta cells in row 2 blank
meta_row2 = header2[:9]
if all(m == '' for m in meta_row2):
    print("✓ Meta cells in row 2 are blank (correct)")
else:
    print(f"⚠️  Non-empty meta cells in row 2: {[m for m in meta_row2 if m]}")

# 1h. Expected meta column names
expected_meta = ['Resolution', 'Date', 'Title', 'Topic Tags', 'UN Digital Library Link',
                 'Yes', 'No', 'Abstain', 'No Vote']
if meta_headers == expected_meta:
    print(f"✓ Meta column names match expected: {expected_meta}")
else:
    print(f"❌ Meta column mismatch. Got: {meta_headers}")

# ══════════════════════════════════════════════════════════════════════════════
separator("2. DATA FIELD VALIDATION")

# 2a. Resolution ID format
res_ids = [r[0] for r in data]
unusual = [rid for rid in res_ids if not re.match(r'^A/(RES|DEC)/', rid)]
if not unusual:
    print("✓ All resolution IDs match expected A/RES/ or A/DEC/ pattern")
else:
    print(f"⚠️  Unusual resolution IDs: {unusual}")

# 2b. Duplicate resolution IDs
if len(res_ids) == len(set(res_ids)):
    print("✓ No duplicate resolution IDs")
else:
    dupes = {k: v for k, v in Counter(res_ids).items() if v > 1}
    print(f"❌ Duplicate resolution IDs: {dupes}")

# 2c. Date format & range
dates = [r[1] for r in data]
bad_dates = [(i, d) for i, d in enumerate(dates) if not re.match(r'^2025-\d{2}-\d{2}$', d)]
if not bad_dates:
    print("✓ All dates are valid 2025 dates")
else:
    for i, d in bad_dates:
        print(f"  ❌ Row {i+3}: Invalid date '{d}'")

# 2d. Date ordering
if dates == sorted(dates):
    print(f"✓ Sorted by date ascending ({min(dates)} → {max(dates)})")
else:
    print("❌ NOT sorted by date ascending")

# 2e. Titles non-empty & cleaned
empty_titles = [data[i][0] for i in range(len(data)) if not data[i][2].strip()]
boilerplate = [(data[i][0], data[i][2]) for i in range(len(data))
               if 'adopted by the general assembly' in data[i][2].lower()]
if not empty_titles:
    print("✓ All titles populated")
else:
    print(f"❌ Empty titles for: {empty_titles}")
if not boilerplate:
    print("✓ All titles cleaned (no boilerplate suffix)")
else:
    for rid, t in boilerplate:
        print(f"  ⚠️  {rid}: still has boilerplate: ...{t[-50:]}")

# 2f. Links
bad_links = [(data[i][0], data[i][4]) for i in range(len(data))
             if not data[i][4].startswith('https://digitallibrary.un.org/record/')]
if not bad_links:
    print("✓ All UN Digital Library links valid format")
else:
    for rid, link in bad_links:
        print(f"  ❌ {rid}: Invalid link '{link}'")

# 2g. Vote cell values
valid_votes = {'YES', 'NO', 'ABSTAIN', ''}
all_vals = set()
for r in data:
    for v in r[9:]:
        all_vals.add(v)
invalid = all_vals - valid_votes
if not invalid:
    print("✓ All vote values are valid (YES / NO / ABSTAIN / blank)")
else:
    print(f"❌ Invalid vote values: {invalid}")

# 2h. Vote count fields are integers
count_errors = []
for i, r in enumerate(data):
    for j, label in [(5, 'Yes'), (6, 'No'), (7, 'Abstain'), (8, 'NoVote')]:
        try:
            int(r[j])
        except ValueError:
            count_errors.append((data[i][0], label, r[j]))
if not count_errors:
    print("✓ All vote count fields are valid integers")
else:
    for rid, label, val in count_errors:
        print(f"  ❌ {rid}: Non-integer {label} count: '{val}'")


# ══════════════════════════════════════════════════════════════════════════════
separator("3. VOTE ARITHMETIC (per-resolution)")

arith_errors = 0
for i, r in enumerate(data):
    votes = r[9:]
    counted_y = sum(1 for v in votes if v == 'YES')
    counted_n = sum(1 for v in votes if v == 'NO')
    counted_a = sum(1 for v in votes if v == 'ABSTAIN')
    counted_nv = sum(1 for v in votes if v == '')

    expected_y = int(r[5])
    expected_n = int(r[6])
    expected_a = int(r[7])
    expected_nv = int(r[8])

    total_from_cells = counted_y + counted_n + counted_a + counted_nv

    errors = []
    if counted_y != expected_y:
        errors.append(f"YES: got {counted_y}, expected {expected_y}")
    if counted_n != expected_n:
        errors.append(f"NO: got {counted_n}, expected {expected_n}")
    if counted_a != expected_a:
        errors.append(f"ABSTAIN: got {counted_a}, expected {expected_a}")
    if counted_nv != expected_nv:
        errors.append(f"NO-VOTE: got {counted_nv}, expected {expected_nv}")
    if total_from_cells != len(country_iso3):
        errors.append(f"TOTAL cells: {total_from_cells}, expected {len(country_iso3)}")

    if errors:
        arith_errors += 1
        print(f"❌ {r[0]}: {'; '.join(errors)}")

if arith_errors == 0:
    print(f"✓ All {len(data)} resolutions: vote counts match exactly")
    print(f"  (YES + NO + ABSTAIN + blank = {len(country_iso3)} for every resolution)")
else:
    print(f"⚠️  {arith_errors} resolution(s) with arithmetic issues")


# ══════════════════════════════════════════════════════════════════════════════
separator("4. CROSS-CHECK vs annual_scores.csv")

annual = pd.read_csv(ANNUAL_PATH)
a25 = annual[annual['Year'] == 2025].copy()
print(f"annual_scores.csv has {len(a25)} countries for 2025")

# For each country, sum YES/NO/ABSTAIN across all 33 resolutions in our CSV
# and compare against annual_scores totals
csv_country_totals = {}
for iso_idx, iso in enumerate(country_iso3):
    col_idx = 9 + iso_idx
    y = sum(1 for r in data if r[col_idx] == 'YES')
    n = sum(1 for r in data if r[col_idx] == 'NO')
    a = sum(1 for r in data if r[col_idx] == 'ABSTAIN')
    total = y + n + a
    csv_country_totals[iso] = {'Yes': y, 'No': n, 'Abstain': a, 'Total': total}

# Compare
mismatches = []
matched = 0
missing_from_annual = []
for iso in country_iso3:
    row = a25[a25['Country name'] == iso]
    if len(row) == 0:
        missing_from_annual.append(iso)
        continue
    row = row.iloc[0]
    ann_y = int(row['Yes Votes'])
    ann_n = int(row['No Votes'])
    ann_a = int(row['Abstain Votes'])
    ann_t = int(row['Total Votes in Year'])

    csv_t = csv_country_totals[iso]

    if csv_t['Yes'] != ann_y or csv_t['No'] != ann_n or csv_t['Abstain'] != ann_a or csv_t['Total'] != ann_t:
        mismatches.append({
            'ISO3': iso,
            'CSV_Y': csv_t['Yes'], 'ANN_Y': ann_y,
            'CSV_N': csv_t['No'], 'ANN_N': ann_n,
            'CSV_A': csv_t['Abstain'], 'ANN_A': ann_a,
            'CSV_T': csv_t['Total'], 'ANN_T': ann_t,
        })
    else:
        matched += 1

if missing_from_annual:
    print(f"⚠️  {len(missing_from_annual)} countries in CSV but not in annual_scores 2025: {missing_from_annual}")

if not mismatches:
    print(f"✓ All {matched} countries: vote totals match annual_scores.csv exactly")
else:
    print(f"❌ {len(mismatches)} countries with vote total mismatches:")
    for m in mismatches[:20]:
        print(f"  {m['ISO3']}: CSV(Y={m['CSV_Y']} N={m['CSV_N']} A={m['CSV_A']} T={m['CSV_T']}) "
              f"vs Annual(Y={m['ANN_Y']} N={m['ANN_N']} A={m['ANN_A']} T={m['ANN_T']})")
    if len(mismatches) > 20:
        print(f"  ... and {len(mismatches) - 20} more")
    # Show summary stats
    diff_totals = [m['CSV_T'] - m['ANN_T'] for m in mismatches]
    print(f"\n  Total vote difference stats: min={min(diff_totals)}, max={max(diff_totals)}, "
          f"mean={np.mean(diff_totals):.1f}")
    # How many resolutions does annual_scores expect?
    # annual_scores 'Total Votes in Year' represents #resolutions the country voted on
    sample = a25.iloc[0]
    print(f"\n  Note: annual_scores Total Votes in Year for {sample['Country name']}: "
          f"{int(sample['Total Votes in Year'])}")
    print(f"  Our CSV has {len(data)} resolutions")
    print(f"  If annual_scores includes resolutions from a broader scrape window,")
    print(f"  differences may reflect timing of the upstream data refresh.")


# ══════════════════════════════════════════════════════════════════════════════
separator("5. CROSS-CHECK vs topic_votes_yearly.csv")

topic = pd.read_csv(TOPIC_PATH)
t25 = topic[topic['Year'] == 2025].copy()
print(f"topic_votes_yearly.csv has {len(t25)} rows for 2025")
print(f"  {t25['Country'].nunique()} unique countries, {t25['TopicTag'].nunique()} unique topics")

# For a sample country, compare
for sample_iso in ['USA', 'CHN', 'GBR']:
    t_country = t25[t25['Country'] == sample_iso]
    t_total_y = t_country['YesVotes_Topic'].sum()
    t_total_n = t_country['NoVotes_Topic'].sum()
    t_total_a = t_country['AbstainVotes_Topic'].sum()

    csv_t = csv_country_totals.get(sample_iso, {})
    print(f"\n  {sample_iso}: CSV totals: Y={csv_t.get('Yes','-')} N={csv_t.get('No','-')} A={csv_t.get('Abstain','-')}")
    print(f"  {sample_iso}: topic_votes sums (multi-tagged, expect higher): Y={t_total_y} N={t_total_n} A={t_total_a}")

    if t_total_y >= csv_t.get('Yes', 0) and t_total_n >= csv_t.get('No', 0):
        print(f"  ✓ Topic sums >= CSV totals (expected due to multi-tagging)")
    else:
        print(f"  ⚠️  Topic sum unexpectedly LOWER than CSV total for some vote type")


# ══════════════════════════════════════════════════════════════════════════════
separator("6. DATA COMPLETENESS & ANOMALIES")

# 6a. Countries with zero votes across all resolutions
zero_vote_countries = []
for iso_idx, iso in enumerate(country_iso3):
    col_idx = 9 + iso_idx
    total_votes = sum(1 for r in data if r[col_idx] in ('YES', 'NO', 'ABSTAIN'))
    if total_votes == 0:
        zero_vote_countries.append(iso)

if zero_vote_countries:
    print(f"⚠️  {len(zero_vote_countries)} countries with ZERO votes across all {len(data)} resolutions: {zero_vote_countries}")
else:
    print("✓ All countries voted on at least one resolution")

# 6b. Resolutions with very low participation
print("\nResolution participation rates:")
for i, r in enumerate(data):
    votes = r[9:]
    participated = sum(1 for v in votes if v in ('YES', 'NO', 'ABSTAIN'))
    n_countries = len(country_iso3)
    pct = participated / n_countries * 100
    marker = '⚠️' if pct < 70 else '✓'
    if pct < 70 or i < 5:  # Show low-participation and first 5
        print(f"  {marker} {r[0]:18s}: {participated}/{n_countries} ({pct:.1f}%) voted")

# 6c. Countries that always voted YES or always NO (might indicate data issues)
print("\nCountries with extreme voting patterns:")
extreme = []
for iso_idx, iso in enumerate(country_iso3):
    col_idx = 9 + iso_idx
    votes = [r[col_idx] for r in data if r[col_idx] in ('YES', 'NO', 'ABSTAIN')]
    if len(votes) == 0:
        continue
    yes_pct = sum(1 for v in votes if v == 'YES') / len(votes) * 100
    no_pct = sum(1 for v in votes if v == 'NO') / len(votes) * 100
    if yes_pct == 100 and len(votes) >= 10:
        extreme.append((iso, f"100% YES ({len(votes)} votes)"))
    elif no_pct >= 90 and len(votes) >= 10:
        extreme.append((iso, f"{no_pct:.0f}% NO ({len(votes)} votes)"))

for iso, pattern in extreme[:10]:
    print(f"  {iso}: {pattern}")
if not extreme:
    print("  (no extreme patterns found)")

# 6d. Resolution A/RES/79/XX placeholder
placeholder = [r[0] for r in data if '/XX' in r[0] or r[0].endswith('/XX')]
if placeholder:
    print(f"\n⚠️  Placeholder resolution ID found: {placeholder}")
    print("  This needs manual resolution number assignment from the upstream scraper")

# 6e. Tags validation — check that tags are non-empty and semicolon-separated
empty_tags = [data[i][0] for i in range(len(data)) if not data[i][3].strip()]
if empty_tags:
    print(f"\n⚠️  Resolutions with empty topic tags: {empty_tags}")
else:
    print(f"\n✓ All resolutions have topic tags")


# ══════════════════════════════════════════════════════════════════════════════
separator("7. SAMPLE DATA DISPLAY")

print("First 5 resolutions (meta only):")
for r in data[:5]:
    print(f"  {r[0]:18s} | {r[1]} | Y:{r[5]:>3s} N:{r[6]:>3s} A:{r[7]:>3s} NV:{r[8]:>3s} | {r[2][:65]}")

print(f"\nKey country votes on first resolution ({data[0][0]}):")
for sample_iso in ['USA', 'GBR', 'FRA', 'DEU', 'CHN', 'RUS', 'IND', 'BRA', 'ISR', 'IRN', 'CUB', 'PRK', 'UKR', 'AUS', 'JPN']:
    if sample_iso in country_iso3:
        idx = 9 + country_iso3.index(sample_iso)
        name = country_names[country_iso3.index(sample_iso)]
        vote = data[0][idx] if data[0][idx] else '(no vote)'
        print(f"  {sample_iso} ({name[:30]:30s}): {vote}")


separator("VALIDATION COMPLETE")
