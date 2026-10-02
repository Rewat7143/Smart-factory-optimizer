# Judges Q&A: Factory Energy Autopilot

### 1. What exactly is the problem?
Industrial facilities pay massive penalties for exceeding their "contracted peak demand" (the maximum power drawn in a 15-minute window). However, most energy dashboards simply tell factory managers to "use less energy," which usually means slowing down production. That is unacceptable in manufacturing.

### 2. Why can't factories simply switch machines off?
Production schedules are tightly constrained by supply chain demands and labor. Shutting down a critical motor stops the line, costing far more in lost revenue than the energy saved.

### 3. How do you protect production?
We treat production as a **hard mathematical constraint**. The OR-Tools optimization engine is programmed to evaluate schedules. If a proposed schedule (like switching off a main motor) results in `production < target`, the optimizer categorically Rejects it. It will only Select schedules that shift flexible auxiliary loads (like HVAC, pumps, or delayed compressor starts).

### 4. Where is AI actually used?
It is used in a specific three-part pipeline:
1. **Forecasting (XGBoost):** Predicts demand 15 minutes ahead based on historical lags and production rates.
2. **Anomaly Detection (Isolation Forest):** Learns the normal operating envelope of each machine from historical data and flags deviations (idle waste, faults).
3. **Decision Engine (OR-Tools):** Solves the constraint-satisfaction problem to find the optimal load schedule.

### 5. Why XGBoost?
Factory energy consumption is non-linear and heavily dependent on sudden machine startups and categorical states. XGBoost handles tabular, non-linear feature interactions (like time-of-day + machine state + temperature) much better and faster than deep learning models like LSTMs, which are overkill for 15-minute horizon tabular data.

### 6. Why Isolation Forest?
Machine faults are rare, meaning we do not have balanced labeled data of "broken" machines. Isolation Forest is an unsupervised algorithm perfect for identifying outliers (anomalies) in highly dimensional normal operational data without needing explicit failure labels.

### 7. How does the system know which machine caused the peak?
When the forecast predicts a peak, the backend iterates through the `FactoryState` to identify all currently running assets. It ranks them by their active power contribution and categorizes them by criticality, instantly attributing the predicted peak to specific controllable vs. protected loads.

### 8. How does it scale?
The software architecture is fully decoupled. The frontend is stateless Next.js. The backend is a stateless FastAPI service. The core state is held in a database. To scale from 3 assets to 10,000, we simply provision a managed PostgreSQL/Supabase instance and add more rows to the `EnergyReading` table.

### 9. Why Arduino UNO Q / Modbus?
While the current version uses a deterministic software simulator, the architecture utilizes an `EnergyDataSource` abstraction layer. In a real deployment, an L&T physical energy meter reads the current via CT clamps, outputs over RS-485 Modbus to an Arduino UNO Q (or industrial gateway), which then posts the canonical JSON schema to our API. The AI does not know or care if the data comes from the simulator or a physical meter.

### 10. How is ROI calculated?
We maintain absolute data honesty. We separate:
- **Measured:** What the factory actually consumed today.
- **Simulated:** The kWh and kW the optimizer proved it *could* have saved.
- **Projected:** The simulated savings annualized over 12 months, multiplied by the local industrial tariff. We never present simulated savings as realized cash.
