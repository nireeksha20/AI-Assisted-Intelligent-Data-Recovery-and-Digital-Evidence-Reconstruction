import { useEffect, useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";

import "./App.css";

function App() {
  // One theme for the whole application
  const [theme, setTheme] = useState(
    localStorage.getItem("theme") || "light"
  );

  // Save theme and apply it globally
  useEffect(() => {
    localStorage.setItem("theme", theme);

    document.documentElement.setAttribute(
      "data-theme",
      theme
    );
  }, [theme]);

  return (
    <BrowserRouter>
      <Routes>

        {/* HOME */}
        <Route
          path="/"
          element={
            <Home
              theme={theme}
              setTheme={setTheme}
            />
          }
        />

        {/* LOGIN */}
        <Route
          path="/login"
          element={
            <Login
              theme={theme}
              setTheme={setTheme}
            />
          }
        />

        {/* SIGNUP */}
        <Route
          path="/signup"
          element={
            <Signup
              theme={theme}
              setTheme={setTheme}
            />
          }
        />

        {/* DASHBOARD */}
        <Route
          path="/dashboard"
          element={
            <Dashboard
              theme={theme}
              setTheme={setTheme}
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;