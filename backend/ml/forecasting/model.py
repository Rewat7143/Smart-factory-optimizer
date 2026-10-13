import numpy as np
import pandas as pd
import xgboost as xgb
import joblib
import os
import datetime

DEFAULT_MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "models", "forecasting", "xgboost_steel_v1.joblib")
)

class DemandForecaster:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model = None
        
    def load(self):
        if self.model is not None:
            return True
        candidates = [self.model_path, DEFAULT_MODEL_PATH, "models/forecasting/xgboost_steel_v1.joblib"]
        for p in candidates:
            if p and os.path.exists(p):
                try:
                    self.model = joblib.load(p)
                    self.model_path = p
                    return True
                except Exception:
                    pass
        return False
        
    def predict_15m(self, current_demand: float, lag_demand: float, production_rate: float, temp: float, 
                    lag_4: float = None, lag_8: float = None, rolling_mean: float = None, rolling_max: float = None, hour: int = None, day_of_week: int = None) -> float:
        if not self.load():
            return current_demand * 1.02 # Safe physical fallback
            
        now = datetime.datetime.now(datetime.timezone.utc)
        h = hour if hour is not None else now.hour
        m = now.minute
        dow = day_of_week if day_of_week is not None else now.weekday()
        is_weekend = 1 if dow >= 5 else 0
        nsm = h * 3600 + m * 60
        
        # In XGBoost steel model: input lags are energy (kWh per 15 min = power_kw / 4)
        c_kwh = current_demand / 4.0
        lag_1h_kwh = (lag_4 / 4.0) if lag_4 is not None else c_kwh
        roll_kwh = (rolling_mean / 4.0) if rolling_mean is not None else c_kwh
        
        X = pd.DataFrame([{
            'hour': h,
            'minute': m,
            'day_of_week': dow,
            'is_weekend': is_weekend,
            'NSM': nsm,
            'lag_1h': lag_1h_kwh,
            'lag_24h': c_kwh,
            'rolling_mean_4h': roll_kwh
        }])
        
        try:
            pred_kwh = float(self.model.predict(X)[0])
            raw_kw = pred_kwh * 4.0
            # Blend autoregressive response with current operating setpoint
            pred_kw = round(current_demand * 0.65 + raw_kw * 0.35, 1)
            return max(40.0, min(120.0, pred_kw))
        except Exception:
            return round(current_demand * 1.02, 1)

    def predict_15m_from_history(self, history_df: pd.DataFrame) -> dict:
        """
        Infers next 15-minute load from history dataframe using XGBoost.
        Gracefully handles streaming telemetry buffers via adaptive rolling lag extraction.
        """
        if not self.load():
            if len(history_df) > 0 and 'power_kw' in history_df:
                cur = float(history_df['power_kw'].iloc[-1])
            else:
                cur = 90.8
            t_next = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)).isoformat()
            return {'timestamp': t_next, 'predicted_kw': round(cur * 1.02, 1)}

        if len(history_df) == 0:
            now = datetime.datetime.now(datetime.timezone.utc)
            t_pred = now + datetime.timedelta(minutes=15)
            return {'timestamp': t_pred.isoformat(), 'predicted_kw': 91.5}

        # Clean dataframe
        df = history_df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        df = df.dropna(subset=['power_kw'])
        df = df.sort_values('timestamp')

        now = df['timestamp'].iloc[-1]
        current_kw = float(df['power_kw'].iloc[-1])
        t_pred = now + pd.Timedelta(minutes=15)

        # Extract available lags
        rolling_mean_kw = float(df['power_kw'].tail(16).mean()) if len(df) >= 2 else current_kw
        lag_1h_kw = float(df['power_kw'].iloc[-4]) if len(df) >= 4 else current_kw

        h = t_pred.hour
        m = t_pred.minute
        dow = t_pred.weekday()
        is_weekend = 1 if dow >= 5 else 0
        nsm = h * 3600 + m * 60

        X = pd.DataFrame([{
            'hour': h,
            'minute': m,
            'day_of_week': dow,
            'is_weekend': is_weekend,
            'NSM': nsm,
            'lag_1h': lag_1h_kw / 4.0,
            'lag_24h': current_kw / 4.0,
            'rolling_mean_4h': rolling_mean_kw / 4.0
        }])

        try:
            pred_kwh = float(self.model.predict(X)[0])
            raw_kw = pred_kwh * 4.0
            # Blend autoregressive model response with current operating baseline
            pred_kw = round(current_kw * 0.65 + raw_kw * 0.35, 1)
            pred_kw = max(45.0, min(120.0, pred_kw))
        except Exception:
            pred_kw = round(current_kw * 1.02, 1)

        return {
            'timestamp': t_pred.isoformat(),
            'predicted_kw': pred_kw
        }

    def predict_trajectory(self, history_df: pd.DataFrame, steps: int = 8) -> list:
        """
        Generates contiguous multi-step predicted load trajectory (e.g. +15m, +30m, +45m, +1h... up to 4h)
        for real-time dashboard plotting and horizon analysis.
        """
        if not self.load():
            now = datetime.datetime.now(datetime.timezone.utc)
            base_kw = 90.8
            if len(history_df) > 0 and 'power_kw' in history_df:
                base_kw = float(history_df['power_kw'].iloc[-1])
            return [
                {
                    'timestamp': (now + datetime.timedelta(minutes=15 * s)).isoformat(),
                    'predicted_kw': round(base_kw + (s * 0.4), 1),
                    'horizon_min': 15 * s
                }
                for s in range(1, steps + 1)
            ]

        if len(history_df) == 0:
            now = datetime.datetime.now(datetime.timezone.utc)
            current_kw = 90.8
            rolling_kw = 90.8
        else:
            df = history_df.copy()
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
            df = df.dropna(subset=['power_kw']).sort_values('timestamp')
            now = df['timestamp'].iloc[-1]
            current_kw = float(df['power_kw'].iloc[-1])
            rolling_kw = float(df['power_kw'].tail(16).mean()) if len(df) >= 2 else current_kw

        forecast_points = []
        cur_step_kw = current_kw

        for s in range(1, steps + 1):
            t_future = now + datetime.timedelta(minutes=15 * s)
            h, m, dow = t_future.hour, t_future.minute, t_future.weekday()
            is_weekend = 1 if dow >= 5 else 0
            nsm = h * 3600 + m * 60

            X = pd.DataFrame([{
                'hour': h,
                'minute': m,
                'day_of_week': dow,
                'is_weekend': is_weekend,
                'NSM': nsm,
                'lag_1h': cur_step_kw / 4.0,
                'lag_24h': current_kw / 4.0,
                'rolling_mean_4h': rolling_kw / 4.0
            }])

            try:
                pred_kwh = float(self.model.predict(X)[0])
                raw_kw = pred_kwh * 4.0
                step_kw = round(current_kw * 0.65 + raw_kw * 0.35, 1)
                step_kw = max(45.0, min(120.0, step_kw))
            except Exception:
                step_kw = round(cur_step_kw * 1.01, 1)

            forecast_points.append({
                'timestamp': t_future.isoformat(),
                'predicted_kw': step_kw,
                'horizon_min': 15 * s
            })
            cur_step_kw = step_kw

        return forecast_points


forecaster = DemandForecaster()
