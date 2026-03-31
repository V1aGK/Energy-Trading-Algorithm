import pandas as pd
import os
import holidays

df = pd.read_parquet("data/raw/prices.parquet")

df["HourDK"] = pd.to_datetime(df["HourDK"])
#New dataframe with UTC index
df_calendar = pd.DataFrame(index=df["HourUTC"])

#Extract calendar features using Denmark Time
df_calendar["Hour"] = df["HourDK"].dt.hour.values
df_calendar["DayOfWeek"] = df["HourDK"].dt.dayofweek.values
df_calendar["Month"] = df["HourDK"].dt.month.values
df_calendar["is_weekend"] = (df["HourDK"].dt.dayofweek >= 5).values
df_calendar["is_peak"] = df["HourDK"].dt.hour.between(8,19).values
df_calendar["Season"]= df["HourDK"].dt.month.map({12: "Winter", 1: "Winter", 2: "Winter",
                                                  3: "Spring", 4: "Spring", 5: "Spring",
                                                  6: "Summer", 7: "Summer", 8: "Summer",
                                                  9: "Fall", 10: "Fall", 11: "Fall"}).values

#Add holiday feature
# Holidays - check against Copenhagen date, not UTC
dk_holidays = holidays.Denmark(years=range(2018, 2026))
df_calendar["is_holiday"] = df["HourDK"].dt.normalize().dt.tz_localize(None).isin(dk_holidays).values

#Save the calendar features to a new parquet file
os.makedirs("data/raw", exist_ok=True)
df_calendar.to_parquet("data/raw/calendar_features.parquet")
print(df_calendar.head())
print(df_calendar.shape)