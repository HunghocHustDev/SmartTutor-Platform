import React from "react";
import bgImage from "../assets/Bg.png";

export default function Banner({ onFindTutorClick, onBeTutorClick }) {
  // Đọc dữ liệu user ảo từ localStorage để Banner biết mình nên hiện nội dung gì
  const user = JSON.parse(localStorage.getItem("user")) || null;

  // =========================================================================
  // TRƯỜNG HỢP 1: CHƯA ĐĂNG NHẬP (Khách vãng lai) -> Hiện Banner quảng cáo gốc của bạn
  // =========================================================================
  if (!user || !user.role) {
    return (
      <section className="flex justify-between items-center px-[8%] py-[60px] bg-gray-100 min-h-[550px] gap-10 flex-wrap">
        {/* Khối nội dung bên trái */}
        <div className="flex-1 min-w-[320px] flex flex-col items-start">
          <span className="bg-blue-50 text-blue-600 px-3.5 py-1.5 rounded-full text-sm font-semibold mb-[15px]">
            Nền Tảng Uy Tín Toàn Quốc
          </span>

          <h1 className="text-[48px] font-extrabold text-gray-900 leading-[1.2] m-0 mb-[15px]">
            Tìm Gia Sư Giỏi,
            <br />
            Nâng Tầm <span className="text-orange-500">Tri Thức</span>
          </h1>

          {/* Đánh giá 5 sao */}
          <div className="flex items-center gap-2 mb-5">
            <span className="text-amber-400 text-xl">★★★★★</span>
            <span className="text-gray-600 font-medium">
              4.9/5 (15,000+ phụ huynh tin dùng)
            </span>
          </div>

          <p className="text-base text-gray-600 leading-relaxed mb-[30px] max-w-[540px] text-justify">
            Kết nối học viên với hơn 5,000+ Gia sư chất lượng cao, sinh viên
            xuất sắc từ các trường đại học top đầu (Bách Khoa, Ngoại Thương, Sư
            Phạm). Học thử miễn phí 2 buổi, cam kết tiến bộ rõ rệt sau 1 tháng.
          </p>

          {/* Các nút bấm tương tác */}
          <div className="flex gap-[15px] flex-wrap">
            <button
              onClick={onFindTutorClick}
              className="px-7 py-3.5 bg-blue-600 text-white border-none rounded-8px text-base font-bold cursor-pointer transition-transform duration-200 active:scale-95 shadow-[0_4px_6px_-1px_rgba(26,86,219,0.3)] hover:bg-blue-700 rounded-lg"
            >
              Tìm Gia Sư Ngay
            </button>
            <button
              onClick={onBeTutorClick}
              className="px-7 py-3.5 bg-white text-blue-600 border-2 border-solid border-blue-600 rounded-lg text-base font-bold cursor-pointer transition-colors duration-200 hover:bg-blue-50"
            >
              Trở Thành Gia Sư
            </button>
          </div>
        </div>

        {/* Khối hình ảnh nổi bật bên phải */}
        <div className="flex-1 min-w-[320px] flex justify-center items-center">
          <div className="relative w-100% max-w-[480px] h-[360px] rounded-2xl overflow-hidden shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1),0_10px_10px_-5px_rgba(0,0,0,0.04)]">
            <img
              src={bgImage}
              alt="Gia sư và học viên"
              className="w-full h-full object-cover"
            />
            <div className="absolute top-5 left-5 bg-red-500 text-white px-3.5 py-1.5 rounded font-bold text-[13px] uppercase tracking-wide">
              Lớp Học 1 kèm 1
            </div>
          </div>
        </div>
      </section>
    );
  }

  // =========================================================================
  // TRƯỜNG HỢP 2: ĐÃ ĐĂNG NHẬP -> Biến thành Banner Dashboard mini chào mừng từng Role
  // =========================================================================
  const config = {
    student: {
      bg: "bg-gradient-to-r from-purple-600 to-indigo-700",
      title: `Xin chào học viên, ${user.name}! 👋`,
      subtitle:
        "Hôm nay bạn muốn học môn gì nào? Hãy theo dõi lịch học bên dưới hoặc tạo yêu cầu mới nhé.",
      actionText: "Gửi nhu cầu tìm gia sư mới",
      actionClick: onFindTutorClick,
    },
    tutor: {
      bg: "bg-gradient-to-r from-emerald-600 to-teal-700",
      title: `Chào mừng Gia sư, ${user.name}! 🎓`,
      subtitle:
        "Đừng quên cập nhật điểm danh và nhật ký buổi học sau khi dạy xong để hệ thống tính học phí chính xác nhé.",
      actionText: "Cập nhật lịch rảnh",
      actionClick: onBeTutorClick,
    },
    admin: {
      bg: "bg-gradient-to-r from-slate-800 to-slate-900",
      title: `Trung Tâm Điều Phối - Nhân Viên: ${user.name} 💻`,
      subtitle:
        "Hệ thống đang có các nhu cầu học mới cần kết nối. Kiểm tra và phân công gia sư ngay.",
      actionText: "Vào trang xử lý nghiệp vụ",
      actionClick: () => alert("Chuyển hướng đến bảng quản lý admin"),
    },
  };

  const currentView = config[user.role] || config.student;

  return (
    <section
      className={`px-[8%] py-10 text-white ${currentView.bg} shadow-md transition-all`}
    >
      <div className="max-w-4xl">
        <h1 className="text-3xl font-bold mb-2">{currentView.title}</h1>
        <p className="text-gray-100 opacity-90 max-w-2xl text-sm leading-relaxed mb-4">
          {currentView.subtitle}
        </p>
        <button
          onClick={currentView.actionClick}
          className="px-4 py-2 bg-white text-gray-800 text-xs font-bold rounded-md shadow hover:bg-gray-100 transition-colors cursor-pointer"
        >
          {currentView.actionText} →
        </button>
      </div>
    </section>
  );
}
