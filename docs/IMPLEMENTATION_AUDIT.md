# Implementation Audit

## Subsystem Status

| Subsystem | Classification | Notes |
|-----------|----------------|-------|
| Simulator | SIMULATED | Functional, generates deterministic scenarios. Needs a history buffer to feed ML models genuinely. |
| FactoryState | REAL | The central truth payload from the API is correctly structured. |
| Energy DNA | MOCK | Currently calculates stats from static asset definitions. Needs to be derived from historical simulation runs. |
| Forecasting (XGBoost) | SIMULATED/MOCK | The model uses XGBoost but currently trains on a randomly generated synthetic dataset inside `train()`. Needs to pull actual historical data from the simulator buffer. |
| Anomaly Detection (IsoForest) | SIMULATED/MOCK | Instantiates IsolationForest, but the baseline uses a randomly uniform distribution around the *current* power instead of actual historical normal behavior. |
| Peak Attribution | SIMULATED/MOCK | Partially implemented in `routes.py`, needs formal extraction into a structured attribution engine. |
| Optimization (OR-Tools) | MODEL | The constraint solver logic evaluates constraints (production vs peak). It generates baseline and selected/rejected alternatives correctly. |
| Digital Twin | REAL | Functional representation of the `FactoryState`. |
| Scale Simulator | MOCK | Hardcoded extrapolation multiplier. Needs to be tied to actual calculated opportunity metrics from the ML models. |
| Database | PLACEHOLDER | `schema.sql` created, but Python is not connecting/writing to Supabase/PostgreSQL yet. Memory arrays or local sqlite should be used as intermediate if Supabase isn't provisioned. |

## Red Flags Addressed
1. Energy DNA mock will be replaced with real aggregations.
2. Forecasting and Anomaly models will be wired to a historical data generator that logs actual simulator states over time (e.g. 30 simulated days) and trains on that genuine deterministic behavior.
