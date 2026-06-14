import React, { useState, useEffect } from "react";
import {
  Routes,
  Route,
  Navigate,
  useLocation,
  useNavigate,
} from "react-router-dom";

// --- IMPORT CONTEXT & COMPONENTS ---
import { useAuth } from "./context/AuthContext";
import Header from "./components/Header";
import Banner from "./components/Banner";
import ClassList from "./components/ClassList";
import Workflow from "./components/Workflow";
import Footer from "./components/Footer";
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";

// --- IMPORT PAGES ---
import StudentPage from "./pages/StudentPage";
import TutorPage from "./pages/TutorPage";

// --- IMPORT COMPONENTS CON HỌC VIÊN ---
import StudentRequests from "./components/student/StudentRequests";
import StudentClasses from "./components/student/StudentClasses";
import StudentSchedule from "./components/student/StudentSchedule";
import StudentTuition from "./components/student/StudentTuition";

// --- 🌟 IMPORT ĐÚNG 3 CHỨC NĂNG CON CỦA GIA SƯ (SỬA LỖI TRẮNG TRANG TẠI ĐÂY) 🌟 ---
import TutorClasses from "./components/tutor/TutorClasses";
import TutorSchedule from "./components/tutor/TutorSchedule";
import TutorReports from "./components/tutor/TutorReports";

// COMPONENT CHẶN QUYỀN TRUY CẬP (PROTECTED ROUTE)
const ProtectedRoute = ({ allowedRoles, children }) => {
  const { user } = useAuth();
  if (!user) return <Navigate to="/" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role))
    return <Navigate to="/" replace />;
  return children;
};

export default function App() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [activeModal, setActiveModal] = useState(null);

  useEffect(() => {
    if (user && location.pathname === "/") {
      if (user.role === "student") navigate("/student/requests");
      else if (user.role === "tutor")
        navigate("/tutor/schedule"); // Đồng bộ về lịch dạy khi đăng nhập thành công
      else if (user.role === "admin") navigate("/admin/dashboard");
    }
  }, [user, location.pathname, navigate]);

  const HomeView = (
    <>
      <Banner
        key={user?.role || "guest"}
        currentUser={user}
        onFindTutorClick={() => setActiveModal("login")}
        onBeTutorClick={() => setActiveModal("register")}
      />
      <ClassList />
      <Workflow />
    </>
  );

  return (
    <div className="flex flex-col min-h-screen bg-white">
      <Header
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
      />

      <main className="flex-1 w-full flex flex-col">
        <Routes>
          <Route path="/" element={HomeView} />
          <Route
            path="/about"
            element={
              <div className="p-10 text-center text-gray-500">
                Trang Giới thiệu (Đang cập nhật...)
              </div>
            }
          />

          {/* PHÂN HỆ HỌC VIÊN */}
          <Route
            path="/student"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <StudentPage />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="requests" replace />} />
            <Route path="requests" element={<StudentRequests />} />
            <Route path="classes" element={<StudentClasses />} />
            <Route path="schedule" element={<StudentSchedule />} />
            <Route path="tuition" element={<StudentTuition />} />
          </Route>

          {/* ==========================================
              PHÂN HỆ GIA SƯ - ĐÃ ĐỒNG BỘ CHUẨN ĐƯỜNG DẪN 
              ========================================== */}
          <Route
            path="/tutor"
            element={
              <ProtectedRoute allowedRoles={["tutor"]}>
                <TutorPage />
              </ProtectedRoute>
            }
          >
            {/* Tự động hướng tới lịch dạy tuần này khi truy cập /tutor */}
            <Route index element={<Navigate to="schedule" replace />} />
            <Route path="schedule" element={<TutorSchedule />} />
            <Route path="classes" element={<TutorClasses />} />
            <Route path="reports" element={<TutorReports />} />
          </Route>

          {/* PHÂN HỆ ADMIN */}
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <div className="p-10 text-center font-bold text-xl text-red-600 min-h-[400px]">
                  ⚙️ Giao diện Quản trị (Đang phát triển...)
                </div>
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />

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
