import { useEffect, useState } from "react";

function ThemeToggle() {
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  // Apply theme class to HTML tag
  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <div className="idw-toggle-container" onClick={toggleTheme}>
      <div className={`idw-toggle-slider ${theme === "dark" ? "active" : ""}`}>
        <div className="idw-toggle-knob"></div>
      </div>
    </div>
  );
}

export default ThemeToggle;



