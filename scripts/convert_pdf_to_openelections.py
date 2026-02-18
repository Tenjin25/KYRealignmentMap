"""
Convert Kentucky election PDF files to OpenElections CSV format.

This script uses tabula to extract tables from PDF files and converts them
to the OpenElections format.

Usage:
    py scripts/convert_pdf_to_openelections.py <pdf_file> <election_date> [level]
    
Example:
    py scripts/convert_pdf_to_openelections.py "data/2012genresults.pdf" 20121106 county
"""

import sys
import os
from pathlib import Path
import re

# Add tools directory to path to import pdf_to_csv
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

try:
    import tabula
    import pandas as pd
    import pdfplumber
except ImportError:
    print("Error: Required libraries not installed.")
    print("Install with: pip install tabula-py pandas pdfplumber")
    sys.exit(1)

try:
    from pdf_to_csv import parse_ky_pdf_tabula, clean_value
except ImportError:
    print("Error: Could not import tools/pdf_to_csv.py")
    sys.exit(1)


def normalize_county_key(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 .-]", "", str(text or ""))
    value = re.sub(r"\s+", " ", value).strip().upper()
    return value


def load_county_lookup() -> dict:
    lookup_path = Path(__file__).resolve().parent.parent / "data" / "county_name_lookup.csv"
    if not lookup_path.exists():
        print(f"Warning: county lookup not found at {lookup_path}")
        return {}

    county_map = {}
    df = pd.read_csv(lookup_path, dtype=str).fillna("")
    for _, row in df.iterrows():
        canonical = str(row.get("county_name", "")).strip()
        if not canonical:
            continue
        keys = {
            normalize_county_key(canonical),
            normalize_county_key(row.get("county_namelsad", "")),
            normalize_county_key(row.get("match_key_normalized", "")),
        }
        no_suffix = re.sub(r"\s+COUNTY$", "", normalize_county_key(canonical))
        if no_suffix:
            keys.add(no_suffix)
        for key in keys:
            if key:
                county_map[key] = canonical
    return county_map


COUNTY_LOOKUP = load_county_lookup()


def canonicalize_county_name(raw_county: str) -> str:
    key = normalize_county_key(raw_county)
    if not key:
        return ""
    if key in COUNTY_LOOKUP:
        return COUNTY_LOOKUP[key]
    no_suffix = re.sub(r"\s+COUNTY$", "", key)
    if no_suffix in COUNTY_LOOKUP:
        return COUNTY_LOOKUP[no_suffix]
    return str(raw_county).strip().title()


def infer_county_from_pdf_name(pdf_path: str) -> str:
    stem = Path(pdf_path).stem
    cleaned = re.sub(r"\s+", " ", stem).strip()
    return canonicalize_county_name(cleaned)


def extract_district_from_office(office_text: str) -> str:
    patterns = [
        r"(\d+)(?:st|nd|rd|th)\s+Congressional District",
        r"(\d+)(?:st|nd|rd|th)\s+Senatorial District",
        r"(\d+)(?:st|nd|rd|th)\s+Representative District",
    ]
    for pattern in patterns:
        m = re.search(pattern, office_text, re.IGNORECASE)
        if m:
            return m.group(1)
    return ""


