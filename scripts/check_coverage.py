"""Check which election years are covered in data folder."""

from pathlib import Path
from collections import defaultdict

csv_dir = Path("data")

# Extract years from filenames
years = defaultdict(list)
for csv in csv_dir.glob("*.csv"):
    name = csv.name
    if name.startswith("20"):  # Election date starts with 20
        year = name[:4]
        race_type = "General" if "__general__" in name else "Other"
        years[year].append((name, race_type))

print("=" * 80)
print("EXISTING DATA COVERAGE")
print("=" * 80)

for year in sorted(years.keys(), reverse=True):
    races = years[year]
    print(f"\n{year}: {len(races)} file(s)")
    for filename, race_type in races:
        print(f"     📊 {filename}")

print("\n" + "=" * 80)
print("MISSING YEARS (SCANNED PDFs)")
print("=" * 80)
missing = {
    "2019": "2019 General Certified Results.pdf (SCANNED)",
    "2022": "2022 Certified General Election Results.pdf (SCANNED)",
    "2010 (Off-year)": "off2010gen.pdf (SCANNED)",
    "2011 (Off-year)": "off2011gen.pdf (SCANNED)"
}
for year, desc in missing.items():
    print(f"❌ {year}: {desc}")

print("\n" + "=" * 80)
print("AVAILABLE FOR QUICK EXTRACTION (from PDFs with text)")
print("=" * 80)
quick_extract = {
    "2014": "2014 General Election Results.pdf",
    "2015": "2015 General Election Results.pdf", 
    "2016": "2016 General Election Results.pdf",
    "2023": "Certification of Election Results for 2023 General Election Final.pdf"
}
for year, desc in quick_extract.items():
    if Path(f"data/{desc}").exists():
        print(f"✅ {year}: {desc}")
    else:
        print(f"⚠️  {year}: PDF not found")
