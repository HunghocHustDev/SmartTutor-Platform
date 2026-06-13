import React, { useState, useEffect } from "react";

// ==========================================

// 1. COMPONENT LOGO

// ==========================================

const HeaderLogo = ({ onTabChange }) => (
  <div className="header-logo">
    <h1
      className="text-[28px] font-bold text-blue-600 m-0 cursor-pointer"
      onClick={() => {
        if (onTabChange) {
          onTabChange("home"); // Quay về trang chủ khi nhấn logo thay vì F5 lại trang cố định
        } else {
          window.location.href = "/";
        }
      }}
    >
      GiaSư<span className="text-orange-500">TâmTâm</span>
    </h1>
  </div>
);

// ==========================================

// 2. COMPONENT NAV MENU (Đồng bộ value theo 4 mục Student và 3 mục Tutor)

// ==========================================

const HeaderNav = ({ user, activeTab, onTabChange }) => {
  let menuItems = [];

  // Phân chia danh sách các mục trên Header dựa theo Vai trò (Role)

  if (!user || !user.role) {
    // Menu dành cho khách vãng lai chưa đăng nhập

    menuItems = [
      { label: "Trang chủ", value: "home", href: "/" },

      { label: "Tìm gia sư", value: "home", href: "#tim-gia-su" },

      { label: "Lớp mới tuyển", value: "home", href: "#lop-moi" },

      { label: "Trở thành gia sư", value: "home", href: "#dang-ky-gia-su" },

      { label: "Giới thiệu", value: "home", href: "#gioi-thieu" },
    ];
  } else if (user.role === "student") {
    // CHUẨN HÓA: 4 mục con của Học viên đều mang giá trị value tổng là "student"

    menuItems = [
      { label: "Trang chủ", value: "home", href: "/" },

      { label: "Lớp đang học", value: "student", href: "#student-classes" },

      { label: "Thời khóa biểu", value: "student", href: "#student-schedule" },

      {
        label: "Học phí & Thanh toán",

        value: "student",

        href: "#student-tuition",
      },

      { label: "Gửi nhu cầu mới", value: "student", href: "#create-request" },
    ];
  } else if (user.role === "tutor") {
    // CHUẨN HÓA: 3 mục con của Gia sư đều mang giá trị value tổng là "tutor"

    menuItems = [
      { label: "Trang chủ", value: "home", href: "/" },

      { label: "Lớp phụ trách", value: "tutor", href: "#tutor-classes" },

      { label: "Lịch dạy", value: "tutor", href: "#tutor-schedule" },

      { label: "Hồ sơ & Lịch rảnh", value: "tutor", href: "#tutor-profile" },
    ];
  } else if (user.role === "admin") {
    // CHUẨN HÓA: Các mục quản trị mang giá trị value tổng là "admin"

    menuItems = [
      { label: "Tổng quan", value: "admin", href: "/" },

      { label: "Quản lý Gia sư", value: "admin", href: "#admin-tutors" },

      { label: "Xử lý Nhu cầu", value: "admin", href: "#admin-requests" },

      { label: "Quản lý Lớp học", value: "admin", href: "#admin-classes" },

      { label: "Học phí & Thu chi", value: "admin", href: "#admin-finance" },
    ];
  }

  return (
    <nav className="header-nav flex gap-[25px]">
      {menuItems.map((item, index) => {
        // Kiểm tra trạng thái Active chính xác theo không gian tab lớn

        const isActive = activeTab === item.value;

        return (
          <a
            key={index}
            href={item.href}
            onClick={(e) => {
              if (onTabChange) {
                e.preventDefault(); // Ngăn F5 tải lại trang làm mất State ứng dụng

                onTabChange(item.value); // Kích hoạt đổi vùng không gian bên App.jsx
              }
            }}
            className={`no-underline font-medium transition-colors cursor-pointer ${
              isActive
                ? "text-blue-600 font-bold border-b-2 border-blue-600"
                : "text-gray-600 hover:text-blue-600"
            }`}
          >
            {item.label}
          </a>
        );
      })}
    </nav>
  );
};

// ==========================================

// 3. COMPONENT ACTIONS (Sạch lỗi dấu ngoặc - Đồng bộ State tổng)

// ==========================================

const HeaderActions = ({
  user,

  onLoginClick,

  onRegisterClick,

  onLogout,

  handleFakeLogin,
}) => {
  const [showFakeBox, setShowFakeBox] = useState(false);

  // TRƯỜNG HỢP 1: CHƯA ĐĂNG NHẬP

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
          onClick={onLoginClick}
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

  // TRƯỜNG HỢP 2: ĐÃ ĐĂNG NHẬP

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

// 4. COMPONENT CHÍNH EXPORT ĐỂ SỬ DỤNG

// ==========================================

export default function Header({
  onLoginClick,

  onRegisterClick,

  activeTab,

  onTabChange,

  onUserChange, // Nhận prop callback để thông báo cập nhật user tổng lên App.jsx
}) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");

    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // Đã sửa: Gỡ bỏ reload cứng, cập nhật state đồng bộ qua luồng dữ liệu React

  const handleFakeLogin = (role, name) => {
    const fakeUserData = { role, name, token: "fake-jwt-token-12345" };

    localStorage.setItem("user", JSON.stringify(fakeUserData));

    setUser(fakeUserData);

    if (onUserChange) onUserChange(); // Cập nhật user tổng để làm mới giao diện Banner lời chào

    if (onTabChange) onTabChange(role); // Tự động mở vùng điều hướng của vai trò đó ngay lập tức
  };

  // Đã sửa: Gỡ bỏ reload cứng, dọn sạch bộ nhớ và đẩy hướng mượt mà về trang chủ

  const handleLogout = () => {
    localStorage.removeItem("user");

    setUser(null);

    if (onUserChange) onUserChange(); // Xóa trạng thái đăng nhập của App.jsx

    if (onTabChange) onTabChange("home"); // Đá luồng hiển thị về màn hình chính
  };

  return (
    <header className="main-header flex justify-between items-center px-10 py-[15px] bg-white shadow-[0_2px_4px_rgba(0,0,0,0.05)] sticky top-0 z-[100]">
      <HeaderLogo onTabChange={onTabChange} />

      <HeaderNav user={user} activeTab={activeTab} onTabChange={onTabChange} />

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
