#!/usr/bin/env python3
"""
Generate a CSV of all 2025 UNGA voted resolutions with per-country votes.

Source:  data/un_votes_2025_processed.csv
Output: analysis/unga_2025_resolutions.csv

Format:
  - Row 1: ISO3 codes as column headers (for country columns)
  - Row 2: Full country names (for country columns)
  - Rows 3+: One resolution per row, sorted by date ascending
  - Country vote values: YES / NO / ABSTAIN / (blank = did not vote)
"""

import csv
import re
from pathlib import Path

import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
SOURCE = REPO_ROOT / "data" / "un_votes_2025_processed.csv"
MAPPING = Path("/Users/hgoz/Documents/10298/un-digital-library-scraper"
               "/src/un_report_api/app/required_csvs/UN_Country_Region_Mapping_clean.csv")
OUTPUT = REPO_ROOT / "analysis" / "unga_2025_resolutions.csv"

# ── Load source data ──────────────────────────────────────────────────────────
print("Loading source data...")
df = pd.read_csv(SOURCE, low_memory=False)
print(f"  Total rows in source: {len(df)}")

# Filter to General Assembly only (exclude Security Council)
ga = df[df['Council'] == 'General Assembly'].copy()
ga = ga.sort_values('Date').reset_index(drop=True)
print(f"  GA resolutions: {len(ga)}")

# ── Identify country columns ──────────────────────────────────────────────────
# The source file has 16 meta columns (indices 0-15) followed by ISO3 country columns
country_iso3_cols = sorted(list(df.columns[16:]))
print(f"  {len(country_iso3_cols)} country columns identified")

# ── Build ISO3 → Country Name mapping ─────────────────────────────────────────
mapping_df = pd.read_csv(MAPPING)
iso3_to_name = dict(zip(mapping_df['ISO-alpha3 code'], mapping_df['Country']))

# Fill any unmapped ISO3 codes
unmapped = [c for c in country_iso3_cols if c not in iso3_to_name]
if unmapped:
    print(f"  ⚠️  Unmapped ISO3 codes (will use code as name): {unmapped}")
for c in unmapped:
    iso3_to_name[c] = c

# ── Clean titles ──────────────────────────────────────────────────────────────
def clean_title(title):
    """Remove boilerplate suffix like ': resolution / adopted by the General Assembly'."""
    patterns = [
        r'\s*:\s*resolution\s*/\s*adopted by the General Assembly\s*$',
        r'\s*:\s*decision\s*/\s*adopted by the General Assembly\s*$',
    ]
    for pat in patterns:
        title = re.sub(pat, '', title, flags=re.IGNORECASE)
    return title.strip()

ga['Title_Clean'] = ga['Title'].apply(clean_title)

# ── Clean date ─────────────────────────────────────────────────────────────────
ga['Date_Clean'] = pd.to_datetime(ga['Date']).dt.strftime('%Y-%m-%d')

# ── Build the UN Digital Library URL ───────────────────────────────────────────
ga['URL'] = 'https://digitallibrary.un.org/record/' + ga['token'].astype(str)

# ── Clean tags (pipe-separated for readability) ───────────────────────────────
def clean_tags(raw_tags):
    """Deduplicate and format tags as semicolon-separated."""
    if pd.isna(raw_tags):
        return ''
    # Tags come as comma-separated with repeated main categories
    parts = [t.strip() for t in str(raw_tags).split(',')]
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            unique.append(p)
    return '; '.join(unique)

ga['Tags_Clean'] = ga['tags'].apply(clean_tags)

# ── Assemble output ───────────────────────────────────────────────────────────
# Build header row 1 (ISO3 codes) and header row 2 (country names)
header_meta = ['Resolution', 'Date', 'Title', 'Topic Tags', 'UN Digital Library Link',
               'Yes', 'No', 'Abstain', 'No Vote']
header_row1 = header_meta + country_iso3_cols
header_row2 = [''] * len(header_meta) + [iso3_to_name.get(c, c) for c in country_iso3_cols]

# Build data rows
# Note: Source NO-VOTE COUNT is based on 193 UN members, but our CSV has 191 columns
# (AFG and VEN are absent from source). We recalculate NV from actual cells.
data_rows = []
for _, r in ga.iterrows():
    # Count votes from the actual country columns
    votes = []
    for c in country_iso3_cols:
        val = r[c]
        if pd.isna(val) or val == '':
            votes.append('')
        else:
            votes.append(str(val).strip())

    nv_count = sum(1 for v in votes if v == '')

    row = [
        r['Resolution'],
        r['Date_Clean'],
        r['Title_Clean'],
        r['Tags_Clean'],
        r['URL'],
        int(r['YES COUNT']),
        int(r['NO COUNT']),
        int(r['ABSTAIN COUNT']),
        nv_count,
    ] + votes
    data_rows.append(row)

# ── Write CSV ──────────────────────────────────────────────────────────────────
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header_row1)
    writer.writerow(header_row2)
    writer.writerows(data_rows)

print(f"\n✓ CSV written to: {OUTPUT}")
print(f"  Shape: {len(data_rows)} resolutions × {len(header_row1)} columns")
print(f"  ({len(header_meta)} metadata cols + {len(country_iso3_cols)} country cols)")

# ── Quick validation ───────────────────────────────────────────────────────────
print("\n── Quick Validation ──")
# Check vote arithmetic per resolution
errors = 0
for _, r in ga.iterrows():
    counted_yes = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'YES')
    counted_no = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'NO')
    counted_abs = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'ABSTAIN')
    counted_nv = sum(1 for c in country_iso3_cols if pd.isna(r.get(c, '')) or str(r.get(c, '')).strip() == '')
    expected_y = int(r['YES COUNT'])
    expected_n = int(r['NO COUNT'])
    expected_a = int(r['ABSTAIN COUNT'])
    expected_nv = int(r['NO-VOTE COUNT']) - 2  # Source counts 193 members, we have 191

    if counted_yes != expected_y or counted_no != expected_n or counted_abs != expected_a or counted_nv != expected_nv:
        print(f"  ❌ {r['Resolution']}: counted Y={counted_yes} N={counted_no} A={counted_abs} NV={counted_nv} "
              f"vs expected Y={expected_y} N={expected_n} A={expected_a} NV={expected_nv}")
        errors += 1

if errors == 0:
    print(f"  ✓ All {len(ga)} resolutions: vote counts match individual country votes exactly")
else:
    print(f"  ⚠️  {errors} resolution(s) with count mismatches")

# ── Summary ────────────────────────────────────────────────────────────────────
print(f"\n── Summary ──")
print(f"  Date range: {ga['Date_Clean'].min()} → {ga['Date_Clean'].max()}")
print(f"  Countries: {len(country_iso3_cols)}")
print(f"  File size: {OUTPUT.stat().st_size / 1024:.1f} KB")
