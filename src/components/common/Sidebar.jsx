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
      { label: 'Lớp đang học', path: '/my-classes' },
      { label: 'Học phí', path: '/tuition' },
      { label: 'Gửi nhu cầu', path: '/request' },
    ];
  } else if (user.role === 'tutor') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Lớp phụ trách', path: '/tutor-classes' },
      { label: 'Lịch dạy', path: '/tutor-schedule' },
      { label: 'Hồ sơ', path: '/tutor-profile' },
    ];
  } else if (user.role === 'admin') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Quản lý Gia sư', path: '/admin/tutors' },
      { label: 'Xử lý Nhu cầu', path: '/admin/requests' },
      { label: 'Quản lý Lớp', path: '/admin/classes' },
      { label: 'Học phí', path: '/admin/finance' },
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