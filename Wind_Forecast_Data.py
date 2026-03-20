import pandas as pd
from entsoe import EntsoePandasClient
from dotenv import load_dotenv
import os

load_dotenv()
client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))

start = pd.Timestamp("2018-01-01", tz="Europe/Copenhagen")
end   = pd.Timestamp("2025-10-01", tz="Europe/Copenhagen")

#We will start by using only wind forecast as its production is both volatile and the biggest in Denmark's energy mix.
# Onshore wind forecast
wind_onshore = client.query_wind_and_solar_forecast(
    "10YDK-1--------W",
    start=start,
    end=end,
    psr_type="B18"
)

# Offshore wind forecast
wind_offshore = client.query_wind_and_solar_forecast(
    "10YDK-1--------W",
    start=start,
    end=end,
    psr_type="B19"
)


print("Onshore shape:", wind_onshore.shape)
print("Offshore shape:", wind_offshore.shape)
#The columns printed should be around 68000, in order to match the hours in this time period. These numbers printed mean that maybe there is something wrong with the intervals. This is what I am checking below.
print(wind_onshore.head(10))
print(wind_onshore.index.freq)

# Rename columns
wind_onshore.columns  = ["wind_onshore_mw"]
wind_offshore.columns = ["wind_offshore_mw"]

#Resample to hourly by taking the mean of each hour
wind_onshore_hourly  = wind_onshore.resample("h").mean()
wind_offshore_hourly = wind_offshore.resample("h").mean()

#Check now if we have any missing values
print(f"Onshore missing values: {wind_onshore_hourly.isnull().sum().sum()}")
print(f"Offshore missing values: {wind_offshore_hourly.isnull().sum().sum()}")
print(f"Onshore negative values: {(wind_onshore_hourly < 0).sum().sum()}")
print(f"Offshore negative values: {(wind_offshore_hourly < 0).sum().sum()}")

#We have missing values, so we interpolate.

wind_onshore_hourly = wind_onshore_hourly.interpolate(method='linear')
wind_offshore_hourly= wind_offshore_hourly.interpolate(method='linear')

#No missing values.
#Save our data

wind_onshore_hourly.to_parquet("/Users/evank/Desktop/Trading Algorithm/data/raw/wind_onshore.parquet")

wind_offshore_hourly.to_parquet("/Users/evank/Desktop/Trading Algorithm/data/raw/wind_offshore.parquet")




