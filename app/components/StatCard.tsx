import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color?: "green" | "yellow" | "red" | "blue";
}

export function StatCard({ title, value, subtitle, icon: Icon, trend, color = "blue" }: StatCardProps) {
  const colorConfigs = {
    green: {
      bg: "bg-green-100",
      icon: "text-green-600",
      border: "border-green-200",
    },
    yellow: {
      bg: "bg-yellow-100",
      icon: "text-yellow-600",
      border: "border-yellow-200",
    },
    red: {
      bg: "bg-red-100",
      icon: "text-red-600",
      border: "border-red-200",
    },
    blue: {
      bg: "bg-blue-100",
      icon: "text-blue-600",
      border: "border-blue-200",
    },
  };

  const config = colorConfigs[color];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
          {trend && (
            <p
              className={`text-sm mt-2 ${
                trend.isPositive ? "text-green-600" : "text-red-600"
              }`}
            >
              {trend.isPositive ? "↑" : "↓"} {Math.abs(trend.value)}% from last week
            </p>
          )}
        </div>
        <div className={`${config.bg} ${config.icon} p-3 rounded-lg`}>
          <Icon size={24} />
        </div>
      </div>
    </div>
  );
}
