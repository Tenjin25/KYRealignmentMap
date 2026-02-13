"""
Extract 2020 Presidential results from Kentucky PDF.
Same format as 2024 - just different candidates.
"""

import sys
from pathlib import Path
import pandas as pd
import pdfplumber
import re

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

candidates_2020_pres = [
    {'name': 'Donald J. Trump', 'party': 'REP'},
    {'name': 'Joseph R. Biden', 'party': 'DEM'},
    {'name': 'Jo Jorgensen', 'party': 'LIB'},
    {'name': 'Kanye West', 'party': 'IND'},
    {'name': 'Brock Pierce', 'party': 'IND'},
    {'name': 'Howie Hawkins', 'party': 'GRN'},
    {'name': 'Brian Carroll', 'party': 'ASP'},
    {'name': 'Gloria La Riva', 'party': 'PSL'},
    {'name': 'Mark Charles', 'party': 'IND'},
    {'name': 'Jade Simmons', 'party': 'WI'},
    {'name': 'Tom Hoefling', 'party': 'WI'},
    {'name': 'Shawn Howard', 'party': 'WI'},
    {'name': 'President R19 Boddie', 'party': 'WI'},
    {'name': 'Kasey Wells', 'party': 'WI'},
    {'name': 'Timothy Allen Stevens', 'party': 'WI'},
    {'name': 'Mary Ruth Caro Simmons', 'party': 'WI'}
]


def extract_data(pdf_path, candidates, office='President'):
    """Extract vote data from PDF."""
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            for line in lines:
                county = None
                for ky_county in KY_COUNTIES:
                    if line.strip().startswith(ky_county):
                        county = ky_county
                        break
                
                if not county:
                    continue
                
                numbers = re.findall(r'(\d{1,3}(?:,\d{3})*|\d+)', line)
                votes = []
                for num in numbers:
                    try:
                        votes.append(int(num.replace(',', '')))
                    except:
                        pass
                
                if not votes:
                    continue
                
                for i, cand_info in enumerate(candidates):
                    if i < len(votes):
                        results.append({
                            'county': county,
                            'office': office,
                            'district': '',
                            'candidate': cand_info['name'],
                            'party': cand_info['party'],
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


def main():
    if len(sys.argv) < 2:
        print("Usage: py extract_2020_pres.py <pdf_file>")
        print("\nExample:")
        print('  py extract_2020_pres.py "data/2020 General Election Results.pdf"')
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print("="*70)
    print("Extracting 2020 Presidential Results from Kentucky PDF")
    print("="*70)
    print(f"\nPDF: {Path(pdf_path).name}")
    print(f"Candidates: {len(candidates_2020_pres)}")
    
    print("\nExtracting...")
    df = extract_data(pdf_path, candidates_2020_pres, office='President')
    
    if df.empty:
        print("\n❌ No data extracted")
        sys.exit(1)
    
    output_file = Path('data') / '20201103__ky__general__county.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved: {output_file}")
    print(f"Counties: {df['county'].nunique()}/120")
    print(f"Records: {len(df):,}")
    print(f"Total votes: {df['votes'].sum():,}")
    
    print("\nTop 5 candidates:")
    for name, total in df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(5).items():
        pct = 100 * total / df['votes'].sum()
        print(f"  {name:30s} {total:10,} ({pct:5.2f}%)")
    
    print("\nSample (first 20 rows):")
    pd.set_option('display.max_colwidth', 25)
    print(df[['county', 'candidate', 'party', 'votes']].head(20).to_string(index=False))


if __name__ == '__main__':
    main()
