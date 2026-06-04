from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
from xgboost import XGBRegressor
import pandas as pd
import numpy as np
import os 

param_grid = {
    "n_estimators": [300, 500, 700, 1000],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 5, 7],
    "subsample": [0.7, 0.8, 0.9],
    "colsample_bytree": [0.7, 0.8, 0.9],
}

tscv = TimeSeriesSplit(n_splits=5)

search = RandomizedSearchCV(
    estimator=XGBRegressor(objective="reg:squarederror", random_state=42),
    param_distributions=param_grid,
    n_iter=20,
    scoring="neg_mean_absolute_error",
    cv=tscv,
    random_state=42,
    n_jobs=-1,
    verbose=1,
)

param_grid = {
    "n_estimators": [300, 500, 700, 1000],
    "learning_rate": [0.01, 0.05, 0.1],
    "max_depth": [3, 5, 7],
    "subsample": [0.7, 0.8, 0.9],
    "colsample_bytree": [0.7, 0.8, 0.9],
}

tscv = TimeSeriesSplit(n_splits=5)

search = RandomizedSearchCV(
    estimator=XGBRegressor(objective="reg:squarederror", random_state=42),
    param_distributions=param_grid,
    n_iter=20,
    scoring="neg_mean_absolute_error",
    cv=tscv,
    random_state=42,
    n_jobs=-1,
    verbose=1,
)

df_merged = pd.read_parquet("data/processed/merged_data.parquet")
df_xgboost = df_merged[["wind_onshore_mw", "wind_offshore_mw", "temperature_2m", "load_forecast_mw", "SpotPriceEUR", "Hour", "DayOfWeek", "Month", "is_holiday"]]
df_xgboost["wind_penetration"] = (df_xgboost["wind_onshore_mw"] + df_xgboost["wind_offshore_mw"]) / df_xgboost["load_forecast_mw"]
# Create lag features for the target variable
df_xgboost["SpotPriceEUR_lag_24h"] = df_xgboost["SpotPriceEUR"].shift(24)
df_xgboost["SpotPriceEUR_lag_48h"] = df_xgboost["SpotPriceEUR"].shift(48)
df_xgboost["SpotPriceEUR_lag_72h"] = df_xgboost["SpotPriceEUR"].shift(72)
df_xgboost["SpotPriceEUR_lag_96h"] = df_xgboost["SpotPriceEUR"].shift(96)
df_xgboost["SpotPriceEUR_lag_120h"] = df_xgboost["SpotPriceEUR"].shift(120)
df_xgboost["SpotPriceEUR_lag_168h"] = df_xgboost["SpotPriceEUR"].shift(168)

# Create a rolling mean features
df_xgboost["Rolling_Mean_7d"] = df_xgboost["SpotPriceEUR"].shift(24).rolling(window=168).mean()
df_xgboost["Rolling_Mean_30d"] = df_xgboost["SpotPriceEUR"].shift(24).rolling(window=720).mean()
df_xgboost["Rolling_std_7d"] = df_xgboost["SpotPriceEUR"].shift(24).rolling(window=168).std()

# Convert the 'is_holiday' column to integer type
df_xgboost["is_holiday"] = df_xgboost["is_holiday"].astype(int)
# Drop rows with NaN values resulting from the lag features
df_xgboost = df_xgboost.dropna()

# Define the features and target variable for training
features = ["wind_onshore_mw", "wind_offshore_mw", "temperature_2m", "load_forecast_mw", "wind_penetration", "Hour", "DayOfWeek", "Month", "is_holiday", "SpotPriceEUR_lag_24h", 
            "SpotPriceEUR_lag_168h", "SpotPriceEUR_lag_48h", "SpotPriceEUR_lag_72h", "SpotPriceEUR_lag_96h", "SpotPriceEUR_lag_120h", "Rolling_Mean_7d", "Rolling_Mean_30d", "Rolling_std_7d"]
target = "SpotPriceEUR"

folds = [{"train_start": "2018-01-01", "train_end": "2020-12-31", "test_start": "2021-01-01", "test_end": "2021-12-31"},
         {"train_start": "2018-01-01", "train_end": "2021-12-31", "test_start": "2022-01-01", "test_end": "2022-12-31"},
         {"train_start": "2018-01-01", "train_end": "2022-12-31", "test_start": "2023-01-01", "test_end": "2023-12-31"},
         {"train_start": "2018-01-01", "train_end": "2023-12-31", "test_start": "2024-01-01", "test_end": "2024-12-31"},]

results = {}
for fold in folds:
    df_xgboost_train = df_xgboost[(df_xgboost.index >= fold["train_start"]) & (df_xgboost.index <= fold["train_end"])]
    df_xgboost_test = df_xgboost[(df_xgboost.index >= fold["test_start"]) & (df_xgboost.index <= fold["test_end"])]
    df_tune = df_xgboost[df_xgboost.index < "2025-01-01"]
    X_tune = df_tune[features]
    y_tune = df_tune[target]
    X_train = df_xgboost_train[features]
    Y_train = df_xgboost_train[target]
    X_test = df_xgboost_test[features]
    Y_test = df_xgboost_test[target]
    model = XGBRegressor(objective="reg:squarederror", n_estimators=1000, learning_rate=0.01, max_depth=5, random_state=42)
    model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)
    mean_absolute_error_xgboost = mean_absolute_error(Y_test, Y_pred)
    mean_squared_error_xgboost = root_mean_squared_error(Y_test, Y_pred)
    actual_direction = Y_test.diff() > 0
    forecast_direction_xgboost = pd.Series(Y_pred, index=Y_test.index).diff() > 0
    direction_accuracy_xgboost = np.mean(actual_direction.values == forecast_direction_xgboost.values)
    print(f"XGBoost Regression Fold {fold['test_start']} - {fold['test_end']} - MAE: {mean_absolute_error_xgboost:.2f}, RMSE: {mean_squared_error_xgboost:.2f}")
    print(f"XGBoost Regression Fold {fold['test_start']} - {fold['test_end']} - Direction Accuracy: {direction_accuracy_xgboost:.2%}")
    results[f"XGBoost_Regression_{fold['test_start']}_{fold['test_end']}"] = {
        "MAE": mean_absolute_error_xgboost,
        "RMSE": mean_squared_error_xgboost,
        "Direction_Accuracy": direction_accuracy_xgboost
    }

search.fit(X_tune, y_tune)
print("Best parameters:", search.best_params_)
print("Best MAE:", -search.best_score_)