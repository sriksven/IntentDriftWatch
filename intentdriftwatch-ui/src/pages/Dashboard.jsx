import { useEffect, useState, useCallback } from "react";
import DriftCharts from "../components/DriftCharts";
import TopicModal from "../components/TopicModal";

const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl
  ? settings.apiBaseUrl
  : window.location.hostname.includes("github.io")
    ? "https://intentdriftwatch.onrender.com"
    : "http://127.0.0.1:8000";
const REFRESH_MS = settings.refreshInterval || 30000;

function Dashboard() {
  const [selectedDate, setSelectedDate] = useState("");

  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState(null);

  const [semantic, setSemantic] = useState([]);
  const [concept, setConcept] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [error, setError] = useState("");

  /* -------------------------------------------------- */
  /*  LOAD DATA                                         */
  /* -------------------------------------------------- */
  /* -------------------------------------------------- */
  /*  LOAD DATES                                        */
  /* -------------------------------------------------- */
  useEffect(() => {
    async function loadDates() {
      try {
        const res = await fetch(`${API_BASE}/embeddings/info`);
        const json = await res.json();
        const dates = json.dates || [];
        if (dates.length > 0) {
          // Dates are typically sorted, but let's take the last one just in case
          // or sort them ourselves if needed. Assuming backend returns sorted or valid list.
          // Usually last item is latest.
          setSelectedDate(dates[dates.length - 1]);
        }
      } catch (err) {
        console.error("Failed to load dates:", err);
      }
    }
    loadDates();
  }, []);

  /* -------------------------------------------------- */
  /*  LOAD DATA                                         */
  /* -------------------------------------------------- */
  const loadData = useCallback(async () => {
    if (!selectedDate) return;

    setLoading(true);
    setError("");

    try {
      const timestamp = new Date().getTime();
      const query = `?date=${selectedDate}&_t=${timestamp}`;

      const [summaryRes, semRes, conceptRes, alertsRes] = await Promise.all([
        fetch(`${API_BASE}/drift_summary${query}`),
        fetch(`${API_BASE}/semantic_drift${query}`),
        fetch(`${API_BASE}/concept_drift${query}`),
        fetch(`${API_BASE}/alert_status${query}`)
      ]);

      const summaryJson = await summaryRes.json();
      const semJson = await semRes.json();
      const conceptJson = await conceptRes.json();
      const alertsJson = await alertsRes.json();

      setSummary(summaryJson);
      setSemantic(semJson.items || semJson || []);
      setConcept(conceptJson.items || conceptJson || []);
      setAlerts(alertsJson.alerts || alertsJson || []);

    } catch (e) {
      console.error(e);
      setError("Failed to load analytics. Check backend.");
    }

    setLoading(false);

  }, [selectedDate]);

  /* -------------------------------------------------- */
  /*  SAFE AUTO REFRESH                                 */
  /* -------------------------------------------------- */
  useEffect(() => {
    let active = true;
    requestAnimationFrame(() => {
      if (active) loadData();
    });
    // Refresh less frequently for global analytics
    const interval = setInterval(() => {
      if (active) loadData();
    }, 60000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [loadData, selectedDate]);

  // Helper to check if summary is valid
  const isValidSummary = summary && !summary.detail;

  return (
    <div className="idw-main">

      <header className="idw-header-block">
        <h1 className="idw-page-title">Dashboard</h1>
        <p className="idw-page-subtitle">
          Snapshot analysis for specific date.
        </p>
      </header>

      {/* ----------------------------------------------- */}
      {/* Controls                                         */}
      {/* ----------------------------------------------- */}
      <section className="idw-controls" style={{ flexWrap: "wrap", gap: "1.5rem" }}>

        {/* Date Picker */}
        <label className="idw-field">
          <span>Snapshot Date</span>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="idw-input"
            />
            {selectedDate && (
              <button
                className="idw-btn-xs"
                onClick={() => setSelectedDate("")}
                title="Clear to view history"
              >
                Clear
              </button>
            )}
          </div>
        </label>

        <div style={{ alignSelf: "flex-end", paddingBottom: "0.5rem", fontSize: "0.9rem", color: "#666" }}>
          {selectedDate ? `Viewing Snapshot: ${selectedDate}` : "Select a date to view snapshot"}
        </div>
      </section>

      {error && <p className="idw-error">{error}</p>}

      {/* ================================================================================= */}
      {/* VIEW MODE 2: SNAPSHOT (Specific Date)                                            */}
      {/* ================================================================================= */}
      {selectedDate && isValidSummary ? (
        <>
          <section className="idw-summary-row">
            <StatCard label="Snapshot Date" value={summary.date || "N/A"} highlight />
            <StatCard label="Semantic Drift Score" value={fmt(summary.semantic_drift_score)} />
            <StatCard label="Concept Drift Score" value={fmt(summary.concept_drift_score)} />
            <StatCard label="Topics Monitored" value={summary.topic_count || 0} />
            <StatCard label="Alerts" value={summary.alert_count || 0} />
          </section>

          {/* Charts (Topic Comparison mode) */}
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
                <SemanticTable items={semantic} setSelectedTopic={setSelectedTopic} />
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
          </section >

          {/* Alerts */}
          <section className="idw-panel">
            <header className="idw-panel-header"><h3>Active Alerts</h3></header>
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
                          className={`idw-pill ${a.severity === "critical"
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
        </>
      ) : (
        !loading && !selectedDate && (
          <div className="idw-panel" style={{ marginTop: "1rem", padding: "2rem", textAlign: "center", color: "#9ca3af" }}>
            Select a date to view snapshot analysis.
          </div>
        )
      )}

      {selectedTopic && (
        <TopicModal topic={selectedTopic} onClose={() => setSelectedTopic(null)} />
      )
      }

    </div >
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

function SemanticTable({ items, setSelectedTopic }) {
  // Check if we have any valid data for these columns
  const showDelta = items.some((i) => i.delta_freq !== null && i.delta_freq !== undefined && i.delta_freq !== "N/A");
  const showPVal = items.some((i) => i.p_value !== null && i.p_value !== undefined && i.p_value !== "N/A");

  return (
    <table className="idw-table">
      <thead>
        <tr>
          <th>Topic</th>
          <th>Drift Score</th>
          {showDelta && <th>Delta Freq</th>}
          {showPVal && <th>P Value</th>}
        </tr>
      </thead>
      <tbody>
        {items.map((s, i) => (
          <tr key={i} onClick={() => setSelectedTopic(s.topic)}>
            <td>{s.topic}</td>
            <td>{fmt(s.drift_score)}</td>
            {showDelta && <td>{fmt(s.delta_freq)}</td>}
            {showPVal && <td>{fmt(s.p_value, 4)}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function EmptyState({ message }) {
  return <p className="idw-empty">{message}</p>;
}

export default Dashboard;
