"""
Download OpenElections precinct files for ALL years and aggregate each year to county level
Save each year separately: KY_YYYY_OFFICIAL_COUNTY.csv
"""

import pandas as pd
import urllib.request
from pathlib import Path
import time

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")
data_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DOWNLOADING OPENELECTIONS KENTUCKY DATA - ALL YEARS")
print("=" * 80)

base_url = "https://raw.githubusercontent.com/openelections/openelections-data-ky/master"

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

# Years to try (based on what's typically in the repo)
years = [2024, 2023, 2020, 2019, 2018, 2016, 2015, 2014, 2012, 2011, 2010]

print(f"\nWill attempt to download: {len(years)} years × {len(counties)} counties = {len(years) * len(counties)} files\n")

results = {}

statewide_patterns = [
    "{year}1105__ky__general__precinct.csv",
    "{year}1107__ky__general__precinct.csv",
    "{year}1104__ky__general__precinct.csv",
    "{year}1102__ky__general__precinct.csv",
    "{year}1106__ky__general__precinct.csv",
    "{year}1108__ky__general__precinct.csv",
]

for year in years:
    print(f"\n{'=' * 80}")
    print(f"YEAR {year}")
    print(f"{'=' * 80}")
    
    year_data = []
    success_count = 0
    fail_count = 0

    # Try statewide precinct file first
    statewide_loaded = False
    for pattern in statewide_patterns:
        statewide_name = pattern.format(year=year)
        url = f"{base_url}/{year}/{statewide_name}"
        try:
            response = urllib.request.urlopen(url)
            df_statewide = pd.read_csv(response)
            df_statewide.columns = [col.lower().strip() for col in df_statewide.columns]
            year_data.append(df_statewide)
            success_count = 1
            statewide_loaded = True
            print(f"  ✓ statewide file {statewide_name}")
            break
        except Exception:
            continue
    
    if not statewide_loaded:
        for county in counties:
            # Try different filename patterns
            patterns = [
                f"{year}1105__ky__general__{county}__precinct.csv",  # 2024/2023 style
                f"{year}1107__ky__general__{county}__precinct.csv",  # 2023 alternate
                f"{year}1102__ky__general__{county}__precinct.csv",  # 2020/2016 style
                f"{year}1104__ky__general__{county}__precinct.csv",  # 2019/2014 style
                f"{year}1106__ky__general__{county}__precinct.csv",  # 2012 style
                f"{year}1108__ky__general__{county}__precinct.csv",  # 2011 style
                f"{year}1102__ky__general__{county}__precinct.csv",  # 2010 style
            ]

            found = False
            for filename in patterns:
                url = f"{base_url}/{year}/General/{filename}"

                try:
                    response = urllib.request.urlopen(url)
                    df = pd.read_csv(response)

                    # Standardize columns
                    df.columns = [col.lower().strip() for col in df.columns]

                    print(f"  ✓ {county:15} {filename:45}")
                    year_data.append(df)
                    success_count += 1
                    found = True
                    break

                except Exception:
                    pass

            if not found:
                fail_count += 1
    
    if success_count > 0:
        print(f"\n  Downloaded: {success_count}/{len(counties)} counties")
        
        # Combine all counties for this year
        df_year = pd.concat(year_data, ignore_index=True)

        # Aggregate precinct -> county (retain OpenElections schema)
        if 'office' not in df_year.columns:
            df_year['office'] = ''
        if 'district' not in df_year.columns:
            df_year['district'] = ''
        if 'party' not in df_year.columns:
            df_year['party'] = ''

        # Avoid dropping rows due to NaN in group-by fields
        df_year['office'] = df_year['office'].fillna('')
        df_year['district'] = df_year['district'].fillna('')
        df_year['party'] = df_year['party'].fillna('')
        df_year['county'] = df_year['county'].fillna('')
        df_year['candidate'] = df_year['candidate'].fillna('')

        group_cols = ['county', 'office', 'district', 'candidate', 'party']
        df_county = df_year.groupby(group_cols, as_index=False).agg({
            'votes': 'sum'
        })

        df_county['year'] = year
        df_county = df_county[['year', 'county', 'office', 'district', 'candidate', 'party', 'votes']]
        
        # Save
        output_file = data_dir / f"KY_{year}_OFFICIAL_COUNTY.csv"
        df_county.to_csv(output_file, index=False)
        
        total_votes = df_county['votes'].sum()
        total_counties = df_county['county'].nunique()
        total_candidates = df_county['candidate'].nunique()
        
        print(f"  Aggregated: {len(df_county):,} county-level records")
        print(f"  Total votes: {total_votes:,.0f}")
        print(f"  Counties: {total_counties}")
        print(f"  Candidates: {total_candidates:,}")
        print(f"  Saved: {output_file.name}")
        
        results[year] = {
            'records': len(df_county),
            'votes': total_votes,
            'counties': total_counties,
            'candidates': total_candidates,
            'file': output_file.name
        }
        
        time.sleep(0.5)
    else:
        print(f"  ✗ Could not find General election data for {year}")

# Summary
print(f"\n\n" + "=" * 80)
print(f"SUMMARY")
print(f"=" * 80)

if results:
    print(f"\nSuccessfully downloaded and processed {len(results)} years:\n")
    for year in sorted(results.keys(), reverse=True):
        r = results[year]
        print(f"  {year}: {r['records']:>6,} records | {r['votes']:>12,.0f} votes | {r['counties']:>3} counties | {r['file']}")
else:
    print("No data downloaded!")

print(f"\nAll files saved to: {data_dir}")
