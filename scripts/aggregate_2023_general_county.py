"""
Aggregate 2023 General precinct files to county-level OpenElections format.
"""

from pathlib import Path
import pandas as pd

repo_root = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections_repo")
input_dir = repo_root / "2023" / "General"
output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "KY_2023_GENERAL_COUNTY.csv"

print("=" * 80)
print("AGGREGATE 2023 GENERAL TO COUNTY")
print("=" * 80)

if not input_dir.exists():
    raise FileNotFoundError(f"Missing input directory: {input_dir}")

csv_files = sorted(input_dir.glob("*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in: {input_dir}")

frames = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df.columns = [col.lower().strip() for col in df.columns]
    frames.append(df)

combined = pd.concat(frames, ignore_index=True)

required_cols = ["county", "office", "district", "candidate", "party", "votes"]
missing = [col for col in required_cols if col not in combined.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Normalize nullable fields so groupby does not drop rows.
combined["office"] = combined["office"].fillna("")
combined["district"] = combined["district"].fillna("")
combined["party"] = combined["party"].fillna("")
combined["county"] = combined["county"].fillna("")
combined["candidate"] = combined["candidate"].fillna("")

# Aggregate precinct -> county
agg_cols = ["county", "office", "district", "candidate", "party"]
county_df = combined.groupby(agg_cols, as_index=False)["votes"].sum()

# Add year column
county_df.insert(0, "year", 2023)

# Save
county_df.to_csv(output_file, index=False)

print(f"Input files: {len(csv_files)}")
print(f"Input rows: {len(combined):,}")
print(f"Output rows: {len(county_df):,}")
print(f"Counties: {county_df['county'].nunique()}")
print(f"Total votes: {county_df['votes'].sum():,}")
print(f"Saved: {output_file}")
