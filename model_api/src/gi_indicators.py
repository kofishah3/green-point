"""
Greenery Index (GI) Indicators Computation
Computes indicators across 4 domains:
1. Quantity
2. Accessibility & Equity  
3. Environmental Quality & Resilience
4. Connectivity & Biodiversity Potential
"""
import pandas as pd
import numpy as np
import geopandas as gpd
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Tuple, Optional


class GIIndicatorComputer:
    """Compute GI domain indicators"""
    
    def __init__(self, barangay_gdf: gpd.GeoDataFrame):
        self.barangay_gdf = barangay_gdf
        self.indicators = pd.DataFrame(index=barangay_gdf.index)
        
    def compute_quantity_indicators(self, 
                                   ndvi_data: pd.DataFrame,
                                   tree_cover_data: np.ndarray) -> pd.DataFrame:
        """
        Domain 1: Quantity
        - NDVI Mean
        - Canopy Cover %
        - Green Space Area
        - Green Space Ratio
        """
        print('Computing Quantity indicators...')
        
        # NDVI Mean per barangay
        if 'adm4_pcode' in self.barangay_gdf.columns and ndvi_data is not None:
            if '3_NDVI' in ndvi_data.columns:
                ndvi_mean = ndvi_data.groupby('adm4_pcode')['3_NDVI'].mean()
                self.indicators['ndvi_mean'] = self.barangay_gdf['adm4_pcode'].map(ndvi_mean)
        
        # Green Space Area (m²) - estimate from total area
        if 'brgy_total_area' in self.barangay_gdf.columns:
            self.indicators['total_area'] = self.barangay_gdf['brgy_total_area']
            
            # Estimate green space from NDVI (NDVI > 0.3 considered vegetated)
            if 'ndvi_mean' in self.indicators.columns:
                # Simple proxy: higher NDVI = more green space
                self.indicators['green_space_area'] = (
                    self.indicators['total_area'] * 
                    np.clip(self.indicators['ndvi_mean'], 0, 1)
                )
                
                # Green Space Ratio
                self.indicators['green_space_ratio'] = (
                    self.indicators['green_space_area'] / 
                    self.indicators['total_area']
                ).fillna(0)
        
        # Canopy Cover % - would need raster zonal stats (placeholder)
        self.indicators['canopy_cover_pct'] = np.nan
        
        print(f'✓ Computed {self._count_valid_cols()} quantity indicators')
        return self.indicators
    
    def compute_accessibility_equity_indicators(self,
                                               population_data: pd.DataFrame) -> pd.DataFrame:
        """
        Domain 2: Accessibility & Equity
        - Per Capita Green Space
        - Proximity to Parks (placeholder)
        - Vulnerable Group Access (placeholder)
        - Equity Score
        """
        print('Computing Accessibility & Equity indicators...')
        
        # Per Capita Green Space
        if population_data is not None and 'population' in population_data.columns:
            if 'adm4_pcode' in population_data.columns:
                pop_sum = population_data.groupby('adm4_pcode')['population'].sum()
                self.indicators['population'] = self.barangay_gdf['adm4_pcode'].map(pop_sum)
                
                if 'green_space_area' in self.indicators.columns:
                    self.indicators['per_capita_green_space'] = (
                        self.indicators['green_space_area'] / 
                        self.indicators['population']
                    ).replace([np.inf, -np.inf], np.nan).fillna(0)
        
        # Equity Score (Gini coefficient - placeholder with simplified version)
        if 'per_capita_green_space' in self.indicators.columns:
            values = self.indicators['per_capita_green_space'].dropna()
            if len(values) > 0:
                # Simplified inequality measure
                mean_val = values.mean()
                std_val = values.std()
                self.indicators['equity_score'] = 1 - (std_val / mean_val if mean_val > 0 else 0)
            else:
                self.indicators['equity_score'] = 0
        
        # Placeholders for future implementation
        self.indicators['proximity_to_parks'] = np.nan
        self.indicators['vulnerable_group_access'] = np.nan
        
        print(f'✓ Computed {self._count_valid_cols()} accessibility indicators')
        return self.indicators
    
    def compute_environmental_quality_indicators(self,
                                                lst_data: pd.DataFrame,
                                                hazard_gdfs: Dict[str, gpd.GeoDataFrame],
                                                air_quality_data: pd.DataFrame) -> pd.DataFrame:
        """
        Domain 3: Environmental Quality & Resilience
        - Heat Anomaly
        - Flood Exposure
        - Air Quality Impact
        - Hazard Resilience
        """
        print('Computing Environmental Quality & Resilience indicators...')
        
        # Heat Anomaly (LST deviation from mean)
        temp_col = None
        if lst_data is not None:
            # Try to find the temperature column
            possible_cols = ['F1_VISUALIZED', 'C0/median', 'C0/mean', 'C0/min', 'C0/max']
            for col in possible_cols:
                if col in lst_data.columns:
                    temp_col = col
                    break
        
        if lst_data is not None and temp_col:
            # Ensure Celsius
            # Check a sample value to determine unit
            sample_val = lst_data[temp_col].mean()
            if sample_val > 200:  # Likely Kelvin (e.g. 300K)
                print(f'Converting LST from Kelvin to Celsius (mean: {sample_val:.1f}K)')
                lst_data[temp_col] = lst_data[temp_col] - 273.15
            else:
                print(f'LST appears to be in Celsius (mean: {sample_val:.1f}°C)')

            city_mean_temp = lst_data[temp_col].mean()
            
            if 'adm4_pcode' in lst_data.columns:
                temp_mean = lst_data.groupby('adm4_pcode')[temp_col].mean()
                self.indicators['mean_lst'] = self.barangay_gdf['adm4_pcode'].map(temp_mean)
                self.indicators['heat_anomaly'] = self.indicators['mean_lst'] - city_mean_temp
            else:
                # Fallback: If no spatial breakdown, use city mean
                print("⚠ LST data lacks 'adm4_pcode'. Using city-wide mean.")
                self.indicators['mean_lst'] = city_mean_temp
                self.indicators['heat_anomaly'] = 0.0
        
        # Hazard Exposure (simplified - would need spatial overlay)
        hazard_cols = []
        for hazard_name, hazard_gdf in hazard_gdfs.items():
            if hazard_gdf is not None:
                col_name = f'{hazard_name}_exposure'
                # Placeholder: binary presence (needs proper spatial analysis)
                self.indicators[col_name] = 0  # Would use spatial join
                hazard_cols.append(col_name)
        
        # Multi-hazard exposure index
        if hazard_cols:
            self.indicators['multi_hazard_exposure'] = (
                self.indicators[hazard_cols].sum(axis=1) / len(hazard_cols)
            )
        
        # Air Quality Impact (placeholder)
        self.indicators['air_quality_score'] = np.nan
        
        # Hazard Resilience (inverse of exposure, weighted by green infrastructure)
        if 'multi_hazard_exposure' in self.indicators.columns:
            if 'green_space_ratio' in self.indicators.columns:
                self.indicators['hazard_resilience'] = (
                    (1 - self.indicators['multi_hazard_exposure']) * 
                    self.indicators['green_space_ratio']
                )
        
        print(f'✓ Computed {self._count_valid_cols()} environmental quality indicators')
        return self.indicators
    
    def compute_connectivity_indicators(self) -> pd.DataFrame:
        """
        Domain 4: Connectivity & Biodiversity Potential
        - Green Patch Size
        - Fragmentation Index
        - Ecological Connectivity
        - Edge Density
        """
        print('Computing Connectivity & Biodiversity indicators...')
        
        # These require detailed raster analysis - placeholders for now
        self.indicators['mean_patch_size'] = np.nan
        self.indicators['fragmentation_index'] = np.nan
        self.indicators['ecological_connectivity'] = np.nan
        self.indicators['edge_density'] = np.nan
        
        print(f'✓ Computed connectivity indicators (placeholders)')
        return self.indicators
    
    def _count_valid_cols(self) -> int:
        """Count columns with non-null values"""
        return self.indicators.notna().any().sum()
    
    def get_indicators(self) -> pd.DataFrame:
        """Return computed indicators"""
        return self.indicators
    
    def normalize_indicators(self) -> pd.DataFrame:
        """Normalize all indicators to [0, 1] scale"""
        print('Normalizing indicators...')
        
        scaler = MinMaxScaler()
        numeric_cols = self.indicators.select_dtypes(include=[np.number]).columns
        
        normalized = self.indicators.copy()
        normalized[numeric_cols] = scaler.fit_transform(
            self.indicators[numeric_cols].fillna(0)
        )
        
        print(f'✓ Normalized {len(numeric_cols)} indicators')
        return normalized




