import { useEffect, useState, useCallback } from "react";
import DriftCharts from "../components/DriftCharts";
import TopicModal from "../components/TopicModal";

const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl || "http://127.0.0.1:8000";
const REFRESH_MS = settings.refreshInterval || 30000;

function Dashboard() {
  const [timeRange, setTimeRange] = useState("7d");
  const [modelName, setModelName] = useState("default");
  const [summaryDate, setSummaryDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [semantic, setSemantic] = useState([]);
  const [concept, setConcept] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [error, setError] = useState("");

  /* -------------------------------------------------- */
  /*  LOAD DATA (memoized for ESLint)                   */
  /* -------------------------------------------------- */
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const query = `?time_range=${encodeURIComponent(timeRange)}&model=${encodeURIComponent(
        modelName
      )}`;

      const [summaryRes, semRes, conceptRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/drift_summary`),
        fetch(`${API_BASE}/semantic_drift${query}`),
        fetch(`${API_BASE}/concept_drift${query}`),
        fetch(`${API_BASE}/alert_status${query}`)
      ]);

      const summaryJson = await summaryRes.json();
      const semJson = await semRes.json();
      const conceptJson = await conceptRes.json();
      const alertsJson = await alertsRes.json();

      setSummary(summaryJson);
      setSummaryDate(summaryJson.date || "");

      setSemantic(semJson.items || semJson || []);
      setConcept(conceptJson.items || conceptJson || []);
      setAlerts(alertsJson.alerts || alertsJson || []);

    } catch {
      setError("Failed to load dashboard data. Check backend.");
    }

    setLoading(false);

  }, [timeRange, modelName]);

  /* -------------------------------------------------- */
  /*  SAFE AUTO REFRESH (no ESLint warnings)            */
  /* -------------------------------------------------- */
  useEffect(() => {
    let active = true;

    requestAnimationFrame(() => {
      if (active) loadData();
    });

    const interval = setInterval(() => {
      if (active) loadData();
    }, REFRESH_MS);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [loadData]);

  /* -------------------------------------------------- */
  /*  DATE OVERRIDE                                      */
  /* -------------------------------------------------- */
  function handleDateOverride() {
    if (!summaryDate) return;

    fetch(`${API_BASE}/drift_summary?date=${summaryDate}`)
      .then((r) => r.json())
      .then((s) => setSummary(s))
      .catch(() => setError("Failed to load summary for selected date."));
  }

  return (
    <div className="idw-main">

      <header className="idw-header-block">
        <h1 className="idw-page-title">Dashboard</h1>
        <p className="idw-page-subtitle">Live monitoring of semantic and concept drift.</p>
      </header>

      {/* ----------------------------------------------- */}
      {/* Controls                                         */}
      {/* ----------------------------------------------- */}
      <section className="idw-controls">

        <label className="idw-field">
          <span>Time Range</span>
          <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="24h">24 hours</option>
            <option value="7d">7 days</option>
            <option value="30d">30 days</option>
          </select>
        </label>

        <label className="idw-field">
          <span>Model</span>
          <input value={modelName} onChange={(e) => setModelName(e.target.value)} />
        </label>

        <label className="idw-field">
          <span>Date</span>
          <input
            value={summaryDate}
            onChange={(e) => setSummaryDate(e.target.value)}
            onBlur={handleDateOverride}
            placeholder="YYYY-MM-DD"
          />
        </label>

      </section>

      {error && <p className="idw-error">{error}</p>}

      {/* ----------------------------------------------- */}
      {/* Summary Cards                                    */}
      {/* ----------------------------------------------- */}
      {summary && (
        <section className="idw-summary-row">
          <StatCard label="Semantic Drift Score" value={fmt(summary.semantic_drift_score)} />
          <StatCard label="Concept Drift Score" value={fmt(summary.concept_drift_score)} />
          <StatCard label="Topics Monitored" value={summary.topic_count || 0} />
          <StatCard label="Alerts" value={summary.alert_count || 0} highlight />
        </section>
      )}

      {/* Charts */}
      <DriftCharts semantic={semantic} concept={concept} />

      {/* Semantic Table */}
      <section className="idw-panel">
        <header className="idw-panel-header">
          <h3>Semantic Drift</h3>
          <p>Embedding drift per topic.</p>
        </header>

        <div className="idw-panel-body">
          {loading ? (
            <TableSkeleton rows={4} />
          ) : semantic.length === 0 ? (
            <EmptyState message="No semantic drift detected" />
          ) : (
            <table className="idw-table">
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Drift Score</th>
                  <th>Delta Freq</th>
                  <th>P Value</th>
                </tr>
              </thead>
              <tbody>
                {semantic.map((s, i) => (
                  <tr key={i} onClick={() => setSelectedTopic(s.topic)}>
                    <td>{s.topic}</td>
                    <td>{fmt(s.drift_score)}</td>
                    <td>{fmt(s.delta_freq)}</td>
                    <td>{fmt(s.p_value, 4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {/* Concept Drift */}
      <section className="idw-panel">
        <header className="idw-panel-header">
          <h3>Concept Drift</h3>
          <p>Distribution drift across labels or features.</p>
        </header>

        <div className="idw-panel-body">
          {loading ? (
            <TableSkeleton rows={4} />
          ) : concept.length === 0 ? (
            <EmptyState message="No concept drift detected" />
          ) : (
            <table className="idw-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>Test</th>
                  <th>Statistic</th>
                  <th>P Value</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {concept.map((c, i) => (
                  <tr key={i} onClick={() => setSelectedTopic(c.feature || c.label)}>
                    <td>{c.feature || c.label}</td>
                    <td>{c.test_name}</td>
                    <td>{fmt(c.statistic)}</td>
                    <td>{fmt(c.p_value, 4)}</td>
                    <td>
                      <span className={c.is_drifting ? "idw-pill idw-pill-bad" : "idw-pill idw-pill-ok"}>
                        {c.is_drifting ? "Drifting" : "Stable"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>

      {/* Alerts */}
      <section className="idw-panel">
        <header className="idw-panel-header">
          <h3>Alerts</h3>
          <p>Triggered drift alerts.</p>
        </header>
        <div className="idw-panel-body">
          {loading ? (
            <TableSkeleton rows={3} />
          ) : alerts.length === 0 ? (
            <EmptyState message="No alerts triggered" />
          ) : (
            <ul className="idw-alert-list">
              {alerts.map((a, i) => (
                <li key={i} className="idw-alert-item">
                  <div className="idw-alert-header">
                    <span
                      className={`idw-pill ${
                        a.severity === "critical"
                          ? "idw-pill-bad"
                          : a.severity === "warning"
                          ? "idw-pill-warn"
                          : "idw-pill-ok"
                      }`}
                    >
                      {a.severity}
                    </span>
                    <span>{a.timestamp}</span>
                  </div>
                  <p className="idw-alert-message">{a.message}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      {selectedTopic && (
        <TopicModal topic={selectedTopic} onClose={() => setSelectedTopic(null)} />
      )}

    </div>
  );
}

function fmt(v, d = 3, f = "N/A") {
  if (v === null || v === undefined || isNaN(v)) return f;
  return Number(v).toFixed(d);
}

function StatCard({ label, value, highlight }) {
  return (
    <div className={`idw-stat-card ${highlight ? "idw-stat-highlight" : ""}`}>
      <p className="idw-stat-label">{label}</p>
      <p className="idw-stat-value">{value}</p>
    </div>
  );
}

function TableSkeleton({ rows }) {
  return (
    <div className="idw-table-skeleton">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="idw-skeleton-row" />
      ))}
    </div>
  );
}

function EmptyState({ message }) {
  return <p className="idw-empty">{message}</p>;
}

export default Dashboard;
