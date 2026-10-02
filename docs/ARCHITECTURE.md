# Architecture: Factory Energy Autopilot

## 1. High-Level Architecture

```mermaid
flowchart TD
    Factory[Factory] --> EdgeConnector
    EdgeConnector --> ArduinoUnoQ[Arduino UNO Q]
    ArduinoUnoQ --> DataIngestion[Data Ingestion (FastAPI/Modbus)]
    
    DataIngestion --> DataEngine[Data Engine]
    
    DataEngine --> ForecastingAI[Forecasting AI]
    DataEngine --> AnomalyAI[Anomaly AI]
    DataEngine --> EnergyDNA[Energy DNA Engine]
    
    ForecastingAI --> PeakAttribution[Peak Attribution]
    AnomalyAI --> PeakAttribution
    EnergyDNA --> PeakAttribution
    
    PeakAttribution --> ConstraintEngine[Constraint Engine]
    ConstraintEngine --> Optimizer[OR-Tools Optimizer]
    
    Optimizer --> RecommendationEngine[Recommendation Engine]
    
    RecommendationEngine --> Simulator[What-If Simulator]
    RecommendationEngine --> OperatorUI[Operator UI]
    
    OperatorUI --> FutureHardware[Future Hardware Control]
    FutureHardware --> VerifyResult[Verify Result]
```

## 2. Core Principles
- **Production is a constraint. Energy is the optimization variable.** 
- We do not optimize by stopping critical production.
- Flexible, opportunistic, and overlapping loads are optimized to minimize peak demand and energy costs.

## 3. Technology Stack
- **Frontend**: Next.js, TypeScript, Tailwind CSS, shadcn/ui, ECharts
- **Backend**: Python, FastAPI, Pydantic
- **Database**: Supabase PostgreSQL
- **AI/ML**: Scikit-learn, XGBoost, Isolation Forest
- **Optimization**: Google OR-Tools
- **Deployment**: Vercel (Frontend), Docker on Render/Cloud Run (Backend)

## 4. Data Source Abstraction
An abstract interface `EnergyDataSource` ensures the system works with simulated data now, and real hardware (L&T Meter via Modbus/Arduino UNO Q) in the future without backend logic rewrites.

- `SimulatedEnergyDataSource` (Current)
- `UnoQEnergyDataSource` (Future)

## 5. Sub-Systems
1. **Digital Factory Model**: Realistic physics-informed simulator (not just random numbers).
2. **Asset Model**: Encapsulates state (OFF, STARTING, RUNNING, IDLE, FAULT) and criticality (CRITICAL, FLEXIBLE, OPPORTUNISTIC).
3. **Forecasting**: Predicts 15, 30, 60-minute ahead demand peaks.
4. **Optimization Engine**: Uses OR-Tools with MILP scheduling to shift flexible loads without violating production constraints.
