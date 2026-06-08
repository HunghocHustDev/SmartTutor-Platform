import React from "react";

const HeaderLogo = () => (
  <div className="header-logo">
    <h1
      style={{
        fontSize: "28px",
        fontWeight: "bold",
        color: "#1A56DB",
        margin: 0,
      }}
    >
      GiaSư<span style={{ color: "#F97316" }}>TâmTâm</span>
    </h1>
  </div>
);

const HeaderNav = () => {
  const menuItems = [
    "Trang chủ",
    "Tìm gia sư",
    "Lớp mới tuyển",
    "Trở thành gia sư",
    "Giới thiệu",
  ];
  return (
    <nav className="header-nav" style={{ display: "flex", gap: "25px" }}>
      {menuItems.map((item, index) => (
        <a
          key={index}
          href={`#${item.toLowerCase().replace(/\s/g, "-")}`}
          style={{
            textDecoration: "none",
            color: "#4B5563",
            fontWeight: "500",
          }}
        >
          {item}
        </a>
      ))}
    </nav>
  );
};

// Nhận props từ cha truyền xuống để xử lý click
const HeaderActions = ({ onLoginClick, onRegisterClick }) => {
  return (
    <div className="header-actions" style={{ display: "flex", gap: "12px" }}>
      <button
        onClick={onLoginClick}
        style={{
          padding: "8px 16px",
          background: "none",
          border: "none",
          color: "#1A56DB",
          fontWeight: "600",
          cursor: "pointer",
        }}
      >
        Đăng nhập
      </button>
      <button
        onClick={onRegisterClick}
        style={{
          padding: "8px 18px",
          backgroundColor: "#1A56DB",
          color: "white",
          border: "none",
          borderRadius: "6px",
          fontWeight: "600",
          cursor: "pointer",
        }}
      >
        Đăng ký
      </button>
    </div>
  );
};

// Nhận hàm từ App.jsx và truyền tiếp xuống HeaderActions
export default function Header({ onLoginClick, onRegisterClick }) {
  return (
    <header
      className="main-header"
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "15px 40px",
        backgroundColor: "#ffffff",
        boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}
    >
      <HeaderLogo />
      <HeaderNav />
      <HeaderActions
        onLoginClick={onLoginClick}
        onRegisterClick={onRegisterClick}
      />
    </header>
  );
}
