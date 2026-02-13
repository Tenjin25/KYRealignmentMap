"""
FRESH START: Build clean dataset from ONLY good CSV files
- EXCLUDE: 20121106 (CORRUPTED - 633 trillion votes), 20241106 (Candidate_# garbage), precinct file
- USE: All other *county.csv files
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

print("=" * 80)
print("CLEAN BUILD: GOOD FILES ONLY")
print("=" * 80)

# Define good files explicitly (exclude corrupted ones)
good_files = [
    "20021105__ky__general__county.csv",
    "20031104__ky__general__county.csv",
    "20041102__ky__general__county.csv",
    "20071106__ky__general__county.csv",
    "20081104__ky__general__county.csv",
    "20101102__ky__general__county.csv",
    "20101102__ky__general__senate__county.csv",
    "20111108__ky__general__county.csv",
    # SKIP: "20121106__ky__general__county.csv"  # CORRUPTED
    "20141104__ky__general__county.csv",
    "20151103__ky__general__county.csv",
    "20161108__ky__general__county.csv",
    "20161108__ky__general__senate__county.csv",
    "20191105__ky__general__county.csv",
    "20201103__ky__general__county.csv",
    "20201103__ky__general__senate__county.csv",
    "20231107__ky__general__county.csv",
    "20241105__ky__general__county.csv",  # Use THIS, not 20241106
    # SKIP: "20241105__ky__general__precinct.csv",  # Precinct-level
    # SKIP: "20241106__ky__general__county.csv"  # CORRUPTED
]

print(f"\nLoading {len(good_files)} FILES:\n")

all_data = []

for fname in good_files:
    fpath = data_dir / fname
    if not fpath.exists():
        print(f"  ✗ NOT FOUND: {fname}")
        continue
    
    df = pd.read_csv(fpath)
    
    # Standardize columns
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Extract year from filename
    year = int(fname[:4])
    if 'year' not in df.columns:
        df['year'] = year
    
    # Keep only essential columns
    essential_cols = ['county', 'candidate', 'party', 'votes']
    for col in essential_cols:
        if col not in df.columns:
            print(f"  ⚠ {fname} missing '{col}'")
    
    # Select only essential columns that exist
    cols_to_keep = [col for col in ['county', 'candidate', 'party', 'votes', 'year'] if col in df.columns]
    df = df[cols_to_keep]
    
    print(f"  ✓ {fname:45} {len(df):>5} records, {df['votes'].sum():>12,.0f} votes")
    
    all_data.append(df)

# Combine
print(f"\nCombining...")
df_final = pd.concat(all_data, ignore_index=True)

print(f"  Combined: {len(df_final):,} records")
print(f"  Total votes: {df_final['votes'].sum():,.0f}")

# Basic cleaning
print(f"\nCleaning...")
before = len(df_final)

# Remove nulls in critical fields
df_final = df_final.dropna(subset=['county', 'candidate', 'votes'])

# Convert votes to numeric
df_final['votes'] = pd.to_numeric(df_final['votes'], errors='coerce')
df_final = df_final.dropna(subset=['votes'])

# Remove zero-vote records
df_final = df_final[df_final['votes'] > 0]

print(f"  Removed {before - len(df_final):,} problematic records")
print(f"  Final: {len(df_final):,} records, {df_final['votes'].sum():,.0f} votes")

# Summary
print(f"\n" + "=" * 80)
print(f"FINAL DATASET")
print(f"=" * 80)
print(f"\nRecords: {len(df_final):,}")
print(f"Total votes: {df_final['votes'].sum():,.0f}")
print(f"Counties: {df_final['county'].nunique()}")
print(f"Candidates: {df_final['candidate'].nunique():,}")
print(f"Election years: {sorted(df_final['year'].unique())}")

print(f"\nTOP 15 CANDIDATES:")
top_15 = df_final.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(15)
for idx, (name, votes) in enumerate(top_15.items(), 1):
    print(f"{idx:2}. {name:35} {votes:>12,.0f}")

# Candidate name cleanup - fix spacing issues
print(f"\n" + "=" * 80)
print(f"CHECKING FOR NAME VARIANTS")
print(f"=" * 80)

# Check for Trump variants
trump_variants = df_final[df_final['candidate'].str.contains('Trump|Donald', case=False, na=False)]['candidate'].unique()
print(f"\nTrump variants: {len(trump_variants)}")
for name in sorted(trump_variants):
    votes = df_final[df_final['candidate'] == name]['votes'].sum()
    print(f"  {name:35} {votes:>12,.0f}")

# Save
output_file = data_dir / "KY_ELECTIONS_CLEAN.csv"
df_final.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")
