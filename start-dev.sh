#!/bin/bash

# Start FastAPI backend
cd backend
source .venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Next.js frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Development servers started."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID
