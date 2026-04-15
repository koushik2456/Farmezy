import { useState, useEffect } from "react";
import { PriceChart } from "../components/PriceChart";
import { RiskBadge } from "../components/RiskBadge";
import { getCrops, getCropHistory, Crop, PriceData } from "../data/api";
import {
  TrendingDown,
  TrendingUp,
  CloudRain,
  Package,
  Truck,
  Info,
} from "lucide-react";

export default function DetailedAnalysis() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCropId, setSelectedCropId] = useState<number | null>(null);
  const [priceData, setPriceData] = useState<PriceData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCrops()
      .then((data) => {
        setCrops(data);
        if (data.length > 0) {
          setSelectedCropId(data[0].id);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedCropId) {
      getCropHistory(selectedCropId)
        .then((data) => setPriceData(data.price_history))
        .catch(console.error);
    }
  }, [selectedCropId]);

  if (loading) return <div className="p-8 text-center text-gray-500">Loading analysis data...</div>;

  const selectedCrop = crops.find((c) => c.id === selectedCropId) || crops[0];
  if (!selectedCrop) return <div className="p-8 text-center text-gray-500">No crop data available</div>;

  const currentPrice = selectedCrop.current_price;
  const predictedPrice = priceData.length > 0 ? (priceData[priceData.length - 1].predicted || currentPrice) : currentPrice;
  const priceDifference = predictedPrice - currentPrice;
  const percentChange = currentPrice > 0 ? ((priceDifference / currentPrice) * 100).toFixed(2) : "0.00";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Detailed Price Analysis</h1>
        <p className="text-gray-600">
          In-depth price shock prediction and historical trend analysis
        </p>
      </div>

      {/* Crop Selector */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Crop for Analysis
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {crops.map((crop) => (
            <button
              key={crop.id}
              onClick={() => setSelectedCropId(crop.id)}
              className={`p-3 rounded-lg border-2 transition-all ${
                selectedCropId === crop.id
                  ? "border-green-600 bg-green-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <p className="font-semibold text-sm text-gray-900">{crop.name}</p>
              <p className="text-xs text-gray-600">{crop.name_hindi}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Crop Overview */}
      <div className="bg-gradient-to-br from-green-50 to-blue-50 border border-gray-200 rounded-lg p-8 mb-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-1">
              {selectedCrop.name} ({selectedCrop.name_hindi})
            </h2>
            <p className="text-gray-600">Season: {selectedCrop.season}</p>
          </div>
          <RiskBadge level={selectedCrop.risk_level} size="lg" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Current Price</p>
            <p className="text-2xl font-bold text-gray-900">₹{currentPrice}</p>
            <p className="text-xs text-gray-600">/quintal</p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Predicted (14 days)</p>
            <p className="text-2xl font-bold text-gray-900">₹{predictedPrice}</p>
            <p
              className={`text-sm font-medium ${
                priceDifference >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {priceDifference >= 0 ? "+" : ""}₹{priceDifference.toFixed(0)} ({percentChange}%)
            </p>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Shock Probability</p>
            <p className="text-2xl font-bold text-gray-900">{selectedCrop.predicted_shock}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className={`h-2 rounded-full ${
                  selectedCrop.risk_level === "high"
                    ? "bg-red-500"
                    : selectedCrop.risk_level === "medium"
                    ? "bg-yellow-500"
                    : "bg-green-500"
                }`}
                style={{ width: `${selectedCrop.predicted_shock}%` }}
              />
            </div>
          </div>
          <div className="bg-white rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Price Trend</p>
            <div className="flex items-center gap-2">
              {selectedCrop.trend === "up" ? (
                <TrendingUp size={24} className="text-green-600" />
              ) : selectedCrop.trend === "down" ? (
                <TrendingDown size={24} className="text-red-600" />
              ) : (
                <TrendingUp size={24} className="text-gray-600" />
              )}
              <p className="text-2xl font-bold text-gray-900">
                {selectedCrop.price_change > 0 ? "+" : ""}
                {selectedCrop.price_change}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Price Chart */}
      <div className="mb-8">
        <PriceChart data={priceData} cropName={selectedCrop.name} />
      </div>

      {/* Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-blue-100 text-blue-600 p-3 rounded-lg">
              <Truck size={24} />
            </div>
            <h3 className="font-semibold text-gray-900">Selling Advice</h3>
          </div>
          <p className="text-sm text-gray-700">
            {selectedCrop.risk_level === "high"
              ? "Consider selling immediately or within 2-3 days to avoid potential price drop."
              : selectedCrop.risk_level === "medium"
              ? "Monitor market for next 3-4 days. Sell when prices stabilize."
              : "Current conditions are favorable. Good time to sell produce."}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-purple-100 text-purple-600 p-3 rounded-lg">
              <Package size={24} />
            </div>
            <h3 className="font-semibold text-gray-900">Storage Advice</h3>
          </div>
          <p className="text-sm text-gray-700">
            {selectedCrop.risk_level === "high"
              ? "Storage not recommended unless you have cold storage facilities."
              : selectedCrop.risk_level === "medium"
              ? "Short-term storage (5-7 days) can be considered if facilities available."
              : "Storage can help you wait for better prices in coming weeks."}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-green-100 text-green-600 p-3 rounded-lg">
              <CloudRain size={24} />
            </div>
            <h3 className="font-semibold text-gray-900">Weather Impact</h3>
          </div>
          <p className="text-sm text-gray-700">
            Current weather conditions are being monitored. Rainfall in growing regions may
            affect supply and prices in coming weeks.
          </p>
        </div>
      </div>

      {/* Risk Factors */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Info size={20} className="text-blue-600" />
          <h3 className="font-semibold text-gray-900">Risk Factors Analysis</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Contributing Factors</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-red-600 mt-1">•</span>
                <span>Supply increase expected from neighboring regions</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 mt-1">•</span>
                <span>Seasonal harvest peak approaching</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">•</span>
                <span>Transportation costs fluctuating</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1">•</span>
                <span>Demand remains stable in major markets</span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Mitigation Strategies</h4>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>Explore alternative markets with better prices</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>Consider value addition or processing options</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>Coordinate with FPO for collective bargaining</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>Monitor daily alerts for market changes</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
