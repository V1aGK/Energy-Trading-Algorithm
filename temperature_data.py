import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 56.1629,
    "longitude": 10.2039,
    "start_date": "2018-01-01",
    "end_date": "2025-10-01",
    "hourly": "temperature_2m"
}

response = openmeteo.weather_api(url, params=params)

# Take the first (and only) location from the response
response_data = response[0]

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response_data.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

#Convert the raw data from API to a pandas DataFrame
hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
#Add the temperature data to the hourly data dictionary and convert it to a DataFrame
hourly_data["temperature_2m"] = hourly_temperature_2m
#Convert the hourly data dictionary to a DataFrame for easier analysis and manipulation
hourly_dataframe = pd.DataFrame(data=hourly_data)
hourly_dataframe.set_index("date", inplace=True)

#Save temperature data
hourly_dataframe.to_parquet("data/raw/temperature.parquet")
print("Data saved to data/raw/temperature.parquet")
print(hourly_dataframe.shape)
print(hourly_dataframe.head())