import React from "react";

export default function StudentClasses() {
  const classes = [
    {
      id: "L001",
      name: "Lớp Toán 12 - Gia sư Nguyễn Văn A",
      schedule: "Thứ 2, Thứ 4 (19:30)",
      status: "Đang học",
    },
    {
      id: "L002",
      name: "Lớp IELTS - Gia sư Trần Thị B",
      schedule: "Thứ 7 (14:00)",
      status: "Đang học",
    },
  ];

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold text-gray-800 mb-6">Các lớp đang học</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {classes.map((cls) => (
          <div
            key={cls.id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-semibold uppercase px-2 py-1 bg-blue-50 text-blue-600 rounded">
                {cls.id}
              </span>
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                {cls.status}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 mb-1">{cls.name}</h3>
            <p className="text-sm text-gray-500">
              Lịch học cố định: {cls.schedule}
            </p>
            <button className="mt-4 text-sm text-blue-600 font-medium hover:underline">
              Xem chi tiết buổi học &rarr;
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
