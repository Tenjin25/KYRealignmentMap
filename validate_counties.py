#!/usr/bin/env python3
"""
Create additional county name mappings for better matching
Handles abbreviations, alternate spellings, etc.
"""

import json

# Load both files
with open('data/ky_election_results.json', 'r') as f:
    election_data = json.load(f)

with open('data/tl_2020_21_county20/tl_2020_21_county20.geojson', 'r') as f:
    geojson_data = json.load(f)

# Extract county names from both sources
election_counties = set()
for year in election_data['results_by_year'].values():
    for office in year.values():
        for contest in office.values():
            if 'results' in contest:
                election_counties.update(contest['results'].keys())

geojson_counties = set()
for feature in geojson_data['features']:
    name = feature['properties'].get('NAME20', '')
    if name:
        geojson_counties.add(name)

# Check for mismatches
print("GeoJSON County Names (sorted):")
print(f"  Total: {len(sorted(geojson_counties))}")

print("\nElection County Names (sorted):")
print(f"  Total: {len(sorted(election_counties))}")

# Find matching/missing
matching = election_counties & geojson_counties
missing_in_geojson = election_counties - geojson_counties
missing_in_election = geojson_counties - election_counties

print(f"\n✓ Matching:         {len(matching)}")
print(f"✗ Missing in GeoJSON: {len(missing_in_geojson)}")
print(f"✗ Missing in Election: {len(missing_in_election)}")

if missing_in_geojson:
    print("\nMissing in GeoJSON:")
    for county in sorted(missing_in_geojson):
        print(f"  - {county}")

if missing_in_election:
    print("\nMissing in Election Data:")
    for county in sorted(missing_in_election):
        print(f"  - {county}")

# Create mapping for any abbreviations or alternate names
COUNTY_ABBREVIATIONS = {
    # Common abbreviations (add as needed based on findings)
    'Ky': 'Kentucky',
    'St': 'Saint',  # For counties with "Saint" in name
}

# Create aliases for counties that might appear abbreviated
COUNTY_ALIASES = {
    # Example: 'Mcd': 'McCreary',
    # Add as needed
}

print("\n✓ County name validation complete")
print(f"  Matching counties: {len(matching)} / 120")

# Save statistics
stats = {
    'total_geojson': len(geojson_counties),
    'total_election': len(election_counties),
    'matching': len(matching),
    'missing_in_geojson': sorted(list(missing_in_geojson)),
    'missing_in_election': sorted(list(missing_in_election)),
}

with open('county_validation_report.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("\n✓ Validation report saved to county_validation_report.json")
