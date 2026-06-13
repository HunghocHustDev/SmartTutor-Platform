import React, { useState } from "react";

function Workflow() {
  const [activeTab, setActiveTab] = useState("tutor");

  const tutorSteps = [
    {
      id: "01",
      title: "Đăng ký tài khoản",
      desc: "Cập nhật hồ sơ, bằng cấp, thẻ sinh viên/giáo viên và chọn môn học có thể dạy.",
    },
    {
      id: "02",
      title: "Lựa chọn lớp phù hợp",
      desc: "Duyệt danh sách lớp mới công khai và nhấn 'Đăng ký nhận lớp' để gửi yêu cầu.",
    },
    {
      id: "03",
      title: "Xác nhận & Phỏng vấn",
      desc: "Nhân viên trung tâm kiểm tra hồ sơ, phỏng vấn ngắn và giao lớp nếu đạt yêu cầu.",
    },
    {
      id: "04",
      title: "Bắt đầu giảng dạy",
      desc: "Nhận thông tin học viên, nhận lịch dạy, cập nhật nhật ký buổi học định kỳ trên hệ thống.",
    },
  ];

  const studentSteps = [
    {
      id: "01",
      title: "Gửi nhu cầu học",
      desc: "Điền thông tin môn học, lớp, thời gian mong muốn và mức học phí dự kiến.",
    },
    {
      id: "02",
      title: "Trung tâm điều phối",
      desc: "Nhân viên tiếp nhận nhu cầu, duyệt thông tin và tìm kiếm gia sư có năng lực phù hợp nhất.",
    },
    {
      id: "03",
      title: "Học thử miễn phí",
      desc: "Học viên được sắp xếp học thử 1-2 buổi đầu tiên để đánh giá mức độ tương thích với gia sư.",
    },
    {
      id: "04",
      title: "Theo dõi & Tiến bộ",
      desc: "Chính thức học, theo dõi lịch trình, điểm danh và quản lý học phí minh bạch qua web.",
    },
  ];

  const currentSteps = activeTab === "tutor" ? tutorSteps : studentSteps;

  return (
    <section className="py-16 bg-white border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Tiêu đề chính */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Quy Trình Kết Nối Chuyên Nghiệp
          </h2>
          <p className="mt-4 text-lg text-gray-500">
            Hệ thống quản trị thông minh giúp tối giản hóa các bước từ tiếp nhận
            đến bàn giao lớp học.
          </p>

          {/* Nút chuyển đổi Tab dữ liệu */}
          <div className="mt-8 inline-flex p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setActiveTab("tutor")}
              className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "tutor"
                  ? "bg-blue-600 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Dành Cho Gia Sư
            </button>
            <button
              onClick={() => setActiveTab("student")}
              className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
                activeTab === "student"
                  ? "bg-emerald-600 text-white shadow-md"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Dành Cho Phụ Huynh / Học Viên
            </button>
          </div>
        </div>

        {/* Danh sách các bước dạng Thẻ (Cards) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {currentSteps.map((step, index) => (
            <div
              key={step.id}
              className="relative p-6 bg-gray-50 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow group"
            >
              {/* Số thứ tự nổi bật */}
              <div
                className={`text-5xl font-black mb-4 transition-colors ${
                  activeTab === "tutor"
                    ? "text-blue-100 group-hover:text-blue-200"
                    : "text-emerald-100 group-hover:text-emerald-200"
                }`}
              >
                {step.id}
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                {step.desc}
              </p>

              {/* Mũi tên kết nối giữa các thẻ (Ẩn ở màn hình mobile, hiện ở màn hình lớn) */}
              {index < 3 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10 text-gray-300 font-light text-2xl">
                  ➜
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Khối số liệu Thống kê giả lập tích hợp phía dưới */}
        <div className="mt-16 pt-12 border-t border-gray-100 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <p className="text-3xl font-extrabold text-blue-600">1,500+</p>
            <p className="text-sm font-medium text-gray-500 mt-1">
              Gia sư xác thực
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-emerald-600">3,200+</p>
            <p className="text-sm font-medium text-gray-500 mt-1">
              Học viên tiến bộ
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-indigo-600">98.5%</p>
            <p className="text-sm font-medium text-gray-500 mt-1">
              Tỷ lệ hài lòng
            </p>
          </div>
          <div>
            <p className="text-3xl font-extrabold text-amber-500">45 Phút</p>
            <p className="text-sm font-medium text-gray-500 mt-1">
              Thời gian điều phối
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Workflow;
