import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, root_mean_squared_error
import os

from simulator.factory import history_db

class DemandForecaster:
    def __init__(self, model_path: str = "demand_model.xgb"):
        self.model_path = model_path
        self.model_15m = None
        
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Features: lags (15m, 30m, 1h, 2h)
        df['lag_1'] = df['total_demand_kw'].shift(1)
        df['lag_2'] = df['total_demand_kw'].shift(2)
        df['lag_4'] = df['total_demand_kw'].shift(4)
        df['lag_8'] = df['total_demand_kw'].shift(8)
        
        # Rolling means
        df['rolling_mean_1h'] = df['total_demand_kw'].shift(1).rolling(4).mean()
        df['rolling_max_1h'] = df['total_demand_kw'].shift(1).rolling(4).max()
        
        # Time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # We want to predict target_15m (the value AT this row) using ONLY shifted past data and current knowns (production_target)
        # Wait, the target is the current row's 'total_demand_kw'. Features are lags.
        df['target'] = df['total_demand_kw']
        
        df.dropna(inplace=True)
        return df
        
    def train(self):
        print("Training Forecaster on historical simulation data...")
        df_raw = history_db.get_history()
        df = self.generate_features(df_raw)
        
        feature_cols = ['lag_1', 'lag_2', 'lag_4', 'lag_8', 'rolling_mean_1h', 'rolling_max_1h', 
                        'hour', 'day_of_week', 'production_rate', 'temperature_c']
                        
        X = df[feature_cols]
        y = df['target']
        
        # Time-aware Train-test split (80/20)
        split = int(len(df) * 0.8)
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]
        
        # XGBoost Model
        self.model_15m = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.05, random_state=42)
        self.model_15m.fit(X_train, y_train)
        
        # Evaluation
        preds = self.model_15m.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = root_mean_squared_error(y_test, preds)
        
        # Baseline model (persistence - just using lag_1 as prediction)
        baseline_preds = X_test['lag_1']
        baseline_mae = mean_absolute_error(y_test, baseline_preds)
        
        improvement = ((baseline_mae - mae) / baseline_mae) * 100 if baseline_mae > 0 else 0
        
        self.model_15m.save_model(self.model_path)
        
        return {
            "model": "XGBoost",
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "baseline_mae": round(baseline_mae, 2),
            "improvement_percent": round(improvement, 1),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        }
        
    def load(self):
        if os.path.exists(self.model_path):
            self.model_15m = xgb.XGBRegressor()
            self.model_15m.load_model(self.model_path)
            return True
        return False
        
    def predict_15m(self, current_demand: float, lag_demand: float, production_rate: float, temp: float, 
                    lag_4: float = None, lag_8: float = None, rolling_mean: float = None, rolling_max: float = None, hour: int = 12, day_of_week: int = 1) -> float:
        if self.model_15m is None:
            if not self.load():
                self.train()
                
        # Fill missing with approximations for the live demo if not provided
        lag_4 = lag_4 or current_demand
        lag_8 = lag_8 or current_demand
        rolling_mean = rolling_mean or current_demand
        rolling_max = rolling_max or current_demand
                
        X = pd.DataFrame([{
            'lag_1': current_demand,
            'lag_2': lag_demand,
            'lag_4': lag_4,
            'lag_8': lag_8,
            'rolling_mean_1h': rolling_mean,
            'rolling_max_1h': rolling_max,
            'hour': hour,
            'day_of_week': day_of_week,
            'production_rate': production_rate,
            'temperature_c': temp
        }])
        
        pred = self.model_15m.predict(X)[0]
        return float(pred)

# Global instance
forecaster = DemandForecaster()
