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

  useEffect(() => {
    async function loadHistory() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/topic_history/${encodeURIComponent(topic)}`);
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
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function num(v) {
  return v === undefined || v === null ? "—" : v.toFixed(3);
}
