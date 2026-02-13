import pandas as pd

df1 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241105__ky__general__county.csv")
df2 = pd.read_csv("c:/Users/Shama/OneDrive/Documents/Course_Materials/CPT-236/Side_Projects/KYRealignments/data/20241106__ky__general__county.csv")

print("20241105 size:", len(df1))
print("20241106 size:", len(df2))
print("Same data?", df1.equals(df2))
print()
print("20241105 columns:", list(df1.columns))
print("20241105 votes sum:", df1['votes'].sum() if 'votes' in df1.columns else 'N/A')
print()
print("20241106 columns:", list(df2.columns))
print("20241106 votes sum:", df2['votes'].sum() if 'votes' in df2.columns else 'N/A')
print()
print("Difference in votes:", df1['votes'].sum() - df2['votes'].sum() if 'votes' in df1.columns and 'votes' in df2.columns else 'N/A')
