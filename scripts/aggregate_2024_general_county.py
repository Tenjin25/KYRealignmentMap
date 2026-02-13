"""
Aggregate 2024 General statewide precinct data to county-level OpenElections format.
"""

from pathlib import Path
import pandas as pd

repo_root = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections_repo")
input_file = repo_root / "2024" / "20241105__ky__general__precinct.csv"
output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "KY_2024_GENERAL_COUNTY.csv"

print("=" * 80)
print("AGGREGATE 2024 GENERAL TO COUNTY")
print("=" * 80)

if not input_file.exists():
    raise FileNotFoundError(f"Missing input file: {input_file}")

df = pd.read_csv(input_file)
df.columns = [col.lower().strip() for col in df.columns]

required_cols = ["county", "office", "district", "candidate", "party", "votes"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Normalize nullable fields so groupby does not drop rows.
df["office"] = df["office"].fillna("")
df["district"] = df["district"].fillna("")
df["party"] = df["party"].fillna("")
df["county"] = df["county"].fillna("")
df["candidate"] = df["candidate"].fillna("")

# Aggregate precinct -> county
agg_cols = ["county", "office", "district", "candidate", "party"]
df_county = df.groupby(agg_cols, as_index=False)["votes"].sum()

# Add year column

df_county.insert(0, "year", 2024)

# Save

df_county.to_csv(output_file, index=False)

print(f"Input rows: {len(df):,}")
print(f"Output rows: {len(df_county):,}")
print(f"Counties: {df_county['county'].nunique()}")
print(f"Total votes: {df_county['votes'].sum():,}")
print(f"Saved: {output_file}")
