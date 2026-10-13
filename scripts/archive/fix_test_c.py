import pandas as pd
import numpy as np
import datetime
import os
import sys

sys.path.append(os.path.abspath('backend'))
from ml.forecasting.model import DemandForecaster

print("\n--- TEST C: Invalid Model Outputs (Fixed Density) ---")
forecaster = DemandForecaster(model_path="backend/models/forecasting/xgboost_steel_v1.joblib")

# Mock the model to return a negative prediction
class MockModel:
    def predict(self, X):
        return [-10.0]
        
forecaster.model = MockModel()

# Generate valid history (Dense)
now = datetime.datetime.now(datetime.timezone.utc)
data = []
for i in range(100):
    for r in range(10): # 10 readings per bin
        data.append({
            'timestamp': now - pd.Timedelta(minutes=15 * i) + pd.Timedelta(seconds=60*r), 
            'power_kw': 100.0
        })
df = pd.DataFrame(data).sort_values('timestamp')

try:
    forecaster.predict_15m_from_history(df)
    print("Failure: Model allowed negative output.")
except Exception as e:
    if "negative power" in str(e):
        print("Success: Model strictly rejected negative power.")
    else:
        print(f"Failure: Expected negative power exception, got: {e}")
