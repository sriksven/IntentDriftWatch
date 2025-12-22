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
const API_BASE = settings.apiBaseUrl
  ? settings.apiBaseUrl
  : window.location.hostname.includes("github.io")
    ? "https://intentdriftwatch.onrender.com"
    : "http://127.0.0.1:8000";

export default function TopicModal({ topic, onClose }) {
  const [semanticTS, setSemanticTS] = useState([]);
  const [conceptTS, setConceptTS] = useState([]);
  const [loading, setLoading] = useState(true);

  const [driftDetails, setDriftDetails] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [selectedIdx, setSelectedIdx] = useState(0);

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
        if (json.semantic && json.semantic.length > 0) {
          setSelectedIdx(json.semantic.length - 1);
        }

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

            {/* Time Travel Scrubber */}
            <div className="idw-panel" style={{ marginTop: "1rem", background: "linear-gradient(to bottom, #f8fafc, #fff)", border: "1px solid #e2e8f0" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h4 style={{ margin: 0, color: "#1e293b" }}>🕰 Time Travel Analysis</h4>
                {semanticTS.length > 0 && selectedIdx > 0 && (
                  <span style={{ fontSize: "0.9rem", color: "#64748b", background: "#f1f5f9", padding: "0.2rem 0.6rem", borderRadius: "12px" }}>
                    Comparing: <strong>{semanticTS[selectedIdx - 1].date}</strong> vs <strong>{semanticTS[selectedIdx].date}</strong>
                  </span>
                )}
              </div>

              {semanticTS.length < 2 ? (
                <p>Insufficient history for time travel.</p>
              ) : (
                <div style={{ padding: "0 1rem" }}>
                  {/* Slider */}
                  <input
                    type="range"
                    min="1"
                    max={semanticTS.length - 1}
                    value={selectedIdx}
                    onChange={(e) => {
                      const idx = parseInt(e.target.value);
                      setSelectedIdx(idx);
                    }}
                    style={{ width: "100%", cursor: "pointer", accentColor: "#4f46e5" }}
                  />

                  {/* Date Labels below Slider */}
                  <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.5rem", fontSize: "0.8rem", color: "#94a3b8" }}>
                    <span>{semanticTS[0]?.date}</span>
                    <span>{semanticTS[semanticTS.length - 1]?.date}</span>
                  </div>

                  <div style={{ textAlign: "center", marginTop: "1.5rem" }}>
                    <div style={{ fontSize: "2.5rem", fontWeight: "900", color: "#4f46e5", lineHeight: "1" }}>
                      {semanticTS[selectedIdx]?.date}
                    </div>
                    <div style={{ color: "#64748b", marginTop: "0.5rem" }}>
                      Drift Score: <span style={{ color: "#0f172a", fontWeight: "bold" }}>{num(semanticTS[selectedIdx]?.drift_score)}</span>
                    </div>

                    <button
                      className="idw-btn"
                      style={{ marginTop: "1.5rem", padding: "0.75rem 2rem", fontSize: "1.1rem" }}
                      onClick={() => analyzeDrift(selectedIdx)}
                      disabled={detailsLoading}
                    >
                      {detailsLoading ? "Analyzing..." : "Analyze Context Shift ✨"}
                    </button>
                  </div>
                </div>
              )}
            </div>

            {detailsLoading && <div className="idw-panel">Generating plain english explanation...</div>}

            {driftDetails && (
              <div className="idw-panel" style={{ marginTop: "1rem", borderTop: "1px solid #eee", background: "#fff" }}>
                <h4 style={{ marginBottom: "1rem", color: "#111827", fontSize: "1.2rem" }}>
                  🔍 What Changed? (Common Man Explanation)
                </h4>
                <p style={{ marginBottom: "1.5rem", color: "#6b7280" }}>
                  Analyzing usage shift from <strong>{driftDetails.period.split("->")[0]}</strong> to <strong>{driftDetails.period.split("->")[1]}</strong>.
                </p>

                {driftDetails.word_context && driftDetails.word_context.length > 0 ? (
                  <div className="idw-context-comparison">
                    {driftDetails.word_context.map((item, i) => (
                      <div k={i} className="idw-comparison-row" style={{ marginBottom: "1.5rem", padding: "1.5rem", background: "#f8fafc", borderRadius: "12px" }}>
                        <div style={{ marginBottom: "1rem" }}>
                          <span style={{ fontSize: "1.1rem", fontWeight: "bold", marginRight: "0.5rem" }}>
                            The word "{item.word}"
                          </span>
                          <span className={item.type === "rising" ? "idw-tag-green" : "idw-tag-red"}>
                            {item.type === "rising" ? "became more frequent" : "became less frequent"}
                          </span>
                        </div>


                        {item.llm_explanation && (
                          <div style={{ marginBottom: "1rem", padding: "1rem", background: "#eff6ff", borderRadius: "8px", borderLeft: "4px solid #3b82f6", color: "#1e3a8a" }}>
                            <div style={{ fontWeight: "bold", marginBottom: "0.25rem", textTransform: "uppercase", fontSize: "0.75rem", letterSpacing: "0.05em", color: "#3b82f6" }}>
                              AI Summary
                            </div>
                            {item.llm_explanation}
                          </div>
                        )}

                        <details>
                          <summary style={{ cursor: "pointer", color: "#6b7280", marginBottom: "1rem", fontSize: "0.9rem", userSelect: "none" }}>
                            View Raw Context Snippets (Evidence)
                          </summary>

                          <div className="idw-narrative-grid" style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", gap: "1rem", alignItems: "center" }}>

                            {/* Old Context */}
                            <div className="idw-context-box" style={{ background: "white", padding: "1rem", borderRadius: "8px", border: "1px solid #e5e7eb" }}>
                              <div style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "#6b7280", marginBottom: "0.5rem", fontWeight: "bold" }}>
                                Used to mean:
                              </div>
                              {item.context_old.length > 0 ? (
                                <ul style={{ paddingLeft: "1.2rem", margin: 0, fontSize: "0.95rem", color: "#374151" }}>
                                  {item.context_old.map((s, idx) => (
                                    <li key={idx} style={{ marginBottom: "0.4rem" }}>"{s}"</li>
                                  ))}
                                </ul>
                              ) : (
                                <p style={{ fontStyle: "italic", color: "#9ca3af" }}>Rarely used in this context previously.</p>
                              )}
                            </div>

                            {/* Arrow */}
                            <div style={{ fontSize: "2rem", color: "#9ca3af", textAlign: "center" }}>
                              ➝
                            </div>

                            {/* New Context */}
                            <div className="idw-context-box" style={{ background: "white", padding: "1rem", borderRadius: "8px", border: "1px solid #e5e7eb", borderColor: "#f472b6" }}>
                              <div style={{ fontSize: "0.85rem", textTransform: "uppercase", color: "#db2777", marginBottom: "0.5rem", fontWeight: "bold" }}>
                                Now refers to:
                              </div>
                              {item.context_new.length > 0 ? (
                                <ul style={{ paddingLeft: "1.2rem", margin: 0, fontSize: "0.95rem", color: "#374151" }}>
                                  {item.context_new.map((s, idx) => (
                                    <li key={idx} style={{ marginBottom: "0.4rem" }}>"{s}"</li>
                                  ))}
                                </ul>
                              ) : (
                                <p style={{ fontStyle: "italic", color: "#9ca3af" }}>Usage has faded in current context.</p>
                              )}
                            </div>

                          </div>
                        </details>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No significant change in word meaning detected for this period.</p>
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
