import React, { useState } from "react";

export default function StudentRequests() {
  const [requests, setRequests] = useState([
    {
      id: "REQ001",
      subject: "Toán 12",
      target: "Ôn thi đại học",
      status: "Đang chờ",
      date: "2026-06-01",
    },
    {
      id: "REQ002",
      subject: "Tiếng Anh IELTS",
      target: "Đạt Đẩu ra 6.5",
      status: "Đã phân công",
      date: "2026-05-15",
    },
  ]);

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">Nhu cầu học của tôi</h2>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium text-sm transition">
          + Tạo nhu cầu học mới
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Mã YC
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Môn học
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Mục tiêu
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Ngày tạo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Trạng thái
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200 text-sm">
            {requests.map((req) => (
              <tr key={req.id}>
                <td className="px-6 py-4 font-medium text-gray-900">
                  {req.id}
                </td>
                <td className="px-6 py-4 text-gray-700">{req.subject}</td>
                <td className="px-6 py-4 text-gray-500">{req.target}</td>
                <td className="px-6 py-4 text-gray-500">{req.date}</td>
                <td className="px-6 py-4">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      req.status === "Đang chờ"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-green-100 text-green-800"
                    }`}
                  >
                    {req.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
