import React from "react";

function DriftVelocityGauge({ driftScore, title = "Drift Velocity" }) {
    // Score 0.0 to 0.2 (typical range)
    // We'll normalize 0.15 as "Red Line" (Max velocity)
    const MAX_VAL = 0.15;
    const normalized = Math.min(driftScore / MAX_VAL, 1); // 0 to 1
    const angle = normalized * 180; // 0 to 180 degrees

    // SVG Arch
    const radius = 80;
    const stroke = 15;
    const cx = 100;
    const cy = 100;

    // Calculate pointer position
    const radians = (angle - 180) * (Math.PI / 180);
    const x = cx + radius * Math.cos(radians);
    const y = cy + radius * Math.sin(radians);

    return (
        <div className="idw-panel" style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
            <h4 style={{ margin: "0 0 1rem 0", color: "#4b5563" }}>{title}</h4>
            <div style={{ position: "relative", width: "200px", height: "110px", overflow: "hidden" }}>
                <svg width="200" height="200" viewBox="0 0 200 200">
                    {/* Background Arch */}
                    <circle
                        cx={cx}
                        cy={cy}
                        r={radius}
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth={stroke}
                        strokeDasharray={`${Math.PI * radius} ${Math.PI * radius}`}
                        strokeDashoffset={0}
                        transform={`rotate(180 ${cx} ${cy})`}
                    />
                    {/* Color Gradient Defs */}
                    <defs>
                        <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#22c55e" />
                            <stop offset="50%" stopColor="#eab308" />
                            <stop offset="100%" stopColor="#ef4444" />
                        </linearGradient>
                    </defs>

                    {/* Filled Arch (Masked manually or simplified) */}
                    {/* Actually, simple gauge arch with dashoffset is easier for value */}
                    <circle
                        cx={cx}
                        cy={cy}
                        r={radius}
                        fill="none"
                        stroke="url(#gaugeGrad)"
                        strokeWidth={stroke}
                        strokeDasharray={`${Math.PI * radius} ${Math.PI * radius}`}
                        strokeDashoffset={Math.PI * radius * (1 - normalized)}
                        strrokeLinecap="round"
                        transform={`rotate(180 ${cx} ${cy})`}
                    />

                    {/* Needle */}
                    <line x1={cx} y1={cy} x2={x} y2={y} stroke="#374151" strokeWidth="4" />
                    <circle cx={cx} cy={cy} r="6" fill="#374151" />
                </svg>

                <div style={{ position: "absolute", bottom: "0", left: "0", right: "0", display: "flex", justifyContent: "space-between", padding: "0 20px", fontSize: "0.8rem", color: "#9ca3af" }}>
                    <span>Stable</span>
                    <span>Volatile</span>
                </div>
            </div>
            <div style={{ fontSize: "2rem", fontWeight: "bold", marginTop: "-10px", color: normalized > 0.6 ? "#ef4444" : "#374151" }}>
                {(driftScore * 100).toFixed(1)}
                <span style={{ fontSize: "1rem", color: "#9ca3af", fontWeight: "normal" }}>%</span>
            </div>
        </div>
    );
}

export default DriftVelocityGauge;
