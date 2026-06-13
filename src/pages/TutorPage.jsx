import React, { useState } from "react";

// IMPORT ĐÚNG 3 CHỨC NĂNG CON HIỆN TẠI CỦA BẠN

import TutorClasses from "../components/tutor/TutorClasses";

import TutorSchedule from "../components/tutor/TutorSchedule";

import TutorReports from "../components/tutor/TutorReports";

function TutorPage({ currentUser }) {
  // 1. QUẢN LÝ TAB HOẠT ĐỘNG TRONG SIDEBAR (Giữ nguyên logic của bạn)

  const [activeTab, setActiveTab] = useState("schedule");

  return (
    <div className="w-full bg-gray-50 flex flex-col font-sans">
      {/* BANNER CHÀO MỪNG GIA SƯ (Tối ưu hóa: lấy trực tiếp dữ liệu từ currentUser tổng) */}

      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 text-white py-8 px-10 shadow-sm">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">
              Xin chào, {currentUser?.name || "Gia sư"} 👋
            </h1>

            <p className="text-emerald-100 text-sm mt-1">
              Chào mừng bạn đến với không gian quản trị giảng dạy của
              **GiaSưTâmTâm**. Hãy cập nhật lịch trình và nhật ký lớp học đúng
              hạn nhé!
            </p>
          </div>

          <div className="bg-emerald-500/20 border border-emerald-300/30 text-white text-xs font-mono px-3 py-1.5 rounded-lg">
            🔑 Mã số: GS-{currentUser?.id || "001"}
          </div>
        </div>
      </div>

      {/* KHU VỰC ĐIỀU HƯỚNG TAB & NỘI DUNG CHỨC NĂNG */}

      <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col md:flex-row gap-8">
        {/* SIDEBAR - MENU ĐIỀU HƯỚNG BÊN TRÁI (Giữ nguyên cấu trúc giao diện bạn thích) */}

        <aside className="w-full md:w-64 flex-shrink-0">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 space-y-1 sticky top-24">
            <p className="text-[11px] font-bold text-gray-400 uppercase tracking-wider px-3 mb-2">
              Bảng điều khiển
            </p>

            {/* Tab 1: Lịch Dạy */}

            <button
              onClick={() => setActiveTab("schedule")}
              className={`w-full text-left px-4 py-3 rounded-lg text-sm font-semibold transition flex items-center gap-3 ${
                activeTab === "schedule"
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-200 transform scale-[1.01]"
                  : "text-gray-600 hover:bg-gray-50 hover:text-emerald-600"
              }`}
            >
              <span className="text-base">📅</span> Lịch dạy tuần này
            </button>

            {/* Tab 2: Lớp Học */}

            <button
              onClick={() => setActiveTab("classes")}
              className={`w-full text-left px-4 py-3 rounded-lg text-sm font-semibold transition flex items-center gap-3 ${
                activeTab === "classes"
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-200 transform scale-[1.01]"
                  : "text-gray-600 hover:bg-gray-50 hover:text-emerald-600"
              }`}
            >
              <span className="text-base">💼</span> Lớp học đang dạy
            </button>

            {/* Tab 3: Báo Cáo / Nhật Ký */}

            <button
              onClick={() => setActiveTab("reports")}
              className={`w-full text-left px-4 py-3 rounded-lg text-sm font-semibold transition flex items-center gap-3 ${
                activeTab === "reports"
                  ? "bg-emerald-600 text-white shadow-md shadow-emerald-200 transform scale-[1.01]"
                  : "text-gray-600 hover:bg-gray-50 hover:text-emerald-600"
              }`}
            >
              <span className="text-base">📝</span> Nhật ký & Điểm danh
            </button>
          </div>
        </aside>

        {/* NỘI DUNG CHỦ ĐỘNG HIỂN THỊ BÊN PHẢI (Nạp các component con của bạn) */}

        <main className="flex-1 bg-white p-6 rounded-xl shadow-sm border border-gray-100 min-h-[450px]">
          {activeTab === "schedule" && <TutorSchedule />}

          {activeTab === "classes" && <TutorClasses />}

          {activeTab === "reports" && <TutorReports />}
        </main>
      </div>
    </div>
  );
}

export default TutorPage;
