import { useState, useEffect } from "react";
import { CropCard } from "../components/CropCard";
import { getCrops, Crop, RiskLevel } from "../data/api";
import { Search, Filter } from "lucide-react";
import { useNavigate } from "react-router";

export default function CropAnalysis() {
  const navigate = useNavigate();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRisk, setSelectedRisk] = useState<RiskLevel | "all">("all");
  const [selectedSeason, setSelectedSeason] = useState<string>("all");

  useEffect(() => {
    getCrops()
      .then(setCrops)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const seasons = ["all", "Rabi", "Kharif", "Year-round", "Rabi & Kharif"];

  const filteredCrops = crops.filter((crop) => {
    const matchesSearch =
      crop.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (crop.name_hindi && crop.name_hindi.includes(searchTerm));
    const matchesRisk = selectedRisk === "all" || crop.risk_level === selectedRisk;
    const matchesSeason = selectedSeason === "all" || crop.season === selectedSeason;

    return matchesSearch && matchesRisk && matchesSeason;
  });

  const riskCounts = {
    high: crops.filter((c) => c.risk_level === "high").length,
    medium: crops.filter((c) => c.risk_level === "medium").length,
    low: crops.filter((c) => c.risk_level === "low").length,
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading crops...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Crop-wise Analysis</h1>
        <p className="text-gray-600">
          Detailed price shock risk analysis for all monitored crops
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-sm text-red-800 mb-2">High Risk</h3>
          <p className="text-4xl font-bold text-red-900">{riskCounts.high}</p>
          <p className="text-sm text-red-700 mt-2">Crops need immediate attention</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-sm text-yellow-800 mb-2">Medium Risk</h3>
          <p className="text-4xl font-bold text-yellow-900">{riskCounts.medium}</p>
          <p className="text-sm text-yellow-700 mt-2">Monitor market conditions</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-sm text-green-800 mb-2">Low Risk</h3>
          <p className="text-4xl font-bold text-green-900">{riskCounts.low}</p>
          <p className="text-sm text-green-700 mt-2">Stable market conditions</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-600" />
          <h3 className="font-semibold text-gray-900">Filter Crops</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Crop
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
                placeholder="Search by name..."
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

          {/* Season */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Season</label>
            <select
              value={selectedSeason}
              onChange={(e) => setSelectedSeason(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              {seasons.map((season) => (
                <option key={season} value={season}>
                  {season === "all" ? "All Seasons" : season}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          Showing {filteredCrops.length} of {crops.length} crops
        </p>
      </div>

      {/* Crop Grid */}
      {filteredCrops.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCrops.map((crop) => (
            <CropCard key={crop.id} crop={crop} onClick={() => navigate("/analysis")} />
          ))}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-600">No crops match your filters</p>
          <button
            onClick={() => {
              setSearchTerm("");
              setSelectedRisk("all");
              setSelectedSeason("all");
            }}
            className="mt-4 text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear all filters
          </button>
        </div>
      )}
    </div>
  );
}
