"""
Fix duplicates: Aggregate precinct-level data to true county totals
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")
final_file = data_dir / "KY_ELECTIONS_FINAL.csv"

df = pd.read_csv(final_file)

print("=" * 80)
print("DEDUPLICATION: PRECINCT -> COUNTY AGGREGATION")
print("=" * 80)

print(f"\nBefore: {len(df):,} records with {df['votes'].sum():,} total votes")
print(f"Duplicates found: 8,041")

# Group by county, candidate, year, office and sum votes
# This converts precinct-level data to county totals
agg_dict = {
    'votes': 'sum',
    'party': 'first',  # Same for all precincts in county
    'election_day': 'first',
    'county': 'first'
}

# Only include columns that exist
available_cols = df.columns.tolist()
agg_dict = {k: v for k, v in agg_dict.items() if k in available_cols}

# Group by key columns
groupby_cols = ['county', 'candidate', 'year']
if 'office' in available_cols:
    groupby_cols.append('office')

df_dedup = df.groupby(groupby_cols, as_index=False).agg(agg_dict)

print(f"After: {len(df_dedup):,} records with {df_dedup['votes'].sum():,} total votes")
print(f"Removed: {len(df) - len(df_dedup):,} duplicate entries")

# Verify fix
print("\n" + "=" * 80)
print("VERIFICATION AFTER DEDUPLICATION")
print("=" * 80)

# Check for remaining duplicates
remaining_dups = df_dedup[df_dedup.duplicated(subset=['county', 'candidate', 'year'], keep=False)]
if len(remaining_dups) > 0:
    print(f"⚠ Still have {len(remaining_dups)} duplicate records")
else:
    print("✓ No duplicate records remaining")

# Check Trump
trump_dedup = df_dedup[df_dedup['candidate'].str.contains('Trump', case=False, na=False)]
print(f"\nTrump after dedup: {trump_dedup['votes'].sum():,} total votes")
trump_by_year = trump_dedup.groupby('year')['votes'].sum()
for year, votes in trump_by_year.items():
    print(f"  {year}: {votes:>12,}")

# Check McConnell
mcc_dedup = df_dedup[df_dedup['candidate'].str.contains('Mcconnell|McConnell', case=False, na=False)]
print(f"\nMcConnell after dedup: {mcc_dedup['votes'].sum():,} total votes")
mcc_by_year = mcc_dedup.groupby('year')['votes'].sum()
for year, votes in mcc_by_year.items():
    print(f"  {year}: {votes:>12,}")

# Total votes by year
print(f"\nTotal votes by year (AFTER dedup):")
votes_by_year = df_dedup.groupby('year')['votes'].sum()
for year, votes in votes_by_year.items():
    print(f"  {year}: {votes:>12,}")

print("\n" + "=" * 80)
print("TOP 15 CANDIDATES (AFTER DEDUP)")
print("=" * 80)

top_15 = df_dedup.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(15)
for idx, (name, votes) in enumerate(top_15.items(), 1):
    print(f"{idx:2}. {name:35} {votes:>12,}")

# Save deduplicated data
dedup_file = data_dir / "KY_ELECTIONS_DEDUP.csv"
df_dedup.to_csv(dedup_file, index=False)
print(f"\n✓ Saved: {dedup_file}")

print(f"\nTotal records: {len(df_dedup):,}")
print(f"Total votes: {df_dedup['votes'].sum():,}")
print(f"Unique counties: {df_dedup['county'].nunique()}")
print(f"Unique candidates: {df_dedup['candidate'].nunique()}")
