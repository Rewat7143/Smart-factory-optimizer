# Optimization Engine

The core value proposition of the Factory Energy Autopilot is that it treats production as a hard constraint. It optimizes energy *around* production.

## Algorithm
*   **Solver**: Custom Counterfactual Evaluator (Currently scaffolding OR-Tools MILP structure).
*   **Objective**: Minimize Peak Demand (kW) below the Safe Target.

## Constraints
1.  **Production Protection (HARD CONSTRAINT)**: Any proposed schedule that reduces the production target below 100% is categorically `REJECTED`. The system will accept a high peak demand penalty over sacrificing production.
2.  **Asset Flexibility**: Only assets designated as `FLEXIBLE` or `OPPORTUNISTIC` (e.g., HVAC, Auxiliary Pumps, delayable Compressors) can be modified.
3.  **Critical Loads**: Assets tagged with `production_dependency = True` are locked and protected.

## Counterfactual Output
The optimizer does not just return one answer. It returns an evaluation matrix:
1.  **BASELINE**: Do nothing (Usually results in HIGH peak risk).
2.  **REJECTED OPTION**: Stop a production motor (Rejected due to constraint).
3.  **SELECTED OPTION**: Delay a flexible compressor (Reduces peak, maintains production).
