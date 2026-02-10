#!/usr/bin/env python3
"""
Topic Votes Data Validation Script
===================================
Validates: topic_votes_yearly (1).csv
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
    data_path = Path(__file__).parent.parent / "data" / "topic_votes_yearly.csv"
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
    dup_count = df.duplicated(subset=['Year', 'Country', 'TopicTag']).sum()
    print(f"\n🔍 Duplicate Year-Country-Topic combinations: {dup_count}")
    if dup_count > 0:
        dups = df[df.duplicated(subset=['Year', 'Country', 'TopicTag'], keep=False)]
        print("   ❌ Duplicates found!")
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
    
    print(f"\n🌍 Unique Countries: {df['Country'].nunique()}")
    
    # =========================================================================
    # 3. TOPIC TAG ANALYSIS
    # =========================================================================
    separator("3. TOPIC TAG ANALYSIS")
    
    print(f"\n🏷️ Unique Topic Tags: {df['TopicTag'].nunique()}")
    print("\n📋 All Topic Tags:")
    topics = df['TopicTag'].value_counts()
    for topic, count in topics.items():
        print(f"   • {topic}: {count:,} records ({count/len(df)*100:.1f}%)")
    
    # Check for inconsistent topic names
    print("\n🔍 Checking for potential duplicates/typos in topic names:")
    topic_list = df['TopicTag'].unique()
    similar_topics = []
    for i, t1 in enumerate(topic_list):
        for t2 in topic_list[i+1:]:
            # Check if topics differ only in whitespace/case
            if t1.lower().strip() == t2.lower().strip() and t1 != t2:
                similar_topics.append((t1, t2))
    
    if similar_topics:
        print("   ⚠️ Potentially duplicate topics:")
        for t1, t2 in similar_topics:
            print(f"      '{t1}' vs '{t2}'")
    else:
        print("   ✓ No obvious duplicate topic names")
    
    # =========================================================================
    # 4. SUMMARY STATISTICS
    # =========================================================================
    separator("4. SUMMARY STATISTICS")
    
    vote_cols = ['YesVotes_Topic', 'NoVotes_Topic', 'AbstainVotes_Topic', 'TotalVotes_Topic']
    
    print("\n📊 Vote Column Statistics:")
    print(df[vote_cols].describe().round(2).to_string())
    
    # =========================================================================
    # 5. VOTE COUNT VALIDATION
    # =========================================================================
    separator("5. VOTE COUNT VALIDATION")
    
    print("\n🗳️ Vote Counts Check:")
    for col in vote_cols:
        if col in df.columns:
            neg_count = (df[col] < 0).sum()
            null_count = df[col].isnull().sum()
            status = "✓" if neg_count == 0 else "❌"
            print(f"   {status} {col}: min={df[col].min()}, max={df[col].max()}, negatives={neg_count}, nulls={null_count}")
    
    # Check Yes + No + Abstain = Total
    print("\n🔢 Yes + No + Abstain = Total check:")
    df['calc_total'] = df['YesVotes_Topic'] + df['NoVotes_Topic'] + df['AbstainVotes_Topic']
    mismatches = (df['calc_total'] != df['TotalVotes_Topic']).sum()
    if mismatches == 0:
        print(f"   ✓ All {len(df):,} rows match")
    else:
        print(f"   ❌ {mismatches} rows have mismatched totals")
        bad_rows = df[df['calc_total'] != df['TotalVotes_Topic']]
        print(bad_rows[['Year', 'Country', 'TopicTag'] + vote_cols + ['calc_total']].head(10))
    df.drop('calc_total', axis=1, inplace=True)
    
    # =========================================================================
    # 6. VOTES BY TOPIC DISTRIBUTION
    # =========================================================================
    separator("6. VOTES BY TOPIC DISTRIBUTION")
    
    print("\n📊 Average Votes per Topic:")
    topic_stats = df.groupby('TopicTag').agg({
        'YesVotes_Topic': 'mean',
        'NoVotes_Topic': 'mean',
        'AbstainVotes_Topic': 'mean',
        'TotalVotes_Topic': ['mean', 'sum']
    }).round(2)
    topic_stats.columns = ['Avg Yes', 'Avg No', 'Avg Abstain', 'Avg Total', 'Sum Total']
    topic_stats = topic_stats.sort_values('Sum Total', ascending=False)
    print(topic_stats.to_string())
    
    # =========================================================================
    # 7. OUTLIER ANALYSIS
    # =========================================================================
    separator("7. OUTLIER ANALYSIS")
    
    print("\n🔍 Extreme vote counts by topic:")
    for topic in df['TopicTag'].unique()[:5]:  # Top 5 topics
        topic_df = df[df['TopicTag'] == topic]
        max_total = topic_df['TotalVotes_Topic'].max()
        max_row = topic_df[topic_df['TotalVotes_Topic'] == max_total].iloc[0]
        print(f"\n   {topic}:")
        print(f"      Max votes: {max_total} ({max_row['Country']}, {max_row['Year']})")
    
    # Countries with extreme voting patterns
    print("\n🔍 Countries with extreme total votes (top 10):")
    country_totals = df.groupby('Country')['TotalVotes_Topic'].sum().sort_values(ascending=False)
    print(country_totals.head(10).to_string())
    
    # =========================================================================
    # 8. YEARLY TRENDS
    # =========================================================================
    separator("8. YEARLY TRENDS")
    
    print("\n📅 Votes by Year (sample):")
    yearly = df.groupby('Year').agg({
        'YesVotes_Topic': 'sum',
        'NoVotes_Topic': 'sum',
        'AbstainVotes_Topic': 'sum',
        'TotalVotes_Topic': 'sum',
        'Country': 'nunique',
        'TopicTag': 'nunique'
    })
    yearly.columns = ['Total Yes', 'Total No', 'Total Abstain', 'Total Votes', 'Countries', 'Topics']
    print(yearly.head(10).to_string())
    print("   ...")
    print(yearly.tail(5).to_string())
    
    # =========================================================================
    # 9. CROSS-VALIDATION PREP (for cross-file check)
    # =========================================================================
    separator("9. CROSS-VALIDATION DATA")
    
    print("\n📊 Country-Year Vote Totals (for cross-check with annual_scores):")
    country_year_totals = df.groupby(['Country', 'Year'])['TotalVotes_Topic'].sum().reset_index()
    country_year_totals.columns = ['Country', 'Year', 'TopicSum']
    print(f"   Unique Country-Year combinations: {len(country_year_totals):,}")
    
    # =========================================================================
    # 10. RANDOM SAMPLES FOR VERIFICATION
    # =========================================================================
    separator("10. RANDOM SAMPLES FOR VERIFICATION")
    
    print("\n🎲 5 Random samples for web verification:")
    sample = df.sample(n=min(5, len(df)), random_state=42)
    print(sample.to_string())
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    separator("VALIDATION SUMMARY")
    
    issues = []
    if dup_count > 0:
        issues.append(f"Found {dup_count} duplicate Year-Country-Topic rows")
    if missing_years:
        issues.append(f"Missing years: {missing_years}")
    if missing.sum() > 0:
        issues.append(f"Total missing values: {missing.sum()}")
    if mismatches > 0:
        issues.append(f"{mismatches} rows with vote count mismatches")
    
    warnings = []
    if similar_topics:
        warnings.append(f"Potential duplicate topic names found: {len(similar_topics)}")
    
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
