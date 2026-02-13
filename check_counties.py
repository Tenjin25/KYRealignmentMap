import json

# Load election results
with open('data/ky_election_results.json') as f:
    data = json.load(f)

# Extract all unique county names from election data
counties = set()
for year in data['results_by_year'].values():
    for office in year.values():
        for contest in office.values():
            # Counties are in the 'results' key
            for county in contest.get('results', {}).keys():
                counties.add(county)

print(f"Found {len(counties)} counties in election data")
print("\nFirst 10 counties:")
for county in sorted(list(counties))[:10]:
    print(f"  - {county}")

# Load GeoJSON to check county names there
with open('data/tl_2020_21_county20/tl_2020_21_county20.geojson') as f:
    geojson = json.load(f)

geojson_counties = set()
for feature in geojson['features']:
    name = feature['properties'].get('NAME20')
    if name:
        geojson_counties.add(name)

print(f"\nFound {len(geojson_counties)} counties in GeoJSON")
print("First 10 GeoJSON counties:")
for county in sorted(list(geojson_counties))[:10]:
    print(f"  - {county}")

# Check for matches
print("\n" + "="*60)
print("COUNTY NAME MATCHING CHECK")
print("="*60)

election_counties = set(counties)
geojson_counties_set = geojson_counties

matching = election_counties & geojson_counties_set
missing_in_geojson = election_counties - geojson_counties_set
missing_in_election = geojson_counties_set - election_counties

print(f"\nMatching counties: {len(matching)}")
print(f"Missing in GeoJSON: {len(missing_in_geojson)}")
if missing_in_geojson:
    print(f"  {missing_in_geojson}")
print(f"Missing in Election JSON: {len(missing_in_election)}")
if missing_in_election:
    print(f"  {missing_in_election}")
