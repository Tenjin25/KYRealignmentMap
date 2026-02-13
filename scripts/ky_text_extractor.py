"""
Kentucky PDF extractor using pdfplumber with explicit table settings.
This tells pdfplumber exactly where to look for table boundaries.
"""

import sys
import re
from pathlib import Path
import pandas as pd
import pdfplumber

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


def extract_from_text(pdf_path, candidates):
    """Extract by parsing raw text line by line."""
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                # Check if line starts with a county name
                county = None
                for ky_county in KY_COUNTIES:
                    if line.strip().startswith(ky_county):
                        county = ky_county
                        break
                
                if not county:
                    continue
                
                # Extract all numbers from the line
                numbers = re.findall(r'[\d,]+', line)
                votes = [int(n.replace(',', '')) for n in numbers]
                
                # Match votes to candidates
                for i, candidate_info in enumerate(candidates):
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
    print("Enter candidates from your PDF (left to right)")
    print("="*70)
    print("Press Enter with blank name when done.\n")
    
    candidates = []
    i = 1
    
    while True:
        print(f"\nCandidate #{i}:")
        name = input("  Name: ").strip()
        
        if not name:
            break
        
        party = input("  Party (REP/DEM/LIB/IND): ").strip().upper()
        office = input("  Office [President]: ").strip() or "President"
        
        candidates.append({
            'name': name,
            'party': party,
            'office': office
        })
        
        i += 1
    
    return candidates


def save_results(df, pdf_path):
    """Save to OpenElections format."""
    # Get year from filename
    filename = Path(pdf_path).stem
    year = re.search(r'20\d{2}', filename)
    year = year.group() if year else '2024'
    
    date = f"{year}1105"
    output_file = Path('data') / f"{date}__ky__general__county.csv"
    
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved: {output_file}")
    print(f"\nCounties: {df['county'].nunique()}/{len(KY_COUNTIES)}")
    print(f"Candidates: {df['candidate'].nunique()}")
    print(f"Records: {len(df):,}")
    print(f"Total votes: {df['votes'].sum():,}")
    
    print(f"\nTop candidates:")
    for name, total in df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(5).items():
        print(f"  {name}: {total:,} votes")
    
    print("\nSample data:")
    print(df.head(15).to_string(index=False, max_colwidth=20))
    
    return output_file


def main():
    print("="*70)
    print("KENTUCKY PDF TEXT EXTRACTOR")
    print("="*70)
    
    if len(sys.argv) < 2:
        print("\nUsage: py scripts/ky_text_extractor.py \"path/to/file.pdf\"")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"\n❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print(f"\nPDF: {Path(pdf_path).name}\n")
    print("IMPORTANT: Candidates must be entered in the EXACT order they")
    print("appear in the PDF from LEFT to RIGHT across the columns.")
    
    # Get candidates
    candidates = get_candidates_interactive()
    
    if not candidates:
        print("\n❌ No candidates entered")
        sys.exit(1)
    
    print(f"\n✓ Will extract {len(candidates)} candidates")
    
    # Extract
    print("\nExtracting data...")
    df = extract_from_text(pdf_path, candidates)
    
    if df.empty:
        print("\n❌ No data extracted")
        sys.exit(1)
    
    # Save
    save_results(df, pdf_path)


if __name__ == '__main__':
    main()
