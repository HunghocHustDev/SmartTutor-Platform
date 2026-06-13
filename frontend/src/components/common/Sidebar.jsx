import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = () => {
  const { user } = useAuth();
  if (!user) return null;

  // Menu items dựa trên role (giống HeaderNav nhưng dạng dọc)
  let menuItems = [];
  if (user.role === 'student') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Yêu cầu học', path: '/request' },
      { label: 'Lớp đang học', path: '/my-classes' },
      { label: 'Lịch học', path: '/my-schedule' },
      { label: 'Buổi học', path: '/my-sessions' },
      { label: 'Học phí', path: '/tuition' },
    ];
  } else if (user.role === 'tutor') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Hồ sơ gia sư', path: '/tutor-profile' },
      { label: 'Lớp phụ trách', path: '/tutor-classes' },
      { label: 'Lịch dạy', path: '/tutor-schedule' },
      { label: 'Buổi học', path: '/tutor-sessions' },
    ];
  } else if (user.role === 'staff') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Quản lý Học viên', path: '/staff/students' },
      { label: 'Quản lý Gia sư', path: '/staff/tutors' },
      { label: 'Quản lý Môn học', path: '/staff/subjects' },
      { label: 'Xử lý Nhu cầu', path: '/staff/requests' },
      { label: 'Phân công Gia sư', path: '/staff/assignments' },
      { label: 'Quản lý Lớp', path: '/staff/classes' },
      { label: 'Lịch học Cố định', path: '/staff/schedules' },
      { label: 'Buổi học', path: '/staff/sessions' },
      { label: 'Học phí', path: '/staff/finance' },
    ];
  } else {
    return null;
  }

  return (
    <aside className="w-64 bg-white border-r p-4 h-screen sticky top-0">
      <nav className="flex flex-col gap-2">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `px-3 py-2 rounded-md transition-colors ${
                isActive ? 'bg-blue-100 text-blue-700 font-semibold' : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;
