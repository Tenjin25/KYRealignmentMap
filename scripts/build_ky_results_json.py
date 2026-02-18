"""
Build a KY election results JSON from county-level OpenElections files and historical txt files.
Applies margin calculations using the legend criteria.
"""

from pathlib import Path
import json
import pandas as pd
import re

input_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")
output_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/ky_election_results.json")
county_lookup_file = input_dir / "county_name_lookup.csv"

# Collect both CSV and TXT files
csv_patterns = [
    "openelections/KY_*_GENERAL_COUNTY.csv",
    "*__ky__general__county.csv",
]
csv_files = sorted({p for pattern in csv_patterns for p in input_dir.glob(pattern)})

# Find txt files more explicitly
txt_files = []
for txt_candidate in [
    "00Gen_Statewidebycounty.txt",
    "2002statebycounty.txt", 
    "2003statewidebycounty.txt",
    "2004statebyCOUNTY.txt",
    "2006STATEwidebycounty.txt",
    "2007statewidebyCOUNTY.txt",
    "STATEwide by candidate by county gen 08.txt"
]:
    candidate_path = input_dir / txt_candidate
    if candidate_path.exists():
        txt_files.append(candidate_path)

all_dataframes = []


def normalize_county_key(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 .-]", "", str(text or ""))
    value = re.sub(r"\s+", " ", value).strip()
    return value


def load_county_lookup(path: Path) -> tuple[dict, dict]:
    """Load county lookup CSV and return (normalized_name_map, abbr_map)."""
    if not path.exists():
        raise FileNotFoundError(f"County lookup not found: {path}")

    df = pd.read_csv(path, dtype=str).fillna("")
    required_cols = {"county_name", "county_namelsad", "match_key_normalized"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"county_name_lookup.csv missing columns: {sorted(missing)}")

    normalized_map = {}
    abbr_map = {}

    for _, row in df.iterrows():
        county_name = str(row["county_name"]).strip()
        if not county_name:
            continue

        keys = {
            normalize_county_key(county_name),
            normalize_county_key(row["county_namelsad"]),
            normalize_county_key(row["match_key_normalized"]),
        }
        county_no_suffix = re.sub(r"\s+COUNTY$", "", normalize_county_key(county_name))
        if county_no_suffix:
            keys.add(county_no_suffix)

        for key in keys:
            if key:
                normalized_map[key] = county_name

        # Default 4-char abbreviation used in historical TXT county headers
        alpha = re.sub(r"[^A-Z]", "", county_name.upper())
        if len(alpha) >= 4:
            abbr_map.setdefault(alpha[:4], county_name.title())

    # Known SOS/TXT abbreviation quirks
    abbr_map.update({
        "GREU": "Greenup",
        "KENT": "Kenton",
        "MASO": "Mason",
        "MCCK": "McCracken",
        "MCCR": "McCreary",
        "MCLE": "McLean",
    })

    # Known spelling/label variants seen in legacy files
    normalized_map[normalize_county_key("Breckenridge")] = "Breckinridge"
    normalized_map[normalize_county_key("Bulter")] = "Butler"

    return normalized_map, abbr_map


COUNTY_NORMALIZED_MAP, COUNTY_ABBR_MAP = load_county_lookup(county_lookup_file)


def canonicalize_county_name(raw_county: str) -> str:
    key = normalize_county_key(raw_county)
    if not key:
        return ""

    if key in COUNTY_NORMALIZED_MAP:
        return COUNTY_NORMALIZED_MAP[key]

    no_suffix = re.sub(r"\s+COUNTY$", "", key)
    if no_suffix in COUNTY_NORMALIZED_MAP:
        return COUNTY_NORMALIZED_MAP[no_suffix]

    # Stop capping all last names, just return as-is
    return str(raw_county).strip()


def party_bucket(party: str) -> str:
    if not isinstance(party, str):
        return "other"
    p = party.strip().upper()
    if p in {"DEM", "DEMOCRAT", "D"}:
        return "dem"
    if p in {"REP", "REPUBLICAN", "R", "GOP"}:
        return "rep"
    return "other"


def get_competitiveness(margin_pct: float, winner_party: str) -> dict:
    """Map margin percentage to competitiveness category with color."""
    colors = {
        "Annihilation": {"REP": "#67000d", "DEM": "#08306b"},
        "Dominant": {"REP": "#a50f15", "DEM": "#08519c"},
        "Stronghold": {"REP": "#cb181d", "DEM": "#3182bd"},
        "Safe": {"REP": "#ef3b2c", "DEM": "#6baed6"},
        "Likely": {"REP": "#fb6a4a", "DEM": "#9ecae1"},
        "Lean": {"REP": "#fcae91", "DEM": "#c6dbef"},
        "Tilt": {"REP": "#fee8c8", "DEM": "#e1f5fe"},
        "Tossup": {"REP": "#f7f7f7", "DEM": "#f7f7f7"},
    }
    
    code_parts = {
        "Annihilation": "ANNIHILATION",
        "Dominant": "DOMINANT",
        "Stronghold": "STRONGHOLD",
        "Safe": "SAFE",
        "Likely": "LIKELY",
        "Lean": "LEAN",
        "Tilt": "TILT",
        "Tossup": "TOSSUP",
    }
    
    if margin_pct >= 40:
        category = "Annihilation"
    elif margin_pct >= 30:
        category = "Dominant"
    elif margin_pct >= 20:
        category = "Stronghold"
    elif margin_pct >= 10:
        category = "Safe"
    elif margin_pct >= 5.50:
        category = "Likely"
    elif margin_pct >= 1.00:
        category = "Lean"
    elif margin_pct >= 0.50:
        category = "Tilt"
    else:
        category = "Tossup"
    
    code = f"{winner_party}_{code_parts[category]}"
    
    return {
        "category": category,
        "party": winner_party,
        "code": code,
        "color": colors[category][winner_party]
    }


def get_contest_name(office: str) -> str:
    """Convert office to friendly contest name."""
    office_lower = (office or "").strip().lower()
    
    if "president" in office_lower:
        return "President"
    elif "senate" in office_lower:
        return "U.S. Senate"
    elif "governor" in office_lower:
        if "lieutenant" in office_lower:
            return "Lieutenant Governor"
        return "Governor"
    elif "attorney" in office_lower:
        return "Attorney General"
    elif "secretary" in office_lower:
        return "Secretary of State"
    elif "treasurer" in office_lower:
        return "State Treasurer"
    elif "auditor" in office_lower:
        return "Auditor of Public Accounts"
    elif "agriculture" in office_lower or "commissioner" in office_lower:
        return "Commissioner of Agriculture"
    else:
        return office


def guess_party(candidate: str) -> str:
    """Heuristically guess party from candidate info (for historical txt data)."""
    name_lower = (candidate or "").lower()
    dem_names = {
        # National
        "gore", "lieberman", "weinberg", "mondale", "ferraro", "dukakis", 
        "bentsen", "clinton", "kerry", "edwards", "obama", "biden",
        "harris", "waltz", "robinson", "combs", "grimes", "adkins",
        # 2003 KY statewide
        "chandler", "owen", "maple", "stumbo", "luallen", "miller", "baesler",
        # 2007 KY statewide
        "beshear", "mongiardo", "hendrickson", "conway", "luallen", "hollenbach", "williams",
        # 2008 US Senate
        "lunsford",
    }
    rep_names = {
        # National
        "bush", "cheney", "dole", "kemp", "reagan", "quayle", "mccain",
        "palin", "romney", "ryan", "trump", "pence", "mcconnell", "nolan",
        "williams", "forgy", "bunning",
        # 2003 KY statewide
        "fletcher", "pence", "grayson", "wood", "greenwell", "koenig", "farmer",
        # 2007 KY statewide
        "fletcher", "rudolph", "grayson", "lee", "greenwell", "wheeler", "farmer",
    }
    
    for dem in dem_names:
        if dem in name_lower:
            return "DEM"
    for rep in rep_names:
        if rep in name_lower:
            return "REP"
    return "OTHER"


def parse_txt_file(filepath: Path) -> pd.DataFrame:
    """Parse Kentucky election txt files with county-by-candidate format."""
    filename = filepath.stem.lower()
    filename_full = filepath.name.lower()
    
    # Extract year from filename
    if "00gen" in filename or "2000" in filename_full:
        year = 2000
    elif "2002" in filename_full:
        year = 2002
    elif "2003" in filename_full:
        year = 2003
    elif "2004" in filename_full:
        year = 2004
    elif "2006" in filename_full:
        year = 2006
    elif "2007" in filename_full:
        year = 2007
    elif "2008" in filename_full or "08" in filename_full:
        year = 2008
    else:
        return pd.DataFrame()
    
    rows = []
    try:
        with open(filepath, 'r', encoding='latin-1', errors='ignore') as f:
            content = f.read()
    except:
        return pd.DataFrame()
    
    lines = content.split('\n')
    current_office = None
    county_order = []
    
    for i, line in enumerate(lines):
        # Extract office - handle multi-line office names
        if 'OFFICE:' in line:
            # Extract everything after "OFFICE: A##/###/###"
            match = re.search(r'OFFICE:\s+[A-Z0-9/]+\s+(.*)', line)
            if match:
                office_part = match.group(1).strip()
                # If line continues to next, append it
                if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip()[0].isupper() and '*' not in lines[i + 1]:
                    office_part += " " + lines[i + 1].strip()
                current_office = office_part
                county_order = []
        
        # Find county header line (contains *ABBR patterns)
        if line.strip() and '*' in line and (line.count('*') >= 3):
            parts = line.split()
            county_order = []
            for p in parts:
                if p.startswith('*'):
                    abbr = re.sub(r"[^A-Z0-9]", "", p[1:].upper())
                    county_name = COUNTY_ABBR_MAP.get(abbr, abbr.title())
                    county_order.append(county_name.title())
        
        # Parse vote lines (candidate + numbers)
        if current_office and county_order and line.strip() and not 'OFFICE' in line:
            parts = line.split()
            
            # Need at least candidate name + county count numbers
            if len(parts) >= len(county_order):
                # Check if last N items are numbers
                vote_nums = parts[-len(county_order):]
                
                try:
                    # Try to parse all as integers
                    votes = []
                    for v in vote_nums:
                        # Handle commas in numbers
                        clean_v = v.replace(',', '')
                        votes.append(int(clean_v))
                    
                    # Success - this is a vote line
                    candidate = ' '.join(parts[:-len(county_order)]).strip().title()
                    
                    # Filter out blank lines and headers
                    if candidate and len(candidate) > 1:
                        party = guess_party(candidate)
                        for county_name, vote_count in zip(county_order, votes):
                            canonical_county = canonicalize_county_name(county_name)
                            if vote_count > 0 and canonical_county:  # Only add non-zero votes
                                rows.append({
                                    'year': year,
                                    'county': canonical_county,
                                    'office': current_office,
                                    'district': '',
                                    'candidate': candidate,
                                    'party': party,
                                    'votes': vote_count
                                })
                except (ValueError, IndexError):
                    # Not a vote line, skip
                    pass
    
    return pd.DataFrame(rows)


