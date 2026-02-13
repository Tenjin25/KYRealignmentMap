"""
Check OpenElections GitHub repository for Kentucky election data.
Guides you through finding and downloading the missing years.
"""

print("=" * 80)
print("OPENELECTIONS GITHUB - KENTUCKY DATA FINDER")
print("=" * 80)

repos = {
    "2019 General": {
        "url": "https://github.com/openelections/openelections-data-ky/tree/master/2019",
        "look_for": [
            "20190105__ky__general__county.csv",
            "*general*county.csv"
        ]
    },
    "2022 General": {
        "url": "https://github.com/openelections/openelections-data-ky/tree/master/2022",
        "look_for": [
            "20221108__ky__general__county.csv",
            "*general*county.csv"
        ]
    },
    "2010 Off-Year": {
        "url": "https://github.com/openelections/openelections-data-ky/tree/master/2010",
        "look_for": [
            "*general*county.csv",
            "*.csv"
        ]
    },
    "2011 Off-Year": {
        "url": "https://github.com/openelections/openelections-data-ky/tree/master/2011",
        "look_for": [
            "*general*county.csv",
            "*.csv"
        ]
    }
}

print("\n🔍 OPENELECTIONS GITHUB REPOSITORY\n")
print("Base repository: https://github.com/openelections/openelections-data-ky\n")

for year, info in repos.items():
    print(f"\n{year}:")
    print(f"  URL: {info['url']}")
    print(f"  Look for files like: {', '.join(info['look_for'])}")

print("\n" + "=" * 80)
print("STEP-BY-STEP: HOW TO DOWNLOAD FROM GITHUB")
print("=" * 80)

instructions = """
1. VISIT THE REPOSITORY
   Go to: https://github.com/openelections/openelections-data-ky

2. NAVIGATE TO YOUR YEAR
   Click on the folder for the year you need:
   - 2019 (governor election)
   - 2022 (senate/congressional)
   - 2010 (off-year)  
   - 2011 (off-year)

3. FIND THE CSV FILE
   Look for county-level results CSV file
   Usually named: YYYYMMDD__ky__general__county.csv
   
   Example:
   - 2019: 20190105__ky__general__county.csv
   - 2022: 20221108__ky__general__county.csv

4. DOWNLOAD THE FILE
   Option A (EASY):
     - Click on the CSV file
     - Click the "Raw" button (top right)
     - Right-click → "Save as..."
     - Save to: data/ folder
   
   Option B (Direct download):
     - Click on the CSV file name
     - Click the download button (⬇️ icon)
     - Choose save location

5. VERIFY THE FILE
   - Open in Excel to check it looks good
   - Should have columns: county, candidate, party, votes, office
   - Should NOT look scrambled

6. REPEAT FOR OTHER YEARS
   Go back to step 2 and repeat for 2022, 2010, 2011
"""

print(instructions)

print("\n" + "=" * 80)
print("WHAT IF FILES DON'T EXIST ON GITHUB?")
print("=" * 80)
print("""
If the CSV files aren't in those folders:

Option 1: Check related files
  - Look for .txt files (might be easier to parse)
  - Look for files without "county" in name
  - Check if there's a README.md with info

Option 2: Try the State Website
  Go to: https://elections.ky.gov/results-and-data/
  Look for download options for those years

Option 3: Email the Kentucky Secretary of State
  elections@ky.gov
  Subject: "Request CSV export - 2019, 2022, 2010, 2011 election results"
  (They often have these ready to share)

Option 4: Try Dave Leip's Atlas
  https://uselectionatlas.org/RESULTS/state.php?f=0&year=2019&off=0
  (Can copy/paste table data into Excel)
""")

print("\n" + "=" * 80)
print("AFTER YOU DOWNLOAD THE FILES")
print("=" * 80)
print("""
1. Save all CSV files to: data/ folder

2. Make sure filenames follow the pattern:
   YYYYMMDD__ky__general__county.csv
   
   Examples:
   - 20190105__ky__general__county.csv (for 2019)
   - 20221108__ky__general__county.csv (for 2022)

3. Open each file in Excel to verify:
   ✓ Headers look correct
   ✓ Data is readable (not scrambled like the manual conversions)
   ✓ Has county names and vote counts

4. Tell me when you've saved them!
   I can then verify and integrate them into your project.
""")

print("\n✨ Let me know what you find!\n")
