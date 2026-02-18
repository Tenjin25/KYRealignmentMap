"""
Aggregate OpenElections KY precinct CSV files into county-level CSV.

Usage:
    py scripts/aggregate_openelections_precinct_to_county.py 2010
    py scripts/aggregate_openelections_precinct_to_county.py 2010 2011
"""

from pathlib import Path
import sys
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
OE_REPO_DIR = BASE_DIR / "data" / "openelections_repo"
OUT_DIR = BASE_DIR / "data" / "openelections"


def aggregate_year(year: str) -> Path:
    year_dir = OE_REPO_DIR / year
    if not year_dir.exists():
        raise FileNotFoundError(f"Year directory not found: {year_dir}")

    precinct_files = sorted(year_dir.glob("*__ky__general__*__precinct.csv"))
    if not precinct_files:
        raise FileNotFoundError(f"No general precinct CSV files found in: {year_dir}")

    frames = []
    for file in precinct_files:
        df = pd.read_csv(file, dtype=str).fillna("")
        df.columns = [c.lower().strip() for c in df.columns]
        required = {"county", "office", "district", "party", "candidate", "votes"}
        missing = required - set(df.columns)
        if missing:
            print(f"Skipping {file.name}: missing {sorted(missing)}")
            continue
        frames.append(df[list(required)])

    if not frames:
        raise RuntimeError(f"No usable precinct files in: {year_dir}")

    combined = pd.concat(frames, ignore_index=True)
    combined["votes"] = (
        pd.to_numeric(
            combined["votes"].astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )
    combined["year"] = int(year)

    out = (
        combined.groupby(
            ["year", "county", "office", "district", "candidate", "party"],
            dropna=False,
            as_index=False,
        )["votes"]
        .sum()
        .sort_values(["county", "office", "district", "candidate", "party"])
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"KY_{year}_GENERAL_COUNTY.csv"
    out.to_csv(out_path, index=False)
    return out_path


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    years = [arg.strip() for arg in sys.argv[1:] if arg.strip()]
    for year in years:
        path = aggregate_year(year)
        print(f"Created {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
