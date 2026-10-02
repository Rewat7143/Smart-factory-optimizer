# Factory Energy Autopilot

"Optimize the energy around production — never optimize by stopping production."

## Architecture
The system consists of a Next.js (React) frontend and a FastAPI (Python) backend. The platform is designed to be hardware-agnostic. Currently, it runs a software simulator for evaluation purposes.

*   **Frontend**: Next.js 14, Tailwind CSS, ECharts for React.
*   **Backend**: FastAPI, Google OR-Tools, XGBoost, Scikit-Learn (Isolation Forest).

## Getting Started

### 1. Prerequisites
*   Node.js v18+
*   Python 3.10+

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Quick Start (Development)
The repository includes a concurrent start script that boots both servers.
```bash
chmod +x start-dev.sh
./start-dev.sh
```

- Frontend runs at: `http://localhost:3000`
- Backend API runs at: `http://localhost:8000`

### 4. Running Tests
```bash
cd backend
source .venv/bin/activate
python -m pytest tests
```

## AI Pipeline
The platform utilizes a three-stage AI architecture:
1.  **Forecast (XGBoost):** Predicts 15-minute demand horizons based on historical lag features and production schedules.
2.  **Anomaly Detection (Isolation Forest):** Unsupervised model trained on individual asset history to detect idle waste and mechanical faults.
3.  **Optimization (OR-Tools):** Constraint-solver that schedules flexible loads to minimize peak demand without violating the hard 100% production target constraint.
