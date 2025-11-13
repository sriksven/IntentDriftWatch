import { useTheme } from "../theme/ThemeContext";

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="idw-toggle-container" onClick={toggleTheme}>
      <div className={`idw-toggle-slider ${theme === "dark" ? "active" : ""}`}>
        <div className="idw-toggle-knob"></div>
      </div>
    </div>
  );
}

export default ThemeToggle;
