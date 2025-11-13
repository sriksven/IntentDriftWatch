import { useEffect, useState } from "react";

/* Settings */
const settings = JSON.parse(localStorage.getItem("idw-settings")) || {};
const API_BASE = settings.apiBaseUrl || "http://127.0.0.1:8000";
const REFRESH_MS = settings.refreshInterval || 30000; // not used here

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
    <div className="idw-main">
      <h1 className="idw-page-title">Explore Embeddings</h1>
      <p className="idw-page-subtitle">
        View embedding snapshots, metadata, and drift reports per topic.
      </p>

      {/* Topic Cards */}
      {loading ? (
        <p>Loading topics...</p>
      ) : (
        <div className="idw-explore-grid">
          {topics.length === 0 ? (
            <p>No topics found.</p>
          ) : (
            topics.map((topic, idx) => (
              <div
                key={idx}
                className={`idw-explore-card ${
                  selectedTopic === topic ? "active" : ""
                }`}
                onClick={() => loadTopicDetails(topic)}
              >
                <h3>{topic}</h3>
                <p>{dates.length} snapshot dates available</p>
              </div>
            ))
          )}
        </div>
      )}

      {/* Topic Details */}
      {selectedTopic && (
        <section className="idw-panel" style={{ marginTop: "2rem" }}>
          <header className="idw-panel-header">
            <h3>{selectedTopic}</h3>
            <p>Embedding snapshots across dates.</p>
          </header>

          <div className="idw-panel-body">
            {embInfo.length === 0 ? (
              <p>No embeddings recorded for this topic.</p>
            ) : (
              <table className="idw-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Path</th>
                    <th>Reports</th>
                  </tr>
                </thead>

                <tbody>
                  {embInfo.map((row, idx) => {
                    const BASE = import.meta.env.BASE_URL;

                    const topicKey = selectedTopic.replace(/ /g, "_");

                    return (
                      <tr key={idx}>
                        <td>{row.date}</td>
                        <td>{row.path}</td>

                        <td>
                          {/* Semantic Report */}
                          <a
                            href={`${BASE}drift_reports/semantic/${topicKey}_semantic_drift_${row.date}.html`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="idw-link"
                          >
                            Semantic
                          </a>

                          {" | "}

                          {/* Concept Report */}
                          <a
                            href={`${BASE}drift_reports/concept/${topicKey}_concept_drift_${row.date}.html`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="idw-link"
                          >
                            Concept
                          </a>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

export default ExplorePage;
