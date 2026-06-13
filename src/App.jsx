import React, { useState, useEffect } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

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

// --- IMPORT 4 TRANG CON HỌC VIÊN (ĐÃ ĐỒNG BỘ CHỮ 'S' VỚI HEADER) ---
import StudentRequests from "./components/student/StudentRequests";
import StudentClasses from "./components/student/StudentClasses";
import StudentSchedule from "./components/student/StudentSchedule";
import StudentTuition from "./components/student/StudentTuition";

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeModal, setActiveModal] = useState(null);

  // State quản lý User tổng của cả ứng dụng (Lazy Initialization để tối ưu hiệu năng)
  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem("user")) || null;
  });

  // Hàm đồng bộ trạng thái khi đăng nhập/đăng xuất thành công
  const handleUserChange = (newUser) => {
    setCurrentUser(newUser);
  };

  // Tự động điều hướng URL khi user thay đổi trạng thái
  useEffect(() => {
    if (currentUser) {
      // Nếu user đang ở trang chủ, tự động đẩy vào không gian làm việc của vai trò đó
      if (location.pathname === "/") {
        if (currentUser.role === "student") navigate("/student/requests");
        else if (currentUser.role === "tutor") navigate("/tutor/classes");
        else if (currentUser.role === "admin") navigate("/admin/dashboard");
      }
    }
  }, [currentUser, location.pathname, navigate]);

  // View Trang chủ công khai (Dành cho khách vãng lai)
  const HomeView = (
    <>
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

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* ĐÃ DỌN SẠCH: Bỏ hoàn toàn activeTab và onTabChange.
        Header bây giờ sẽ tự động sáng xanh dựa trên URL trình duyệt.
      */}
      <Header
        currentUser={currentUser}
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
        onUserChange={handleUserChange}
      />

      {/* THÂN TRANG QUẢN LÝ ĐỊNH TUYẾN URL */}
      <main className="flex-1 w-full flex flex-col">
        <Routes>
          {/* TRANG CHỦ CÔNG KHAI */}
          <Route path="/" element={HomeView} />
          <Route
            path="/about"
            element={
              <div className="p-10 text-center text-gray-500">
                Trang Giới thiệu (Đang cập nhật...)
              </div>
            }
          />

          {/* KHÔNG GIAN HỌC VIÊN + ĐỒNG BỘ 4 ROUTE CON KHỚP 100% VỚI HEADER */}
          <Route
            path="/student"
            element={<StudentPage currentUser={currentUser} />}
          >
            <Route index element={<Navigate to="requests" replace />} />
            <Route path="requests" element={<StudentRequests />} />
            <Route path="classes" element={<StudentClasses />} />
            <Route path="schedule" element={<StudentSchedule />} />
            <Route path="tuition" element={<StudentTuition />} />
          </Route>

          {/* KHÔNG GIAN GIA SƯ */}
          <Route
            path="/tutor"
            element={<TutorPage currentUser={currentUser} />}
          >
            <Route index element={<Navigate to="classes" replace />} />
            <Route
              path="classes"
              element={<div>Giao diện Lớp phụ trách (Đang phát triển...)</div>}
            />
            <Route
              path="schedule"
              element={<div>Giao diện Lịch dạy (Đang phát triển...)</div>}
            />
            <Route
              path="profile"
              element={
                <div>Giao diện Hồ sơ & Lịch rảnh (Đang phát triển...)</div>
              }
            />
          </Route>

          {/* KHÔNG GIAN ADMIN */}
          <Route
            path="/admin/*"
            element={
              <div className="p-10 text-center font-bold text-xl text-red-600 min-h-[400px]">
                ⚙️ Giao diện Quản trị Hệ thống EduConnection (Đang phát
                triển...)
              </div>
            }
          />

          {/* BẪY URL: Người dùng gõ bậy hoặc không khớp quyền -> Tự động trả về trang chủ */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />

      {/* --- MODALS THỰC THI CHỨC NĂNG --- */}
      {activeModal === "login" && (
        <LoginForm
          onClose={() => setActiveModal(null)}
          switchToRegister={() => setActiveModal("register")}
          onLoginSuccess={() => {
            // Lấy dữ liệu mới nhất vừa lưu từ LoginForm để cập nhật state tổng
            const loggedInUser = JSON.parse(localStorage.getItem("user"));
            handleUserChange(loggedInUser);
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
