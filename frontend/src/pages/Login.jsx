import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === "admin" && password === "admin123") {
      navigate("/");
    } else {
      alert("Invalid credentials");
    }
  };

  return (
    <div className="login-page">
      <h2>🔑 System Login</h2>
      <form onSubmit={handleLogin}>
        <label>Username</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} required />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" className="btn-primary">
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;
