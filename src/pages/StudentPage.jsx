import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";

function StudentPage() {
  const location = useLocation();

  {
    location.pathname === "/student" && (
      <div className="p-6 bg-blue-50 rounded-xl mb-6">
        <h2 className="text-xl font-bold text-blue-800">
          Chào mừng bạn quay lại, {user?.name}!
        </h2>
        <p>Hệ thống EduConnection sẵn sàng hỗ trợ bạn.</p>
      </div>
    );
  }

  // Danh sách 4 mục chức năng hiển thị ở Sidebar (đã đồng bộ thứ tự chuẩn)
  const sidebarSubItems = [
    { label: "Tạo yêu cầu", path: "/student/requests", icon: "➕" },
    { label: "Lớp của tôi", path: "/student/classes", icon: "📚" },
    { label: "Lịch học", path: "/student/schedule", icon: "📅" },
    { label: "Học phí", path: "/student/tuition", icon: "💵" },
  ];

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
          <p className="text-xs text-purple-600 font-semibold bg-purple-50 px-2 py-1 rounded inline-block">
            Không gian Học viên
          </p>
        </div>

        {/* Danh sách các Link điều hướng con */}
        <nav className="flex flex-col gap-1 flex-1">
          {sidebarSubItems.map((item, index) => {
            // Sử dụng startsWith để giữ trạng thái active chính xác hơn nếu có đường dẫn con sâu hơn
            const isSubActive = location.pathname.startsWith(item.path);

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
      </aside>

      {/* ==========================================
          MAIN CONTENT - NƠI HIỂN THỊ NỘI DUNG CÁC FILE CON
          ========================================== */}
      <main className="flex-1 p-8 max-w-6xl mx-auto w-full transition-all duration-300">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 min-h-[500px]">
          {/* Outlet nạp giao diện động của 4 file mục con */}
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default StudentPage;
