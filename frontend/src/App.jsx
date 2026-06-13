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
import SubjectsPage from './pages/SubjectsPage';
import AssignmentsPage from './pages/AssignmentsPage';
import SchedulesPage from './pages/SchedulesPage';
import SessionsPage from './pages/SessionsPage';
import FinancePage from './pages/FinancePage';
import TutorProfilePage from './pages/TutorProfilePage';
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
      { path: 'tutor-schedule', element: <SchedulesPage /> },
      { path: 'tutor-sessions', element: <SessionsPage /> },
      { path: 'tutor-profile', element: <TutorProfilePage /> },

      // --- ROUTE CHO STUDENT (HỌC VIÊN) ---
      { path: 'my-classes', element: <ClassesPage /> },          // Lớp đang học
      { path: 'my-schedule', element: <SchedulesPage /> },
      { path: 'my-sessions', element: <SessionsPage /> },
      { path: 'tuition', element: <FinancePage /> },
      { path: 'request', element: <LearningRequestsPage /> },

      // --- ROUTE CHO STAFF ---
      { path: 'staff/tutors', element: <TutorsPage /> },
      { path: 'staff/subjects', element: <SubjectsPage /> },
      { path: 'staff/requests', element: <LearningRequestsPage /> },
      { path: 'staff/assignments', element: <AssignmentsPage /> },
      { path: 'staff/classes', element: <ClassesPage /> },
      { path: 'staff/schedules', element: <SchedulesPage /> },
      { path: 'staff/sessions', element: <SessionsPage /> },
      { path: 'staff/finance', element: <FinancePage /> },
      { path: 'staff/students', element: <StudentList /> },
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
