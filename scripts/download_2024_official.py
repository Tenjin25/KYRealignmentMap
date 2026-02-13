"""
Download OpenElections precinct files and aggregate to county level
"""

import pandas as pd
import urllib.request
from pathlib import Path
import time

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")
data_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DOWNLOADING OPENELECTIONS 2024 PRECINCT DATA")
print("=" * 80)

base_url = "https://raw.githubusercontent.com/openelections/openelections-data-ky/master/2024/General"

# All 120 Kentucky counties
counties = [
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

print(f"\nDownloading {len(counties)} county precinct files...\n")

all_data = []
success_count = 0
fail_count = 0

for county in counties:
    filename = f"20241105__ky__general__{county}__precinct.csv"
    url = f"{base_url}/{filename}"
    
    try:
        print(f"  {county:15}", end=" ", flush=True)
        
        response = urllib.request.urlopen(url)
        df = pd.read_csv(response)
        
        # Standardize columns
        df.columns = [col.lower().strip() for col in df.columns]
        
        print(f"✓ ({len(df)} rows)")
        all_data.append(df)
        success_count += 1
        
        time.sleep(0.1)  # Be nice to GitHub
        
    except Exception as e:
        print(f"✗ ({str(e)[:30]})")
        fail_count += 1

print(f"\n✓ Downloaded {success_count}/{len(counties)} files")

if len(all_data) == 0:
    print("ERROR: No files downloaded!")
    exit(1)

# Combine all
print(f"\nCombining {len(all_data)} files...")
df_combined = pd.concat(all_data, ignore_index=True)

print(f"  Total records: {len(df_combined):,}")
print(f"  Total votes: {df_combined['votes'].sum():,.0f}")

# Aggregate precinct -> county
print(f"\nAggregating precinct -> county...")
df_county = df_combined.groupby(['county', 'candidate'], as_index=False).agg({
    'votes': 'sum',
    'party': 'first'
})

df_county['year'] = 2024
df_county = df_county[['county', 'candidate', 'party', 'votes', 'year']]

print(f"  County-level records: {len(df_county):,}")
print(f"  Total votes: {df_county['votes'].sum():,.0f}")

# Summary
print(f"\n" + "=" * 80)
print(f"2024 OFFICIAL DATA")
print(f"=" * 80)

print(f"\nRecords: {len(df_county):,}")
print(f"Total votes: {df_county['votes'].sum():,.0f}")
print(f"Counties: {df_county['county'].nunique()}")
print(f"Candidates: {df_county['candidate'].nunique():,}")

print(f"\nTop 10 candidates:")
top10 = df_county.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
for idx, (name, votes) in enumerate(top10.items(), 1):
    print(f"{idx:2}. {name:35} {votes:>12,.0f}")

# Save
output_file = data_dir / "KY_2024_OFFICIAL.csv"
df_county.to_csv(output_file, index=False)
print(f"\n✓ Saved: {output_file}")

print(f"\n" + "=" * 80)
print(f"EXPECTED vs ACTUAL")
print(f"=" * 80)
print(f"\nKentucky 2024 General Election certified results:")
print(f"  Trump (R):  1,463,092")
print(f"  Harris (D): 1,026,622")
print(f"  Total:      ~2.7M")
print(f"\nOur downloaded data:")
trump = df_county[df_county['candidate'].str.contains('Trump', case=False, na=False)]['votes'].sum()
harris = df_county[df_county['candidate'].str.contains('Harris', case=False, na=False)]['votes'].sum()
print(f"  Trump:      {trump:,.0f}")
print(f"  Harris:     {harris:,.0f}")
print(f"  Total:      {df_county['votes'].sum():,.0f}")
