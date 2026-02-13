"""
Verify the data to understand why vote totals are so high
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")
final_file = data_dir / "KY_ELECTIONS_FINAL.csv"

df = pd.read_csv(final_file)

print("=" * 80)
print("DATA VERIFICATION")
print("=" * 80)

print(f"\nTotal records: {len(df):,}")
print(f"Total votes (summed): {df['votes'].sum():,}")
print(f"Average votes per record: {df['votes'].mean():,.0f}")

# Check for duplicates
print("\n" + "=" * 80)
print("DUPLICATE CHECK")
print("=" * 80)

# Check duplicates on county+candidate+year
dup_cols = ['county', 'candidate', 'year']
duplicates = df[df.duplicated(subset=dup_cols, keep=False)]

if len(duplicates) > 0:
    print(f"\n⚠ Found {len(duplicates)} duplicate records (same county/candidate/year)!")
    print("\nSample duplicates:")
    print(duplicates[dup_cols + ['votes']].sort_values(by=['candidate', 'county', 'year']).head(20))
else:
    print("\n✓ No exact duplicates found")

# Check Trump specifically
print("\n" + "=" * 80)
print("TRUMP VOTES BREAKDOWN")
print("=" * 80)

trump_data = df[df['candidate'].str.contains('Trump', case=False, na=False)]
print(f"\nTrump records: {len(trump_data)}")
print(f"Total Trump votes: {trump_data['votes'].sum():,}")

trump_by_year = trump_data.groupby('year')['votes'].sum().sort_index()
print("\nTrump votes by year:")
for year, votes in trump_by_year.items():
    print(f"  {year}: {votes:>12,}")

print("\nTrump records by year and county (first 10):")
trump_grouped = trump_data.groupby(['year', 'county'])['votes'].sum().sort_index(ascending=[False, True])
for (year, county), votes in trump_grouped.head(10).items():
    print(f"  {year} - {county:20} {votes:>12,}")

# Check McConnell
print("\n" + "=" * 80)
print("McCONNELL VOTES BREAKDOWN")
print("=" * 80)

mcconnell_data = df[df['candidate'].str.contains('Mcconnell|McConnell', case=False, na=False)]
print(f"\nMcConnell records: {len(mcconnell_data)}")
print(f"Total McConnell votes: {mcconnell_data['votes'].sum():,}")

mcc_by_year = mcconnell_data.groupby('year')['votes'].sum().sort_index()
print("\nMcConnell votes by year:")
for year, votes in mcc_by_year.items():
    print(f"  {year}: {votes:>12,}")

# Overall sanity check - total votes per year
print("\n" + "=" * 80)
print("TOTAL VOTES BY YEAR")
print("=" * 80)

votes_by_year = df.groupby('year')['votes'].sum().sort_index()
print("\nTotal votes cast (all candidates) by year:")
for year, votes in votes_by_year.items():
    print(f"  {year}: {votes:>12,}")

# Estimate expected votes (rough)
print("\n" + "=" * 80)
print("SANITY CHECK")
print("=" * 80)
print("\nKentucky registered voters: ~3 million")
print("Average turnout: 50-60%")
print("Expected votes per election: ~1.5-2 million")
print("\nIf dataset is correct, total votes across 14 elections")
print("should be roughly 14 * 1.5M to 14 * 2M = 21-28 million")
print(f"\nActual total votes in dataset: {df['votes'].sum():,}")
