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
                    <tr>
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
          </>
        )}

        {detailsLoading && <div className="idw-panel">Loading analysis...</div>}

        {driftDetails && (
          <div className="idw-panel" style={{ marginTop: "1rem", borderTop: "1px solid #eee" }}>
            <h4 style={{ marginBottom: "1rem" }}>
              Word Drift: {driftDetails.period}
            </h4>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
              <div>
                <h5 style={{ color: "#059669", marginBottom: "0.5rem" }}>Trending Up ↗</h5>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {driftDetails.rising.map((w, i) => (
                    <span key={i} className="idw-tag-green" title={`Score: ${w.score.toFixed(4)}`}>
                      {w.word}
                    </span>
                  ))}
                  {driftDetails.rising.length === 0 && <span style={{ color: "#999", fontSize: "0.9em" }}>No significant changes</span>}
                </div>
              </div>
              <div>
                <h5 style={{ color: "#dc2626", marginBottom: "0.5rem" }}>Trending Down ↘</h5>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {driftDetails.falling.map((w, i) => (
                    <span key={i} className="idw-tag-red" title={`Score: ${w.score.toFixed(4)}`}>
                      {w.word}
                    </span>
                  ))}
                  {driftDetails.falling.length === 0 && <span style={{ color: "#999", fontSize: "0.9em" }}>No significant changes</span>}
                </div>
              </div>
            </div>

            {driftDetails.snippets.length > 0 && (
              <div>
                <h5 style={{ marginBottom: "0.5rem" }}>Context Snippets (New)</h5>
                <ul style={{ paddingLeft: "1.2rem", fontSize: "0.9rem", color: "#555" }}>
                  {driftDetails.snippets.map((s, i) => (
                    <li key={i} style={{ marginBottom: "0.5rem" }}>
                      "{s.text}" <span style={{ color: "#059669", fontWeight: "bold" }}>[{s.keyword}]</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}

function num(v) {
  return v === undefined || v === null ? "—" : v.toFixed(3);
}
