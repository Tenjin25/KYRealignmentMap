"""
Convert Kentucky election data to OpenElections CSV format.

This script handles various input formats and normalizes them to the standard
OpenElections format used by the OpenElections project.

OpenElections County Format:
    county,office,district,candidate,party,votes,election_day,absentee,
    av_counting_boards,early_voting,mail,provisional,pre_process_absentee

OpenElections Precinct Format:
    county,precinct,office,district,candidate,party,votes,election_day,absentee,
    av_counting_boards,early_voting,mail,provisional,pre_process_absentee
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    import tabula
    import pandas as pd
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    print("Warning: tabula-py not installed. PDF parsing will not be available.")
    print("Install with: pip install tabula-py")


class OpenElectionsFormatter:
    """Convert election data to OpenElections CSV format."""
    
    COUNTY_HEADERS = [
        'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    PRECINCT_HEADERS = [
        'county', 'precinct', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    def __init__(self, output_dir: str = 'data'):
        """Initialize the formatter with an output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Known candidate to party mappings
        self.party_mappings = {
            # 2000 Presidential
            'Gore & Lieberman': 'DEM',
            'Bush & Cheney': 'REP',
            'Hagelin & Goldhaber': 'NAT',
            'Browne & Olivier': 'LIB',
            'Buchanan & Foster': 'REF',
            'Nader & LaDuke': 'GRN',
            
            # 2002 Senate
            'Mitch McConnell': 'REP',
            'Lois Combs Weinberg': 'DEM',
            
            # 2004 Presidential
            'Bush & Cheney': 'REP',
            'Kerry & Edwards': 'DEM',
            'Badnarik & Campagna': 'LIB',
            'Peroutka & Baldwin': 'CON',
            'Cobb & LaMarche': 'GRN',
            
            # 2008 Presidential
            'McCain & Palin': 'REP',
            'Obama & Biden': 'DEM',
            'Nader & Gonzalez': 'IND',
            'Baldwin & Thornsberry': 'CON',
            'Barr & Root': 'LIB',
            
            # Common Kentucky politicians - US House
            'Edward Whitfield': 'REP',
            'Klint Alexander': 'DEM',
            'Ron Lewis': 'REP',
            'David L. Williams': 'DEM',
            'Anne Northup': 'REP',
            'Jack Conway': 'DEM',
            'Tony Page': 'DEM',
            'Ben Chandler': 'DEM',
            'Nick Carter': 'REP',
            'Tom Buford': 'REP',
            'Ken Lucas': 'DEM',
            'Geoff Davis': 'REP',
            'Nick Clooney': 'DEM',
            'Hal Rogers': 'REP',
            'Sidney Jane Bailey-Burchett': 'DEM',
            'Ernie Fletcher': 'REP',
            'Scotty Baesler': 'DEM',
            
            # Gubernatorial
            'Steve Beshear': 'DEM',
            'Ernie Fletcher': 'REP',
            'Paul Patton': 'DEM',
            'Peppy Martin': 'REP',
            'Gatewood Galbraith': 'REF',
            
            # Other statewide
            'Trey Grayson': 'REP',
            'Bruce Lunsford': 'DEM',
            'Greg Stumbo': 'DEM',
            'Richie Farmer': 'REP',
        }
    
    def get_party(self, candidate: str, office: str = '') -> str:
        """
        Get party affiliation for a candidate.
        
        Args:
            candidate: Candidate name
            office: Office being sought (for context)
        
        Returns:
            Party abbreviation or empty string if unknown
        """
        # Direct lookup
        if candidate in self.party_mappings:
            return self.party_mappings[candidate]
        
        # Try partial matches for common names
        candidate_lower = candidate.lower()
        for known_candidate, party in self.party_mappings.items():
            if known_candidate.lower() in candidate_lower or candidate_lower in known_candidate.lower():
                return party
        
        return ''
    
    def parse_fixed_width_file(self, file_path: str, election_date: str) -> List[Dict]:
        """
        Parse Kentucky State Board of Elections fixed-width format files.
        
        These files have candidates in rows and counties in columns.
        Example: 2002statebycounty.txt, STATEwide by candidate by county gen 08.txt
        
        Args:
            file_path: Path to the fixed-width text file
            election_date: Date in YYYYMMDD format (e.g., '20021106')
        
        Returns:
            List of dictionaries with election results
        """
        results = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        current_office = None
        current_district = ''
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for office header
            if 'OFFICE:' in line:
                # Extract office name and district
                office_match = re.search(r'OFFICE:\s+\w+/\d+/(\d+)\s+(.+)', line)
                if office_match:
                    district = office_match.group(1).strip()
                    office_name = office_match.group(2).strip()
                    
                    # Clean up office name
                    current_office = office_name
                    current_district = district if district != '000' else ''
                    
                i += 1
                continue
            
            # Look for county headers (lines with *XXXX patterns)
            if '*' in line and current_office:
                # Extract county abbreviations
                county_abbrevs = re.findall(r'\*([A-Z]{4})', line)
                if county_abbrevs:
                    i += 1
                    
                    # Process candidate data lines until next header or blank lines
                    while i < len(lines):
                        data_line = lines[i]
                        
                        # Stop if we hit another county header, office header, or separator
                        if ('*' in data_line and re.search(r'\*[A-Z]{4}', data_line)) or \
                           'OFFICE:' in data_line or \
                           'KENTUCKY STATE BOARD' in data_line or \
                           (data_line.strip() == '' and i + 1 < len(lines) and lines[i+1].strip() == ''):
                            break
                        
                        # Skip blank lines
                        if not data_line.strip():
                            i += 1
                            continue
                        
                        # Extract candidate name - it's left-aligned and followed by numbers
                        # Candidate names can have multiple words, so we need to find where numbers start
                        candidate_match = re.match(r'^\s*([A-Za-z\s&\.\'\"\-]+?)\s{2,}([\d,\s]+)', data_line)
                        if candidate_match:
                            candidate = ' '.join(candidate_match.group(1).split())
                            vote_data = candidate_match.group(2)
                            
                            # Extract vote counts - they're comma-separated numbers with spaces
                            votes = re.findall(r'([\d,]+)', vote_data)
                            votes = [int(v.replace(',', '')) for v in votes if v.strip()]
                            
                            # Match votes to counties
                            for j, county_abbrev in enumerate(county_abbrevs):
                                if j < len(votes):
                                    county_name = self._expand_county_abbrev(county_abbrev)
                                    party = self.get_party(candidate, current_office)
                                    results.append({
                                        'county': county_name,
                                        'office': current_office,
                                        'district': current_district,
                                        'candidate': candidate,
                                        'party': party,
                                        'votes': str(votes[j]),
                                        'election_day': '',
                                        'absentee': '',
                                        'av_counting_boards': '',
                                        'early_voting': '',
                                        'mail': '',
                                        'provisional': '',
                                        'pre_process_absentee': ''
                                    })
                        
                        i += 1
                    continue
            
            i += 1
        
        return results
    
    def parse_pdf_file(self, file_path: str, election_date: str) -> List[Dict]:
        """
        Parse Kentucky election results PDFs using tabula.
        
        Args:
            file_path: Path to the PDF file
            election_date: Date in YYYYMMDD format (e.g., '20121106')
        
        Returns:
            List of dictionaries with election results
        """
        if not TABULA_AVAILABLE:
            raise ImportError("tabula-py is required for PDF parsing. Install with: pip install tabula-py")
        
        results = []
        
        print(f"Extracting tables from PDF (this may take a moment)...")
        
        try:
            # Read all tables from the PDF
            tables = tabula.read_pdf(file_path, pages='all', multiple_tables=True, 
                                    lattice=True, encoding='utf-8')
            
            for table_idx, df in enumerate(tables):
                if df is None or df.empty:
                    continue
                
                print(f"  Processing table {table_idx + 1}/{len(tables)} ({len(df)} rows)")
                
                # Try to identify columns
                # Look for common column patterns in Kentucky election PDFs
                columns = df.columns.tolist()
                
                # Common patterns: County, Office/Race, Candidate, Party, Votes
                # Try to map columns intelligently
                for index, row in df.iterrows():
                    # Skip rows that are all NaN or header rows
                    if row.isna().all():
                        continue
                    
                    # Convert row to list of strings
                    row_data = [str(val).strip() if not pd.isna(val) else '' for val in row]
                    
                    # Basic heuristic: if row has enough data, try to extract
                    if len([x for x in row_data if x and x != 'nan']) >= 3:
                        # This is a simplified parser - you may need to customize
                        # based on the actual PDF structure
                        # For now, we'll collect raw data
                        pass
            
            # If tables are empty or complex, inform user
            if not results:
                print("  ⚠ PDF parsing requires manual configuration for this file format.")
                print("  ⚠ Consider using the existing pdf_to_csv.py tool in tools/ directory.")
                
        except Exception as e:
            print(f"  Error parsing PDF: {e}")
            print("  ⚠ Try using tools/pdf_to_csv.py for more advanced PDF handling.")
        
        return results
    
    def _expand_county_abbrev(self, abbrev: str) -> str:
        """Expand 4-letter county abbreviations to full names."""
        # Common Kentucky county abbreviations
        abbrev_map = {
            'ADAI': 'Adair', 'ALLE': 'Allen', 'ANDE': 'Anderson', 'BALL': 'Ballard',
            'BARR': 'Barren', 'BATH': 'Bath', 'BELL': 'Bell', 'BOON': 'Boone',
            'BOUR': 'Bourbon', 'BOYD': 'Boyd', 'BOYL': 'Boyle', 'BRAC': 'Bracken',
            'BREA': 'Breathitt', 'BREC': 'Breckinridge', 'BULL': 'Bullitt', 'BUTL': 'Butler',
            'CALD': 'Caldwell', 'CALL': 'Calloway', 'CAMP': 'Campbell', 'CARL': 'Carlisle',
            'CARR': 'Carroll', 'CART': 'Carter', 'CASE': 'Casey', 'CHRI': 'Christian',
            'CLAR': 'Clark', 'CLAY': 'Clay', 'CLIN': 'Clinton', 'CRIT': 'Crittenden',
            'CUMB': 'Cumberland', 'DAVI': 'Daviess', 'EDMO': 'Edmonson', 'ELLI': 'Elliott',
            'ESTI': 'Estill', 'FAYE': 'Fayette', 'FLEM': 'Fleming', 'FLOY': 'Floyd',
            'FRAN': 'Franklin', 'FULT': 'Fulton', 'GALL': 'Gallatin', 'GARR': 'Garrard',
            'GRAN': 'Grant', 'GRAV': 'Graves', 'GRAY': 'Grayson', 'GREE': 'Green',
            'GREU': 'Greenup', 'HANC': 'Hancock', 'HARD': 'Hardin', 'HARL': 'Harlan',
            'HARR': 'Harrison', 'HART': 'Hart', 'HEND': 'Henderson', 'HENR': 'Henry',
            'HICK': 'Hickman', 'HOPK': 'Hopkins', 'JACK': 'Jackson', 'JEFF': 'Jefferson',
            'JESS': 'Jessamine', 'JOHN': 'Johnson', 'KENT': 'Kenton', 'KNOT': 'Knott',
            'KNOX': 'Knox', 'LARU': 'LaRue', 'LAUR': 'Laurel', 'LAWR': 'Lawrence',
            'LEE': 'Lee', 'LESL': 'Leslie', 'LETH': 'Letcher', 'LEWI': 'Lewis',
            'LINC': 'Lincoln', 'LIVI': 'Livingston', 'LOGA': 'Logan', 'LYON': 'Lyon',
            'MCCA': 'McCracken', 'MCCR': 'McCreary', 'MCLE': 'McLean', 'MADI': 'Madison',
            'MAGO': 'Magoffin', 'MARI': 'Marion', 'MARS': 'Marshall', 'MART': 'Martin',
            'MASO': 'Mason', 'MEAD': 'Meade', 'MENI': 'Menifee', 'MERC': 'Mercer',
            'META': 'Metcalfe', 'MONR': 'Monroe', 'MONT': 'Montgomery', 'MORG': 'Morgan',
            'MUHL': 'Muhlenberg', 'NELS': 'Nelson', 'NICH': 'Nicholas', 'OHIO': 'Ohio',
            'OLDH': 'Oldham', 'OWEN': 'Owen', 'OWSL': 'Owsley', 'PEND': 'Pendleton',
            'PERR': 'Perry', 'PIKE': 'Pike', 'POWE': 'Powell', 'PULA': 'Pulaski',
            'ROBE': 'Robertson', 'ROCK': 'Rockcastle', 'ROWA': 'Rowan', 'RUSS': 'Russell',
            'SCOT': 'Scott', 'SHEL': 'Shelby', 'SIMP': 'Simpson', 'SPEN': 'Spencer',
            'TAYL': 'Taylor', 'TODD': 'Todd', 'TRIG': 'Trigg', 'TRIM': 'Trimble',
            'UNIO': 'Union', 'WARR': 'Warren', 'WASH': 'Washington', 'WAYN': 'Wayne',
            'WEBS': 'Webster', 'WHIT': 'Whitley', 'WOLF': 'Wolfe', 'WOOD': 'Woodford'
        }
        return abbrev_map.get(abbrev.upper(), abbrev.capitalize())
    
    def create_county_csv(self, results: List[Dict], output_filename: str):
        """
        Create a county-level OpenElections CSV file.
        
        Args:
            results: List of result dictionaries
            output_filename: Name of output file (e.g., '20021106__ky__general__county.csv')
        """
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.COUNTY_HEADERS)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Created: {output_path} ({len(results)} rows)")
    
    def create_precinct_csv(self, results: List[Dict], output_filename: str):
        """
        Create a precinct-level OpenElections CSV file.
        
        Args:
            results: List of result dictionaries (must include 'precinct' field)
            output_filename: Name of output file (e.g., '20241105__ky__general__precinct.csv')
        """
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.PRECINCT_HEADERS)
            writer.writeheader()
            writer.writerows(results)
        
        print(f"Created: {output_path} ({len(results)} rows)")
    
    def convert_file(self, input_file: str, election_date: str, 
                    election_type: str = 'general', level: str = 'county'):
        """
        Convert any supported format to OpenElections CSV.
        
        Args:
            input_file: Path to input file
            election_date: Date in YYYYMMDD format
            election_type: 'general', 'primary', 'special', etc.
            level: 'county' or 'precinct'
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            print(f"Error: File not found: {input_file}")
            return
        
        # Determine input format and parse
        if input_path.suffix == '.txt':
            print(f"Parsing fixed-width format: {input_file}")
            results = self.parse_fixed_width_file(input_file, election_date)
        elif input_path.suffix == '.pdf':
            print(f"Parsing PDF format: {input_file}")
            print("Note: PDF parsing is complex. For best results, use tools/pdf_to_csv.py")
            results = self.parse_pdf_file(input_file, election_date)
            if not results:
                print("\n⚠ PDF parsing incomplete. Recommended: use tools/pdf_to_csv.py instead.")
                return
        else:
            print(f"Error: Unsupported file format: {input_path.suffix}")
            print("Supported formats: .txt (fixed-width), .pdf (experimental)")
            return
        
        if not results:
            print("Error: No data extracted from file")
            return
        
        # Generate output filename
        output_filename = f"{election_date}__ky__{election_type}__{level}.csv"
        
        # Create output file
        if level == 'county':
            self.create_county_csv(results, output_filename)
        else:
            self.create_precinct_csv(results, output_filename)


def main():
    """Main function with examples."""
    formatter = OpenElectionsFormatter(output_dir='data')
    
    # Example conversions
    examples = [
        {
            'input': 'data/2002statebycounty.txt',
            'date': '20021105',
            'type': 'general',
            'level': 'county'
        },
        {
            'input': 'data/STATEwide by candidate by county gen 08.txt',
            'date': '20081104',
            'type': 'general',
            'level': 'county'
        },
    ]
    
    print("OpenElections Format Converter")
    print("=" * 60)
    print()
    
    # List example files that can be converted
    print("Example conversions you can run:")
    for i, ex in enumerate(examples, 1):
        print(f"{i}. {ex['input']}")
        print(f"   -> {ex['date']}__ky__{ex['type']}__{ex['level']}.csv")
    
    print()
    print("To convert a file, call:")
    print("  formatter.convert_file('input.txt', 'YYYYMMDD', 'general', 'county')")


if __name__ == '__main__':
    main()
