import json
import copy

# Load Kentucky GeoJSON
print("Loading Kentucky GeoJSON...")
with open('data/tl_2020_21_county20/tl_2020_21_county20.geojson') as f:
    geojson = json.load(f)

# Load election data
print("Loading election results...")
with open('data/ky_election_results.json') as f:
    election_data = json.load(f)

# Create a mapping of valid Kentucky counties (from GeoJSON)
valid_counties = {}
for feature in geojson['features']:
    name = feature['properties'].get('NAME20')
    if name:
        valid_counties[name] = feature

print(f"Found {len(valid_counties)} Kentucky counties")

# Merge election data into each county feature
print("Merging election data...")

for county_name, feature in valid_counties.items():
    county_elections = {}
    
    # Extract election results for this county across all years
    for year, offices in election_data['results_by_year'].items():
        county_elections[year] = {}
        
        for office_name, contests in offices.items():
            for contest_key, contest in contests.items():
                # Get results for this county if it exists
                if 'results' in contest and county_name in contest['results']:
                    county_result = contest['results'][county_name]
                    
                    # Store the result  
                    contest_id = f"{office_name}_{contest_key}"
                    county_elections[year][contest_id] = {
                        'contest_name': county_result.get('contest_name'),
                        'dem_votes': county_result.get('dem_votes', 0),
                        'rep_votes': county_result.get('rep_votes', 0),
                        'other_votes': county_result.get('other_votes', 0),
                        'total_votes': county_result.get('total_votes', 0),
                        'winner': county_result.get('winner'),
                        'margin': county_result.get('margin'),
                        'margin_pct': county_result.get('margin_pct'),
                        'competitiveness': county_result.get('competitiveness'),
                    }
    
    # Add elections to feature properties
    if county_elections:
        feature['properties']['elections'] = county_elections

print(f"Merged election data into {len(valid_counties)} features")

# Save the merged GeoJSON
output_path = 'data/kentucky_counties.geojson'
print(f"Saving to {output_path}...")
with open(output_path, 'w') as f:
    json.dump(geojson, f)

print(f"✓ Merged GeoJSON saved successfully")
print(f"  - Counties: {len(geojson['features'])}")
print(f"  - Years available: 2000, 2002-2004, 2007-2008, 2012-2024")
print(f"  - File size: {len(json.dumps(geojson)) / 1024 / 1024:.2f} MB")
