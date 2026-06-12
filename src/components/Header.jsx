import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useModal } from '../contexts/ModalContext';

const HeaderLogo = () => {
  return (
    <div className="header-logo">
      <Link to="/">
        <h1 className="text-[28px] font-bold text-blue-600 m-0 cursor-pointer">
          GiaSư<span className="text-orange-500">TâmTâm</span>
        </h1>
      </Link>
    </div>
  );
};

const HeaderNav = () => {
  const { user } = useAuth();
  let menuItems = [];

  if (!user || !user.role) {
    menuItems = [
      { label: 'Trang chủ', path: '/' },
      { label: 'Tìm gia sư', path: '/tim-gia-su' },
      { label: 'Lớp mới tuyển', path: '/lop-moi' },
      { label: 'Trở thành gia sư', path: '/dang-ky-gia-su' },
      { label: 'Giới thiệu', path: '/gioi-thieu' },
    ];
  } else if (user.role === 'student') {
    menuItems = [
      { label: 'Dashboard', path: '/' },
      { label: 'Lớp đang học', path: '/my-classes' },
      { label: 'Học phí', path: '/tuition' },
      { label: 'Gửi nhu cầu', path: '/request' },
    ];
  } else if (user.role === 'tutor') {
    menuItems = [
      { label: 'Dashboard', path: '/' },
      { label: 'Lớp phụ trách', path: '/tutor-classes' },
      { label: 'Lịch dạy', path: '/tutor-schedule' },
      { label: 'Hồ sơ', path: '/tutor-profile' },
    ];
  } else if (user.role === 'admin') {
    menuItems = [
      { label: 'Tổng quan', path: '/' },
      { label: 'Học viên', path: '/admin/students' },
      { label: 'Quản lý Gia sư', path: '/admin/tutors' },
      { label: 'Xử lý Nhu cầu', path: '/admin/requests' },
      { label: 'Quản lý Lớp', path: '/admin/classes' },
    ];
  }

  return (
    <nav className="header-nav flex gap-[25px]">
      {menuItems.map((item, idx) => (
        <Link
          key={idx}
          to={item.path}
          className={({ isActive }) =>
            `no-underline font-medium transition-colors cursor-pointer ${
              isActive ? 'text-blue-600 font-bold border-b-2 border-blue-600' : 'text-gray-600 hover:text-blue-600'
            }`
          }
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
};

const HeaderActions = () => {
  const { user, logout, fakeLogin } = useAuth();
  const { openLogin, openRegister } = useModal();
  const [showFakeBox, setShowFakeBox] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (!user || !user.role) {
    return (
      <div className="header-actions flex gap-[12px] relative items-center">
        <button
          onClick={() => setShowFakeBox(!showFakeBox)}
          className="px-2 py-1 text-xs bg-amber-500 text-white rounded hover:bg-amber-600 font-mono"
        >
          ⚙️ Test Roles
        </button>
        {showFakeBox && (
          <div className="absolute right-0 top-10 bg-white border border-gray-200 shadow-xl p-3 rounded-lg flex flex-col gap-2 z-50 w-48 text-sm">
            <p className="font-bold text-gray-500 text-xs border-b pb-1">CHỌN TÀI KHOẢN ẢO</p>
            <button
              onClick={() => {
                fakeLogin('student', 'Nguyễn Khánh An');
                setShowFakeBox(false);
                navigate('/');
              }}
              className="text-left py-1 px-2 hover:bg-purple-50 text-purple-700 rounded font-medium"
            >
              1. Học viên (An)
            </button>
            <button
              onClick={() => {
                fakeLogin('tutor', 'Thầy giáo Ngô Bảo');
                setShowFakeBox(false);
                navigate('/');
              }}
              className="text-left py-1 px-2 hover:bg-green-50 text-green-700 rounded font-medium"
            >
              2. Gia sư (Bảo)
            </button>
            <button
              onClick={() => {
                fakeLogin('admin', 'Admin Trung Tâm');
                setShowFakeBox(false);
                navigate('/');
              }}
              className="text-left py-1 px-2 hover:bg-red-50 text-red-700 rounded font-medium"
            >
              3. Nhân viên
            </button>
          </div>
        )}
        <button onClick={openLogin} className="px-4 py-2 bg-transparent border-none text-blue-600 font-semibold cursor-pointer hover:text-blue-700 text-sm">
          Đăng nhập
        </button>
        <button onClick={openRegister} className="px-[18px] py-2 bg-blue-600 text-white border-none rounded-[6px] font-semibold cursor-pointer hover:bg-blue-700 transition-colors text-sm">
          Đăng ký
        </button>
      </div>
    );
  }

  const roleStyles = {
    admin: { label: 'Nhân viên', style: 'bg-red-100 text-red-700' },
    tutor: { label: 'Gia sư', style: 'bg-green-100 text-green-700' },
    student: { label: 'Học viên', style: 'bg-purple-100 text-purple-700' },
  };
  const currentStyle = roleStyles[user.role] || { label: 'Thành viên', style: 'bg-gray-100' };

  return (
    <div className="header-actions flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span className={`text-xs px-2.5 py-1 rounded-full font-semibold ${currentStyle.style}`}>
          {currentStyle.label}
        </span>
        <span className="text-gray-700 font-medium max-w-[150px] truncate">{user.name}</span>
      </div>
      <button onClick={handleLogout} className="px-4 py-2 bg-gray-100 text-gray-600 rounded-[6px] font-semibold border-none cursor-pointer hover:bg-red-50 hover:text-red-600 transition-colors text-sm">
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