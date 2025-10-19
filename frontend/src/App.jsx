import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Footer from "./components/Footer";

// Pages
import LandingPage from "./pages/LandingPage";
import Users from "./pages/Users";
import Consumers from "./pages/Consumers";
import Metering from "./pages/Metering";
import Billing from "./pages/Billing";
import Prepaid from "./pages/Prepaid";
import Vendors from "./pages/Vendors";
import Notifications from "./pages/Notifications";
import Login from "./pages/Login";

import "./styles/main.css";

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/users" element={<Users />} />
            <Route path="/consumers" element={<Consumers />} />
            <Route path="/metering" element={<Metering />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/prepaid" element={<Prepaid />} />
            <Route path="/vendors" element={<Vendors />} />
            <Route path="/notifications" element={<Notifications />} />
          </Routes>
          <Footer />
        </main>
      </div>
    </Router>
  );
}

export default App;
