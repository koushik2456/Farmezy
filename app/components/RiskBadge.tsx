import { RiskLevel } from "../data/api";
import { AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";

interface RiskBadgeProps {
  level: RiskLevel;
  size?: "sm" | "md" | "lg";
  showIcon?: boolean;
}

export function RiskBadge({ level, size = "md", showIcon = true }: RiskBadgeProps) {
  const configs = {
    low: {
      bg: "bg-green-100",
      text: "text-green-800",
      border: "border-green-300",
      label: "Low Risk",
      Icon: CheckCircle,
    },
    medium: {
      bg: "bg-yellow-100",
      text: "text-yellow-800",
      border: "border-yellow-300",
      label: "Medium Risk",
      Icon: AlertCircle,
    },
    high: {
      bg: "bg-red-100",
      text: "text-red-800",
      border: "border-red-300",
      label: "High Risk",
      Icon: AlertTriangle,
    },
  };

  const config = configs[level];
  const Icon = config.Icon;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
    lg: "px-4 py-2 text-base",
  };

  const iconSizes = {
    sm: 12,
    md: 16,
    lg: 20,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${config.bg} ${config.text} ${config.border} ${sizeClasses[size]} font-medium`}
    >
      {showIcon && <Icon size={iconSizes[size]} />}
      {config.label}
    </span>
  );
}
