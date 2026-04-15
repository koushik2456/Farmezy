import { useState, useEffect } from "react";
import { AlertCard } from "../components/AlertCard";
import { getAlerts, markAlertRead, Alert, RiskLevel } from "../data/api";
import { Bell, BellOff, Filter } from "lucide-react";

export default function Alerts() {
  const [alertList, setAlertList] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState<RiskLevel | "all">("all");

  useEffect(() => {
    getAlerts(false)
      .then(setAlertList)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleMarkAsRead = async (id: number) => {
    try {
      await markAlertRead(id);
      setAlertList((prev) =>
        prev.map((alert) => (alert.id === id ? { ...alert, is_read: true } : alert))
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllAsRead = () => {
    const unread = alertList.filter((a) => !a.is_read);
    Promise.all(unread.map((a) => markAlertRead(a.id)))
      .then(() => {
        setAlertList((prev) => prev.map((alert) => ({ ...alert, is_read: true })));
      })
      .catch(console.error);
  };

  const filteredAlerts = alertList.filter((alert) => {
    const matchesReadStatus = !showUnreadOnly || !alert.is_read;
    const matchesRisk = selectedRisk === "all" || alert.risk_level === selectedRisk;
    return matchesReadStatus && matchesRisk;
  });

  const unreadCount = alertList.filter((a) => !a.is_read).length;

  if (loading) return <div className="p-8 text-center text-gray-500">Loading alerts...</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900">Alerts & Notifications</h1>
            {unreadCount > 0 && (
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-semibold">
                {unreadCount} new
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Mark all as read
            </button>
          )}
        </div>
        <p className="text-gray-600">Early warning alerts for price shock predictions</p>
      </div>

      {/* Alert Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Bell size={24} className="text-blue-600" />
            <h3 className="font-semibold text-gray-900">Total Alerts</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900">{alertList.length}</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <Bell size={24} className="text-red-600" />
            <h3 className="font-semibold text-red-900">Unread</h3>
          </div>
          <p className="text-3xl font-bold text-red-900">{unreadCount}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-center gap-3 mb-2">
            <BellOff size={24} className="text-green-600" />
            <h3 className="font-semibold text-green-900">Read</h3>
          </div>
          <p className="text-3xl font-bold text-green-900">
            {alertList.length - unreadCount}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-600" />
          <h3 className="font-semibold text-gray-900">Filter Alerts</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={showUnreadOnly}
                  onChange={(e) => setShowUnreadOnly(e.target.checked)}
                  className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <span className="text-sm text-gray-700">Show unread only</span>
              </label>
            </div>
          </div>

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
          Showing {filteredAlerts.length} of {alertList.length} alerts
        </p>
      </div>

      {/* Alert List */}
      {filteredAlerts.length > 0 ? (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <AlertCard key={alert.id} alert={alert} onMarkAsRead={handleMarkAsRead} />
          ))}
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <BellOff size={48} className="text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-2">No alerts match your filters</p>
          <button
            onClick={() => {
              setShowUnreadOnly(false);
              setSelectedRisk("all");
            }}
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Notification Settings Info */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="font-semibold text-yellow-900 mb-2">Alert Notification Settings</h3>
        <p className="text-sm text-yellow-800">
          You will receive alerts when price shock risk exceeds 50% for any crop in your
          selected markets. Alerts are generated daily based on latest market data and ML
          predictions.
        </p>
      </div>
    </div>
  );
}
