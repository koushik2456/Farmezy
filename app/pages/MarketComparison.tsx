import { useEffect, useState } from "react";
import { getCrops, getMarketComparison, Crop, MarketCropComparison } from "../data/api";
import { RiskBadge } from "../components/RiskBadge";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  MapPin,
  Truck,
  Package,
  Users,
  Award,
  ArrowRight,
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

type ComparisonOrigin = { city: string; state: string; note: string };

export default function MarketComparison() {
  const [crops, setCrops] = useState<Crop[]>([]);
  const [selectedCropId, setSelectedCropId] = useState<number | null>(null);
  const [markets, setMarkets] = useState<MarketCropComparison[]>([]);
  const [comparisonOrigin, setComparisonOrigin] = useState<ComparisonOrigin | null>(null);
  const [loading, setLoading] = useState(true);
  const [comparisonLoading, setComparisonLoading] = useState(false);

  useEffect(() => {
    getCrops()
      .then((data) => {
        setCrops(data);
        if (data.length) setSelectedCropId(data[0].id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCropId) {
      setMarkets([]);
      setComparisonOrigin(null);
      return;
    }
    let cancelled = false;
    setComparisonLoading(true);
    getMarketComparison(selectedCropId)
      .then((bundle) => {
        if (!cancelled) {
          setMarkets(Array.isArray(bundle.markets) ? bundle.markets : []);
          setComparisonOrigin({
            city: bundle.origin_city,
            state: bundle.origin_state,
            note: bundle.origin_note,
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setMarkets([]);
          setComparisonOrigin(null);
        }
      })
      .finally(() => {
        if (!cancelled) setComparisonLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedCropId]);

  const selectedCrop = crops.find((c) => c.id === selectedCropId);

  // Calculate net profit for each market
  const marketsWithProfit = markets.map((market) => ({
    ...market,
    netPrice: market.current_price - market.transport_cost,
    netProfit: market.current_price - market.transport_cost,
  }));

  // Sort markets by net profit (descending)
  const sortedMarkets = [...marketsWithProfit].sort((a, b) => b.netProfit - a.netProfit);
  const bestMarket = sortedMarkets[0];

  // Prepare data for chart
  const chartData = marketsWithProfit.map((market) => ({
    name: market.market_name.split(" ")[0], // Short name
    price: market.current_price,
    netPrice: market.netPrice,
    transport: market.transport_cost,
  }));

  const getRiskColor = (risk: string) => {
    if (risk === "high") return "#dc2626";
    if (risk === "medium") return "#f59e0b";
    return "#16a34a";
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading comparison data...</div>;
  if (!selectedCrop) return <div className="p-8 text-center text-gray-500">No crop data available</div>;
  if (comparisonLoading) {
    return (
      <div className="p-8 text-center text-gray-500">
        Loading market comparison for {selectedCrop.name}...
      </div>
    );
  }
  if (markets.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Comparison</h1>
        <p className="text-gray-600 mb-4">No market rows returned for this crop. Check that the backend is running and markets are seeded.</p>
        <button
          type="button"
          onClick={() => {
            if (!selectedCropId) return;
            setComparisonLoading(true);
            getMarketComparison(selectedCropId)
              .then((bundle) => {
                setMarkets(Array.isArray(bundle.markets) ? bundle.markets : []);
                setComparisonOrigin({
                  city: bundle.origin_city,
                  state: bundle.origin_state,
                  note: bundle.origin_note,
                });
              })
              .catch(() => {
                setMarkets([]);
                setComparisonOrigin(null);
              })
              .finally(() => setComparisonLoading(false));
          }}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          Retry load
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Comparison</h1>
        <p className="text-gray-600">
          Compare prices and risks across different markets for the same crop
        </p>
        {comparisonOrigin && (
          <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-900">
            <p className="font-semibold">
              Reference location: {comparisonOrigin.city}, {comparisonOrigin.state}
            </p>
            <p className="mt-1 text-blue-800">{comparisonOrigin.note}</p>
          </div>
        )}
      </div>

      {/* Crop Selector */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Select Crop to Compare
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {crops.map((crop) => (
            <button
              key={crop.id}
              onClick={() => setSelectedCropId(crop.id)}
              className={`p-4 rounded-lg border-2 transition-all ${
                selectedCropId === crop.id
                  ? "border-green-600 bg-green-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <p className="font-semibold text-gray-900">{crop.name}</p>
              <p className="text-sm text-gray-600">{crop.name_hindi}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Best Market Recommendation */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 rounded-lg p-6 mb-8">
        <div className="flex items-start gap-4">
          <div className="bg-green-600 text-white p-3 rounded-lg">
            <Award size={32} />
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Best Market Recommendation for {selectedCrop.name}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
              <div>
                <p className="text-sm text-gray-600">Market</p>
                <p className="text-lg font-bold text-gray-900">{bestMarket.market_name}</p>
                <p className="text-sm text-gray-600">{bestMarket.state}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Net Price</p>
                <p className="text-2xl font-bold text-green-600">₹{bestMarket.netPrice}</p>
                <p className="text-xs text-gray-600">/quintal (after transport)</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Risk Level</p>
                <RiskBadge level={bestMarket.risk_level} size="md" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Distance</p>
                <p className="text-lg font-bold text-gray-900">
                  {bestMarket.distance_km <= 15
                    ? "Near Chennai"
                    : `${bestMarket.distance_km} km from Chennai`}
                </p>
              </div>
            </div>
            <p className="text-sm text-gray-700 bg-white rounded-lg p-3 border border-green-200">
              <strong>Recommendation:</strong> This market offers the best net profit with{" "}
              {bestMarket.risk_level} risk. {bestMarket.demand_level === "high" && "High demand ensures quick sales."}
              {bestMarket.storage_available && " Storage facilities are available if needed."}
            </p>
          </div>
        </div>
      </div>

      {/* Price Comparison Chart */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <h3 className="font-semibold text-lg text-gray-900 mb-4">
          Price Comparison - {selectedCrop.name}
        </h3>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} label={{ value: "Price (₹/quintal)", angle: -90, position: "insideLeft" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
              }}
              formatter={(value: number) => `₹${value}`}
            />
            <Legend />
            <Bar dataKey="price" fill="#3b82f6" name="Market Price" />
            <Bar dataKey="netPrice" fill="#16a34a" name="Net Price (after transport)" />
            <Bar dataKey="transport" fill="#f59e0b" name="Transport Cost" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Market Cards */}
      <div className="mb-4">
        <h3 className="font-semibold text-lg text-gray-900 mb-4">
          Detailed Market Comparison ({markets.length} Markets)
        </h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {sortedMarkets.map((market, index) => {
          const TrendIcon =
            market.trend === "up" ? TrendingUp : market.trend === "down" ? TrendingDown : Minus;
          const trendColor =
            market.trend === "up"
              ? "text-green-600"
              : market.trend === "down"
              ? "text-red-600"
              : "text-gray-600";

          const profitDiff = market.netProfit - bestMarket.netProfit;

          return (
            <div
              key={market.market_id}
              className={`bg-white border-2 rounded-lg p-6 ${
                index === 0 ? "border-green-500 shadow-lg" : "border-gray-200"
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start gap-3">
                  <div className="bg-blue-100 text-blue-600 p-2 rounded-lg">
                    <MapPin size={24} />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg text-gray-900">{market.market_name}</h4>
                    <p className="text-sm text-gray-600">{market.state}</p>
                  </div>
                </div>
                <div className="text-right">
                  <RiskBadge level={market.risk_level} size="sm" />
                  {index === 0 && (
                    <p className="text-xs text-green-600 font-semibold mt-1">BEST OPTION</p>
                  )}
                </div>
              </div>

              {/* Price Info */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Market Price</p>
                  <p className="text-xl font-bold text-gray-900">₹{market.current_price}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <TrendIcon size={16} className={trendColor} />
                    <span className={`text-sm font-semibold ${trendColor}`}>
                      {market.price_change > 0 ? "+" : ""}
                      {market.price_change}%
                    </span>
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-3">
                  <p className="text-xs text-gray-600 mb-1">Net Price</p>
                  <p className="text-xl font-bold text-green-900">₹{market.netPrice}</p>
                  <p className="text-xs text-gray-600 mt-1">After transport cost</p>
                </div>
              </div>

              {/* Additional Info */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-gray-700">
                    <Truck size={16} className="text-gray-500" />
                    <span>Distance & Transport</span>
                  </div>
                  <span className="font-semibold text-gray-900">
                    {market.distance_km <= 15
                      ? "Near Chennai"
                      : `${market.distance_km} km from Chennai`}{" "}
                    • ₹{market.transport_cost}/qtl
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-gray-700">
                    <Users size={16} className="text-gray-500" />
                    <span>Demand Level</span>
                  </div>
                  <span
                    className={`font-semibold ${
                      market.demand_level === "high"
                        ? "text-green-600"
                        : market.demand_level === "medium"
                        ? "text-yellow-600"
                        : "text-red-600"
                    }`}
                  >
                    {market.demand_level.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2 text-gray-700">
                    <Package size={16} className="text-gray-500" />
                    <span>Storage Available</span>
                  </div>
                  <span
                    className={`font-semibold ${
                      market.storage_available ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {market.storage_available ? "YES" : "NO"}
                  </span>
                </div>
              </div>

              {/* Risk Indicator */}
              <div className="border-t border-gray-200 pt-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Price Shock Risk</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {market.predicted_shock}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full"
                    style={{
                      width: `${market.predicted_shock}%`,
                      backgroundColor: getRiskColor(market.risk_level),
                    }}
                  />
                </div>
              </div>

              {/* Profit Comparison */}
              {profitDiff < 0 && (
                <div className="mt-3 bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-xs text-yellow-800">
                    <strong>Note:</strong> You could earn ₹{Math.abs(profitDiff)} more per quintal in {bestMarket.market_name}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Decision Helper */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="font-semibold text-lg text-gray-900 mb-4 flex items-center gap-2">
          <ArrowRight className="text-blue-600" size={20} />
          Decision Making Guide
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">If Priority is Maximum Price</h4>
            <p className="text-sm text-gray-700 mb-2">
              Choose market with highest net price after transport costs.
            </p>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="font-semibold text-green-900">{bestMarket.market_name}</p>
              <p className="text-sm text-green-700">₹{bestMarket.netPrice}/quintal</p>
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">If Priority is Low Risk</h4>
            <p className="text-sm text-gray-700 mb-2">
              Choose market with lowest price shock probability.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              {(() => {
                const lowestRisk = [...sortedMarkets].sort(
                  (a, b) => a.predicted_shock - b.predicted_shock
                )[0];
                return (
                  <>
                    <p className="font-semibold text-blue-900">{lowestRisk.market_name}</p>
                    <p className="text-sm text-blue-700">{lowestRisk.predicted_shock}% risk</p>
                  </>
                );
              })()}
            </div>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">If Priority is Quick Sale</h4>
            <p className="text-sm text-gray-700 mb-2">
              Choose market with high demand and low distance.
            </p>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              {(() => {
                const quickSale = [...sortedMarkets].filter(
                  (m) => m.demand_level === "high"
                )[0];
                return quickSale ? (
                  <>
                    <p className="font-semibold text-purple-900">{quickSale.market_name}</p>
                    <p className="text-sm text-purple-700">High demand</p>
                  </>
                ) : (
                  <p className="text-sm text-purple-700">No high-demand markets</p>
                );
              })()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
