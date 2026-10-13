import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import json
import os
import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.google_sheets import gsheets_db

# Connect to Google Sheets to retrieve the dataset
gsheets_db.connect()
df = gsheets_db.get_historical_dataset()

if df.empty:
    print("WARNING: Google Sheets dataset is empty or offline. Falling back to local CSV for training.")
    df = pd.read_csv('data/industrial/uci_steel/raw_data.csv')


df['timestamp'] = pd.to_datetime(df['date'], format='%d/%m/%Y %H:%M')
df = df.sort_values('timestamp').reset_index(drop=True)
df['industrial_energy_consumption'] = df['Usage_kWh']

df['hour'] = df['timestamp'].dt.hour
df['minute'] = df['timestamp'].dt.minute
df['day_of_week'] = df['timestamp'].dt.dayofweek
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

df['lag_1h'] = df['industrial_energy_consumption'].shift(4)
df['lag_24h'] = df['industrial_energy_consumption'].shift(96)
df['rolling_mean_4h'] = df['industrial_energy_consumption'].shift(1).rolling(16).mean()

df = df.dropna().reset_index(drop=True)

features = [
    'hour', 'minute', 'day_of_week', 'is_weekend', 'NSM',
    'lag_1h', 'lag_24h', 'rolling_mean_4h'
]
target = 'industrial_energy_consumption'

n = len(df)
train_idx = int(n * 0.7)
val_idx = int(n * 0.85)

train_df = df.iloc[:train_idx]
val_df = df.iloc[train_idx:val_idx]
test_df = df.iloc[val_idx:]

X_train, y_train = train_df[features], train_df[target]
X_val, y_val = val_df[features], val_df[target]
X_test, y_test = test_df[features], test_df[target]

print("Training XGBoost...")
model = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

naive_pred = test_df['lag_24h']
naive_mae = mean_absolute_error(y_test, naive_pred)

print(f"XGBoost MAE: {mae:.2f}")
print(f"Naive Baseline MAE: {naive_mae:.2f}")

os.makedirs('models/forecasting', exist_ok=True)
model_path = 'models/forecasting/xgboost_steel_v1.joblib'
joblib.dump(model, model_path)

importance = dict(zip(features, [float(x) for x in model.feature_importances_]))
importance = dict(sorted(importance.items(), key=lambda item: item[1], reverse=True))

registry_path = 'models/forecasting/registry.json'
registry = {}
if os.path.exists(registry_path):
    with open(registry_path, 'r') as f:
        registry = json.load(f)

model_id = "FORECAST-XGB-STEEL-V1"
registry[model_id] = {
    "model_id": model_id,
    "version": "1.0",
    "model_type": "XGBRegressor",
    "dataset": "UCI Steel Industry Dataset",
    "dataset_version": "1.0",
    "training_period": f"{train_df['timestamp'].min().isoformat()} to {train_df['timestamp'].max().isoformat()}",
    "validation_period": f"{val_df['timestamp'].min().isoformat()} to {val_df['timestamp'].max().isoformat()}",
    "test_period": f"{test_df['timestamp'].min().isoformat()} to {test_df['timestamp'].max().isoformat()}",
    "features": features,
    "metrics": {
        "xgboost_mae": round(mae, 4),
        "xgboost_rmse": round(rmse, 4),
        "naive_mae": round(naive_mae, 4)
    },
    "feature_importance": importance,
    "artifact_path": model_path,
    "created_at": datetime.datetime.now().isoformat(),
    "status": "VALIDATED"
}

with open(registry_path, 'w') as f:
    json.dump(registry, f, indent=4)

print("Saved model and updated registry.")
