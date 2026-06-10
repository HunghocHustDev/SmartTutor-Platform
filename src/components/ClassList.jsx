import React, { useRef } from "react";

// ==========================================
// 1. DỮ LIỆU ẢO (MOCK DATA) - ĐỂ RIÊNG Ở ĐÂY
// ==========================================
// 💡 SAU NÀY KẾT NỐI API THÌ XÓA MẢNG NÀY ĐI.
// Thay vào đó, bạn sẽ dùng useEffect gọi API: axios.get('/api/classes').then(res => setClasses(res.data))
const MOCK_CLASSES = [
  {
    id: "L001",
    subject: "Toán học (Ôn thi THPT Quốc Gia)",
    grade: "Lớp 12",
    fee: "250.000đ/buổi",
    address: "Quận Hai Bà Trưng, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L002",
    subject: "Tiếng Anh Giao Tiếp Cơ Bản",
    grade: "Người đi làm",
    fee: "300.000đ/buổi",
    address: "Quận Cầu Giấy, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "3 buổi/tuần",
  },
  {
    id: "L003",
    subject: "Vật Lý (Luyện thi vào 10)",
    grade: "Lớp 9",
    fee: "200.000đ/buổi",
    address: "Quận Đống Đa, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L004",
    subject: "Hóa Học Cơ Bản & Nâng Cao",
    grade: "Lớp 11",
    fee: "220.000đ/buổi",
    address: "Quận Ba Đình, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L005",
    subject: "Lập trình Python Kid",
    grade: "Lớp 7",
    fee: "350.000đ/buổi",
    address: "Quận Nam Từ Liêm, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "1 buổi/tuần",
  },
  {
    id: "L006",
    subject: "Ngữ Văn (Bồi dưỡng học sinh giỏi)",
    grade: "Lớp 9",
    fee: "200.000đ/buổi",
    address: "Quận Hoàn Kiếm, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
];

export default function ClassList({ onClassClick }) {
  // Dùng useRef để điều khiển cuộn thanh trượt bằng nút bấm
  const scrollContainerRef = useRef(null);

  // Hàm xử lý khi bấm nút trượt sang trái/phải
  const handleScroll = (direction) => {
    if (scrollContainerRef.current) {
      const cardWidth = 360 + 24; // Chiều rộng của 1 card + gap
      const scrollAmount = direction === "left" ? -cardWidth : cardWidth;
      scrollContainerRef.current.scrollBy({
        left: scrollAmount,
        behavior: "smooth",
      });
    }
  };

  // Hàm giả lập đăng ký nhận lớp khi chưa có backend
  const handleApplyFake = (cls) => {
    // Đọc user hiện tại từ localStorage xem là ai đang bấm đăng ký
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user || user.role !== "tutor") {
      alert(
        "Chức năng 'Đăng Ký Nhận Lớp' chỉ dành riêng cho tài khoản hệ Vai trò: Gia sư! Vui lòng chọn tài khoản Gia sư ở nút Test Roles trên Header để thử nghiệm.",
      );
      return;
    }

    // Nếu đúng là Gia sư, xử lý tiếp
    alert(
      `[MOCK SUCCESS] Gia sư "${user.name}" đã gửi yêu cầu nhận lớp mã: ${cls.id} (${cls.subject}).\n\n💡 GIẢI THÍCH BACKEND: Sau này chỗ này bạn sẽ gửi một yêu cầu API: axios.post('/api/requests/apply', { tutorId: user.id, classId: cls.id }) lên server để lưu vào database và thông báo cho Admin duyệt.`,
    );

    if (onClassClick) {
      onClassClick(cls);
    }
  };

  return (
    <section className="px-[8%] py-[60px] bg-white relative">
      {/* Tiêu đề vùng hiển thị */}
      <div className="flex justify-between items-end mb-[30px]">
        <div>
          <h2 className="text-[28px] font-bold text-gray-900 m-0 mb-2">
            Lớp Học Mới Đang Tìm Gia Sư
          </h2>
          <p className="text-base text-gray-500 m-0">
            Các lớp học vừa được đăng ký, nhận lớp ngay hôm nay
          </p>
        </div>

        {/* Nút bấm điều hướng trượt ngang */}
        <div className="flex gap-2.5">
          <button
            onClick={() => handleScroll("left")}
            className="w-10 h-10 rounded-full border border-solid border-gray-300 bg-white text-lg cursor-pointer flex justify-center items-center shadow-[0_2px_4px_rgba(0,0,0,0.05)] select-none transition-all duration-200 active:scale-95 hover:bg-gray-50"
          >
            ←
          </button>
          <button
            onClick={() => handleScroll("right")}
            className="w-10 h-10 rounded-full border border-solid border-gray-300 bg-white text-lg cursor-pointer flex justify-center items-center shadow-[0_2px_4px_rgba(0,0,0,0.05)] select-none transition-all duration-200 active:scale-95 hover:bg-gray-50"
          >
            →
          </button>
        </div>
      </div>

      {/* Vùng chứa danh sách lớp có hỗ trợ scroll ngang ẩn thanh cuộn */}
      {/* Mẹo ẩn thanh cuộn: Thêm thuộc tính overflow-x-auto và style ẩn ở file CSS tổng */}
      <div
        ref={scrollContainerRef}
        className="flex gap-6 overflow-x-auto scroll-smooth pb-4 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
      >
        {MOCK_CLASSES.map((cls) => (
          <div
            key={cls.id}
            className="flex-[0_0_calc(33.333%-16px)] min-w-[340px] bg-gray-50 border border-solid border-gray-200 rounded-xl p-6 box-border flex flex-col justify-between shadow-[0_4px_6px_-1px_rgba(0,0,0,0.02)]"
          >
            <div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-[13px] font-semibold text-gray-400">
                  Mã: {cls.id}
                </span>
                <span className="bg-amber-100 text-amber-600 px-2.5 py-1 rounded-full text-xs font-semibold">
                  {cls.status}
                </span>
              </div>

              <h3 className="text-lg font-bold text-gray-800 m-0 mb-4 leading-normal h-[54px] overflow-hidden line-clamp-2">
                {cls.subject}
              </h3>

              <div className="space-y-2.5">
                <div className="flex justify-between text-sm leading-normal">
                  <span className="text-gray-500">Trình độ:</span>
                  <span className="text-gray-700 font-medium text-right max-w-[70%]">
                    {cls.grade}
                  </span>
                </div>
                <div className="flex justify-between text-sm leading-normal">
                  <span className="text-gray-500">Học phí:</span>
                  <span className="text-red-500 font-bold text-right max-w-[70%]">
                    {cls.fee}
                  </span>
                </div>
                <div className="flex justify-between text-sm leading-normal">
                  <span className="text-gray-500">Lịch học:</span>
                  <span className="text-gray-700 font-medium text-right max-w-[70%]">
                    {cls.frequency}
                  </span>
                </div>
                <div className="flex justify-between text-sm leading-normal">
                  <span className="text-gray-500">Địa điểm:</span>
                  <span className="text-gray-700 font-medium text-right max-w-[70%]">
                    {cls.address}
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={() => handleApplyFake(cls)}
              className="mt-5 w-full p-3 bg-blue-600 text-white border-none rounded-lg text-sm font-bold cursor-pointer text-center hover:bg-blue-700 transition-colors duration-200 active:scale-[0.98]"
            >
              Đăng Ký Nhận Lớp
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
