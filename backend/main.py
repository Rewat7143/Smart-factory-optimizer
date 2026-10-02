from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routes
from dotenv import load_dotenv

load_dotenv()

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

app.include_router(routes.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Factory Energy Autopilot API is running"}
