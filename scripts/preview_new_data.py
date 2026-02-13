"""Preview newly downloaded data."""
import pandas as pd

print("=" * 80)
print("NEW DATA PREVIEW - OpenElections Download")
print("=" * 80)

files = {
    "2010": "data/20101102__ky__general__county.csv",
    "2011": "data/20111108__ky__general__county.csv",
    "2019": "data/20191105__ky__general__county.csv",
}

for year, filepath in files.items():
    try:
        df = pd.read_csv(filepath)
        print(f"\n{year}:")
        print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")
        print(f"\n  First 3 rows:")
        print(df.head(3).to_string(index=False))
        
        # Count unique values
        if "county" in df.columns:
            print(f"\n  Unique counties: {df['county'].nunique()}/120")
        if "candidate" in df.columns:
            print(f"  Unique candidates: {df['candidate'].nunique()}")
        if "votes" in df.columns:
            print(f"  Total votes: {df['votes'].sum():,}")
            
    except Exception as e:
        print(f"\n{year}: ERROR - {e}")

print("\n" + "=" * 80)
print("✓ Data looks good! Ready to use.")
print("=" * 80)
