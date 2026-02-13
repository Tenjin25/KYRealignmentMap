"""
Validation and testing utilities for PDF extraction.
Helps diagnose issues and verify extraction quality.

Usage:
    python scripts/validate_extraction.py data/20241105__ky__general__county.csv
    python scripts/validate_extraction.py --compare data/file1.csv data/file2.csv
"""

import sys
from pathlib import Path
import pandas as pd
from typing import List, Tuple, Dict

try:
    from pdf_utils import KY_COUNTIES, logger
except ImportError:
    logger = None
    KY_COUNTIES = set()


def validate_openelections_format(csv_path: str) -> Tuple[bool, List[str]]:
    """
    Validate OpenElections CSV format and data quality.
    
    Returns:
        (is_valid, list of issues/warnings)
    """
    issues = []
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        return False, [f"File not found: {csv_path}"]
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return False, [f"Error reading CSV: {e}"]
    
    # Check for required columns
    required_columns = ['county', 'office', 'district', 'candidate', 'party', 'votes']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        issues.append(f"❌ Missing required columns: {', '.join(missing_cols)}")
        return False, issues
    
    # Basic statistics
    print(f"\n{'='*70}")
    print(f"Validation Report: {csv_path.name}")
    print(f"{'='*70}")
    print(f"\n📊 Basic Statistics:")
    print(f"   Total rows: {len(df):,}")
    print(f"   Unique counties: {df['county'].nunique()}")
    print(f"   Unique candidates: {df['candidate'].nunique()}")
    print(f"   Total votes: {df['votes'].sum():,}")
    
    # Check data quality
    print(f"\n🔍 Data Quality Checks:")
    
    # 1. Empty values
    empty_counties = df['county'].isna().sum() + (df['county'] == '').sum()
    empty_candidates = df['candidate'].isna().sum() + (df['candidate'] == '').sum()
    
    if empty_counties > 0:
        issues.append(f"⚠️  {empty_counties} rows with missing county")
        print(f"   ⚠️  {empty_counties} rows with missing county")
    else:
        print(f"   ✅ All rows have county")
    
    if empty_candidates > 0:
        issues.append(f"⚠️  {empty_candidates} rows with missing candidate")
        print(f"   ⚠️  {empty_candidates} rows with missing candidate")
    else:
        print(f"   ✅ All rows have candidate")
    
    # 2. Zero votes
    zero_votes = (df['votes'] == 0).sum()
    if zero_votes > len(df) * 0.3:
        issues.append(f"⚠️  {zero_votes:,} rows ({zero_votes/len(df)*100:.1f}%) with zero votes")
        print(f"   ⚠️  {zero_votes:,} rows with zero votes ({zero_votes/len(df)*100:.1f}%)")
    else:
        print(f"   ✅ Zero votes: {zero_votes:,} rows ({zero_votes/len(df)*100:.1f}%)")
    
    # 3. Negative votes
    negative_votes = (df['votes'] < 0).sum()
    if negative_votes > 0:
        issues.append(f"❌ {negative_votes} rows with negative votes")
        print(f"   ❌ {negative_votes} rows with negative votes")
    else:
        print(f"   ✅ No negative votes")
    
    # 4. County coverage
    unique_counties = df['county'].dropna().str.upper().unique()
    county_coverage = len(unique_counties)
    expected_counties = 120  # Kentucky has 120 counties
    
    if county_coverage < expected_counties * 0.5:
        issues.append(f"⚠️  Low county coverage: {county_coverage}/{expected_counties}")
        print(f"   ⚠️  Low county coverage: {county_coverage}/{expected_counties} counties")
    elif county_coverage < expected_counties:
        print(f"   ⚠️  Partial county coverage: {county_coverage}/{expected_counties} counties")
    else:
        print(f"   ✅ Good county coverage: {county_coverage} counties")
    
    # Check for unrecognized counties if we have the list
    if KY_COUNTIES:
        unrecognized = [c for c in unique_counties if c not in KY_COUNTIES and c != '']
        if unrecognized:
            print(f"   ⚠️  Unrecognized counties: {', '.join(unrecognized[:5])}")
            if len(unrecognized) > 5:
                print(f"      ... and {len(unrecognized) - 5} more")
    
    # 5. Party affiliation
    missing_party = (df['party'].isna() | (df['party'] == '')).sum()
    if missing_party > len(df) * 0.5:
        issues.append(f"⚠️  {missing_party:,} rows ({missing_party/len(df)*100:.1f}%) missing party")
        print(f"   ⚠️  {missing_party:,} rows missing party ({missing_party/len(df)*100:.1f}%)")
    else:
        print(f"   ✅ Party info: {len(df) - missing_party:,}/{len(df):,} rows ({(1-missing_party/len(df))*100:.1f}%)")
    
    # Show party breakdown
    if 'party' in df.columns:
        party_counts = df['party'].value_counts()
        if len(party_counts) > 0:
            print(f"\n   Party breakdown:")
            for party, count in party_counts.head(10).items():
                party_name = party if party else '(blank)'
                print(f"      {party_name}: {count:,} ({count/len(df)*100:.1f}%)")
    
    # 6. Office information
    missing_office = (df['office'].isna() | (df['office'] == '')).sum()
    if missing_office == len(df):
        print(f"   ⚠️  No office information (may need manual entry)")
    elif missing_office > 0:
        print(f"   ⚠️  {missing_office:,} rows missing office")
    else:
        print(f"   ✅ All rows have office")
        # Show office breakdown
        office_counts = df['office'].value_counts()
        print(f"\n   Office breakdown:")
        for office, count in office_counts.head(10).items():
            print(f"      {office}: {count:,}")
    
    # 7. Duplicates check
    dup_cols = ['county', 'candidate', 'party']
    if all(col in df.columns for col in dup_cols):
        duplicates = df.duplicated(subset=dup_cols, keep=False).sum()
        if duplicates > 0:
            issues.append(f"⚠️  {duplicates} potential duplicate rows")
            print(f"   ⚠️  {duplicates} potential duplicate rows")
        else:
            print(f"   ✅ No obvious duplicates")
    
    # Top candidates by votes
    print(f"\n🏆 Top 10 Candidates by Total Votes:")
    top_candidates = df.groupby(['candidate', 'party'])['votes'].sum().sort_values(ascending=False).head(10)
    for i, ((candidate, party), votes) in enumerate(top_candidates.items(), 1):
        party_str = f"({party})" if party else ""
        print(f"   {i:2d}. {candidate:30s} {party_str:6s} {votes:>10,} votes")
    
    # County with most votes
    print(f"\n🗺️  Top 10 Counties by Total Votes:")
    top_counties = df.groupby('county')['votes'].sum().sort_values(ascending=False).head(10)
    for i, (county, votes) in enumerate(top_counties.items(), 1):
        print(f"   {i:2d}. {county:20s} {votes:>10,} votes")
    
    # Final verdict
    print(f"\n{'='*70}")
    if len(issues) == 0:
        print("✅ Validation PASSED - No critical issues found")
        print("='*70}")
        return True, []
    else:
        print(f"⚠️  Validation completed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"   {issue}")
        print(f"{'='*70}")
        return len([i for i in issues if '❌' in i]) == 0, issues


def compare_csvs(csv1: str, csv2: str):
    """Compare two CSV files to spot differences."""
    print(f"\n{'='*70}")
    print(f"Comparing CSVs")
    print(f"{'='*70}")
    print(f"File 1: {csv1}")
    print(f"File 2: {csv2}")
    
    try:
        df1 = pd.read_csv(csv1)
        df2 = pd.read_csv(csv2)
    except Exception as e:
        print(f"❌ Error reading files: {e}")
        return
    
    print(f"\n📊 Row counts:")
    print(f"   File 1: {len(df1):,} rows")
    print(f"   File 2: {len(df2):,} rows")
    print(f"   Difference: {abs(len(df1) - len(df2)):,} rows")
    
    print(f"\n📊 Vote totals:")
    total1 = df1['votes'].sum()
    total2 = df2['votes'].sum()
    print(f"   File 1: {total1:,} votes")
    print(f"   File 2: {total2:,} votes")
    print(f"   Difference: {abs(total1 - total2):,} votes")
    
    print(f"\n📊 County coverage:")
    counties1 = set(df1['county'].dropna().unique())
    counties2 = set(df2['county'].dropna().unique())
    print(f"   File 1: {len(counties1)} counties")
    print(f"   File 2: {len(counties2)} counties")
    
    only_in_1 = counties1 - counties2
    only_in_2 = counties2 - counties1
    
    if only_in_1:
        print(f"   Only in File 1: {', '.join(sorted(only_in_1))}")
    if only_in_2:
        print(f"   Only in File 2: {', '.join(sorted(only_in_2))}")
    
    print(f"\n📊 Candidate coverage:")
    candidates1 = set(df1['candidate'].dropna().unique())
    candidates2 = set(df2['candidate'].dropna().unique())
    print(f"   File 1: {len(candidates1)} candidates")
    print(f"   File 2: {len(candidates2)} candidates")
    
    only_in_1 = candidates1 - candidates2
    only_in_2 = candidates2 - candidates1
    
    if only_in_1:
        print(f"   Only in File 1: {', '.join(sorted(list(only_in_1))[:10])}")
    if only_in_2:
        print(f"   Only in File 2: {', '.join(sorted(list(only_in_2))[:10])}")
    
    print(f"\n{'='*70}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_file', nargs='?', help='CSV file to validate')
    parser.add_argument('--compare', nargs=2, metavar=('FILE1', 'FILE2'),
                       help='Compare two CSV files')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_csvs(args.compare[0], args.compare[1])
    elif args.csv_file:
        is_valid, issues = validate_openelections_format(args.csv_file)
        sys.exit(0 if is_valid else 1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
