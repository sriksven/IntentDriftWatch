// src/components/ThemeToggle.jsx
import { useTheme } from "../theme/useTheme";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      style={{
        padding: "0.6rem 1rem",
        borderRadius: "6px",
        border: "1px solid #555",
        background: "var(--card-bg)",
        color: "var(--text-primary)",
        cursor: "pointer",
      }}
    >
      {theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
    </button>
  );
}
