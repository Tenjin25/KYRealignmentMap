"""
Build a JSON manifest of downloaded 2022 recap PDFs.
"""

from pathlib import Path
import json

output_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/2022_recaps")
manifest_path = output_dir / "2022_recaps_manifest.json"

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

manifest = {
    "base_dir": str(output_dir),
    "total_counties": len(counties),
    "files": {},
    "missing": [],
}

for county in counties:
    filename = f"{county} County.pdf"
    file_path = output_dir / filename
    if file_path.exists():
        manifest["files"][county] = {
            "file": str(file_path),
            "status": "downloaded",
        }
    else:
        manifest["missing"].append(county)

manifest["downloaded_count"] = len(manifest["files"])
manifest["missing_count"] = len(manifest["missing"])

manifest_path.write_text(json.dumps(manifest, indent=2))

print("=" * 80)
print("2022 RECAPS MANIFEST")
print("=" * 80)
print(f"Downloaded: {manifest['downloaded_count']}/{manifest['total_counties']}")
print(f"Missing: {manifest['missing_count']}")
print(f"Saved: {manifest_path}")
