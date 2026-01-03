# Model API - Successfully Running! 🎉

## Status

✅ **Model API is now running on http://localhost:8000**

## What Was Fixed

### Issue
The original batch script had dependency installation issues:
1. Missing `click` module for uvicorn  
2. `OneHotEncoder` API changed in newer scikit-learn (sparse → sparse_output)
3. Geospatial packages (geopandas, rasterio) require Rust/GDAL compilation

### Solutions Applied

1. **Updated app.py**
   - Made pipeline imports optional
   - API can run without geospatial dependencies
   - Gracefully handles missing dependencies
   - Serves existing data files or trains new models

2. **Fixed impact_prediction.py**
   - Updated `OneHotEncoder` to use `sparse_output` parameter
   - Added fallback for older scikit-learn versions

3. **Installed Core Dependencies**
   ```bash
   pip install --user click starlette pydantic-core annotated-types
   pip install --user --upgrade pydantic fastapi
   ```

## Testing the API

### Health Check
```bash
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing | Select-Object -ExpandProperty Content

# Expected: {"status":"online","message":"GreenPoint Model API"}
```

### API Documentation
Open in browser: http://localhost:8000/docs

### Available Endpoints

- `GET /` - Health check ✅
- `GET /data/scores` - GI scores (requires outputs/)
- `GET /data/priorities` - Intervention priorities (requires outputs/)
- `GET /data/indicators` - All indicators (requires outputs/)
- `GET /data/final_results` - Complete results (requires outputs/)
- `GET /data/recommendations` - Recommendations (requires outputs/)
- `POST /predict` - Predict intervention impacts ✅
- `POST /run_pipeline` - Trigger pipeline (requires geospatial libs)

## Next Steps

### Option 1: Use Existing Data (Quick)
If you have pre-computed outputs from the notebook:
1. Copy the outputs from `analysis_workspace/outputs/` to `model_api/outputs/`
2. Restart the API
3. All data endpoints will work

### Option 2: Generate Data (Requires Full Setup)
To run the full pipeline and generate data:
1. Install geospatial dependencies (requires GDAL/Rust):
   ```bash
   # This may be complex on Windows
   pip install geopandas rasterio fiona
   ```
2. Run the pipeline manually or via API endpoint

### Option 3: Use API for Predictions Only (Current)
The API is currently functional for:
- Health checks ✅
- ML model predictions ✅
- Training new models ✅

## Testing Predictions

```bash
# PowerShell
$body = @{
    barangay_features = @{
        baseline_ndvi = 0.3
        baseline_lst = 32
        baseline_canopy = 15
        impervious_surface_pct = 70
        population_density = 8000
        building_density = 0.6
        flood_depth = 1.0
        storm_surge_height = 2.0
    }
    intervention_type = "street_trees"
    intervention_scale = @{
        intervention_area = 5000
        tree_count = 200
        green_roof_area = 1000
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing | Select-Object -ExpandProperty Content
```

## Integration with Next.js

Now that the Model API is running:

1. **Set Environment Variable**
   Create `.env.local` in the root:
   ```env
   NEXT_PUBLIC_MODEL_API_URL=http://localhost:8000
   ```

2. **Test Integration**
   - Next.js is already configured to proxy requests
   - The `modelAPI` client is ready to use
   - Restart Next.js dev server to pick up env vars

3. **Use in Components**
   ```typescript
   import { modelAPI } from '@/lib/api/model-api';
   
   // Fetch predictions
   const impact = await modelAPI.predictImpact({...});
   ```

## Server Control

- **Stop Server**: Ctrl+C in the terminal running uvicorn
- **Restart Server**: Run the command again
- **Check if Running**: `Invoke-WebRequest -Uri "http://localhost:8000/"`

## Summary

The Model API is successfully running with core ML functionality. While the full geospatial pipeline requires additional setup, the API can:
- Serve predictions
- Train and cache models
- Integrate with Next.js

For full data endpoints, either copy pre-computed outputs or install geospatial dependencies.
