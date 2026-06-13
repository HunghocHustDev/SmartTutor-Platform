import React from 'react';

export default function Navbar({ onLogout }) {
  return (
    <header className="bg-white h-16 border-b border-slate-200 px-6 flex items-center justify-between shadow-sm sticky top-0 z-10">
      {/* Tiêu đề trạng thái */}
      <div className="flex items-center space-x-2">
        <span className="inline-block w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Hệ thống trực tuyến (Chế độ Demo)
        </span>
      </div>

      {/* Khối User Profile + Đăng xuất */}
      <div className="flex items-center space-x-4">
        <div className="text-right">
          <div className="text-sm font-bold text-slate-800">Nguyễn Quang Huy</div>
          <div className="text-[11px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.25 rounded-md inline-block mt-0.5">
            🔑 Nhân Viên Trung Tâm
          </div>
        </div>
        
        {/* Nút Đăng xuất thực tế */}
        <button
          onClick={onLogout}
          className="bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 text-xs font-medium px-3 py-2 rounded-lg transition"
        >
          Đăng xuất
        </button>
      </div>
    </header>
  );
}