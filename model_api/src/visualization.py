"""
Visualization utilities for GreenPoint framework
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import folium
from pathlib import Path
from typing import Optional, List, Dict


def plot_gi_distribution(gi_scores: pd.DataFrame, output_path: Optional[Path] = None):
    """Plot GI score distribution"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram
    axes[0].hist(gi_scores['gi_score'], bins=20, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('GI Score')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Distribution of GI Scores')
    axes[0].axvline(gi_scores['gi_score'].mean(), color='red', linestyle='--', 
                    label=f'Mean: {gi_scores["gi_score"].mean():.2f}')
    axes[0].legend()
    
    # Level counts
    if 'gi_level' in gi_scores.columns:
        level_counts = gi_scores['gi_level'].value_counts().sort_index()
        axes[1].bar(range(len(level_counts)), level_counts.values)
        axes[1].set_xticks(range(len(level_counts)))
        axes[1].set_xticklabels(level_counts.index, rotation=45)
        axes[1].set_ylabel('Count')
        axes[1].set_title('GI Level Distribution')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved plot to {output_path}')
    
    plt.show()


def plot_choropleth_map(gdf: gpd.GeoDataFrame, 
                       value_col: str,
                       title: str,
                       cmap: str = 'YlGn',
                       output_path: Optional[Path] = None):
    """Plot choropleth map"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    gdf.plot(column=value_col, ax=ax, legend=True, cmap=cmap,
            edgecolor='black', linewidth=0.5, alpha=0.8)
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved map to {output_path}')
    
    plt.show()


def create_interactive_map(gdf: gpd.GeoDataFrame,
                          value_col: str,
                          name_col: str,
                          title: str,
                          output_path: Optional[Path] = None) -> folium.Map:
    """Create interactive Folium map"""
    # Get center
    centroid = gdf.geometry.centroid.unary_union.centroid
    
    # Create map
    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Add choropleth
    folium.Choropleth(
        geo_data=gdf,
        name=title,
        data=gdf,
        columns=[gdf.index, value_col],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name=title
    ).add_to(m)
    
    # Add tooltips
    for idx, row in gdf.iterrows():
        if name_col in row:
            folium.CircleMarker(
                location=[row.geometry.centroid.y, row.geometry.centroid.x],
                radius=3,
                popup=f"{row[name_col]}<br>{value_col}: {row[value_col]:.2f}",
                color='blue',
                fill=True
            ).add_to(m)
    
    if output_path:
        m.save(str(output_path))
        print(f'✓ Saved interactive map to {output_path}')
    
    return m


def plot_domain_scores(gi_scores: pd.DataFrame,
                      output_path: Optional[Path] = None):
    """Plot radar chart of domain scores"""
    domain_cols = [c for c in gi_scores.columns if c.endswith('_score') and c != 'gi_score']
    
    if not domain_cols:
        print('⚠ No domain scores found')
        return
    
    # Calculate mean scores
    means = gi_scores[domain_cols].mean()
    
    # Radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=means.values,
        theta=[c.replace('_score', '').replace('_', ' ').title() for c in domain_cols],
        fill='toself',
        name='Average Domain Scores'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1])
        ),
        showlegend=True,
        title='Average GI Domain Scores'
    )
    
    if output_path:
        fig.write_html(str(output_path))
        print(f'✓ Saved radar chart to {output_path}')
    
    fig.show()


def plot_priority_vs_gi(priorities: pd.DataFrame,
                       output_path: Optional[Path] = None):
    """Plot priority score vs GI score"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    scatter = ax.scatter(
        priorities['gi_score'],
        priorities['priority_score'],
        c=priorities['priority_rank'],
        cmap='RdYlGn_r',
        s=100,
        alpha=0.6,
        edgecolor='black'
    )
    
    ax.set_xlabel('GI Score (Greenness)')
    ax.set_ylabel('Priority Score (Intervention Urgency)')
    ax.set_title('Intervention Priority vs. Current Greenness')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Priority Rank')
    
    # Add quadrant lines
    ax.axhline(priorities['priority_score'].median(), color='gray', 
              linestyle='--', alpha=0.5)
    ax.axvline(priorities['gi_score'].median(), color='gray',
              linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'✓ Saved plot to {output_path}')
    
    plt.show()


def create_recommendation_dashboard(barangay_data: Dict,
                                  recommendations: Dict,
                                  impacts: Dict,
                                  output_path: Optional[Path] = None):
    """Create interactive dashboard for recommendations"""
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('GI Scores', 'Priority Ranking', 
                       'Predicted Impacts', 'Cost Analysis'),
        specs=[[{'type': 'bar'}, {'type': 'scatter'}],
               [{'type': 'bar'}, {'type': 'scatter'}]]
    )
    
    # Would implement full dashboard here
    # Placeholder for now
    
    if output_path:
        fig.write_html(str(output_path))
        print(f'✓ Saved dashboard to {output_path}')
    
    return fig


def export_results_table(results: pd.DataFrame,
                        output_path: Path,
                        format: str = 'csv'):
    """Export results to file"""
    output_path = Path(output_path)
    
    if format == 'csv':
        results.to_csv(output_path, index=False)
    elif format == 'excel':
        results.to_excel(output_path, index=False)
    elif format == 'geojson' and isinstance(results, gpd.GeoDataFrame):
        results.to_file(output_path, driver='GeoJSON')
    
    print(f'✓ Exported results to {output_path}')




