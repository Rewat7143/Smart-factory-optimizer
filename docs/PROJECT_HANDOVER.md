# Project Handover: Factory Energy Autopilot

## Overview
This document outlines the state, structure, and handover details for the Factory Energy Autopilot built for the INFOSYS IGNITE ENG NEXT 2026 HACK-AI-THON.

## Current State
The project is initialized in a monorepo structure containing both frontend and backend systems, built initially with a realistic physics-informed factory digital twin. 

## Development Phases
- [x] Phase 1: Repository setup, Next.js, FastAPI, configuration.
- [ ] Phase 2: Database, Factory model, Asset model, Tariff model.
- [ ] Phase 3: Simulator, Machine states, Production model, Scenarios.
- [ ] Phase 4-21: Ongoing...

## Running the Application
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Future Hardware Integration
The system is built with an abstraction layer (`EnergyDataSource`) allowing the simulated factory model to be seamlessly swapped out for live data from L&T energy meters communicating via RS-485 Modbus to an Arduino UNO Q, which in turn sends data to the FastAPI ingestion layer.

## Key Constraints Validated
- The system must never recommend optimizing by stopping critical production. 
- All optimizations target flexible/opportunistic loads.
