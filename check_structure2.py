import json

with open('data/ky_election_results.json') as f:
    data = json.load(f)

# Check 2024 structure
year_2024 = data['results_by_year']['2024']
contest = year_2024['President']['President']
results = contest['results']

print("Keys in 'results':", list(results.keys())[:5])

# Check if counties are keys
counties_sample = list(results.keys())[:5]
print(f"\nSample 'results' keys (these should be counties): {counties_sample}")

# Check structure of one county result
first_county_key = counties_sample[0]
first_county_value = results[first_county_key]
print(f"\nStructure of '{first_county_key}': {type(first_county_value)}")
if isinstance(first_county_value, dict):
    print(f"Keys: {list(first_county_value.keys())}")
