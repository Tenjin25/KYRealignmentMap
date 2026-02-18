"""
Validate 2022 county-level results quality.

Checks:
1) County coverage for statewide contests (expects 120 KY counties)
2) U.S. Senate party totals versus certified statewide totals

Usage:
    py scripts/validate_2022_results_quality.py
    py scripts/validate_2022_results_quality.py data/20221108__ky__general__county.csv
"""

from pathlib import Path
import sys
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV = BASE_DIR / "data" / "20221108__ky__general__county.csv"
COUNTY_LOOKUP = BASE_DIR / "data" / "county_name_lookup.csv"

STATEWIDE_OFFICE_TOKENS = [
    "president",
    "u.s. senate",
    "united states senate",
    "us senate",
    "u.s. senator",
    "united states senator",
    "us senator",
    "governor",
    "lieutenant governor",
    "attorney general",
    "secretary of state",
    "state treasurer",
    "treasurer",
    "auditor of public accounts",
    "state auditor",
    "commissioner of agriculture",
]

# Certified statewide totals from the 1.17.2023 certified PDF (U.S. Senate)
CERTIFIED_2022_US_SENATE_TOTALS = {
    "REP": 913326,
    "DEM": 564311,
    "W": 193,  # Charles Lee THOMASON + Billy Ray WILSON
}


def is_statewide_office(office: str) -> bool:
    text = str(office or "").strip().lower()
    return any(tok in text for tok in STATEWIDE_OFFICE_TOKENS)


def main() -> int:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not csv_path.exists():
        print(f"ERROR: missing input CSV: {csv_path}")
        return 1
    if not COUNTY_LOOKUP.exists():
        print(f"ERROR: missing county lookup CSV: {COUNTY_LOOKUP}")
        return 1

    counties = set(
        pd.read_csv(COUNTY_LOOKUP, dtype=str)["county_name"]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )
    expected_counties = len(counties)

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    for col in ["year", "votes", "office", "county", "party", "district"]:
        if col not in df.columns:
            print(f"ERROR: required column missing: {col}")
            return 1

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)
    df_2022 = df[df["year"] == 2022].copy()
    if df_2022.empty:
        print("ERROR: no year=2022 rows found in input CSV")
        return 1

    print(f"Input: {csv_path}")
    print(f"2022 rows: {len(df_2022)}")
    print(f"Expected KY counties: {expected_counties}")
    print()

    # Coverage for statewide offices
    print("Statewide contest coverage:")
    offices = sorted(df_2022["office"].dropna().astype(str).str.strip().unique())
    statewide_offices = [o for o in offices if is_statewide_office(o)]
    if not statewide_offices:
        print("  (no statewide contests found)")
    for office in statewide_offices:
        office_df = df_2022[df_2022["office"].astype(str) == office]
        present = set(office_df["county"].dropna().astype(str).str.strip().unique())
        missing = sorted(counties - present)
        status = "OK" if len(present) == expected_counties else "INCOMPLETE"
        print(f"  - {office}: {len(present)}/{expected_counties} counties [{status}]")
        if missing:
            preview = ", ".join(missing[:12])
            suffix = " ..." if len(missing) > 12 else ""
            print(f"    missing: {preview}{suffix}")

    print()

    # Certified totals check for U.S. Senate
    senate_mask = df_2022["office"].astype(str).str.lower().str.contains("senator", na=False)
    senate_df = df_2022[senate_mask].copy()
    if senate_df.empty:
        print("U.S. Senate totals check: no senator rows found.")
        return 0

    party_totals = senate_df.groupby("party", dropna=False)["votes"].sum().to_dict()
    rep = int(party_totals.get("REP", 0))
    dem = int(party_totals.get("DEM", 0))
    w_total = int(party_totals.get("W", 0))

    print("U.S. Senate totals check (2022):")
    print(f"  REP parsed: {rep:,} | certified: {CERTIFIED_2022_US_SENATE_TOTALS['REP']:,} | diff: {rep - CERTIFIED_2022_US_SENATE_TOTALS['REP']:+,}")
    print(f"  DEM parsed: {dem:,} | certified: {CERTIFIED_2022_US_SENATE_TOTALS['DEM']:,} | diff: {dem - CERTIFIED_2022_US_SENATE_TOTALS['DEM']:+,}")
    print(f"  W   parsed: {w_total:,} | certified: {CERTIFIED_2022_US_SENATE_TOTALS['W']:,} | diff: {w_total - CERTIFIED_2022_US_SENATE_TOTALS['W']:+,}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
