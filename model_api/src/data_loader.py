"""
Data loading utilities for GreenPoint framework
"""
import pandas as pd
import geopandas as gpd
import rasterio
from pathlib import Path
from typing import Optional, Dict, Any
import warnings

warnings.filterwarnings('ignore')


class GreenPointDataLoader:
    """Load and manage GreenPoint datasets"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.datasets = {}
        
    def load_barangay_geography(self) -> gpd.GeoDataFrame:
        """Load barangay geography with geometry"""
        print('Loading barangay geography...')
        df = pd.read_csv(self.data_dir / 'brgy_geography.csv')
        
        if 'geometry' in df.columns:
            from shapely import wkt
            df['geometry'] = df['geometry'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
            print(f'✓ Loaded {len(gdf)} barangays')
            return gdf
        return df
    
    def load_ndvi_data(self) -> Optional[pd.DataFrame]:
        """Load Sentinel-2 NDVI data"""
        ndvi_file = 'Sentinel-2 L2A-3_NDVI-2020-10-20T00_00_00.000Z-2025-10-20T23_59_59.999Z.csv'
        path = self.data_dir / ndvi_file
        
        if path.exists():
            print('Loading NDVI data...')
            df = pd.read_csv(path)
            print(f'✓ Loaded NDVI data: {df.shape}')
            return df
        print(f'⚠ NDVI data not found')
        return None
    
    def load_tree_cover_density(self) -> Optional[Dict[str, Any]]:
        """Load Tree Cover Density raster"""
        tcd_file = '2020-01-01-00_00_2020-01-01-23_59_TCD_Pan-tropical_10m_Yearly_V1_TCD-10.tiff'
        path = self.data_dir / tcd_file
        
        if path.exists():
            print('Loading Tree Cover Density...')
            with rasterio.open(path) as src:
                data = src.read(1)
                meta = src.meta
                bounds = src.bounds
            
            print(f'✓ Loaded TCD: {data.shape}')
            return {'data': data, 'meta': meta, 'bounds': bounds}
        print(f'⚠ TCD data not found')
        return None
    
    def load_lst_data(self) -> Optional[pd.DataFrame]:
        """Load Land Surface Temperature data"""
        lst_file = 'Sentinel-3 SLSTR-F1_VISUALIZED-2020-10-08T00_00_00.000Z-2025-10-08T23_59_59.999Z.csv'
        path = self.data_dir / lst_file
        
        if path.exists():
            print('Loading LST data...')
            df = pd.read_csv(path)
            print(f'✓ Loaded LST data: {df.shape}')
            return df
        print(f'⚠ LST data not found')
        return None
    
    def load_hazard_map(self, hazard_type: str) -> Optional[gpd.GeoDataFrame]:
        """
        Load hazard shapefiles
        
        Args:
            hazard_type: 'flood', 'storm_surge', or 'landslide'
        """
        file_map = {
            'flood': 'PH072200000_FH_100yr.shp',
            'storm_surge': 'Cebu_StormSurge_SSA4.shp',
            'landslide': 'Cebu_LandslideHazards.shp'
        }
        
        if hazard_type not in file_map:
            raise ValueError(f"Unknown hazard type: {hazard_type}")
        
        path = self.data_dir / file_map[hazard_type]
        
        if path.exists():
            print(f'Loading {hazard_type} hazard map...')
            gdf = gpd.read_file(path)
            print(f'✓ Loaded {hazard_type}: {gdf.shape}')
            return gdf
        print(f'⚠ {hazard_type} data not found')
        return None
    
    def load_air_quality(self, nrows: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Load air quality data"""
        aq_file = 'climate_air_quality.csv'
        path = self.data_dir / aq_file
        
        if path.exists():
            print('Loading air quality data...')
            df = pd.read_csv(path, nrows=nrows)
            print(f'✓ Loaded air quality data: {df.shape}')
            return df
        print(f'⚠ Air quality data not found')
        return None
    
    def load_population_data(self) -> Optional[pd.DataFrame]:
        """Load WorldPop population data"""
        pop_file = 'worldpop_population.csv'
        path = self.data_dir / pop_file
        
        if path.exists():
            print('Loading population data...')
            df = pd.read_csv(path)
            print(f'✓ Loaded population data: {df.shape}')
            return df
        print(f'⚠ Population data not found')
        return None
    
    def load_building_footprints(self) -> Optional[pd.DataFrame]:
        """Load Google Open Buildings data"""
        buildings_file = 'google_open_buildings.csv'
        path = self.data_dir / buildings_file
        
        if path.exists():
            print('Loading building footprints...')
            df = pd.read_csv(path)
            print(f'✓ Loaded building data: {df.shape}')
            return df
        print(f'⚠ Building data not found')
        return None
    
    def load_climate_indices(self) -> Optional[pd.DataFrame]:
        """Load climate indices (SPI, precipitation)"""
        climate_file = 'climate_indices.csv'
        path = self.data_dir / climate_file
        
        if path.exists():
            print('Loading climate indices...')
            df = pd.read_csv(path)
            print(f'✓ Loaded climate indices: {df.shape}')
            return df
        print(f'⚠ Climate indices not found')
        return None
    
    def load_all(self) -> Dict[str, Any]:
        """Load all available datasets"""
        print('Loading all datasets...')
        print('='*60)
        
        datasets = {
            'barangay_geography': self.load_barangay_geography(),
            'ndvi': self.load_ndvi_data(),
            'tree_cover': self.load_tree_cover_density(),
            'lst': self.load_lst_data(),
            'flood_hazard': self.load_hazard_map('flood'),
            'storm_surge': self.load_hazard_map('storm_surge'),
            'landslide_hazard': self.load_hazard_map('landslide'),
            'air_quality': self.load_air_quality(nrows=10000),
            'population': self.load_population_data(),
            'buildings': self.load_building_footprints(),
            'climate': self.load_climate_indices()
        }
        
        print('='*60)
        loaded = sum(1 for v in datasets.values() if v is not None)
        print(f'✓ Loaded {loaded}/{len(datasets)} datasets')
        
        self.datasets = datasets
        return datasets




