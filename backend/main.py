import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routes


app = FastAPI(
    title="Factory Energy Autopilot API",
    description="API for the Factory Energy Optimization Platform",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.simulation import simulation_controller

from ml.online_learner import continuous_learning_loop
import asyncio
from api.google_sheets import gsheets_db

@app.on_event("startup")
def startup_event():
    gsheets_db.connect()
    simulation_controller.start()
    asyncio.create_task(continuous_learning_loop())

@app.on_event("shutdown")
def shutdown_event():
    simulation_controller.stop()
    gsheets_db.flush_telemetry()

app.include_router(routes.router, prefix="/api")
from api import telemetry

app.include_router(telemetry.router, prefix="/api")
from api import control
app.include_router(control.router, prefix="/api")


from api import train_route
app.include_router(train_route.router, prefix="/api")

from api import asset_routes
app.include_router(asset_routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Factory Energy Autopilot API is running"}
