"""
Aggregate all Kentucky election data into one comprehensive dataset.
"""

import pandas as pd
from pathlib import Path
import sys

print("=" * 80)
print("KENTUCKY ELECTION DATA AGGREGATOR")
print("=" * 80)

# Use absolute path to data directory
data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

# Find all election CSV files
csv_files = sorted(list(data_dir.glob("*__ky__*county.csv")))

print(f"\nFound {len(csv_files)} election CSV files:\n")

all_data = []
file_info = []

for csv_file in csv_files:
    try:
        df = pd.read_csv(csv_file)
        
        # Standardize column names
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Extract date from filename (format: YYYYMMDD)
        filename = csv_file.stem
        date_part = filename.split('__')[0]  # e.g., "20241105"
        
        if len(date_part) == 8:
            year = date_part[:4]
            df['year'] = int(year)
            df['election_date'] = date_part
        else:
            df['year'] = None
            df['election_date'] = None
        
        # Ensure standard columns
        for col in ['county', 'candidate', 'party', 'office', 'votes']:
            if col not in df.columns:
                df[col] = None
        
        all_data.append(df)
        
        # Track info
        file_info.append({
            'file': csv_file.name,
            'rows': len(df),
            'year': year,
            'counties': df['county'].nunique() if 'county' in df.columns else 0,
            'candidates': df['candidate'].nunique() if 'candidate' in df.columns else 0,
            'total_votes': df['votes'].sum() if 'votes' in df.columns else 0
        })
        
        print(f"  ✓ {csv_file.name}")
        print(f"    Rows: {len(df):,} | Counties: {df['county'].nunique()}/120 | Votes: {df['votes'].sum():,.0f}")
        
    except Exception as e:
        print(f"  ✗ {csv_file.name}: {e}")

# Combine all data
print(f"\n{'='*80}")
print("COMBINING DATA...")
print(f"{'='*80}")

combined_df = pd.concat(all_data, ignore_index=True)

print(f"\nTotal rows: {len(combined_df):,}")
print(f"Years covered: {sorted(combined_df['year'].dropna().unique())}")
print(f"Total unique candidates: {combined_df['candidate'].nunique():,}")
print(f"Total votes across all years: {combined_df['votes'].sum():,.0f}")

# Save the master file
master_file = data_dir / "KY_ELECTIONS_MASTER.csv"
combined_df.to_csv(master_file, index=False)
print(f"\n✓ Saved master file: {master_file}")

# Create summary by year
print(f"\n{'='*80}")
print("SUMMARY BY YEAR")
print(f"{'='*80}\n")

year_summary = combined_df.groupby('year').agg({
    'county': 'nunique',
    'candidate': 'nunique',
    'office': 'nunique',
    'votes': 'sum',
    'election_date': 'first'
}).round(0)

year_summary.columns = ['Counties', 'Candidates', 'Offices', 'Total Votes', 'Date']

print(year_summary.to_string())

# Save summary
summary_file = data_dir / "SUMMARY_BY_YEAR.csv"
year_summary.to_csv(summary_file)
print(f"\n✓ Saved summary: {summary_file}")

# List of files included
print(f"\n{'='*80}")
print("FILES INCLUDED IN AGGREGATION")
print(f"{'='*80}\n")

summary_df = pd.DataFrame(file_info)
print(summary_df.to_string(index=False))

print(f"\n{'='*80}")
print("DATA QUALITY CHECKS")
print(f"{'='*80}\n")

# Check for issues
print(f"Records with missing county: {combined_df['county'].isna().sum()}")
print(f"Records with missing candidate: {combined_df['candidate'].isna().sum()}")
print(f"Records with missing votes: {combined_df['votes'].isna().sum()}")
print(f"Records with 0 votes: {(combined_df['votes'] == 0).sum()}")

# Top candidates overall
print(f"\n{'='*80}")
print("TOP 20 VOTE-GETTERS (ALL TIME)")
print(f"{'='*80}\n")

top_candidates = combined_df.groupby('candidate')[['votes']].sum().sort_values('votes', ascending=False).head(20)
for idx, (name, row) in enumerate(top_candidates.iterrows(), 1):
    print(f"{idx:2}. {name:40} {row['votes']:>15,.0f} votes")

print(f"\n{'='*80}")
print("✓ AGGREGATION COMPLETE")
print(f"{'='*80}")
print("""
Next steps:
  1. Review: cat data/KY_ELECTIONS_MASTER.csv (first few rows)
  2. Analyze: Use this master file for analysis
  3. Export: Convert to other formats (JSON, Excel, etc.)
  4. Query: Filter by year, county, candidate, office
""")
