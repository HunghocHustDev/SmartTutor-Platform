import React from "react";

export default function StudentSchedule() {
  const sessions = [
    {
      id: 1,
      date: "08/06/2026",
      class: "Toán 12",
      content: "Đạo hàm và ứng dụng",
      attendance: "Có mặt",
    },
    {
      id: 2,
      date: "10/06/2026",
      class: "Toán 12",
      content: "Khảo sát hàm số (Bản kế tiếp)",
      attendance: "Chưa diễn ra",
    },
  ];

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold text-gray-800 mb-6">
        Lịch học và Nhật ký điểm danh
      </h2>
      <div className="space-y-4">
        {sessions.map((ss) => (
          <div
            key={ss.id}
            className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100"
          >
            <div>
              <span className="text-sm font-semibold text-blue-600">
                {ss.date}
              </span>
              <h4 className="font-bold text-gray-900">{ss.class}</h4>
              <p className="text-sm text-gray-500">
                Nội dung bài học: {ss.content}
              </p>
            </div>
            <div className="mt-2 sm:mt-0">
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  ss.attendance === "Có mặt"
                    ? "bg-green-100 text-green-800"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {ss.attendance}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
