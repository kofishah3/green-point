interface GreeneryIndexData {
  name: string;
  greenery_index: number;
  ndvi: number;
  lst: number;
  tree_canopy: number;
  flood_exposure: string;
  current_intervention: string;
}

interface APIBarangayData {
  brgy_name: string;
  gi_score: number;
  ndvi_mean: number;
  mean_lst: number;
  canopy_cover_pct: number;
  flood_exposure?: string;
  [key: string]: any;
}

interface Recommendation {
  barangay_name: string;
  intervention_type: string;
  intervention_name: string;
  priority_rank: number;
  efficiency_score?: number;
  estimated_cost_per_sqm: number;
  cooling_potential: number;
  stormwater_retention: number;
  pm25_removal: number;
  canopy_gain?: number;
  no2_removal?: number;
  explanation?: string;
}

export function mergeGI(geoJSON: GeoJSON.FeatureCollection, giJSON: GreeneryIndexData[]) {
  return {
    ...geoJSON,
    features: geoJSON.features.map(feature => {
      const name = feature.properties?.name;
      const match = giJSON.find(d => d.name === name);
      return {
        ...feature,
        properties: {
          ...feature.properties, 
          greenery_index: match ? match.greenery_index : null,
          ndvi: match ? match.ndvi : null,
          lst: match ? match.lst : null,
          tree_canopy: match ? match.tree_canopy : null,
          flood_exposure: match ? match.flood_exposure : null,
          current_intervention: match ? match.current_intervention : null,
        }
      }
    })
  }
}

// Clean barangay name for display (remove (Pob.) suffix)
export function cleanBarangayName(name: string): string {
  return name.replace(/\s*\(Pob\.\)\s*$/i, '').trim();
}

export function mergeAPIData(geoJSON: GeoJSON.FeatureCollection, apiData: APIBarangayData[], recommendations: Recommendation[] = []) {
  return {
    ...geoJSON,
    features: geoJSON.features.map(feature => {
      const name = feature.properties?.name;
      // Try to match by normalizing names
      const normalizeName = (n: string) => n.toLowerCase().replace(/[^a-z0-9]/g, "").trim();
      const normalizedName = normalizeName(name || "");
      const match = apiData.find(d => normalizeName(d.brgy_name) === normalizedName);
      
      const topRec = recommendations
        .filter(r => normalizeName(r.barangay_name) === normalizedName)
        .sort((a, b) => (b.efficiency_score || 0) - (a.efficiency_score || 0))[0];

      return {
        ...feature,
        properties: {
          ...feature.properties,
          name: cleanBarangayName(feature.properties?.name || ""),
          greenery_index: match ? match.gi_score : null,
          ndvi: match ? match.ndvi_mean : null,
          lst: match ? match.mean_lst : null,
          tree_canopy: match ? match.canopy_cover_pct : null,
          flood_exposure: match?.flood_exposure || null,
          current_intervention: topRec?.intervention_name || null,
          current_intervention_details: topRec ? {
            name: topRec.intervention_name,
            type: topRec.intervention_type,
            efficiency_score: topRec.efficiency_score || 0,
            cost: topRec.estimated_cost_per_sqm,
            impact: topRec.cooling_potential,
            description: topRec.explanation || "",
            short_description: topRec.explanation ? topRec.explanation.substring(0, 100) + "..." : "",
            cooling_potential: topRec.cooling_potential,
            canopy_gain: topRec.canopy_gain,
            stormwater_retention: topRec.stormwater_retention,
            pm25_removal: topRec.pm25_removal,
            no2_removal: topRec.no2_removal
          } : undefined
        }
      }
    })
  }
}