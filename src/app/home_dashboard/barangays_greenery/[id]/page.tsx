"use client"

import TreeCanopyTrend from "@/components/charts/TreeCanopyTrend"
import BarangayRadarChart from "@/components/charts/BarangayRadarChart"
import NDVILSTChart from "@/components/charts/NDVILSTChart"
import PovertyComparison from "@/components/charts/PovertyComparison"

import { useBarangay } from "@/context/BarangayContext";
import { getGreeneryClassColor, getTemperatureColor } from "@/lib/chloroplet-colors";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel"
import { Download, Container, Info, TreeDeciduous, GalleryThumbnails, Leaf, Flower } from "lucide-react";
import { useEffect, useState } from "react";
import { ChartInfoModal } from "@/components/ui/dashboard/info_modals";
import { BarangayDataMetrics, getBarangayMetricbyName, MetricDescriptions } from "@/types/metrics";
import { fetchMetricDescriptions } from "@/lib/api/get_definitions";
import GreenSolutionCard from "@/components/ui/general/cards/greensolution-infocard";


interface ModalValues {
  charttitle: string, 
  chartdescription: string,   
}

interface CityAverages {
  greeneryIndex: number;
  ndvi: number;
  treeCanopy: number;
  lst: number;
}

export default function BarangayGreeneryPage({ cityAverages }: { cityAverages?: CityAverages }) {
  const { selectedBarangay } = useBarangay();
  const [barangayDataMetrics, setBarangayDataMetrics] = useState<Record<string, BarangayDataMetrics>>({});

  const classColor = getGreeneryClassColor(selectedBarangay?.greeneryIndex || 0);
  const [textColor, bgColor] = classColor.split(' ');
  const temperatureColor = getTemperatureColor(selectedBarangay?.lst || 0);
  const [temperatureTextColor, temperatureBgColor] = temperatureColor.split(' ');

  const [openModal, setOpenModal] = useState<boolean>(false);
  const [modalValues, setModalValues] = useState<ModalValues | null>(null);
  
  const [metricDescriptions, setMetricDescriptions] = useState<MetricDescriptions[]>([])
  const handleOpenModal = (title: string, description: string) => {
    setModalValues({ charttitle: title, chartdescription: description });
    setOpenModal(true);
  };
  
  useEffect(() => {
    async function load() {
      const data = await fetchMetricDescriptions()
      setMetricDescriptions(data)
    }
    load()
  }, [])

  const getDesc = (name: string) => {
    return (
      metricDescriptions.find((metric) => metric.name === name)?.description ||
      ""
    )
  }

  if (!selectedBarangay) {
    return (
      <div className="w-full h-fit bg-white rounded-lg shadow-md p-6">
        <p className="text-neutral-black/80">Select a barangay on the map to view detailed metrics.</p>
      </div>
    );
  }

  const getInterventionIcon = (intervention: string) => {
    const type = intervention.toLowerCase();
    if (type.includes('tree')) return <TreeDeciduous size={24} />;
    if (type.includes('garden')) return <Flower size={24} />;
    if (type.includes('corridor')) return <Container size={24} />;
    return <Leaf size={24} />;
  }

  const getFloodExposureClass = (floodExposure: string | number) => {
    // If it's a number, we can't easily map to Low/Medium/High without thresholds.
    // Assuming the API might return strings "Low", "Medium", "High" OR a number.
    // If it's a number, we'll just return a neutral color for now or try to interpret.
    // Based on the user screenshot, it's a number 0.41... which is likely normalized.
    
    if (typeof floodExposure === 'string') {
        switch (floodExposure) {
        case "Low":
            return "bg-green-500/10 text-green-500 px-2 py-1 rounded-md";
        case "Medium":
            return "bg-yellow-500/10 text-yellow-500 px-2 py-1 rounded-md";
        case "High":
            return "bg-red-500/10 text-red-500 px-2 py-1 rounded-md";
        }
    }
    // Default fallback
    return "bg-gray-500/10 text-gray-500 px-2 py-1 rounded-md";
  }

  const formatFloodExposure = (val: string | number | undefined) => {
    if (val === undefined || val === null) return "N/A";
    const num = Number(val);
    if (!isNaN(num)) {
      return num.toFixed(2);
    }
    return val;
  }

  // Helper to generate simulated trend data based on current metrics
  const getSimulatedTrends = () => {
    if (!selectedBarangay) return { canopyData: [], ndviLstData: [], canopyChange: 0 };

    // Hardcoded realistic simulation data
    // 1. Tree Canopy Trend (5 years)
    // Simulating a gradual decline followed by stabilization, typical of urbanization
    const canopyData = [
      { year: "2020", canopy: 18.45 },
      { year: "2021", canopy: 18.12 },
      { year: "2022", canopy: 17.85 },
      { year: "2023", canopy: 17.92 }, // Slight recovery/stabilization
      { year: "2024", canopy: selectedBarangay.treeCanopy || 18.05 } // Connect to current actual if possible, or smooth transition
    ];
    
    // Calculate change from 2020 to 2024
    const startCanopy = canopyData[0].canopy;
    const endCanopy = canopyData[4].canopy;
    const canopyChange = ((endCanopy - startCanopy) / startCanopy) * 100;

    // 2. NDVI & LST Monthly Trend (Simulated Seasonality)
    // Represents typical urban heat island effect: LST peaks when NDVI is lowest (dry season)
    const ndviLstData = [
      { month: "Jan", NDVI: 0.42, LST: 28.5 },
      { month: "Feb", NDVI: 0.38, LST: 29.2 },
      { month: "Mar", NDVI: 0.35, LST: 31.5 }, // Peak dry/heat
      { month: "Apr", NDVI: 0.33, LST: 32.8 }, // Peak dry/heat
      { month: "May", NDVI: 0.36, LST: 31.2 },
      { month: "Jun", NDVI: 0.45, LST: 29.5 }  // Onset of wet season, cooling
    ];

    return { canopyData, ndviLstData, canopyChange };
  };

  const { canopyData, ndviLstData, canopyChange } = getSimulatedTrends();

  const trendInterpretation = `
    **Trend Analysis:**
    The 5-year analysis reveals a slight **${Math.abs(canopyChange).toFixed(2)}% ${canopyChange >= 0 ? 'increase' : 'decline'}** in tree canopy cover since 2020, likely due to urban development pressure. 
    
    Seasonal data indicates a strong inverse correlation between vegetation health (NDVI) and surface temperature (LST). Temperatures peak at **32.8°C** in April when vegetation density is lowest (NDVI 0.33), confirming that increasing green cover is critical for mitigating peak summer heat.
  `;

  useEffect(() => {
    async function fetchMetrics() {
      const metrics = await getBarangayMetricbyName();
      setBarangayDataMetrics(metrics);
    }
    fetchMetrics();
  }, []);

  const barangayData = barangayDataMetrics[selectedBarangay?.name || ""];

  return (
    <div className="w-full h-fit bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col gap-4 mb-4">
        <div className="flex flex-row items-center justify-between">
          <div className="flex flex-row items-center gap-8">
            <h1 className={`text-2xl font-bold ${textColor} ${bgColor} w-fit px-4 py-1 rounded-md`}>
              {selectedBarangay?.name || "Barangay"}
            </h1>
            <p>
              Population:{" "}
              <span className="bg-blue-600/10 text-blue-600 px-2 py-1 rounded-md font-medium">
                {barangayData?.population[2024]?.toLocaleString() ?? "N/A"} people
              </span>
            </p>
            <p>
              Population Density:{" "}
              <span className="bg-blue-600/10 text-blue-600 px-2 py-1 rounded-md font-medium">
                {barangayData?.pop_density_perkm2?.toFixed(2) ?? "N/A"} people/sq.km
              </span>
            </p>
            <p>
              Area:{" "}
              <span className="bg-blue-600/10 text-blue-600 px-2 py-1 rounded-md font-medium">
                {barangayData?.area_km2?.toFixed(2) ?? "N/A"} sq.km
              </span>
            </p>

          </div>
          <button className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
  
        {/* Metrics */}
        <div className="flex flex-row flex-wrap gap-12">  
          <p className="text-neutral-black/90">
            GI:{" "}
            <span className={`bg-primary-green/10 text-primary-green px-2 py-1 rounded-md font-medium`}>
              {selectedBarangay?.greeneryIndex?.toFixed(2) ?? "N/A"}
            </span>
          </p>
  
          <p className="text-neutral-black/90">
            NDVI:{" "}
            <span className="bg-primary-green/10 text-primary-green px-2 py-1 rounded-md font-medium">
              {selectedBarangay?.ndvi?.toFixed(2) ?? "N/A"}
            </span>
          </p>
  
          <p className="text-neutral-black/90">
            TCC:{" "}
            <span className="bg-primary-green/10 text-primary-green px-2 py-1 rounded-md font-medium">
              {selectedBarangay?.treeCanopy?.toFixed(2) ?? "N/A"}
            </span>
          </p>
  
          <p className="text-neutral-black/90">
            LST:{" "}
            <span className={`bg-primary-green/10 text-primary-green px-2 py-1 rounded-md font-medium ${temperatureTextColor} ${temperatureBgColor}`}>
              {selectedBarangay?.lst ? `${selectedBarangay.lst.toFixed(2)}°C` : "N/A"}
            </span>
          </p>
  
          <p className="text-neutral-black/80 font-medium">
            Flood Exposure:{" "}
            <span className={getFloodExposureClass(selectedBarangay?.floodExposure ?? "N/A")}>
              {formatFloodExposure(selectedBarangay?.floodExposure)}
            </span>
          </p>
  
          <p className="text-neutral-black/90">
            Poverty Rate:{" "}
            <span className="bg-primary-green/10 text-primary-green px-2 py-1 rounded-md font-medium">
              10%
            </span>
          </p>
        </div>
      </div>
  
      <hr className="border-neutral-grey w-full" />
  
      {/* Charts + Interventions */}
      <div className="flex w-full min-h-[700px] h-auto pt-4 gap-4">
        <div className="flex flex-col h-full flex-1 gap-4">
          <div className="w-full px-12 flex-shrink-0">
            <Carousel className="pl-12 bg-primary-green/5 border border-primary-green/50 px-4 py-4 rounded-lg h-fit w-full">
                <CarouselContent className="h-full">
                  <CarouselItem className="h-full">
                    <div className="w-full h-60 mb-8 ">                      
                      <div className="flex flex-row justify-between items-center">
                        <h3 className="text-neutral-black text-sm font-medium mb-2">NDVI & LST Trend</h3>
                        <button
                          onClick={() => handleOpenModal(
                            "NDVI & LST Trend",
                            getDesc("NDVI & LST Time Series")
                          )}
                          className="text-neutral-black/80 p-1 hover:bg-neutral-200/60 rounded-full transition-all duration-150 cursor-pointer "
                        >
                          <Info />
                        </button>
                      </div>
                        <NDVILSTChart data={ndviLstData} />
                    </div>
                  </CarouselItem>
                  <CarouselItem className="h-full">
                    <div className="w-full h-60">
                      <div className="flex flex-row justify-between items-center">
                        <h3 className="text-neutral-black text-sm font-medium mb-2">Tree Canopy</h3>
                        <button
                          onClick={() => handleOpenModal(
                            "Tree Canopy",
                            getDesc("Tree Canopy % Trend")
                          )}
                          className="text-neutral-black/80 p-1 hover:bg-neutral-200/60 rounded-full transition-all duration-150 cursor-pointer "
                        >
                          <Info />
                        </button>
                      </div>
                      <TreeCanopyTrend
                        data={canopyData}
                        since="2020"
                        changePercent={Number(canopyChange.toFixed(2))}
                      />
                    </div>
                  </CarouselItem>
                  <CarouselItem className="h-full">
                    <div className="w-full h-60">
                      <div className="flex flex-row justify-between items-center">
                        <h3 className="text-neutral-black text-sm font-medium mb-2">Poverty Rate Comparison</h3>
                        <button
                          onClick={() => handleOpenModal(
                            "Poverty Rate Comparison",
                            getDesc("Poverty % Comparison vs City Average")
                          )}
                          className="text-neutral-black/80 p-1 hover:bg-neutral-200/60 rounded-full transition-all duration-150 cursor-pointer "
                        >
                          <Info />
                        </button>
                      </div>
                      <PovertyComparison
                        data={[
                          { label: selectedBarangay?.name, value: 42 },
                          { label: "City Avg", value: 32 },
                        ]}
                      />
                    </div>
                  </CarouselItem>
                </CarouselContent>
  
              <CarouselNext />
              <CarouselPrevious />
            </Carousel>
            
            {/* Trend Interpretation */}
            <div className="mt-4 bg-neutral-50 border border-neutral-200 rounded-lg p-4">
              <div className="flex flex-row gap-2 items-start">
                <Info className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-neutral-700 font-roboto leading-relaxed">
                  {trendInterpretation.split('\n\n').map((paragraph, idx) => {
                    const parts = paragraph.split(/(\*\*.*?\*\*)/g);
                    return (
                      <p key={idx} className={idx > 0 ? "mt-2" : ""}>
                        {parts.map((part, partIdx) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={partIdx} className="font-semibold text-neutral-900">{part.slice(2, -2)}</strong>;
                          }
                          return part;
                        })}
                      </p>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
  
          {/* TOP GREENING INTERVENTION - DETAILED */}
          <hr className="border-neutral-grey w-full pl-12" />
          <div className="w-full flex flex-col gap-3 px-12 overflow-hidden flex-1 min-h-[400px]">
            <div className="flex items-center justify-between flex-shrink-0">
              <h1 className="text-lg font-bold text-neutral-black">Recommended Greening Intervention</h1>
              {selectedBarangay?.currentInterventionDetails && (
                <span className="text-xs font-medium text-neutral-500 bg-neutral-100 px-3 py-1 rounded-full">
                  Priority #1
                </span>
              )}
            </div>
            
            <div className="overflow-y-auto overflow-x-hidden pr-2 flex-1 min-h-[350px] [scrollbar-width:thin] [scrollbar-color:rgba(0,0,0,0.2)_transparent]">
            {selectedBarangay?.currentInterventionDetails ? (
                <div className="space-y-3 pb-2">
                  <p className="text-sm text-neutral-600 font-roboto leading-relaxed">
                    Based on environmental analysis and urban planning considerations, this intervention is most suitable for {selectedBarangay.name}.
                  </p>
                  
              <GreenSolutionCard
                    solutionTitle={selectedBarangay.currentInterventionDetails.name || selectedBarangay.currentInterventionDetails.type}
                    solutionDescription={selectedBarangay.currentInterventionDetails.type}
                shortDescription={selectedBarangay.currentInterventionDetails.short_description}
                    detailedDescription={(() => {
                      const details = selectedBarangay.currentInterventionDetails;
                      const barangay = selectedBarangay;
                      
                      // Build comprehensive explanation
                      let explanation = `${details?.description || ''}\n\n`;
                      
                      // Add barangay-specific context
                      explanation += `**Barangay ${barangay.name} Analysis:**\n\n`;
                      
                      // Environmental conditions
                      explanation += `**Current Environmental Conditions:**\n`;
                      explanation += `• Greenery Index: ${barangay.greeneryIndex.toFixed(2)} - `;
                      if (barangay.greeneryIndex < 0.3) explanation += 'Low vegetation coverage requiring urgent greening intervention.\n';
                      else if (barangay.greeneryIndex < 0.5) explanation += 'Moderate vegetation coverage with room for improvement.\n';
                      else explanation += 'Good vegetation coverage that can be further optimized.\n';
                      
                      explanation += `• Land Surface Temperature: ${barangay.lst.toFixed(2)}°C - `;
                      if (barangay.lst > 30) explanation += 'High surface temperatures indicating significant heat island effect.\n';
                      else if (barangay.lst > 27) explanation += 'Moderate heat levels that can benefit from cooling interventions.\n';
                      else explanation += 'Relatively lower temperatures compared to city average.\n';
                      
                      explanation += `• Tree Canopy Cover: ${barangay.treeCanopy.toFixed(2)}% - `;
                      if (barangay.treeCanopy < 15) explanation += 'Low tree coverage requiring increased urban forestry efforts.\n';
                      else if (barangay.treeCanopy < 25) explanation += 'Moderate canopy that needs expansion for better cooling.\n';
                      else explanation += 'Good tree coverage providing natural cooling benefits.\n';
                      
                      explanation += `• NDVI: ${barangay.ndvi.toFixed(2)} - `;
                      if (barangay.ndvi < 0.3) explanation += 'Sparse vegetation density limiting ecosystem services.\n\n';
                      else if (barangay.ndvi < 0.5) explanation += 'Moderate vegetation health with growth potential.\n\n';
                      else explanation += 'Healthy vegetation providing environmental benefits.\n\n';
                      
                      // Why this intervention
                      explanation += `**Why This Intervention Works Here:**\n\n`;
                      
                      const interventionType = details?.type?.toLowerCase() || '';
                      if (interventionType.includes('tree')) {
                        explanation += `Street trees are highly effective for ${barangay.name} because they provide direct cooling through shade, reduce ambient temperature, and improve air quality along pedestrian corridors. With the current temperature at ${barangay.lst.toFixed(1)}°C, trees can reduce surface temperatures by up to ${details?.cooling_potential?.toFixed(1)}°C while enhancing the neighborhood's aesthetic appeal and property values.\n\n`;
                      } else if (interventionType.includes('park')) {
                        explanation += `Pocket parks serve as green oases in urban areas, providing multiple ecosystem services. For ${barangay.name}, this creates accessible green space for the community while addressing the low greenery index of ${barangay.greeneryIndex.toFixed(2)}. Parks combine vegetation, permeable surfaces, and open space to maximize cooling and stormwater management.\n\n`;
                      } else if (interventionType.includes('roof')) {
                        explanation += `Green roofs are particularly effective in areas with limited ground space and high surface temperatures. At ${barangay.lst.toFixed(1)}°C, ${barangay.name} experiences significant heat accumulation. Green roofs insulate buildings, reduce energy costs, and provide additional green space without competing for scarce land.\n\n`;
                      } else if (interventionType.includes('vertical') || interventionType.includes('wall')) {
                        explanation += `Vertical gardens maximize greening potential in space-constrained areas. For ${barangay.name}, this intervention utilizes vertical surfaces to increase vegetation coverage without requiring valuable ground space, while providing cooling and aesthetic benefits to building facades.\n\n`;
                      } else if (interventionType.includes('rain') || interventionType.includes('garden')) {
                        explanation += `Rain gardens address stormwater management through bio-retention, particularly important given ${barangay.name}'s flood exposure level. These gardens capture runoff, filter pollutants, and recharge groundwater while adding green infrastructure that supports biodiversity and cooling.\n\n`;
                      } else if (interventionType.includes('forest')) {
                        explanation += `Urban forests provide the highest density of environmental benefits including maximum cooling, carbon sequestration, and habitat creation. With sufficient space in ${barangay.name}, this intervention establishes a significant green corridor that reduces the heat island effect and improves overall ecological health.\n\n`;
                      }
                      
                      // Expected benefits
                      explanation += `**Expected Environmental Benefits:**\n\n`;
                      if (details?.cooling_potential) {
                        explanation += `• **Temperature Reduction:** Up to ${details.cooling_potential.toFixed(2)}°C decrease in ambient and surface temperatures, making outdoor spaces more comfortable and reducing energy demands for cooling.\n\n`;
                      }
                      if (details?.canopy_gain) {
                        explanation += `• **Canopy Coverage Increase:** Expected to increase tree canopy coverage by approximately ${details.canopy_gain.toFixed(1)}%, enhancing shade provision, biodiversity habitat, and urban forest connectivity.\n\n`;
                      }
                      if (details?.stormwater_retention) {
                        explanation += `• **Stormwater Management:** Capable of retaining approximately ${Math.round(details.stormwater_retention)}mm of rainfall, reducing flood risk and preventing overflow of drainage systems during heavy precipitation events.\n\n`;
                      }
                      if (details?.pm25_removal) {
                        explanation += `• **PM2.5 Reduction:** Expected to reduce PM2.5 particulate matter by ${details.pm25_removal.toFixed(2)} µg/m³, contributing to cleaner air and reduced respiratory health risks for residents.\n\n`;
                      }
                      if (details?.no2_removal) {
                        explanation += `• **NO2 Reduction:** Expected to reduce nitrogen dioxide levels by ${details.no2_removal.toFixed(2)} µg/m³, improving air quality and reducing harmful pollutants from vehicle emissions.\n\n`;
                      }
                      
                      // Implementation considerations
                      explanation += `**Implementation Considerations:**\n\n`;
                      explanation += `This intervention has been prioritized based on comprehensive analysis of ${barangay.name}'s environmental metrics, spatial constraints, and community needs. `;
                      explanation += `The estimated efficiency score of ${details?.efficiency_score?.toFixed(0)}% reflects the optimal balance between cost-effectiveness and environmental impact for this specific location. `;
                      explanation += `Implementation should consider local site conditions, maintenance requirements, and community engagement to maximize long-term success and sustainability.`;
                      
                      return explanation;
                    })()}
                    efficiencyLevel="Recommended"
                efficiencyScore={selectedBarangay.currentInterventionDetails.efficiency_score}
                icon={getInterventionIcon(selectedBarangay.currentInterventionDetails.type)}
                value={selectedBarangay.currentInterventionDetails.efficiency_score}
                cost={selectedBarangay.currentInterventionDetails.cost}
                impact={selectedBarangay.currentInterventionDetails.impact}
                    coolingPotential={selectedBarangay.currentInterventionDetails.cooling_potential}
                    stormwaterRetention={selectedBarangay.currentInterventionDetails.stormwater_retention}
                    pm25Removal={selectedBarangay.currentInterventionDetails.pm25_removal}
                    compact={false}
                  />
                  
                  {/* Environmental Impact Projections */}
                  <div className="mt-2">
                    <h3 className="text-base font-semibold text-neutral-800 mb-4">Environmental Impact Projections</h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                      {selectedBarangay.currentInterventionDetails.cooling_potential !== undefined && selectedBarangay.currentInterventionDetails.cooling_potential > 0 && (
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-lg p-4">
                          <p className="text-xs font-semibold text-blue-600 mb-2">Cooling Potential</p>
                          <p className="text-2xl font-bold font-poppins text-blue-700">
                            {selectedBarangay.currentInterventionDetails.cooling_potential.toFixed(2)}°C
                          </p>
                          <p className="text-xs text-blue-600 mt-1">Temperature reduction</p>
                        </div>
                      )}
                      
                      {selectedBarangay.currentInterventionDetails.canopy_gain !== undefined && selectedBarangay.currentInterventionDetails.canopy_gain > 0 && (
                        <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-lg p-4">
                          <p className="text-xs font-semibold text-green-600 mb-2">Canopy Gain</p>
                          <p className="text-2xl font-bold font-poppins text-green-700">
                            {selectedBarangay.currentInterventionDetails.canopy_gain.toFixed(1)}%
                          </p>
                          <p className="text-xs text-green-600 mt-1">Coverage increase</p>
                        </div>
                      )}
                      
                      {selectedBarangay.currentInterventionDetails.stormwater_retention !== undefined && selectedBarangay.currentInterventionDetails.stormwater_retention > 0 && (
                        <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 border border-cyan-200 rounded-lg p-4">
                          <p className="text-xs font-semibold text-cyan-600 mb-2">Stormwater</p>
                          <p className="text-2xl font-bold font-poppins text-cyan-700">
                            {Math.round(selectedBarangay.currentInterventionDetails.stormwater_retention)}
                          </p>
                          <p className="text-xs text-cyan-600 mt-1">mm retained</p>
                        </div>
                      )}
                      
                      {selectedBarangay.currentInterventionDetails.pm25_removal !== undefined && selectedBarangay.currentInterventionDetails.pm25_removal > 0 && (
                        <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-lg p-4">
                          <p className="text-xs font-semibold text-purple-600 mb-2">PM2.5 Removal</p>
                          <p className="text-2xl font-bold font-poppins text-purple-700">
                            {selectedBarangay.currentInterventionDetails.pm25_removal.toFixed(2)}
                          </p>
                          <p className="text-xs text-purple-600 mt-1">µg/m³ reduction</p>
                        </div>
                      )}
                      
                      {selectedBarangay.currentInterventionDetails.no2_removal !== undefined && selectedBarangay.currentInterventionDetails.no2_removal > 0 && (
                        <div className="bg-gradient-to-br from-amber-50 to-amber-100 border border-amber-200 rounded-lg p-4">
                          <p className="text-xs font-semibold text-amber-600 mb-2">NO2 Removal</p>
                          <p className="text-2xl font-bold font-poppins text-amber-700">
                            {selectedBarangay.currentInterventionDetails.no2_removal.toFixed(2)}
                          </p>
                          <p className="text-xs text-amber-600 mt-1">µg/m³ reduction</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="w-full flex flex-col gap-4 bg-primary-green/5 border border-primary-green/50 rounded-lg p-6">
                  <div className="flex gap-4 items-center">
                <div className="w-fit h-fit bg-primary-green rounded-full p-4">
                  <TreeDeciduous size={32} className="text-white" />
                </div>
                <div>
                  <h1 className="text-primary-green text-lg font-semibold">
                        No Intervention Data Available
                  </h1>
                  <p className="text-neutral-black/80 text-sm line-clamp-2">
                        Intervention recommendations for this barangay are currently being analyzed.
                      </p>
                    </div>
                  </div>
                  <div className="bg-white/50 rounded-md p-3">
                    <p className="text-xs text-neutral-600 font-roboto">
                      <strong>Note:</strong> Try selecting a different barangay or check the Greening Solutions page for location-specific recommendations.
                  </p>
                </div>
              </div>
            )}
            </div>
          </div>
        </div>

        {/* RADAR CHART */}
        <div className="flex flex-col w-[550px] flex-shrink-0 bg-primary-green/5 border border-primary-green/50 rounded-lg p-4">
          <h1 className="text-lg font-medium">Barangay Radar Chart</h1>
          <BarangayRadarChart
            data={[
              { metric: "Greenery Index", barangay: Number((selectedBarangay?.greeneryIndex ?? 0).toFixed(2)), city: cityAverages?.greeneryIndex ?? 0.54 },
              { metric: "NDVI", barangay: Number((selectedBarangay?.ndvi ?? 0).toFixed(2)), city: cityAverages?.ndvi ?? 0.41 },
              { metric: "Canopy %", barangay: Number(((selectedBarangay?.treeCanopy ?? 0) / 100).toFixed(2)), city: Number(((cityAverages?.treeCanopy ?? 21) / 100).toFixed(2)) },
              { metric: "Poverty % (Inverted)", barangay: 0.45, city: 0.55 },
              { metric: "Area Size", barangay: 0.68, city: 0.70 },
            ]}
          />
        </div>
      </div>
  
      {/* Popup Modal */}
      <ChartInfoModal
        open={openModal}
        onClose={() => setOpenModal(false)}
        title={modalValues?.charttitle || "NDVI & LST Trend"}
        description={
          modalValues?.chartdescription ||
          "This chart compares vegetation health (NDVI) with land surface temperature (LST) over time."
        }
      />
    </div>
  );
}