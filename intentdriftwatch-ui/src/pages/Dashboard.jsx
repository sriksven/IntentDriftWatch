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
  const [timeRange, setTimeRange] = useState("7d");
  const [selectedDate, setSelectedDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [contextShift, setContextShift] = useState(null);

  const [semantic, setSemantic] = useState([]);
  const [concept, setConcept] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [error, setError] = useState("");

  /* -------------------------------------------------- */
  /*  LOAD DATA                                         */
  /* -------------------------------------------------- */
  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const timestamp = new Date().getTime();
      let query = "";

      // Feature 1: Snapshot View (Specific Date)
      if (selectedDate) {
        query = `?date=${selectedDate}&_t=${timestamp}`;
        setTimeSeriesData([]); // Clear time series in snapshot mode
        setContextShift(null);

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
      }
      // Feature 2: Time Series View (Global Trend)
      else {
        query = `?time_range=${encodeURIComponent(timeRange)}&_t=${timestamp}`;

        // Fetch Trend & Top Shift
        const [trendRes, shiftRes, alertsRes] = await Promise.all([
          fetch(`${API_BASE}/analytics/global_trend${query}`),
          fetch(`${API_BASE}/analytics/top_shift${query}`),
          fetch(`${API_BASE}/alert_status${query}`) // Still show latest alerts? Or range alerts? Backend alert_status handles time_range
        ]);

        const trendJson = await trendRes.json();
        const shiftJson = await shiftRes.json();
        const alertsJson = await alertsRes.json();

        setTimeSeriesData(trendJson.trend || []);
        setContextShift(shiftJson.word_context ? shiftJson : null);
        setAlerts(alertsJson.alerts || alertsJson || []);

        // Clear snapshot specific data to avoid confusion
        setSummary(null);
        setSemantic([]);
        setConcept([]);
      }

    } catch (e) {
      console.error(e);
      setError("Failed to load analytics. Check backend.");
    }

    setLoading(false);

  }, [selectedDate, timeRange]);

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
    }, selectedDate ? REFRESH_MS : 60000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [loadData, selectedDate]);

  // Helper to check if summary is valid
  const isSnapshotMode = !!selectedDate;

  return (
    <div className="idw-main">

      <header className="idw-header-block">
        <h1 className="idw-page-title">Dashboard</h1>
        <p className="idw-page-subtitle">
          {isSnapshotMode ? "Snapshot analysis for specific date." : "Historical trends and key shifts."}
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

        {/* Time Range Selector */}
        <label className={`idw-field ${selectedDate ? "idw-disabled" : ""}`}>
          <span>Time Range</span>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            disabled={!!selectedDate}
            className="idw-select"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days (1 Week)</option>
            <option value="30d">Last 30 Days (1 Month)</option>
            <option value="6m">Last 6 Months</option>
            <option value="1y">Last 1 Year</option>
          </select>
        </label>

        <div style={{ alignSelf: "flex-end", paddingBottom: "0.5rem", fontSize: "0.9rem", color: "#666" }}>
          {isSnapshotMode
            ? `Viewing Snapshot: ${selectedDate}`
            : `Viewing Trend: ${timeRange}`}
        </div>
      </section>

      {error && <p className="idw-error">{error}</p>}

      {/* ================================================================================= */}
      {/* VIEW MODE 1: GLOBAL TRENDS (Default when no date selected)                        */}
      {/* ================================================================================= */}
      {!isSnapshotMode && (
        <>
          {/* Global Chart */}
          <DriftCharts timeSeriesData={timeSeriesData} />

          {/* Top Concept Shift Explanation */}
          {contextShift ? (
            <section className="idw-panel" style={{ marginTop: "1.5rem" }}>
              <header className="idw-panel-header" style={{ borderBottom: "1px solid #e5e7eb", paddingBottom: "1rem" }}>
                <div>
                  <h3 style={{ color: "#db2777" }}>Top Context Shift: {contextShift.topic}</h3>
                  <p>Most significant meaning change detected in this period ({contextShift.period}).</p>
                </div>
              </header>
              <div className="idw-panel-body">
                {contextShift.word_context && contextShift.word_context.map((item, i) => (
                  <div key={i} className="idw-comparison-row" style={{ marginBottom: "1rem", padding: "1rem", background: "#f9fafb", borderRadius: "8px" }}>
                    <div style={{ marginBottom: "0.5rem", fontWeight: "bold" }}>"{item.word}" ({item.type === "rising" ? "Rising" : "Falling"})</div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.9rem" }}>

                      <div style={{ background: "white", padding: "0.5rem", borderRadius: "4px", border: "1px solid #eee" }}>
                        <span style={{ color: "#6b7280", fontSize: "0.75rem", textTransform: "uppercase" }}>Used to mean:</span>
                        <ul style={{ paddingLeft: "1rem", margin: "0.5rem 0 0 0", color: "#4b5563" }}>
                          {item.context_old.map((s, idx) => <li key={idx}>{s}</li>)}
                        </ul>
                      </div>

                      <div style={{ background: "white", padding: "0.5rem", borderRadius: "4px", border: "1px solid #fce7f3" }}>
                        <span style={{ color: "#db2777", fontSize: "0.75rem", textTransform: "uppercase" }}>Now refers to:</span>
                        <ul style={{ paddingLeft: "1rem", margin: "0.5rem 0 0 0", color: "#4b5563" }}>
                          {item.context_new.map((s, idx) => <li key={idx}>{s}</li>)}
                        </ul>
                      </div>

                    </div>
                  </div>
                ))}
                <div style={{ marginTop: "1rem", textAlign: "right" }}>
                  <button className="idw-btn-xs" onClick={() => setSelectedTopic(contextShift.topic)}>Deep Dive Analysis →</button>
                </div>
              </div>
            </section>
          ) : (
            !loading && <div className="idw-panel" style={{ marginTop: "1rem", padding: "2rem", textAlign: "center", color: "#9ca3af" }}>No significant shifts detected in this range.</div>
          )}

          {/* Range Alerts */}
          <section className="idw-panel" style={{ marginTop: "1.5rem" }}>
            <header className="idw-panel-header">
              <h3>Recent Alerts</h3>
            </header>
            <div className="idw-panel-body">
              {loading ? (
                <TableSkeleton rows={3} />
              ) : alerts.length === 0 ? (
                <EmptyState message="No alerts in this period" />
              ) : (
                <ul className="idw-alert-list">
                  {alerts.map((a, i) => (
                    <li key={i} className="idw-alert-item">
                      <span className={`idw-pill ${a.severity === "critical" ? "idw-pill-bad" : a.severity === "warning" ? "idw-pill-warn" : "idw-pill-ok"}`}>{a.severity}</span>
                      <span style={{ marginLeft: "1rem" }}>{a.message}</span>
                      <span style={{ marginLeft: "auto", fontSize: "0.8rem", color: "#9ca3af" }}>{a.timestamp}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        </>
      )}

      {/* ================================================================================= */}
      {/* VIEW MODE 2: SNAPSHOT (Specific Date)                                            */}
      {/* ================================================================================= */}
      {isSnapshotMode && isValidSummary && (
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
