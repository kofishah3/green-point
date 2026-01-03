# GreenPoint Integration - Quick Start Guide

## Prerequisites

- Python 3.10+ (for Model API)
- Node.js 20+ (for Next.js)
- Docker Desktop (optional, for containerized deployment)

## Option 1: Local Development (Recommended for Testing)

### Step 1: Set up Model API

```bash
# Navigate to model_api directory
cd model_api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### Step 2: Configure Next.js

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_MODEL_API_URL=http://localhost:8000
```

### Step 3: Run Next.js

```bash
# In the root directory
npm run dev
```

The app will be available at http://localhost:3000

## Option 2: Docker Deployment

### Prerequisites
- Docker Desktop must be running

### Build and Run

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

Access:
- Next.js App: http://localhost:3000
- Model API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Services

```bash
docker-compose down
```

## Testing the Integration

### 1. Check Model API Health

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status": "online", "message": "GreenPoint Model API"}
```

### 2. Fetch GI Scores

```bash
curl http://localhost:8000/data/scores
```

### 3. Test Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Troubleshooting

### Model API Issues

**Problem**: API fails to start
- Check Python version: `python --version` (should be 3.10+)
- Check if port 8000 is available
- Review logs for missing dependencies

**Problem**: Pipeline takes too long
- First run processes all data (~10-20 minutes)
- Subsequent runs load cached results
- Check `model_api/outputs/` for generated files

### Next.js Issues

**Problem**: Cannot connect to Model API
- Verify Model API is running: `curl http://localhost:8000/`
- Check `.env.local` has correct `NEXT_PUBLIC_MODEL_API_URL`
- Restart Next.js dev server after changing env vars

**Problem**: CORS errors
- Model API has CORS enabled for all origins
- Check browser console for specific errors

### Docker Issues

**Problem**: Docker build fails
- Ensure Docker Desktop is running
- Check available disk space (images are large)
- Try: `docker system prune` to free space

**Problem**: Container crashes
- Check logs: `docker-compose logs model-api`
- Verify Dataset folder exists and has data
- Check memory allocation in Docker Desktop settings

## Development Workflow

1. **Make changes to analysis code**: Edit files in `model_api/src/`
2. **Restart Model API**: The API will reload automatically with `--reload` flag
3. **Trigger pipeline**: `curl -X POST http://localhost:8000/run_pipeline`
4. **Next.js auto-updates**: Changes to Next.js code hot-reload automatically

## Production Deployment

For production:
1. Use `docker-compose.yml` for orchestration
2. Set proper environment variables
3. Configure reverse proxy (nginx/traefik)
4. Enable HTTPS
5. Set up monitoring and logging
6. Consider using managed services for the database
