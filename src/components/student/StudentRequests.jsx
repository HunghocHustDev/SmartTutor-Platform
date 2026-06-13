import React, { useState } from "react";

function StudentRequests() {
  // State quản lý xem đang hiện bảng danh sách (view) hay hiện form tạo mới (create)
  const [mode, setMode] = useState("view");

  // Dữ liệu mẫu (Mock data) để hiển thị lịch sử yêu cầu
  const [requests, setRequests] = useState([
    {
      id: "REQ001",
      subject: "Toán học 12",
      grade: "Lớp 12",
      frequency: "3 buổi/tuần",
      status: "Đang tìm gia sư",
      date: "10/06/2026",
    },
    {
      id: "REQ002",
      subject: "Tiếng Anh (IELTS)",
      grade: "Người đi làm",
      frequency: "2 buổi/tuần",
      status: "Chờ duyệt",
      date: "12/06/2026",
    },
    {
      id: "REQ003",
      subject: "Vật lý 11",
      grade: "Lớp 11",
      frequency: "2 buổi/tuần",
      status: "Đã tạo lớp",
      date: "05/06/2026",
    },
  ]);

  // Hàm trả về màu sắc badge tương ứng với trạng thái yêu cầu
  const getStatusColor = (status) => {
    switch (status) {
      case "Chờ duyệt":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "Đang tìm gia sư":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "Đã tạo lớp":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* ================= THẾ TRẬN 1: GIAO DIỆN XEM DANH SÁCH LỊCH SỬ ================= */}
      {mode === "view" && (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                Yêu cầu gia sư của tôi
              </h2>
              <p className="text-sm text-gray-500">
                Theo dõi trạng thái các yêu cầu tìm gia sư bạn đã gửi lên trung
                tâm
              </p>
            </div>
            {/* NÚT BẤM CHUYỂN SANG PHÂN HỆ TẠO MỚI */}
            <button
              onClick={() => setMode("create")}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition flex items-center gap-2"
            >
              <span>➕</span> Tạo yêu cầu mới
            </button>
          </div>

          {/* BẢNG LỊCH SỬ YÊU CẦU */}
          <div className="overflow-x-auto border border-gray-100 rounded-lg">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 text-gray-600 text-sm font-semibold border-b border-gray-100">
                  <th className="p-4">Mã yêu cầu</th>
                  <th className="p-4">Môn học</th>
                  <th className="p-4">Trình độ / Lớp</th>
                  <th className="p-4">Tần suất</th>
                  <th className="p-4">Ngày tạo</th>
                  <th className="p-4">Trạng thái</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50 text-sm text-gray-700">
                {requests.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50/50 transition">
                    <td className="p-4 font-medium text-blue-600">{req.id}</td>
                    <td className="p-4 font-medium text-gray-900">
                      {req.subject}
                    </td>
                    <td className="p-4">{req.grade}</td>
                    <td className="p-4">{req.frequency}</td>
                    <td className="p-4 text-gray-500">{req.date}</td>
                    <td className="p-4">
                      <span
                        className={`px-2.5 py-1 rounded-full text-xs font-medium border ${getStatusColor(req.status)}`}
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
      )}

      {/* ================= THẾ TRẬN 2: GIAO DIỆN FORM ĐIỀN THÔNG TIN (ẢNH 2 CỦA BẠN) ================= */}
      {mode === "create" && (
        <div>
          <div className="flex items-center gap-3 mb-6">
            {/* NÚT QUAY LẠI BẢNG */}
            <button
              onClick={() => setMode("view")}
              className="text-gray-400 hover:text-gray-600 text-lg p-1"
            >
              ⬅️
            </button>
            <div>
              <h2 className="text-xl font-bold text-gray-800">
                Tạo yêu cầu tìm gia sư mới
              </h2>
              <p className="text-sm text-gray-500">
                Vui lòng điền đầy đủ thông tin để hệ thống tìm kiếm gia sư phù
                hợp nhất
              </p>
            </div>
          </div>

          {/* CODE PHẦN BIỂU MẪU (FORM GRID 2 CỘT) MÀ CÁC BẠN ĐÃ LÀM Ở ẢNH 2 NHÉT VÀO ĐÂY */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setMode("view");
            }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Môn học đăng ký
                </label>
                <input
                  type="text"
                  placeholder="Ví dụ: Toán lớp 12"
                  className="w-full border border-gray-200 rounded-lg p-2.5 outline-none focus:border-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Yêu cầu trình độ gia sư
                </label>
                <select className="w-full border border-gray-200 rounded-lg p-2.5 outline-none focus:border-blue-500">
                  <option>Sinh viên xuất sắc / Sư phạm</option>
                  <option>Giáo viên tự do</option>
                  <option>Giáo viên đứng lớp trường công</option>
                </select>
              </div>
              {/* ...Các input khác của nhóm giữ nguyên... */}
            </div>

            {/* HÀNG NÚT BẤM CUỐI FORM */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setMode("view")}
                className="px-5 py-2 rounded-lg border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 transition"
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition"
              >
                Gửi yêu cầu lên hệ thống
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default StudentRequests;
