import React from 'react';

export default function Sidebar({ currentTab, setCurrentTab }) {
  // Danh sách Menu dựa theo đặc tả luồng Nhân viên trung tâm
  const menuItems = [
    { id: 'dashboard', name: '📊 Tổng quan (Dashboard)' },
    { id: 'students', name: '👥 Quản lý Học viên' },
    { id: 'tutors', name: '👨‍🏫 Quản lý Gia sư' },
    { id: 'requests', name: '⏳ Xử lý Nhu cầu học' },
    { id: 'classes', name: '🏫 Quản lý Lớp học' },
    { id: 'invoices', name: '💰 Quản lý Học phí' },
  ];

  return (
    <div className="w-64 bg-slate-900 text-slate-300 flex flex-col h-screen sticky top-0 shadow-xl">
      {/* Logo Trung tâm */}
      <div className="p-5 border-b border-slate-800 bg-slate-950 flex items-center space-x-2">
        <span className="text-xl">🎓</span>
        <h1 className="text-sm font-bold text-white tracking-wider uppercase">SmartTutor Admin</h1>
      </div>

      {/* Menu items */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest px-3 mb-2">Menu Nhân Viên</p>
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentTab(item.id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 flex items-center justify-between ${
              currentTab === item.id
                ? 'bg-blue-600 text-white shadow-md shadow-blue-600/10'
                : 'hover:bg-slate-800 hover:text-slate-100'
            }`}
          >
            <span>{item.name}</span>
            {currentTab === item.id && <span className="text-xs">▶</span>}
          </button>
        ))}
      </nav>

      {/* Thông tin phiên đăng nhập giả lập */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50 text-xs text-slate-500">
        <p>Đang chạy thử nghiệm v1.0</p>
        <p className="font-mono mt-0.5">localhost:5173</p>
      </div>
    </div>
  );
}