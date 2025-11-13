import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function DriftCharts({ semantic = [], concept = [] }) {
  // Prepare chart-friendly data
  const data = semantic.map((s, i) => ({
    name: s.topic,
    semantic: s.drift_score,
    concept: concept[i]?.statistic || 0,
  }));

  if (data.length === 0) {
    return (
      <div className="idw-panel" style={{ marginTop: "1rem" }}>
        <header className="idw-panel-header">
          <h3>Drift Chart</h3>
          <p>No drift data available.</p>
        </header>
      </div>
    );
  }

  return (
    <div className="idw-panel" style={{ marginTop: "1rem" }}>
      <header className="idw-panel-header">
        <h3>Drift Overview</h3>
        <p>Semantic vs Concept drift across topics</p>
      </header>

      <div className="idw-panel-body" style={{ height: "300px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />

            <Line type="monotone" dataKey="semantic" stroke="#4f46e5" strokeWidth={2} />
            <Line type="monotone" dataKey="concept" stroke="#e11d48" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
