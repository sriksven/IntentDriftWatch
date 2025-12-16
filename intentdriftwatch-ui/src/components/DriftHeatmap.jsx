import React from "react";

function DriftHeatmap({ trendData, title = "Drift Heatmap" }) {
    // trendData: [{ date: "YYYY-MM-DD", avg_semantic_drift: 0.05, ... }]

    // Find max for scaling
    const maxDrift = Math.max(...trendData.map(d => d.avg_semantic_drift || 0), 0.1);

    const getColor = (val) => {
        // 0 -> Green/Gray, Max -> Red
        // Simple interpolation
        const intensity = Math.min(val / 0.12, 1); // Cap at 0.12 for max red
        if (intensity < 0.3) return "#dcfce7"; // heavy green
        if (intensity < 0.5) return "#fef9c3"; // yellow
        if (intensity < 0.7) return "#fdba74"; // orange
        return "#f87171"; // red
    };

    const getTooltip = (d) => {
        return `${d.date}: ${(d.avg_semantic_drift * 100).toFixed(2)}% Shift`;
    };

    return (
        <div className="idw-panel">
            <h4 style={{ margin: "0 0 1rem 0", color: "#4b5563" }}>{title}</h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                {trendData.map((d, i) => (
                    <div
                        key={i}
                        title={getTooltip(d)}
                        style={{
                            width: "16px",
                            height: "16px",
                            backgroundColor: getColor(d.avg_semantic_drift),
                            borderRadius: "2px",
                            cursor: "pointer",
                            transition: "transform 0.1s"
                        }}
                        onMouseEnter={(e) => e.target.style.transform = "scale(1.2)"}
                        onMouseLeave={(e) => e.target.style.transform = "scale(1)"}
                    />
                ))}
            </div>
            <div style={{ marginTop: "0.5rem", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "#6b7280" }}>
                <span>Low</span>
                <div style={{ width: "40px", height: "8px", background: "linear-gradient(to right, #dcfce7, #f87171)" }} />
                <span>High Shift</span>
            </div>
        </div>
    );
}

export default DriftHeatmap;
