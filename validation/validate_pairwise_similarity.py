#!/usr/bin/env python3
"""
Pairwise Similarity Data Validation Script
===========================================
Validates: pairwise_similarity_yearly (1).csv
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
    data_path = Path(__file__).parent.parent / "data" / "pairwise_similarity_yearly.csv"
    print(f"Loading: {data_path}")
    print("(This may take a moment due to large file size...)")
    df = pd.read_csv(data_path)
    
    # =========================================================================
    # 1. SCHEMA & STRUCTURE
    # =========================================================================
    separator("1. SCHEMA & STRUCTURE")
    
    print(f"\n📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"\n📋 Columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns):
        print(f"   {i+1}. {col} ({df[col].dtype})")
    
    # ISO3 code validation
    print("\n🔍 ISO3 Code Validation:")
    for col in ['Country1_ISO3', 'Country2_ISO3']:
        if col in df.columns:
            non_3char = df[~df[col].str.len().eq(3)][col].nunique()
            non_alpha = df[~df[col].str.match(r'^[A-Z]{3}$', na=False)][col].unique()
            print(f"   {col}:")
            print(f"      Unique codes: {df[col].nunique()}")
            if len(non_alpha) > 0:
                if len(non_alpha) <= 10:
                    print(f"      ⚠️ Non-standard codes: {list(non_alpha)}")
                else:
                    print(f"      ⚠️ {len(non_alpha)} non-standard codes found")
            else:
                print(f"      ✓ All codes match [A-Z]{{3}} pattern")
    
    # Check for duplicates
    dup_count = df.duplicated(subset=['Year', 'Country1_ISO3', 'Country2_ISO3']).sum()
    print(f"\n🔍 Duplicate Year-Country1-Country2 combinations: {dup_count}")
    if dup_count > 0:
        print("   ❌ Duplicates found!")
    
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
    
    # Check symmetry of pairs
    print("\n🔄 Pair Symmetry Check (sample 1000 random pairs):")
    sample_size = min(1000, len(df))
    sample = df.sample(n=sample_size, random_state=42)
    symmetric_count = 0
    asymmetric_pairs = []
    
    for _, row in sample.iterrows():
        reverse = df[(df['Year'] == row['Year']) & 
                     (df['Country1_ISO3'] == row['Country2_ISO3']) & 
                     (df['Country2_ISO3'] == row['Country1_ISO3'])]
        if len(reverse) > 0:
            symmetric_count += 1
        else:
            if len(asymmetric_pairs) < 5:
                asymmetric_pairs.append((row['Year'], row['Country1_ISO3'], row['Country2_ISO3']))
    
    print(f"   Symmetric pairs found: {symmetric_count}/{sample_size}")
    if asymmetric_pairs:
        print(f"   Sample asymmetric: {asymmetric_pairs[:3]}")
    
    # =========================================================================
    # 3. SUMMARY STATISTICS
    # =========================================================================
    separator("3. SUMMARY STATISTICS")
    
    print("\n📊 Cosine Similarity Statistics:")
    print(f"   Count:  {df['CosineSimilarity'].count():,}")
    print(f"   Mean:   {df['CosineSimilarity'].mean():.4f}")
    print(f"   Std:    {df['CosineSimilarity'].std():.4f}")
    print(f"   Min:    {df['CosineSimilarity'].min():.4f}")
    print(f"   25%:    {df['CosineSimilarity'].quantile(0.25):.4f}")
    print(f"   50%:    {df['CosineSimilarity'].quantile(0.50):.4f}")
    print(f"   75%:    {df['CosineSimilarity'].quantile(0.75):.4f}")
    print(f"   Max:    {df['CosineSimilarity'].max():.4f}")
    
    # =========================================================================
    # 4. COSINE SIMILARITY RANGE VALIDATION
    # =========================================================================
    separator("4. COSINE SIMILARITY RANGE CHECK")
    
    print("\n📏 Expected Range: [-1, 1]")
    min_val = df['CosineSimilarity'].min()
    max_val = df['CosineSimilarity'].max()
    
    out_of_range = df[(df['CosineSimilarity'] < -1) | (df['CosineSimilarity'] > 1)]
    if len(out_of_range) == 0:
        print(f"   ✓ All values in range: [{min_val:.6f}, {max_val:.6f}]")
    else:
        print(f"   ❌ {len(out_of_range):,} values outside [-1, 1] range!")
        print(out_of_range.head(10))
    
    # Zero/near-zero similarity analysis
    zero_sim = (df['CosineSimilarity'] == 0).sum()
    near_zero = ((df['CosineSimilarity'] > -0.001) & (df['CosineSimilarity'] < 0.001)).sum()
    print(f"\n   Zero similarity pairs: {zero_sim:,} ({zero_sim/len(df)*100:.2f}%)")
    print(f"   Near-zero similarity: {near_zero:,} ({near_zero/len(df)*100:.2f}%)")
    
    # =========================================================================
    # 5. EXTREME VALUE ANALYSIS
    # =========================================================================
    separator("5. EXTREME VALUE ANALYSIS")
    
    # Perfect similarity
    perfect_sim = df[df['CosineSimilarity'] == 1.0]
    print(f"\n🎯 Perfect Similarity (1.0): {len(perfect_sim):,} pairs")
    if len(perfect_sim) > 0 and len(perfect_sim) <= 10:
        print(perfect_sim.to_string())
    elif len(perfect_sim) > 10:
        print(f"   Sample:")
        print(perfect_sim.head(5).to_string())
    
    # Perfect dissimilarity
    perfect_dissim = df[df['CosineSimilarity'] == -1.0]
    print(f"\n🎯 Perfect Dissimilarity (-1.0): {len(perfect_dissim):,} pairs")
    if len(perfect_dissim) > 0 and len(perfect_dissim) <= 10:
        print(perfect_dissim.to_string())
    
    # Top similar pairs (non-identical)
    print("\n📈 Top 10 Most Similar Pairs (excluding 1.0):")
    top_sim = df[df['CosineSimilarity'] < 1.0].nlargest(10, 'CosineSimilarity')
    print(top_sim.to_string())
    
    # Most dissimilar pairs
    print("\n📉 Top 10 Most Dissimilar Pairs:")
    top_dissim = df.nsmallest(10, 'CosineSimilarity')
    print(top_dissim.to_string())
    
    # =========================================================================
    # 6. YEARLY DISTRIBUTION
    # =========================================================================
    separator("6. YEARLY DISTRIBUTION")
    
    print("\n📅 Statistics by Year (sample):")
    yearly_stats = df.groupby('Year')['CosineSimilarity'].agg(['count', 'mean', 'std', 'min', 'max'])
    yearly_stats.columns = ['Count', 'Mean', 'Std', 'Min', 'Max']
    print(yearly_stats.head(10).round(4).to_string())
    print("   ...")
    print(yearly_stats.tail(5).round(4).to_string())
    
    # Pairs per year
    print("\n📊 Country Pairs per Year:")
    pairs_per_year = df.groupby('Year').size()
    print(f"   Min pairs: {pairs_per_year.min():,} (Year {pairs_per_year.idxmin()})")
    print(f"   Max pairs: {pairs_per_year.max():,} (Year {pairs_per_year.idxmax()})")
    
    # =========================================================================
    # 7. COUNTRY COVERAGE
    # =========================================================================
    separator("7. COUNTRY COVERAGE")
    
    all_countries = set(df['Country1_ISO3'].unique()) | set(df['Country2_ISO3'].unique())
    print(f"\n🌍 Total Unique Countries: {len(all_countries)}")
    print(f"   Sample countries: {sorted(list(all_countries))[:20]}...")
    
    # =========================================================================
    # 8. RANDOM SAMPLES FOR VERIFICATION
    # =========================================================================
    separator("8. RANDOM SAMPLES FOR VERIFICATION")
    
    print("\n🎲 5 Random high-similarity pairs for verification:")
    high_sim = df[df['CosineSimilarity'] > 0.9].sample(n=min(5, len(df[df['CosineSimilarity'] > 0.9])), random_state=42)
    print(high_sim.to_string())
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    separator("VALIDATION SUMMARY")
    
    issues = []
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate rows")
    if missing_years:
        issues.append(f"Missing years: {missing_years}")
    if missing.sum() > 0:
        issues.append(f"Total missing values: {missing.sum()}")
    if len(out_of_range) > 0:
        issues.append(f"{len(out_of_range)} values outside [-1, 1] range")
    
    warnings = []
    if zero_sim / len(df) > 0.5:
        warnings.append(f"High proportion ({zero_sim/len(df)*100:.1f}%) of zero similarities")
    
    if not issues:
        print("\n✅ All critical validation checks passed!")
    else:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print("\n⚠️ Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("\n" + "="*60)
    print("  END OF VALIDATION REPORT")
    print("="*60)

if __name__ == "__main__":
    main()
