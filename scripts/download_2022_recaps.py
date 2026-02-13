"""
Download all 2022 General Recap PDF sheets (one per county).
Source: https://elect.ky.gov/results/2020-2029/Pages/2022-General-Recap-Sheets.aspx
"""

from pathlib import Path
import urllib.request

base_url = "https://elect.ky.gov/results/2020-2029/2022ElectionReports/GeneralRecaps"
output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/2022_recaps")
output_dir.mkdir(exist_ok=True)

counties = [
    "Adair", "Allen", "Anderson", "Ballard", "Barren", "Bath", "Bell", "Boone",
    "Bourbon", "Boyd", "Boyle", "Bracken", "Breathitt", "Breckinridge", "Bullitt",
    "Butler", "Caldwell", "Calloway", "Campbell", "Carlisle", "Carroll", "Carter",
    "Casey", "Christian", "Clark", "Clay", "Clinton", "Crittenden", "Cumberland",
    "Daviess", "Edmonson", "Elliott", "Estill", "Fayette", "Fleming", "Floyd",
    "Franklin", "Fulton", "Gallatin", "Garrard", "Grant", "Graves", "Grayson",
    "Green", "Greenup", "Hancock", "Hardin", "Harlan", "Harrison", "Hart",
    "Henderson", "Henry", "Hickman", "Hopkins", "Jackson", "Jefferson", "Jessamine",
    "Johnson", "Kenton", "Knott", "Knox", "Larue", "Laurel", "Lawrence", "Lee",
    "Leslie", "Letcher", "Lewis", "Lincoln", "Livingston", "Logan", "Lyon",
    "Madison", "Magoffin", "Marion", "Marshall", "Martin", "Mason", "McCracken",
    "McCreary", "McLean", "Meade", "Menifee", "Mercer", "Metcalfe", "Monroe",
    "Montgomery", "Morgan", "Muhlenberg", "Nelson", "Nicholas", "Ohio", "Oldham",
    "Owen", "Owsley", "Pendleton", "Perry", "Pike", "Powell", "Pulaski",
    "Robertson", "Rockcastle", "Rowan", "Russell", "Scott", "Shelby", "Simpson",
    "Spencer", "Taylor", "Todd", "Trigg", "Trimble", "Union", "Warren",
    "Washington", "Wayne", "Webster", "Whitley", "Wolfe", "Woodford"
]

print("=" * 80)
print("DOWNLOADING 2022 GENERAL RECAP PDFS")
print("=" * 80)
print(f"Output: {output_dir}")

success = 0
failures = []

for county in counties:
    filename = f"{county} County.pdf"
    url = f"{base_url}/{filename.replace(' ', '%20')}"
    out_path = output_dir / filename

    if out_path.exists():
        print(f"  - {filename} (already exists)")
        success += 1
        continue

    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request) as response:
            out_path.write_bytes(response.read())
        success += 1
        print(f"  ✓ {filename}")
    except Exception as exc:
        failures.append((county, str(exc)))
        print(f"  ✗ {filename} ({exc})")

print("\nDone.")
print(f"Downloaded: {success}/{len(counties)}")
if failures:
    print("Failed:")
    for county, err in failures:
        print(f"  - {county}: {err}")
