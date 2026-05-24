from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return {
        "service": "ecoanalyzer",
        "status": "running",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "version": os.getenv("IMAGE_TAG", "latest"),
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/analysis")
def analysis():
    return {
        "result": {
            "co2": 42,
            "energy": 120,
            "efficiency": "good"
        }
    }