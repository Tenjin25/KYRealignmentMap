import pandas as pd

# Raw 20241105 file
df_raw = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241105__ky__general__county.csv")

print("20241105 raw analysis:")
print(f"Total records: {len(df_raw)}")
print(f"Total votes: {df_raw['votes'].sum():,}")
print(f"Unique candidates: {df_raw['candidate'].nunique()}")
print(f"Unique counties: {df_raw['county'].nunique()}")

print("\nCandidate vote totals (top 10):")
top_10 = df_raw.groupby('candidate')['votes'].sum().sort_values(ascending=False).head(10)
for name, votes in top_10.items():
    print(f"  {name:30} {votes:>12,}")

print("\nCheck for duplicates in raw 20241105:")
dups = df_raw[df_raw.duplicated(subset=['county', 'candidate'], keep=False)]
print(f"  Duplicate county/candidate: {len(dups)}")

if len(dups) > 0:
    print("\nSample duplicates:")
    print(dups[['county', 'candidate', 'votes']].sort_values(['candidate', 'county']).head(20).to_string())

# Now check precinct file
print("\n" + "="*80)
print("PRECINCT FILE check:")
precinct_file = "c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241105__ky__general__precinct.csv"
df_precinct = pd.read_csv(precinct_file, nrows=5)
print(f"Precinct file shape (first 5): {df_precinct.shape}")
print(f"Precinct columns: {list(df_precinct.columns)}")
