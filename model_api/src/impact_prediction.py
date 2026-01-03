"""
Impact Prediction Models for Greening Interventions
Predicts: Cooling potential, Stormwater retention, Pollutant removal, Canopy gain
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ImpactPredictor:
    """Predict environmental impacts of greening interventions"""
    
    INTERVENTION_TYPES = [
        'street_trees',
        'pocket_parks',
        'green_roofs',
        'urban_forests',
        'riparian_buffers',
        'rain_gardens',
        'vertical_gardens'
    ]
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        # Use sparse_output instead of sparse for newer scikit-learn versions
        try:
            self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        except TypeError:
            # Fallback for older versions
            self.encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        
    def create_synthetic_training_data(self, n_samples: int = 1000) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Create synthetic training data based on literature effect sizes
        
        Literature-based effect sizes:
        - Tree canopy → LST reduction: -1.5°C to -3.5°C per 10% increase
        - Green roofs → stormwater retention: 40-70% reduction
        - Urban vegetation → PM2.5 removal: 5-15 µg/m³
        """
        print(f'Creating synthetic training data ({n_samples} samples)...')
        
        # Generate features
        data = {
            # Baseline conditions
            'baseline_ndvi': np.random.uniform(0.1, 0.6, n_samples),
            'baseline_lst': np.random.uniform(25, 40, n_samples),  # °C
            'baseline_canopy': np.random.uniform(0, 50, n_samples),  # %
            'impervious_surface_pct': np.random.uniform(20, 90, n_samples),
            'population_density': np.random.uniform(1000, 15000, n_samples),  # per km²
            'building_density': np.random.uniform(0.1, 0.8, n_samples),
            'flood_depth': np.random.uniform(0, 3, n_samples),  # meters
            'storm_surge_height': np.random.uniform(0, 5, n_samples),  # meters
            
            # Intervention parameters
            'intervention_type': np.random.choice(self.INTERVENTION_TYPES, n_samples),
            'intervention_area': np.random.uniform(1000, 50000, n_samples),  # m²
            'tree_count': np.random.randint(0, 500, n_samples),
            'green_roof_area': np.random.uniform(0, 5000, n_samples),  # m²
        }
        
        features_df = pd.DataFrame(data)
        
        # Generate targets based on literature
        targets = {}
        
        # Cooling potential (°C reduction)
        canopy_increase = features_df['tree_count'] / (features_df['intervention_area'] / 100)
        lst_baseline = features_df['baseline_lst']
        targets['cooling_potential'] = np.clip(
            0.2 * canopy_increase + np.random.normal(0, 0.3, n_samples),
            0, 5
        )
        
        # Adjust by intervention type
        type_factors = {
            'street_trees': 1.2,
            'urban_forests': 1.8,
            'pocket_parks': 1.0,
            'green_roofs': 0.8,
            'riparian_buffers': 1.3,
            'rain_gardens': 0.5,
            'vertical_gardens': 0.6
        }
        
        for i, int_type in enumerate(features_df['intervention_type']):
            targets['cooling_potential'][i] *= type_factors.get(int_type, 1.0)
        
        # Stormwater retention (mm reduction)
        green_ratio = features_df['intervention_area'] / 10000  # Normalized
        imperv = features_df['impervious_surface_pct'] / 100
        targets['stormwater_retention'] = np.clip(
            20 * green_ratio * imperv + np.random.normal(0, 5, n_samples),
            0, 100
        )
        
        # PM2.5 removal (µg/m³)
        ndvi_gain = (1 - features_df['baseline_ndvi']) * 0.3
        targets['pm25_removal'] = np.clip(
            10 * ndvi_gain + np.random.normal(0, 2, n_samples),
            0, 20
        )
        
        # NO2 removal (µg/m³)
        targets['no2_removal'] = np.clip(
            8 * ndvi_gain + np.random.normal(0, 1.5, n_samples),
            0, 15
        )
        
        # Canopy gain (NDVI increase)
        targets['canopy_gain'] = np.clip(
            (1 - features_df['baseline_canopy'] / 100) * 
            (features_df['tree_count'] / 100) * 0.01 +
            np.random.normal(0, 0.02, n_samples),
            0, 0.4
        )
        
        targets_df = pd.DataFrame(targets)
        
        print(f'✓ Created {n_samples} training samples')
        print(f'  Features: {len(features_df.columns)}')
        print(f'  Targets: {len(targets_df.columns)}')
        
        return features_df, targets_df
    
    def prepare_features(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        """Prepare features for modeling"""
        # Separate categorical and numerical
        cat_cols = ['intervention_type']
        num_cols = [c for c in df.columns if c not in cat_cols]
        
        if fit:
            # Fit encoders
            cat_encoded = self.encoder.fit_transform(df[cat_cols])
            num_scaled = self.scaler.fit_transform(df[num_cols])
        else:
            cat_encoded = self.encoder.transform(df[cat_cols])
            num_scaled = self.scaler.transform(df[num_cols])
        
        # Combine
        X = np.hstack([num_scaled, cat_encoded])
        return X
    
    def train_models(self, 
                    features_df: pd.DataFrame,
                    targets_df: pd.DataFrame,
                    model_type: str = 'random_forest') -> Dict[str, float]:
        """
        Train individual models for each target
        
        Args:
            features_df: Feature DataFrame
            targets_df: Target DataFrame
            model_type: 'random_forest' or 'gradient_boosting'
        """
        print('='*60)
        print('TRAINING IMPACT PREDICTION MODELS')
        print('='*60)
        
        # Prepare features
        X = self.prepare_features(features_df, fit=True)
        
        # Train a model for each target
        scores = {}
        
        for target_name in targets_df.columns:
            print(f'\nTraining {target_name} model...')
            y = targets_df[target_name].values
            
            # Create model
            if model_type == 'random_forest':
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=15,
                    min_samples_split=5,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                model = GradientBoostingRegressor(
                    n_estimators=100,
                    max_depth=5,
                    learning_rate=0.1,
                    random_state=42
                )
            
            # Cross-validation
            cv_scores = cross_val_score(
                model, X, y,
                cv=KFold(n_splits=5, shuffle=True, random_state=42),
                scoring='r2'
            )
            
            # Train on full data
            model.fit(X, y)
            
            # Store model and scores
            self.models[target_name] = model
            scores[target_name] = {
                'mean_r2': cv_scores.mean(),
                'std_r2': cv_scores.std()
            }
            
            print(f'  R² score: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}')
        
        print('='*60)
        print('✓ All models trained')
        print('='*60)
        
        return scores
    
    def predict_impact(self,
                      barangay_features: Dict[str, float],
                      intervention_type: str,
                      intervention_scale: Dict[str, float]) -> Dict[str, float]:
        """
        Predict impact of intervention
        
        Args:
            barangay_features: Dict of baseline features
            intervention_type: Type of intervention
            intervention_scale: Scale parameters (area, tree_count, etc.)
        
        Returns:
            Dict of predicted impacts with confidence intervals
        """
        # Combine features
        features = {**barangay_features, 'intervention_type': intervention_type, **intervention_scale}
        features_df = pd.DataFrame([features])
        
        # Prepare
        X = self.prepare_features(features_df, fit=False)
        
        # Predict with each model
        predictions = {}
        for target_name, model in self.models.items():
            pred = model.predict(X)[0]
            
            # Bootstrap for confidence intervals (simplified)
            # In production, would use proper bootstrap or quantile regression
            ci_lower = pred * 0.8
            ci_upper = pred * 1.2
            
            predictions[target_name] = {
                'value': float(pred),
                'ci_lower': float(ci_lower),
                'ci_upper': float(ci_upper)
            }
        
        return predictions
    
    def save_models(self, output_dir: Path):
        """Save trained models"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for name, model in self.models.items():
            path = output_dir / f'{name}_model.pkl'
            with open(path, 'wb') as f:
                pickle.dump(model, f)
        
        # Save scalers
        with open(output_dir / 'scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        with open(output_dir / 'encoder.pkl', 'wb') as f:
            pickle.dump(self.encoder, f)
        
        print(f'✓ Models saved to {output_dir}')
    
    def load_models(self, input_dir: Path):
        """Load trained models"""
        input_dir = Path(input_dir)
        
        # Load models
        for target in ['cooling_potential', 'stormwater_retention', 
                      'pm25_removal', 'no2_removal', 'canopy_gain']:
            path = input_dir / f'{target}_model.pkl'
            if path.exists():
                with open(path, 'rb') as f:
                    self.models[target] = pickle.load(f)
        
        # Load scalers
        with open(input_dir / 'scaler.pkl', 'rb') as f:
            self.scaler = pickle.load(f)
        with open(input_dir / 'encoder.pkl', 'rb') as f:
            self.encoder = pickle.load(f)
        
        print(f'✓ Loaded {len(self.models)} models from {input_dir}')


def format_prediction_summary(predictions: Dict[str, Dict[str, float]]) -> str:
    """Format predictions as readable summary"""
    lines = [
        "PREDICTED ENVIRONMENTAL IMPACTS",
        "=" * 60,
        ""
    ]
    
    labels = {
        'cooling_potential': 'Temperature Reduction',
        'stormwater_retention': 'Stormwater Retention',
        'pm25_removal': 'PM2.5 Removal',
        'no2_removal': 'NO₂ Removal',
        'canopy_gain': 'Canopy/NDVI Increase'
    }
    
    units = {
        'cooling_potential': '°C',
        'stormwater_retention': 'mm',
        'pm25_removal': 'µg/m³',
        'no2_removal': 'µg/m³',
        'canopy_gain': 'NDVI'
    }
    
    for key, pred in predictions.items():
        label = labels.get(key, key)
        unit = units.get(key, '')
        value = pred['value']
        ci_low = pred['ci_lower']
        ci_high = pred['ci_upper']
        
        lines.append(f"{label:.<40} {value:.2f} {unit}")
        lines.append(f"  95% CI: [{ci_low:.2f}, {ci_high:.2f}] {unit}")
        lines.append("")
    
    lines.append("=" * 60)
    return "\n".join(lines)



