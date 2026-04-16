import { useEffect, useState } from "react";
import { getAdminStatus, refreshAllCrops, trainShockModel, AdminStatus } from "../data/api";
import { Activity, RefreshCw, Brain, Info, ShieldAlert } from "lucide-react";

export default function AdminMonitoring() {
  const [status, setStatus] = useState<AdminStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState<"refresh" | "train" | null>(null);

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

  if (loading) return <div className="p-8 text-center text-gray-500">Loading admin status...</div>;
  if (!status) return <div className="p-8 text-center text-red-500">Failed to load admin status</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{"Admin & data ops"}</h1>
        <p className="text-gray-600 max-w-3xl">
          This area is for <strong>operators or developers</strong>, not end farmers. It controls how fresh mandi data
          is pulled in and how the <strong>price-shock risk model</strong> is rebuilt from stored history.
        </p>
      </div>

      <div className="mb-8 rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
        <div className="flex gap-2">
          <ShieldAlert className="shrink-0 text-amber-700" size={20} />
          <div>
            <p className="font-semibold">Who should use this page?</p>
            <p className="mt-1">
              Someone who can run the backend, fix data.gov.in API issues, and occasionally retrain the model after enough
              new price rows exist. Farmers use <strong>Dashboard</strong>, <strong>Crops</strong>,{" "}
              <strong>Compare</strong>, and <strong>Alerts</strong> instead.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 mb-8">
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="mb-3 flex items-center gap-2 text-gray-900">
            <RefreshCw size={18} className="text-blue-600" />
            <h2 className="text-lg font-semibold">Refresh all crops</h2>
          </div>
          <p className="text-sm text-gray-700 mb-3">
            Queues a <strong>background job per crop</strong>: fetch latest prices (Agmarknet pipeline where
            configured), insert new rows, recompute risk scores, and regenerate the 14-day forecast. The hourly scheduler
            does the same automatically; this button is for an <strong>immediate full refresh</strong>.
          </p>
          <ul className="list-disc pl-5 text-sm text-gray-600 space-y-1">
            <li>
              <strong>data.gov.in 403 “Key not authorised”</strong> means the key in{" "}
              <code className="rounded bg-gray-100 px-1">backend/.env</code> is invalid for this dataset, or the portal
              has not approved API access for your account. Fix it on{" "}
              <a className="text-blue-600 underline" href="https://data.gov.in/" target="_blank" rel="noreferrer">
                data.gov.in
              </a>{" "}
              (same key + correct resource URL); do not rely on code changes alone.
            </li>
            <li>
              <strong>Total runs / Failed runs</strong> count pipeline executions (manual + scheduled). If failures
              rise, check backend logs and whether the local Agmarknet helper is reachable.
            </li>
            <li>
              <strong>Stale crops</strong> = crops whose last <em>actual</em> price date is older than 2 days (rule of
              thumb for demo freshness).
            </li>
          </ul>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <div className="mb-3 flex items-center gap-2 text-gray-900">
            <Brain size={18} className="text-green-600" />
            <h2 className="text-lg font-semibold">Train shock model</h2>
          </div>
          <p className="text-sm text-gray-700 mb-3">
            Rebuilds the <strong>RandomForest</strong> classifier from historical <code className="rounded bg-gray-100 px-1">price_data</code>{" "}
            rows: features from rolling windows, label = <strong>1</strong> if next-day price drops by more than{" "}
            <strong>10%</strong>, else <strong>0</strong>. On success, the model is saved to{" "}
            <code className="rounded bg-gray-100 px-1">backend/artifacts/shock_model.pkl</code> and the API starts using{" "}
            <code className="rounded bg-gray-100 px-1">predict_proba</code> for shock %. If training is skipped (not
            enough samples), the app keeps using the built-in rule-based score until you have more history.
          </p>
          <p className="text-sm text-gray-600">
            <strong>Prophet</strong> (separate step inside the pipeline) still drives the short price <em>curve</em>;
            this training step is only for the <strong>shock probability</strong> head.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Total Runs</p>
          <p className="text-2xl font-bold">{status.pipeline.total_runs}</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Failed Runs</p>
          <p className="text-2xl font-bold text-red-600">{status.pipeline.failed_runs}</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Stale Crops</p>
          <p className="text-2xl font-bold text-yellow-600">{status.stale_crops}</p>
        </div>
        <div className="bg-white border rounded-lg p-4">
          <p className="text-sm text-gray-600">Tracked Crops</p>
          <p className="text-2xl font-bold">{status.total_crops}</p>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-6 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Activity size={20} className="text-blue-600" />
          <h2 className="text-lg font-semibold">Operations</h2>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleRefreshAll}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw size={16} />
            {busy === "refresh" ? "Queuing…" : "Refresh all crops"}
          </button>
          <button
            type="button"
            disabled={busy !== null}
            onClick={handleTrainModel}
            className="px-4 py-2 rounded-lg bg-green-600 text-white flex items-center gap-2 disabled:opacity-50"
          >
            <Brain size={16} />
            {busy === "train" ? "Training…" : "Train shock model"}
          </button>
          <button type="button" onClick={loadStatus} className="px-4 py-2 rounded-lg border">
            Reload status
          </button>
        </div>
        {message && (
          <pre className="mt-4 max-h-64 overflow-auto rounded-md bg-gray-900 p-3 text-left text-xs text-green-100 whitespace-pre-wrap">
            {message}
          </pre>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6">
        <div className="mb-4 flex items-center gap-2">
          <Info size={18} className="text-gray-500" />
          <h2 className="text-lg font-semibold">Crop data freshness</h2>
        </div>
        <p className="mb-4 text-sm text-gray-600">
          Latest <strong>observed</strong> (non-forecast) price date per crop. Large gaps mean risk charts may be stale
          until the next successful refresh.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2">Crop</th>
                <th className="py-2">Latest actual date</th>
                <th className="py-2">Days since update</th>
              </tr>
            </thead>
            <tbody>
              {status.freshness.map((row) => (
                <tr key={row.crop_id} className="border-b">
                  <td className="py-2">{row.crop_name}</td>
                  <td className="py-2">{row.latest_actual_date || "-"}</td>
                  <td className={`py-2 ${(row.days_since_update || 0) > 2 ? "text-red-600 font-semibold" : "text-gray-700"}`}>
                    {row.days_since_update ?? "-"}
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
