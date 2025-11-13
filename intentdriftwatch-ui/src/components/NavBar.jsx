import { Link, useLocation } from "react-router-dom";
import ThemeToggle from "../theme/ThemeProvider";

function NavBar() {
  const { pathname } = useLocation();

  return (
    <nav className="idw-navbar">
      <div className="idw-nav-left">
        <h2 className="idw-nav-title">IntentDriftWatch</h2>

        <Link
          to="/"
          className={`idw-nav-item ${pathname === "/" ? "active" : ""}`}
        >
          Dashboard
        </Link>

        <Link
          to="/explore"
          className={`idw-nav-item ${
            pathname === "/explore" ? "active" : ""
          }`}
        >
          Explore
        </Link>

        <Link
          to="/settings"
          className={`idw-nav-item ${
            pathname === "/settings" ? "active" : ""
          }`}
        >
          Settings
        </Link>
      </div>

      <div className="idw-nav-right">
        <ThemeToggle />
      </div>
    </nav>
  );
}

export default NavBar;
