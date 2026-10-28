
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import {
  Wind,
  Activity,
  Target,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import "./App.css";

const API = "https://windscope-wind-forecast-dashboard.onrender.com";

const DAY_AHEAD_CUTOFF_HOUR = 10;

function StatCard({ title, value, subtitle, icon: Icon }) {
  return (
    <article className="stat-card">
      <div className="stat-heading">
        <span>{title}</span>
        <Icon size={20} />
      </div>
      <h2>{value ?? "â€”"}</h2>
      <p>{subtitle}</p>
    </article>
  );
}

function formatTime(value) {
  return new Date(value).toLocaleString("en-GB", {
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  });
}

function selectDayAheadForecasts(forecasts) {
  const selected = new Map();

  for (const item of forecasts) {
    const deliveryTime = new Date(item.startTime);
    const publicationTime = new Date(item.publishTime);

    if (
      Number.isNaN(deliveryTime.getTime()) ||
      Number.isNaN(publicationTime.getTime())
    ) {
      continue;
    }

    const cutoff = new Date(deliveryTime);
    cutoff.setUTCDate(cutoff.getUTCDate() - 1);
    cutoff.setUTCHours(DAY_AHEAD_CUTOFF_HOUR, 0, 0, 0);

    if (publicationTime > cutoff) {
      continue;
    }

    const existing = selected.get(item.startTime);

    if (
      !existing ||
      publicationTime > new Date(existing.publishTime)
    ) {
      selected.set(item.startTime, item);
    }
  }

  return [...selected.values()].sort(
    (a, b) => new Date(a.startTime) - new Date(b.startTime)
  );
}

export default function App() {
  const [actuals, setActuals] = useState([]);
  const [forecasts, setForecasts] = useState([]);
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const responses = await Promise.all([
        fetch(`${API}/api/actuals`),
        fetch(`${API}/api/forecasts`),
        fetch(`${API}/api/accuracy`),
      ]);

      if (responses.some((response) => !response.ok)) {
        throw new Error("The backend returned an error.");
      }

      const [actualData, forecastData, accuracyData] =
        await Promise.all(
          responses.map((response) => response.json())
        );

      setActuals(actualData.data ?? []);
      setForecasts(forecastData.data ?? []);
      setAccuracy(accuracyData);
    } catch {
      setError(
        "Could not load data. Check that the Python backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const dayAheadForecasts = selectDayAheadForecasts(forecasts);

  const actualByTime = new Map(
    actuals.map((item) => [
      item.startTime,
      Number(item.generation),
    ])
  );

  const chartData = dayAheadForecasts.map((item) => ({
    time: formatTime(item.startTime),
    timestamp: item.startTime,
    forecast: Number(item.generation),
    actual: actualByTime.get(item.startTime) ?? null,
    publishTime: item.publishTime,
  }));

  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Wind size={26} />
          </div>
          <div>
            <h1>WindScope</h1>
            <p>Renewable Generation Intelligence</p>
          </div>
        </div>

        <button
          className="refresh-button"
          onClick={loadDashboard}
          disabled={loading}
        >
          <RefreshCw size={16} />
          {loading ? "Loading..." : "Refresh data"}
        </button>
      </header>

      <section className="intro">
        <p className="eyebrow">UK ENERGY MARKET Â· ELEXON BMRS</p>
        <h2>Wind Forecast Analytics</h2>
        <p>
          Explore historical wind forecasts, compare them with
          actual generation, and understand forecast uncertainty
          for day-ahead purchasing decisions.
        </p>
      </section>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <p className="loading">Loading January 2026 data...</p>
      ) : (
        <>
          <section className="stats-grid">
            <StatCard
              title="Matched Periods"
              value={accuracy?.matched_periods}
              subtitle="Matching forecast and actual timestamps"
              icon={Activity}
            />
            <StatCard
              title="Mean Absolute Error"
              value={accuracy?.mae}
              subtitle="Average absolute forecast error"
              icon={Target}
            />
            <StatCard
              title="Root Mean Squared Error"
              value={accuracy?.rmse}
              subtitle="Highlights larger errors"
              icon={TrendingUp}
            />
            <StatCard
              title="Forecast Bias"
              value={accuracy?.bias}
              subtitle="Positive means overforecast"
              icon={Wind}
            />
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h3>Day-Ahead Forecast vs Actual Generation</h3>
                <p>
                  Delivery timestamps shown in UTC. Forecasts
                  published by 10:00 UTC on the previous day.
                </p>
              </div>
              <span className="chart-tag">
                {chartData.length} selected forecasts
              </span>
            </div>

            {chartData.length > 0 ? (
              <div className="chart">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="time"
                      minTickGap={35}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(_, payload) =>
                        payload?.[0]?.payload?.timestamp
                          ? new Date(
                              payload[0].payload.timestamp
                            ).toISOString()
                          : ""
                      }
                      formatter={(value, name) => [
                        value == null
                          ? "No matching actual"
                          : Number(value).toLocaleString(),
                        name,
                      ]}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      name="Day-Ahead Forecast"
                      stroke="#16a34a"
                      dot={false}
                      connectNulls={false}
                    />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      name="Actual Generation"
                      stroke="#2563eb"
                      dot={false}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="empty">
                No forecasts were available before the selected cutoff.
              </p>
            )}
          </section>

          <section className="panel">
            <div className="panel-heading">
              <div>
                <h3>Forecast Publication Details</h3>
                <p>
                  All historical forecast records returned by Elexon,
                  including revisions.
                </p>
              </div>
            </div>

            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Delivery time (UTC)</th>
                    <th>Publication time (UTC)</th>
                    <th>Forecast generation</th>
                  </tr>
                </thead>
                <tbody>
                  {forecasts.map((item, index) => (
                    <tr key={`${item.startTime}-${item.publishTime}-${index}`}>
                      <td>{item.startTime}</td>
                      <td>{item.publishTime}</td>
                      <td>
                        {Number(item.generation).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <p className="disclaimer">
            Preliminary analysis only. The 10:00 UTC cutoff is a
            project assumption and should be validated against the
            intended procurement decision time. Forecast accuracy
            depends on matching the same delivery periods and using
            only forecasts available by that cutoff.
          </p>
        </>
      )}
    </main>
  );
}

