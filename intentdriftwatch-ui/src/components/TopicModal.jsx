import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl || "http://127.0.0.1:8000";

export default function TopicModal({ topic, onClose }) {
  const [semanticTS, setSemanticTS] = useState([]);
  const [conceptTS, setConceptTS] = useState([]);
  const [loading, setLoading] = useState(true);

  const [driftDetails, setDriftDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  const analyzeDrift = async (index) => {
    if (index <= 0) return;
    const current = semanticTS[index];
    const prev = semanticTS[index - 1];

    setDriftDetails(null);
    setDetailsLoading(true);

    try {
      const url = `${API_BASE}/drift_details?topic=${encodeURIComponent(topic)}&old_date=${prev.date}&new_date=${current.date}`;
      const res = await fetch(url);
      const json = await res.json();
      setDriftDetails(json);
    } catch (e) {
      console.error("Drift details fetch failed:", e);
    }
    setDetailsLoading(false);
  };

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/topic/${encodeURIComponent(topic)}/history`);
        const json = await res.json();

        setSemanticTS(json.semantic || []);
        setConceptTS(json.concept || []);

      } catch (e) {
        console.error("Topic history fetch failed:", e);
      }
      setLoading(false);
    }
    loadHistory();
  }, [topic]);

  return (
    <div className="idw-modal-overlay" onClick={onClose}>
      <div className="idw-modal" onClick={(e) => e.stopPropagation()}>

        <button className="idw-modal-close" onClick={onClose}>×</button>
        <h3 className="idw-modal-title">{topic}</h3>
        <p className="idw-modal-subtitle">Historical drift analysis</p>

        {loading ? (
          <p>Loading...</p>
        ) : (
          <>
            <div className="idw-chart-block">
              <h4 className="idw-chart-title">Semantic Drift Over Time</h4>
              <div style={{ height: "250px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={semanticTS}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="drift_score" stroke="#4f46e5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="idw-chart-block">
              <h4 className="idw-chart-title">Concept Drift (Accuracy Drop)</h4>
              <div style={{ height: "250px" }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={conceptTS}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="accuracy_drop" stroke="#e11d48" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="idw-panel" style={{ marginTop: "1rem" }}>
              <h4 style={{ marginBottom: "0.5rem" }}>Latest Snapshot Metrics</h4>

              {semanticTS.length === 0 ? (
                <p>No drift history available.</p>
              ) : (
                <table className="idw-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Semantic Drift</th>
                      <th>Cosine</th>
                      <th>JSD</th>
                      <th>Concept Acc</th>
                      <th>Accuracy Drop</th>
                      <th>Context</th>
                    </tr>
                  </thead>

                  <tbody>
                    {semanticTS.map((s, i) => (
                      <tr key={i}>
                        <td>{s.date}</td>
                        <td>{num(s.drift_score)}</td>
                        <td>{num(s.cosine_drift)}</td>
                        <td>{num(s.jsd_drift)}</td>
                        <td>{conceptTS[i]?.test_acc ?? "—"}</td>
                        <td>{conceptTS[i]?.accuracy_drop ?? "—"}</td>
                        <td>
                          {i > 0 && (
                            <button
                              className="idw-btn-xs"
                              onClick={() => analyzeDrift(i)}
                            >
                              Analyze
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {detailsLoading && <div className="idw-panel">Loading analysis...</div>}

            {driftDetails && (
              <div className="idw-panel" style={{ marginTop: "1rem", borderTop: "1px solid #eee" }}>
                <h4 style={{ marginBottom: "1rem" }}>
                  Context Shift: {driftDetails.period}
                </h4>

                {driftDetails.word_context && driftDetails.word_context.length > 0 ? (
                  <div className="idw-context-comparison">
                    {driftDetails.word_context.map((item, i) => (
                      <div k={i} className="idw-comparison-row" style={{ marginBottom: "1.5rem", paddingBottom: "1.5rem", borderBottom: "1px solid #f0f0f0" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.5rem" }}>
                          <h5 style={{ fontSize: "1.1rem", margin: 0 }}>
                            <span className={item.type === "rising" ? "idw-tag-green" : "idw-tag-red"}>
                              {item.word}
                            </span>
                          </h5>
                          <span style={{ fontSize: "0.85rem", color: "#888" }}>
                            Shift Score: {item.score.toFixed(3)}
                          </span>
                        </div>

                        <div className="idw-grid-2" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                          {/* Old Context */}
                          <div className="idw-context-box" style={{ background: "#f9fafb", padding: "0.75rem", borderRadius: "6px" }}>
                            <h6 style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#6b7280", marginBottom: "0.5rem" }}>
                              Then (Old Context)
                            </h6>
                            {item.context_old.length > 0 ? (
                              <ul style={{ paddingLeft: "1rem", margin: 0, fontSize: "0.9rem", color: "#374151" }}>
                                {item.context_old.map((s, idx) => (
                                  <li key={idx} style={{ marginBottom: "0.25rem" }}>"{s}"</li>
                                ))}
                              </ul>
                            ) : (
                              <p style={{ fontSize: "0.85rem", color: "#9ca3af", fontStyle: "italic" }}>No usage found in old snapshot.</p>
                            )}
                          </div>

                          {/* New Context */}
                          <div className="idw-context-box" style={{ background: "#fdf2f8", padding: "0.75rem", borderRadius: "6px" }}>
                            <h6 style={{ fontSize: "0.75rem", textTransform: "uppercase", color: "#db2777", marginBottom: "0.5rem" }}>
                              Now (New Context)
                            </h6>
                            {item.context_new.length > 0 ? (
                              <ul style={{ paddingLeft: "1rem", margin: 0, fontSize: "0.9rem", color: "#374151" }}>
                                {item.context_new.map((s, idx) => (
                                  <li key={idx} style={{ marginBottom: "0.25rem" }}>"{s}"</li>
                                ))}
                              </ul>
                            ) : (
                              <p style={{ fontSize: "0.85rem", color: "#9ca3af", fontStyle: "italic" }}>No usage found in new snapshot.</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No significant context shift detected for this period.</p>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function num(v) {
  return v === undefined || v === null ? "—" : v.toFixed(3);
}
