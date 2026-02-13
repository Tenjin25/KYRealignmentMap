#!/usr/bin/env python3
"""
Generate county-specific data cards with actual election metrics
Pulls real numbers from election JSON to create data-driven analysis
"""

import json
from statistics import mean, stdev
from collections import defaultdict

# Load election data
with open('data/ky_election_results.json', 'r') as f:
    election_data = json.load(f)

results = election_data['results_by_year']

def get_county_metrics(county_name):
    """Get voting metrics for a county across all years"""
    margins = []
    winners = defaultdict(int)
    
    for year in sorted(results.keys()):
        for office in results[year].values():
            for contest in office.values():
                if 'results' in contest and county_name in contest['results']:
                    county_data = contest['results'][county_name]
                    margin = county_data.get('margin_pct', 0)
                    winner = county_data.get('winner', 'UNKNOWN')
                    margins.append(abs(margin))
                    winners[winner] += 1
    
    if not margins:
        return None
    
    return {
        'avg_margin': mean(margins),
        'max_margin': max(margins),
        'winners': dict(winners),
    }

def get_top_republican_counties(n=5):
    """Get counties with highest Republican average margins"""
    county_metrics = {}
    
    all_counties = set()
    for year in results.values():
        for office in year.values():
            for contest in office.values():
                if 'results' in contest:
                    all_counties.update(contest['results'].keys())
    
    for county in all_counties:
        metrics = get_county_metrics(county)
        if metrics:
            county_metrics[county] = metrics['avg_margin']
    
    sorted_counties = sorted(county_metrics.items(), key=lambda x: x[1], reverse=True)
    return sorted_counties[:n]

def get_top_democratic_counties(n=5):
    """Get counties with highest Democratic average margins"""
    county_metrics = {}
    
    all_counties = set()
    for year in results.values():
        for office in year.values():
            for contest in office.values():
                if 'results' in contest:
                    all_counties.update(contest['results'].keys())
    
    for county in all_counties:
        metrics = get_county_metrics(county)
        if metrics:
            county_metrics[county] = metrics['avg_margin']
    
    # Get counties with DEM wins
    dem_counties = {}
    for year in results.values():
        for office in year.values():
            for contest in office.values():
                if 'results' in contest:
                    for county, data in contest['results'].items():
                        if data.get('winner') == 'DEM':
                            if county not in dem_counties:
                                dem_counties[county] = 0
                            dem_counties[county] += 1
    
    sorted_counties = sorted(dem_counties.items(), key=lambda x: x[1], reverse=True)
    return sorted_counties[:n]

def get_county_swing(county_name):
    """Get swing change in a county from first to last year"""
    first_year_margin = None
    last_year_margin = None
    
    years = sorted(results.keys())
    
    # Get first year
    for year in years:
        for office in results[year].values():
            for contest in office.values():
                if 'results' in contest and county_name in contest['results']:
                    if first_year_margin is None:
                        data = contest['results'][county_name]
                        first_year_margin = data.get('margin_pct', 0)
                        first_year = year
                    break
    
    # Get last year
    for year in reversed(years):
        for office in results[year].values():
            for contest in office.values():
                if 'results' in contest and county_name in contest['results']:
                    if last_year_margin is None:
                        data = contest['results'][county_name]
                        last_year_margin = data.get('margin_pct', 0)
                        last_year = year
                    break
    
    if first_year_margin is not None and last_year_margin is not None:
        swing = last_year_margin - first_year_margin
        return {
            'first_year': first_year,
            'first_margin': first_year_margin,
            'last_year': last_year,
            'last_margin': last_year_margin,
            'swing': swing,
        }
    
    return None

# Generate analysis
print("=" * 80)
print("COUNTY-SPECIFIC ELECTORAL ANALYSIS - KENTUCKY 2000-2024")
print("=" * 80)

# Top Republican counties
print("\n📊 TOP REPUBLICAN COUNTIES (by average margin 2000-2024)")
print("-" * 80)
rep_counties = get_top_republican_counties(5)
for i, (county, margin) in enumerate(rep_counties, 1):
    print(f"{i}. {county:20} R+{margin:5.1f}%")

# Top Democratic counties
print("\n📊 TOP DEMOCRATIC COUNTIES (by favorable results)")
print("-" * 80)
dem_counties = get_top_democratic_counties(5)
for i, (county, wins) in enumerate(dem_counties, 1):
    print(f"{i}. {county:20} DEM wins in {wins} contests")

# County swings
print("\n📊 BIGGEST RIGHTWARD SHIFTS (2000-2024)")
print("-" * 80)

all_counties = set()
for year in results.values():
    for office in year.values():
        for contest in office.values():
            if 'results' in contest:
                all_counties.update(contest['results'].keys())

swings = []
for county in all_counties:
    swing_data = get_county_swing(county)
    if swing_data:
        swings.append((county, swing_data['swing']))

swings.sort(key=lambda x: x[1], reverse=True)

for i, (county, swing) in enumerate(swings[:5], 1):
    direction = "→ DEM" if swing < 0 else "→ REP"
    print(f"{i}. {county:20} {swing:+6.1f}% {direction}")

print("\n" + "=" * 80)
print("Data analysis complete")
print("=" * 80)
