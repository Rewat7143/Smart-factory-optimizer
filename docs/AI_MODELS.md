# AI Models Evidence

The Factory Energy Autopilot is not a simple dashboard; it uses mathematically rigorous ML models to drive its intelligence.

## 1. Forecasting Engine
*   **Algorithm**: XGBoost Regressor (with Chronos-Bolt benchmarking)
*   **Purpose**: Predict peak power demand into the future to allow proactive load shifting.
*   **Training Data**: REAL INDUSTRIAL DATA. Model is trained on the UCI Steel Industry Energy Consumption dataset (ID 851, 35,040 observations).
*   **Split Methodology**: Chronological split (70% train, 15% validation, 15% test) to prevent future-data leakage.
*   **Features Used**: Time of day (Hour, Minute, NSM), Day of Week, lag_1h, lag_24h, rolling_mean_4h.
*   **Evaluation**: Evaluated using Mean Absolute Error (MAE) and Root Mean Square Error (RMSE) on the held-out test set against a Naive Seasonal Baseline (lag_24h).
*   **Factory Adaptation**: The public industrial dataset provides the bootstrap baseline methodology. Once live factory telemetry arrives via OPC-UA/Modbus, the pipeline is retrained to yield a factory-specific model.

## 2. Anomaly Detection
*   **Algorithm**: Isolation Forest (Scikit-Learn)
*   **Purpose**: Detect mechanical faults (over-drawing power) and idle energy waste (drawing power while not producing) without requiring labeled failure datasets.
*   **Training Data**: Asset-specific historical behavioural fingerprint (Power vs. State).
*   **Execution**: Unsupervised outlier detection calculates an anomaly score and compares it against a 0.05 contamination threshold. Identifies deviation % and extrapolates ₹ cost impact.

## 3. Energy DNA
*   **Engine**: Pandas Analytical Pipeline
*   **Purpose**: Extract the exact operational envelope of each machine (Idle Power, Startup Power, Peak Contribution, Variability) directly from historical data to feed the Optimizer.
