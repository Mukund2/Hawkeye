import pandas as pd

# Read the CSV
df = pd.read_csv('aircraft_data.csv')

# Show basic info
print(f"Total records: {len(df)}")
print(f"Unique aircraft: {df['icao24'].nunique()}")
print(f"\nFirst 10 records:")
print(df.head(10))

# Show some interesting stats
print(f"\nTop 5 countries:")
print(df['origin_country'].value_counts().head())