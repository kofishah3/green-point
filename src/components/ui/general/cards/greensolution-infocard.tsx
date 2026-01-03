import { ReactNode, useState } from "react";
import HalfCircleBar from "../../dashboard/halfcirclebar";
import { ArrowRight, Info } from "lucide-react";

interface GreenSolutionCardProps {
  solutionTitle: string;
  solutionDescription: string;
  shortDescription?: string;
  detailedDescription: string; 
  efficiencyLevel: string;
  efficiencyScore?: number;
  icon: ReactNode;
  value: number;
  equityIndex?: number;
  cost?: number;
  impact?: number;
  // API prediction fields
  coolingPotential?: number;
  stormwaterRetention?: number;
  pm25Removal?: number;
  canopyGain?: number;
  no2Removal?: number;
  compact?: boolean;
}

export default function GreenSolutionCard({
  solutionTitle,
  solutionDescription,
  shortDescription,
  detailedDescription,
  efficiencyLevel,
  efficiencyScore,
  icon,
  value,
  equityIndex,
  cost,
  impact,
  coolingPotential,
  stormwaterRetention,
  pm25Removal,
  canopyGain,
  no2Removal,
  compact = false,
}: GreenSolutionCardProps) {
  
  const getGradientStyle = (score: number) => {
    if (score >= 80) return {
      bg: "bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200",
      border: "border-emerald-200",
      text: "text-emerald-800",
      badge: "bg-emerald-500 text-white shadow-emerald-200",
      iconBg: "bg-emerald-100 text-emerald-600"
    };
    if (score >= 60) return {
      bg: "bg-gradient-to-br from-lime-50 to-lime-100 border-lime-200",
      border: "border-lime-200",
      text: "text-lime-800",
      badge: "bg-lime-500 text-white shadow-lime-200",
      iconBg: "bg-lime-100 text-lime-600"
    };
    if (score >= 40) return {
      bg: "bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200",
      border: "border-yellow-200",
      text: "text-yellow-800",
      badge: "bg-yellow-500 text-white shadow-yellow-200",
      iconBg: "bg-yellow-100 text-yellow-600"
    };
    return {
      bg: "bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200",
      border: "border-orange-200",
      text: "text-orange-800",
      badge: "bg-orange-500 text-white shadow-orange-200",
      iconBg: "bg-orange-100 text-orange-600"
    };
  };

  const style = efficiencyScore !== undefined 
    ? getGradientStyle(efficiencyScore)
    : {
        bg: "bg-gray-50 border-gray-200",
        border: "border-gray-200",
        text: "text-gray-700",
        badge: "bg-gray-500 text-white",
        iconBg: "bg-gray-200 text-gray-600"
      };

  const [isHover, setIsHover] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div
        onMouseEnter={() => setIsHover(true)}
        onMouseLeave={() => setIsHover(false)}
        onClick={() => setIsModalOpen(true)}
        className={`flex flex-col justify-between rounded-xl 
        transition-all duration-300 border ${style.border} ${style.bg}
        hover:-translate-y-1 hover:shadow-lg hover:shadow-neutral-200/50 cursor-pointer group relative overflow-hidden
        ${compact ? "p-3" : "my-2"}`}
      >
        <div className={`flex flex-row items-center justify-between w-full ${compact ? "gap-3" : "py-4 px-6"}`}>
          <div className="flex items-center space-x-4 flex-1 min-w-0">
            <div
              className={`rounded-full flex items-center justify-center transition-colors duration-300 ${style.iconBg}
              ${compact ? "p-2 w-10 h-10" : "p-4 w-16 h-16"}`}
            >
              {icon}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className={`font-poppins font-semibold text-neutral-black whitespace-nowrap overflow-hidden text-ellipsis
                  ${compact ? "text-sm" : "text-lg"}`}>
                  {solutionTitle}
                </h3>
                {!compact && (
                   <span
                   className={`text-[10px] font-bold font-poppins px-2 py-0.5 rounded-full uppercase tracking-wider shadow-sm ${style.badge}`}
               >
                 {efficiencyScore ? `${efficiencyScore.toFixed(0)}% Eff.` : efficiencyLevel}
               </span>
                )}
              </div>
              
              {/* Show API prediction metrics */}
              {(coolingPotential !== undefined || stormwaterRetention !== undefined || pm25Removal !== undefined || canopyGain !== undefined || no2Removal !== undefined) ? (
                <div className={`flex flex-wrap items-center gap-2 ${compact ? "text-xs" : "text-sm"}`}>
                  {coolingPotential !== undefined && coolingPotential > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-black/60 font-roboto text-xs">Cooling:</span>
                      <span className="font-semibold text-blue-600 text-xs">
                        {coolingPotential.toFixed(2)}°C
                      </span>
                    </div>
                  )}
                  {canopyGain !== undefined && canopyGain > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-black/60 font-roboto text-xs">Canopy:</span>
                      <span className="font-semibold text-green-600 text-xs">
                        +{canopyGain.toFixed(1)}%
                      </span>
                    </div>
                  )}
                  {stormwaterRetention !== undefined && stormwaterRetention > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-black/60 font-roboto text-xs">Stormwater:</span>
                      <span className="font-semibold text-cyan-600 text-xs">
                        {Math.round(stormwaterRetention)}mm
                      </span>
                    </div>
                  )}
                  {pm25Removal !== undefined && pm25Removal > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-black/60 font-roboto text-xs">PM2.5:</span>
                      <span className="font-semibold text-purple-600 text-xs">
                        {pm25Removal.toFixed(2)}
                      </span>
                    </div>
                  )}
                  {no2Removal !== undefined && no2Removal > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-neutral-black/60 font-roboto text-xs">NO2:</span>
                      <span className="font-semibold text-amber-600 text-xs">
                        {no2Removal.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              ) : null}
              
              {!compact && shortDescription && (
                <p className="text-neutral-black/60 text-xs font-roboto mb-2 italic line-clamp-2">
                  {shortDescription}
                </p>
              )}

              {compact && (
                 <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md ${style.badge}`}>
                      {efficiencyScore ? `${efficiencyScore.toFixed(0)}%` : efficiencyLevel}
                    </span>
                 </div>
              )}
            </div>
          </div>

          {!compact && (
            <div className="mb-2 pl-4 border-l border-neutral-200/50">
              <HalfCircleBar sizePx={80} min={0} max={100} value={value} trailColor="#ffffff80" pathColor={efficiencyScore && efficiencyScore > 70 ? "#16a34a" : "#ca8a04"} />
            </div>
          )}
          
          {compact && (
             <div className="text-neutral-400 group-hover:text-neutral-600 transition-colors">
                <ArrowRight size={16} />
             </div>
          )}
        </div>

        {!compact && (
          <div
            className={`w-full flex items-center justify-center px-4 rounded-b-xl transition-all duration-300 overflow-hidden bg-black/5
            ${isHover ? "max-h-10 py-2 opacity-100" : "max-h-0 py-0 opacity-0"}`}
          >
            <p className="font-roboto text-xs font-medium text-neutral-700 flex items-center gap-1">
              See Details <ArrowRight size={12} />
            </p>
          </div>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white animate-in fade-in duration-200">
          <div 
            className="w-full h-full relative overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={`absolute top-0 left-0 w-full h-48 ${style.bg} opacity-50`}></div>
            
            <button
              onClick={(e) => {
                e.stopPropagation(); 
                setIsModalOpen(false);
              }}
              className="absolute top-6 right-6 w-10 h-10 flex items-center justify-center rounded-full bg-white/80 hover:bg-white text-neutral-500 hover:text-neutral-800 transition-all shadow-md z-10"
            >
              ✕
            </button>
            
            <div className="relative pt-10 px-6 md:px-12 lg:px-24 pb-10 overflow-y-auto flex-1 w-full max-w-5xl mx-auto">
              <div className="flex items-start space-x-6 mb-8 pt-8">
                <div className={`p-5 rounded-3xl bg-white shadow-xl ${style.iconBg} ring-4 ring-white shrink-0`}>
                  {icon}
                </div>
                <div className="flex-1 pt-2">
                  <h2 className="text-3xl md:text-4xl font-poppins font-bold text-neutral-black leading-tight">{solutionTitle}</h2>
                  <p className="text-neutral-500 font-medium text-lg mt-2">{solutionDescription}</p>
                  <span className={`inline-flex items-center gap-1 mt-4 text-sm font-bold font-poppins px-4 py-1.5 rounded-full shadow-sm ${style.badge}`}>
                     {efficiencyScore ? `Efficiency Score: ${efficiencyScore.toFixed(0)}%` : efficiencyLevel}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-10">
                {coolingPotential !== undefined && coolingPotential > 0 && (
                  <div className="bg-white border border-neutral-100 rounded-2xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Cooling Potential</p>
                    <p className="text-3xl font-bold font-poppins text-blue-600">
                      {coolingPotential.toFixed(2)}°C
                    </p>
                    <p className="text-sm text-neutral-500 mt-2">Temperature reduction</p>
                  </div>
                )}
                {canopyGain !== undefined && canopyGain > 0 && (
                  <div className="bg-white border border-neutral-100 rounded-2xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Canopy Gain</p>
                    <p className="text-3xl font-bold font-poppins text-green-600">
                      {canopyGain.toFixed(1)}%
                    </p>
                    <p className="text-sm text-neutral-500 mt-2">Coverage increase</p>
                  </div>
                )}
                {stormwaterRetention !== undefined && stormwaterRetention > 0 && (
                  <div className="bg-white border border-neutral-100 rounded-2xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">Stormwater</p>
                    <p className="text-3xl font-bold font-poppins text-cyan-600">
                      {Math.round(stormwaterRetention)}
                    </p>
                    <p className="text-sm text-neutral-500 mt-2">mm retained</p>
                  </div>
                )}
                {pm25Removal !== undefined && pm25Removal > 0 && (
                  <div className="bg-white border border-neutral-100 rounded-2xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">PM2.5 Removal</p>
                    <p className="text-3xl font-bold font-poppins text-purple-600">
                      {pm25Removal.toFixed(2)}
                    </p>
                    <p className="text-sm text-neutral-500 mt-2">µg/m³ reduction</p>
                  </div>
                )}
                {no2Removal !== undefined && no2Removal > 0 && (
                  <div className="bg-white border border-neutral-100 rounded-2xl p-6 text-center shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">NO2 Removal</p>
                    <p className="text-3xl font-bold font-poppins text-amber-600">
                      {no2Removal.toFixed(2)}
                    </p>
                    <p className="text-sm text-neutral-500 mt-2">µg/m³ reduction</p>
                  </div>
                )}
              </div>
              
              <div className="mb-10 bg-neutral-50 rounded-2xl p-8 border border-neutral-100 max-h-none overflow-visible">
                 <h4 className="flex items-center gap-2 text-sm font-bold text-neutral-500 uppercase tracking-wider mb-4">
                    <Info size={18} /> Why this intervention?
                 </h4>
                 <div className="text-neutral-700 font-roboto text-base md:text-lg leading-relaxed space-y-4">
                  {detailedDescription.split('\n\n').map((paragraph, idx) => {
                    // Check if paragraph contains bold markdown (**text**)
                    const parts = paragraph.split(/(\*\*.*?\*\*)/g);
                    
                    return (
                      <p key={idx} className="whitespace-pre-wrap">
                        {parts.map((part, partIdx) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            // Bold text
                            return (
                              <strong key={partIdx} className="font-semibold text-neutral-900">
                                {part.slice(2, -2)}
                              </strong>
                            );
                          }
                          return <span key={partIdx}>{part}</span>;
                        })}
                      </p>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
