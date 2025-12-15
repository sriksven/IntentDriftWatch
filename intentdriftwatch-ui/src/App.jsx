import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";

import Dashboard from "./pages/Dashboard";
import TrendsPage from "./pages/TrendsPage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <div className="idw-root">
      <NavBar />

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/trends" element={<TrendsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </div>
  );
}

export default App;
