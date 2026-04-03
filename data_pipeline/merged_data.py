import pandas as pd
import os

#Read the data from all parquets we have created so far
df_calendar = pd.read_parquet("data/raw/calendar_features.parquet")
df_prices = pd.read_parquet("data/raw/prices.parquet")
df_loadst=pd.read_parquet("data/raw/loadst.parquet")
df_temperature = pd.read_parquet("data/raw/temperature.parquet")
df_wind_offshore = pd.read_parquet("data/raw/wind_offshore.parquet")
df_wind_onshore = pd.read_parquet("data/raw/wind_onshore.parquet")

df_prices = df_prices.set_index("HourUTC")

df_prices.index = df_prices.index.tz_localize("UTC")
df_calendar.index = df_calendar.index.tz_localize("UTC")
# Ensure all dataframes have their timestamp index in UTC timezone
df_loadst= df_loadst.tz_convert("UTC")
df_wind_offshore = df_wind_offshore.tz_convert("UTC")
df_wind_onshore = df_wind_onshore.tz_convert("UTC")

df_loadst=df_loadst.interpolate(method="linear").ffill().bfill()
df_temperature=df_temperature.interpolate(method="linear").ffill().bfill()
# Merge all dataframes on the UTC timestamp index
df_merged = df_prices.join(df_calendar, how="left").join(df_loadst, how="left").join(df_temperature, how="left").join(df_wind_offshore, how="left").join(df_wind_onshore, how="left")
df_merged = df_merged.drop(columns=["HourDK", "PriceArea", "SpotPriceDKK"])
df_merged = df_merged.ffill().bfill()
#Save the merged dataframe to a new parquet file
os.makedirs("data/processed", exist_ok=True)
df_merged.to_parquet("data/processed/merged_data.parquet")

