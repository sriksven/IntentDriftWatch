import { Routes, Route } from "react-router-dom";
import NavBar from "./components/NavBar";

import Dashboard from "./pages/Dashboard";
import ExplorePage from "./pages/ExplorePage";
import SettingsPage from "./pages/SettingsPage";

function App() {
  return (
    <div className="idw-root">
      <NavBar />

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </div>
  );
}

export default App;
