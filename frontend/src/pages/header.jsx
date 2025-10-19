// src/components/Header.jsx
import React from 'react';
// Assuming you will import the main stylesheet in App.jsx or index.js

const Header = () => {
  return (
    <header className="utility-header">
      <div className="header-logo">
        <span className="logo-text">⚡ Utility CIS</span>
      </div>
      
      {/* Login Status/Details Area */}
      <div className="login-details">
        <p>Welcome, **Guest User**</p>
        <a href="/login">System Login</a>
      </div>
    </header>
  );
};

export default Header;