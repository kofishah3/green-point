import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import GreenSolutionCard from "@/components/ui/general/cards/greensolution-infocard"
import { Trees, Flower, Cookie, Info } from "lucide-react"

const SimulationResults = ({ results }) => {
  return (
    <div className="space-y-6">
      {/* Environmental Impact Projections */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Environmental Impact Projections</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
            <div className="text-sm text-blue-700 font-medium mb-1">Cooling Potential</div>
            <div className="text-3xl font-bold text-blue-900">{results.environmental.cooling_potential}°C</div>
            <div className="text-xs text-blue-600 mt-1">Temperature reduction</div>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
            <div className="text-sm text-green-700 font-medium mb-1">Canopy Gain</div>
            <div className="text-3xl font-bold text-green-900">{results.environmental.canopy_gain}%</div>
            <div className="text-xs text-green-600 mt-1">Coverage increase</div>
          </div>
          <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 border border-cyan-200 rounded-lg p-4">
            <div className="text-sm text-cyan-700 font-medium mb-1">Stormwater</div>
            <div className="text-3xl font-bold text-cyan-900">{results.environmental.stormwater_retention}</div>
            <div className="text-xs text-cyan-600 mt-1">mm retained</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
            <div className="text-sm text-purple-700 font-medium mb-1">PM2.5 Removal</div>
            <div className="text-3xl font-bold text-purple-900">{results.environmental.pm25_removal}</div>
            <div className="text-xs text-purple-600 mt-1">µg/m³ reduction</div>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-lg p-4">
            <div className="text-sm text-orange-700 font-medium mb-1">NO2 Removal</div>
            <div className="text-3xl font-bold text-orange-900">{results.environmental.no2_removal}</div>
            <div className="text-xs text-orange-600 mt-1">µg/m³ reduction</div>
          </div>
        </div>
      </div>

      {/* Greenery Index Evolution */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Greenery Index Evolution</h3>
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={results.giEvolution}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="year" label={{ value: 'Year', position: 'insideBottom', offset: -5 }} tick={{ fill: '#6b7280' }} />
              <YAxis label={{ value: 'Score', angle: -90, position: 'insideLeft' }} tick={{ fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend verticalAlign="top" height={36} />
              <Line type="monotone" dataKey="gi_score" stroke="#059669" strokeWidth={3} name="GI Score" dot={{ r: 4, fill: '#059669' }} activeDot={{ r: 6 }} />
              <Line type="monotone" dataKey="quantity_score" stroke="#3b82f6" strokeWidth={2} name="Quantity Score" dot={{ r: 3, fill: '#3b82f6' }} />
              <Line type="monotone" dataKey="environmental_quality_score" stroke="#f59e0b" strokeWidth={2} name="Environmental Quality" dot={{ r: 3, fill: '#f59e0b' }} />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-6 flex items-center justify-center gap-12 border-t border-gray-100 pt-4">
            <div className="text-center">
              <div className="text-sm text-gray-500 font-medium uppercase tracking-wide">Final GI Score</div>
              <div className="text-3xl font-bold text-emerald-600 mt-1">{results.finalGI.gi_score}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500 font-medium uppercase tracking-wide">Classification</div>
              <div className={`text-3xl font-bold mt-1 ${results.finalGI.gi_level === 'Excellent' ? 'text-emerald-600' :
                  results.finalGI.gi_level === 'High' ? 'text-green-600' :
                    results.finalGI.gi_level === 'Medium' ? 'text-yellow-600' : 'text-orange-600'
                }`}>
                {results.finalGI.gi_level}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation Summary & Interpretation */}
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-4">Recommendation & Analysis</h3>
        <div className="space-y-4">
          {/* Main Recommendation Card */}
          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 rounded-xl p-6 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-start gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${results.recommendation.priority === 'High' ? 'bg-red-100 text-red-700' :
                      results.recommendation.priority === 'Moderate' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                    }`}>
                    {results.recommendation.priority} Priority
                  </span>
                </div>
                <h4 className="text-2xl font-bold text-gray-900 mb-2">{results.recommendation.strategy}</h4>
                <p className="text-gray-700 leading-relaxed text-lg">{results.recommendation.rationale}</p>
              </div>
            </div>

            {/* Simulation Interpretation Integrated */}
            {results.interpretation && (
              <div className="mt-6 pt-6 border-t border-emerald-200/60">
                <h5 className="text-sm font-bold text-emerald-800 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <Info size={16} /> Simulation Interpretation
                </h5>
                <div className="text-neutral-700 text-sm leading-relaxed font-roboto bg-white/60 rounded-lg p-4 border border-emerald-100/50">
                  {results.interpretation.split('\n').map((line, i) => {
                    const parts = line.trim().split(/(\*\*.*?\*\*)/g);
                    return line.trim() ? (
                      <p key={i} className="mb-2 last:mb-0">
                        {parts.map((part, idx) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={idx} className="font-bold text-emerald-900">{part.slice(2, -2)}</strong>;
                          }
                          return part;
                        })}
                      </p>
                    ) : null;
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Suggested Interventions */}
          <div className="pt-4">
            <h4 className="text-lg font-semibold text-gray-800 mb-4">Suggested Intervention Models</h4>
            <div className="flex flex-col gap-4">
              <div className="w-full">
                <GreenSolutionCard
                  solutionTitle="Street Trees"
                  solutionDescription="Trees planted along urban streets and walkways."
                  detailedDescription="Street trees are trees planted along urban streets that provide environmental, social, and economic benefits, such as improving air quality, reducing stormwater runoff, providing shade, and enhancing the aesthetic appeal of a city. They are a key component of urban planning that can increase property values, improve walkability, and create a healthier environment for residents."
                  efficiencyLevel="Highly Efficient"
                  value={90}
                  icon={<Trees size={24} />}
                  efficiencyScore={90}
                  coolingPotential={2.5}
                  canopyGain={15}
                  stormwaterRetention={45}
                  pm25Removal={8.5}
                  no2Removal={5.2}
                  compact={false}
                />
              </div>

              <div className="w-full">
                <GreenSolutionCard
                  solutionTitle="Roof Gardens"
                  solutionDescription="Gardens grown on the rooftops of buildings."
                  detailedDescription="A roof garden is a garden on the roof of a building, also known as a green roof or landscaped rooftop. They can range from small container gardens to large landscapes with trees and walkways, and they provide benefits such as temperature control, improved air quality, stormwater management, and a space for recreation and growing food."
                  efficiencyLevel="Moderately Efficient"
                  value={40}
                  icon={<Flower size={24} />}
                  efficiencyScore={40}
                  coolingPotential={1.2}
                  canopyGain={5}
                  stormwaterRetention={25}
                  pm25Removal={3.5}
                  no2Removal={2.1}
                  compact={false}
                />
              </div>

              <div className="w-full">
                <GreenSolutionCard
                  solutionTitle="Mixed Blue-Green Corridors"
                  solutionDescription="Urban pathways that combine water-based and vegetative features."
                  detailedDescription="Mixed blue-green corridors are integrated urban planning solutions that link natural land (green) and water features (blue) to create interconnected passageways that provide multiple environmental, social, and economic benefits. This approach, also known as blue-green infrastructure (BGI), is a key strategy for making cities more resilient to climate change impacts like flooding and heatwaves."
                  efficiencyLevel="Not Efficient"
                  value={30}
                  icon={<Cookie size={24} />}
                  efficiencyScore={30}
                  coolingPotential={3.1}
                  canopyGain={12}
                  stormwaterRetention={80}
                  pm25Removal={9.5}
                  no2Removal={6.2}
                  compact={false}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationResults;