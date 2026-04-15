import { Link, useLocation } from "react-router";
import { LayoutDashboard, Sprout, MapPin, Bell, BarChart3, LogOut, GitCompare, ShieldCheck } from "lucide-react";

interface NavigationProps {
  onLogout?: () => void;
}

export function Navigation({ onLogout }: NavigationProps) {
  const location = useLocation();

  const links = [
    { path: "/", label: "Dashboard", icon: LayoutDashboard },
    { path: "/crops", label: "Crops", icon: Sprout },
    { path: "/markets", label: "Markets", icon: MapPin },
    { path: "/comparison", label: "Compare", icon: GitCompare },
    { path: "/alerts", label: "Alerts", icon: Bell },
    { path: "/analysis", label: "Analysis", icon: BarChart3 },
    { path: "/admin", label: "Admin (ops)", icon: ShieldCheck },
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div className="bg-green-600 text-white p-2 rounded-lg">
              <Sprout size={24} />
            </div>
            <div>
              <h1 className="font-bold text-lg text-gray-900">Price Shock Predictor</h1>
              <p className="text-xs text-gray-600">For Indian Farmers</p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;

              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                    isActive
                      ? "bg-green-100 text-green-800 font-medium"
                      : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                  }`}
                >
                  <Icon size={18} />
                  <span className="hidden sm:inline">{link.label}</span>
                </Link>
              );
            })}
            
            {onLogout && (
              <button
                onClick={onLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-red-600 hover:bg-red-50 ml-2"
                title="Logout"
              >
                <LogOut size={18} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}