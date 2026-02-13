"""
Simple, clean Kentucky election PDF extractor.
Built from scratch to handle KY's format: candidates in columns, counties in rows.

Usage:
    py scripts/simple_ky_extractor.py "data/2024 General Election.pdf"
"""

import sys
import re
from pathlib import Path
import pandas as pd
import tabula
import pdfplumber

# Kentucky's 120 counties
KY_COUNTIES = {
    'Adair', 'Allen', 'Anderson', 'Ballard', 'Barren', 'Bath', 'Bell', 'Boone',
    'Bourbon', 'Boyd', 'Boyle', 'Bracken', 'Breathitt', 'Breckinridge', 'Bullitt',
    'Butler', 'Caldwell', 'Calloway', 'Campbell', 'Carlisle', 'Carroll', 'Carter',
    'Casey', 'Christian', 'Clark', 'Clay', 'Clinton', 'Crittenden', 'Cumberland',
    'Daviess', 'Edmonson', 'Elliott', 'Estill', 'Fayette', 'Fleming', 'Floyd',
    'Franklin', 'Fulton', 'Gallatin', 'Garrard', 'Grant', 'Graves', 'Grayson',
    'Green', 'Greenup', 'Hancock', 'Hardin', 'Harlan', 'Harrison', 'Hart',
    'Henderson', 'Henry', 'Hickman', 'Hopkins', 'Jackson', 'Jefferson', 'Jessamine',
    'Johnson', 'Kenton', 'Knott', 'Knox', 'Larue', 'Laurel', 'Lawrence', 'Lee',
    'Leslie', 'Letcher', 'Lewis', 'Lincoln', 'Livingston', 'Logan', 'Lyon',
    'Madison', 'Magoffin', 'Marion', 'Marshall', 'Martin', 'Mason', 'Mccracken',
    'Mccreary', 'Mclean', 'Meade', 'Menifee', 'Mercer', 'Metcalfe', 'Monroe',
    'Montgomery', 'Morgan', 'Muhlenberg', 'Nelson', 'Nicholas', 'Ohio', 'Oldham',
    'Owen', 'Owsley', 'Pendleton', 'Perry', 'Pike', 'Powell', 'Pulaski',
    'Robertson', 'Rockcastle', 'Rowan', 'Russell', 'Scott', 'Shelby', 'Simpson',
    'Spencer', 'Taylor', 'Todd', 'Trigg', 'Trimble', 'Union', 'Warren',
    'Washington', 'Wayne', 'Webster', 'Whitley', 'Wolfe', 'Woodford'
}


def extract_candidates_from_header(pdf_path):
    """Extract candidate names and parties from PDF header using better text parsing."""
    candidates = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # Get first page with data (usually page 2)
        for page_num in range(min(3, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text or 'Adair' not in text:
                continue
            
            lines = text.split('\n')
            
            # Common patterns in KY PDFs:
            # Line 1: Running Mate name OR party + candidate on same line
            # Line 2: Party name (if not on line 1)
            # Line 3: Candidate name (if not on line 1)
            
            # Find the section between office title and first county
            start_idx = None
            end_idx = None
            
            for i, line in enumerate(lines):
                if 'President and Vice President' in line or 'PRESIDENT' in line.upper():
                    start_idx = i + 1
                if 'Adair' in line and start_idx:
                    end_idx = i
                    break
            
            if not start_idx or not end_idx:
                continue
            
            header_text = '\n'.join(lines[start_idx:end_idx])
            
            # Simple pattern: look for known parties and grab the next meaningful name
            # Split by party keywords
            for party_keyword, party_abbr in [
                ('Republican Party', 'REP'),
                ('Democratic Party', 'DEM'),
                ('Libertarian Party', 'LIB'),
                ('Kentucky Party', 'KY'),
                ('Independent', 'IND'),
                ('Write-In', 'WI')
            ]:
                if party_keyword in header_text:
                    # Find candidate name after this party
                    # Look for pattern: party keyword followed by names
                    idx = header_text.index(party_keyword)
                    after_party = header_text[idx + len(party_keyword):idx + len(party_keyword) + 200]
                    
                    # Extract first capitalized name sequence
                    name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z.]+)*(?:\s+[A-Z]+)?)', after_party)
                    if name_match:
                        candidate_name = name_match.group(1).strip()
                        # Skip if it's another party name
                        if not any(p in candidate_name for p in ['Party', 'Republican', 'Democratic', 'Write']):
                            candidates.append({
                                'party': party_abbr,
                                'candidate': candidate_name
                            })
            
            if len(candidates) >= 2:  # Need at least 2 major candidates
                break
    
    return candidates


def extract_table_data(pdf_path):
    """Extract the vote table using tabula."""
    # Try to extract tables from all pages
    tables = tabula.read_pdf(
        pdf_path,
        pages='all',
        multiple_tables=True,
        lattice=False,  # Stream mode for tables without borders
        guess=True
    )
    
    # Find the table with county data
    best_table = None
    max_rows = 0
    
    for table in tables:
        if len(table) > max_rows:
            # Check if first column looks like counties
            first_col = table.iloc[:, 0].astype(str)
            county_matches = sum(1 for val in first_col 
                               if any(county.lower() in val.lower() 
                                    for county in KY_COUNTIES))
            if county_matches > 5:  # At least 5 counties found
                best_table = table
                max_rows = len(table)
    
    return best_table


