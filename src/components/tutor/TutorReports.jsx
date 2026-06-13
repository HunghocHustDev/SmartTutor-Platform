import React, { useState } from "react";

function TutorReports() {
  // 1. DANH SÁCH LỚP GIA SƯ ĐANG DẠY (Để đổ vào thẻ select)
  const [tutorClasses] = useState([
    {
      id: "LHP042",
      subject:
        "Toán học 12 (Ôn thi THPT Quốc Gia) - Học viên: Nguyễn Hoàng Nam",
    },
    {
      id: "LHP109",
      subject: "Luyện thi IELTS (Writing & Speaking) - Học viên: Trần Thu Hà",
    },
  ]);

  // 2. DỮ LIỆU GIẢ LẬP LỊCH SỬ CÁC BUỔI HỌC ĐÃ BÁO CÁO
  const [reports, setReports] = useState([
    {
      id: "REP001",
      classId: "LHP042",
      date: "09/06/2026",
      slot: "18:00 - 20:00",
      attendance: "Đi học đủ",
      content: "Chữa đề thi thử số 5, ôn tập kỹ phần Khảo sát hàm số nâng cao.",
      homework: "Làm tiếp bài tập mặt nón, mặt trụ trong file PDF.",
    },
    {
      id: "REP002",
      classId: "LHP109",
      date: "10/06/2026",
      slot: "19:30 - 21:30",
      attendance: "Nghỉ có phép",
      content:
        "Học viên xin nghỉ ốm, đã hẹn lịch học bù vào Chủ Nhật tuần này.",
      homework: "Không có",
    },
  ]);

  // State quản lý Form nhập dữ liệu mới
  const [selectedClass, setSelectedClass] = useState("");
  const [reportDate, setReportDate] = useState("");
  const [attendanceStatus, setAttendanceStatus] = useState("Đi học đủ");
  const [lessonContent, setLessonContent] = useState("");
  const [homeworkContent, setHomeworkContent] = useState("");

  // Hàm xử lý khi bấm nút "Gửi báo cáo"
  const handleSubmitReport = (e) => {
    e.preventDefault();

    if (!selectedClass || !reportDate || !lessonContent) {
      alert(
        "Vui lòng điền đầy đủ các thông tin cốt lõi (Lớp học, Ngày học, Nội dung)!",
      );
      return;
    }

    const newReport = {
      id: `REP${Math.floor(100 + Math.random() * 900)}`, // Tạo mã báo cáo ngẫu nhiên để test UI
      classId: selectedClass,
      date: new Date(reportDate).toLocaleDateString("vi-VN"),
      slot: "Theo lịch cố định",
      attendance: attendanceStatus,
      content: lessonContent,
      homework: homeworkContent || "Không có",
    };

    // Thêm báo cáo mới lên đầu danh sách hiển thị
    setReports([newReport, ...reports]);
    alert("Gửi nhật ký buổi học lên trung tâm thành công!");

    // Reset lại form trống
    setReportDate("");
    setLessonContent("");
    setHomeworkContent("");
  };

  return (
    <div className="tutor-reports-container space-y-8">
      {/* TIÊU ĐỀ */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h2 className="text-xl font-bold text-gray-800">
          📝 Nhật ký & Điểm danh buổi học
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Gia sư bắt buộc phải cập nhật báo cáo sau mỗi buổi dạy để trung tâm
          theo dõi tiến độ và làm căn cứ tính lương cuối tháng.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* KHỐI TRÁI: FORM CẬP NHẬT BUỔI HỌC MỚI (Chiếm 1 cột) */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-emerald-100 lg:col-span-1">
          <h3 className="text-base font-bold text-gray-800 border-b border-gray-100 pb-3 mb-4 flex items-center gap-2">
            <span className="text-emerald-600">➕</span> Báo cáo buổi học mới
          </h3>

          <form onSubmit={handleSubmitReport} className="space-y-4">
            {/* Chọn lớp học */}
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">
                Chọn lớp dạy *
              </label>
              <select
                className="w-full bg-gray-50 border border-gray-200 rounded-md p-2 text-sm focus:outline-emerald-500"
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
              >
                <option value="">-- Chọn lớp học --</option>
                {tutorClasses.map((c) => (
                  <option key={c.id} value={c.id}>
                    [{c.id}] {c.subject}
                  </option>
                ))}
              </select>
            </div>

            {/* Chọn ngày dạy */}
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">
                Ngày dạy học *
              </label>
              <input
                type="date"
                className="w-full bg-gray-50 border border-gray-200 rounded-md p-2 text-sm focus:outline-emerald-500"
                value={reportDate}
                onChange={(e) => setReportDate(e.target.value)}
              />
            </div>

            {/* Trạng thái điểm danh */}
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">
                Tình trạng học viên *
              </label>
              <div className="flex gap-4 mt-1 text-sm">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    type="radio"
                    name="attendance"
                    value="Đi học đủ"
                    checked={attendanceStatus === "Đi học đủ"}
                    onChange={(e) => setAttendanceStatus(e.target.value)}
                    className="accent-emerald-600"
                  />
                  Đi học đủ
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer text-amber-600">
                  <input
                    type="radio"
                    name="attendance"
                    value="Nghỉ có phép"
                    checked={attendanceStatus === "Nghỉ có phép"}
                    onChange={(e) => setAttendanceStatus(e.target.value)}
                    className="accent-amber-500"
                  />
                  Nghỉ có phép
                </label>
              </div>
            </div>

            {/* Nội dung bài học */}
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">
                Nội dung đã dạy trong buổi *
              </label>
              <textarea
                rows="3"
                placeholder="Ví dụ: Học lý thuyết bài 2 chương hình học, luyện giải 10 câu trắc nghiệm nâng cao..."
                className="w-full bg-gray-50 border border-gray-200 rounded-md p-2 text-sm focus:outline-emerald-500"
                value={lessonContent}
                onChange={(e) => setLessonContent(e.target.value)}
              ></textarea>
            </div>

            {/* Bài tập về nhà */}
            <div>
              <label className="block text-xs font-bold text-gray-600 uppercase mb-1">
                Bài tập giao về nhà (Nếu có)
              </label>
              <textarea
                rows="2"
                placeholder="Ví dụ: Làm bài tập từ câu 1 đến câu 20 trong giáo trình..."
                className="w-full bg-gray-50 border border-gray-200 rounded-md p-2 text-sm focus:outline-emerald-500"
                value={homeworkContent}
                onChange={(e) => setHomeworkContent(e.target.value)}
              ></textarea>
            </div>

            {/* Nút gửi */}
            <button
              type="submit"
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-md transition text-sm shadow-sm mt-2"
            >
              🚀 Gửi báo cáo buổi học
            </button>
          </form>
        </div>

        {/* KHỐI PHẢI: LỊCH SỬ NHẬT KÝ ĐÃ GỬI (Chiếm 2 cột) */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-2 space-y-4">
          <h3 className="text-base font-bold text-gray-800 border-b border-gray-100 pb-3 flex justify-between items-center">
            <span>📋 Lịch sử nhật ký giảng dạy gần đây</span>
            <span className="text-xs bg-gray-100 text-gray-500 font-normal px-2 py-1 rounded">
              Tháng hiện tại
            </span>
          </h3>

          <div className="space-y-4 overflow-y-auto max-h-[520px] pr-2">
            {reports.map((rep) => (
              <div
                key={rep.id}
                className="border border-gray-100 rounded-lg p-4 bg-gray-50/50 hover:bg-gray-50 transition space-y-2"
              >
                {/* Dòng trên cùng: Mã lớp + Ngày học */}
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded">
                      Lớp: {rep.classId}
                    </span>
                    <span className="text-xs text-gray-400">
                      Mã BC: {rep.id}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 font-medium">
                      🗓️ Ngày: {rep.date}
                    </span>
                    <span
                      className={`text-[11px] font-semibold px-2 py-0.5 rounded ${
                        rep.attendance === "Đi học đủ"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {rep.attendance}
                    </span>
                  </div>
                </div>

                {/* Nội dung chi tiết */}
                <div className="text-sm text-gray-700 space-y-1 pt-1 border-t border-dashed border-gray-200">
                  <p>
                    <strong>📖 Bài giảng:</strong> {rep.content}
                  </p>
                  <p className="text-gray-600">
                    <strong>📝 Bài tập về nhà:</strong> {rep.homework}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default TutorReports;
