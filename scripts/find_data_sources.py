"""
Search for alternative Kentucky election data sources.
Checks online repositories and official sources.
"""

from pathlib import Path

print("=" * 80)
print("FINDING ALTERNATIVE DATA SOURCES FOR MISSING ELECTION YEARS")
print("=" * 80)

missing_years = {
    "2019": "General Election",
    "2022": "General Election", 
    "2010 off-year": "Off-year elections",
    "2011 off-year": "Off-year elections"
}

# Known sources to check
sources = {
    "OpenElections KY Data": {
        "url": "https://github.com/openelections/openelections-data-ky",
        "type": "GitHub repository",
        "notes": "Official OpenElections Kentucky data repository"
    },
    "Kentucky Secretary of State": {
        "url": "https://elections.ky.gov/results-and-data/election-results/",  
        "type": "Official website",
        "notes": "Main source for election results"
    },
    "FEC - Federal Election Commission": {
        "url": "https://www.fec.gov/pubrec/electionresults/",
        "type": "Federal database",
        "notes": "Has general/presidential election data"
    },
    "Election Administration and Voting Survey": {
        "url": "https://www.eac.gov/research-and-data/datasets-codebooks-and-surveys",
        "type": "EAC dataset",
        "notes": "Election data agency"
    },
    "Ballotpedia": {
        "url": "https://ballotpedia.org/Kentucky_elections",
        "type": "Election wiki",
        "notes": "Curated election information"
    },
    "Dave Leip's Atlas of US Elections": {
        "url": "https://uselectionatlas.org/",
        "type": "Historical database",
        "notes": "Comprehensive historical election data by county"
    },
    "Kentucky Data Portal": {
        "url": "https://data.ky.gov/resource/search",
        "type": "State data portal",
        "notes": "Open data from Kentucky state government"
    }
}

print("\n📊 RECOMMENDED SOURCES TO CHECK:\n")

for name, info in sources.items():
    print(f"🔗 {name}")
    print(f"   Type: {info['type']}")
    print(f"   URL: {info['url']}")
    print(f"   Notes: {info['notes']}")
    print()

print("=" * 80)
print("SPECIFIC NEXT STEPS:")
print("=" * 80)
print("""
FOR 2019 & 2022 GENERAL ELECTIONS:
  1. Visit Kentucky Secretary of State: elections.ky.gov
     - Look for "Election Results" or "Past Election Results"
     - May have downloadable Excel/CSV format
  
  2. Check OpenElections GitHub:
     - https://github.com/openelections/openelections-data-ky
     - May have transcribed data from these years
  
  3. Try Dave Leip's Atlas:
     - https://uselectionatlas.org/ → Kentucky → 2020 cycle
     - Has county-level results for many elections

FOR 2010/2011 OFF-YEAR ELECTIONS:
  1. Check Kentucky Secretary of State archives
  2. Look for city/county clerk websites
  3. Try state legislative archives

FOR QUICK WINS:
  1. Email Kentucky Secretary of State elections department
     - They often have CSV exports ready to share
  2. Check if Ballotpedia has downloadable data
  3. Search GitHub for "Kentucky elections" + year

WHAT TO LOOK FOR IN DATA:
  ✓ County-level results
  ✓ Candidate names and voles
  ✓ CSV/Excel format (best)
  ✓ UTF-8 encoded if text
""")

print("\n" + "=" * 80)
print("OPEN-ELECTIONS GITHUB CHECK:")
print("=" * 80)
print("""
The OpenElections project is most likely to have this data.
Check: https://github.com/openelections/openelections-data-ky

In the repository, look for:
  - 2019/ folder → CSV files
  - 2022/ folder → CSV files
  - off-year/ or similar folders
  
If found, copy the matching CSV files to your data/ folder.
""")
