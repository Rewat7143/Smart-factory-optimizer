import re

file_path = 'backend/ml/forecasting/model.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = """        # Get the rolling 4h window ending at `now` (which is t_pred - 15m)
        t_rolling_start = now - pd.Timedelta(hours=4) + pd.Timedelta(minutes=15) # 16 steps total
        rolling_window = resampled_df.loc[t_rolling_start:now]
        
        # Training strictly dropped any row where rolling(16) had NaNs. 
        # So we must enforce EXACTLY 16 valid, adequately sampled bins.
        if len(rolling_window) != 16:
            raise Exception(f"Insufficient time span in rolling 4h window. Expected 16 steps, found {len(rolling_window)}.")
            
        if rolling_window['mean'].isna().any():
            raise Exception("Rolling 4h window contains missing intervals. Training strictly required 16 contiguous valid intervals.")
            
        # We must also validate that every bin in the rolling window has adequate density
        invalid_bins = rolling_window[rolling_window['count'] < MIN_BIN_COUNT]
        if not invalid_bins.empty:
            raise Exception(f"Rolling window contains bins with inadequate sampling density (< {MIN_BIN_COUNT} readings).")
            
        # 4. Construct Features for t_pred"""

pattern = r'        # Get the rolling 4h window ending at `now`.*# 4\. Construct Features for t_pred'
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)
