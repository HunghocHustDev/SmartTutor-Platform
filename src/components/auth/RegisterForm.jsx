import React, { useState } from "react";

export default function RegisterForm({ onClose, switchToLogin }) {
  // Sử dụng state để quản lý dữ liệu nhập vào
  const [role, setRole] = useState("student");
  const [phone, setPhone] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({
      fullName,
      email,
      password,
      phone,
      role,
    });
    alert(
      `Đăng ký thành công tài khoản ${role === "tutor" ? "Gia sư" : "Học viên"}!`,
    );
  };

  return (
    <div style={modalOverlayStyle}>
      <div style={modalContentStyle}>
        <button onClick={onClose} style={closeButtonStyle}>
          &times;
        </button>
        <h2
          style={{
            marginBottom: "25px",
            color: "#F97316",
            fontSize: "24px",
            textAlign: "center",
          }}
        >
          Đăng Ký Tài Khoản
        </h2>

        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "15px" }}
        >
          {/* 1. Các ô nhập thông tin cá nhân lên trước */}
          <input
            type="text"
            placeholder="Họ và tên"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            style={inputStyle}
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={inputStyle}
            required
          />

          <input
            type="tel"
            placeholder="Số điện thoại"
            pattern="[0-9]{10}"
            title="Số điện thoại phải gồm 10 chữ số"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            style={inputStyle}
            required
          />

          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={inputStyle}
            required
          />

          {/* 2. Phần chọn vai trò đã được đẩy xuống cuối cùng ở đây */}
          <div style={roleContainerStyle}>
            <label
              style={{
                fontWeight: "600",
                color: "#4B5563",
                marginRight: "10px",
              }}
            >
              Bạn là:
            </label>

            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="role"
                value="student"
                checked={role === "student"}
                onChange={() => setRole("student")}
                style={radioInputStyle}
              />
              Học viên / Phụ huynh
            </label>

            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="role"
                value="tutor"
                checked={role === "tutor"}
                onChange={() => setRole("tutor")}
                style={radioInputStyle}
              />
              Gia sư
            </label>
          </div>

          <button type="submit" style={btnSubmitStyle}>
            Đăng Ký
          </button>
        </form>

        <p
          style={{
            marginTop: "20px",
            fontSize: "14px",
            color: "#6B7280",
            textAlign: "center",
          }}
        >
          Đã có tài khoản?{" "}
          <span
            onClick={switchToLogin}
            style={{ color: "#1A56DB", cursor: "pointer", fontWeight: "bold" }}
          >
            Đăng nhập
          </span>
        </p>
      </div>
    </div>
  );
}

// Giữ nguyên bộ style CSS inline ổn định
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
  width: "420px",
  boxShadow: "0 4px 25px rgba(0,0,0,0.15)",
  position: "relative",
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
  fontSize: "15px",
  outline: "none",
  width: "100%",
  boxSizing: "border-box",
};

// CSS cho khu vực phân vai trò nằm cuối
const roleContainerStyle = {
  display: "flex",
  alignItems: "center",
  gap: "15px",
  marginTop: "5px",
  marginBottom: "5px",
  fontSize: "15px",
};
const radioLabelStyle = {
  display: "flex",
  alignItems: "center",
  gap: "6px",
  cursor: "pointer",
  color: "#374151",
};
const radioInputStyle = {
  width: "16px",
  height: "16px",
  cursor: "pointer",
  accentColor: "#F97316",
};

const btnSubmitStyle = {
  padding: "12px",
  backgroundColor: "#F97316",
  color: "white",
  border: "none",
  borderRadius: "6px",
  fontSize: "16px",
  fontWeight: "bold",
  cursor: "pointer",
  marginTop: "5px",
};
