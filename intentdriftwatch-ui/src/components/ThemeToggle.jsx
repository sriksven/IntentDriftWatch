import { useTheme } from "../theme/useTheme";


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
