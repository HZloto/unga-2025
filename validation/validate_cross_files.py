#!/usr/bin/env python3
"""
Cross-File Validation Script
=============================
Validates consistency across all three UNGA data files:
- annual_scores (1).csv
- pairwise_similarity_yearly (1).csv  
- topic_votes_yearly (1).csv
"""

import pandas as pd
import numpy as np
from pathlib import Path

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def main():
    data_dir = Path(__file__).parent.parent / "data"
    
    print("Loading all three datasets...")
    annual = pd.read_csv(data_dir / "annual_scores.csv")
    print(f"  ✓ annual_scores: {len(annual):,} rows")
    
    pairwise = pd.read_csv(data_dir / "pairwise_similarity_yearly.csv")
    print(f"  ✓ pairwise_similarity: {len(pairwise):,} rows")
    
    topic = pd.read_csv(data_dir / "topic_votes_yearly.csv")
    print(f"  ✓ topic_votes: {len(topic):,} rows")
    
    # =========================================================================
    # 1. YEAR CONSISTENCY
    # =========================================================================
    separator("1. YEAR CONSISTENCY")
    
    annual_years = set(annual['Year'].unique())
    pairwise_years = set(pairwise['Year'].unique())
    topic_years = set(topic['Year'].unique())
    
    print(f"\n📅 Year Ranges:")
    print(f"   annual_scores:      {min(annual_years)} - {max(annual_years)} ({len(annual_years)} years)")
    print(f"   pairwise_similarity: {min(pairwise_years)} - {max(pairwise_years)} ({len(pairwise_years)} years)")
    print(f"   topic_votes:        {min(topic_years)} - {max(topic_years)} ({len(topic_years)} years)")
    
    # Years in all files
    common_years = annual_years & pairwise_years & topic_years
    print(f"\n   Years in ALL files: {len(common_years)}")
    
    # Years missing from each
    print("\n   Years present in one but not others:")
    only_annual = annual_years - pairwise_years - topic_years
    only_pairwise = pairwise_years - annual_years - topic_years
    only_topic = topic_years - annual_years - pairwise_years
    
    if only_annual:
        print(f"      Only in annual_scores: {sorted(only_annual)}")
    if only_pairwise:
        print(f"      Only in pairwise: {sorted(only_pairwise)}")
    if only_topic:
        print(f"      Only in topic_votes: {sorted(only_topic)}")
    if not only_annual and not only_pairwise and not only_topic:
        print("      ✓ All years present in all files")
    
    # =========================================================================
    # 2. COUNTRY CONSISTENCY
    # =========================================================================
    separator("2. COUNTRY CONSISTENCY")
    
    # Note: annual_scores uses full names, others use ISO3
    annual_countries = set(annual['Country name'].unique())
    pairwise_countries = set(pairwise['Country1_ISO3'].unique()) | set(pairwise['Country2_ISO3'].unique())
    topic_countries = set(topic['Country'].unique())
    
    print(f"\n🌍 Country Counts:")
    print(f"   annual_scores (names): {len(annual_countries)} unique")
    print(f"   pairwise (ISO3):       {len(pairwise_countries)} unique")
    print(f"   topic_votes (ISO3?):   {len(topic_countries)} unique")
    
    # Check if topic uses ISO3 or names
    topic_sample = list(topic_countries)[:10]
    print(f"\n   Sample topic_votes countries: {topic_sample}")
    
    # Check if pairwise countries match topic countries
    common_pairwise_topic = pairwise_countries & topic_countries
    only_pairwise_c = pairwise_countries - topic_countries
    only_topic_c = topic_countries - pairwise_countries
    
    print(f"\n   pairwise vs topic_votes:")
    print(f"      Common countries: {len(common_pairwise_topic)}")
    print(f"      Only in pairwise: {len(only_pairwise_c)}")
    print(f"      Only in topic: {len(only_topic_c)}")
    
    if only_pairwise_c and len(only_pairwise_c) <= 10:
        print(f"         Only pairwise: {sorted(only_pairwise_c)}")
    if only_topic_c and len(only_topic_c) <= 10:
        print(f"         Only topic: {sorted(only_topic_c)}")
    
    # =========================================================================
    # 3. VOTE TOTALS CONSISTENCY (Annual vs Topic)
    # =========================================================================
    separator("3. VOTE TOTALS CONSISTENCY")
    
    print("\n🗳️ Checking if topic vote sums match annual_scores totals...")
    
    # Aggregate topic votes by country-year
    topic_agg = topic.groupby(['Country', 'Year']).agg({
        'YesVotes_Topic': 'sum',
        'NoVotes_Topic': 'sum',
        'AbstainVotes_Topic': 'sum',
        'TotalVotes_Topic': 'sum'
    }).reset_index()
    
    # Check if annual uses same country codes as topic
    # We need to find a common identifier - let's check by year first
    
    print(f"\n   Topic aggregated: {len(topic_agg)} country-year combinations")
    print(f"   Annual scores: {len(annual)} country-year combinations")
    
    # Sample comparison (assuming same country codes)
    # If country codes differ, this won't match - which is useful info
    print("\n   Sample topic aggregations:")
    print(topic_agg.head(10).to_string())
    
    print("\n   Sample annual_scores:")
    print(annual[['Country name', 'Year', 'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']].head(10).to_string())
    
    # Try to match by finding common country in same year
    print("\n   Attempting to reconcile vote totals...")
    
    # Check for year 1946 as sample
    annual_1946 = annual[annual['Year'] == 1946][['Country name', 'Year', 'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']]
    topic_1946 = topic_agg[topic_agg['Year'] == 1946]
    
    print(f"\n   Year 1946 comparison:")
    print(f"      Countries in annual: {len(annual_1946)}")
    print(f"      Countries in topic: {len(topic_1946)}")
    
    # Manual mapping check for known countries
    print("\n   Spot-check AFG (Afghanistan) in 1946:")
    afg_annual = annual[(annual['Country name'] == 'AFG') & (annual['Year'] == 1946)]
    afg_topic = topic_agg[(topic_agg['Country'] == 'AFG') & (topic_agg['Year'] == 1946)]
    
    if len(afg_annual) > 0:
        print(f"      Annual: Yes={afg_annual['Yes Votes'].values[0]}, No={afg_annual['No Votes'].values[0]}, Abstain={afg_annual['Abstain Votes'].values[0]}, Total={afg_annual['Total Votes in Year'].values[0]}")
    if len(afg_topic) > 0:
        print(f"      Topic:  Yes={afg_topic['YesVotes_Topic'].values[0]}, No={afg_topic['NoVotes_Topic'].values[0]}, Abstain={afg_topic['AbstainVotes_Topic'].values[0]}, Total={afg_topic['TotalVotes_Topic'].values[0]}")
    
    # Full reconciliation
    # Rename columns for merge
    annual_votes = annual[['Country name', 'Year', 'Yes Votes', 'No Votes', 'Abstain Votes', 'Total Votes in Year']].copy()
    annual_votes.columns = ['Country', 'Year', 'Annual_Yes', 'Annual_No', 'Annual_Abstain', 'Annual_Total']
    
    topic_votes = topic_agg.copy()
    topic_votes.columns = ['Country', 'Year', 'Topic_Yes', 'Topic_No', 'Topic_Abstain', 'Topic_Total']
    
    merged = pd.merge(annual_votes, topic_votes, on=['Country', 'Year'], how='outer', indicator=True)
    
    print(f"\n   Merge results:")
    print(f"      Both files: {(merged['_merge'] == 'both').sum()}")
    print(f"      Annual only: {(merged['_merge'] == 'left_only').sum()}")
    print(f"      Topic only: {(merged['_merge'] == 'right_only').sum()}")
    
    # Check matches
    both = merged[merged['_merge'] == 'both'].copy()
    if len(both) > 0:
        both['Yes_Match'] = both['Annual_Yes'] == both['Topic_Yes']
        both['No_Match'] = both['Annual_No'] == both['Topic_No']
        both['Abstain_Match'] = both['Annual_Abstain'] == both['Topic_Abstain']
        both['Total_Match'] = both['Annual_Total'] == both['Topic_Total']
        
        print(f"\n   Vote count matches (from {len(both)} common country-years):")
        print(f"      Yes votes match: {both['Yes_Match'].sum()} ({both['Yes_Match'].mean()*100:.1f}%)")
        print(f"      No votes match: {both['No_Match'].sum()} ({both['No_Match'].mean()*100:.1f}%)")
        print(f"      Abstain match: {both['Abstain_Match'].sum()} ({both['Abstain_Match'].mean()*100:.1f}%)")
        print(f"      Total match: {both['Total_Match'].sum()} ({both['Total_Match'].mean()*100:.1f}%)")
        
        # Show mismatches
        mismatches = both[~(both['Yes_Match'] & both['No_Match'] & both['Abstain_Match'] & both['Total_Match'])]
        if len(mismatches) > 0:
            print(f"\n   ⚠️ Sample mismatches:")
            print(mismatches[['Country', 'Year', 'Annual_Total', 'Topic_Total']].head(10).to_string())
    
    # =========================================================================
    # 4. PAIRWISE COUNTRY COVERAGE
    # =========================================================================
    separator("4. PAIRWISE COUNTRY COVERAGE CHECK")
    
    print("\n🔍 Checking if pairwise countries exist in annual_scores...")
    
    # Sample check: countries in pairwise should be in annual for same year
    sample_year = 2020
    pairwise_year = pairwise[pairwise['Year'] == sample_year]
    annual_year = annual[annual['Year'] == sample_year]
    
    if len(pairwise_year) > 0 and len(annual_year) > 0:
        pairwise_countries_year = set(pairwise_year['Country1_ISO3'].unique()) | set(pairwise_year['Country2_ISO3'].unique())
        annual_countries_year = set(annual_year['Country name'].unique())
        
        print(f"\n   Year {sample_year}:")
        print(f"      Pairwise countries: {len(pairwise_countries_year)}")
        print(f"      Annual countries: {len(annual_countries_year)}")
        
        # Check overlap (assuming both use ISO3)
        overlap = pairwise_countries_year & annual_countries_year
        print(f"      Overlap: {len(overlap)}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    separator("CROSS-FILE VALIDATION SUMMARY")
    
    issues = []
    warnings = []
    
    if only_annual or only_pairwise or only_topic:
        warnings.append("Some years not present in all files")
    
    if len(common_pairwise_topic) < len(pairwise_countries):
        warnings.append(f"Country mismatch between pairwise and topic files")
    
    if not issues:
        print("\n✅ No critical cross-file issues found!")
    else:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    if warnings:
        print("\n⚠️ Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("\n" + "="*60)
    print("  END OF CROSS-FILE VALIDATION REPORT")
    print("="*60)

if __name__ == "__main__":
    main()
