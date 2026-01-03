"""
Intervention Matching using LLM + RAG
Matches barangay profiles to suitable greening interventions
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json


class InterventionMatcher:
    """Match barangay profiles to interventions using rule-based system"""
    
    INTERVENTION_LIBRARY = {
        'street_trees': {
            'name': 'Street Trees',
            'description': 'Plant native trees along roadways and sidewalks',
            'best_for': ['high_heat', 'low_canopy', 'urban_core'],
            'cooling_effect': 'high',
            'stormwater_effect': 'medium',
            'air_quality_effect': 'high',
            'cost_per_sqm': 600,
            'maintenance': 'medium',
            'space_requirement': 'low'
        },
        'pocket_parks': {
            'name': 'Pocket Parks',
            'description': 'Small-scale green spaces in dense urban areas',
            'best_for': ['low_green_space', 'high_population', 'equity_deficit'],
            'cooling_effect': 'medium',
            'stormwater_effect': 'medium',
            'air_quality_effect': 'medium',
            'cost_per_sqm': 800,
            'maintenance': 'medium',
            'space_requirement': 'medium'
        },
        'green_roofs': {
            'name': 'Green Roofs',
            'description': 'Building-integrated vegetation on rooftops',
            'best_for': ['space_constrained', 'high_heat', 'stormwater_issues'],
            'cooling_effect': 'medium',
            'stormwater_effect': 'high',
            'air_quality_effect': 'low',
            'cost_per_sqm': 1200,
            'maintenance': 'high',
            'space_requirement': 'none'
        },
        'urban_forests': {
            'name': 'Urban Forest Restoration',
            'description': 'Large-scale native tree planting and forest restoration',
            'best_for': ['degraded_land', 'biodiversity', 'carbon_sequestration'],
            'cooling_effect': 'very_high',
            'stormwater_effect': 'high',
            'air_quality_effect': 'very_high',
            'cost_per_sqm': 400,
            'maintenance': 'low',
            'space_requirement': 'high'
        },
        'riparian_buffers': {
            'name': 'Riparian Vegetation Buffers',
            'description': 'Vegetated zones along waterways',
            'best_for': ['flood_prone', 'water_quality', 'coastal'],
            'cooling_effect': 'medium',
            'stormwater_effect': 'very_high',
            'air_quality_effect': 'medium',
            'cost_per_sqm': 500,
            'maintenance': 'low',
            'space_requirement': 'medium'
        },
        'rain_gardens': {
            'name': 'Rain Gardens & Bioretention',
            'description': 'Strategic bioretention for stormwater management',
            'best_for': ['flood_prone', 'stormwater_management', 'low_cost'],
            'cooling_effect': 'low',
            'stormwater_effect': 'very_high',
            'air_quality_effect': 'low',
            'cost_per_sqm': 350,
            'maintenance': 'medium',
            'space_requirement': 'low'
        },
        'vertical_gardens': {
            'name': 'Vertical Gardens',
            'description': 'Wall-mounted vegetation systems',
            'best_for': ['space_constrained', 'aesthetic', 'pilot_projects'],
            'cooling_effect': 'low',
            'stormwater_effect': 'low',
            'air_quality_effect': 'low',
            'cost_per_sqm': 1500,
            'maintenance': 'high',
            'space_requirement': 'none'
        }
    }
    
    def __init__(self):
        self.case_studies = self._load_case_studies()
    
    def _load_case_studies(self) -> List[Dict]:
        """Load intervention case studies (would come from literature)"""
        # Simplified case studies
        return [
            {
                'location': 'Singapore',
                'intervention': 'street_trees',
                'profile': {'heat_anomaly': 3.5, 'canopy_cover': 15, 'urban_density': 0.8},
                'outcomes': {'cooling': -2.1, 'satisfaction': 0.85}
            },
            {
                'location': 'Melbourne',
                'intervention': 'urban_forests',
                'profile': {'heat_anomaly': 2.8, 'canopy_cover': 25, 'urban_density': 0.5},
                'outcomes': {'cooling': -3.2, 'biodiversity_increase': 0.4}
            },
            {
                'location': 'Portland',
                'intervention': 'rain_gardens',
                'profile': {'flood_exposure': 0.7, 'imperviousness': 0.6},
                'outcomes': {'stormwater_reduction': 45, 'flood_events': -0.3}
            }
        ]
    
    def match_intervention(self, 
                          barangay_profile: Dict[str, float],
                          budget_constraint: Optional[float] = None) -> Dict[str, any]:
        """
        Match barangay to suitable intervention
        
        Args:
            barangay_profile: Dict with GI scores, hazards, demographics
            budget_constraint: Optional budget limit
        
        Returns:
            Dict with recommended intervention and reasoning
        """
        # Extract key issues
        issues = self._identify_issues(barangay_profile)
        
        # Score interventions
        scores = {}
        for int_type, int_data in self.INTERVENTION_LIBRARY.items():
            score = self._score_intervention(int_type, int_data, issues, barangay_profile)
            
            # Apply budget constraint
            if budget_constraint:
                est_area = barangay_profile.get('intervention_area', 5000)
                est_cost = int_data['cost_per_sqm'] * est_area
                if est_cost > budget_constraint:
                    score *= 0.5  # Penalize but don't eliminate
            
            scores[int_type] = score
        
        # Get top recommendation
        best_intervention = max(scores, key=scores.get)
        best_data = self.INTERVENTION_LIBRARY[best_intervention]
        
        # Generate reasoning
        reasoning = self._generate_reasoning(best_intervention, best_data, issues)
        
        return {
            'intervention_type': best_intervention,
            'intervention_name': best_data['name'],
            'description': best_data['description'],
            'main_issues_addressed': issues[:3],
            'reasoning': reasoning,
            'estimated_cost_per_sqm': best_data['cost_per_sqm'],
            'maintenance_level': best_data['maintenance'],
            'match_score': scores[best_intervention],
            'alternatives': self._get_alternatives(scores, best_intervention)
        }
    
    def _identify_issues(self, profile: Dict[str, float]) -> List[str]:
        """Identify main environmental/social issues"""
        issues = []
        
        # GI deficit
        if profile.get('gi_score', 0.5) < 0.4:
            issues.append('low_greenery')
        
        # Heat
        if profile.get('heat_anomaly', 0) > 1.0:
            issues.append('high_heat')
        
        # Canopy
        if profile.get('canopy_cover_pct', 50) < 20:
            issues.append('low_canopy')
        
        # Flood
        if profile.get('flood_exposure', 0) > 0.5:
            issues.append('flood_prone')
        
        # Storm surge
        if profile.get('storm_surge_exposure', 0) > 0.5:
            issues.append('coastal_hazard')
        
        # Air quality
        if profile.get('air_quality_score', 0.5) < 0.4:
            issues.append('poor_air_quality')
        
        # Equity
        if profile.get('per_capita_green_space', 10) < 5:
            issues.append('equity_deficit')
        
        # Population
        if profile.get('population', 1000) > 10000:
            issues.append('high_population')
        
        return issues
    
    def _score_intervention(self,
                           int_type: str,
                           int_data: Dict,
                           issues: List[str],
                           profile: Dict) -> float:
        """Score how well intervention addresses issues"""
        score = 0.0
        
        # Match to identified issues
        best_for = int_data['best_for']
        for issue in issues:
            if issue in best_for or any(b in issue for b in best_for):
                score += 2.0
        
        # Match effect levels to severity
        if 'high_heat' in issues:
            effect_map = {'very_high': 3, 'high': 2, 'medium': 1, 'low': 0}
            score += effect_map.get(int_data['cooling_effect'], 0)
        
        if 'flood_prone' in issues or 'coastal_hazard' in issues:
            effect_map = {'very_high': 3, 'high': 2, 'medium': 1, 'low': 0}
            score += effect_map.get(int_data['stormwater_effect'], 0)
        
        if 'poor_air_quality' in issues:
            effect_map = {'very_high': 3, 'high': 2, 'medium': 1, 'low': 0}
            score += effect_map.get(int_data['air_quality_effect'], 0)
        
        # Space availability
        if profile.get('available_space', 1.0) < 0.3:
            if int_data['space_requirement'] in ['none', 'low']:
                score += 1.0
        
        return score
    
    def _generate_reasoning(self,
                           int_type: str,
                           int_data: Dict,
                           issues: List[str]) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        reasons.append(f"Recommended: {int_data['name']}")
        reasons.append(f"Primary issues: {', '.join(issues[:3])}")
        
        if 'high_heat' in issues:
            reasons.append(f"Cooling effect: {int_data['cooling_effect']}")
        
        if 'flood_prone' in issues:
            reasons.append(f"Stormwater management: {int_data['stormwater_effect']}")
        
        reasons.append(f"Estimated cost: ₱{int_data['cost_per_sqm']}/m²")
        reasons.append(f"Maintenance: {int_data['maintenance']}")
        
        return " | ".join(reasons)
    
    def _get_alternatives(self, scores: Dict[str, float], best: str) -> List[Dict]:
        """Get alternative interventions"""
        sorted_interventions = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        alternatives = []
        for int_type, score in sorted_interventions[1:3]:  # Top 2 alternatives
            int_data = self.INTERVENTION_LIBRARY[int_type]
            alternatives.append({
                'type': int_type,
                'name': int_data['name'],
                'score': score
            })
        
        return alternatives
    
    def create_recommendation_report(self,
                                    barangay_id: str,
                                    barangay_profile: Dict,
                                    recommendation: Dict,
                                    predicted_impacts: Dict) -> str:
        """Create formatted recommendation report"""
        lines = [
            "=" * 70,
            f"GREENING RECOMMENDATION REPORT",
            f"Barangay: {barangay_id}",
            "=" * 70,
            "",
            "CURRENT STATUS",
            "-" * 70,
            f"GI Score: {barangay_profile.get('gi_score', 0):.2f}",
            f"GI Level: {barangay_profile.get('gi_level', 'N/A')}",
            f"Priority Rank: {barangay_profile.get('priority_rank', 'N/A')}",
            "",
            "MAIN ISSUES",
            "-" * 70,
        ]
        
        for issue in recommendation['main_issues_addressed']:
            lines.append(f"• {issue.replace('_', ' ').title()}")
        
        lines.extend([
            "",
            "RECOMMENDED INTERVENTION",
            "-" * 70,
            f"Intervention: {recommendation['intervention_name']}",
            f"Description: {recommendation['description']}",
            f"Match Score: {recommendation['match_score']:.1f}/10",
            "",
            "ESTIMATED COSTS",
            "-" * 70,
            f"Cost per m²: ₱{recommendation['estimated_cost_per_sqm']:,.0f}",
            f"Maintenance: {recommendation['maintenance_level'].title()}",
            "",
            "PREDICTED ENVIRONMENTAL IMPACTS",
            "-" * 70,
        ])
        
        if predicted_impacts:
            for key, pred in predicted_impacts.items():
                label = key.replace('_', ' ').title()
                value = pred['value']
                lines.append(f"{label}: {value:.2f}")
        
        lines.extend([
            "",
            "ALTERNATIVE OPTIONS",
            "-" * 70,
        ])
        
        for alt in recommendation['alternatives']:
            lines.append(f"• {alt['name']} (score: {alt['score']:.1f})")
        
        lines.extend([
            "",
            "=" * 70,
        ])
        
        return "\n".join(lines)