def parse_sos_precinct_recap_pdf(pdf_path: str, election_date: str) -> pd.DataFrame:
    """
    Parse SOS precinct recap PDFs (e.g. 2022_recaps/*.pdf) by reading text lines and
    aggregating precinct totals into county-level rows.
    """
    county = infer_county_from_pdf_name(pdf_path)
    year = election_date[:4]
    rows = []
    current_office = ""
    current_district = ""

    skip_prefixes = (
        "Choice Party ",
        "Cast Votes:",
        "Undervotes:",
        "Overvotes:",
        "Run Time ",
        "Run Date ",
        "Precinct Results Report",
        "GENERAL ELECTION HELD ON",
        "Ballots Cast",
        "Election Night Reporting",
        "Precincts Reporting",
    )
    party_tokens = {"REP", "DEM", "LIB", "IND", "GRN", "CON", "W", "(W)"}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for raw_line in text.splitlines():
                line = re.sub(r"\s+", " ", raw_line).strip()
                if not line:
                    continue

                if any(line.startswith(prefix) for prefix in skip_prefixes):
                    continue

                # Detect contest header lines
                office_match = re.match(r"^(.*?)\s*-\s*\(Vote for", line, flags=re.IGNORECASE)
                if office_match:
                    current_office = office_match.group(1).strip()
                    current_district = extract_district_from_office(current_office)
                    continue

                if not current_office:
                    continue

                # Must end in percent to be a candidate line in this SOS format
                tokens = line.split()
                if len(tokens) < 5 or not re.fullmatch(r"\d+\.\d+%", tokens[-1]):
                    continue

                # Total votes is the rightmost integer token before final percentage.
                total_votes = None
                for tok in reversed(tokens[:-1]):
                    if re.fullmatch(r"\d[\d,]*", tok):
                        total_votes = int(tok.replace(",", ""))
                        break
                if total_votes is None:
                    continue

                # Candidate + party section is before first numeric token.
                first_numeric_idx = None
                for i, tok in enumerate(tokens):
                    if re.fullmatch(r"\d[\d,]*", tok):
                        first_numeric_idx = i
                        break
                if first_numeric_idx is None or first_numeric_idx < 2:
                    continue

                cand_party_tokens = tokens[:first_numeric_idx]

                party = ""
                party_idx = None
                for i, tok in enumerate(cand_party_tokens):
                    if tok in party_tokens:
                        party_idx = i
                        party = tok
                        break
                if party_idx is None:
                    # Skip lines that don't look like candidate vote lines.
                    continue

                candidate = " ".join(cand_party_tokens[:party_idx]).strip()
                if not candidate:
                    continue

                if party == "(W)":
                    party = "W"

                rows.append({
                    "county": county,
                    "office": current_office,
                    "district": current_district,
                    "candidate": candidate,
                    "party": party,
                    "votes": total_votes,
                    "year": year,
                })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    group_cols = ["county", "office", "district", "candidate", "party", "year"]
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)
    df = df.groupby(group_cols, as_index=False)["votes"].sum()
    return df


def is_sos_precinct_recap(pdf_path: str) -> bool:
    if "recap" in pdf_path.lower():
        return True

    try:
        with pdfplumber.open(pdf_path) as pdf:
            sample = "\n".join((page.extract_text() or "") for page in pdf.pages[:2])
        return (
            "Precinct Results Report" in sample
            and "OFFICIAL BALLOT FOR" in sample
        )
    except Exception:
        return False


