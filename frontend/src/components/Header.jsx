import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useModal } from '../contexts/ModalContext';

const HeaderLogo = () => (
  <div className="header-logo">
    <Link to="/">
      <h1 className="m-0 cursor-pointer text-[28px] font-bold text-blue-600">
        GiaSư<span className="text-orange-500">TamTam</span>
      </h1>
    </Link>
  </div>
);

const HeaderNav = () => {
  const { user } = useAuth();
  let menuItems = [];

  if (!user || !user.role) {
    menuItems = [
      { label: 'Trang chủ', path: '/' },
      { label: 'Lớp mới tuyển', path: '/lop-moi' },
    ];
  } else if (user.role === 'student') {
    menuItems = [
      { label: 'Dashboard', path: '/' },
      { label: 'Yêu cầu học', path: '/request' },
      { label: 'Lớp đang học', path: '/my-classes' },
      { label: 'Lịch học', path: '/my-schedule' },
      { label: 'Học phí', path: '/tuition' },
    ];
  } else if (user.role === 'tutor') {
    menuItems = [
      { label: 'Dashboard', path: '/' },
      { label: 'Hồ sơ', path: '/tutor-profile' },
      { label: 'Lớp phụ trách', path: '/tutor-classes' },
      { label: 'Lịch dạy', path: '/tutor-schedule' },
      { label: 'Buổi học', path: '/tutor-sessions' },
    ];
  } else if (user.role === 'staff') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Học viên', path: '/staff/students' },
      { label: 'Gia sư', path: '/staff/tutors' },
      { label: 'Môn học', path: '/staff/subjects' },
      { label: 'Nhu cầu', path: '/staff/requests' },
      { label: 'Phân công', path: '/staff/assignments' },
      { label: 'Lớp học', path: '/staff/classes' },
    ];
  }

  return (
    <nav className="header-nav flex gap-[25px]">
      {menuItems.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            `no-underline font-medium transition-colors cursor-pointer ${
              isActive ? 'text-blue-600 font-bold border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600'
            }`
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
};

const HeaderActions = () => {
  const { user, logout } = useAuth();
  const { openLogin, openRegister } = useModal();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!user || !user.role) {
    return (
      <div className="header-actions flex gap-[12px] relative items-center">
        <button
          onClick={openLogin}
          className="px-4 py-2 bg-transparent border-none text-blue-600 font-semibold cursor-pointer hover:text-blue-700 text-sm"
        >
          Đăng nhập
        </button>
        <button
          onClick={openRegister}
          className="px-[18px] py-2 bg-blue-600 text-white border-none rounded-[6px] font-semibold cursor-pointer hover:bg-blue-700 transition-colors text-sm"
        >
          Đăng ký
        </button>
      </div>
    );
  }

  const roleStyles = {
    staff: { label: 'Nhân viên', style: 'bg-red-100 text-red-700' },
    tutor: { label: 'Gia sư', style: 'bg-green-100 text-green-700' },
    student: { label: 'Học viên', style: 'bg-purple-100 text-purple-700' },
  };
  const currentStyle = roleStyles[user.role] || { label: 'Thành viên', style: 'bg-gray-100 text-gray-700' };

  return (
    <div className="header-actions flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${currentStyle.style}`}>
          {currentStyle.label}
        </span>
        <span className="text-gray-700 font-medium max-w-[150px] truncate">{user.name}</span>
      </div>
      <button
        onClick={handleLogout}
        className="px-4 py-2 bg-gray-100 text-gray-600 rounded-[6px] font-semibold border-none cursor-pointer hover:bg-red-50 hover:text-red-600 transition-colors text-sm"
      >
        Đăng xuất
      </button>
    </div>
  );
};

export default function Header() {
  return (
    <header className="main-header flex justify-between items-center px-10 py-[15px] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] sticky top-0 z-[100]">
      <HeaderLogo />
      <HeaderNav />
      <HeaderActions />
    </header>
  );
}
