# GreenPoint Model API - README

## Overview

This directory contains the FastAPI service that exposes the GreenPoint analysis framework as a REST API.

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

### Docker

Build and run with Docker:
```bash
docker build -t greenpoint-model-api .
docker run -p 8000:8000 -v $(pwd)/outputs:/app/outputs greenpoint-model-api
```

## API Endpoints

### Data Endpoints

- `GET /` - Health check
- `GET /data/scores` - GI scores for all barangays
- `GET /data/priorities` - Intervention priorities
- `GET /data/indicators` - All computed indicators
- `GET /data/final_results` - Complete analysis results
- `GET /data/recommendations` - Intervention recommendations

### Prediction Endpoints

- `POST /predict` - Predict impact of interventions
  ```json
  {
    "barangay_features": {
      "baseline_ndvi": 0.3,
      "baseline_lst": 32,
      "baseline_canopy": 15,
      "impervious_surface_pct": 70,
      "population_density": 8000,
      "building_density": 0.6,
      "flood_depth": 1.0,
      "storm_surge_height": 2.0
    },
    "intervention_type": "street_trees",
    "intervention_scale": {
      "intervention_area": 5000,
      "tree_count": 200,
      "green_roof_area": 1000
    }
  }
  ```

### Pipeline Management

- `POST /run_pipeline` - Manually trigger the analysis pipeline

## Directory Structure

```
model_api/
├── app.py                 # FastAPI application
├── main_pipeline.py       # GreenPoint pipeline
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── .dockerignore         # Docker ignore rules
├── src/                  # Source modules
│   ├── data_loader.py
│   ├── gi_indicators.py
│   ├── gi_computation.py
│   ├── site_prioritization.py
│   ├── impact_prediction.py
│   ├── intervention_matcher.py
│   └── visualization.py
├── Dataset/              # Input data (read-only)
└── outputs/              # Generated outputs (persistent)
    ├── gi_scores.csv
    ├── intervention_priorities.csv
    ├── gi_indicators.csv
    ├── greenpoint_final_results.csv
    ├── intervention_recommendations.csv
    └── models/           # Trained ML models
```

## Notes

- The first startup will run the full analysis pipeline (~10-20 minutes)
- Subsequent startups load pre-computed results
- Models are trained on synthetic data and saved for reuse
- The Dataset folder is ~1GB and mounted read-only in Docker