def pdf_to_openelections(pdf_path: str, election_date: str, level: str = 'county'):
    """
    Convert a Kentucky election PDF to OpenElections format.
    
    Args:
        pdf_path: Path to the PDF file
        election_date: Date in YYYYMMDD format
        level: 'county' or 'precinct'
    """
    print(f"Converting: {pdf_path}")
    print(f"Election date: {election_date}")
    print(f"Level: {level}")
    print()
    
    # Use SOS text parser for precinct recap PDFs; otherwise use tabula parser.
    if is_sos_precinct_recap(pdf_path):
        print("Extracting data using SOS text parser...")
        df = parse_sos_precinct_recap_pdf(pdf_path, election_date)
    else:
        print("Extracting data using tabula...")
        df = parse_ky_pdf_tabula(pdf_path)
    
    if df.empty:
        print("Warning: No data extracted. The PDF may have a complex layout.")
        print("   Try manually reviewing the PDF structure.")
        return False

    if "county" in df.columns:
        df["county"] = df["county"].map(canonicalize_county_name)
    else:
        df["county"] = ""

    inferred_county = infer_county_from_pdf_name(pdf_path)
    if inferred_county:
        if df["county"].eq("").all():
            df["county"] = inferred_county
        else:
            alpha_ratio = df["county"].astype(str).str.contains(r"[A-Za-z]", regex=True).mean()
            if alpha_ratio < 0.3:
                df["county"] = inferred_county

    print(f"Extracted {len(df)} rows of data")
    print()
    
    year_value = int(election_date[:4])

    # Convert to OpenElections format
    output_filename = f"{election_date}__ky__general__{level}.csv"
    output_path = Path('data') / output_filename
    
    # The OpenElections format requires specific columns
    required_columns = [
        'year', 'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    if level == 'precinct':
        required_columns.insert(1, 'precinct')
    
    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''  # Add missing columns
    df['year'] = year_value
    
    # Select and reorder columns
    output_df = df[required_columns]
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    
    print(f"Created: {output_path}")
    print(f"  {len(output_df)} rows")
    
    # Show a preview
    print("\nPreview (first 5 rows):")
    print(output_df.head().to_string(index=False))
    
    return True


def directory_to_openelections(pdf_dir: str, election_date: str, level: str = "county"):
    """
    Convert all PDFs in a directory and merge into one OpenElections county CSV.
    """
    pdf_paths = sorted(Path(pdf_dir).glob("*.pdf"))
    if not pdf_paths:
        print(f"Error: No PDF files found in {pdf_dir}")
        return False

    print(f"Converting directory: {pdf_dir}")
    print(f"Election date: {election_date}")
    print(f"Level: {level}")
    print(f"PDF files: {len(pdf_paths)}")
    print()

    all_frames = []
    for i, pdf in enumerate(pdf_paths, 1):
        print(f"[{i}/{len(pdf_paths)}] {pdf.name}")
        if is_sos_precinct_recap(str(pdf)):
            df = parse_sos_precinct_recap_pdf(str(pdf), election_date)
        else:
            df = parse_ky_pdf_tabula(str(pdf))
            if "county" in df.columns:
                df["county"] = df["county"].map(canonicalize_county_name)
            else:
                df["county"] = infer_county_from_pdf_name(str(pdf))

        if not df.empty:
            all_frames.append(df)

    if not all_frames:
        print("Warning: No rows extracted from directory PDFs.")
        return False

    merged = pd.concat(all_frames, ignore_index=True)
    merged["votes"] = pd.to_numeric(merged["votes"], errors="coerce").fillna(0).astype(int)
    merged["year"] = int(election_date[:4])
    merged = (
        merged.groupby(
            ["year", "county", "office", "district", "candidate", "party"],
            as_index=False,
            dropna=False,
        )["votes"]
        .sum()
    )

    output_filename = f"{election_date}__ky__general__{level}.csv"
    output_path = Path("data") / output_filename

    required_columns = [
        "year", "county", "office", "district", "candidate", "party", "votes",
        "election_day", "absentee", "av_counting_boards", "early_voting",
        "mail", "provisional", "pre_process_absentee",
    ]
    for col in required_columns:
        if col not in merged.columns:
            merged[col] = ""
    output_df = merged[required_columns]
    output_df.to_csv(output_path, index=False)

    print()
    print(f"Created: {output_path}")
    print(f"Rows: {len(output_df)}")
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    
    pdf_file = sys.argv[1]
    election_date = sys.argv[2]
    level = sys.argv[3] if len(sys.argv) > 3 else 'county'
    
    # Validate inputs
    input_path = Path(pdf_file)
    if not input_path.exists():
        print(f"Error: File or directory not found: {pdf_file}")
        return
    
    if len(election_date) != 8 or not election_date.isdigit():
        print(f"Error: Invalid date format. Expected YYYYMMDD, got: {election_date}")
        return
    
    if level not in ['county', 'precinct']:
        print(f"Error: Invalid level. Expected 'county' or 'precinct', got: {level}")
        return
    
    if input_path.is_dir():
        success = directory_to_openelections(pdf_file, election_date, level)
    else:
        success = pdf_to_openelections(pdf_file, election_date, level)
    
    if not success:
        print("\nNote: PDF extraction can be tricky. For complex PDFs:")
        print("  1. Try opening the PDF and checking its structure")
        print("  2. Use tools/pdf_to_csv.py directly for more control")
        print("  3. Consider manual extraction to Excel/CSV first")


if __name__ == '__main__':
    main()
