"""
Download official OpenElections Kentucky data (clean, verified county results)
https://github.com/openelections/openelections-data-ky
"""

import pandas as pd
import urllib.request
from pathlib import Path

data_dir = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/openelections")
data_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DOWNLOADING OFFICIAL OPENELECTIONS KENTUCKY DATA")
print("=" * 80)

# OpenElections repo structure: /2024/2024-general-counties.csv
base_url = "https://raw.githubusercontent.com/openelections/openelections-data-ky/master"

files_to_download = [
    ("2024/2024-general-counties.csv", "2024_general"),
    ("2020/2020-general-counties.csv", "2020_general"),
    ("2016/2016-general-counties.csv", "2016_general"),
    ("2015/2015-general-counties.csv", "2015_general"),
    ("2014/2014-general-counties.csv", "2014_general"),
    ("2012/2012-general-counties.csv", "2012_general"),
    ("2011/2011-general-counties.csv", "2011_general"),
    ("2010/2010-general-counties.csv", "2010_general"),
]

print(f"\nAttempting to download {len(files_to_download)} files:\n")

downloaded = []

for remote_path, local_name in files_to_download:
    url = f"{base_url}/{remote_path}"
    output_file = data_dir / f"{local_name}.csv"
    
    try:
        print(f"Downloading: {remote_path}...", end=" ")
        urllib.request.urlretrieve(url, output_file)
        
        # Verify it's valid
        df = pd.read_csv(output_file, nrows=5)
        print(f"✓ ({len(df)} rows)")
        downloaded.append(output_file)
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:50]}")

print(f"\n✓ Downloaded {len(downloaded)} files to {data_dir}")

# Now load and combine them
print(f"\n" + "=" * 80)
print(f"COMBINING OFFICIAL DATA")
print(f"=" * 80)

all_data = []

for csv_file in sorted(downloaded):
    df = pd.read_csv(csv_file)
    
    # Standardize columns
    df.columns = [col.lower().strip() for col in df.columns]
    
    print(f"\n{csv_file.name}:")
    print(f"  Records: {len(df):,}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Votes total: {df['votes'].sum():,.0f}" if 'votes' in df.columns else "  (no votes column)")
    
    all_data.append(df)

# Combine
df_final = pd.concat(all_data, ignore_index=True)

print(f"\n" + "=" * 80)
print(f"COMBINED OFFICIAL DATA")
print(f"=" * 80)
print(f"\nTotal records: {len(df_final):,}")
print(f"Total votes: {df_final['votes'].sum():,.0f}" if 'votes' in df_final.columns else "")
print(f"Columns: {list(df_final.columns)}")

# Top candidates
if 'candidate' in df_final.columns and 'votes' in df_final.columns:
    print(f"\nTop 10 candidates:")
    top10 = df_final.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
    for idx, (name, votes) in enumerate(top10.items(), 1):
        print(f"{idx:2}. {name:35} {votes:>12,.0f}")

# Save combined
output_file = Path("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/KY_OPENELECTIONS_OFFICIAL.csv")
df_final.to_csv(output_file, index=False)
print(f"\n✓ Saved: KY_OPENELECTIONS_OFFICIAL.csv")
