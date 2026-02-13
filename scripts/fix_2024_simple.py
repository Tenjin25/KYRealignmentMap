"""
Simple fix: Take KY_ELECTIONS_DEDUP.csv and replace 2024 with properly aggregated 2024
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

print("=" * 80)
print("FIXING 2024 DATA INFLATION")
print("=" * 80)

# Load clean dataset (2002-2023)
df_clean = pd.read_csv(data_dir / "KY_ELECTIONS_DEDUP.csv")
print(f"\n1. Base clean dataset: {len(df_clean):,} records")
print(f"   Years: {sorted(df_clean['year'].unique())}")
print(f"   Trump votes (2016, 2020): {df_clean[(df_clean['candidate']=='Donald J Trump') & (df_clean['year'].isin([2016, 2020]))]['votes'].sum():,}")

# Remove 2024 from clean dataset
df_no_2024 = df_clean[df_clean['year'] != 2024]
print(f"\n2. Removed 2024: {len(df_no_2024):,} records remaining")
print(f"   New Trump total (2016, 2020 only): {df_no_2024[(df_no_2024['candidate']=='Donald J Trump') & (df_no_2024['year'].isin([2016, 2020]))]['votes'].sum():,}")

# Load and properly aggregate 2024 precinct data
print(f"\n3. Loading 2024 precinct data (20241105)...")
df_2024_raw = pd.read_csv(data_dir / "20241105__ky__general__county.csv")

# Rename columns to match
df_2024_raw.columns = [col.lower() for col in df_2024_raw.columns]
df_2024_raw['year'] = 2024

# Aggregate precincts to counties
df_2024_county = df_2024_raw.groupby(['county', 'candidate', 'year', 'office'], as_index=False).agg({
    'votes': 'sum',
    'party': 'first'
})

print(f"   Aggregated to: {len(df_2024_county):,} records, {df_2024_county['votes'].sum():,} votes")
print(f"   Trump 2024: {df_2024_county[df_2024_county['candidate']=='Donald J. Trump']['votes'].sum():,}")
print(f"   Harris 2024: {df_2024_county[df_2024_county['candidate']=='Kamala D. Harris']['votes'].sum():,}")

# Standardize 2024 candidate names (add space to "J.")
df_2024_county['candidate'] = df_2024_county['candidate'].str.replace('Donald J.', 'Donald J')
df_2024_county['candidate'] = df_2024_county['candidate'].str.replace('Kamala D.', 'Kamala D')

print(f"\n   After standardization:")
print(f"   Trump 2024: {df_2024_county[df_2024_county['candidate']=='Donald J Trump']['votes'].sum():,}")
print(f"   Harris 2024: {df_2024_county[df_2024_county['candidate']=='Kamala D Harris']['votes'].sum():,}")

# Drop office column if exists to match base dataset
if 'office' in df_2024_county.columns:
    df_2024_county = df_2024_county.drop('office', axis=1)
if 'election_day' in df_2024_county.columns:
    df_2024_county = df_2024_county.drop('election_day', axis=1)

# Combine
print(f"\n4. Combining...")
df_final = pd.concat([df_no_2024, df_2024_county], ignore_index=True)

# Ensure columns match
required_cols = ['county', 'candidate', 'votes', 'year', 'party']
for col in required_cols:
    if col not in df_final.columns:
        print(f"   ⚠ Missing column: {col}")

df_final = df_final[required_cols]

print(f"   Final dataset: {len(df_final):,} records")
print(f"   Total votes: {df_final['votes'].sum():,}")

# Verify
print(f"\n5. VERIFICATION:")
print(f"   Years: {sorted(df_final['year'].unique())}")
print(f"   Counties: {df_final['county'].nunique()}")
print(f"   Candidates: {df_final['candidate'].nunique():,}")

print(f"\n   Trump votes by year:")
trump_by_year = df_final[df_final['candidate']=='Donald J Trump'].groupby('year')['votes'].sum()
for year, votes in trump_by_year.items():
    print(f"     {year}: {votes:>12,}")

print(f"\n   Harris votes by year:")
harris_by_year = df_final[df_final['candidate'].str.contains('Harris', case=False, na=False)].groupby('year')['votes'].sum()
for year, votes in harris_by_year.items():
    print(f"     {year}: {votes:>12,}")

# Save
output_file = data_dir / "KY_ELECTIONS_CORRECTED.csv"
df_final.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")
print(f"\n✓✓✓ VOLUME CHECK: Should be ~2-3M votes for 2024, Trump ~1.46M")
