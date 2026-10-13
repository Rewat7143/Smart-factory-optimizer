import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """        # Calculate dynamic bin coverage requirements based on the actual telemetry polling frequency
        # We find the median time delta between consecutive readings to infer the hardware's true polling interval.
        median_interval_sec = history_df.index.to_series().diff().dt.total_seconds().median()
        if pd.isna(median_interval_sec) or median_interval_sec <= 0:
            median_interval_sec = 1.0 # fallback
            
        expected_per_bin = (15 * 60) / median_interval_sec
        # Require at least 25% of expected readings, and an absolute minimum of 3 readings to prevent stray single-point clusters
        MIN_BIN_COUNT = max(3, int(expected_per_bin * 0.25))
        
        # 3. Check for unacceptable missing data gaps for required lags
        t_pred = now + pd.Timedelta(minutes=15)
        
        t_lag1h = t_pred - pd.Timedelta(hours=1)
        t_lag24h = t_pred - pd.Timedelta(hours=24)
        
        # Check if exactly required lags are present in the dataset AND have sufficient density
        if t_lag1h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag1h, 'mean']):
            raise Exception(f"Missing required data for lag_1h at {t_lag1h}")
        if resampled_df.loc[t_lag1h, 'count'] < MIN_BIN_COUNT:
            raise Exception(f"Inadequate sampling for lag_1h at {t_lag1h} (Count: {resampled_df.loc[t_lag1h, 'count']} < {MIN_BIN_COUNT})")
            
        if t_lag24h not in resampled_df.index or pd.isna(resampled_df.loc[t_lag24h, 'mean']):
            raise Exception(f"Missing required data for lag_24h at {t_lag24h}")
        if resampled_df.loc[t_lag24h, 'count'] < MIN_BIN_COUNT:
            raise Exception(f"Inadequate sampling for lag_24h at {t_lag24h} (Count: {resampled_df.loc[t_lag24h, 'count']} < {MIN_BIN_COUNT})")
"""

pattern = r'        MIN_BIN_COUNT = 45\s*# 3\. Check for unacceptable missing data gaps.*\(Count: \{resampled_df\.loc\[t_lag24h, \'count\'\]\} < \{MIN_BIN_COUNT\}\)"\)'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
