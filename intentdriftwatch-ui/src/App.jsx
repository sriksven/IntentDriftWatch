import { useState, useEffect } from "react";
import axios from "axios";
import { API_BASE } from "./config";

function App() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_BASE}/latest_summary`);
        if (res.data && res.data.rows) {
          // Only update if valid data returned
          setSummary(res.data);
        }
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };

    fetchData(); // initial fetch
    const interval = setInterval(fetchData, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif" }}>
      <h1>IntentDriftWatch Dashboard</h1>
      <h3>Live Summary from Backend</h3>

      {!summary ? (
        <p>Loading drift summary...</p>
      ) : summary.rows.length === 0 ? (
        <p>No data available yet.</p>
      ) : (
        <table
          border="1"
          cellPadding="8"
          style={{ marginTop: "1rem", borderCollapse: "collapse" }}
        >
          <thead style={{ backgroundColor: "#f0f0f0" }}>
            <tr>
              <th>Topic</th>
              <th>Semantic Status</th>
              <th>Semantic Score</th>
              <th>Concept Status</th>
              <th>Accuracy Drop</th>
            </tr>
          </thead>
          <tbody>
            {summary.rows.map((r) => (
              <tr key={r.topic}>
                <td>{r.topic}</td>
                <td>{r.semantic_status}</td>
                <td>{r.semantic_score?.toFixed(3)}</td>
                <td>{r.concept_status}</td>
                <td>{r.accuracy_drop?.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
