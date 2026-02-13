import json

with open('data/ky_election_results.json') as f:
    data = json.load(f)

# Check 2024 structure
year_2024 = data['results_by_year']['2024']
print("2024 keys:", list(year_2024.keys()))

# Get first office type
office_type = list(year_2024.keys())[0]
print(f"\nOffice type: {office_type}")
print(f"Office type keys: {list(year_2024[office_type].keys())}")

# Get first contest
contest_key = list(year_2024[office_type].keys())[0]
contest = year_2024[office_type][contest_key]
print(f"\nContest key: {contest_key}")
print(f"Contest keys: {list(contest.keys())}")

# Check counties in this contest
if 'counties' in contest:
    counties_in_contest = list(contest['counties'].keys())[:5]
    print(f"\nSample counties: {counties_in_contest}")
else:
    print("\nNo 'counties' key found - checking structure...")
    print(f"Contest structure: {list(contest.keys())}")
    # Print the actual structure
    import pprint
    sample = {k: type(v).__name__ for k,v in list(contest.items())[:3]}
    print(f"Sample types: {sample}")
