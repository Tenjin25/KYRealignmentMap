"""
Manually add missing counties to 2010 Senate extraction.
Missing: Caldwell, Casey, Greenup, Harlan, Woodford
"""

import pandas as pd
from pathlib import Path

# Load existing data
csv_path = Path('data/20101102__ky__general__senate__county.csv')
df = pd.read_csv(csv_path)

print("="*70)
print("Add Missing Counties - 2010 US Senate")
print("="*70)
print("\nCurrent data:")
print(f"  Counties: {df['county'].nunique()}/120")
print(f"  Total votes: {df['votes'].sum():,}")

missing_counties = ['Caldwell', 'Casey', 'Greenup', 'Harlan', 'Woodford']
print(f"\nMissing counties: {', '.join(missing_counties)}")

candidates = [
    {'name': 'Rand Paul', 'party': 'REP'},
    {'name': 'Jack Conway', 'party': 'DEM'},
    {'name': 'Billy Ray Wilson', 'party': 'WI'}
]

print("\n" + "="*70)
print("Enter vote counts for each county")
print("="*70)
print("Format: RandPaul JackConway BillyRayWilson (space-separated)")
print("Example: 5280 3145 12")
print("(Press Enter to skip a county)\n")

new_rows = []

for county in missing_counties:
    votes_input = input(f"{county}: ").strip()
    
    if not votes_input:
        print(f"  Skipped {county}")
        continue
    
    try:
        votes = [int(v.replace(',', '')) for v in votes_input.split()]
        
        if len(votes) != 3:
            print(f"  ⚠ Error: Need 3 values, got {len(votes)}. Skipping.")
            continue
        
        # Add rows for each candidate
        for i, cand_info in enumerate(candidates):
            new_rows.append({
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
        
        print(f"  ✓ Added {county}: Paul={votes[0]:,}, Conway={votes[1]:,}, Wilson={votes[2]}")
    
    except ValueError as e:
        print(f"  ⚠ Error parsing votes for {county}: {e}")
        continue

if new_rows:
    # Add new rows to dataframe
    new_df = pd.DataFrame(new_rows)
    df = pd.concat([df, new_df], ignore_index=True)
    
    # Save updated CSV
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*70)
    print("✓ UPDATED")
    print("="*70)
    print(f"\nAdded {len(new_rows)//3} counties")
    print(f"New total counties: {df['county'].nunique()}/120")
    print(f"New total votes: {df['votes'].sum():,}")
    
    print("\nUpdated results:")
    for cand, votes in df.groupby('candidate')['votes'].sum().sort_values(ascending=False).items():
        party = df[df['candidate'] == cand]['party'].iloc[0]
        pct = 100 * votes / df['votes'].sum()
        winner = "  ✓ WINNER" if votes == df.groupby('candidate')['votes'].sum().max() else ""
        print(f"  {cand:35s} ({party:3s}) {votes:10,} ({pct:5.2f}%){winner}")
else:
    print("\nNo counties added.")
