import React, { useState } from "react";
import Header from "./components/Header";
import Banner from "./components/Banner";
import ClassList from "./components/ClassList"; // Đã import chuẩn
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";
import "./App.css";

function App() {
  const [activeModal, setActiveModal] = useState(null);

  // Hàm bổ sung để khi bấm "Đăng ký nhận lớp" trong danh sách, nó tự bật modal login
  const handleClassApply = (cls) => {
    alert(
      `Bạn đang đăng ký nhận lớp ${cls.id} - ${cls.subject}. Vui lòng đăng nhập tài khoản gia sư!`,
    );
    setActiveModal("login");
  };

  return (
    <div
      className="app-container"
      style={{ fontFamily: "system-ui, sans-serif" }}
    >
      <Header
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
      />

      <Banner
        onFindTutorClick={() => setActiveModal("login")}
        onBeTutorClick={() => setActiveModal("register")}
      />

      {/* THAY THẾ ĐOẠN <main> CŨ BẰNG COMPONENT CLASSLIST Ở ĐÂY */}
      <ClassList onClassClick={handleClassApply} />

      {activeModal === "login" && (
        <LoginForm
          onClose={() => setActiveModal(null)}
          switchToRegister={() => setActiveModal("register")}
        />
      )}

      {activeModal === "register" && (
        <RegisterForm
          onClose={() => setActiveModal(null)}
          switchToLogin={() => setActiveModal("login")}
        />
      )}
    </div>
  );
}

export default App;