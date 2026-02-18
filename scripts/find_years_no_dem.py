import json
from pathlib import Path

json_path = Path("data/ky_election_results.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

results_by_year = data.get("results_by_year", {})
no_dem_years = []
summary = {}

for year, offices in results_by_year.items():
    dem_found = False
    for office, contests in offices.items():
        for contest, contest_data in contests.items():
            for county, result in contest_data["results"].items():
                if result.get("dem_votes", 0) > 0 or result.get("dem_candidate"):
                    dem_found = True
                    break
            if dem_found:
                break
        if dem_found:
            break
    if not dem_found:
        no_dem_years.append(year)
    summary[year] = dem_found

print("Years with NO Dem candidates:")
for year in no_dem_years:
    print(year)

print("\nSummary (year: has_dem):")
for year, has_dem in sorted(summary.items()):
    print(f"{year}: {'YES' if has_dem else 'NO'}")
