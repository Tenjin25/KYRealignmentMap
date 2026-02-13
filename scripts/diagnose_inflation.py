"""
Investigate why vote totals are still inflated
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

df = pd.read_csv(data_dir / "KY_ELECTIONS_FINAL_CLEAN.csv")

print("=" * 80)
print("INVESTIGATING VOTE INFLATION")
print("=" * 80)

print(f"\nDataset: {len(df):,} records, {df['votes'].sum():,.0f} votes")

# Check 2024 specifically
df_2024 = df[df['year'] == 2024]
print(f"\n2024 data: {len(df_2024):,} records, {df_2024['votes'].sum():,.0f} votes")

# Trump 2024
trump_2024 = df_2024[df_2024['candidate'] == 'Donald J. Trump']
print(f"  Trump 2024: {len(trump_2024)} records, {trump_2024['votes'].sum():,.0f} votes")

if len(trump_2024) > 0:
    print(f"\n  Trump 2024 by county (first 10):")
    print(trump_2024[['county', 'votes']].sort_values('votes', ascending=False).head(10).to_string(index=False))

# Check if we have office/district data in source files
raw_file = data_dir / "20241105__ky__general__county.csv"
df_raw = pd.read_csv(raw_file)

print(f"\n\nRAW 20241105 file analysis:")
print(f"  Columns: {list(df_raw.columns)}")

if 'office' in df_raw.columns:
    print(f"  Unique offices: {df_raw['office'].nunique()}")
    print(df_raw['office'].value_counts().head(10))
    
    trump_raw = df_raw[df_raw['candidate'] == 'Donald J. Trump']
    print(f"\n  Trump total in raw file: {trump_raw['votes'].sum():,.0f}")
    print(f"  Trump by office:")
    print(trump_raw.groupby('office')['votes'].sum())

# Are we aggregating to just county/candidate/year, or losing office info?
print(f"\n\nCLEAN file structure check:")
print(f"  Columns: {list(df.columns)}")

# Count how many times each county/candidate combo appears for 2024
dup_check = df_2024.groupby(['county', 'candidate']).size()
if (dup_check > 1).any():
    print(f"  ⚠ Found duplicate county/candidate pairs in 2024:")
    dupes = dup_check[dup_check > 1]
    for (county, cand), count in dupes.head(5).items():
        print(f"    {cand:30} in {county:15} appears {count}x")
else:
    print(f"  ✓ No county/candidate duplicates in 2024")

# Expected votes
print(f"\n" + "=" * 80)
print(f"SANITY CHECK")
print(f"=" * 80)
print(f"\nKentucky 2024 General Election (from news):")
print(f"  Trump: ~1.46M")
print(f"  Harris: ~1.02M")
print(f"  Total: ~2.7M votes\n")

print(f"Our 2024 data:")
print(f"  Trump: {df_2024[df_2024['candidate']=='Donald J. Trump']['votes'].sum():,.0f}")
harris_2024 = df_2024[df_2024['candidate'].str.contains('Harris', case=False, na=False)]['votes'].sum()
print(f"  Harris: {harris_2024:,.0f}")
print(f"  Total: {df_2024['votes'].sum():,.0f}")

# Check other major years
print(f"\n2020 General Election (from news):")
print(f"  Trump: ~1.1M")
print(f"  Biden: ~1.1M")
print(f"  Total: ~2.4M\n")

df_2020 = df[df['year'] == 2020]
print(f"Our 2020 data: {df_2020['votes'].sum():,.0f} votes")
print(f"  Trump: {df_2020[df_2020['candidate'].str.contains('Trump', case=False, na=False)]['votes'].sum():,.0f}")
print(f"  Biden: {df_2020[df_2020['candidate'].str.contains('Biden', case=False, na=False)]['votes'].sum():,.0f}")
