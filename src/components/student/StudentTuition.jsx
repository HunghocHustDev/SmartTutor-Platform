import React from "react";

export default function StudentTuition() {
  const tuitions = [
    {
      id: "T001",
      className: "Toán 12",
      amount: "1,500,000 đ",
      period: "Tháng 05/2026",
      status: "Đã hoàn thành",
    },
    {
      id: "T002",
      className: "IELTS",
      amount: "2,000,000 đ",
      period: "Tháng 06/2026",
      status: "Chưa thanh toán",
    },
  ];

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold text-gray-800 mb-6">Theo dõi học phí</h2>
      <div className="space-y-4">
        {tuitions.map((t) => (
          <div
            key={t.id}
            className="border border-gray-200 rounded-lg p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center"
          >
            <div>
              <h3 className="font-bold text-gray-900">Lớp: {t.className}</h3>
              <p className="text-sm text-gray-500">Kỳ học phí: {t.period}</p>
              <p className="text-lg font-semibold text-red-600 mt-1">
                {t.amount}
              </p>
            </div>
            <div className="mt-3 sm:mt-0">
              <span
                className={`px-3 py-1 rounded-full text-xs font-medium ${
                  t.status === "Đã hoàn thành"
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {t.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
