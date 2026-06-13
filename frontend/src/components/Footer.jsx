import React from "react";

function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Cột 1: Giới thiệu trung tâm */}
        <div>
          <div className="flex items-center space-x-2 text-white mb-4">
            <span className="text-2xl font-black tracking-wider text-blue-500">
              GS
            </span>
            <span className="text-xl font-bold">MANAGEMENT</span>
          </div>
          <p className="text-sm text-gray-400 leading-relaxed">
            Hệ thống quản trị điều phối gia sư toàn diện. Giải pháp kết nối tri
            thức, tối ưu hóa quy trình dạy và học trực tuyến, nâng cao chất
            lượng quản lý nội bộ trung tâm.
          </p>
        </div>

        {/* Cột 2: Thông tin liên hệ hành chính */}
        <div>
          <h3 className="text-white font-semibold text-base mb-4 uppercase tracking-wider">
            Thông Tin Liên Hệ
          </h3>
          <ul className="space-y-3 text-sm">
            <li className="flex items-start">
              <span className="mr-2">📍</span>
              <span>Khu đô thị Đại học Quốc gia, TP. Hồ Chí Minh / Hà Nội</span>
            </li>
            <li className="flex items-center">
              <span className="mr-2">📞</span>
              <span>Hotline: 1900 xxxx (08:00 - 21:00)</span>
            </li>
            <li className="flex items-center">
              <span className="mr-2">✉️</span>
              <span>Email: lienhe@trungtamgiasu.edu.vn</span>
            </li>
          </ul>
        </div>

        {/* Cột 3: Gợi ý các Actor kiểm thử nhanh cho Giảng viên */}
        <div>
          <h3 className="text-white font-semibold text-base mb-4 uppercase tracking-wider">
            Tài khoản Demo Hội đồng
          </h3>
          <p className="text-xs text-gray-500 mb-3">
            Demo hiện dùng các vai trò nghiệp vụ thật của hệ thống:
          </p>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-gray-800 rounded text-xs text-blue-400 font-mono">
              Role: staff (Nhân viên)
            </span>
            <span className="px-2 py-1 bg-gray-800 rounded text-xs text-emerald-400 font-mono">
              Role: tutor (Gia sư)
            </span>
            <span className="px-2 py-1 bg-gray-800 rounded text-xs text-purple-400 font-mono">
              Role: student (Học viên)
            </span>
          </div>
        </div>
      </div>

      {/* Dòng bản quyền chân trang */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8 pt-8 border-t border-gray-800 text-center text-xs text-gray-500">
        © {new Date().getFullYear()} Đề tài Báo cáo Bài tập lớn - Hệ thống quản
        trị trung tâm gia sư nội bộ. All rights reserved.
      </div>
    </footer>
  );
}

export default Footer;
