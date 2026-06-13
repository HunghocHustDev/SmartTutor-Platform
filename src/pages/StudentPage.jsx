import React from "react";

import { Link, Outlet, useLocation } from "react-router-dom";

function StudentPage({ currentUser }) {
  const location = useLocation();

  // Danh sách 4 mục chức năng hiển thị ở Bảng điều khiển Sidebar

  const sidebarSubItems = [
    { label: "Tạo yêu cầu", path: "/student/request", icon: "➕" },

    { label: "Lớp của tôi", path: "/student/classes", icon: "📚" },

    { label: "Lịch học", path: "/student/schedule", icon: "📅" },

    { label: "Học phí", path: "/student/tuition", icon: "💵" },
  ];

  return (
    <div className="flex min-h-[calc(100vh-70px)] bg-gray-50">
      {/* ==========================================

          SIDEBAR - BẢNG ĐIỀU KHIỂN DỌC BÊN TRÁI

          ========================================== */}

      <aside className="w-64 bg-white border-r border-gray-200 p-5 flex flex-col gap-6 shrink-0 shadow-sm">
        <div className="pb-3 border-b border-gray-100">
          <h3 className="text-xs font-bold text-gray-400 tracking-wider uppercase mb-1">
            Bảng điều khiển
          </h3>

          <p className="text-xs text-purple-600 font-semibold bg-purple-50 px-2 py-1 rounded inline-block">
            Không gian Học viên
          </p>
        </div>

        {/* Danh sách các Link điều hướng con */}

        <nav className="flex flex-col gap-1 flex-1">
          {sidebarSubItems.map((item, index) => {
            // Kiểm tra link con nào đang trùng với đường dẫn hiện tại để kích hoạt màu nền

            const isSubActive = location.pathname === item.path;

            return (
              <Link
                key={index}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 text-sm ${
                  isSubActive
                    ? "bg-purple-600 text-white shadow-md shadow-purple-200 transform scale-[1.02]"
                    : "text-gray-600 hover:bg-purple-50 hover:text-purple-600"
                }`}
              >
                <span className="text-base">{item.icon}</span>

                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Widget nhỏ hiển thị nhanh thông tin tài khóa */}

        <div className="bg-gray-50 border border-gray-100 p-3 rounded-xl text-center">
          <p className="text-[11px] text-gray-400 font-medium uppercase">
            Mã học viên
          </p>

          <p className="text-sm font-bold text-gray-700 font-mono">
            HV-{currentUser?.id || "001"}
          </p>
        </div>
      </aside>

      {/* ==========================================

          MAIN NỘI DUNG ĐỘNG BÊN PHẢI (CHỨA OUTLET)

          ========================================== */}

      <main className="flex-1 p-8 max-w-6xl mx-auto w-full transition-all duration-300">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 min-h-[500px]">
          {/* Outlet giữ vai trò nạp tầng giao diện động (request, classes, schedule, tuition) */}

          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default StudentPage;
