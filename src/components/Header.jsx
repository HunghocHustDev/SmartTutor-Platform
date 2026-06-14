import React, { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext"; // Import custom hook từ Context toàn cục

// ==========================================
// 1. COMPONENT LOGO (Đã sửa lỗi thiếu Prop)
// ==========================================
const HeaderLogo = ({ user }) => (
  <div className="header-logo">
    <Link
      to={
        user?.role === "student"
          ? "/student"
          : user?.role === "tutor"
            ? "/tutor"
            : "/"
      }
      className="no-underline select-none"
    >
      <h1 className="text-2xl font-extrabold tracking-tight text-gray-900">
        Edu<span className="text-blue-600">Connection</span>
      </h1>
    </Link>
  </div>
);

// ==========================================
// 2. COMPONENT NAV MENU (Tối ưu theo kiến trúc Dashboard + Outlet)
// ==========================================
const HeaderNav = ({ user, onLoginClick, onRegisterClick }) => {
  let menuItems = [];

  // Khi CHƯA đăng nhập: Hiển thị các menu điều hướng trang công khai (Landing Page)
  if (!user || !user.role) {
    menuItems = [
      { label: "Trang chủ", to: "/" },
      { label: "Giới thiệu", to: "/about" },
      {
        label: "Tìm gia sư",
        to: "#",
        isAction: true,
        onClick: () => onLoginClick(),
      },
      {
        label: "Trở thành gia sư",
        to: "#",
        isAction: true,
        onClick: onRegisterClick,
      },
    ];
  } else {
    // Khi ĐÃ đăng nhập: Menu chi tiết đã được đẩy xuống Sidebar của từng phân hệ.
    // Trên Header chỉ giữ lại các liên kết điều hướng nhanh mang tính tổng quan.
    menuItems = [
      { label: "Trang chủ hệ thống", to: "/" },
      {
        label: "Vào Không gian làm việc",
        to: user.role === "admin" ? "/admin/dashboard" : `/${user.role}`,
      },
    ];
  }

  return (
    <nav className="header-nav flex gap-6 items-center">
      {menuItems.map((item, index) => {
        if (item.isAction) {
          return (
            <button
              key={index}
              onClick={item.onClick}
              className="text-base font-medium text-gray-600 hover:text-blue-600 bg-transparent border-none p-0 cursor-pointer transition-colors"
            >
              {item.label}
            </button>
          );
        }

        return (
          <NavLink
            key={index}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `text-base font-medium transition-colors cursor-pointer pb-1 border-b-2 ${
                isActive
                  ? "text-blue-600 font-semibold border-blue-600"
                  : "text-gray-600 border-transparent hover:text-blue-600"
              }`
            }
          >
            {item.label}
          </NavLink>
        );
      })}
    </nav>
  );
};

