import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { STUDENT_MENU } from "../constants/navigation"; // 🌟 Import hằng số menu sạch sẽ

function StudentPage() {
  const { user } = useAuth();

  return (
    <div className="flex min-h-[calc(100vh-70px)] bg-gray-50">
      {/* ==========================================
          SIDEBAR - THANH ĐIỀU HƯỚNG DỌC BÊN TRÁI
          ========================================== */}
      <aside className="w-64 bg-white border-r border-gray-200 p-5 flex flex-col gap-6 shrink-0 shadow-sm">
        <div className="pb-3 border-b border-gray-100">
          <h3 className="text-xs font-bold text-gray-400 tracking-wider uppercase mb-1">
            Menu học viên
          </h3>
          <p className="text-xs text-purple-600 font-semibold bg-purple-50 px-2 py-1 rounded inline-block select-none">
            Không gian Học viên
          </p>
        </div>

        {/* Danh sách các Link điều hướng con sử dụng hằng số tập trung */}
        <nav className="flex flex-col gap-1 flex-1">
          {STUDENT_MENU.map((item, index) => (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 text-sm ${
                  isActive
                    ? "bg-purple-600 text-white shadow-md shadow-purple-200 transform scale-[1.02]"
                    : "text-gray-600 hover:bg-purple-50 hover:text-purple-600"
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* ==========================================
          MAIN CONTENT - NƠI HIỂN THỊ NỘI DUNG DÂN DỤNG
          ========================================== */}
      <main className="flex-1 p-8 max-w-6xl mx-auto w-full transition-all duration-300 flex flex-col gap-4">
        {/* Hộp thoại chào mừng */}
        <div className="p-6 bg-purple-50 rounded-2xl border border-purple-100 shadow-sm">
          <h2 className="text-xl font-bold text-purple-900">
            Chào mừng bạn quay lại, {user?.name || "Học viên"}!
          </h2>
          <p className="text-sm text-purple-700 mt-1">
            Hệ thống EduConnection sẵn sàng hỗ trợ bạn quản lý lịch trình học
            tập.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 min-h-[500px]">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default StudentPage;
