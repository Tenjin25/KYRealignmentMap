"""
Create office-specific county files from existing KY_*_GENERAL_COUNTY.csv files.
Outputs per year:
- KY_{year}_PRESIDENT_COUNTY.csv
- KY_{year}_US_SENATE_COUNTY.csv (when present)
- KY_{year}_STATEWIDE_COUNTY.csv (Gov/AG/SOS/etc.)
"""

from pathlib import Path
import pandas as pd
import re

output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")

files = sorted(output_dir.glob("KY_*_GENERAL_COUNTY.csv"))

print("=" * 80)
print("FILTER OFFICE-SPECIFIC COUNTY FILES")
print("=" * 80)

if not files:
    print("No county files found in:", output_dir)
    raise SystemExit(1)

# Office matchers (case-insensitive)
PRESIDENT_RE = re.compile(
    r"^\s*president\s*$|president\s+and\s+vice\s+president|president\s*/\s*vice\s+president",
    re.IGNORECASE,
)
US_SENATE_RE = re.compile(
    r"u\.s\.\s*senate|united\s+states\s+senate|us\s+senate|u\.s\.\s+senator|united\s+states\s+senator",
    re.IGNORECASE,
)

STATEWIDE_RE = re.compile(
    r"\bgovernor\b|\blieutenant\s+governor\b|attorney\s+general|secretary\s+of\s+state|"
    r"state\s+treasurer|treasurer|auditor\s+of\s+public\s+accounts|state\s+auditor|"
    r"commissioner\s+of\s+agriculture|agriculture\s+commissioner",
    re.IGNORECASE,
)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [col.lower().strip() for col in df.columns]
    return df


def write_if_any(df: pd.DataFrame, path: Path, label: str) -> None:
    if df.empty:
        print(f"  {label}: no rows")
        return
    df.to_csv(path, index=False)
    print(f"  {label}: {len(df):,} rows -> {path.name}")


for csv_file in files:
    df = normalize_columns(pd.read_csv(csv_file))

    required_cols = ["year", "county", "office", "district", "candidate", "party", "votes"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        print(f"\n{csv_file.name}: missing columns {missing}")
        continue

    year = int(df["year"].iloc[0])
    print(f"\n{year}:")

    # President only
    pres_df = df[df["office"].apply(lambda x: bool(PRESIDENT_RE.search(str(x))))]
    pres_out = output_dir / f"KY_{year}_PRESIDENT_COUNTY.csv"
    write_if_any(pres_df, pres_out, "President")

    # U.S. Senate when applicable
    us_senate_df = df[df["office"].apply(lambda x: bool(US_SENATE_RE.search(str(x))))]
    us_senate_out = output_dir / f"KY_{year}_US_SENATE_COUNTY.csv"
    write_if_any(us_senate_df, us_senate_out, "U.S. Senate")

    # Statewide offices
    statewide_df = df[df["office"].apply(lambda x: bool(STATEWIDE_RE.search(str(x))))]
    statewide_out = output_dir / f"KY_{year}_STATEWIDE_COUNTY.csv"
    write_if_any(statewide_df, statewide_out, "Statewide")

print("\nDone.")
