import React, { useMemo, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

export default function RegisterForm({ onClose, switchToLogin }) {
  const { registerAccount } = useAuth();
  const [role, setRole] = useState("student");
  const [form, setForm] = useState({
    fullName: "",
    email: "",
    phone: "",
    password: "",
    area: "",
    level: "",
    university: "",
    major: "",
    experience: "0",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const roleLabel = useMemo(
    () => (role === "student" ? "Học viên / Phụ huynh" : "Gia sư"),
    [role]
  );

  const updateField = (key) => (e) => {
    setForm((prev) => ({
      ...prev,
      [key]: e.target.value,
    }));
  };

  const handleRoleChange = (nextRole) => {
    setRole(nextRole);
    setError("");
    setSuccess("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        full_name: form.fullName.trim(),
        email: form.email.trim(),
        password: form.password,
        phone: form.phone.trim(),
        role,
        area: form.area.trim(),
      };

      if (role === "student") {
        payload.level = form.level.trim();
      } else {
        payload.university = form.university.trim();
        payload.major = form.major.trim();
        payload.experience = Number(form.experience || 0);
      }

      await registerAccount(payload);
      setSuccess("Đăng ký thành công. Đăng nhập tự động...");
      setTimeout(() => {
        onClose();
      }, 400);
    } catch (err) {
      setError(err?.message || "Đăng ký thất bại");
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
        <h2 style={titleStyle}>Đăng Ký Tài Khoản</h2>
        <p style={subtitleStyle}>Hoàn thiện thông tin cho {roleLabel.toLowerCase()}</p>
        <form onSubmit={handleSubmit} style={formStyle}>
          <input
            type="text"
            placeholder="Họ và tên"
            value={form.fullName}
            onChange={updateField("fullName")}
            style={inputStyle}
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={updateField("email")}
            style={inputStyle}
            required
          />
          <input
            type="tel"
            placeholder="Số điện thoại"
            pattern="[0-9]{10}"
            title="Số điện thoại phải gồm 10 chữ số"
            value={form.phone}
            onChange={updateField("phone")}
            style={inputStyle}
            required
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            value={form.password}
            onChange={updateField("password")}
            style={inputStyle}
            required
          />

          <div style={roleContainerStyle}>
            <label style={roleTitleStyle}>Bạn là:</label>
            <label style={radioLabelStyle}>
              <input
                type="radio"
                name="role"
                value="student"
                checked={role === "student"}
                onChange={() => handleRoleChange("student")}
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
                onChange={() => handleRoleChange("tutor")}
                style={radioInputStyle}
              />
              Gia sư
            </label>
          </div>

          <input
            type="text"
            placeholder="Khu vực"
            value={form.area}
            onChange={updateField("area")}
            style={inputStyle}
            required
          />

          {role === "student" ? (
            <input
              type="text"
              placeholder="Trình độ / Lớp hiện tại"
              value={form.level}
              onChange={updateField("level")}
              style={inputStyle}
              required
            />
          ) : (
            <>
              <input
                type="text"
                placeholder="Trường đại học"
                value={form.university}
                onChange={updateField("university")}
                style={inputStyle}
                required
              />
              <input
                type="text"
                placeholder="Chuyên ngành"
                value={form.major}
                onChange={updateField("major")}
                style={inputStyle}
                required
              />
              <input
                type="number"
                placeholder="Số năm kinh nghiệm"
                min="0"
                value={form.experience}
                onChange={updateField("experience")}
                style={inputStyle}
                required
              />
            </>
          )}

          {error && <div style={errorStyle}>{error}</div>}
          {success && <div style={successStyle}>{success}</div>}

          <button type="submit" style={btnSubmitStyle} disabled={loading}>
            {loading ? "Đang đăng ký..." : "Đăng Ký"}
          </button>
        </form>
        <p style={footerTextStyle}>
          Đã có tài khoản?{" "}
          <span onClick={switchToLogin} style={switchLinkStyle}>
            Đăng nhập
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
  padding: "32px",
  borderRadius: "12px",
  width: "440px",
  maxWidth: "92vw",
  boxShadow: "0 4px 25px rgba(0,0,0,0.15)",
  position: "relative",
};

const titleStyle = {
  marginBottom: "8px",
  color: "#F97316",
  fontSize: "24px",
  textAlign: "center",
};

const subtitleStyle = {
  marginTop: 0,
  marginBottom: "20px",
  color: "#6B7280",
  fontSize: "14px",
  textAlign: "center",
};

const formStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "14px",
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

const roleContainerStyle = {
  display: "flex",
  alignItems: "center",
  gap: "14px",
  marginTop: "2px",
  marginBottom: "2px",
  fontSize: "15px",
  flexWrap: "wrap",
};

const roleTitleStyle = {
  fontWeight: "600",
  color: "#4B5563",
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

const errorStyle = {
  color: "#DC2626",
  fontSize: "14px",
};

const successStyle = {
  color: "#15803D",
  fontSize: "14px",
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
  marginTop: "4px",
};

const footerTextStyle = {
  marginTop: "18px",
  fontSize: "14px",
  color: "#6B7280",
  textAlign: "center",
};

const switchLinkStyle = {
  color: "#1A56DB",
  cursor: "pointer",
  fontWeight: "bold",
};
