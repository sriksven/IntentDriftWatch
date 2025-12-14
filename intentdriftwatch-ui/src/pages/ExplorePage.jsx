import { useEffect, useState } from "react";

/* Settings */
const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl
  ? settings.apiBaseUrl
  : window.location.hostname.includes("github.io")
    ? "https://intentdriftwatch.onrender.com"
    : "http://127.0.0.1:8000";

function ExplorePage() {
  const [topics, setTopics] = useState([]);
  const [dates, setDates] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [embInfo, setEmbInfo] = useState([]);
  const [loading, setLoading] = useState(true);

  /* Load global embedding metadata */
  useEffect(() => {
    async function loadInfo() {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/embeddings/info`);
        const json = await res.json();
        setTopics(json.topics || []);
        setDates(json.dates || []);
      } catch (err) {
        console.error("Failed to load embedding info:", err);
      }
      setLoading(false);
    }
    loadInfo();
  }, []);

  /* Load details for a topic */
  async function loadTopicDetails(topic) {
    if (selectedTopic === topic) {
      setSelectedTopic(null); // Toggle off
      return;
    }
    setSelectedTopic(topic);
    setEmbInfo([]);

    try {
      const res = await fetch(
        `${API_BASE}/embeddings/${encodeURIComponent(topic)}`
      );
      const json = await res.json();
      setEmbInfo(json.embeddings || []);
    } catch (err) {
      console.error("Failed to load topic embeddings:", err);
    }
  }

  return (
    <div className="idw-main animate-fade-in">
      <header className="idw-header-block">
        <h1 className="idw-page-title">Drift Analytics</h1>
        <p className="idw-page-subtitle">
          Deep dive into embedding trajectories and concept stability.
        </p>
      </header>

      {/* Hero Stats / Highlights */}
      <section className="idw-hero-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "1.5rem", marginBottom: "3rem" }}>
        <div className="idw-card-premium idw-gradient-1">
          <h3>Active Monitors</h3>
          <p className="idw-big-stat">{topics.length}</p>
          <span className="idw-stat-sub">Tracking intent drift</span>
        </div>
        <div className="idw-card-premium idw-gradient-2">
          <h3>Total Snapshots</h3>
          <p className="idw-big-stat">{dates.length * topics.length}</p>
          <span className="idw-stat-sub">Across time</span>
        </div>
        <div className="idw-card-premium idw-gradient-3">
          <h3>System Status</h3>
          <p className="idw-big-stat">Healthy</p>
          <span className="idw-stat-sub">Pipeline active</span>
        </div>
      </section>

      {/* Topic Grid */}
      <section>
        <h2 className="idw-section-title" style={{ fontSize: "1.2rem", fontWeight: "700", marginBottom: "1rem" }}>Topic Registry</h2>
        {loading ? (
          <div className="idw-loader-pulse">Scanning embeddings...</div>
        ) : (
          <div className="idw-explore-grid">
            {topics.length === 0 ? (
              <p>No topics found.</p>
            ) : (
              topics.map((topic, idx) => (
                <div
                  key={idx}
                  className={`idw-explore-card-modern ${selectedTopic === topic ? "active" : ""}`}
                  onClick={() => loadTopicDetails(topic)}
                >
                  <div className="idw-card-header">
                    <div className="idw-topic-icon">{topic[0]}</div>
                    <h3 style={{ margin: 0, fontSize: "1.1rem" }}>{topic}</h3>
                  </div>
                  <div className="idw-card-footer">
                    <span>{dates.length} Snapshots</span>
                    <span className="idw-action-arrow">→</span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </section>

      {/* Topic Details Panel (With Animation) */}
      {selectedTopic && (
        <section className="idw-panel-slide-up" style={{ marginTop: "2rem" }}>
          <header className="idw-panel-header">
            <div>
              <h3 style={{ margin: 0 }}>{selectedTopic} Analysis</h3>
              <p style={{ margin: 0, color: "#6b7280", fontSize: "0.9rem" }}>Historical snapshots and generated reports.</p>
            </div>
            <button className="idw-btn-ghost" onClick={() => setSelectedTopic(null)}>Close</button>
          </header>

          <div className="idw-panel-body">
            {embInfo.length === 0 ? (
              <p>Loading analytics...</p>
            ) : (
              <div className="idw-table-wrapper">
                <table className="idw-table-modern">
                  <thead>
                    <tr>
                      <th>Snapshot Date</th>
                      <th>Artifact Path</th>
                      <th>Deep Dive Reports</th>
                    </tr>
                  </thead>

                  <tbody>
                    {embInfo.map((row, idx) => {
                      const topicKey = selectedTopic.replace(/ /g, "_");
                      return (
                        <tr key={idx}>
                          <td><span className="idw-mono-date">{row.date}</span></td>
                          <td className="idw-mono-path" title={row.path}>
                            {row.path.split("/").pop()}
                          </td>

                          <td>
                            <div className="idw-actions-group">
                              <a
                                href={`${API_BASE}/drift_reports/visual/${topicKey}_semantic_drift_${row.date}.html`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="idw-btn-xs idw-btn-outline"
                              >
                                Semantic Report ↗
                              </a>
                              <a
                                href={`${API_BASE}/drift_reports/visual/${topicKey}_concept_drift_${row.date}.html`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="idw-btn-xs idw-btn-outline"
                              >
                                Concept Report ↗
                              </a>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default ExplorePage;
