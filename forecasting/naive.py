import pandas as pd
import os 
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import numpy as np


df_naive = pd.read_parquet("data/processed/merged_data.parquet")
# Create naive forecasts by shifting the actual spot price by 24 hours and 168 hours (1 week)
df_naive["Naive_Forecast_24h"] = df_naive["SpotPriceEUR"].shift(24)
df_naive["Naive_Forecast_168h"] = df_naive["SpotPriceEUR"].shift(168)

# Drop rows with NaN values resulting from the shifts
df_naive = df_naive.dropna()

# Split the data into training and testing sets based on a cutoff date
df_naive_train = df_naive[df_naive.index < "2023-01-01"]
df_naive_test = df_naive[df_naive.index >= "2023-01-01"]

# Calculate error metrics for the naive forecasts 
mean_absolute_error_24h = mean_absolute_error(df_naive_test["SpotPriceEUR"], df_naive_test["Naive_Forecast_24h"])
mean_squared_error_24h = root_mean_squared_error(df_naive_test["SpotPriceEUR"], df_naive_test["Naive_Forecast_24h"])
mean_absolute_error_168h = mean_absolute_error(df_naive_test["SpotPriceEUR"], df_naive_test["Naive_Forecast_168h"])
mean_squared_error_168h = root_mean_squared_error(df_naive_test["SpotPriceEUR"], df_naive_test["Naive_Forecast_168h"])
actual_direction = df_naive_test["SpotPriceEUR"].diff() > 0
forecast_direction_24h = df_naive_test["Naive_Forecast_24h"].diff() > 0
forecast_direction_168h = df_naive_test["Naive_Forecast_168h"].diff() > 0
direction_accuracy_24h = np.mean(actual_direction == forecast_direction_24h)
direction_accuracy_168h = np.mean(actual_direction == forecast_direction_168h)

print(f"Naive Forecast 24h - MAE: {mean_absolute_error_24h:.2f}, RMSE: {mean_squared_error_24h:.2f}")
print(f"Naive Forecast 168h - MAE: {mean_absolute_error_168h:.2f}, RMSE: {mean_squared_error_168h:.2f}")
print(f"Naive Forecast 24h - Direction Accuracy: {direction_accuracy_24h:.2%}")
print(f"Naive Forecast 168h - Direction Accuracy: {direction_accuracy_168h:.2%}")

results = {
    "Naive_Forecast_24h": {
        "MAE": mean_absolute_error_24h,
        "RMSE": mean_squared_error_24h,
        "Direction_Accuracy": direction_accuracy_24h
    },
    "Naive_Forecast_168h": {
        "MAE": mean_absolute_error_168h,
        "RMSE": mean_squared_error_168h,
        "Direction_Accuracy": direction_accuracy_168h
    }
}

os.makedirs("results", exist_ok=True)
results_df = pd.DataFrame(results).T
results_df.to_csv("results/naive_forecast_results.csv", index=True)