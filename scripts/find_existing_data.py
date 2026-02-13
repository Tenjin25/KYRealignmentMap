"""
Smart search for pre-existing Kentucky election data.
Checks the most likely sources where this data already exists.
"""

import json
from pathlib import Path

print("=" * 80)
print("FINDING PRE-EXISTING ELECTION DATA (Better Than OCR)")
print("=" * 80)

missing_data = {
    "2019": {
        "name": "2019 Kentucky General Election",
        "race": "General (Governor, State offices)",
        "sources": [
            ("OpenElections GitHub", "https://github.com/openelections/openelections-data-ky/tree/master/2019"),
            ("Kentucky Secretary of State", "https://elections.ky.gov/results-and-data/2019-general/"),
            ("Dave Leip's Atlas", "https://uselectionatlas.org/RESULTS/state.php?f=0&year=2019&off=0"),
        ]
    },
    "2022": {
        "name": "2022 Kentucky General Election", 
        "race": "General (U.S. Senate, Congressional)",
        "sources": [
            ("OpenElections GitHub", "https://github.com/openelections/openelections-data-ky/tree/master/2022"),
            ("Kentucky Secretary of State", "https://elections.ky.gov/results-and-data/2022-general/"),
            ("FEC Federal Election Commission", "https://www.fec.gov/pubrec/electionresults/"),
        ]
    },
    "2010 Off-Year": {
        "name": "2010 Kentucky Off-Year Elections",
        "race": "Off-year (District/local)",
        "sources": [
            ("OpenElections GitHub", "https://github.com/openelections/openelections-data-ky/tree/master/2010"),
            ("Kentucky Secretary of State Archives", "https://elections.ky.gov/results-and-data/"),
            ("State Legislative Archives", "https://legislature.ky.gov/"),
        ]
    },
    "2011 Off-Year": {
        "name": "2011 Kentucky Off-Year Elections",
        "race": "Off-year (District/local)",
        "sources": [
            ("OpenElections GitHub", "https://github.com/openelections/openelections-data-ky/tree/master/2011"),
            ("Kentucky Secretary of State Archives", "https://elections.ky.gov/results-and-data/"),
            ("State Legislative Archives", "https://legislature.ky.gov/"),
        ]
    },
}

print("\n🎯 STEP-BY-STEP ACTION PLAN\n")
print("=" * 80)

for year, info in sorted(missing_data.items()):
    print(f"\n{year} - {info['name']}")
    print(f"Race Type: {info['race']}")
    print("\nCheck these sources (in order):")
    for i, (source, url) in enumerate(info['sources'], 1):
        print(f"  {i}. {source}")
        print(f"     {url}")

print("\n" + "=" * 80)
print("HOW TO USE THESE SOURCES")
print("=" * 80)

instructions = {
    "OpenElections GitHub": """
    1. Visit the URL
    2. Look for CSV files named like:
       - 20190105__ky__general__county.csv
       - 20220104__ky__general__county.csv
    3. Click on the file
    4. Click 'Raw' button on GitHub
    5. Right-click → 'Save as...' or Ctrl+S
    6. Save to: data/
    
    ✓ MOST LIKELY TO HAVE THE DATA
    """,
    
    "Kentucky Secretary of State": """
    1. Visit https://elections.ky.gov/results-and-data/
    2. Look for year you need (2019, 2022, 2010, 2011)
    3. Look for "Download" or "Export" buttons
    4. Try Excel or CSV format
    5. Save to: data/
    
    ✓ OFFICIAL SOURCE
    """,
    
    "Dave Leip's Atlas": """
    1. Visit https://uselectionatlas.org/
    2. Select Kentucky
    3. Select year
    4. Right-click on table → Copy
    5. Paste into Excel
    6. Save as CSV
    
    ✓ GOOD FOR VERIFICATION, SLOWER TO EXTRACT
    """,
}

for method, instruction in instructions.items():
    print(f"\n{method}:")
    print(instruction)

print("\n" + "=" * 80)
print("WHAT TO LOOK FOR")
print("=" * 80)
print("""
✅ Good signs (data is usable):
   - File name format: YYYYMMDD__ky__general__county.csv
   - Can preview before downloading
   - Column headers are clear: county, candidate, party, votes
   - Readable data

❌ Bad signs (skip this):
   - Mangled/scrambled data
   - No headers
   - Looks like failed OCR
   - Says "preliminary" with "TBD" values
""")

print("\n" + "=" * 80)
print("IF YOU FIND THE DATA")
print("=" * 80)
print("""
1. Download CSV files
2. Rename to follow pattern: YYYYMMDD__ky__general__county.csv
   Example: 20190105__ky__general__county.csv
3. Copy to data/ folder
4. Verify it looks good (open in Excel to check)
5. Done! Your data is ready to use
""")

print("\n" + "=" * 80)
print("PRIORITY ORDER TO CHECK")
print("=" * 80)
print("""
1st Priority: OpenElections GitHub
    - Most likely to have clean, verified data
    - Free, no account needed
    - Time: 2 minutes

2nd Priority: Kentucky Secretary of State
    - Official source
    - May have data in Excel/CSV download
    - Time: 5 minutes

3rd Priority: Dave Leip's Atlas
    - Good for verification
    - May need manual copying
    - Time: 10 minutes

Last Resort: Email elections@ky.gov
    - Request CSV files directly
    - They often keep them ready
    - Time: instant response or wait for email
""")

print("\n✨ Bottom line: Don't waste time with OCR conversions.")
print("   The data exists somewhere - find it instead of reconstructing it!\n")
