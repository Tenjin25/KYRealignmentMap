"""
Aggregate General precinct files to county-level OpenElections format for multiple years.
Uses local OpenElections repo clone.
"""

from pathlib import Path
import pandas as pd

repo_root = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections_repo")
output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")
output_dir.mkdir(exist_ok=True)

years = [2019, 2018, 2016, 2015, 2014, 2012, 2011, 2010]

print("=" * 80)
print("AGGREGATE GENERAL YEARS TO COUNTY")
print("=" * 80)


def load_year_files(year_dir: Path) -> list:
    files = []

    general_dir = year_dir / "General"
    if general_dir.exists():
        files.extend(sorted(general_dir.glob("*.csv")))

    # Look for statewide precinct files at year root.
    files.extend(sorted(year_dir.glob("*__ky__general__precinct.csv")))

    # Some years may store precinct files at year root without double underscores.
    files.extend(sorted(year_dir.glob("*general*precinct*.csv")))

    # De-duplicate while preserving order.
    seen = set()
    unique = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def aggregate_year(year: int) -> None:
    year_dir = repo_root / str(year)
    if not year_dir.exists():
        print(f"\n{year}: folder not found")
        return

    files = load_year_files(year_dir)
    if not files:
        print(f"\n{year}: no General precinct files found")
        return

    frames = []
    for csv_file in files:
        try:
            df = pd.read_csv(csv_file)
            df.columns = [col.lower().strip() for col in df.columns]
            frames.append(df)
        except Exception as exc:
            print(f"  {year}: failed to read {csv_file.name}: {exc}")

    if not frames:
        print(f"\n{year}: no readable files")
        return

    combined = pd.concat(frames, ignore_index=True)

    required_cols = ["county", "office", "district", "candidate", "party", "votes"]
    missing = [col for col in required_cols if col not in combined.columns]
    if missing:
        print(f"\n{year}: missing columns {missing}")
        return

    # Normalize nullable fields so groupby does not drop rows.
    combined["office"] = combined["office"].fillna("")
    combined["district"] = combined["district"].fillna("")
    combined["party"] = combined["party"].fillna("")
    combined["county"] = combined["county"].fillna("")
    combined["candidate"] = combined["candidate"].fillna("")

    agg_cols = ["county", "office", "district", "candidate", "party"]
    county_df = combined.groupby(agg_cols, as_index=False)["votes"].sum()
    county_df.insert(0, "year", year)

    output_file = output_dir / f"KY_{year}_GENERAL_COUNTY.csv"
    county_df.to_csv(output_file, index=False)

    print(f"\n{year}:")
    print(f"  input files: {len(files)}")
    print(f"  input rows: {len(combined):,}")
    print(f"  output rows: {len(county_df):,}")
    print(f"  counties: {county_df['county'].nunique()}")
    print(f"  total votes: {county_df['votes'].sum():,}")
    print(f"  saved: {output_file}")


for year in years:
    aggregate_year(year)

print("\nDone.")
