import { useState, useEffect } from "react";
import { useTheme } from "../theme/ThemeContext";
import ThemeToggle from "../components/ThemeToggle";

const DEFAULT_SETTINGS = {
  apiBaseUrl: "http://127.0.0.1:8000",
  refreshInterval: 30000,
};

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();

  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem("idw-settings");
    return saved ? JSON.parse(saved) : DEFAULT_SETTINGS;
  });

  const [apiBaseUrl, setApiBaseUrl] = useState(settings.apiBaseUrl);
  const [refreshInterval, setRefreshInterval] = useState(settings.refreshInterval);

  useEffect(() => {
    localStorage.setItem(
      "idw-settings",
      JSON.stringify({ apiBaseUrl, refreshInterval })
    );
  }, [apiBaseUrl, refreshInterval]);

  return (
    <div style={{ padding: "2rem" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Settings</h1>

      {/* API URL */}
      <section style={{ marginBottom: "2rem" }}>
        <h2>Backend API URL</h2>
        <p>This is where the dashboard fetches data from.</p>

        <input
          type="text"
          value={apiBaseUrl}
          onChange={(e) => setApiBaseUrl(e.target.value)}
          style={{
            width: "100%",
            padding: "0.6rem",
            marginTop: "0.6rem",
            borderRadius: "6px",
            border: "1px solid #555",
            background: "var(--card-bg)",
            color: "var(--text-primary)",
          }}
        />
      </section>

      {/* Refresh Interval */}
      <section style={{ marginBottom: "2rem" }}>
        <h2>Auto Refresh Interval</h2>
        <p>How often dashboard data should refresh.</p>

        <select
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}
          style={{
            padding: "0.6rem",
            marginTop: "0.6rem",
            borderRadius: "6px",
            border: "1px solid #555",
            background: "var(--card-bg)",
            color: "var(--text-primary)",
          }}
        >
          <option value={10000}>10 seconds</option>
          <option value={30000}>30 seconds</option>
          <option value={60000}>1 minute</option>
        </select>
      </section>

      {/* Theme */}
      <section style={{ marginBottom: "2rem" }}>
        <h2>Theme</h2>
        <p>Toggle dark or light mode.</p>
        <ThemeToggle />

      </section>
    </div>
  );
}
