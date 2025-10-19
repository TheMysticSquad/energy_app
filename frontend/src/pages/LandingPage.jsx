// src/pages/LandingPage.jsx
import React from 'react';
import Header from '../components/Header'; // Import the new Header component
import { Link } from 'react-router-dom'; // Assuming you will install react-router-dom

// Define the modules for easy rendering
const modules = [
  { name: 'Users', icon: '👤', path: '/users', description: 'Manage staff and customer access, roles, and permissions.' },
  { name: 'Consumers', icon: '🏠', path: '/consumers', description: 'Centralized customer accounts, service points, and contact information.' },
  { name: 'Metering', icon: '📏', path: '/metering', description: 'Device registration, installation records, and smart meter data ingestion (AMR).' },
  { name: 'Billing', icon: '💰', path: '/billing', description: 'Tariff plan management, usage calculation, and automated invoice generation.' },
  { name: 'Prepaid', icon: '💳', path: '/prepaid', description: 'Prepaid account balance tracking, voucher validation, and recharge processing.' },
  { name: 'Vendors', icon: '🤝', path: '/vendors', description: 'Integrate and audit third-party systems like payment gateways and AMISPs.' },
  { name: 'Notifications', icon: '🔔', path: '/notifications', description: 'System-wide alerts, SMS and email communication, and status updates.' },
];


const LandingPage = () => {
  return (
    <div className="landing-page-wrapper">
      <Header />
      
      <main className="landing-page-content">
        {/* --- Hero Section --- */}
        <section className="hero-section">
          <div className="hero-content">
            <h1>The Core System for Utility Operations.</h1>
            <p>Manage Customer Accounts, Metering, Billing, and Prepaid services all from one centralized platform.</p>
            <div className="hero-buttons">
              <Link to="/users" className="btn-primary btn-large">Explore Modules</Link>
              <a href="#" className="btn-secondary btn-large">System Docs</a>
            </div>
          </div>
          <div className="hero-image">
            CIS Dashboard Overview 💻
          </div>
        </section>

        {/* --- Modules Section (The Boxes) --- */}
        <section id="modules" className="modules-section">
          <h2>Utility CIS Application Modules</h2>
          <div className="module-grid">
            {modules.map((module) => (
              <Link to={module.path} key={module.name} className="module-card">
                <span className="module-icon">{module.icon}</span>
                <h3>{module.name}</h3>
                <p>{module.description}</p>
              </Link>
            ))}
          </div>
        </section>
      </main>

      {/* --- Footer Component --- */}
      <footer className="utility-footer">
        <p>&copy; 2024 Utility CIS. All rights reserved. | Built with Django & React</p>
      </footer>
    </div>
  );
};

export default LandingPage;