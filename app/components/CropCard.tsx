import { Crop } from "../data/api";
import { RiskBadge } from "./RiskBadge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface CropCardProps {
  crop: Crop;
  onClick?: () => void;
}

export function CropCard({ crop, onClick }: CropCardProps) {
  const TrendIcon =
    crop.trend === "up" ? TrendingUp : crop.trend === "down" ? TrendingDown : Minus;

  const trendColor =
    crop.trend === "up"
      ? "text-green-600"
      : crop.trend === "down"
      ? "text-red-600"
      : "text-gray-600";

  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-lg text-gray-900">{crop.name}</h3>
          <p className="text-sm text-gray-600">{crop.name_hindi}</p>
        </div>
        <RiskBadge level={crop.risk_level} size="sm" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-600 mb-1">Current Price</p>
          <p className="text-xl font-bold text-gray-900">
            ₹{crop.current_price}
            <span className="text-sm text-gray-600 font-normal ml-1">/quintal</span>
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-600 mb-1">Price Change</p>
          <div className="flex items-center gap-1">
            <TrendIcon size={20} className={trendColor} />
            <span className={`text-xl font-bold ${trendColor}`}>
              {crop.price_change > 0 ? "+" : ""}
              {crop.price_change}%
            </span>
          </div>
        </div>
      </div>

      <div className="border-t border-gray-200 pt-3 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Shock Probability</span>
          <span className="text-sm font-semibold text-gray-900">{crop.predicted_shock}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              crop.risk_level === "high"
                ? "bg-red-500"
                : crop.risk_level === "medium"
                ? "bg-yellow-500"
                : "bg-green-500"
            }`}
            style={{ width: `${crop.predicted_shock}%` }}
          />
        </div>
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>Season: {crop.season}</span>
        </div>
      </div>
    </div>
  );
}
