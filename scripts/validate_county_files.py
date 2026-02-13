"""
Validate generated county-level OpenElections files for duplicates.
Checks for duplicate keys per file: year, county, office, district, candidate, party.
"""

from pathlib import Path
import pandas as pd

output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")

files = sorted(output_dir.glob("KY_*_GENERAL_COUNTY.csv"))

print("=" * 80)
print("VALIDATE COUNTY FILES")
print("=" * 80)

if not files:
    print("No county files found in:", output_dir)
    raise SystemExit(1)

key_cols = ["year", "county", "office", "district", "candidate", "party"]

for csv_file in files:
    df = pd.read_csv(csv_file)
    df.columns = [col.lower().strip() for col in df.columns]

    missing = [col for col in key_cols if col not in df.columns]
    if missing:
        print(f"\n{csv_file.name}: missing columns {missing}")
        continue

    dupes = df[df.duplicated(subset=key_cols, keep=False)]
    print(f"\n{csv_file.name}:")
    print(f"  rows: {len(df):,}")
    print(f"  duplicates: {len(dupes):,}")

    if len(dupes) > 0:
        # Show a sample to inspect
        sample = dupes[key_cols + ["votes"]].head(10)
        print("  sample duplicates:")
        print(sample.to_string(index=False))

print("\nDone.")
