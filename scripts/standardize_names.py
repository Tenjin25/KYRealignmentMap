"""
Second pass: Fix remaining data quality issues.
- Standardize candidate names (capitalization, spacing)
- Identify non-Kentucky counties
- Merge duplicate candidates
"""

import pandas as pd
from pathlib import Path
import sys

print("=" * 80)
print("SECOND CLEANING PASS - NAME STANDARDIZATION")
print("=" * 80, flush=True)

cleaned_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_ELECTIONS_CLEANED.csv")

df = pd.read_csv(cleaned_file)

print(f"\nStarting size: {len(df):,} rows")
print(f"Unique candidates: {df['candidate'].nunique():,}")
print(f"Unique counties: {df['county'].nunique()}")

# Step 1: Standardize candidate names
print("\n" + "="*80)
print("STEP 1: STANDARDIZE CANDIDATE NAMES")
print("="*80)

# Function to clean candidate names
def standardize_name(name):
    if pd.isna(name):
        return name
    
    name = str(name).strip()
    
    # Title case each word
    words = name.split()
    standardized_words = []
    
    for word in words:
        # Remove trailing punctuation
        word = word.rstrip('.,')
        
        # Special cases
        if word.lower() in ['jr', 'sr', 'iii', 'ii', 'iv']:
            standardized_words.append(word.upper())
        elif '/' in word:
            # Handle hyphenated or combined names
            standardized_words.append(word.lower())
        else:
            # Title case
            standardized_words.append(word.title())
    
    return ' '.join(standardized_words)

# Apply standardization
df['candidate'] = df['candidate'].apply(standardize_name)
df['county'] = df['county'].apply(lambda x: x.strip().title() if pd.notna(x) else x)

print(f"After standardization: {df['candidate'].nunique():,} unique candidates")

# Step 2: Find extra counties
print("\n" + "="*80)
print("STEP 2: IDENTIFY POTENTIAL NON-COUNTY ENTRIES")
print("="*80)

ky_counties = [
    'Adair', 'Allen', 'Anderson', 'Ballard', 'Barren', 'Bath', 'Bell', 'Boone',
    'Bourbon', 'Boyd', 'Boyle', 'Bracken', 'Breathitt', 'Breckinridge', 'Bullitt',
    'Butler', 'Caldwell', 'Calloway', 'Campbell', 'Carlisle', 'Carroll', 'Carter',
    'Casey', 'Christian', 'Clark', 'Clay', 'Clinton', 'Crittenden', 'Cumberland',
    'Daviess', 'Edmonson', 'Elliott', 'Estill', 'Fayette', 'Fleming', 'Floyd',
    'Franklin', 'Fulton', 'Gallatin', 'Garrard', 'Grant', 'Graves', 'Grayson',
    'Green', 'Greenup', 'Hancock', 'Hardin', 'Harlan', 'Harrison', 'Hart',
    'Henderson', 'Henry', 'Hickman', 'Hopkins', 'Jackson', 'Jefferson', 'Jessamine',
    'Johnson', 'Kenton', 'Knott', 'Knox', 'Larue', 'Laurel', 'Lawrence', 'Lee',
    'Leslie', 'Letcher', 'Lewis', 'Lincoln', 'Livingston', 'Logan', 'Lyon',
    'Madison', 'Magoffin', 'Marion', 'Marshall', 'Martin', 'Mason', 'Mccracken',
    'Mccreary', 'Mclean', 'Meade', 'Menifee', 'Mercer', 'Metcalfe', 'Monroe',
    'Montgomery', 'Morgan', 'Muhlenberg', 'Nelson', 'Nicholas', 'Ohio', 'Oldham',
    'Owen', 'Owsley', 'Pendleton', 'Perry', 'Pike', 'Powell', 'Pulaski',
    'Robertson', 'Rockcastle', 'Rowan', 'Russell', 'Scott', 'Shelby', 'Simpson',
    'Spencer', 'Taylor', 'Todd', 'Trigg', 'Trimble', 'Union', 'Warren',
    'Washington', 'Wayne', 'Webster', 'Whitley', 'Wolfe', 'Woodford'
]

unique_counties = df['county'].unique()
extra_counties = [c for c in unique_counties if c not in ky_counties]

print(f"Found {len(extra_counties)} non-standard county entries:")
for county in sorted(extra_counties):
    count = (df['county'] == county).sum()
    print(f"  - {county:20} ({count:,} records)")

# Step 3: Handle duplicates (skip for now - just verify names changed)
print("\n" + "="*80)
print("STEP 3: CANDIDATE STANDARDIZATION COMPLETE")
print("="*80)

# Step 4: Save standardized data
print("="*80)
print("STEP 4: SAVE STANDARDIZED DATA")
print("="*80)

standardized_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_ELECTIONS_STANDARDIZED.csv")
df.to_csv(standardized_file, index=False)
print(f"\n✓ Saved: {standardized_file}")

# Step 5: Final summary
print("\n" + "="*80)
print("FINAL DATA SUMMARY")
print("="*80)

print(f"\nClean rows: {len(df):,}")
print(f"Kentucky counties: {len(ky_counties)}")
print(f"Found counties: {len([c for c in unique_counties if c in ky_counties])}")
print(f"Extra/unknown counties: {len(extra_counties)}")
print(f"Unique candidates: {df['candidate'].nunique():,}")
print(f"Total votes: {df['votes'].sum():,}")

print(f"\nTop 10 candidates (STANDARDIZED):")
top_10 = df.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
for idx, (name, votes) in enumerate(top_10.items(), 1):
    print(f"  {idx:2}. {name:40} {votes:>12,}")

print("\n✓ Standardization complete!")
print("\nNext: Manual review of county names and duplicate candidates")
