#!/usr/bin/env python3
"""
Generate a CSV of all 2025 UNGA voted resolutions with per-country votes.

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
RAW_DATA = Path("/Users/hgoz/Documents/10298/un-digital-library-scraper"
                "/src/un_report_api/app/sc_data/un_votes_with_sc_rows (2).csv")
MAPPING = Path("/Users/hgoz/Documents/10298/un-digital-library-scraper"
               "/src/un_report_api/app/required_csvs/UN_Country_Region_Mapping_clean.csv")
OUTPUT = REPO_ROOT / "analysis" / "unga_2025_resolutions.csv"

# ── Load raw data ─────────────────────────────────────────────────────────────
print("Loading raw voting data...")
df = pd.read_csv(RAW_DATA, low_memory=False)

# Filter to 2025 General Assembly resolutions
ga25 = df[(df['Council'] == 'General Assembly') & (df['Scrape_Year'] == 2025)].copy()
ga25 = ga25.sort_values('Date').reset_index(drop=True)
print(f"  Found {len(ga25)} resolutions in 2025 GA session")

# ── Identify country columns ──────────────────────────────────────────────────
meta_cols = [
    'Council', 'Date', 'Title', 'Resolution', 'country', 'subregion',
    'continent', 'tags', 'TOTAL VOTES', 'NO-VOTE COUNT', 'ABSTAIN COUNT',
    'NO COUNT', 'YES COUNT', 'Link', 'token', 'Scrape_Year',
    'created_at', 'updated_at'
]
country_iso3_cols = sorted([c for c in df.columns if c not in meta_cols])
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

ga25['Title_Clean'] = ga25['Title'].apply(clean_title)

# ── Clean date ─────────────────────────────────────────────────────────────────
ga25['Date_Clean'] = pd.to_datetime(ga25['Date']).dt.strftime('%Y-%m-%d')

# ── Build the UN Digital Library URL ───────────────────────────────────────────
ga25['URL'] = 'https://digitallibrary.un.org/record/' + ga25['token'].astype(str)

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

ga25['Tags_Clean'] = ga25['tags'].apply(clean_tags)

# ── Assemble output ───────────────────────────────────────────────────────────
# Meta columns for the output
output_meta = ['Resolution', 'Date_Clean', 'Title_Clean', 'Tags_Clean', 'URL',
               'YES COUNT', 'NO COUNT', 'ABSTAIN COUNT', 'NO-VOTE COUNT']

# Build header row 1 (ISO3 codes) and header row 2 (country names)
header_meta = ['Resolution', 'Date', 'Title', 'Topic Tags', 'UN Digital Library Link',
               'Yes', 'No', 'Abstain', 'No Vote']
header_row1 = header_meta + country_iso3_cols
header_row2 = ['', '', '', '', '', '', '', '', ''] + [iso3_to_name.get(c, c) for c in country_iso3_cols]

# Build data rows
data_rows = []
for _, r in ga25.iterrows():
    row = [
        r['Resolution'],
        r['Date_Clean'],
        r['Title_Clean'],
        r['Tags_Clean'],
        r['URL'],
        int(r['YES COUNT']),
        int(r['NO COUNT']),
        int(r['ABSTAIN COUNT']),
        int(r['NO-VOTE COUNT']),
    ]
    for c in country_iso3_cols:
        val = r[c]
        if pd.isna(val) or val == '':
            row.append('')
        else:
            row.append(str(val).strip())
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
for _, r in ga25.iterrows():
    counted_yes = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'YES')
    counted_no = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'NO')
    counted_abs = sum(1 for c in country_iso3_cols if str(r.get(c, '')).strip() == 'ABSTAIN')
    counted_nv = sum(1 for c in country_iso3_cols if pd.isna(r.get(c, '')) or str(r.get(c, '')).strip() == '')
    expected_y = int(r['YES COUNT'])
    expected_n = int(r['NO COUNT'])
    expected_a = int(r['ABSTAIN COUNT'])
    expected_nv = int(r['NO-VOTE COUNT'])

    if counted_yes != expected_y or counted_no != expected_n or counted_abs != expected_a or counted_nv != expected_nv:
        print(f"  ❌ {r['Resolution']}: counted Y={counted_yes} N={counted_no} A={counted_abs} NV={counted_nv} "
              f"vs expected Y={expected_y} N={expected_n} A={expected_a} NV={expected_nv}")
        errors += 1

if errors == 0:
    print("  ✓ All 33 resolutions: vote counts match individual country votes exactly")
else:
    print(f"  ⚠️  {errors} resolution(s) with count mismatches")

# Sample output
print("\n── Sample: First 3 resolutions ──")
for row in data_rows[:3]:
    print(f"  {row[0]} | {row[1]} | {row[2][:60]}...")
