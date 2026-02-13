"""
Download and aggregate Kentucky election data from OpenElections GitHub.
Converts precinct-level CSV files to county-level aggregates.
"""

import os
import pandas as pd
from pathlib import Path
import urllib.request
import urllib.error
import time

print("=" * 80)
print("OPENELECTIONS DATA AGGREGATOR")
print("=" * 80)

# Configuration
BASE_URL = "https://raw.githubusercontent.com/openelections/openelections-data-ky/master"
DATA_DIR = Path("data")

# Define what to download
jobs = {
    "2010": {
        "url_base": f"{BASE_URL}/2010",
        "file_pattern": "20101102__ky__general__{county}__precinct.csv",
        "output": "20101102__ky__general__county.csv"
    },
    "2011": {
        "url_base": f"{BASE_URL}/2011",
        "file_pattern": "20111108__ky__general__{county}__precinct.csv",
        "output": "20111108__ky__general__county.csv"
    },
    "2019": {
        "url_base": f"{BASE_URL}/2019",
        "file_pattern": "20191105__ky__general__{county}__precinct.csv",
        "output": "20191105__ky__general__county.csv"
    }
}

KY_COUNTIES = [
    'adair', 'allen', 'anderson', 'ballard', 'barren', 'bath', 'bell', 'boone',
    'bourbon', 'boyd', 'boyle', 'bracken', 'breathitt', 'breckinridge', 'bullitt',
    'butler', 'caldwell', 'calloway', 'campbell', 'carlisle', 'carroll', 'carter',
    'casey', 'christian', 'clark', 'clay', 'clinton', 'crittenden', 'cumberland',
    'daviess', 'edmonson', 'elliott', 'estill', 'fayette', 'fleming', 'floyd',
    'franklin', 'fulton', 'gallatin', 'garrard', 'grant', 'graves', 'grayson',
    'green', 'greenup', 'hancock', 'hardin', 'harlan', 'harrison', 'hart',
    'henderson', 'henry', 'hickman', 'hopkins', 'jackson', 'jefferson', 'jessamine',
    'johnson', 'kenton', 'knott', 'knox', 'larue', 'laurel', 'lawrence', 'lee',
    'leslie', 'letcher', 'lewis', 'lincoln', 'livingston', 'logan', 'lyon',
    'madison', 'magoffin', 'marion', 'marshall', 'martin', 'mason', 'mccracken',
    'mccreary', 'mclean', 'meade', 'menifee', 'mercer', 'metcalfe', 'monroe',
    'montgomery', 'morgan', 'muhlenberg', 'nelson', 'nicholas', 'ohio', 'oldham',
    'owen', 'owsley', 'pendleton', 'perry', 'pike', 'powell', 'pulaski',
    'robertson', 'rockcastle', 'rowan', 'russell', 'scott', 'shelby', 'simpson',
    'spencer', 'taylor', 'todd', 'trigg', 'trimble', 'union', 'warren',
    'washington', 'wayne', 'webster', 'whitley', 'wolfe', 'woodford'
]


def download_and_aggregate_year(year, job_config):
    """Download precinct CSVs and aggregate to county level."""
    
    print(f"\n{'='*80}")
    print(f"Processing {year}")
    print(f"{'='*80}")
    
    all_data = []
    downloaded = 0
    failed = 0
    
    for county in KY_COUNTIES:
        filename = job_config["file_pattern"].format(county=county)
        url = f"{job_config['url_base']}/{filename}"
        
        try:
            print(f"  Downloading {county}...", end=" ")
            
            # Download with a short timeout
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read().decode('utf-8')
                
            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(data))
            all_data.append(df)
            
            print(f"✓ ({len(df)} rows)")
            downloaded += 1
            
            # Be nice to the server
            time.sleep(0.2)
            
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"✗ Not found")
            else:
                print(f"✗ Error {e.code}")
            failed += 1
        except Exception as e:
            print(f"✗ Error: {str(e)[:40]}")
            failed += 1
    
    if not all_data:
        print(f"\n❌ No data downloaded for {year}")
        return None
    
    # Combine all data
    print(f"\n  Combining {downloaded} county files...")
    combined = pd.concat(all_data, ignore_index=True)
    
    # Aggregate to county level if precinct data
    if 'precinct' in combined.columns:
        print(f"  Aggregating precinct→county...")
        # Group by county, candidate, party, office and sum votes
        county_col = 'county'
        group_cols = [col for col in ['county', 'candidate', 'party', 'office']
                      if col in combined.columns]
        
        if 'votes' in combined.columns:
            aggregated = combined.groupby(group_cols, as_index=False)['votes'].sum()
        else:
            aggregated = combined
        
        combined = aggregated
    
    # Save
    output_path = DATA_DIR / job_config["output"]
    print(f"  Saving to {output_path}...")
    combined.to_csv(output_path, index=False)
    
    print(f"\n✓ {year} complete: {len(combined)} rows saved")
    return output_path


print("\n🚀 Starting download...\n")

for year, config in jobs.items():
    result = download_and_aggregate_year(year, config)
    if result:
        print(f"  Saved: {result}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
Check your data/ folder for:
  - 20101102__ky__general__county.csv
  - 20111108__ky__general__county.csv
  - 20191105__ky__general__county.csv

Next steps:
  1. Verify the files look good (open 1-2 rows in Excel)
  2. Run: py scripts/check_coverage.py
  3. Compare with your existing files

For 2022:
  - Not found in 2022 folder
  - Try 2022 folder: check for different naming
  - Or check state website: https://elections.ky.gov/
  - Or email: elections@ky.gov
""")

print("\nDone!\n")
