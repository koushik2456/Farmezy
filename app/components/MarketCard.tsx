import { Market } from "../data/api";
import { RiskBadge } from "./RiskBadge";
import { MapPin, TrendingDown, TrendingUp } from "lucide-react";

interface MarketCardProps {
  market: Market;
}

export function MarketCard({ market }: MarketCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start gap-3">
          <div className="bg-blue-100 text-blue-600 p-2 rounded-lg">
            <MapPin size={20} />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{market.name}</h3>
            <p className="text-sm text-gray-600">{market.state}</p>
          </div>
        </div>
        <RiskBadge level={market.risk_level} size="sm" />
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">High Risk Crops</p>
          <p className="text-2xl font-bold text-gray-900">
            {market.high_risk_crops}
            <span className="text-sm text-gray-600 font-normal">
              /{market.total_crops}
            </span>
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">Avg Price Change</p>
          <div className="flex items-center gap-1">
            {market.average_price_change >= 0 ? (
              <TrendingUp size={18} className="text-green-600" />
            ) : (
              <TrendingDown size={18} className="text-red-600" />
            )}
            <span
              className={`text-2xl font-bold ${
                market.average_price_change >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {market.average_price_change > 0 ? "+" : ""}
              {market.average_price_change}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
