import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from "recharts";
import { PriceData } from "../data/api";

interface PriceChartProps {
  data: PriceData[];
  cropName: string;
}

export function PriceChart({ data, cropName }: PriceChartProps) {
  const formattedData = data.map((item) => ({
    ...item,
    displayDate: new Date(item.date).toLocaleDateString("en-IN", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="font-semibold text-lg text-gray-900 mb-4">
        Price Trend & Prediction - {cropName}
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={formattedData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="displayDate"
            tick={{ fontSize: 12 }}
            tickMargin={10}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickMargin={10}
            label={{ value: "Price (₹/quintal)", angle: -90, position: "insideLeft" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
            }}
            formatter={(value: number, name: string) => {
              if (name === "price") return [`₹${value}`, "Actual Price"];
              if (name === "predicted") return [`₹${value}`, "Predicted Price"];
              if (name === "shock_probability") return [`${value}%`, "Shock Risk"];
              return [value, name];
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="price"
            stroke="#2563eb"
            strokeWidth={2}
            dot={false}
            name="Actual Price"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="predicted"
            stroke="#16a34a"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="Predicted Price"
            connectNulls
          />
          <Line
            type="monotone"
            dataKey="shock_probability"
            stroke="#dc2626"
            strokeWidth={2}
            dot={false}
            name="Shock Risk %"
            connectNulls
            yAxisId="right"
          />
          <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 bg-blue-600 rounded-full" />
            <p className="text-xs text-gray-600">Actual Price</p>
          </div>
          <p className="text-sm text-gray-900">Historical market data</p>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 bg-green-600 rounded-full" />
            <p className="text-xs text-gray-600">Predicted Price</p>
          </div>
          <p className="text-sm text-gray-900">ML model forecast</p>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 bg-red-600 rounded-full" />
            <p className="text-xs text-gray-600">Shock Risk</p>
          </div>
          <p className="text-sm text-gray-900">Probability of price drop</p>
        </div>
      </div>
    </div>
  );
}
