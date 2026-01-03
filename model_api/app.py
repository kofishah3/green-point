from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import pandas as pd
import json
import sys
import os

# Add current dir to path
sys.path.append(str(Path(__file__).parent))

# Try to import pipeline components (may fail if geospatial libs not installed)
try:
    from main_pipeline import run_greenpoint_pipeline
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Pipeline not available (missing dependencies: {e})")
    print("API will serve existing data files only.")
    PIPELINE_AVAILABLE = False

from src.impact_prediction import ImpactPredictor
from src.intervention_matcher import InterventionMatcher

app = FastAPI(title="GreenPoint Model API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'Dataset'
OUTPUT_DIR = BASE_DIR / 'outputs'
MODELS_DIR = OUTPUT_DIR / 'models'

# Global state
predictor = None
matcher = None

class PredictionRequest(BaseModel):
    barangay_features: dict
    intervention_type: str
    intervention_scale: dict

@app.on_event("startup")
async def startup_event():
    global predictor, matcher
    
    print("Starting GreenPoint Model API...")
    
    # Ensure outputs directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Check if we should run pipeline
    if not (OUTPUT_DIR / 'greenpoint_final_results.csv').exists():
        if PIPELINE_AVAILABLE:
            print("Outputs not found. Running initial pipeline...")
            try:
                run_greenpoint_pipeline(DATA_DIR, OUTPUT_DIR)
            except Exception as e:
                print(f"Warning: Pipeline failed: {e}")
                print("API will start without pre-computed data.")
        else:
            print("Warning: Outputs not found and pipeline unavailable.")
            print("Install geospatial dependencies: pip install geopandas rasterio fiona")
    else:
        print("Found existing outputs.")

    # Initialize and load models
    predictor = ImpactPredictor()
    if (MODELS_DIR / 'cooling_potential_model.pkl').exists():
        print("Loading trained models...")
        try:
            predictor.load_models(MODELS_DIR)
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
    else:
        print("Models not found. Training new models...")
        try:
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            features_df, targets_df = predictor.create_synthetic_training_data(n_samples=1000)
            predictor.train_models(features_df, targets_df)
            predictor.save_models(MODELS_DIR)
        except Exception as e:
            print(f"Warning: Could not train models: {e}")
    
    matcher = InterventionMatcher()
    print("API Ready.")

@app.get("/")
def read_root():
    return {"status": "online", "message": "GreenPoint Model API"}

@app.get("/data/scores")
def get_scores():
    try:
        df = pd.read_csv(OUTPUT_DIR / 'gi_scores.csv')
        # Replace NaN with null for JSON compatibility
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found: {str(e)}")

@app.get("/data/priorities")
def get_priorities():
    try:
        df = pd.read_csv(OUTPUT_DIR / 'intervention_priorities.csv')
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found: {str(e)}")

@app.get("/data/indicators")
def get_indicators():
    try:
        df = pd.read_csv(OUTPUT_DIR / 'gi_indicators.csv')
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found: {str(e)}")

@app.get("/data/final_results")
def get_final_results():
    try:
        df = pd.read_csv(OUTPUT_DIR / 'greenpoint_final_results.csv')
        # Replace inf/-inf with nan first, then replace nan with None
        df = df.replace([float('inf'), float('-inf')], float('nan'))
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Data not found: {str(e)}")

@app.get("/data/recommendations")
def get_recommendations():
    try:
        df = pd.read_csv(OUTPUT_DIR / 'intervention_recommendations.csv')
        df = df.where(pd.notnull(df), None)
        return df.to_dict(orient='records')
    except Exception as e:
        # If recommendations file doesn't exist, return empty list or error
        # It might not exist if pipeline failed or wasn't fully run
        return []

@app.post("/predict")
def predict_impact(request: PredictionRequest):
    global predictor
    if not predictor:
        raise HTTPException(status_code=503, detail="Predictor not initialized")
    
    try:
        predictions = predictor.predict_impact(
            request.barangay_features,
            request.intervention_type,
            request.intervention_scale
        )
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_pipeline")
def trigger_pipeline():
    """Manually trigger the pipeline to refresh data"""
    if not PIPELINE_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="Pipeline not available. Install geospatial dependencies: pip install geopandas rasterio fiona"
        )
    try:
        run_greenpoint_pipeline(DATA_DIR, OUTPUT_DIR)
        return {"status": "success", "message": "Pipeline executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

