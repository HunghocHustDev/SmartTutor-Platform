import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

export default function LoginForm({ onClose, switchToRegister }) {
  const { loginWithCredentials } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await loginWithCredentials(email, password);
      onClose();
    } catch (err) {
      setError(err?.message || "Đăng nhập thất bại");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={modalOverlayStyle}>
      <div style={modalContentStyle}>
        <button onClick={onClose} style={closeButtonStyle}>
          &times;
        </button>
        <h2 style={{ marginBottom: "20px", color: "#1A56DB" }}>Đăng Nhập Gia Sư / Học Viên</h2>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "15px" }}>
          <input
            type="email"
            placeholder="Email đăng nhập"
            style={inputStyle}
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            style={inputStyle}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <div style={{ color: "#DC2626", fontSize: "14px" }}>{error}</div>}
          <button type="submit" style={btnSubmitStyle} disabled={loading}>
            {loading ? "Đang đăng nhập..." : "Đăng Nhập"}
          </button>
        </form>
        <p style={{ marginTop: "15px", fontSize: "14px", color: "#6B7280" }}>
          Chưa có tài khoản?{" "}
          <span
            onClick={switchToRegister}
            style={{ color: "#F97316", cursor: "pointer", fontWeight: "bold" }}
          >
            Đăng ký ngay
          </span>
        </p>
      </div>
    </div>
  );
}

const modalOverlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};
const modalContentStyle = {
  backgroundColor: "#fff",
  padding: "40px",
  borderRadius: "12px",
  width: "400px",
  boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
  position: "relative",
  textAlign: "center",
};
const closeButtonStyle = {
  position: "absolute",
  top: "10px",
  right: "15px",
  background: "none",
  border: "none",
  fontSize: "24px",
  cursor: "pointer",
  color: "#9CA3AF",
};
const inputStyle = {
  padding: "12px",
  border: "1px solid #D1D5DB",
  borderRadius: "6px",
  fontSize: "16px",
  outline: "none",
};
const btnSubmitStyle = {
  padding: "12px",
  backgroundColor: "#1A56DB",
  color: "white",
  border: "none",
  borderRadius: "6px",
  fontSize: "16px",
  fontWeight: "bold",
  cursor: "pointer",
  opacity: 1,
};
