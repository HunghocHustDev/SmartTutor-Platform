import React, { useState, useEffect } from "react";
import { Link, NavLink, useNavigate, useLocation } from "react-router-dom";

// ==========================================
// 1. COMPONENT LOGO
// ==========================================
const HeaderLogo = (
  { user }, // Truyền thêm user prop vào đây
) => (
  <div className="header-logo">
    <Link
      to={
        user?.role === "student"
          ? "/student"
          : user?.role === "tutor"
            ? "/tutor"
            : "/"
      }
      className="no-underline"
    >
      <h1 className="...">
        Edu<span className="...">Connection</span>
      </h1>
    </Link>
  </div>
);

// ==========================================
// 2. COMPONENT NAV MENU
// ==========================================
const HeaderNav = ({ user, onLoginClick, onRegisterClick }) => {
  let menuItems = [];

  // Phân chia danh sách menu theo Vai trò (Role)
  if (!user || !user.role) {
    menuItems = [
      {
        label: "Trang chủ",
        to:
          user?.role === "student"
            ? "/student"
            : user?.role === "tutor"
              ? "/tutor"
              : "/",
      },
      { label: "Giới thiệu", to: "/about" },
      {
        label: "Tìm gia sư",
        to: "#action-find-tutor",
        isAction: true,
        onClick: () => onLoginClick("/student/requests"), // Truyền kèm target route nếu muốn chuyển hướng sau đăng nhập
      },
      {
        label: "Trở thành gia sư",
        to: "#action-be-tutor",
        isAction: true,
        onClick: onRegisterClick,
      },
    ];
  } else if (user.role === "student") {
    menuItems = [
      { label: "Trang chủ", to: "/" },
      { label: "Lớp đang học", to: "/student/classes" },
      { label: "Thời khóa biểu", to: "/student/schedule" },
      { label: "Học phí & Thanh toán", to: "/student/tuition" },
      { label: "Gửi nhu cầu mới", to: "/student/requests" },
    ];
  } else if (user.role === "tutor") {
    menuItems = [
      { label: "Trang chủ", to: "/" },
      { label: "Lớp phụ trách", to: "/tutor/classes" },
      { label: "Lịch dạy", to: "/tutor/schedule" },
      { label: "Hồ sơ & Lịch rảnh", to: "/tutor/profile" },
    ];
  } else if (user.role === "admin") {
    menuItems = [
      { label: "Tổng quan", to: "/admin/dashboard" },
      { label: "Quản lý Gia sư", to: "/admin/tutors" },
      { label: "Xử lý Nhu cầu", to: "/admin/requests" },
      { label: "Quản lý Lớp học", to: "/admin/classes" },
      { label: "Học phí & Thu chi", to: "/admin/finance" },
    ];
  }

  return (
    <nav className="header-nav flex gap-[25px] items-center">
      {menuItems.map((item, index) => {
        if (item.isAction) {
          return (
            <button
              key={index}
              onClick={item.onClick}
              className="no-underline font-medium text-gray-600 hover:text-blue-600 bg-transparent border-none p-0 cursor-pointer text-base transition-colors"
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
              `no-underline font-medium transition-colors cursor-pointer pb-1 ${
                isActive
                  ? "text-blue-600 font-bold border-b-2 border-blue-600"
                  : "text-gray-600 hover:text-blue-600"
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
// 3. COMPONENT ACTIONS (Hỗ trợ Test và Đăng nhập/Đăng xuất)
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
      <div className="header-actions flex gap-[12px] relative items-center">
        <button
          onClick={() => setShowFakeBox(!showFakeBox)}
          className="px-2 py-1 text-xs bg-amber-500 text-white rounded hover:bg-amber-600 font-mono"
        >
          ⚙️ Test Roles
        </button>

        {showFakeBox && (
          <div className="absolute right-0 top-10 bg-white border border-gray-200 shadow-xl p-3 rounded-lg flex flex-col gap-2 z-50 w-48 text-sm">
            <p className="font-bold text-gray-500 text-xs border-b pb-1">
              CHỌN TÀI KHOẢN ẢO
            </p>
            <button
              onClick={() => {
                handleFakeLogin("student", "Nguyễn Khánh An");
                setShowFakeBox(false);
              }}
              className="text-left py-1 px-2 hover:bg-purple-50 text-purple-700 rounded font-medium"
            >
              1. Học viên (An)
            </button>
            <button
              onClick={() => {
                handleFakeLogin("tutor", "Thầy giáo Ngô Bảo");
                setShowFakeBox(false);
              }}
              className="text-left py-1 px-2 hover:bg-green-50 text-green-700 rounded font-medium"
            >
              2. Gia sư (Bảo)
            </button>
            <button
              onClick={() => {
                handleFakeLogin("admin", "Admin Trung Tâm");
                setShowFakeBox(false);
              }}
              className="text-left py-1 px-2 hover:bg-red-50 text-red-700 rounded font-medium"
            >
              3. Nhân viên
            </button>
          </div>
        )}

        <button
          onClick={() => onLoginClick()}
          className="px-4 py-2 bg-transparent border-none text-blue-600 font-semibold cursor-pointer hover:text-blue-700 text-sm"
        >
          Đăng nhập
        </button>

        <button
          onClick={onRegisterClick}
          className="px-[18px] py-2 bg-blue-600 text-white border-none rounded-[6px] font-semibold cursor-pointer hover:bg-blue-700 transition-colors text-sm"
        >
          Đăng ký
        </button>
      </div>
    );
  }

  const roleStyles = {
    admin: { label: "Nhân viên", style: "bg-red-100 text-red-700" },
    tutor: { label: "Gia sư", style: "bg-green-100 text-green-700" },
    student: { label: "Học viên", style: "bg-purple-100 text-purple-700" },
  };

  const currentStyle = roleStyles[user.role] || {
    label: "Thành viên",
    style: "bg-gray-100",
  };

  return (
    <div className="header-actions flex items-center gap-4">
      <div className="flex items-center gap-2">
        <span
          className={`text-xs px-2.5 py-1 rounded-full font-semibold ${currentStyle.style}`}
        >
          {currentStyle.label}
        </span>
        <span className="text-gray-700 font-medium max-w-[150px] truncate">
          {user.name}
        </span>
      </div>

      <button
        onClick={onLogout}
        className="px-4 py-2 bg-gray-100 text-gray-600 rounded-[6px] font-semibold border-none cursor-pointer hover:bg-red-50 hover:text-red-600 transition-colors text-sm"
      >
        Đăng xuất
      </button>
    </div>
  );
};

// ==========================================
// 4. COMPONENT CHÍNH EXPORT
// ==========================================
export default function Header({
  onLoginClick,
  onRegisterClick,
  onUserChange,
  currentUser, // Nhận trực tiếp user state từ App.jsx đẩy xuống để đồng bộ tức thì
}) {
  const [user, setUser] = useState(() => {
    // Tối ưu hóa: Chỉ đọc localStorage duy nhất một lần khi load trang đầu tiên
    return JSON.parse(localStorage.getItem("user")) || null;
  });

  const navigate = useNavigate();

  // Đồng bộ hóa trạng thái Header khi App.jsx thay đổi user (ví dụ: đăng nhập từ Modal thật công khai)
  useEffect(() => {
    setUser(currentUser);
  }, [currentUser]);

  // Xử lý đăng nhập ảo nhanh để test giao diện phân hệ
  const handleFakeLogin = (role, name) => {
    const fakeUserData = { role, name, token: "fake-jwt-token-12345" };
    localStorage.setItem("user", JSON.stringify(fakeUserData));
    setUser(fakeUserData);

    if (onUserChange) onUserChange(fakeUserData);

    // Điều hướng phân quyền tường minh qua Router URL
    if (role === "student") {
      navigate("/student/requests");
    } else if (role === "tutor") {
      navigate("/tutor/classes");
    } else if (role === "admin") {
      navigate("/admin/dashboard");
    }
  };

  // Đăng xuất xóa bộ nhớ và quay về trang chủ
  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
    if (onUserChange) onUserChange(null);
    navigate("/");
  };

  return (
    <header className="main-header flex justify-between items-center px-10 py-[15px] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] sticky top-0 z-[100]">
      <HeaderLogo />

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
