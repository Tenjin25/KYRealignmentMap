"""
Final cleaning pass: Fix truncated county names
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("FINAL PASS - FIX TRUNCATED COUNTY NAMES")
print("=" * 80)

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

# Try to use standardized file if it exists, otherwise use cleaned
standardized_file = data_dir / "KY_ELECTIONS_STANDARDIZED.csv"
cleaned_file = data_dir / "KY_ELECTIONS_CLEANED.csv"

if standardized_file.exists():
    df = pd.read_csv(standardized_file)
    print("Using standardized file")
else:
    df = pd.read_csv(cleaned_file)
    print("Using cleaned file (standardizing now)")

print(f"\nStarting: {len(df):,} rows, {df['county'].nunique()} unique counties")

# Count records BEFORE
before_counts = {}
for abbr, full in [('Letc', 'Letcher'), ('Mcck', 'Mccracken'), ('Metc', 'Metcalfe')]:
    before_counts[abbr] = (df['county'] == abbr).sum()
    print(f"  {abbr:10} -> {full:15} ({before_counts[abbr]:>3} records)")

# Fix the truncated county names
county_fixes = {
    'Letc': 'Letcher',
    'Mcck': 'Mccracken',
    'Metc': 'Metcalfe'
}

for abbr, full_name in county_fixes.items():
    df.loc[df['county'] == abbr, 'county'] = full_name

print(f"\nAfter fix: {len(df):,} rows, {df['county'].nunique()} unique counties")
print(f"Expected: 120 Kentucky counties ✓" if df['county'].nunique() == 120 else f"⚠ Still have {df['county'].nunique()} (need 120)")

# Save final version
final_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_ELECTIONS_FINAL.csv")
df.to_csv(final_file, index=False)
print(f"\n✓ Saved final dataset: {final_file}")

# Summary
print("\n" + "=" * 80)
print("FINAL DATA QUALITY REPORT")
print("=" * 80)
print(f"\nRecords: {len(df):,}")
print(f"Counties: {df['county'].nunique()} (expected: 120)")
print(f"Candidates: {df['candidate'].nunique():,}")
print(f"Election years: {sorted(df['year'].unique())}")
print(f"Total votes: {df['votes'].sum():,}")

# Check for any remaining issues
nulls = df.isnull().sum()
if nulls.any():
    print("\n⚠ Null values found:")
    print(nulls[nulls > 0])
else:
    print("\n✓ No null values")

zero_votes = (df['votes'] == 0).sum()
if zero_votes > 0:
    print(f"⚠ Zero-vote records: {zero_votes}")
else:
    print("✓ No zero-vote records")

print("\n" + "=" * 80)
print("TOP 15 CANDIDATES")
print("=" * 80)
top_15 = df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(15)
for idx, (name, votes) in enumerate(top_15.items(), 1):
    print(f"{idx:2}. {name:35} {votes:>12,}")
