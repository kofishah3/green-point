import { useState } from 'react';
import { ArrowLeft, Download, GitCompare, X, Play } from 'lucide-react';
import SimulationInputs from './InputsPanel';
import SimulationResults from './ResultsPanel';
import { useBarangay } from '@/context/BarangayContext';
import SimulationLoading from './Loading';

const SimulationModal = ( { isOpen, setIsOpen }: { isOpen: boolean, setIsOpen: (isOpen: boolean) => void } ) => {
  const [stage, setStage] = useState('setup');
  const { simulationBarangay } = useBarangay();
  const [loadingProgress, setLoadingProgress] = useState(0);

  const baselineData = {
    ndvi: simulationBarangay?.ndvi ?? 0.42,
    lst: simulationBarangay?.lst ?? 32.5,
    floodExposure: simulationBarangay?.floodExposure ?? 'Medium',
    greeneryIndex: simulationBarangay?.greeneryIndex ?? 0.58,
    canopyCover: simulationBarangay?.treeCanopy ?? 28,
    currentIntervention: simulationBarangay?.currentIntervention ?? 'Urban Canopy Enhancement'
  };

  const [inputs, setInputs] = useState({
    temperature_increase_rate: 0.03,
    flooding_severity: 'medium',
    rainfall_change_rate: 5,
    canopy_target_percent: 15,
    ndvi_target: 0.15,
    intervention_type: 'mixed strategy',
    total_budget_cap: 5000000,
    cost_per_sqm: 850,
    maintenance_cost_rate: 8,
    time_horizon: 5
  });

  const [results, setResults] = useState(null);

  const closeModal = () => {
    setIsOpen(false);
    setStage('setup');
  };

  const handleInputChange = <K extends keyof typeof inputs>(key: K, value: typeof inputs[K]) => {
    setInputs(prev => ({ ...prev, [key]: value }));
  };

  const resetInputs = () => {
    setInputs({
      temperature_increase_rate: 0.03,
      flooding_severity: 'medium',
      rainfall_change_rate: 5,
      canopy_target_percent: 15,
      ndvi_target: 0.15,
      intervention_type: 'mixed strategy',
      total_budget_cap: 5000000,
      cost_per_sqm: 850,
      maintenance_cost_rate: 8,
      time_horizon: 5
    });
  };

  const runSimulation = () => {
    // Start loading state
    setStage('loading');
    setLoadingProgress(0);

    // Simulate progressive loading
    const progressInterval = setInterval(() => {
      setLoadingProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        // Non-linear progress for more realistic feel
        const increment = prev < 30 ? 5 : prev < 70 ? 3 : 2;
        return Math.min(prev + increment, 100);
      });
    }, 200);

    // Calculate results after loading animation
    setTimeout(() => {
      const timeSteps = inputs.time_horizon;
      const budgetEfficiency = Math.min(inputs.total_budget_cap / (inputs.canopy_target_percent * inputs.cost_per_sqm * 100), 1.2); // 1.2 means budget is plenty
      const effectiveCanopyGain = inputs.canopy_target_percent * Math.min(budgetEfficiency, 1) * 0.9; // 90% success rate assumption
      const ndviGain = inputs.ndvi_target * Math.min(budgetEfficiency, 1) * 0.95;
      
      // Realistic Physics-based Approximations
      // Cooling: Logarithmic returns. First few trees do more than the 100th tree.
      const cooling = (Math.log(effectiveCanopyGain + 1) * 0.5) + (ndviGain * 1.8);
      
      // Stormwater: Linear with canopy, but step-change with specific interventions
      let stormwaterBase = effectiveCanopyGain * 8; // Trees intercept water
      if (inputs.intervention_type.includes('rain') || inputs.intervention_type.includes('garden')) stormwaterBase += 80; // Rain gardens are huge sponges
      if (inputs.intervention_type.includes('roof')) stormwaterBase += 40; // Green roofs retain water
      const stormwater = stormwaterBase * (1 + (inputs.rainfall_change_rate / 100)); // Adjust for climate change rainfall

      // Pollution removal: Directly proportional to biomass (Canopy + NDVI)
      const pm25 = effectiveCanopyGain * 0.9 + ndviGain * 12;
      const no2 = effectiveCanopyGain * 0.5 + ndviGain * 7;

      const giEvolution = [];
      for (let i = 0; i <= timeSteps; i++) {
        const progress = i / timeSteps;
        // Non-linear adoption curve (S-curve)
        const adoptionRate = progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        const quantityScore = Math.min(baselineData.ndvi + (ndviGain * adoptionRate), 1.0);
        // Environmental quality degrades with temp increase, improves with greening
        const envQualityScore = Math.max(0, Math.min(1, 
          0.62 + (0.25 * adoptionRate) - (inputs.temperature_increase_rate * i * 0.8)
        ));
        
        const giScore = (quantityScore * 0.6 + envQualityScore * 0.4);
        
        giEvolution.push({
          year: i,
          gi_score: parseFloat(giScore.toFixed(3)),
          quantity_score: parseFloat(quantityScore.toFixed(3)),
          environmental_quality_score: parseFloat(envQualityScore.toFixed(3))
        });
      }

      const finalGI = giEvolution[giEvolution.length - 1].gi_score;
      let giLevel = 'Low';
      if (finalGI >= 0.75) giLevel = 'Excellent';
      else if (finalGI >= 0.60) giLevel = 'High';
      else if (finalGI >= 0.40) giLevel = 'Medium';

      let recommendation = 'Mixed Strategy with Urban Canopy Focus';
      let priority = 'Moderate';
      let rationale = 'Balanced approach addressing both immediate cooling needs and long-term resilience.';

      // Detailed Logic for Recommendation
      if (inputs.flooding_severity === 'high' || inputs.rainfall_change_rate > 10) {
        recommendation = 'Blue-Green Infrastructure Network';
        priority = 'High';
        rationale = 'Critical flood risks necessitate a network of rain gardens and bioswales. Traditional canopy alone is insufficient for the projected rainfall volume.';
      } else if (cooling > 1.5 && inputs.temperature_increase_rate > 0.04) {
        recommendation = 'Aggressive Urban Forestry';
        priority = 'Critical';
        rationale = 'With rapid temperature rise projected, maximizing canopy cover is the only viable strategy to maintain livability standards.';
      } else if (budgetEfficiency < 0.7) {
        recommendation = 'Targeted Pocket Parks (Phased)';
        priority = 'Moderate';
        rationale = `Current budget covers only ${(budgetEfficiency * 100).toFixed(0)}% of the ambitious target. A phased approach focusing on high-impact pocket parks is recommended to maximize ROI.`;
      } else if (baselineData.greeneryIndex > 0.6 && effectiveCanopyGain < 5) {
        recommendation = 'Maintenance & Preservation Strategy';
        priority = 'Low';
        rationale = 'The area already has healthy greenery. Focus should shift to maintenance and protecting existing assets rather than aggressive new planting.';
      }

      // Generate Interpretation
      const interpretation = `
        **Simulation Analysis:**
        
        Under the selected scenario, achieving a **${effectiveCanopyGain.toFixed(1)}% increase in canopy cover** is projected to reduce local temperatures by **${cooling.toFixed(2)}°C**. 
        
        ${budgetEfficiency < 1.0 
          ? `⚠️ **Budget Warning:** The allocated budget of ₱${(inputs.total_budget_cap/1000000).toFixed(1)}M is insufficient for the full target. The simulation assumes a reduced implementation scale of ${(budgetEfficiency*100).toFixed(0)}%.` 
          : `✅ **Feasibility:** The budget is sufficient to fully realize the intervention targets.`}
        
        **Impact on Resilience:**
        The intervention specifically addresses the **${inputs.flooding_severity}** flood risk by retaining **${stormwater.toFixed(0)}mm** of stormwater annually. The Greenery Index (GI) is projected to improve from **${giEvolution[0].gi_score}** to **${finalGI.toFixed(3)}** over ${timeSteps} years.
      `;

      setResults({
        environmental: {
          cooling_potential: parseFloat(cooling.toFixed(2)),
          canopy_gain: parseFloat(effectiveCanopyGain.toFixed(1)),
          stormwater_retention: parseFloat(stormwater.toFixed(1)),
          pm25_removal: parseFloat(pm25.toFixed(2)),
          no2_removal: parseFloat(no2.toFixed(2))
        },
        giEvolution,
        finalGI: {
          gi_score: parseFloat(finalGI.toFixed(3)),
          gi_level: giLevel
        },
        recommendation: {
          strategy: recommendation,
          priority,
          rationale
        },
        interpretation // Added interpretation field
      });

      clearInterval(progressInterval);
      setStage('results');
    }, 4000); // 4 second loading duration
  };

  const exportReport = () => {
    const report = {
      timestamp: new Date().toISOString(),
      inputs,
      baseline: baselineData,
      results
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={() => setIsOpen(false)}
    >
      <div
        className="bg-white rounded-xl shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white p-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Environmental Scenario Simulation</h2>
            <p className="text-emerald-100 mt-1">
              {stage === 'setup' ? 'Configure simulation parameters' : 'Projected outcomes and recommendations'}
            </p>
          </div>
          <button
            onClick={closeModal}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-lg p-2 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {stage === 'setup' ? (
            <SimulationInputs
              inputs={inputs}
              onInputChange={handleInputChange}
              onReset={resetInputs}
              baselineData={baselineData}
            />
          ) : (
            stage === 'loading' ? (
              <SimulationLoading progress={loadingProgress} />
            ) : (
              <SimulationResults results={results} />
            )
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 bg-gray-50 px-6 py-4 flex items-center justify-between">
          {stage === 'setup' ? (
            <>
              <div className="text-sm text-gray-600">
                Configure parameters and click Run to see projections
              </div>
              <button
                onClick={runSimulation}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors"
              >
                <Play className="w-5 h-5" />
                Run Simulation
              </button>
            </>
          ) : stage === 'results' ? 
          (
            <>
              <button
                onClick={() => setStage('setup')}
                className="border border-gray-300 hover:bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Inputs
              </button>
              <div className="flex gap-3">
                <button
                  onClick={exportReport}
                  className="border border-gray-300 bg-primary-green/15 hover:bg-primary-green/10 text-gray-700 px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export Report
                </button>
          
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default SimulationModal;