"""
Rebuild final dataset using ONLY proper county-level data
- Exclude corrupted 20241106 (Candidate_# garbage)  
- Properly aggregate 20241105 precinct data to county level
- Use only 1 version of each year
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

print("=" * 80)
print("REBUILDING DATASET - COUNTY LEVEL ONLY")
print("=" * 80)

# 1. Load and properly aggregate 20241105 (precinct data mislabeled as county)
print("\n1. Processing 20241105 (2024 General - precinct data)...")
df_2024_precinct = pd.read_csv(data_dir / "20241105__ky__general__county.csv")
print(f"   Raw: {len(df_2024_precinct)} records, {df_2024_precinct['votes'].sum():,} votes")
print(f"   Columns: {list(df_2024_precinct.columns)}")

# Add year if missing
if 'year' not in df_2024_precinct.columns:
    df_2024_precinct['year'] = 2024

# Aggregate to county level
group_cols = ['county', 'candidate', 'office']
df_2024_county = df_2024_precinct.groupby(group_cols, as_index=False).agg({
    'votes': 'sum',
    'party': 'first'
})

print(f"   Aggregated: {len(df_2024_county)} records, {df_2024_county['votes'].sum():,} votes")
print(f"   Trump 2024 now: {df_2024_county[df_2024_county['candidate']=='Donald J. Trump']['votes'].sum():,}")

# 2. Find all other proper county files (* Remove 20241106 - it's corrupted)
all_files = sorted(list(data_dir.glob("*__ky__*county.csv")))

# Remove the corruption
all_files = [f for f in all_files if "20241106" not in f.name]
all_files = [f for f in all_files if "precinct" not in f.name]

print(f"\n2. Found {len(all_files)} valid county CSV files:")
for f in all_files:
    print(f"   - {f.name}")

# 3. Load and combine
print("\n3. Loading all files...")
all_data = []

for csv_file in all_files:
    if "20241105" in csv_file.name:
        # Use our aggregated version
        df = df_2024_county.copy()
        print(f"   ✓ {csv_file.name} - {len(df)} records (aggregated from precinct)")
    else:
        df = pd.read_csv(csv_file)
        # Normalize columns
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Check if it's already aggregated or needs aggregation
        dup_check = df[df.duplicated(subset=['county', 'candidate ', 'year'] if 'year' in df.columns else ['county', 'candidate'], keep=False)]
        if len(dup_check) > 100:
            # Has significant duplicates - aggregate
            group_cols = ['county', 'candidate']
            if 'year' in df.columns:
                group_cols.append('year')
            if 'office' in df.columns:
                group_cols.append('office')
            
            df = df.groupby(group_cols, as_index=False).agg({
                'votes': 'sum',
                'party': 'first'
            }).drop_duplicates(subset=group_cols)
            print(f"   ✓ {csv_file.name} - {len(df)} records (aggregated from precincts)")
        else:
            print(f"   ✓ {csv_file.name} - {len(df)} records")
    
    all_data.append(df)

# 4. Combine all
print("\n4. Combining all files...")
df_final = pd.concat(all_data, ignore_index=True)
print(f"   Combined: {len(df_final)} records, {df_final['votes'].sum():,} votes")

# 5. Standardize and clean
print("\n5. Final standardization...")

# Column names to lowercase
df_final.columns = [col.lower().strip() for col in df_final.columns]

# Remove any remaining header rows
before = len(df_final)
df_final = df_final[~df_final['candidate'].str.contains('  Secretary|President and Vice|General Election|Commonwealth of', case=False, na=False)]
print(f"   Removed {before - len(df_final)} header rows")

# Check results
print("\n6. FINAL RESULTS:")
print(f"   Total records: {len(df_final):,}")
print(f"   Total votes: {df_final['votes'].sum():,}")
print(f"   Counties: {df_final['county'].nunique()}/120")
print(f"   Candidates: {df_final['candidate'].nunique():,}")
print(f"   Years: {sorted(df_final['year'].unique())}")

print("\n   TOP 10:")
top10 = df_final.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
for idx, (name, votes) in enumerate(top10.items(), 1):
    print(f"   {idx:2}. {name:35} {votes:>12,}")

# Save
output_file = data_dir / "KY_ELECTIONS_FINAL_V2.csv"
df_final.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")
