"""
Extract 2016 Presidential Election Results from Kentucky Secretary of State PDF.
30 candidates including Trump, Clinton, Johnson, Stein, McMullin, and 25 others.
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

CANDIDATES_2016 = [
    {'name': 'Donald J. Trump', 'party': 'REP'},
    {'name': 'Hillary Rodham Clinton', 'party': 'DEM'},
    {'name': 'Gary Johnson', 'party': 'LIB'},
    {'name': 'Evan McMullin', 'party': 'IND'},
    {'name': 'Jill Stein', 'party': 'GRN'},
    {'name': 'Rocky Roque De La Fuente', 'party': 'AMR'},
    {'name': 'Darrell L. Castle', 'party': 'CON'},
    {'name': 'Michael A. Maturen', 'party': 'ASP'},
    {'name': 'Tom Hoefling', 'party': 'AIP'},
    {'name': 'Chris Keniston', 'party': 'VET'},
    {'name': 'Denny Carroll Jackson', 'party': 'IND'},
    {'name': 'John Paul Mabry Jr.', 'party': 'IND'},
    {'name': 'Daniel White', 'party': 'IND'},
    {'name': 'Laurence Kotlikoff', 'party': 'IND'},
    {'name': 'Scott Cubbler', 'party': 'IND'},
    {'name': 'Paul Dudley Bowling III', 'party': 'IND'},
    {'name': 'Dave Marshall', 'party': 'IND'},
    {'name': 'Eric "Rick" Seiley', 'party': 'IND'},
    {'name': 'Niles Niemuth', 'party': 'SEP'},
    {'name': 'Douglas Terranova', 'party': 'IND'},
    {'name': 'James Mitchell Jr.', 'party': 'IND'},
    {'name': 'Ricky Johnson', 'party': 'IND'},
    {'name': 'David L. Knight', 'party': 'IND'},
    {'name': 'R. Charles Casper-Kacprowicz', 'party': 'IND'},
    {'name': 'Roger Kushner', 'party': 'IND'},
    {'name': 'Robert E. Ling', 'party': 'IND'},
    {'name': 'Valerie M. Michaels', 'party': 'IND'},
    {'name': 'Daniel Paul Zutler', 'party': 'IND'},
    {'name': 'Aaron Barriere', 'party': 'IND'},
    {'name': 'Anthony J. Valdivia', 'party': 'IND'}
]


def extract_data(pdf_path):
    """Extract presidential race data from Kentucky PDF."""
    results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:5]:  # Presidential race is first ~5 pages
            text = page.extract_text() or ''
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
                
                for i, cand_info in enumerate(CANDIDATES_2016):
                    if i < len(votes):
                        results.append({
                            'county': county,
                            'office': 'President',
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
    
    return results


def main():
    pdf_path = "data/2016 General Election Results.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print("="*70)
    print("Extracting 2016 Presidential Election (Kentucky)")
    print("="*70)
    print(f"\nPDF: {Path(pdf_path).name}")
    print(f"Candidates: {len(CANDIDATES_2016)}\n")
    
    results = extract_data(pdf_path)
    df = pd.DataFrame(results)
    
    if df.empty:
        print("\n❌ No data extracted")
        sys.exit(1)
    
    output_file = Path('data') / '20161108__ky__general__county.csv'
    df.to_csv(output_file, index=False)
    
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved: {output_file}")
    print(f"Counties: {df['county'].nunique()}/120")
    print(f"Total votes: {df['votes'].sum():,}")
    
    print("\n" + "="*70)
    print("TOP 10 CANDIDATES")
    print("="*70)
    
    for cand, votes in df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10).items():
        party = df[df['candidate'] == cand]['party'].iloc[0]
        pct = 100 * votes / df['votes'].sum()
        winner = "  ✓ WINNER" if cand == 'Donald J. Trump' else ""
        print(f"  {cand:35s} ({party:3s}) {votes:10,} ({pct:5.2f}%){winner}")


if __name__ == '__main__':
    main()
