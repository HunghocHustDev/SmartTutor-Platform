import React, { useState } from "react";

function TutorSchedule() {
  // 1. DỮ LIỆU GIẢ LẬP LỊCH DẠY THEO TUẦN CỦA GIA SƯ
  const [scheduleData] = useState([
    {
      id: "SCH001",
      classId: "LHP109",
      subject: "Luyện thi IELTS (Writing & Speaking)",
      studentName: "Trần Thu Hà",
      dayOfWeek: "Thứ 2",
      time: "19:30 - 21:30",
      type: "Online",
      location: "Google Meet Link",
    },
    {
      id: "SCH002",
      classId: "LHP042",
      subject: "Toán học 12 (Ôn thi THPT QG)",
      studentName: "Nguyễn Hoàng Nam",
      dayOfWeek: "Thứ 3",
      time: "18:00 - 20:00",
      type: "Offline",
      location: "Số 1 Đại Cồ Việt, HBT, Hà Nội",
    },
    {
      id: "SCH003",
      classId: "LHP109",
      subject: "Luyện thi IELTS (Writing & Speaking)",
      studentName: "Trần Thu Hà",
      dayOfWeek: "Thứ 4",
      time: "19:30 - 21:30",
      type: "Online",
      location: "Google Meet Link",
    },
    {
      id: "SCH004",
      classId: "LHP042",
      subject: "Toán học 12 (Ôn thi THPT QG)",
      studentName: "Nguyễn Hoàng Nam",
      dayOfWeek: "Thứ 5",
      time: "18:00 - 20:00",
      type: "Offline",
      location: "Số 1 Đại Cồ Việt, HBT, Hà Nội",
    },
    {
      id: "SCH005",
      classId: "LHP109",
      subject: "Luyện thi IELTS (Writing & Speaking)",
      studentName: "Trần Thu Hà",
      dayOfWeek: "Thứ 6",
      time: "19:30 - 21:30",
      type: "Online",
      location: "Google Meet Link",
    },
    {
      id: "SCH006",
      classId: "LHP015",
      subject: "Vật lý lớp 11 (Cơ bản & Nâng cao)",
      studentName: "Lê Minh Triết",
      dayOfWeek: "Chủ Nhật",
      time: "08:30 - 10:30",
      type: "Offline",
      location: "128 Trần Đại Nghĩa, HBT, Hà Nội",
    },
  ]);

  // Danh sách các ngày trong tuần để làm cột tiêu đề
  const daysInWeek = [
    "Thứ 2",
    "Thứ 3",
    "Thứ 4",
    "Thứ 5",
    "Thứ 6",
    "Thứ 7",
    "Chủ Nhật",
  ];

  return (
    <div className="tutor-schedule-container space-y-6">
      {/* TIÊU ĐỀ KHỐI */}
      <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <div>
          <h2 className="text-xl font-bold text-gray-800">Lịch dạy tuần này</h2>
          <p className="text-sm text-gray-500">
            Theo dõi các ca dạy cố định và chuẩn bị bài giảng tương ứng
          </p>
        </div>
        <div className="text-sm bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-lg font-medium border border-emerald-100">
          📅 Tuần hiện tại: 08/06/2026 - 14/06/2026
        </div>
      </div>

      {/* GIAO DIỆN TIMELINE CHIA THEO THỨ (RẤT DỄ NHÌN) */}
      <div className="grid grid-cols-1 gap-4">
        {daysInWeek.map((day) => {
          // Lọc ra các ca dạy thuộc ngày hôm đó
          const sessionsOfDay = scheduleData.filter(
            (item) => item.dayOfWeek === day,
          );

          return (
            <div
              key={day}
              className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col md:flex-row items-start md:items-center gap-4 hover:border-emerald-200 transition"
            >
              {/* Cột hiển thị Thứ */}
              <div className="w-28 flex-shrink-0">
                <span
                  className={`inline-block px-3 py-1.5 rounded-lg font-bold text-sm text-center w-full ${
                    sessionsOfDay.length > 0
                      ? "bg-emerald-600 text-white shadow-sm"
                      : "bg-gray-100 text-gray-400"
                  }`}
                >
                  {day}
                </span>
              </div>

              {/* Cột hiển thị danh sách các ca dạy trong ngày */}
              <div className="flex-1 w-full space-y-3">
                {sessionsOfDay.length > 0 ? (
                  sessionsOfDay.map((session) => (
                    <div
                      key={session.id}
                      className="bg-gray-50/70 border border-gray-100 rounded-lg p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                    >
                      {/* Trái: Thời gian & Môn học */}
                      <div className="space-y-1">
                        <div className="flex items-center gap-3">
                          <span className="text-emerald-600 font-bold text-sm flex items-center gap-1">
                            ⏰ {session.type === "Online" ? "💻" : "🏠"}{" "}
                            {session.time}
                          </span>
                          <span
                            className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${
                              session.type === "Online"
                                ? "bg-blue-50 text-blue-700 border-blue-100"
                                : "bg-amber-50 text-amber-700 border-amber-100"
                            }`}
                          >
                            {session.type}
                          </span>
                        </div>
                        <h4 className="text-base font-bold text-gray-800">
                          {session.subject}
                        </h4>
                        <p className="text-xs text-gray-500">
                          <strong>Học viên:</strong> {session.studentName} |{" "}
                          <strong>Địa điểm:</strong>{" "}
                          <span className="text-gray-600 italic">
                            {session.location}
                          </span>
                        </p>
                      </div>

                      {/* Phải: Nút hành động tương tác */}
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-400 mr-2">
                          Mã lớp: {session.classId}
                        </span>
                        <button
                          onClick={() =>
                            alert(`Vào lớp / Xem giáo án ca dạy ${session.id}`)
                          }
                          className="bg-white hover:bg-gray-100 text-gray-600 border border-gray-200 text-xs font-semibold px-3 py-2 rounded-md transition"
                        >
                          Xem giáo án
                        </button>
                        <button
                          onClick={() =>
                            alert(
                              `Điểm danh nhanh cho học viên ${session.studentName}`,
                            )
                          }
                          className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-2 rounded-md transition shadow-sm"
                        >
                          Điểm danh ca này
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-gray-400 italic py-1 pl-2">
                    Không có ca dạy nào lên lịch.
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TutorSchedule;
