import { createBrowserRouter } from "react-router";
import Dashboard from "./pages/Dashboard";
import CropAnalysis from "./pages/CropAnalysis";
import MarketAnalysis from "./pages/MarketAnalysis";
import Alerts from "./pages/Alerts";
import DetailedAnalysis from "./pages/DetailedAnalysis";
import MarketComparison from "./pages/MarketComparison";
import Root from "./pages/Root";
import AdminMonitoring from "./pages/AdminMonitoring";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Dashboard },
      { path: "crops", Component: CropAnalysis },
      { path: "markets", Component: MarketAnalysis },
      { path: "comparison", Component: MarketComparison },
      { path: "alerts", Component: Alerts },
      { path: "analysis", Component: DetailedAnalysis },
      { path: "admin", Component: AdminMonitoring },
    ],
  },
]);