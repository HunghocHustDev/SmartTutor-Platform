import React, { useState, useEffect } from "react";

import Header from "./components/Header";

import Banner from "./components/Banner";

import ClassList from "./components/ClassList";

import Workflow from "./components/Workflow";

import Footer from "./components/Footer";

import LoginForm from "./components/auth/LoginForm";

import RegisterForm from "./components/auth/RegisterForm";

// --- IMPORT CÁC TRANG DASHBOARD THEO ROLE ---

import StudentPage from "./pages/StudentPage";

import TutorPage from "./pages/TutorPage";

function App() {
  const [activeModal, setActiveModal] = useState(null);

  // 1. Quản lý Không không gian hiển thị tổng thể (Mặc định ban đầu ở trang chủ "home")

  const [activeTab, setActiveTab] = useState("home");

  // 2. State quản lý User tổng của cả ứng dụng

  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem("user")) || null;
  });

  // 3. Hàm đồng bộ trạng thái khi Đăng nhập / Đăng xuất thành công

  const handleUserChange = () => {
    const updatedUser = JSON.parse(localStorage.getItem("user")) || null;

    setCurrentUser(updatedUser);
  };

  // Tự động kiểm tra trạng thái bộ nhớ để điều phối không gian hiển thị khi tải trang hoặc đổi role

  useEffect(() => {
    if (currentUser) {
      // Nếu có user, tự động chuyển về không gian chuẩn của role đó

      setActiveTab(currentUser.role);
    } else {
      // Nếu không có user (đã đăng xuất), ép màn hình về trang chủ

      setActiveTab("home");
    }
  }, [currentUser]);

  // 4. Logic bẫy bảo mật (Role Guard) tự động kiểm tra quyền truy cập vùng chức năng

  useEffect(() => {
    if (
      activeTab === "student" &&
      (!currentUser || currentUser.role !== "student")
    ) {
      alert("⚠️ Bạn không có quyền truy cập không gian Học viên!");

      setActiveTab("home");
    }

    if (
      activeTab === "tutor" &&
      (!currentUser || currentUser.role !== "tutor")
    ) {
      alert("⚠️ Bạn không có quyền truy cập không gian Gia sư!");

      setActiveTab("home");
    }

    if (
      activeTab === "admin" &&
      (!currentUser || currentUser.role !== "admin")
    ) {
      alert("⚠️ Bạn không có quyền truy cập hệ thống Quản trị!");

      setActiveTab("home");
    }
  }, [activeTab, currentUser]);

  // 5. Hàm render nội dung linh hoạt dựa trên vùng `activeTab` tổng thể

  const renderContent = () => {
    // TRƯỜNG HỢP Ở TRANG CHỦ HOẶC KHÁCH VÃNG LAI

    if (activeTab === "home") {
      return (
        <>
          {/* Truyền key để Banner tự render lại lời chào chuẩn chỉ theo currentUser tổng */}

          <Banner
            key={currentUser?.role || "guest"}
            currentUser={currentUser}
            onFindTutorClick={() => setActiveModal("login")}
            onBeTutorClick={() => setActiveModal("register")}
          />

          <ClassList />

          <Workflow />
        </>
      );
    }

    // TRƯỜNG HỢP KHÔNG GIAN HỌC VIÊN (STUDENT DASHBOARD)

    if (activeTab === "student" && currentUser?.role === "student") {
      return <StudentPage currentUser={currentUser} />;
    }

    // TRƯỜNG HỢP KHÔNG GIAN GIA SƯ (TUTOR DASHBOARD)

    if (activeTab === "tutor" && currentUser?.role === "tutor") {
      return <TutorPage currentUser={currentUser} />;
    }

    // TRƯỜNG HỢP KHÔNG GIAN ADMIN

    if (activeTab === "admin" && currentUser?.role === "admin") {
      return (
        <div className="p-10 text-center font-bold text-xl text-red-600 min-h-[400px]">
          ⚙️ Giao diện Quản trị Trung tâm (Đang phát triển...)
        </div>
      );
    }

    // Mặc định dự phòng nếu không khớp tab nào

    return (
      <div className="p-10 text-center text-gray-500 min-h-[400px]">
        Trang không tồn tại hoặc bạn không có quyền.
      </div>
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Thanh Header dùng chung - Lắng nghe activeTab và re-render khi user thay đổi */}

      <Header
        key={currentUser ? `${currentUser.role}-${currentUser.name}` : "guest"}
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
        onUserChange={handleUserChange}
      />

      {/* Thân trang chiếm trọn không gian trống giữa Header và Footer */}

      <main className="flex-1 w-full flex flex-col">{renderContent()}</main>

      <Footer />

      {/* --- CÁC DIALOG/MODAL CHỨC NĂNG --- */}

      {activeModal === "login" && (
        <LoginForm
          onClose={() => setActiveModal(null)}
          switchToRegister={() => setActiveModal("register")}
          onLoginSuccess={() => {
            handleUserChange();

            setActiveModal(null);
          }}
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
