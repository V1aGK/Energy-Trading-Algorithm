import pandas as pd
from entsoe import EntsoePandasClient
from dotenv import load_dotenv
import os

load_dotenv()
client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))

start = pd.Timestamp("2018-01-01", tz="Europe/Copenhagen")
end   = pd.Timestamp("2025-10-01", tz="Europe/Copenhagen")


# Load actual and forecast
load = client.query_load_and_forecast(
    "10YDK-1--------W",
    start=start,
    end=end
)
#Check for missing values
print(f"Missing values before interpolation: {load.isnull().sum().sum()}")

#Interpolate missing values
load=load.interpolate(method='linear')
print(f"Missing values after interpolation: {load.isnull().sum().sum()}")
#Change column names for better readability & understanding
load.columns = ['load_forecast_mw', 'load_actual_mw']

#Save data
os.makedirs("data/raw", exist_ok=True)
load.to_parquet("data/raw/load.parquet")
print("Data saved to data/raw/loadst.parquet")
print(load.shape)
print(load.head())
