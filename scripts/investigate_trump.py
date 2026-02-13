"""
Check what's causing the high vote totals - investigate Trump 2024 in detail
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive\Documents\Course_Materials\CPT-236\Side_Projects\KYRealignments\data")
dedup_file = data_dir / "KY_ELECTIONS_DEDUP.csv"

df = pd.read_csv(dedup_file)

print("=" * 80)
print("INVESTIGATING HIGH VOTE COUNTS")
print("=" * 80)

# Check Trump 2024 specifically
trump_2024 = df[(df['candidate'].str.contains('Trump', case=False, na=False)) & (df['year'] == 2024)]

print(f"\nTrump 2024 records: {len(trump_2024)}")
print(f"Total Trump 2024 votes: {trump_2024['votes'].sum():,}")

print("\nTrump 2024 by office (if column exists):")
if 'office' in df.columns:
    trump_2024_by_office = trump_2024.groupby('office')['votes'].sum()
    for office, votes in trump_2024_by_office.items():
        print(f"  {office}: {votes:>12,} ({len(trump_2024[trump_2024['office']==office])} records)")
else:
    print("  (no office column)")

print("\nCheck all columns for Trump 2024:")
print(trump_2024.columns.tolist())

print("\nSample Trump 2024 records (first 10):")
print(trump_2024[['county', 'candidate', 'votes', 'year']].head(10).to_string())

print("\n" + "=" * 80)
print("CHECK FOR DATA STRUCTURE ISSUES")
print("=" * 80)

# What offices do we have?
if 'office' in df.columns:
    print(f"\nUnique offices: {df['office'].nunique()}")
    print(df['office'].value_counts())

# Check if Trump appears under different names
print(f"\nAll Trump-like entries:")
trump_all = df[df['candidate'].str.contains('Trump', case=False, na=False)]
print(trump_all['candidate'].unique())

print(f"\nTrump 2024 total by county (top 10):")
trump_2024_by_county = trump_2024.groupby('county')['votes'].sum().sort_values(ascending=False)
for county, votes in trump_2024_by_county.head(10).items():
    print(f"  {county:15} {votes:>12,}")

# Calculate expected for comparison
print("\n" + "=" * 80)
print("EXPECTED VS ACTUAL")
print("=" * 80)

print("\nKentucky 2024 General Election actual results:")
print("  Trump (R):  ~1.46M (from news)")
print("  Harris (D): ~1.02M")
print("  Total votes: ~2.7M")

harris_2024 = df[(df['candidate'].str.contains('Harris', case=False, na=False)) & (df['year'] == 2024)]
print(f"\nDataset Harris 2024: {harris_2024['votes'].sum():,}")
print(f"Dataset Trump 2024:  {trump_2024['votes'].sum():,}")
print(f"Dataset total 2024:  {df[df['year']==2024]['votes'].sum():,}")

# Maybe we're looking at precinct-level that wasn't deduplicated by office?
if 'office' in df.columns:
    print("\nLet's check dedup logic - maybe office matters:")
    trump_2024_all = df[(df['candidate'].str.contains('Trump', case=False, na=False)) & (df['year'] == 2024)]
    print(trump_2024_all[['county', 'candidate', 'office', 'votes']].to_string())
