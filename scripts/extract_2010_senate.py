"""
Extract 2010 US Senate election results from scanned PDF using OCR.
Rand Paul (REP) vs Jack Conway (DEM) vs Billy Ray Wilson (WI).
"""

import sys
from pathlib import Path
import pandas as pd
import re

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import fitz  # PyMuPDF
from PIL import Image, ImageEnhance

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


def fuzzy_match_county(line_start, counties):
    """Try to match county name from line, handling OCR errors."""
    line_start_lower = line_start.lower()
    
    # Direct match first
    for county in counties:
        if line_start.strip().startswith(county):
            return county
    
    # Fuzzy match for common OCR errors
    for county in counties:
        county_lower = county.lower()
        # Check if line starts with county (case insensitive)
        if line_start_lower.startswith(county_lower):
            return county
        # Handle common OCR substitutions
        if county == 'Mccracken' and any(x in line_start_lower for x in ['mccracken', 'mceracken', 'mocracken']):
            return county
        if county == 'Mccreary' and any(x in line_start_lower for x in ['mccreary', 'mecreary', 'mocreary']):
            return county
        if county == 'Mclean' and any(x in line_start_lower for x in ['mclean', 'melean', 'molean']):
            return county
        if county == 'Caldwell' and any(x in line_start_lower for x in ['caldwell', 'caidwell', 'caildwell']):
            return county
        if county == 'Casey' and any(x in line_start_lower for x in ['casey', 'caney', 'cesey']):
            return county
        if county == 'Greenup' and any(x in line_start_lower for x in ['greenup', 'oreenup', 'creenup']):
            return county
        if county == 'Harlan' and any(x in line_start_lower for x in ['harlan', 'harian', 'harlen']):
            return county
        if county == 'Woodford' and any(x in line_start_lower for x in ['woodford', 'woodtord', 'wocdford']):
            return county
    
    return None


CANDIDATES_2010_SENATE = [
    {'name': 'Rand Paul', 'party': 'REP'},
    {'name': 'Jack Conway', 'party': 'DEM'},
    {'name': 'Billy Ray Wilson', 'party': 'WI'}
]


def extract_with_ocr(pdf_path, start_page=1, end_page=5):
    """Extract text from PDF pages using OCR."""
    doc = fitz.open(pdf_path)
    results = []
    
    print(f"Processing pages {start_page} to {end_page}...")
    for page_num in range(start_page - 1, min(end_page, len(doc))):
        print(f"  OCR page {page_num + 1}/{len(doc)}...", end='', flush=True)
        page = doc[page_num]
        
        # Render page to image
        pix = page.get_pixmap(dpi=250)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # OCR the image
        text = pytesseract.image_to_string(img)
        lines = text.split('\n')
        
        counties_found = 0
        for line in lines:
            county = fuzzy_match_county(line, KY_COUNTIES)
            
            if not county:
                continue
            
            # Extract numbers from line
            numbers = re.findall(r'(\d{1,3}(?:,\d{3})*|\d+)', line)
            votes = []
            for num in numbers:
                try:
                    votes.append(int(num.replace(',', '')))
                except:
                    pass
            
            if len(votes) < 3:
                continue
            
            counties_found += 1
            for i, cand_info in enumerate(CANDIDATES_2010_SENATE):
                if i < len(votes):
                    results.append({
                        'county': county,
                        'office': 'U.S. Senate',
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
        
        print(f" found {counties_found} counties")
    
    doc.close()
    return results


def main():
    pdf_path = "data/off2010gen.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print("="*70)
    print("2010 US Senate - OCR Extraction")
    print("="*70)
    print(f"\nPDF: {Path(pdf_path).name}")
    print("Race: Rand Paul (REP) vs Jack Conway (DEM)")
    print("\nNOTE: OCR processing pages 1-6 at 250 DPI...\n")
    
    results = extract_with_ocr(pdf_path, start_page=1, end_page=6)
    df = pd.DataFrame(results)
    
    if df.empty:
        print("\n❌ No data extracted")
        sys.exit(1)
    
    # Remove duplicates - keep the row with higher vote count for each county/candidate
    print(f"\nRecords before deduplication: {len(df)}")
    df = df.sort_values('votes', ascending=False).drop_duplicates(['county', 'candidate'], keep='first')
    print(f"Records after deduplication: {len(df)}")
    
    output_file = Path('data') / '20101102__ky__general__senate__county.csv'
    df.to_csv(output_file, index=False)
    
    print("\n" + "="*70)
    print("✓ SUCCESS")
    print("="*70)
    print(f"\nSaved: {output_file}")
    print(f"Counties: {df['county'].nunique()}/120")
    print(f"Total records: {len(df):,}")
    print(f"Total votes: {df['votes'].sum():,}")
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    for cand, votes in df.groupby('candidate')['votes'].sum().sort_values(ascending=False).items():
        party = df[df['candidate'] == cand]['party'].iloc[0]
        pct = 100 * votes / df['votes'].sum()
        winner = "  ✓ WINNER" if votes == df.groupby('candidate')['votes'].sum().max() else ""
        print(f"  {cand:35s} ({party:3s}) {votes:10,} ({pct:5.2f}%){winner}")


if __name__ == '__main__':
    main()
