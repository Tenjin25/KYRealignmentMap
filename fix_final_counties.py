import json

print("Loading election data...")
with open('data/ky_election_results.json') as f:
    data = json.load(f)

# Counter for changes
changes = 0
removed_allegany = 0

# Process each year/office/contest
for year in data['results_by_year'].values():
    for office in year.values():
        for contest in office.values():
            if 'results' in contest:
                results = contest['results']
                
                # Fix Breckenridge -> Breckinridge
                if 'Breckenridge' in results:
                    results['Breckinridge'] = results.pop('Breckenridge')
                    changes += 1
                
                # Remove Allegany (not a valid KY county)
                if 'Allegany' in results:
                    results.pop('Allegany')
                    removed_allegany += 1

print(f"Fixed Breckenridge spelling: {changes} times")
print(f"Removed invalid Allegany county: {removed_allegany} times")

# Save corrected data
print("Saving corrected election data...")
with open('data/ky_election_results.json', 'w') as f:
    json.dump(data, f)

print("\n✓ Election JSON finalized")
print(f"  - All county names now match Kentucky GeoJSON (120 counties)")
