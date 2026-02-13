"""
Start completely fresh - check actual files and understand what we REALLY have
"""

import pandas as pd
from pathlib import Path
import os

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

print("=" * 80)
print("FRESH START - AUDIT ALL CSV FILES")
print("=" * 80)

# Get ALL csv files
csv_files = sorted(data_dir.glob("*__ky__*.csv"))

print(f"\nFound {len(csv_files)} CSV files:\n")

for f in csv_files:
    size_mb = os.path.getsize(f) / 1024 / 1024
    print(f"{'─' * 80}")
    print(f"FILE: {f.name} ({size_mb:.1f} MB)")
    
    df = pd.read_csv(f, nrows=1000)  # Just first 1000 rows for speed
    
    print(f"  Records (sample): {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    
    # Check for year
    if 'year' in df.columns:
        years = df['year'].unique()
        print(f"  Years: {sorted(years)}")
    
    # Check for Trump
    if 'candidate' in df.columns:
        trump_mask = df['candidate'].str.contains('Trump|Donald', case=False, na=False)
        if trump_mask.any():
            trump_votes = df[trump_mask]['votes'].sum() if 'votes' in df.columns else 0
            print(f"  ⚠ HAS TRUMP: {trump_votes:,} votes (in first 1000 rows)")
        
        # Check data quality
        if 'votes' in df.columns:
            total = df['votes'].sum()
            max_vote = df['votes'].max()
            print(f"  Total votes (first 1000): {total:,} (max: {max_vote:,})")
            
            # Check for data issues
            if max_vote > 500000:
                print(f"  ⚠ SUSPICIOUS: Single record with {max_vote:,} votes (>500k)")
            
            generic = df[df['candidate'].str.contains('Candidate_', case=False, na=False)]
            if len(generic) > 0:
                print(f"  ⚠ CORRUPTED: {len(generic)} 'Candidate_#' placeholder entries")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("\nWhich files should we actually USE for a clean dataset?")
print("(Based on data quality, not file size)")
