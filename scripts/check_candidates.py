import pandas as pd

df1 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241105__ky__general__county.csv")
df2 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects\KYRealignments/data/20241106__ky__general__county.csv")

print("20241105 - All candidates (first 20):")
print(df1['candidate'].unique()[:20])

print("\n20241105 - Candidates that might be Trump:")
for cand in df1['candidate'].unique():
    if 'trump' in str(cand).lower() or 'donald' in str(cand).lower():
        votes = df1[df1['candidate'] == cand]['votes'].sum()
        print(f"  {cand}: {votes:,}")

print("\n\n20241106 - Candidates that might be Trump:")
for cand in df2['candidate'].unique():
    if 'trump' in str(cand).lower() or 'donald' in str(cand).lower():
        votes = df2[df2['candidate'] == cand]['votes'].sum()
        print(f"  {cand}: {votes:,}")

# Check if these files even have President info
print("\n\n20241105 Offices:", df1['office'].unique() if 'office' in df1.columns else "NO OFFICE COLUMN")
print("\n20241106 President candidates:")
if 'office' in df2.columns:
    pres_df = df2[df2['office'] == 'President and Vice President of the United States']
    if len(pres_df) > 0:
        print(pres_df['candidate'].unique()[:10])
        print(f"Total records for President: {len(pres_df)}")
    else:
        print("No President records")
