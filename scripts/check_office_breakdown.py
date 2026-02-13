"""
Check if data includes multiple offices that need to be separated
"""

import pandas as pd
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data")

# Check raw files to see if they have office info
raw_2024 = data_dir / "20241105__ky__general__county.csv"
df_raw = pd.read_csv(raw_2024)

print("=" * 80)
print("CHECKING RAW 2024 DATA STRUCTURE")
print("=" * 80)

print(f"\nColumns: {list(df_raw.columns)}")
print(f"Total records: {len(df_raw):,}")
print(f"Total votes: {df_raw['votes'].sum():,.0f}")

if 'office' in df_raw.columns:
    print(f"\nOffices in dataset: {df_raw['office'].nunique()}")
    print("\nVotes by office:")
    votes_by_office = df_raw.groupby('office')['votes'].sum().sort_values(ascending=False)
    for office, votes in votes_by_office.items():
        print(f"  {office:50} {votes:>12,.0f}")
    
    # Just President
    pres_only = df_raw[df_raw['office'] == 'President']
    print(f"\nPresident only: {len(pres_only):,} records, {pres_only['votes'].sum():,.0f} votes")
    
    trump_pres = pres_only[pres_only['candidate'] == 'Donald J. Trump']
    harris_pres = pres_only[pres_only['candidate'] == 'Kamala D. Harris']
    
    print(f"  Trump: {trump_pres['votes'].sum():,.0f}")
    print(f"  Harris: {harris_pres['votes'].sum():,.0f}")

# Check across all years
print(f"\n" + "=" * 80)
print(f"PROPOSAL: FILTER TO PRESIDENTIALONLY")
print(f"=" * 80)

# Load our final clean file and see what happens if we filter
df_final = pd.read_csv(data_dir / "KY_ELECTIONS_FINAL_CLEAN.csv")

print(f"\nCurrent dataset: {len(df_final):,} records, {df_final['votes'].sum():,.0f} votes")

# If we filter to only candidatesnamed Trump/Harris/Biden/etc
presidential_candidates = [
    'Donald J. Trump', 'Donald J Trump', 'Donald Trump',
    'Joseph R. Biden', 'Joseph Biden',
    'Kamala D. Harris', 'Kamala Harris',
    'Barack Hussein Obama', 'John McCain',
    'Mitt Romney', 'George W. Bush',
    'John F. Kerry', 'Al Gore'
]

df_pres = df_final[df_final['candidate'].isin(presidential_candidates)]
print(f"\nFiltered to known presidential candidates: {len(df_pres):,} records")
print(f"Total votes: {df_pres['votes'].sum():,.0f}")

trump_filtered = df_pres[df_pres['candidate'].str.contains('Trump', case=False, na=False)]['votes'].sum()
print(f"Trump total: {trump_filtered:,.0f}")

# By year
print(f"\nTrump by year (filtered to known presidential candidates):")
trump_by_year = df_pres[df_pres['candidate'].str.contains('Trump', case=False, na=False)].groupby('year')['votes'].sum()
for year, votes in trump_by_year.items():
    print(f"  {year}: {votes:>12,.0f}")
