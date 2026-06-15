import React, { useState, useEffect } from "react";

const sampleClasses = [
  {
    id: 1,
    subject: "Toán 12",
    level: "Lớp 12",
    area: "Cầu Giấy",
    schedule: "Tối T2, T4",
    salary: "250k/buổi",
    status: "Đang tuyển",
  },
  {
    id: 2,
    subject: "Ngữ văn 9",
    level: "Lớp 9",
    area: "Đống Đa",
    schedule: "Tối T3, T6",
    salary: "200k/buổi",
    status: "Đang tuyển",
  },
  {
    id: 3,
    subject: "Tiếng Anh 10",
    level: "Lớp 10",
    area: "Thanh Xuân",
    schedule: "Sáng T7, CN",
    salary: "300k/buổi",
    status: "Đã có gia sư",
  },
];

export default function ClassList({ onClassClick }) {
  const [user, setUser] = useState(null);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    // Giả lập gọi API
    setTimeout(() => {
      setClasses(sampleClasses);
      setLoading(false);
    }, 500);
  }, []);

  const canRegister = !user || user?.role === "tutor";

  if (loading) {
    return <div className="p-4 text-center text-gray-500">Đang tải danh sách lớp...</div>;
  }

  if (classes.length === 0) {
    return <div className="p-4 text-center text-gray-500">Hiện chưa có lớp mới nào.</div>;
  }

  return (
    <div className="class-list-container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
      {classes.map((cls) => (
        <div key={cls.id} className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition">
          <div className="p-4">
            <h3 className="text-xl font-bold text-gray-800 mb-2">
              {cls.subject} - {cls.level}
            </h3>
            <div className="space-y-1 text-sm text-gray-600">
              <p><span className="font-medium">📍 Khu vực:</span> {cls.area}</p>
              <p><span className="font-medium">📅 Lịch học:</span> {cls.schedule}</p>
              <p><span className="font-medium">💰 Học phí:</span> {cls.salary}</p>
              <p>
                <span className="font-medium">📌 Trạng thái:</span>{" "}
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${cls.status === "Đang tuyển" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                  {cls.status}
                </span>
              </p>
            </div>
            {canRegister ? (
              <button onClick={() => onClassClick(cls)} className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md transition-colors">
                Đăng ký nhận lớp
              </button>
            ) : (
              <div className="mt-4 text-center text-sm text-gray-400 border-t pt-3">
                {user?.role === "student" && "🚫 Chức năng dành cho gia sư"}
                {user?.role === "staff" && "🔧 Nhân viên không thể nhận lớp"}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
