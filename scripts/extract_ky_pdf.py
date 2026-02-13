"""
Dead simple Kentucky PDF extractor.
You look at the PDF, tell the script the candidate names, it extracts the numbers.

Usage:
    py scripts/extract_ky_pdf.py "data/2024 General Election.pdf"
"""

import sys
import re
from pathlib import Path
import pandas as pd
import tabula

# Kentucky's 120 counties
KY_COUNTIES = [
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
]


def is_county_name(text):
    """Check if text is a Kentucky county name."""
    text = str(text).strip()
    return any(county.lower() in text.lower() for county in KY_COUNTIES)


def extract_county_name(text):
    """Extract clean county name from text."""
    text = str(text).strip()
    for county in KY_COUNTIES:
        if county.lower() in text.lower():
            return county
    return None


def extract_vote_table(pdf_path):
    """Extract the raw table from PDF."""
    print("\nExtracting table from PDF...")
    
    # Try stream mode (no table borders)
    try:
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=False,
            lattice=False,
            stream=True,
            guess=False
        )
        
        if tables and len(tables[0]) > 10:
            return tables[0]
    except:
        pass
    
    # Try lattice mode (with borders)
    try:
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=False,
            lattice=True
        )
        
        if tables and len(tables[0]) > 10:
            return tables[0]
    except:
        pass
    
    return None


def process_pdf(pdf_path, candidates_info):
    """
    Process PDF with known candidate information.
    
    candidates_info: list of dicts with 'name', 'party', 'office'
    """
    # Extract table
    table = extract_vote_table(pdf_path)
    
    if table is None:
        print("❌ Could not extract table from PDF")
        return None
    
    print(f"✓ Extracted table with {len(table)} rows, {len(table.columns)} columns")
    
    # Find rows that are county data
    results = []
    
    for idx, row in table.iterrows():
        # First column should be county name
        first_col = str(row.iloc[0])
        county = extract_county_name(first_col)
        
        if not county:
            continue
        
        # Rest of columns are vote counts
        # Extract all numbers from the row
        votes = []
        for col_idx in range(len(row)):
            cell = str(row.iloc[col_idx])
            # Extract all numbers from this cell
            numbers = re.findall(r'[\d,]+', cell)
            for num_str in numbers:
                try:
                    votes.append(int(num_str.replace(',', '')))
                except:
                    pass
        
        # Skip the first number (it's part of county name usually)
        if votes:
            votes = votes[1:] if len(votes) > len(candidates_info) else votes
        
        # Match votes to candidates
        for i, candidate_info in enumerate(candidates_info):
            if i < len(votes):
                results.append({
                    'county': county,
                    'office': candidate_info.get('office', ''),
                    'district': '',
                    'candidate': candidate_info['name'],
                    'party': candidate_info['party'],
                    'votes': votes[i],
                    'election_day': '',
                    'absentee': '',
                    'av_counting_boards': '',
                    'early_voting': '',
                    'mail': '',
                    'provisional': '',
                    'pre_process_absentee': ''
                })
    
    return pd.DataFrame(results)


def get_candidates_interactive():
    """Ask user for candidate information."""
    print("\n" + "="*70)
    print("CANDIDATE ENTRY")
    print("="*70)
    print("\nLook at your PDF and enter the candidates from LEFT to RIGHT")
    print("Press Enter with blank name when done.\n")
    
    candidates = []
    i = 1
    
    while True:
        print(f"\nCandidate #{i}:")
        name = input("  Full name (or Enter to finish): ").strip()
        
        if not name:
            break
        
        party = input("  Party (REP/DEM/LIB/IND/etc): ").strip().upper()
        office = input("  Office (President/U.S. Senate/etc): ").strip()
        
        candidates.append({
            'name': name,
            'party': party or '',
            'office': office or 'President'
        })
        
        i += 1
    
    return candidates


def get_candidates_from_args():
    """Get candidates from command line arguments."""
    # Format: name:party:office,name:party:office,...
    if len(sys.argv) < 3:
        return None
    
    cand_str = sys.argv[2]
    candidates = []
    
    for cand_info in cand_str.split(','):
        parts = cand_info.split(':')
        if len(parts) >= 2:
            candidates.append({
                'name': parts[0].strip(),
                'party': parts[1].strip().upper(),
                'office': parts[2].strip() if len(parts) > 2 else 'President'
            })
    
    return candidates if candidates else None


def save_results(df, pdf_path, output_dir='data'):
    """Save to OpenElections format."""
    if df is None or df.empty:
        return None
    
    # Get year from filename
    filename = Path(pdf_path).stem
    year = re.search(r'20\d{2}', filename)
    year = year.group() if year else '2024'
    
    # Assume November general election
    date = f"{year}1105"
    output_file = Path(output_dir) / f"{date}__ky__general__county.csv"
    
    # Save
    df.to_csv(output_file, index=False)
    
    # Summary
    print("\n" + "="*70)
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved to: {output_file}")
    print(f"\nSummary:")
    print(f"  Counties: {df['county'].nunique()}/{len(KY_COUNTIES)}")
    print(f"  Candidates: {df['candidate'].nunique()}")
    print(f"  Total records: {len(df):,}")
    print(f"  Total votes: {df['votes'].sum():,}")
    
    # Show top candidates by vote
    print(f"\nTop candidates:")
    top = df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(5)
    for name, votes in top.items():
        print(f"  {name}: {votes:,}")
    
    # Show preview
    print(f"\nFirst few rows:")
    print(df.head(10).to_string(index=False))
    
    return output_file


def main():
    print("\n" + "="*70)
    print("SIMPLE KENTUCKY PDF EXTRACTOR")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print('  py scripts/extract_ky_pdf.py "data/2024.pdf"')
        print('    (interactive mode - you enter candidate names)')
        print()
        print('  py scripts/extract_ky_pdf.py "data/2024.pdf" "Trump:REP,Harris:DEM"')
        print('    (command line mode - candidates specified)')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"\n❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print(f"\nProcessing: {Path(pdf_path).name}")
    
    # Get candidate info
    candidates = get_candidates_from_args()
    
    if not candidates:
        # Interactive mode
        print("\nOpen the PDF in another window to see candidate names")
        input("Press Enter when ready...")
        candidates = get_candidates_interactive()
    
    if not candidates:
        print("\n❌ No candidates entered")
        sys.exit(1)
    
    print(f"\n✓ Will extract data for {len(candidates)} candidates:")
    for c in candidates:
        print(f"  - {c['name']} ({c['party']})")
    
    # Process
    df = process_pdf(pdf_path, candidates)
    
    if df is not None and not df.empty:
        save_results(df, pdf_path)
    else:
        print("\n❌ No data extracted")
        sys.exit(1)


if __name__ == '__main__':
    main()
