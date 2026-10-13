from fastapi import APIRouter
import subprocess
import os
import json

router = APIRouter()

@router.post("/forecast/train")
def train_forecast_model():
    # Execute the actual training pipeline
    try:
        process = subprocess.run(
            ["python3", "scripts/train_forecaster.py"], 
            capture_output=True, text=True, check=True
        )
        
        # Reload registry
        registry = {}
        if os.path.exists("models/forecasting/registry.json"):
            with open("models/forecasting/registry.json", "r") as f:
                registry = json.load(f)
                
        # Force forecaster reload in memory
        from ml.forecasting.model import forecaster
        forecaster.load()
        
        return {"status": "SUCCESS", "logs": process.stdout, "registry": registry}
    except subprocess.CalledProcessError as e:
        return {"status": "ERROR", "error": e.stderr}

@router.get("/forecast/registry")
def get_forecast_registry():
    if os.path.exists("models/forecasting/registry.json"):
        with open("models/forecasting/registry.json", "r") as f:
            return json.load(f)
    return {}
    
@router.get("/forecast/dataset-metadata")
def get_dataset_metadata():
    if os.path.exists("data/industrial/uci_steel/dataset_metadata.json"):
        with open("data/industrial/uci_steel/dataset_metadata.json", "r") as f:
            return json.load(f)
    return {}