# Parse CSV files
for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    df.columns = [col.lower().strip() for col in df.columns]
    required = ["year", "county", "office", "district", "candidate", "party", "votes"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        print(f"Warning: {csv_file.name} missing columns: {missing}")
        continue
    # Normalize party values using party_bucket
    df["party"] = df["party"].apply(party_bucket)
    # Stop uppercasing all candidate last names (leave as-is)
    all_dataframes.append(df)

# Parse TXT files
for txt_file in txt_files:
    print(f"Parsing {txt_file.name}...")
    df = parse_txt_file(txt_file)
    if not df.empty:
        all_dataframes.append(df)
        print(f"  -> {len(df)} rows extracted")

# Combine all data
if not all_dataframes:
    raise SystemExit("No data files found!")

combined_df = pd.concat(all_dataframes, ignore_index=True)
combined_df["county"] = combined_df["county"].map(canonicalize_county_name)
combined_df = combined_df[combined_df["county"].astype(str).str.strip() != ""].copy()
combined_df["votes"] = (
    pd.to_numeric(
        combined_df["votes"].astype(str).str.replace(",", "", regex=False),
        errors="coerce",
    )
    .fillna(0)
    .astype(int)
)
combined_df["year"] = pd.to_numeric(combined_df["year"], errors="coerce")
combined_df = combined_df.dropna(subset=["year"]).copy()
combined_df["year"] = combined_df["year"].astype(int)

# List of statewide offices
STATEWIDE_OFFICES = [
    "president",
    "u.s. senate", "united states senate", "us senate",
    "u.s. senator", "united states senator", "us senator",
    "governor", "lieutenant governor", "attorney general",
    "secretary of state", "state treasurer", "treasurer",
    "auditor of public accounts", "state auditor",
    "commissioner of agriculture",
]

def is_statewide_office(office: str) -> bool:
    text = (office or "").strip().lower()
    return any(token in text for token in STATEWIDE_OFFICES)

results_by_year = {}

for _, row in combined_df.iterrows():
    year = int(row["year"])
    county = str(row["county"]).strip()
    office = str(row["office"]).strip()
    district = str(row["district"]).strip() if pd.notna(row.get("district")) else ""
    candidate = str(row["candidate"]).strip().title()
    party = str(row["party"]).strip()
    votes = int(row["votes"]) if pd.notna(row["votes"]) else 0

    # Skip non-candidate rows
    skip_candidates = {"", "Over Votes", "Under Votes", "Total Votes"}
    if candidate in skip_candidates or party == "":
        continue

    if not is_statewide_office(office):
        continue

    contest_key = office if not district else f"{office} - {district}"

    results_by_year.setdefault(str(year), {})
    results_by_year[str(year)].setdefault(office or "Unknown", {})
    contest = results_by_year[str(year)][office or "Unknown"].setdefault(contest_key, {"results": {}})

    county_results = contest["results"].setdefault(
        county,
        {
            "contest_name": get_contest_name(office),
            "year": year,
            "county": county,
            "dem_votes": 0,
            "rep_votes": 0,
            "other_votes": 0,
            "total_votes": 0,
            "two_party_total": 0,
            "dem_candidate": "",
            "rep_candidate": "",
            "winner": "",
            "margin": 0,
            "margin_pct": 0,
            "competitiveness": {},
            "all_parties": {},
        },
    )

    bucket = party_bucket(party)
    if bucket == "dem":
        county_results["dem_votes"] += votes
        if votes > county_results.get("_dem_max", 0):
            county_results["_dem_max"] = votes
            county_results["dem_candidate"] = candidate
    elif bucket == "rep":
        county_results["rep_votes"] += votes
        if votes > county_results.get("_rep_max", 0):
            county_results["_rep_max"] = votes
            county_results["rep_candidate"] = candidate
    else:
        county_results["other_votes"] += votes

    county_results["total_votes"] += votes

# Finalize margins
for year_data in results_by_year.values():
    for contests in year_data.values():
        for contest in contests.values():
            for county, data in contest["results"].items():
                dem = data["dem_votes"]
                rep = data["rep_votes"]
                other = data["other_votes"]
                total = data["total_votes"]
                
                two_party_total = dem + rep
                data["two_party_total"] = two_party_total
                
                all_parties = {}
                if dem > 0:
                    all_parties["DEM"] = dem
                if rep > 0:
                    all_parties["REP"] = rep
                if other > 0:
                    all_parties["OTHER"] = other
                data["all_parties"] = all_parties
                
                margin = dem - rep
                data["margin"] = margin
                data["margin_pct"] = round((abs(margin) / total) * 100, 2) if total else 0
                
                if dem > rep:
                    data["winner"] = "DEM"
                    data["competitiveness"] = get_competitiveness(data["margin_pct"], "DEM")
                elif rep > dem:
                    data["winner"] = "REP"
                    data["competitiveness"] = get_competitiveness(data["margin_pct"], "REP")
                else:
                    data["winner"] = "TIE"
                    data["competitiveness"] = {
                        "category": "Tossup",
                        "party": "TIE",
                        "code": "TIE_TOSSUP",
                        "color": "#f7f7f7"
                    }

                data.pop("_dem_max", None)
                data.pop("_rep_max", None)

output = {"results_by_year": results_by_year}
output_file.write_text(json.dumps(output, indent=2))

print("=" * 80)
print("KY RESULTS JSON BUILT (CSV + TXT)")
print("=" * 80)
print(f"Years: {sorted(results_by_year.keys())}")
print(f"Saved: {output_file}")