// ==========================================
// 3. COMPONENT ACTIONS (Sử dụng trực tiếp logic từ Context)
// ==========================================
const HeaderActions = ({
  user,
  onLoginClick,
  onRegisterClick,
  onLogout,
  handleFakeLogin,
}) => {
  const [showFakeBox, setShowFakeBox] = useState(false);

  if (!user || !user.role) {
    return (
      <div className="header-actions flex gap-3 relative items-center">
        {/* Nút Test Roles tiện ích phục vụ giai đoạn phát triển */}
        <button
          onClick={() => setShowFakeBox(!showFakeBox)}
          className="px-2 py-1 text-xs bg-amber-500 text-white rounded hover:bg-amber-600 font-mono transition-all"
        >
          ⚙️ Test Roles
        </button>

        {showFakeBox && (
          <div className="absolute right-0 top-11 bg-white border border-gray-200 shadow-xl p-3 rounded-lg flex flex-col gap-2 z-50 w-48 text-sm motion-safe:animate-fadeIn">
            <p className="font-bold text-gray-400 text-[10px] border-b pb-1 tracking-wider">
              CHỌN TÀI KHOẢN GIẢ LẬP
            </p>
            <button
              onClick={() => {
                handleFakeLogin("student", "Nguyễn Khánh An");
                setShowFakeBox(false);
              }}
              className="text-left py-1.5 px-2 hover:bg-purple-50 text-purple-700 rounded font-medium transition-colors"
            >
              1. Học viên (An)
            </button>
            <button
              onClick={() => {
                handleFakeLogin("tutor", "Thầy giáo Ngô Bảo");
                setShowFakeBox(false);
              }}
              className="text-left py-1.5 px-2 hover:bg-green-50 text-green-700 rounded font-medium transition-colors"
            >
              2. Gia sư (Bảo)
            </button>
            <button
              onClick={() => {
                handleFakeLogin("admin", "Admin Trung Tâm");
                setShowFakeBox(false);
              }}
              className="text-left py-1.5 px-2 hover:bg-red-50 text-red-700 rounded font-medium transition-colors"
            >
              3. Ban Quản Trị
            </button>
          </div>
        )}

        <button
          onClick={() => onLoginClick()}
          className="px-4 py-2 text-blue-600 font-semibold hover:text-blue-700 text-sm transition-colors"
        >
          Đăng nhập
        </button>

        <button
          onClick={onRegisterClick}
          className="px-[18px] py-2 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 transition-colors text-sm shadow-sm"
        >
          Đăng ký
        </button>
      </div>
    );
  }

  const roleStyles = {
    admin: { label: "Quản trị viên", style: "bg-red-100 text-red-700" },
    tutor: { label: "Gia sư", style: "bg-green-100 text-green-700" },
    student: { label: "Học viên", style: "bg-purple-100 text-purple-700" },
  };

  const currentStyle = roleStyles[user.role] || {
    label: "Thành viên",
    style: "bg-gray-100 text-gray-700",
  };

  return (
    <div className="header-actions flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span
          className={`text-xs px-2.5 py-1 rounded-full font-semibold ${currentStyle.style}`}
        >
          {currentStyle.label}
        </span>
        <span className="text-gray-700 font-semibold max-w-[150px] truncate">
          {user.name}
        </span>
      </div>

      <button
        onClick={onLogout}
        className="px-4 py-2 bg-gray-100 text-gray-600 rounded-md font-semibold hover:bg-red-50 hover:text-red-600 transition-colors text-sm"
      >
        Đăng xuất
      </button>
    </div>
  );
};

// ==========================================
// 4. COMPONENT CHÍNH EXPORT (Tối giản tối đa State nhờ Context)
// ==========================================
export default function Header({ onLoginClick, onRegisterClick }) {
  // Lấy trực tiếp cục state và hàm xử lý từ bộ kho chứa Context toàn cục
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();

  // Đồng bộ xử lý đăng nhập ảo trực tiếp thông qua hàm login của Context
  const handleFakeLogin = (role, name) => {
    const fakeUserData = { role, name, token: "fake-jwt-token-12345" };

    // Gọi hàm cập nhật state của Context, tự động re-render toàn bộ app ứng dụng
    login(fakeUserData);

    // Điều hướng phân quyền tường minh qua Router URL
    if (role === "student") navigate("/student");
    else if (role === "tutor") navigate("/tutor");
    else if (role === "admin") navigate("/admin/dashboard");
  };

  const handleLogout = () => {
    logout(); // Xóa state trong context và localStorage thông qua hàm của Context
    navigate("/");
  };

  return (
    <header className="main-header flex justify-between items-center px-10 py-4 bg-white shadow-sm sticky top-0 z-[100]">
      {/* Sửa lỗi truyền thiếu prop user */}
      <HeaderLogo user={user} />

      <HeaderNav
        user={user}
        onLoginClick={onLoginClick}
        onRegisterClick={onRegisterClick}
      />

      <HeaderActions
        user={user}
        onLoginClick={onLoginClick}
        onRegisterClick={onRegisterClick}
        onLogout={handleLogout}
        handleFakeLogin={handleFakeLogin}
      />
    </header>
  );
}
