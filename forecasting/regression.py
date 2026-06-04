from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import os 

df_merged = pd.read_parquet("data/processed/merged_data.parquet")
df_linear = df_merged[["wind_onshore_mw", "wind_offshore_mw", "temperature_2m", "load_forecast_mw", "SpotPriceEUR", "Hour", "DayOfWeek", "Month", "is_holiday"]]
# Create lag features for the target variable
df_linear["SpotPriceEUR_lag_24h"] = df_linear["SpotPriceEUR"].shift(24)
df_linear["SpotPriceEUR_lag_168h"] = df_linear["SpotPriceEUR"].shift(168)
# Drop rows with NaN values resulting from the lag features
df_linear = df_linear.dropna()

# Split the data into training and testing sets based on a cutoff date
df_linear_train = df_linear[df_linear.index < "2023-01-01"]
df_linear_test = df_linear[df_linear.index >= "2023-01-01"]

# Define the features and target variable for training
features = ["wind_onshore_mw", "wind_offshore_mw", "temperature_2m", "load_forecast_mw", "Hour", "DayOfWeek", "Month", "is_holiday", "SpotPriceEUR_lag_24h", "SpotPriceEUR_lag_168h"]
target = "SpotPriceEUR"
X_train = df_linear_train[features]
y_train = df_linear_train[target]
X_test = df_linear_test[features]
y_test = df_linear_test[target]
# Train a linear regression model
model = LinearRegression()
model.fit(X_train, y_train)
# Make predictions on the test set
y_pred = model.predict(X_test)
# Calculate error metrics for the linear regression model
mean_absolute_error_linear = mean_absolute_error(y_test, y_pred)
mean_squared_error_linear = root_mean_squared_error(y_test, y_pred)
actual_direction = y_test.diff() > 0
forecast_direction_linear = pd.Series(y_pred).diff() > 0
direction_accuracy_linear = np.mean(actual_direction.values == forecast_direction_linear.values)
print(f"Linear Regression - MAE: {mean_absolute_error_linear:.2f}, RMSE: {mean_squared_error_linear:.2f}")
print(f"Linear Regression - Direction Accuracy: {direction_accuracy_linear:.2%}")

results = {
    "Linear_Regression": {
        "MAE": mean_absolute_error_linear,
        "RMSE": mean_squared_error_linear,
        "Direction_Accuracy": direction_accuracy_linear
    }
}   
os.makedirs("results", exist_ok=True)
results_df = pd.DataFrame(results).T
results_df.to_csv("results/linear_regression_results.csv")

feature_names = X_train.columns
coefficients = pd.Series(model.coef_, index=feature_names)
print(coefficients.sort_values())

coefficients.to_csv("results/linear_regression_coefficients.csv", header=["coefficient"])
