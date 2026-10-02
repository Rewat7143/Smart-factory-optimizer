# Known Limitations & Future Work

As an early-stage MVP designed for the INFOSYS IGNITE ENG NEXT 2026 Hackathon, the following limitations are explicitly acknowledged:

1.  **Hardware Connection**: The application currently runs on a deterministic software simulator. The `UnoQDataSource` adapter exists in architecture but requires physical wiring to an L&T meter to process live Modbus data.
2.  **Database Persistence**: `HistoryGenerator` generates a 30-day realistic DataFrame in-memory upon backend boot. In a production environment, this will be replaced with TimescaleDB or PostgreSQL (Supabase) as defined in `schema.sql`.
3.  **OR-Tools MILP Model**: While the constraints (Production = 100%) are mathematically enforced by the current algorithm, the full Mixed Integer Linear Programming (MILP) model using Google OR-Tools is simplified for real-time presentation speed. 
4.  **Security**: The application currently lacks an authentication layer (OAuth/JWT) and multi-tenant isolation, which would be required before cloud deployment.
5.  **Scale Simulator**: The `/fleet` page uses a linear scale multiplier. A true enterprise deployment would require distributed edge-node aggregators.
