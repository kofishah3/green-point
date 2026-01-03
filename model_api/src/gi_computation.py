"""
GI Score Computation using Entropy Weighting, PCA, and AHP
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import entropy
from typing import Dict, List, Tuple


class GIComputer:
    """Compute final Greenery Index scores"""
    
    def __init__(self, indicators_df: pd.DataFrame):
        self.indicators = indicators_df
        self.weights = {}
        self.gi_scores = None
        
    def compute_entropy_weights(self, domain_indicators: List[str]) -> Dict[str, float]:
        """
        Compute objective weights using entropy method
        Higher entropy = less information = lower weight
        """
        print(f'Computing entropy weights for {len(domain_indicators)} indicators...')
        
        # Normalize data
        data = self.indicators[domain_indicators].fillna(0)
        data_norm = (data - data.min()) / (data.max() - data.min() + 1e-10)
        data_norm = data_norm + 1e-10  # Avoid log(0)
        
        # Compute entropy for each indicator
        n = len(data_norm)
        entropies = {}
        
        for col in domain_indicators:
            p = data_norm[col] / data_norm[col].sum()
            e = -np.sum(p * np.log(p)) / np.log(n) if n > 1 else 0
            entropies[col] = e
        
        # Compute weights (inverse of entropy)
        diversity = {k: 1 - v for k, v in entropies.items()}
        total_diversity = sum(diversity.values())
        weights = {k: v / total_diversity for k, v in diversity.items()}
        
        print(f'✓ Entropy weights computed')
        return weights
    
    def apply_ahp_adjustments(self, 
                             entropy_weights: Dict[str, float],
                             ahp_factors: Dict[str, float]) -> Dict[str, float]:
        """
        Apply AHP expert adjustments to entropy weights
        
        Args:
            entropy_weights: Objective weights from entropy
            ahp_factors: Expert adjustment factors (0.5-2.0 range)
        """
        print('Applying AHP adjustments...')
        
        adjusted = {}
        for indicator, weight in entropy_weights.items():
            factor = ahp_factors.get(indicator, 1.0)
            adjusted[indicator] = weight * factor
        
        # Renormalize
        total = sum(adjusted.values())
        adjusted = {k: v / total for k, v in adjusted.items()}
        
        print(f'✓ AHP adjustments applied')
        return adjusted
    
    def compute_domain_scores(self, 
                             domain_name: str,
                             indicators: List[str],
                             ahp_factors: Optional[Dict[str, float]] = None) -> pd.Series:
        """
        Compute score for one GI domain
        
        Args:
            domain_name: Name of domain
            indicators: List of indicator column names
            ahp_factors: Optional AHP adjustment factors
        """
        print(f'\nComputing {domain_name} domain score...')
        
        # Filter to available indicators
        available_indicators = [i for i in indicators if i in self.indicators.columns]
        
        if not available_indicators:
            print(f'⚠ No indicators available for {domain_name}')
            return pd.Series(0, index=self.indicators.index)
        
        # Compute entropy weights
        entropy_weights = self.compute_entropy_weights(available_indicators)
        
        # Apply AHP if provided
        if ahp_factors:
            weights = self.apply_ahp_adjustments(entropy_weights, ahp_factors)
        else:
            weights = entropy_weights
        
        # Store weights
        self.weights[domain_name] = weights
        
        # Compute weighted score
        data = self.indicators[available_indicators].fillna(0)
        score = sum(data[ind] * weights[ind] for ind in available_indicators)
        
        print(f'✓ {domain_name} scores computed')
        print(f'  Indicators used: {len(available_indicators)}')
        print(f'  Mean score: {score.mean():.3f}')
        
        return score
    
    def compute_gi_scores(self, 
                         domain_definitions: Dict[str, List[str]],
                         ahp_factors: Optional[Dict[str, Dict[str, float]]] = None,
                         domain_weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Compute final GI scores across all domains
        
        Args:
            domain_definitions: Dict mapping domain name to list of indicators
            ahp_factors: Optional AHP factors per domain
            domain_weights: Optional weights for domains (default: equal)
        """
        print('='*60)
        print('COMPUTING GREENERY INDEX (GI) SCORES')
        print('='*60)
        
        results = pd.DataFrame(index=self.indicators.index)
        
        # Compute each domain score
        for domain_name, indicators in domain_definitions.items():
            ahp = ahp_factors.get(domain_name) if ahp_factors else None
            score = self.compute_domain_scores(domain_name, indicators, ahp)
            results[f'{domain_name}_score'] = score
        
        # Compute overall GI score
        domain_cols = [f'{d}_score' for d in domain_definitions.keys()]
        
        if domain_weights is None:
            # Equal weights
            domain_weights = {d: 1.0 / len(domain_definitions) 
                            for d in domain_definitions.keys()}
        
        # Weighted sum of domain scores
        results['gi_score'] = sum(
            results[f'{d}_score'] * domain_weights[d] 
            for d in domain_definitions.keys()
        )
        
        # Classify GI levels
        results['gi_level'] = pd.cut(
            results['gi_score'],
            bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        # Rank barangays
        results['gi_rank'] = results['gi_score'].rank(ascending=False)
        
        print('='*60)
        print('GI COMPUTATION SUMMARY')
        print('='*60)
        print(f'Total barangays: {len(results)}')
        print(f'Mean GI score: {results["gi_score"].mean():.3f}')
        print(f'Std GI score: {results["gi_score"].std():.3f}')
        print(f'\nGI Level Distribution:')
        print(results['gi_level'].value_counts().sort_index())
        print('='*60)
        
        self.gi_scores = results
        return results
    
    def get_weights(self) -> Dict:
        """Return computed weights"""
        return self.weights
    
    def get_gi_scores(self) -> pd.DataFrame:
        """Return GI scores"""
        return self.gi_scores


def get_default_domain_definitions() -> Dict[str, List[str]]:
    """Default GI domain definitions"""
    return {
        'quantity': [
            'ndvi_mean',
            'canopy_cover_pct',
            'green_space_area',
            'green_space_ratio'
        ],
        'accessibility_equity': [
            'per_capita_green_space',
            'proximity_to_parks',
            'vulnerable_group_access',
            'equity_score'
        ],
        'environmental_quality': [
            'heat_anomaly',
            'flood_exposure',
            'storm_surge_exposure',
            'landslide_exposure',
            'air_quality_score',
            'hazard_resilience'
        ],
        'connectivity_biodiversity': [
            'mean_patch_size',
            'fragmentation_index',
            'ecological_connectivity',
            'edge_density'
        ]
    }


def get_default_ahp_factors() -> Dict[str, Dict[str, float]]:
    """Default AHP adjustment factors (expert consensus)"""
    return {
        'quantity': {
            'ndvi_mean': 1.2,
            'canopy_cover_pct': 1.3,
            'green_space_area': 1.0,
            'green_space_ratio': 1.1
        },
        'accessibility_equity': {
            'per_capita_green_space': 1.5,
            'proximity_to_parks': 1.0,
            'vulnerable_group_access': 1.4,
            'equity_score': 1.2
        },
        'environmental_quality': {
            'heat_anomaly': 1.3,
            'flood_exposure': 1.4,
            'storm_surge_exposure': 1.2,
            'landslide_exposure': 1.1,
            'air_quality_score': 1.2,
            'hazard_resilience': 1.5
        },
        'connectivity_biodiversity': {
            'mean_patch_size': 1.0,
            'fragmentation_index': 0.9,
            'ecological_connectivity': 1.2,
            'edge_density': 0.8
        }
    }




