"""
Final polish: Remove remaining garbage entries
"""

import pandas as pd
from pathlib import Path
import re

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

print("=" * 80)
print("FINAL POLISH: REMOVE GARBAGE ENTRIES")
print("=" * 80)

df = pd.read_csv(data_dir / "KY_ELECTIONS_CLEAN.csv")
print(f"\nStarting: {len(df):,} records")

before = len(df)

# Remove VP ticket combinations
vp_tickets = ['Bush & Cheney', 'McCain & Palin', 'Obama & Biden', 'Kerry & Edwards', 
              'Bush Cheney', 'McCain Palin', 'Obama Biden', 'Kerry Edwards',
              'Trump Pence', 'Biden Harris']

for ticket in vp_tickets:
    df = df[~df['candidate'].str.contains(ticket, case=False, na=False)]

removed_vp = before - len(df)
print(f"Removed VP tickets: {removed_vp:,}")

# Remove obviously bad entries
before = len(df)
bad_patterns = [
    r'^Secretary',
    r'^General Election',
    r'^Commonwealth',
    r'^State of Kentucky',
    r'TOTAL',
    r'^Election',
    r'Scattered',
    r'^\d+$',
    r'^Other',
]

for pattern in bad_patterns:
    df = df[~df['candidate'].str.match(pattern, case=False, na=False)]

removed_bad = before - len(df)
print(f"Removed bad names: {removed_bad:,}")

# Fix county name truncations
county_fixes = {
    'Letc': 'Letcher',
    'Mcck': 'Mccracken', 
    'Metc': 'Metcalfe',
    'Letch': 'Letcher'
}

for old, new in county_fixes.items():
    df.loc[df['county'] == old, 'county'] = new

print(f"Fixed truncated counties")

# Check final result
print(f"\n" + "=" * 80)
print(f"FINAL RESULTS")
print(f"=" * 80)

print(f"\nRecords: {len(df):,} (removed {before - len(df):,} entries)")
print(f"Total votes: {df['votes'].sum():,.0f}")
print(f"Counties: {df['county'].nunique()}/120")
print(f"Candidates: {df['candidate'].nunique():,}")
print(f"Years: {sorted(df['year'].unique())}")

print(f"\nTOP 10:")
top10 = df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
for idx, (name, votes) in enumerate(top10.items(), 1):
    print(f"{idx:2}. {name:35} {votes:>12,.0f}")

# Save
output_file = data_dir / "KY_ELECTIONS_FINAL_CLEAN.csv"
df.to_csv(output_file, index=False)
print(f"\n✓ Saved: KY_ELECTIONS_FINAL_CLEAN.csv")
