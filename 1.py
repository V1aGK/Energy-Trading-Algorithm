import requests
import pandas as pd

url = "https://api.energidataservice.dk/dataset/Elspotprices"

params = {
    "start": "2018-01-01T00:00",
    "end": "2025-10-01T00:00",
    "columns": "HourUTC,HourDK,PriceArea,SpotPriceDKK,SpotPriceEUR",
    "filter": '{"PriceArea":["DK1"]}',
    "limit": 100000,
    "sort": "HourUTC asc",
}

response = requests.get(url, params=params)
response.raise_for_status()  # raises if 4xx/5xx

data = response.json()
df_prices = pd.DataFrame(data["records"])

print(df_prices.shape)
print(df_prices.head())

df_prices["HourUTC"] = pd.to_datetime(df_prices["HourUTC"])
df_prices = df_prices.sort_values("HourUTC").reset_index(drop=True)

# Check for gaps
expected_hours = pd.date_range(
    start=df_prices["HourUTC"].min(),
    end=df_prices["HourUTC"].max(),
    freq="h"
)
missing = expected_hours.difference(df_prices["HourUTC"])
print(f"Rows: {len(df_prices)}")
print(f"Missing hours: {len(missing)}")
print(f"Negative prices: {(df_prices['SpotPriceEUR'] < 0).sum()}")

# Save
df_prices.to_parquet("/Users/evank/Desktop/Trading Algorithm/data/raw/prices.parquet", index=False)

print(f"From: {df_prices['HourUTC'].min()}")
print(f"To:   {df_prices['HourUTC'].max()}")