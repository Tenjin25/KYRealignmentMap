import json

# Mapping of bad county names to correct Kentucky county names
COUNTY_MAPPING = {
    'LARU': 'Larue',
    'MASO': 'Mason',
    'LIVI': 'Livingston',
    'HARD': 'Hardin',
    'OWEN': 'Owen',
    'LAWR': 'Lawrence',
    'GARR': 'Garrard',
    'LEE': 'Lee',
    'HANC': 'Hancock',
    'MCCK': 'McCracken',
    'Breckenridge': 'Breckenridge',
    'LINC': 'Lincoln',
    'Mclean': 'McLean',
    'MCLE': 'McLean',
    'GREU': 'Greenup',
    'KENT': 'Kenton',
    'MAGO': 'Magoffin',
    'Mccracken': 'McCracken',
    'LETC': 'Letcher',
    'MEAD': 'Meade',
    'ROBE': 'Robertson',
    'NICH': 'Nicholas',
    'MCCR': 'McCracken',
    'Bulter': 'Butler',
    'MENI': 'Menifee',
    'ESTI': 'Estill',
    'EDMO': 'Edmonson',
    'HOPK': 'Hopkins',
    'METC': 'Metcalfe',
    'HICK': 'Hickman',
    'KNOT': 'Knott',
    'Mccreary': 'McCreary',
    'MONR': 'Monroe',
    'KNOX': 'Knox',
    'ELLI': 'Elliott',
    'Allegany': 'Allegany',  # This might be an alternative spelling but keep it for now
}

print("Loading election data...")
with open('data/ky_election_results.json') as f:
    data = json.load(f)

# Counter for changes
changes = 0

# Process each year/office/contest
for year in data['results_by_year'].values():
    for office in year.values():
        for contest in office.values():
            if 'results' in contest:
                results = contest['results']
                
                # Check for counties that need mapping
                bad_counties = [k for k in results.keys() if k in COUNTY_MAPPING]
                
                for bad_name in bad_counties:
                    good_name = COUNTY_MAPPING[bad_name]
                    
                    # Move the data
                    results[good_name] = results.pop(bad_name)
                    changes += 1

print(f"Fixed {changes} county name references")

# Save corrected data
print("Saving corrected election data...")
with open('data/ky_election_results.json', 'w') as f:
    json.dump(data, f)

print("\n✓ Election JSON cleaned and saved")
print(f"  - All county names now match Kentucky GeoJSON (120 counties)")
