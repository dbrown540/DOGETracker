import pandas as pd

df = pd.read_csv("data/doge_raw_api_data.csv")

print(df.head())

# I want to see all the different agency values

unique_agency_values = df["agency"].unique()
print(unique_agency_values)