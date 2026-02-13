"""
Extract ALL 2023 Kentucky statewide races.
Governor, Attorney General, Secretary of State, Auditor, Treasurer, Ag Commissioner.
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

# Define all 2023 races with their candidates
RACES_2023 = [
    {
        'office': 'Governor',
        'page_start': 1,
        'candidates': [
            {'name': 'Andy Beshear', 'party': 'DEM'},
            {'name': 'Daniel Cameron', 'party': 'REP'},
            {'name': 'Brian Fishback', 'party': 'WI'}
        ]
    },
    {
        'office': 'Secretary of State',
        'page_start': 8,
        'candidates': [
            {'name': 'Michael Adams', 'party': 'REP'},
            {'name': 'Charles "Buddy" Wheatley', 'party': 'DEM'},
            {'name': 'Kenneth C. Moellman Jr.', 'party': 'WI'}
        ]
    },
    {
        'office': 'Attorney General',
        'page_start': 14,
        'candidates': [
            {'name': 'Russell Coleman', 'party': 'REP'},
            {'name': 'Pamela Stevenson', 'party': 'DEM'}
        ]
    },
    {
        'office': 'Auditor of Public Accounts',
        'page_start': 20,
        'candidates': [
            {'name': 'Allison Ball', 'party': 'REP'},
            {'name': 'Kimberley "Kim" Reeder', 'party': 'DEM'}
        ]
    },
    {
        'office': 'State Treasurer',
        'page_start': 26,
        'candidates': [
            {'name': 'Mark H. Metcalf', 'party': 'REP'},
            {'name': 'Michael Bowman', 'party': 'DEM'},
            {'name': 'Robert Perry', 'party': 'WI'}
        ]
    },
    {
        'office': 'Commissioner of Agriculture',
        'page_start': 32,
        'candidates': [
            {'name': 'Jonathan Shell', 'party': 'REP'},
            {'name': 'Sierra J. Enlow', 'party': 'DEM'}
        ]
    }
]


def extract_race(pdf, race_info):
    """Extract data for one race."""
    results = []
    office = race_info['office']
    candidates = race_info['candidates']
    page_start = race_info['page_start']
    
    # Extract from this race's pages (each race is ~5-6 pages)
    for page_num in range(page_start, min(page_start + 6, len(pdf.pages))):
        text = pdf.pages[page_num].extract_text() or ''
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
    
    return results


def main():
    pdf_path = "data/Certification of Election Results for 2023 General Election Final.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print("="*70)
    print("Extracting 2023 Kentucky Statewide Races")
    print("="*70)
    print(f"\nPDF: {Path(pdf_path).name}")
    print("Races: Governor, Secretary of State, Attorney General,")
    print("       Auditor, Treasurer, Agriculture Commissioner\n")
    
    all_results = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for race_info in RACES_2023:
            print(f"Extracting {race_info['office']}...")
            race_results = extract_race(pdf, race_info)
            all_results.extend(race_results)
            print(f"  ✓ {len(race_results)} records")
    
    df = pd.DataFrame(all_results)
    
    if df.empty:
        print("\n❌ No data extracted")
        sys.exit(1)
    
    output_file = Path('data') / '20231107__ky__general__county.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved: {output_file}")
    print(f"Counties: {df['county'].nunique()}/120")
    print(f"Total records: {len(df):,}")
    print(f"Total votes: {df['votes'].sum():,}")
    
    print("\n" + "="*70)
    print("RESULTS BY RACE")
    print("="*70)
    
    for office in df['office'].unique():
        office_df = df[df['office'] == office]
        print(f"\n{office}:")
        for cand, votes in office_df.groupby('candidate')['votes'].sum().sort_values(ascending=False).items():
            party = office_df[office_df['candidate'] == cand]['party'].iloc[0]
            pct = 100 * votes / office_df['votes'].sum()
            winner = "  ✓ WINNER" if votes == office_df.groupby('candidate')['votes'].sum().max() else ""
            print(f"  {cand:35s} ({party:3s}) {votes:10,} ({pct:5.2f}%){winner}")


if __name__ == '__main__':
    main()
