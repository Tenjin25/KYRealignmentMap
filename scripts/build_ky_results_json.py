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

# Collect both CSV and TXT files
csv_files = sorted(input_dir.glob("openelections/KY_*_GENERAL_COUNTY.csv"))

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


def party_bucket(party: str) -> str:
    p = (party or "").strip().upper()
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
    dem_names = {"gore", "lieberman", "weinberg", "mondale", "ferraro", "dukakis", 
                 "bentsen", "clinton", "kerry", "edwards", "obama", "biden",
                 "harris", "waltz", "robinson", "combs", "grimes", "adkins"}
    rep_names = {"bush", "cheney", "dole", "kemp", "reagan", "quayle", "mccain",
                 "palin", "romney", "ryan", "trump", "pence", "mcconnell", "nolan",
                 "williams", "forgy", "bunning"}
    
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
    
    # Simple county abbreviation mapping - Kentucky counties
    county_map = {
        "ADAI": "Adair", "ALLE": "Allegany", "ANDE": "Anderson", "BALL": "Ballard", "BARR": "Barren",
        "BATH": "Bath", "BELL": "Bell", "BOON": "Boone", "BOUR": "Bourbon", "BOYD": "Boyd",
        "BOYL": "Boyle", "BRAC": "Bracken", "BREA": "Breathitt", "BREC": "Breckenridge", "BULL": "Bullitt",
        "BUTL": "Butler", "CALD": "Caldwell", "CALL": "Calloway", "CAMP": "Campbell", "CARL": "Carlisle",
        "CARR": "Carroll", "CART": "Carter", "CASE": "Casey", "CHRI": "Christian", "CLAR": "Clark",
        "CLAY": "Clay", "CLIN": "Clinton", "CRIT": "Crittenden", "CUMB": "Cumberland", "DAVI": "Daviess",
        "DIXO": "Dixon", "FAYE": "Fayette", "FLEM": "Fleming", "FLOY": "Floyd", "FRAN": "Franklin",
        "FULT": "Fulton", "GALL": "Gallatin", "GRAN": "Grant", "GRAV": "Graves", "GRAY": "Grayson",
        "GREE": "Green", "HARL": "Harlan", "HARR": "Harrison", "HART": "Hart", "HEND": "Henderson",
        "HENR": "Henry", "HOPL": "Hopkins", "HOUR": "Houston", "JACK": "Jackson", "JEFF": "Jefferson",
        "JESS": "Jessamine", "JOHN": "Johnson", "KATE": "Kenton", "KNOW": "Knox", "LAUR": "Laurel",
        "LAWS": "Lawrence", "LEES": "Lee", "LESL": "Leslie", "LETT": "Letcher", "LEWI": "Lewis",
        "LIND": "Lincoln", "LIVE": "Livingston", "LOGA": "Logan", "LYON": "Lyon", "MADI": "Madison",
        "MARI": "Marion", "MARS": "Marshall", "MART": "Martin", "MERC": "Mercer", "MIDD": "Middleton",
        "MONT": "Montgomery", "MORG": "Morgan", "MUHL": "Muhlenberg", "NELS": "Nelson", "NICK": "Nicholas",
        "OHIO": "Ohio", "OLDH": "Oldham", "OWEL": "Owen", "OWSL": "Owsley", "PEND": "Pendleton",
        "PERR": "Perry", "PIKE": "Pike", "POLL": "Polk", "POWE": "Powell", "PULA": "Pulaski",
        "ROBA": "Robertson", "ROCK": "Rockcastle", "ROWA": "Rowan", "RUSS": "Russell", "SCOT": "Scott",
        "SHEL": "Shelby", "SIMP": "Simpson", "SPEN": "Spencer", "TAYL": "Taylor", "TODD": "Todd",
        "TRIG": "Trigg", "TRIM": "Trimble", "UNIO": "Union", "WARR": "Warren", "WASH": "Washington",
        "WAYN": "Wayne", "WEBS": "Webster", "WHIT": "Whitley", "WOLF": "Wolfe", "WOOD": "Woodford",
    }
    
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
                    abbr = p[1:].strip()
                    county_name = county_map.get(abbr, abbr)
                    county_order.append(county_name)
        
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
                    candidate = ' '.join(parts[:-len(county_order)]).strip()
                    
                    # Filter out blank lines and headers
                    if candidate and len(candidate) > 1:
                        party = guess_party(candidate)
                        for county_name, vote_count in zip(county_order, votes):
                            if vote_count > 0:  # Only add non-zero votes
                                rows.append({
                                    'year': year,
                                    'county': county_name,
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
    all_dataframes.append(df)

# Parse TXT files
for txt_file in txt_files:
    print(f"Parsing {txt_file.name}...")
    df = parse_txt_file(txt_file)
    if not df.empty:
        all_dataframes.append(df)
        print(f"  → {len(df)} rows extracted")

# Combine all data
if not all_dataframes:
    raise SystemExit("No data files found!")

combined_df = pd.concat(all_dataframes, ignore_index=True)

# List of statewide offices
STATEWIDE_OFFICES = [
    "president", "u.s. senate", "united states senate", "us senate",
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
    candidate = str(row["candidate"]).strip()
    party = str(row["party"]).strip()
    votes = int(row["votes"]) if pd.notna(row["votes"]) else 0

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