def parse_county_row(row_text):
    """
    Parse a row like 'Adair 7,643 1,257 48 13 7 3 2 1 0 0 0'
    Returns: (county_name, [vote_counts])
    """
    row_text = str(row_text).strip()
    
    # Match county name at start
    for county in KY_COUNTIES:
        if row_text.lower().startswith(county.lower()):
            # Remove county name, parse remaining numbers
            remaining = row_text[len(county):].strip()
            votes = []
            for num_str in re.findall(r'[\d,]+', remaining):
                votes.append(int(num_str.replace(',', '')))
            return county, votes
    
    return None, []


def extract_from_pdf(pdf_path):
    """Main extraction function."""
    print(f"\n{'='*60}")
    print(f"Extracting: {Path(pdf_path).name}")
    print('='*60)
    
    # Step 1: Get candidates from header
    print("\n1. Extracting candidate names...")
    candidates = extract_candidates_from_header(pdf_path)
    
    if not candidates:
        print("   ⚠ Could not auto-detect candidates")
        print("   Using manual input mode...")
        return manual_input_mode(pdf_path)
    
    print(f"   Found {len(candidates)} candidates:")
    for i, cand in enumerate(candidates, 1):
        print(f"     {i}. {cand['candidate']} ({cand['party']})")
    
    # Step 2: Extract vote table
    print("\n2. Extracting vote data...")
    table = extract_table_data(pdf_path)
    
    if table is None or table.empty:
        print("   ❌ Could not extract table")
        return None
    
    print(f"   Extracted table with {len(table)} rows")
    
    # Step 3: Parse rows and match with candidates
    print("\n3. Parsing county data...")
    results = []
    
    for _, row in table.iterrows():
        # Get first column as county
        county, votes = parse_county_row(row.iloc[0])
        
        if not county:
            continue
        
        # Match votes to candidates
        for i, vote_count in enumerate(votes):
            if i < len(candidates):
                results.append({
                    'county': county,
                    'office': 'President',  # TODO: detect from PDF
                    'district': '',
                    'candidate': candidates[i]['candidate'],
                    'party': candidates[i]['party'],
                    'votes': vote_count
                })
    
    print(f"   Parsed {len(results)} records from {len(set(r['county'] for r in results))} counties")
    
    return pd.DataFrame(results)


def manual_input_mode(pdf_path):
    """Interactive mode to manually specify candidates."""
    print("\n" + "="*60)
    print("MANUAL INPUT MODE")
    print("="*60)
    print("\nI'll extract the vote numbers, you tell me the candidate names.")
    print("\nOpen the PDF and look at the column headers.")
    print(f"PDF: {pdf_path}\n")
    
    # Extract just the numbers
    table = extract_table_data(pdf_path)
    if table is None:
        print("❌ Could not extract any data")
        return None
    
    # Count columns (excluding county column)
    num_candidates = len(table.columns) - 1
    print(f"Found {num_candidates} vote columns")
    print("\nEnter candidate info for each column:")
    print("(Press Enter to skip)\n")
    
    candidates = []
    for i in range(num_candidates):
        print(f"Column {i+1}:")
        name = input("  Candidate name: ").strip()
        party = input("  Party (REP/DEM/LIB/IND/etc): ").strip().upper()
        
        if name:
            candidates.append({'candidate': name, 'party': party or 'UNK'})
        else:
            candidates.append({'candidate': f'Candidate {i+1}', 'party': 'UNK'})
    
    # Now build results
    results = []
    for _, row in table.iterrows():
        county, votes = parse_county_row(row.iloc[0])
        if not county:
            continue
        
        for i, vote_count in enumerate(votes):
            if i < len(candidates):
                results.append({
                    'county': county,
                    'office': '',
                    'district': '',
                    'candidate': candidates[i]['candidate'],
                    'party': candidates[i]['party'],
                    'votes': vote_count
                })
    
    return pd.DataFrame(results)


def save_to_openelections_format(df, pdf_path, output_dir='data'):
    """Save DataFrame in OpenElections format."""
    if df is None or df.empty:
        return None
    
    # Add missing columns
    for col in ['election_day', 'absentee', 'av_counting_boards', 
                'early_voting', 'mail', 'provisional', 'pre_process_absentee']:
        if col not in df.columns:
            df[col] = ''
    
    # Determine date from PDF filename or use default
    # Look for patterns like 2024, 20241105, etc.
    filename = Path(pdf_path).stem
    year = None
    matches = re.findall(r'20\d{2}', filename)
    if matches:
        year = matches[0]
    
    date = f"{year}1105" if year else "20241105"  # Default to Nov 5
    
    # Generate output filename
    output_file = Path(output_dir) / f"{date}__ky__general__county.csv"
    
    # Ensure column order
    columns = ['county', 'office', 'district', 'candidate', 'party', 'votes',
               'election_day', 'absentee', 'av_counting_boards', 'early_voting',
               'mail', 'provisional', 'pre_process_absentee']
    
    df = df[columns]
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print("✓ SUCCESS")
    print('='*60)
    print(f"Output: {output_file}")
    print(f"Records: {len(df):,}")
    print(f"Counties: {df['county'].nunique()}")
    print(f"Candidates: {df['candidate'].nunique()}")
    print(f"Total votes: {df['votes'].sum():,}")
    
    # Show preview
    print("\nPreview:")
    print(df.head(10).to_string(index=False))
    
    return output_file


def main():
    if len(sys.argv) < 2:
        print("Usage: py scripts/simple_ky_extractor.py <pdf_file>")
        print("\nExample:")
        print('  py scripts/simple_ky_extractor.py "data/2024 General Election.pdf"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    # Extract data
    df = extract_from_pdf(pdf_path)
    
    if df is not None and not df.empty:
        save_to_openelections_format(df, pdf_path)
    else:
        print("\n❌ Extraction failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
