import pandas as pd

# Check what's in each file
df1 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241105__ky__general__county.csv")
df2 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241106__ky__general__county.csv")

print("FILE: 20241105__ky__general__county.csv")
print(f"  Records: {len(df1)}")
print(f"  Offices: {df1['office'].nunique()}")
print(f"  Officer samples: {df1['office'].unique()[:5]}")
print(f"  Trump 2024 Presidential votes: {df1[(df1['candidate']=='Donald J Trump') & (df1['office']=='President')]['votes'].sum():,}")

print("\nFILE: 20241106__ky__general__county.csv")
print(f"  Records: {len(df2)}")
print(f"  Offices: {df2['office'].nunique()}")
print(f"  Officer samples: {df2['office'].unique()[:5]}")
print(f"  Trump Presidential votes: {df2[(df2['candidate']=='Donald J Trump') & (df2['office']=='President')]['votes'].sum():,}")

print("\n20241105 - Trump for ANY office:")
trump_df1 = df1[df1['candidate'] == 'Donald J Trump']
print(trump_df1.groupby('office')['votes'].sum().to_string())

print("\n20241106 - Trump for ANY office:")
trump_df2 = df2[df2['candidate'] == 'Donald J Trump']
print(trump_df2.groupby('office')['votes'].sum().to_string())
