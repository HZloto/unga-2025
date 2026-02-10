#!/usr/bin/env python3
"""
Annual Scores Data Validation Script
=====================================
Validates: annual_scores (1).csv
Performs: Summary statistics, outlier analysis, consistency checks
"""

import pandas as pd
import numpy as np
from pathlib import Path

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def main():
    # Load data
    data_path = Path(__file__).parent.parent / "data" / "annual_scores.csv"
    print(f"Loading: {data_path}")
    df = pd.read_csv(data_path)
    
    # =========================================================================
    # 1. SCHEMA & STRUCTURE
    # =========================================================================
    separator("1. SCHEMA & STRUCTURE")
    
    print(f"\n📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"\n📋 Columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns):
        print(f"   {i+1}. {col} ({df[col].dtype})")
    
    # Check for duplicates
    dup_count = df.duplicated(subset=['Country name', 'Year']).sum()
    print(f"\n🔍 Duplicate Country-Year combinations: {dup_count}")
    if dup_count > 0:
        dups = df[df.duplicated(subset=['Country name', 'Year'], keep=False)]
        print("   Sample duplicates:")
        print(dups.head(10))
    
    # =========================================================================
    # 2. COMPLETENESS ANALYSIS
    # =========================================================================
    separator("2. COMPLETENESS ANALYSIS")
    
    print("\n📉 Missing Values Per Column:")
    missing = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    for col in df.columns:
        if missing[col] > 0:
            print(f"   ❌ {col}: {missing[col]:,} ({missing_pct[col]}%)")
        else:
            print(f"   ✓ {col}: 0")
    
    print(f"\n📅 Year Range: {df['Year'].min()} - {df['Year'].max()}")
    print(f"   Unique years: {df['Year'].nunique()}")
    
    # Check for missing years
    all_years = set(range(df['Year'].min(), df['Year'].max() + 1))
    present_years = set(df['Year'].unique())
    missing_years = all_years - present_years
    if missing_years:
        print(f"   ⚠️ Missing years: {sorted(missing_years)}")
    else:
        print("   ✓ No gaps in year sequence")
    
    print(f"\n🌍 Unique Countries: {df['Country name'].nunique()}")
    
    # Countries with gaps
    print("\n🔍 Countries with year gaps (sample):")
    countries_with_gaps = []
    for country in df['Country name'].unique():
        country_years = set(df[df['Country name'] == country]['Year'])
        expected = set(range(min(country_years), max(country_years) + 1))
        gaps = expected - country_years
        if gaps:
            countries_with_gaps.append((country, len(gaps), sorted(gaps)[:5]))
    
    if countries_with_gaps:
        for c, gap_count, sample in countries_with_gaps[:10]:
            print(f"   {c}: {gap_count} gaps (e.g., {sample})")
        print(f"   ... and {len(countries_with_gaps) - 10} more countries with gaps" if len(countries_with_gaps) > 10 else "")
    else:
        print("   ✓ No countries with year gaps")
    
    # =========================================================================
    # 3. SUMMARY STATISTICS
    # =========================================================================
    separator("3. SUMMARY STATISTICS")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    print(f"\n📊 Numeric Columns Statistics:")
    print(df[numeric_cols].describe().round(2).to_string())
    
    # Pillar score ranges
    separator("4. SCORE RANGE VALIDATION")
    pillar_cols = ['Pillar 1 Score', 'Pillar 2 Score', 'Pillar 3 Score', 'Total Index Average']
    norm_cols = ['Total Index Normalized', 'Pillar 1 Normalized', 'Pillar 2 Normalized', 'Pillar 3 Normalized']
    
    print("\n📏 Pillar Scores Range Check (expected 0-100):")
    for col in pillar_cols:
        if col in df.columns:
            min_val, max_val = df[col].min(), df[col].max()
            status = "✓" if 0 <= min_val and max_val <= 100 else "❌"
            print(f"   {status} {col}: [{min_val:.2f}, {max_val:.2f}]")
    
    print("\n📏 Normalized Scores Range Check (expected 0-100):")
    for col in norm_cols:
        if col in df.columns:
            min_val, max_val = df[col].min(), df[col].max()
            status = "✓" if 0 <= min_val and max_val <= 100 else "❌"
            print(f"   {status} {col}: [{min_val:.2f}, {max_val:.2f}]")
    
    # =========================================================================
    # 5. VOTE COUNT VALIDATION
    # =========================================================================
    separator("5. VOTE COUNT VALIDATION")
    
    vote_cols = ['Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']
    
    print("\n🗳️ Vote Counts Check:")
    for col in vote_cols:
        if col in df.columns:
            neg_count = (df[col] < 0).sum()
            null_count = df[col].isnull().sum()
            status = "✓" if neg_count == 0 else "❌"
            print(f"   {status} {col}: min={df[col].min()}, max={df[col].max()}, negatives={neg_count}, nulls={null_count}")
    
    # Check Yes + No + Abstain = Total
    if all(c in df.columns for c in vote_cols):
        df['calc_total'] = df['Yes Votes'] + df['No Votes'] + df['Abstain Votes']
        mismatches = (df['calc_total'] != df['Total Votes in Year']).sum()
        print(f"\n🔢 Yes + No + Abstain = Total check:")
        if mismatches == 0:
            print(f"   ✓ All {len(df):,} rows match")
        else:
            print(f"   ❌ {mismatches} rows have mismatched totals")
            bad_rows = df[df['calc_total'] != df['Total Votes in Year']]
            print(bad_rows[['Country name', 'Year'] + vote_cols + ['calc_total']].head(5))
        df.drop('calc_total', axis=1, inplace=True)
    
    # =========================================================================
    # 6. OUTLIER ANALYSIS
    # =========================================================================
    separator("6. OUTLIER ANALYSIS (3σ)")
    
    print("\n🔍 Values outside 3 standard deviations:")
    for col in numeric_cols:
        if col not in ['Year']:
            mean = df[col].mean()
            std = df[col].std()
            lower = mean - 3*std
            upper = mean + 3*std
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            if len(outliers) > 0:
                print(f"\n   {col}: {len(outliers)} outliers")
                print(f"      Mean: {mean:.2f}, Std: {std:.2f}, Bounds: [{lower:.2f}, {upper:.2f}]")
                if len(outliers) <= 5:
                    for _, row in outliers.iterrows():
                        print(f"      - {row['Country name']} ({row['Year']}): {row[col]:.2f}")
    
    # =========================================================================
    # 7. RANK CONSISTENCY
    # =========================================================================
    separator("7. RANK CONSISTENCY CHECK")
    
    print("\n📊 Rank columns validation:")
    rank_cols = ['Overall Rank', 'Pillar 1 Rank', 'Pillar 2 Rank', 'Pillar 3 Rank']
    for col in rank_cols:
        if col in df.columns:
            min_val = df[col].min()
            max_val = df[col].max()
            non_int = (~df[col].dropna().apply(lambda x: x == int(x))).sum()
            status = "✓" if min_val >= 1 and non_int == 0 else "⚠️"
            print(f"   {status} {col}: range [{min_val}, {max_val}], non-integers: {non_int}")
    
    # =========================================================================
    # 8. RANDOM SAMPLE FOR MANUAL VERIFICATION
    # =========================================================================
    separator("8. RANDOM SAMPLES FOR VERIFICATION")
    
    print("\n🎲 5 Random samples for web verification:")
    sample = df.sample(n=min(5, len(df)), random_state=42)
    print(sample[['Country name', 'Year', 'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']].to_string())
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    separator("VALIDATION SUMMARY")
    
    issues = []
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate Country-Year rows")
    if missing_years:
        issues.append(f"Missing years in dataset: {missing_years}")
    if missing.sum() > 0:
        issues.append(f"Total missing values: {missing.sum()}")
    
    if not issues:
        print("\n✅ All validation checks passed!")
    else:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    print("\n" + "="*60)
    print("  END OF VALIDATION REPORT")
    print("="*60)

if __name__ == "__main__":
    main()
