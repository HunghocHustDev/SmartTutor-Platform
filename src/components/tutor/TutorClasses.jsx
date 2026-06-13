import React, { useState } from "react";

function TutorClasses() {
  // 1. DỮ LIỆU GIẢ LẬP DANH SÁCH LỚP DẠY CỦA GIA SƯ
  const [classes] = useState([
    {
      id: "LHP042",
      subject: "Toán học 12 (Ôn thi THPT Quốc Gia)",
      studentName: "Nguyễn Hoàng Nam",
      phone: "0912.345.xxx",
      address: "Số 1 Đại Cồ Việt, Bách Khoa, Hai Bà Trưng, Hà Nội",
      scheduleType: "Trực tiếp (Offline)",
      sessionsPerWeek: 2,
      timeSlot: "Thứ 3, Thứ 5 (18:00 - 20:00)",
      salary: "350,000đ / buổi",
      startDate: "15/05/2026",
      status: "active", // active: Đang dạy, completed: Đã kết thúc
    },
    {
      id: "LHP109",
      subject: "Luyện thi IELTS - Kỹ năng Writing & Speaking",
      studentName: "Trần Thu Hà",
      phone: "0988.777.xxx",
      address: "Học trực tuyến qua Google Meet",
      scheduleType: "Trực tuyến (Online)",
      sessionsPerWeek: 3,
      timeSlot: "Thứ 2, Thứ 4, Thứ 6 (19:30 - 21:30)",
      salary: "400,000đ / buổi",
      startDate: "02/04/2026",
      status: "active",
    },
    {
      id: "LHP015",
      subject: "Vật lý lớp 11 (Cơ bản & Nâng cao)",
      studentName: "Lê Minh Triết",
      phone: "0904.555.xxx",
      address: "128 Trần Đại Nghĩa, Hai Bà Trưng, Hà Nội",
      scheduleType: "Trực tiếp (Offline)",
      sessionsPerWeek: 1,
      timeSlot: "Chủ Nhật (08:30 - 10:30)",
      salary: "300,000đ / buổi",
      startDate: "10/01/2026",
      status: "completed",
    },
  ]);

  // Bộ lọc trạng thái lớp học (Tất cả / Đang dạy / Đã kết thúc)
  const [filterStatus, setFilterStatus] = useState("all");

  const filteredClasses = classes.filter((cls) => {
    if (filterStatus === "all") return true;
    return cls.status === filterStatus;
  });

  // Đếm nhanh số lượng để hiển thị lên các thẻ thống kê tổng quan
  const totalActive = classes.filter((c) => c.status === "active").length;
  const totalCompleted = classes.filter((c) => c.status === "completed").length;

  return (
    <div className="tutor-classes-container space-y-6 animate-fade-in">
      {/* 2. KHỐI THỐNG KÊ SỐ LIỆU NHANH (Tương tự ảnh Học viên nhưng đổi tông màu) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">
              Tổng số lớp nhận dạy
            </p>
            <h3 className="text-3xl font-bold text-gray-800 mt-1">
              {classes.length}
            </h3>
          </div>
          <div className="p-3 rounded-full bg-emerald-50 text-emerald-600 text-2xl">
            💼
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">
              Lớp đang đảm nhận
            </p>
            <h3 className="text-3xl font-bold text-emerald-600 mt-1">
              {totalActive}
            </h3>
          </div>
          <div className="p-3 rounded-full bg-amber-50 text-amber-600 text-2xl">
            ⚡
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-500">
              Lớp đã hoàn thành
            </p>
            <h3 className="text-3xl font-bold text-gray-400 mt-1">
              {totalCompleted}
            </h3>
          </div>
          <div className="p-3 rounded-full bg-gray-50 text-gray-400 text-2xl">
            ✅
          </div>
        </div>
      </div>

      {/* 3. THANH BỘ LỌC TÌM KIẾM TRẠNG THÁI */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col sm:flex-row justify-between items-center gap-4">
        <h2 className="text-lg font-bold text-gray-800">
          Danh Sách Lớp Học Quản Lý
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setFilterStatus("all")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              filterStatus === "all"
                ? "bg-emerald-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-250"
            }`}
          >
            Tất cả ({classes.length})
          </button>
          <button
            onClick={() => setFilterStatus("active")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              filterStatus === "active"
                ? "bg-emerald-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-250"
            }`}
          >
            Đang dạy ({totalActive})
          </button>
          <button
            onClick={() => setFilterStatus("completed")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              filterStatus === "completed"
                ? "bg-emerald-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-600 hover:bg-gray-250"
            }`}
          >
            Đã hoàn thành ({totalCompleted})
          </button>
        </div>
      </div>

      {/* 4. GRID HIỂN THỊ DANH SÁCH LỚP DƯỚI DẠNG CARD CHUYÊN NGHIỆP */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredClasses.length > 0 ? (
          filteredClasses.map((cls) => (
            <div
              key={cls.id}
              className={`bg-white rounded-xl shadow-sm border p-6 flex flex-col justify-between transition hover:shadow-md relative overflow-hidden ${
                cls.status === "completed"
                  ? "border-gray-200 opacity-75"
                  : "border-emerald-100"
              }`}
            >
              {/* Nhãn trạng thái góc phải */}
              <div className="absolute top-4 right-4">
                {cls.status === "active" ? (
                  <span className="bg-emerald-100 text-emerald-800 text-xs font-semibold px-2.5 py-1 rounded-full">
                    ● Đang diễn ra
                  </span>
                ) : (
                  <span className="bg-gray-100 text-gray-600 text-xs font-semibold px-2.5 py-1 rounded-full">
                    ✓ Đã kết thúc
                  </span>
                )}
              </div>

              {/* Nội dung chính của lớp */}
              <div className="space-y-4">
                <div>
                  <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
                    Mã lớp: {cls.id}
                  </span>
                  <h3 className="text-[18px] font-bold text-gray-800 mt-2 leading-snug">
                    {cls.subject}
                  </h3>
                </div>

                {/* Chi tiết thông tin */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600 border-t border-b border-gray-50 py-3">
                  <div>
                    <p className="text-xs text-gray-400 font-medium uppercase tracking-wider">
                      Học viên phụ trách
                    </p>
                    <p className="font-semibold text-gray-800 mt-0.5">
                      {cls.studentName}
                    </p>
                    <p className="text-xs text-gray-500">SĐT: {cls.phone}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 font-medium uppercase tracking-wider">
                      Hình thức học
                    </p>
                    <p className="font-semibold text-gray-800 mt-0.5">
                      {cls.scheduleType}
                    </p>
                    <p className="text-xs text-gray-500">
                      Mức lương:{" "}
                      <span className="text-emerald-600 font-bold">
                        {cls.salary}
                      </span>
                    </p>
                  </div>
                </div>

                <div className="space-y-1.5 text-sm text-gray-600">
                  <div className="flex items-start gap-2">
                    <span className="mt-0.5">📅</span>
                    <p>
                      <strong>Lịch dạy cố định:</strong> {cls.timeSlot} (
                      {cls.sessionsPerWeek} buổi/tuần)
                    </p>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="mt-0.5">📍</span>
                    <p className="line-clamp-2">
                      <strong>Địa điểm/Liên kết:</strong> {cls.address}
                    </p>
                  </div>
                  <div className="flex items-start gap-2 text-xs text-gray-400">
                    <span>⏱</span>
                    <p>Ngày bắt đầu nhận lớp: {cls.startDate}</p>
                  </div>
                </div>
              </div>

              {/* Nút hành động tiện ích bổ sung tương tác phục vụ chấm điểm */}
              <div className="mt-6 pt-4 border-t border-gray-100 flex gap-2">
                <button
                  className="flex-1 text-center bg-emerald-50 text-emerald-600 hover:bg-emerald-100 text-sm font-medium py-2 rounded-md transition"
                  onClick={() => alert(`Xem tài liệu bài giảng lớp ${cls.id}`)}
                >
                  📁 Tài liệu lớp học
                </button>
                <button
                  className="flex-1 text-center bg-emerald-600 text-white hover:bg-emerald-700 text-sm font-medium py-2 rounded-md transition shadow-sm"
                  onClick={() =>
                    alert(
                      `Chuyển đến màn hình điểm danh/báo cáo của lớp ${cls.id}`,
                    )
                  }
                >
                  📝 Điểm danh ngay
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full bg-white p-12 rounded-xl text-center border border-gray-100">
            <p className="text-gray-400 text-lg">
              Không tìm thấy lớp học nào ở trạng thái này.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default TutorClasses;
