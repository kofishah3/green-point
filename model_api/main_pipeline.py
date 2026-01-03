"""
GreenPoint Framework - Main Pipeline
End-to-end execution of GI computation, prioritization, and recommendations
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data_loader import GreenPointDataLoader
from src.gi_indicators import GIIndicatorComputer
from src.gi_computation import GIComputer, get_default_domain_definitions, get_default_ahp_factors
from src.site_prioritization import SitePrioritizer, get_default_prioritization_criteria, get_default_prioritization_weights
from src.impact_prediction import ImpactPredictor
from src.intervention_matcher import InterventionMatcher
from src.visualization import (plot_gi_distribution, plot_choropleth_map, 
                              plot_priority_vs_gi, export_results_table)

import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def run_greenpoint_pipeline(data_dir: Path, output_dir: Path):
    """
    Run complete GreenPoint framework pipeline
    
    Pipeline Steps:
    1. Load data
    2. Compute GI indicators
    3. Compute GI scores
    4. Prioritize sites
    5. Match interventions
    6. Predict impacts
    7. Generate reports
    """
    print('\n' + '='*70)
    print('GREENPOINT FRAMEWORK - MANDAUE CITY GREENING ANALYSIS')
    print('='*70 + '\n')
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # =========================================================================
    # STEP 1: DATA LOADING
    # =========================================================================
    print('\n[STEP 1/7] Loading datasets...')
    print('-'*70)
    
    loader = GreenPointDataLoader(data_dir)
    datasets = loader.load_all()
    
    barangay_gdf = datasets['barangay_geography']
    if barangay_gdf is None:
        print('⚠ Error: Barangay geography data not found. Exiting.')
        return
    
    # =========================================================================
    # STEP 2: COMPUTE GI INDICATORS
    # =========================================================================
    print('\n[STEP 2/7] Computing GI indicators...')
    print('-'*70)
    
    indicator_computer = GIIndicatorComputer(barangay_gdf)
    
    # Domain 1: Quantity
    indicator_computer.compute_quantity_indicators(
        datasets['ndvi'],
        datasets['tree_cover']['data'] if datasets['tree_cover'] else None
    )
    
    # Domain 2: Accessibility & Equity
    indicator_computer.compute_accessibility_equity_indicators(
        datasets['population']
    )
    
    # Domain 3: Environmental Quality & Resilience
    hazard_gdfs = {
        'flood': datasets['flood_hazard'],
        'storm_surge': datasets['storm_surge'],
        'landslide': datasets['landslide_hazard']
    }
    indicator_computer.compute_environmental_quality_indicators(
        datasets['lst'],
        hazard_gdfs,
        datasets['air_quality']
    )
    
    # Domain 4: Connectivity & Biodiversity
    indicator_computer.compute_connectivity_indicators()
    
    # Normalize indicators
    indicators_normalized = indicator_computer.normalize_indicators()
    
    # Save indicators
    indicators_path = output_dir / 'gi_indicators.csv'
    indicators_normalized.to_csv(indicators_path)
    print(f'\n✓ Indicators saved to {indicators_path}')
    
    # =========================================================================
    # STEP 3: COMPUTE GI SCORES
    # =========================================================================
    print('\n[STEP 3/7] Computing GI scores...')
    print('-'*70)
    
    gi_computer = GIComputer(indicators_normalized)
    
    domain_defs = get_default_domain_definitions()
    ahp_factors = get_default_ahp_factors()
    
    gi_scores = gi_computer.compute_gi_scores(
        domain_definitions=domain_defs,
        ahp_factors=ahp_factors
    )
    
    # Merge with barangay data
    if isinstance(barangay_gdf, pd.DataFrame):
        result_gdf = barangay_gdf.copy()
        for col in gi_scores.columns:
            result_gdf[col] = gi_scores[col]
    else:
        result_gdf = gi_scores
    
    # Save GI scores
    gi_scores_path = output_dir / 'gi_scores.csv'
    gi_scores.to_csv(gi_scores_path)
    print(f'\n✓ GI scores saved to {gi_scores_path}')
    
    # Visualize
    plot_gi_distribution(gi_scores, output_dir / 'gi_distribution.png')
    
    # =========================================================================
    # STEP 4: SITE PRIORITIZATION
    # =========================================================================
    print('\n[STEP 4/7] Prioritizing intervention sites...')
    print('-'*70)
    
    prioritizer = SitePrioritizer(gi_scores, indicators_normalized)
    
    criteria = get_default_prioritization_criteria()
    weights = get_default_prioritization_weights()
    
    priorities = prioritizer.compute_priorities(criteria, weights)
    
    # Add cost-effectiveness
    priorities_with_cost = prioritizer.compute_cost_effectiveness()
    
    # Save priorities
    priorities_path = output_dir / 'intervention_priorities.csv'
    priorities_with_cost.to_csv(priorities_path)
    print(f'\n✓ Priorities saved to {priorities_path}')
    
    # Visualize
    plot_priority_vs_gi(priorities, output_dir / 'priority_vs_gi.png')
    
    # Get top 10 priorities
    top_10 = prioritizer.get_top_priorities(10)
    print('\n' + '='*70)
    print('TOP 10 PRIORITY BARANGAYS')
    print('='*70)
    print(top_10[['priority_rank', 'gi_score', 'gi_level', 'priority_score']].to_string())
    print('='*70)
    
    # =========================================================================
    # STEP 5: TRAIN IMPACT PREDICTION MODELS
    # =========================================================================
    print('\n[STEP 5/7] Training impact prediction models...')
    print('-'*70)
    
    predictor = ImpactPredictor()
    
    # Create synthetic training data
    features_df, targets_df = predictor.create_synthetic_training_data(n_samples=1000)
    
    # Train models
    model_scores = predictor.train_models(features_df, targets_df)
    
    # Save models
    models_dir = output_dir / 'models'
    predictor.save_models(models_dir)
    
    # =========================================================================
    # STEP 6: MATCH INTERVENTIONS
    # =========================================================================
    print('\n[STEP 6/7] Matching interventions to barangays...')
    print('-'*70)
    
    matcher = InterventionMatcher()
    
    # Generate recommendations for top priorities
    recommendations = []
    
    for idx in top_10.index[:5]:  # Top 5
        # Create barangay profile
        profile = {
            'gi_score': gi_scores.loc[idx, 'gi_score'] if idx in gi_scores.index else 0.3,
            'gi_level': gi_scores.loc[idx, 'gi_level'] if idx in gi_scores.index else 'Low',
            'priority_rank': priorities.loc[idx, 'priority_rank'] if idx in priorities.index else 99,
            'heat_anomaly': indicators_normalized.loc[idx, 'heat_anomaly'] if 'heat_anomaly' in indicators_normalized.columns and idx in indicators_normalized.index else 0,
            'flood_exposure': indicators_normalized.loc[idx, 'flood_exposure'] if 'flood_exposure' in indicators_normalized.columns and idx in indicators_normalized.index else 0,
            'canopy_cover_pct': indicators_normalized.loc[idx, 'canopy_cover_pct'] if 'canopy_cover_pct' in indicators_normalized.columns and idx in indicators_normalized.index else 0,
            'population': indicators_normalized.loc[idx, 'population'] if 'population' in indicators_normalized.columns and idx in indicators_normalized.index else 5000,
        }
        
        # Match intervention
        recommendation = matcher.match_intervention(profile, budget_constraint=5000000)
        
        # Predict impact
        intervention_scale = {
            'intervention_area': 5000,
            'tree_count': 200,
            'green_roof_area': 1000
        }
        
        barangay_features = {
            'baseline_ndvi': 0.3,
            'baseline_lst': 32,
            'baseline_canopy': 15,
            'impervious_surface_pct': 70,
            'population_density': 8000,
            'building_density': 0.6,
            'flood_depth': 1.0,
            'storm_surge_height': 2.0
        }
        
        predicted_impacts = predictor.predict_impact(
            barangay_features,
            recommendation['intervention_type'],
            intervention_scale
        )
        
        # Create report
        barangay_id = f"Barangay_{idx}"
        report = matcher.create_recommendation_report(
            barangay_id,
            profile,
            recommendation,
            predicted_impacts
        )
        
        recommendations.append({
            'barangay_id': barangay_id,
            'recommendation': recommendation,
            'impacts': predicted_impacts,
            'report': report
        })
        
        print(f'\n{report}')
    
    # =========================================================================
    # STEP 7: EXPORT FINAL RESULTS
    # =========================================================================
    print('\n[STEP 7/7] Exporting final results...')
    print('-'*70)
    
    # Export comprehensive results
    final_results = pd.concat([
        gi_scores,
        priorities_with_cost
    ], axis=1)
    
    export_results_table(final_results, output_dir / 'greenpoint_final_results.csv')
    
    # Save recommendations
    recommendations_df = pd.DataFrame([
        {
            'barangay_id': r['barangay_id'],
            'intervention_type': r['recommendation']['intervention_type'],
            'intervention_name': r['recommendation']['intervention_name'],
            'estimated_cost_per_sqm': r['recommendation']['estimated_cost_per_sqm'],
            'cooling_potential': r['impacts']['cooling_potential']['value'],
            'stormwater_retention': r['impacts']['stormwater_retention']['value'],
            'pm25_removal': r['impacts']['pm25_removal']['value']
        }
        for r in recommendations
    ])
    
    export_results_table(recommendations_df, output_dir / 'intervention_recommendations.csv')
    
    # Save full reports
    reports_dir = output_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    for r in recommendations:
        report_path = reports_dir / f"{r['barangay_id']}_recommendation.txt"
        with open(report_path, 'w') as f:
            f.write(r['report'])
    
    print(f'\n✓ Reports saved to {reports_dir}')
    
    # =========================================================================
    # PIPELINE COMPLETE
    # =========================================================================
    print('\n' + '='*70)
    print('✓ GREENPOINT PIPELINE COMPLETED SUCCESSFULLY')
    print('='*70)
    print(f'\nAll outputs saved to: {output_dir}')
    print('\nKey outputs:')
    print(f'  - GI Indicators: {indicators_path}')
    print(f'  - GI Scores: {gi_scores_path}')
    print(f'  - Priorities: {priorities_path}')
    print(f'  - Final Results: {output_dir / "greenpoint_final_results.csv"}')
    print(f'  - Recommendations: {output_dir / "intervention_recommendations.csv"}')
    print(f'  - Detailed Reports: {reports_dir}/')
    print(f'  - Models: {models_dir}/')
    print('='*70 + '\n')


if __name__ == '__main__':
    # Set paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / 'Dataset'
    OUTPUT_DIR = BASE_DIR / 'outputs'
    
    # Run pipeline
    run_greenpoint_pipeline(DATA_DIR, OUTPUT_DIR)




