import { useEffect, useState } from "react";
import { getAdminStatus, refreshAllCrops, trainShockModel, syncIngestAndTrain, AdminStatus } from "../data/api";
import { Activity, RefreshCw, Brain, Info, ShieldAlert, Zap } from "lucide-react";

export default function AdminMonitoring() {
  const [status, setStatus] = useState<AdminStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState<"refresh" | "train" | "full" | null>(null);

  const loadStatus = async () => {
    try {
      const data = await getAdminStatus();
      setStatus(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleRefreshAll = async () => {
    setBusy("refresh");
    setMessage("");
    try {
      const res = await refreshAllCrops();
      setMessage(res.message);
      await loadStatus();
    } catch (e) {
      setMessage(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(null);
    }
  };

  const handleTrainModel = async () => {
    setBusy("train");
    setMessage("");
    try {
      const res = await trainShockModel();
      setMessage(JSON.stringify(res, null, 2));
      await loadStatus();
    } catch (e) {
      setMessage(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(null);
    }
  };

  const handleFullPipeline = async () => {
    setBusy("full");
    setMessage("");
    try {
      const res = await syncIngestAndTrain();
      setMessage(JSON.stringify(res, null, 2));
      await loadStatus();
    } catch (e) {
      setMessage(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(null);
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading admin status...</div>;
  if (!status) return <div className="p-8 text-center text-red-500">Failed to load admin status</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">Data operations</h1>
        <p className="text-gray-600 text-sm">
          Backend maintenance only — farmers use Dashboard, Crops, Compare, Alerts.
        </p>
      </div>

      <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-950">
        <p className="font-semibold mb-2">If the main app shows no crops or markets</p>
        <ol className="list-decimal pl-5 space-y-1">
          <li>
            Open the UI at <strong>http://localhost:5173</strong> (not only <code className="bg-white/80 px-1 rounded">127.0.0.1</code>) so
            browser security matches the API CORS settings.
          </li>
          <li>Restart the backend after pulling updates so CORS + database path changes apply.</li>
          <li>
            Mandi data needs a valid <code className="bg-white/80 px-1 rounded">AGMARKNET_API_KEY</code> in{" "}
            <code className="bg-white/80 px-1 rounded">backend/.env</code>. Rate limits (429) or bad keys show in the backend
            terminal.
          </li>
        </ol>
      </div>

      <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950 flex gap-3">
        <ShieldAlert className="shrink-0 text-amber-700 mt-0.5" size={18} />
        <div>
          <p className="font-semibold">What each action does</p>
          <ul className="mt-2 space-y-2 list-disc pl-5">
            <li>
              <strong>Full ingest + train</strong> — Slow. Fetches mandi prices for every crop, updates forecasts, then
              retrains the shock model. Same as the end of <code className="bg-white/70 px-1 rounded">.\run-dev.ps1</code>.
            </li>
            <li>
              <strong>Refresh all crops</strong> — Starts the same fetch in the background; returns immediately. Check
              stats below after ~1–2 minutes.
            </li>
            <li>
              <strong>Train shock model only</strong> — Retrains the RandomForest from data already in the database (no new
              API fetch).
            </li>
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500">Pipeline runs</p>
          <p className="text-xl font-bold">{status.pipeline.total_runs}</p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500">Failed</p>
          <p className="text-xl font-bold text-red-600">{status.pipeline.failed_runs}</p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500">Stale crops</p>
          <p className="text-xl font-bold text-yellow-600">{status.stale_crops}</p>
        </div>
        <div className="bg-white border rounded-lg p-3">
          <p className="text-xs text-gray-500">Tracked crops</p>
          <p className="text-xl font-bold">{status.total_crops}</p>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-5 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Activity size={18} className="text-blue-600" />
          <h2 className="text-base font-semibold">Actions</h2>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleFullPipeline}
            className="px-3 py-2 rounded-lg bg-slate-800 text-white text-sm flex items-center gap-2 disabled:opacity-50"
          >
            <Zap size={16} />
            {busy === "full" ? "Running…" : "Full ingest + train"}
          </button>
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleRefreshAll}
            className="px-3 py-2 rounded-lg bg-blue-600 text-white text-sm flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw size={16} />
            {busy === "refresh" ? "Queuing…" : "Refresh all (background)"}
          </button>
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleTrainModel}
            className="px-3 py-2 rounded-lg bg-green-600 text-white text-sm flex items-center gap-2 disabled:opacity-50"
          >
            <Brain size={16} />
            {busy === "train" ? "Training…" : "Train model only"}
          </button>
          <button type="button" onClick={loadStatus} className="px-3 py-2 rounded-lg border text-sm">
            Reload status
          </button>
        </div>
        {message && (
          <pre className="mt-4 max-h-56 overflow-auto rounded-md bg-gray-900 p-3 text-left text-xs text-green-100 whitespace-pre-wrap">
            {message}
          </pre>
        )}
      </div>

      <div className="bg-white border rounded-lg p-5">
        <div className="flex items-center gap-2 mb-3">
          <Info size={18} className="text-gray-500" />
          <h2 className="text-base font-semibold">Latest price date per crop</h2>
        </div>
        <p className="text-sm text-gray-600 mb-3">Non-forecast rows only. Red numbers mean data is getting old.</p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-2">Crop</th>
                <th className="py-2 pr-2">Latest date</th>
                <th className="py-2">Days ago</th>
              </tr>
            </thead>
            <tbody>
              {status.freshness.map((row) => (
                <tr key={row.crop_id} className="border-b">
                  <td className="py-2">{row.crop_name}</td>
                  <td className="py-2">{row.latest_actual_date || "—"}</td>
                  <td className={`py-2 ${(row.days_since_update || 0) > 2 ? "text-red-600 font-semibold" : "text-gray-700"}`}>
                    {row.days_since_update ?? "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
