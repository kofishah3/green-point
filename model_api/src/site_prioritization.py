"""
Site Prioritization using TOPSIS and Multi-Criteria Decision Analysis
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Tuple


class SitePrioritizer:
    """Prioritize barangays for greening interventions"""
    
    def __init__(self, gi_scores: pd.DataFrame, indicators: pd.DataFrame):
        self.gi_scores = gi_scores
        self.indicators = indicators
        self.priorities = None
        
    def prepare_criteria_matrix(self, criteria_cols: List[str]) -> np.ndarray:
        """Prepare and normalize criteria matrix"""
        # Combine GI scores and indicators
        data = pd.concat([self.gi_scores, self.indicators], axis=1)
        
        # Extract criteria
        available_criteria = [c for c in criteria_cols if c in data.columns]
        if not available_criteria:
            raise ValueError('No criteria columns available')
        
        matrix = data[available_criteria].fillna(0).values
        
        # Normalize
        scaler = MinMaxScaler()
        matrix_norm = scaler.fit_transform(matrix)
        
        return matrix_norm, available_criteria
    
    def topsis(self,
               criteria_matrix: np.ndarray,
               weights: np.ndarray,
               impacts: List[str]) -> np.ndarray:
        """
        TOPSIS: Technique for Order of Preference by Similarity to Ideal Solution
        
        Args:
            criteria_matrix: Normalized criteria matrix (n_alternatives × n_criteria)
            weights: Criteria weights
            impacts: '+' for benefit, '-' for cost
        """
        # Weighted normalized matrix
        weighted_matrix = criteria_matrix * weights
        
        # Ideal solutions
        ideal_best = np.zeros(weighted_matrix.shape[1])
        ideal_worst = np.zeros(weighted_matrix.shape[1])
        
        for j, impact in enumerate(impacts):
            if impact == '+':
                ideal_best[j] = weighted_matrix[:, j].max()
                ideal_worst[j] = weighted_matrix[:, j].min()
            else:
                ideal_best[j] = weighted_matrix[:, j].min()
                ideal_worst[j] = weighted_matrix[:, j].max()
        
        # Euclidean distances
        dist_best = np.sqrt(((weighted_matrix - ideal_best) ** 2).sum(axis=1))
        dist_worst = np.sqrt(((weighted_matrix - ideal_worst) ** 2).sum(axis=1))
        
        # Relative closeness to ideal solution
        scores = dist_worst / (dist_best + dist_worst + 1e-10)
        
        return scores
    
    def compute_priorities(self,
                          criteria: Dict[str, str] = None,
                          weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        Compute intervention priorities using TOPSIS
        
        Args:
            criteria: Dict of criterion_name -> impact ('+' or '-')
            weights: Dict of criterion_name -> weight
        """
        print('='*60)
        print('COMPUTING INTERVENTION PRIORITIES')
        print('='*60)
        
        # Default criteria
        if criteria is None:
            criteria = {
                'gi_score': '-',  # Lower GI = higher priority
                'population': '+',  # Higher population = higher priority
                'multi_hazard_exposure': '+',  # Higher exposure = higher priority
                'per_capita_green_space': '-',  # Lower green space = higher priority
                'heat_anomaly': '+'  # Higher heat = higher priority
            }
        
        # Default equal weights
        if weights is None:
            weights = {k: 1.0 / len(criteria) for k in criteria.keys()}
        
        # Prepare criteria matrix
        criteria_cols = list(criteria.keys())
        matrix, available_criteria = self.prepare_criteria_matrix(criteria_cols)
        
        print(f'Using {len(available_criteria)} criteria:')
        for c in available_criteria:
            print(f'  - {c}: {criteria.get(c, "+")} (weight: {weights.get(c, 0.0):.2f})')
        
        # Get weights and impacts for available criteria
        weights_array = np.array([weights.get(c, 1.0 / len(available_criteria)) 
                                 for c in available_criteria])
        impacts = [criteria.get(c, '+') for c in available_criteria]
        
        # Normalize weights
        weights_array = weights_array / weights_array.sum()
        
        # Apply TOPSIS
        scores = self.topsis(matrix, weights_array, impacts)
        
        # Create results DataFrame
        results = pd.DataFrame(index=self.gi_scores.index)
        results['priority_score'] = scores
        results['priority_rank'] = scores.argsort()[::-1] + 1
        
        # Add GI score for reference
        results['gi_score'] = self.gi_scores['gi_score']
        results['gi_level'] = self.gi_scores['gi_level']
        
        # Priority classification
        results['priority_level'] = pd.cut(
            results['priority_score'],
            bins=[0, 0.3, 0.5, 0.7, 0.9, 1.0],
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        print('='*60)
        print('PRIORITIZATION SUMMARY')
        print('='*60)
        print(f'Mean priority score: {results["priority_score"].mean():.3f}')
        print(f'\nPriority Level Distribution:')
        print(results['priority_level'].value_counts().sort_index())
        print('='*60)
        
        self.priorities = results
        return results
    
    def get_top_priorities(self, n: int = 10) -> pd.DataFrame:
        """Get top N priority barangays"""
        if self.priorities is None:
            raise ValueError('Must compute priorities first')
        
        return self.priorities.nsmallest(n, 'priority_rank')
    
    def compute_cost_effectiveness(self,
                                   cost_per_sqm: float = 500) -> pd.DataFrame:
        """
        Compute cost-effectiveness scores
        
        Args:
            cost_per_sqm: Estimated cost per square meter of intervention
        """
        if self.priorities is None:
            raise ValueError('Must compute priorities first')
        
        results = self.priorities.copy()
        
        # Estimate intervention area (inverse of GI score)
        gi_deficit = 1 - results['gi_score']
        
        if 'total_area' in self.indicators.columns:
            intervention_area = gi_deficit * self.indicators['total_area']
        else:
            intervention_area = gi_deficit * 10000  # Default 1 hectare
        
        # Estimate cost
        results['estimated_cost'] = intervention_area * cost_per_sqm
        
        # Cost-effectiveness (priority per peso)
        results['cost_effectiveness'] = (
            results['priority_score'] / (results['estimated_cost'] + 1)
        )
        
        results['cost_effectiveness_rank'] = (
            results['cost_effectiveness'].rank(ascending=False)
        )
        
        return results


def get_default_prioritization_criteria() -> Dict[str, str]:
    """Default TOPSIS criteria with impacts"""
    return {
        'gi_score': '-',  # Lower is higher priority
        'population': '+',  # Higher is higher priority
        'multi_hazard_exposure': '+',
        'per_capita_green_space': '-',
        'heat_anomaly': '+',
        'poverty_rate': '+',  # If available
        'elderly_population': '+',  # If available
    }


def get_default_prioritization_weights() -> Dict[str, float]:
    """Default criteria weights (expert opinion)"""
    return {
        'gi_score': 0.25,
        'population': 0.15,
        'multi_hazard_exposure': 0.20,
        'per_capita_green_space': 0.15,
        'heat_anomaly': 0.15,
        'poverty_rate': 0.05,
        'elderly_population': 0.05
    }




