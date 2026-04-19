import { AlertTriangle, TrendingDown, TrendingUp, Sprout, Bell } from "lucide-react";
import { StatCard } from "../components/StatCard";
import { CropCard } from "../components/CropCard";
import { MarketCard } from "../components/MarketCard";
import { AlertCard } from "../components/AlertCard";
import { getCrops, getMarkets, getAlerts, markAlertRead, Crop, Market, Alert } from "../data/api";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router";

export default function Dashboard() {
  const navigate = useNavigate();
  const [crops, setCrops] = useState<Crop[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [alertList, setAlertList] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getCrops(), getMarkets(), getAlerts(false)])
      .then(([c, m, a]) => {
        setCrops(c);
        setMarkets(m);
        setAlertList(a);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const highRiskCrops = crops.filter((c) => c.risk_level === "high");
  const mediumRiskCrops = crops.filter((c) => c.risk_level === "medium");
  const unreadAlerts = alertList.filter((a) => !a.is_read);

  const handleMarkAsRead = async (id: number) => {
    try {
      await markAlertRead(id);
      setAlertList((prev) =>
        prev.map((alert) => (alert.id === id ? { ...alert, is_read: true } : alert))
      );
    } catch (err) {
      console.error("Failed to mark alert as read", err);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading live market data...</div>;
  }

  if (crops.length === 0 && markets.length === 0) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-gray-900 mb-2">No data from the API</h1>
        <p className="text-gray-600 mb-4">
          The backend returned no crops or markets. Usually this is a browser/API connection issue (CORS) or an empty
          database.
        </p>
        <ul className="text-left text-sm text-gray-700 space-y-2 bg-amber-50 border border-amber-200 rounded-lg p-4">
          <li>
            <strong>Open this app at</strong> <code className="bg-white px-1 rounded">http://localhost:5173</code> — if you
            use <code className="bg-white px-1 rounded">127.0.0.1</code> only, refresh using <strong>localhost</strong> after
            updating the app, or ensure the backend allows both (current default).
          </li>
          <li>
            <strong>Restart the backend</strong> after code changes, then hard-refresh the page (Ctrl+Shift+R).
          </li>
          <li>
            Run <code className="bg-white px-1 rounded">.\run-dev.ps1</code> once with seeding enabled so SQLite has crop
            rows.
          </li>
        </ul>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Market Price Shock Dashboard
        </h1>
        <p className="text-gray-600">
          Real-time risk analysis and early warning system for agricultural markets
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="High Risk Crops"
          value={highRiskCrops.length}
          subtitle="Immediate attention needed"
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Medium Risk Crops"
          value={mediumRiskCrops.length}
          subtitle="Monitor closely"
          icon={TrendingDown}
          color="yellow"
        />
        <StatCard
          title="Active Alerts"
          value={unreadAlerts.length}
          subtitle="Unread notifications"
          icon={Bell}
          color="blue"
        />
        <StatCard
          title="Monitored Crops"
          value={crops.length}
          subtitle="Across all markets"
          icon={Sprout}
          color="green"
        />
      </div>

      {/* High Risk Alerts */}
      {unreadAlerts.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Urgent Alerts</h2>
            <button
              onClick={() => navigate("/alerts")}
              className="text-blue-600 hover:text-blue-800 font-medium text-sm"
            >
              View all alerts →
            </button>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {unreadAlerts.slice(0, 2).map((alert) => (
              <AlertCard key={alert.id} alert={alert} onMarkAsRead={(id) => handleMarkAsRead(Number(id))} />
            ))}
          </div>
        </div>
      )}

      {/* High Risk Crops */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">High Risk Crops</h2>
          <button
            onClick={() => navigate("/crops")}
            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            View all crops →
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {highRiskCrops.map((crop) => (
            <CropCard key={crop.id} crop={crop} onClick={() => navigate("/analysis")} />
          ))}
        </div>
      </div>

      {/* Market Overview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Market Overview</h2>
          <button
            onClick={() => navigate("/markets")}
            className="text-blue-600 hover:text-blue-800 font-medium text-sm"
          >
            View all markets →
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {markets.slice(0, 3).map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </div>
      </div>

      {/* Information Banner */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">How This System Helps You</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
          <div>
            <p className="font-medium mb-1">Early Warning</p>
            <p>Get alerts 7-14 days before potential price drops</p>
          </div>
          <div>
            <p className="font-medium mb-1">Better Decisions</p>
            <p>Plan when to sell, store, or transport your produce</p>
          </div>
          <div>
            <p className="font-medium mb-1">Risk Analysis</p>
            <p>ML-based predictions using historical market data</p>
          </div>
        </div>
      </div>
    </div>
  );
}
