import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import PreferencesPage from "./components/PreferencesPage";
import MainPage from "./pages/MainPage";
import DashboardPage from "./pages/DashboardPage";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/preferences" element={<PreferencesPage />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
