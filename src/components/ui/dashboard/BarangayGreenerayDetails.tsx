import { getGreeneryClassColor, getTemperatureColor } from "@/lib/chloroplet-colors";

interface BarangayGreeneryProps {
  icon: React.ElementType;
  valueName: string;
  value: number;
  LST?: boolean;
}

export default function BarangayGreenery({ icon: Icon, valueName, value, LST = false}: BarangayGreeneryProps) {
  // Apply color scaling based on metric type to match dashboard gauges
  const getScaledValue = () => {
    if (valueName === "Normalized Difference Vegetation Index") {
      // NDVI: scale to 0-0.75 range for color calculation
      return Math.min(value / 0.75, 1);
    } else if (valueName === "Tree Canopy Cover") {
      // TCC: scale to 0-40 range for color calculation
      return Math.min(value / 40, 1);
    }
    // Greenery Index and others use value as-is
    return value;
  };

  const scaledValue = getScaledValue();
  const classColor = valueName === "Land Surface Temperature" ? getTemperatureColor(value) : getGreeneryClassColor(scaledValue);
  const [textColor, bgColor] = classColor.split(' ');

  // Format value to 2 decimal places max (1 for LST)
  const formatValue = () => {
    if (value === null || value === undefined) return "N/A";
    if (LST) return `${value.toFixed(1)}°C`;
    return value.toFixed(2);
  };

  return (
    <div className="h-full flex justify-between items-center gap-2 mb-2  p-3 rounded-md">
      <div className="flex items-center gap-2">
        <div className={`w-fit h-fit p-2 rounded-md flex items-center justify-center ${bgColor}`}>
          <Icon size={20} className={textColor} />
        </div>
        <h1 className="text-neutral-black text-md font-medium">{valueName}</h1>
      </div>
      <h1 className={`font-bold font-poppins text-xl ${textColor}`}>{formatValue()}</h1>
    </div>  
  )
}