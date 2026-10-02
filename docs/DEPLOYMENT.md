# Deployment Guide

## Production Environment Architecture
*   **Frontend**: Vercel (Next.js App Router)
*   **Backend API**: Dockerized FastAPI on AWS ECS or DigitalOcean App Platform
*   **Database**: Supabase (PostgreSQL)

## Local Verification
Before deploying, verify the build locally:

### 1. Backend Verification
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/
uvicorn main:app --host 0.0.0.0 --port 8000
```
Check health at: `http://localhost:8000/api/system/status`

### 2. Frontend Verification
```bash
cd frontend
npm install
npm run build
npm run start
```
*Note: If building inside an offline sandbox container, `npm run build` may fail if it cannot reach `fonts.googleapis.com`. This is a sandbox networking restriction, not an application failure. Use `npm run dev` for local offline verification.*

## Environment Variables
Ensure the production environment contains:
- `NEXT_PUBLIC_API_URL` (Pointing to the hosted FastAPI instance)
- `DATABASE_URL` (For future Supabase integration)
