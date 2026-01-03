@echo off
echo ========================================
echo GreenPoint Model API - Local Test
echo ========================================
echo.

cd model_api

echo Checking Python version...
python --version
echo.

echo Installing core dependencies (this may take a few minutes)...
echo.

REM Install minimal dependencies without geospatial packages that need Rust/GDAL
pip install --user fastapi "uvicorn[standard]" pydantic pandas numpy scikit-learn scipy matplotlib seaborn plotly tqdm python-dotenv requests Pillow click

echo.
echo Note: Some geospatial packages (geopandas, rasterio) are skipped for quick testing.
echo For full functionality, install all dependencies: pip install -r requirements.txt
echo.

echo Starting Model API server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
