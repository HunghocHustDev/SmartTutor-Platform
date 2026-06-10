import React, { useState } from "react";
import StudentsPage from "./pages/StudentsPage";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import "./App.css";

function App() {
  // Quản lý trạng thái đăng nhập mô phỏng luồng nghiệp vụ
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [currentTab, setCurrentTab] = useState("students"); // Mặc định mở tab quản lý học viên

  // Hàm xử lý đăng nhập kích hoạt màn hình quản trị
  const handleLogin = (e) => {
    if (e && e.preventDefault) {
      e.preventDefault(); // 🌟 Bắt buộc phải có dòng này để tránh trang web tự F5 làm mất trạng thái đăng nhập
    }
    setIsLoggedIn(true);
  };

  // Hàm xử lý đăng xuất quay về màn hình ban đầu
  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentTab("students");
  };

  // MÀN HÌNH 1: GIAO DIỆN FORM ĐĂNG NHẬP (Chưa Login)
  // MÀN HÌNH 1: GIAO DIỆN FORM ĐĂNG NHẬP (Chưa Login)
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4" style={{ fontFamily: "system-ui, sans-serif" }}>
        <div className="bg-white p-8 rounded-2xl shadow-xl border border-slate-200 w-full max-w-md">
          
          {/* Tiêu đề */}
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">🎓</div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">Hệ Thống Gia Sư</h2>
            <p className="text-sm text-slate-500 mt-1">Cổng thông tin quản trị nội bộ dành cho nhân viên</p>
          </div>

          {/* Form Đăng Nhập - Đã bỏ bớt các ràng buộc gây kẹt nút */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Tài khoản đăng nhập</label>
              <input
                type="text"
                defaultValue="staff_admin"
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-600 font-mono text-sm"
                placeholder="Nhập tài khoản..."
              />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-slate-500 mb-1">Mật khẩu bảo mật</label>
              <input
                type="password"
                defaultValue="123456"
                className="w-full px-3.5 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-600 font-mono text-sm"
                placeholder="Nhập mật khẩu..."
              />
            </div>
            
            {/* Gợi ý hỗ trợ chấm điểm đồ án */}
            <div className="bg-blue-50 border border-blue-100 p-3 rounded-lg text-xs text-blue-700 leading-relaxed">
              💡 <strong>Thông tin Demo:</strong> Hệ thống đã kích hoạt sẵn luồng <strong>Nhân viên trung tâm (Staff Role)</strong> phục vụ chấm điểm[cite: 398, 614]. Ấn nút bên dưới để vào hệ thống ngay!
            </div>

            {/* Nút bấm loại bỏ kiểu submit truyền thống nếu cần thiết để tránh reload trang */}
            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-sm transition shadow-md shadow-blue-600/10 cursor-pointer"
            >
              Đăng nhập hệ thống &rarr;
            </button>
          </form>

        </div>
      </div>
    );
  }

  // MÀN HÌNH 2: GIAO DIỆN SAU KHI ĐĂNG NHẬP THÀNH CÔNG (Staff Dashboard Layout)
  return (
    <div className="flex bg-slate-100 min-h-screen text-slate-800" style={{ fontFamily: "system-ui, sans-serif" }}>
      
      {/* Menu Sidebar Trái */}
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      {/* Khu vực nội dung bên phải */}
      <div className="flex-1 flex flex-col min-w-0">
        
        {/* Thanh Header / Navbar */}
        <Navbar onLogout={handleLogout} />

        {/* Khối hiển thị các trang tương ứng tùy theo Tab được nhấn */}
        <main className="p-6 flex-1 overflow-y-auto">
          {currentTab === "students" ? (
            <StudentsPage />
          ) : (
            <div className="bg-white p-12 text-center border border-dashed border-slate-300 rounded-2xl text-slate-400">
              📭 Màn hình <strong>{currentTab.toUpperCase()}</strong> hiện tại đang được chuẩn bị ghép nối các API nghiệp vụ tiếp theo trong bản phân công công việc.
              <p className="text-xs text-slate-400 mt-2">Vui lòng bấm chọn Menu <strong>"Quản lý Học viên"</strong> để test luồng giao diện!</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;