import React from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ModalProvider } from './contexts/ModalContext';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import ClassListPage from './pages/ClassListPage';
import StudentsPage from './pages/StudentsPage';
import TutorsPage from './pages/TutorsPage';
import LearningRequestsPage from './pages/LearningRequestsPage';
import ClassesPage from './pages/ClassesPage';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import { useModal } from './contexts/ModalContext';
import StudentList from './pages/StudentList';

// Component để render modal toàn cục
const ModalRenderer = () => {
  const { activeModal, closeModal, openLogin, openRegister } = useModal();
  return (
    <>
      {activeModal === 'login' && (
        <LoginForm onClose={closeModal} switchToRegister={openRegister} />
      )}
      {activeModal === 'register' && (
        <RegisterForm onClose={closeModal} switchToLogin={openLogin} />
      )}
    </>
  );
};

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      // 1. TRANG CHỦ TỔNG QUAN (Đường dẫn '/')
      { index: true, element: <DashboardPage /> },
      
      // 2. CÁC ĐƯỜNG DẪN CŨ CỦA BẠN
      { path: 'lop-moi', element: <ClassListPage /> },
      { path: 'students', element: <StudentsPage /> },
      { path: 'tutors', element: <TutorsPage /> },
      { path: 'requests', element: <LearningRequestsPage /> },
      { path: 'classes', element: <ClassesPage /> },

      // =========================================================================
      // 3. ĐỒNG BỘ CÁC ĐƯỜNG DẪN TỪ SIDEBAR VÀO ĐÂY (Để sửa lỗi 404)
      // =========================================================================
      
      // --- ROUTE CHO TUTOR (GIA SƯ) ---
      { path: 'tutor-classes', element: <ClassesPage /> },       // Lớp phụ trách
      { path: 'tutor-schedule', element: <DashboardPage /> },    // Lịch dạy (Tạm thời hướng về Dashboard, bạn thay bằng SchedulePage sau nhé)
      { path: 'tutor-profile', element: <DashboardPage /> },     // Hồ sơ gia sư

      // --- ROUTE CHO STUDENT (HỌC VIÊN) ---
      { path: 'my-classes', element: <ClassesPage /> },          // Lớp đang học
      { path: 'tuition', element: <DashboardPage /> },           // Học phí
      { path: 'request', element: <LearningRequestsPage /> },    // Gửi nhu cầu tìm gia sư

      // --- ROUTE CHO ADMIN ---
      { path: 'admin/tutors', element: <TutorsPage /> },
      { path: 'admin/requests', element: <LearningRequestsPage /> },
      { path: 'admin/classes', element: <ClassesPage /> },
      { path: 'admin/finance', element: <DashboardPage /> },
      { path: 'admin/students', element: <StudentList /> },
    ],
  },
]);

function App() {
  return (
    <AuthProvider>
      <ModalProvider>
        <RouterProvider router={router} />
        <ModalRenderer />
      </ModalProvider>
    </AuthProvider>
  );
}

export default App;