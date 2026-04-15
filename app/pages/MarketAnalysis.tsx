import { useState, useEffect } from "react";
import { MarketCard } from "../components/MarketCard";
import { getMarkets, Market, RiskLevel } from "../data/api";
import { Search, MapPin } from "lucide-react";

export default function MarketAnalysis() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRisk, setSelectedRisk] = useState<RiskLevel | "all">("all");

  useEffect(() => {
    getMarkets()
      .then(setMarkets)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filteredMarkets = markets.filter((market) => {
    const matchesSearch =
      market.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      market.state.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRisk = selectedRisk === "all" || market.risk_level === selectedRisk;

    return matchesSearch && matchesRisk;
  });

  const states = [...new Set(markets.map((m) => m.state))];

  if (loading) return <div className="p-8 text-center text-gray-500">Loading markets...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Analysis</h1>
        <p className="text-gray-600">
          Regional mandi market risk analysis and price trends
        </p>
      </div>

      {/* Market Overview Map */}
      <div className="bg-gradient-to-br from-green-50 to-blue-50 border border-gray-200 rounded-lg p-8 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <MapPin size={24} className="text-green-600" />
          <h2 className="text-xl font-semibold text-gray-900">
            Market Coverage - {states.length} States
          </h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {states.map((state) => {
            const stateMarkets = markets.filter((m) => m.state === state);
            const highRiskMarkets = stateMarkets.filter((m) => m.risk_level === "high");

            return (
              <div key={state} className="bg-white rounded-lg p-4 text-center">
                <p className="font-semibold text-gray-900 mb-1">{state}</p>
                <p className="text-2xl font-bold text-gray-900">{stateMarkets.length}</p>
                <p className="text-xs text-gray-600">
                  {highRiskMarkets.length > 0 && (
                    <span className="text-red-600">{highRiskMarkets.length} high risk</span>
                  )}
                  {highRiskMarkets.length === 0 && <span className="text-green-600">Stable</span>}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <h3 className="font-semibold text-gray-900 mb-4">Filter Markets</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Market or State
            </label>
            <div className="relative">
              <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by market name or state..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>

          {/* Risk Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Level
            </label>
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value as RiskLevel | "all")}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="all">All Levels</option>
              <option value="high">High Risk</option>
              <option value="medium">Medium Risk</option>
              <option value="low">Low Risk</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Showing {filteredMarkets.length} of {markets.length} markets
        </p>
      </div>

      {/* Market Grid */}
      {filteredMarkets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredMarkets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-600">No markets match your filters</p>
          <button
            onClick={() => {
              setSearchTerm("");
              setSelectedRisk("all");
            }}
            className="mt-4 text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}

      {/* Information */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-3">Understanding Market Risk</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>
            <strong>High Risk Markets:</strong> Multiple crops showing high shock probability.
            Consider alternative markets or storage.
          </p>
          <p>
            <strong>Medium Risk Markets:</strong> Some price fluctuations expected. Monitor
            closely before selling.
          </p>
          <p>
            <strong>Low Risk Markets:</strong> Stable conditions. Good time to sell produce.
          </p>
        </div>
      </div>
    </div>
  );
}
