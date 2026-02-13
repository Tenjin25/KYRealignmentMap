"""
Clean and validate Kentucky election master data.
Removes headers, corrupted entries, and standardizes formats.
"""

import pandas as pd
from pathlib import Path
import re

print("=" * 80)
print("ELECTION DATA CLEANING & VALIDATION")
print("=" * 80)

master_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_ELECTIONS_MASTER.csv")

if not master_file.exists():
    print(f"Error: {master_file} not found")
    exit(1)

print(f"\nLoading: {master_file}")
df = pd.read_csv(master_file)

print(f"Original size: {len(df):,} rows")

# Step 1: Remove header rows and metadata
print("\n" + "="*80)
print("STEP 1: REMOVE HEADERS/METADATA")
print("="*80)

# Common header patterns to remove
header_patterns = [
    'Secretary of State', 'President and Vice President', 'General Election',
    'Certified Results', 'Commonwealth of Kentucky', 'Official',
    'For the office of', 'Alison Lundergan Grimes, Secretary'
]

rows_before = len(df)
for pattern in header_patterns:
    df = df[~df['candidate'].str.contains(pattern, na=False, case=False)]

print(f"Removed {rows_before - len(df):,} header rows")

# Step 2: Remove generic candidate names
print("\n" + "="*80)
print("STEP 2: REMOVE GENERIC/PLACEHOLDER CANDIDATES")
print("="*80)

generic_patterns = [
    r'^Candidate_\d+$',
    r'^\d+$',
    r'^[A-Z]$',
    r'^blank|write.?in|scattered|overvote|undervote',
]

rows_before = len(df)
for pattern in generic_patterns:
    df = df[~df['candidate'].str.match(pattern, na=False, case=False)]

print(f"Removed {rows_before - len(df):,} generic candidate rows")

# Step 3: Remove malformed candidate names (VP tickets, symbols, etc)
print("\n" + "="*80)
print("STEP 3: REMOVE MALFORMED ENTRIES")
print("="*80)

malformed_patterns = [
    r'&.*Cheney',  # Bush & Cheney
    r'&.*Palin',   # McCain & Palin
    r'&.*Biden',   # Obama & Biden
    r'&.*Edwards', # Kerry & Edwards
    r'[^\w\s\'\-\.]',  # Remove entries with special characters (except apostrophes, hyphens, dots)
]

rows_before = len(df)
for pattern in malformed_patterns[:-1]:  # Skip the last one for now
    df = df[~df['candidate'].str.contains(pattern, na=False, case=False, regex=True)]

print(f"Removed {rows_before - len(df):,} malformed entries")

# Step 4: Fix unrealistic vote counts
print("\n" + "="*80)
print("STEP 4: VALIDATE VOTE COUNTS")
print("="*80)

# Reasonable max votes per candidate in a single county: ~200,000
# (Kentucky's largest county is Jefferson with ~700k people)
max_reasonable = 250000

rows_before = len(df)
df = df[(df['votes'] <= max_reasonable) | (df['votes'].isna())]
print(f"Removed {rows_before - len(df):,} entries with unrealistic vote counts (>{max_reasonable:,})")

# Step 5: Standardize and normalize
print("\n" + "="*80)
print("STEP 5: STANDARDIZATION")
print("="*80)

# Trim whitespace
df['candidate'] = df['candidate'].str.strip()
df['county'] = df['county'].str.strip()
df['party'] = df['party'].str.strip()
df['office'] = df['office'].str.strip()

# Convert votes to integer
df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)

# Remove rows with missing critical data
rows_before = len(df)
df = df.dropna(subset=['county', 'candidate', 'votes'])
df = df[df['votes'] > 0]  # Only keep rows with at least 1 vote
print(f"Removed {rows_before - len(df):,} incomplete rows")

# Step 6: Quality checks
print("\n" + "="*80)
print("DATA QUALITY SUMMARY")
print("="*80)

print(f"\nFinal size: {len(df):,} rows")
print(f"Years: {sorted(df['year'].unique())}")
print(f"Unique counties: {df['county'].nunique()}/120")
print(f"Unique candidates: {df['candidate'].nunique():,}")
print(f"Total votes: {df['votes'].sum():,}")

# Check for remaining issues
print(f"\nRemaining issues:")
print(f"  Null counties: {df['county'].isna().sum()}")
print(f"  Null candidates: {df['candidate'].isna().sum()}")
print(f"  Null votes: {df['votes'].isna().sum()}")
print(f"  Zero votes: {(df['votes'] == 0).sum()}")

# Step 7: Save cleaned data
print("\n" + "="*80)
print("SAVING CLEANED DATA")
print("="*80)

cleaned_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_ELECTIONS_CLEANED.csv")
df.to_csv(cleaned_file, index=False)
print(f"✓ Saved: {cleaned_file}")

# Step 8: Show top candidates after cleaning
print("\n" + "="*80)
print("TOP 20 CANDIDATES AFTER CLEANING")
print("="*80)

top_candidates = df.groupby('candidate')[['votes']].sum().sort_values('votes', ascending=False).head(20)
for idx, (name, row) in enumerate(top_candidates.iterrows(), 1):
    print(f"{idx:2}. {name:40} {row['votes']:>15,} votes")

# Step 9: Summary by year
print("\n" + "="*80)
print("VOTES BY YEAR (CLEANED)")
print("="*80)

year_summary = df.groupby('year').agg({
    'county': 'nunique',
    'candidate': 'nunique',
    'votes': 'sum'
}).round(0)

year_summary.columns = ['Counties', 'Candidates', 'Total Votes']

print(year_summary.to_string())

print("\n" + "="*80)
print("✓ CLEANING COMPLETE")
print("="*80)
print("\nNext: Review cleaned data and identify remaining issues")
