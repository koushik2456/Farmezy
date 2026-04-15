import { Alert } from "../data/api";
import { RiskBadge } from "./RiskBadge";
import { Clock, MapPin, Sprout, Lightbulb } from "lucide-react";

interface AlertCardProps {
  alert: Alert;
  onMarkAsRead?: (id: number) => void;
}

export function AlertCard({ alert, onMarkAsRead }: AlertCardProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return "Just now";
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays === 1) return "Yesterday";
    return `${diffDays} days ago`;
  };

  return (
    <div
      className={`bg-white border rounded-lg p-5 ${
        alert.is_read ? "border-gray-200" : "border-blue-300 bg-blue-50"
      }`}
    >
      <div className="flex items-start justify-between mb-3">
        <RiskBadge level={alert.risk_level} size="md" />
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Clock size={14} />
          <span>{formatDate(alert.date)}</span>
        </div>
      </div>

      <h3 className="font-semibold text-lg text-gray-900 mb-2">{alert.message}</h3>

      <div className="flex items-center gap-4 mb-3 text-sm text-gray-600">
        <div className="flex items-center gap-1">
          <Sprout size={16} />
          <span>{alert.crop_name || `Crop #${alert.crop_id}`}</span>
        </div>
        <div className="flex items-center gap-1">
          <MapPin size={16} />
          <span>{alert.market_name || `Market #${alert.market_id}`}</span>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
        <div className="flex items-start gap-2">
          <Lightbulb size={16} className="text-yellow-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-xs font-semibold text-yellow-800 mb-1">Recommendation</p>
            <p className="text-sm text-yellow-900">{alert.recommendation}</p>
          </div>
        </div>
      </div>

      {!alert.is_read && onMarkAsRead && (
        <button
          onClick={() => onMarkAsRead(alert.id)}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Mark as read
        </button>
      )}
    </div>
  );
}
