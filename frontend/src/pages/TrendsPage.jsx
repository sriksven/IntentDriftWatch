import { useEffect, useState, useCallback } from "react";
import DriftCharts from "../components/DriftCharts";
import TopicModal from "../components/TopicModal";
import DriftVelocityGauge from "../components/DriftVelocityGauge";
import DriftHeatmap from "../components/DriftHeatmap";


const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl
    ? settings.apiBaseUrl
    : window.location.hostname.includes("github.io")
        ? "https://intentdriftwatch.onrender.com"
        : "http://127.0.0.1:8000";
const REFRESH_MS = 60000; // Trends refresh less often

function TrendsPage() {
    const [timeRange, setTimeRange] = useState("7d");
    const [eli5Mode, setEli5Mode] = useState(false);


    const [loading, setLoading] = useState(true);
    const [timeSeriesData, setTimeSeriesData] = useState([]);
    const [contextShift, setContextShift] = useState(null);

    const [alerts, setAlerts] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState(null);
    const [error, setError] = useState("");

    const loadData = useCallback(async () => {
        setLoading(true);
        setError("");

        try {
            const timestamp = new Date().getTime();
            const query = `?time_range=${encodeURIComponent(timeRange)}&_t=${timestamp}`;

            // Fetch Trend & Top Shift
            const [trendRes, shiftRes, alertsRes] = await Promise.all([
                fetch(`${API_BASE}/analytics/global_trend${query}`),
                fetch(`${API_BASE}/analytics/top_shift${query}`),
                fetch(`${API_BASE}/alert_status${query}`)
            ]);

            const trendJson = await trendRes.json();
            const shiftJson = await shiftRes.json();
            const alertsJson = await alertsRes.json();

            setTimeSeriesData(trendJson);
            setContextShift(shiftJson.word_context ? shiftJson : null);
            setAlerts(alertsJson.alerts || alertsJson || []);

        } catch (e) {
            console.error(e);
            setError("Failed to load analytics. Check backend.");
        }

        setLoading(false);

    }, [timeRange]);

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


    return (
        <div className="idw-main">

            <header className="idw-header-block">
                <h1 className="idw-page-title">Reflex Trends</h1>
                <p className="idw-page-subtitle">
                    Historical drifts and key context shifts over time.
                </p>
            </header>

            {/* Controls */}
            <section className="idw-controls" style={{ flexWrap: "wrap", gap: "1.5rem" }}>
                {/* Time Range Selector */}
                <label className="idw-field">
                    <span>Time Range</span>
                    <select
                        value={timeRange}
                        onChange={(e) => setTimeRange(e.target.value)}
                        className="idw-select"
                    >
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days (1 Week)</option>
                        <option value="30d">Last 30 Days (1 Month)</option>
                        <option value="6m">Last 6 Months</option>
                        <option value="1y">Last 1 Year</option>
                    </select>
                </label>

                {/* ELI5 Toggle */}
                <label className="idw-field" style={{ flexDirection: "row", alignItems: "center", cursor: "pointer" }}>
                    <div style={{ position: "relative", width: "40px", height: "20px", background: eli5Mode ? "#10b981" : "#e5e7eb", borderRadius: "10px", transition: "0.3s" }}>
                        <div style={{ position: "absolute", top: "2px", left: eli5Mode ? "22px" : "2px", width: "16px", height: "16px", background: "white", borderRadius: "50%", transition: "0.3s", boxShadow: "0 1px 3px rgba(0,0,0,0.2)" }} />
                        <input type="checkbox" checked={eli5Mode} onChange={() => setEli5Mode(!eli5Mode)} style={{ opacity: 0, width: "100%", height: "100%", cursor: "pointer" }} />
                    </div>
                    <span style={{ marginLeft: "0.5rem", fontWeight: "bold", color: eli5Mode ? "#10b981" : "#6b7280" }}>
                        {eli5Mode ? "ELI5 Mode: ON" : "Simple Mode"}
                    </span>
                </label>


                <div style={{ alignSelf: "flex-end", paddingBottom: "0.5rem", fontSize: "0.9rem", color: "#666" }}>
                    Viewing Trend: {timeRange}
                </div>
            </section>

            {error && <p className="idw-error">{error}</p>}

            {/* Global Graph Explanation */}
            {
                timeSeriesData.explanation && (
                    <section className="idw-panel" style={{ marginTop: "1rem", marginBottom: "1.5rem", background: "linear-gradient(to right, #fdfbf7, #fff7ed)", border: "1px solid #fed7aa" }}>
                        <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                            <div style={{ fontSize: "1.5rem" }}>💡</div>
                            <div>
                                <h4 style={{ margin: "0 0 0.5rem 0", color: "#9a3412" }}>{eli5Mode ? "What is happening?" : "Trend Analysis"}</h4>
                                <p style={{ margin: 0, color: "#431407", fontStyle: "italic" }}>"{timeSeriesData.explanation}"</p>

                            </div>
                        </div>
                    </section>
                )
            }

            {/* Dashboard Grid for Vis */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginBottom: "1.5rem" }}>
                <DriftVelocityGauge
                    driftScore={timeSeriesData.trend && timeSeriesData.trend.length > 0 ? timeSeriesData.trend[timeSeriesData.trend.length - 1].avg_semantic_drift : 0}
                    title={eli5Mode ? "How fast is it changing?" : "Current Drift Velocity"}
                />
                <DriftHeatmap
                    trendData={timeSeriesData.trend || []}
                    title={eli5Mode ? "Daily Change Intensity" : "Drift Heatmap"}
                />
            </div>

            {/* Global Chart */}
            <DriftCharts timeSeriesData={timeSeriesData.trend || timeSeriesData} eli5={eli5Mode} />


            {/* Top Concept Shift Explanation */}
            {
                contextShift ? (
                    <section className="idw-panel" style={{ marginTop: "1.5rem" }}>
                        <header className="idw-panel-header" style={{ borderBottom: "1px solid #e5e7eb", paddingBottom: "1rem" }}>
                            <div>
                                <h3 style={{ color: "#db2777" }}>{eli5Mode ? "Biggest Meaning Shift" : "Top Context Shift"}: {contextShift.topic}</h3>
                                <p>{eli5Mode ? "This topic changed the most during this time." : `Most significant meaning change detected in this period (${contextShift.period}).`}</p>

                            </div>
                        </header>
                        <div className="idw-panel-body">
                            {contextShift.word_context && contextShift.word_context.map((item, i) => (
                                <div key={i} className="idw-comparison-row" style={{ marginBottom: "1rem", padding: "1rem", background: "#f9fafb", borderRadius: "8px" }}>
                                    <div style={{ marginBottom: "0.5rem", fontWeight: "bold" }}>
                                        "{item.word}" ({item.type === "rising" ? (eli5Mode ? "Becoming Popular" : "Rising") : (eli5Mode ? "Fading Away" : "Falling")})
                                    </div>

                                    {/* Generative Explanation */}
                                    {item.llm_explanation && (
                                        <div style={{ marginBottom: "1rem", padding: "0.75rem", background: "#fdf2f8", borderLeft: "4px solid #db2777", borderRadius: "4px", color: "#be185d", fontStyle: "italic" }}>
                                            {item.llm_explanation}
                                        </div>
                                    )}

                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", fontSize: "0.9rem" }}>

                                        <div style={{ background: "white", padding: "0.5rem", borderRadius: "4px", border: "1px solid #eee" }}>
                                            <span style={{ color: "#6b7280", fontSize: "0.75rem", textTransform: "uppercase" }}>Used to mean:</span>
                                            <ul style={{ paddingLeft: "1rem", margin: "0.5rem 0 0 0", color: "#4b5563" }}>
                                                {item.context_old.map((s, idx) => <li key={idx}>{s}</li>)}
                                            </ul>
                                        </div>

                                        <div style={{ background: "white", padding: "0.5rem", borderRadius: "4px", border: "1px solid #fce7f3" }}>
                                            <span style={{ color: "#db2777", fontSize: "0.75rem", textTransform: "uppercase" }}>{eli5Mode ? "Now means:" : "Now refers to:"}</span>
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
                )
            }

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

            {
                selectedTopic && (
                    <TopicModal
                        topic={selectedTopic}
                        onClose={() => setSelectedTopic(null)}
                        globalTrend={timeSeriesData.trend || []}
                    />
                )
            }

        </div >
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

export default TrendsPage;
