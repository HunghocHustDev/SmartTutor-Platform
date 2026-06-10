import React, { useState } from 'react';

// DỰ LIỆU MẪU (MOCK DATA) ĐẦY ĐỦ ĐỂ PHỤC VỤ LUỒNG DEMO NGHIỆP VỤ
const INITIAL_STUDENTS = [
  { 
    id: 1, 
    name: 'Nguyễn Văn A', 
    phone: '0912345678', 
    email: 'vana@gmail.com',
    address: 'Số 12 Ngõ 45 Cầu Giấy', 
    area: 'Cầu Giấy', 
    current_level: 'Lớp 12', 
    status: 'ACTIVE',
    requests: [
      { id: 'REQ-101', subject: 'Toán học', level: 'Lớp 12', status: 'COMPLETED', date: '15/05/2026' },
      { id: 'REQ-105', subject: 'Vật Lý', level: 'Lớp 12', status: 'WAITING_ASSIGNMENT', date: '01/06/2026' }
    ],
    classes: [
      { id: 'CLASS-001', subject: 'Toán nâng cao 12', tutor: 'Thầy Trần Bình', status: 'ACTIVE' }
    ]
  },
  { 
    id: 2, 
    name: 'Trần Thị B', 
    phone: '0987654321', 
    email: 'thib@gmail.com',
    address: 'Ngõ 299 Tam Trinh', 
    area: 'Hoàng Mai', 
    current_level: 'Lớp 9', 
    status: 'ACTIVE',
    requests: [
      { id: 'REQ-102', subject: 'Tiếng Anh', level: 'Lớp 9', status: 'COMPLETED', date: '20/05/2026' }
    ],
    classes: [
      { id: 'CLASS-003', subject: 'Tiếng Anh Ôn Thi Vào 10', tutor: 'Cô Mai Phương', status: 'ACTIVE' }
    ]
  },
  { 
    id: 3, 
    name: 'Lê Văn C', 
    phone: '0904445556', 
    email: 'vanc@gmail.com',
    address: 'Chung cư HH Linh Đàm', 
    area: 'Hoàng Mai', 
    current_level: 'Lớp 11', 
    status: 'INACTIVE',
    requests: [
      { id: 'REQ-103', subject: 'Hóa Học', level: 'Lớp 11', status: 'CANCELLED', date: '10/05/2026' }
    ],
    classes: [] // Chưa tham gia lớp nào
  },
  { 
    id: 4, 
    name: 'Phạm Minh Đức', 
    phone: '0936667778', 
    email: 'ducpm@gmail.com',
    address: '45 Lê Thanh Nghị', 
    area: 'Hai Bà Trưng', 
    current_level: 'Lớp 12', 
    status: 'ACTIVE',
    requests: [
      { id: 'REQ-104', subject: 'Hóa Học', level: 'Lớp 12', status: 'COMPLETED', date: '25/05/2026' }
    ],
    classes: [
      { id: 'CLASS-002', subject: 'Hóa hữu cơ bứt phá', tutor: 'Anh Nguyễn Minh Triết', status: 'ACTIVE' }
    ]
  }
];

export default function StudentsPage() {
  const [students, setStudents] = useState(INITIAL_STUDENTS);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  
  // State xử lý Modal xem chi tiết
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  // Logic bộ lọc tìm kiếm
  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          student.phone.includes(searchTerm);
    const matchesStatus = statusFilter === 'ALL' || student.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Tính toán số liệu thống kê nhanh ở các Card đầu trang
  const totalStudents = students.length;
  const activeStudents = students.filter(s => s.status === 'ACTIVE').length;
  const waitingRequests = students.reduce((acc, s) => acc + s.requests.filter(r => r.status === 'WAITING_ASSIGNMENT').length, 0);

  const handleOpenDetail = (student) => {
    setSelectedStudent(student);
    setIsDetailOpen(true);
  };

  const handleDeleteClick = (id, name) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa học viên ${name} khỏi hệ thống quản trị?`)) {
      setStudents(students.filter(s => s.id !== id));
    }
  };

  return (
    <div className="space-y-6">
      
      {/* 1. THẺ THỐNG KÊ NHANH (CARDS) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-blue-50 text-blue-600 text-2xl">👥</div>
          <div>
            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Tổng số học viên</p>
            <p className="text-2xl font-bold text-slate-900">{totalStudents}</p>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-green-50 text-green-600 text-2xl">🟢</div>
          <div>
            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Đang hoạt động</p>
            <p className="text-2xl font-bold text-slate-900">{activeStudents}</p>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-amber-50 text-amber-600 text-2xl">⏳</div>
          <div>
            <p className="text-sm font-medium text-slate-500 uppercase tracking-wider">Yêu cầu chờ điều phối</p>
            <p className="text-2xl font-bold text-slate-900">{waitingRequests}</p>
          </div>
        </div>
      </div>

      {/* 2. THANH CÔNG CỤ TÌM KIẾM VÀ LỌC */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex flex-1 w-full sm:w-auto gap-3">
          <input
            type="text"
            placeholder="Tìm theo họ tên hoặc số điện thoại học viên..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 max-w-md px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">Tất cả trạng thái</option>
            <option value="ACTIVE">Đang hoạt động</option>
            <option value="INACTIVE">Tạm dừng học</option>
          </select>
        </div>
        <button 
          onClick={() => alert('Chức năng thêm mới học viên (Form thêm) đang chờ kết nối API.')}
          className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition shadow-sm"
        >
          + Thêm học viên mới
        </button>
      </div>

      {/* 3. BẢNG DỮ LIỆU DANH SÁCH (DATA TABLE) */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 text-xs uppercase font-semibold tracking-wider">
                <th className="px-6 py-3.5">Họ & Tên học viên</th>
                <th className="px-6 py-3.5">Số điện thoại</th>
                <th className="px-6 py-3.5">Khu vực</th>
                <th className="px-6 py-3.5">Trình độ học</th>
                <th className="px-6 py-3.5 text-center">Trạng thái</th>
                <th className="px-6 py-3.5 text-center">Hành động</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 text-sm text-slate-700">
              {filteredStudents.length > 0 ? (
                filteredStudents.map((student) => (
                  <tr key={student.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900">{student.name}</div>
                      <div className="text-xs text-slate-400">{student.email}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-600">{student.phone}</td>
                    <td className="px-6 py-4">{student.area}</td>
                    <td className="px-6 py-4">
                      <span className="bg-slate-100 text-slate-800 text-xs px-2.5 py-1 rounded font-medium">
                        {student.current_level}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        student.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-rose-100 text-rose-800'
                      }`}>
                        {student.status === 'ACTIVE' ? 'Đang hoạt động' : 'Tạm dừng'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center space-x-2">
                      <button
                        onClick={() => handleOpenDetail(student)}
                        className="text-blue-600 hover:text-blue-800 font-medium text-xs bg-blue-50 hover:bg-blue-100 px-2.5 py-1.5 rounded transition"
                      >
                        Chi tiết
                      </button>
                      <button
                        onClick={() => handleDeleteClick(student.id, student.name)}
                        className="text-red-600 hover:text-red-800 font-medium text-xs bg-red-50 hover:bg-red-100 px-2.5 py-1.5 rounded transition"
                      >
                        Xóa
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-slate-400 font-medium">
                    🔍 Không tìm thấy học viên nào phù hợp với bộ lọc.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 4. MODAL CHI TIẾT NGHIỆP VỤ HỌC VIÊN */}
      {isDetailOpen && selectedStudent && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            
            {/* Header Modal */}
            <div className="bg-slate-950 text-white px-6 py-4 flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold">Hồ Sơ Chi Tiết Học Viên</h3>
                <p className="text-xs text-slate-400">Mã định danh hệ thống: #STU-00{selectedStudent.id}</p>
              </div>
              <button 
                onClick={() => setIsDetailOpen(false)} 
                className="text-slate-400 hover:text-white text-2xl font-semibold transition"
              >
                &times;
              </button>
            </div>

            {/* Body Modal */}
            <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
              
              {/* Khối 1: Thông tin liên hệ cơ bản */}
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2">Thông tin cá nhân</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 bg-slate-50 p-4 rounded-xl text-sm border border-slate-100">
                  <div><span className="text-slate-500">Họ và tên:</span> <strong className="text-slate-900">{selectedStudent.name}</strong></div>
                  <div><span className="text-slate-500">Số điện thoại:</span> <strong className="text-slate-900 font-mono">{selectedStudent.phone}</strong></div>
                  <div><span className="text-slate-500">Địa chỉ cụ thể:</span> <span className="text-slate-700">{selectedStudent.address}</span></div>
                  <div><span className="text-slate-500">Khu vực đăng ký:</span> <span className="text-slate-700">{selectedStudent.area}</span></div>
                  <div><span className="text-slate-500">Email liên lạc:</span> <span className="text-slate-700 font-mono">{selectedStudent.email}</span></div>
                  <div><span className="text-slate-500">Cấp học hiện tại:</span> <span className="text-slate-700 font-semibold">{selectedStudent.current_level}</span></div>
                </div>
              </div>

              {/* Khối 2: Lịch sử Đăng ký Nhu cầu Học (Learning Requests) */}
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2">Lịch sử nhu cầu tìm gia sư</h4>
                <div className="border border-slate-200 rounded-lg overflow-hidden">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-100 font-semibold text-slate-600">
                      <tr>
                        <th className="p-2.5 pl-4">Mã Đơn</th>
                        <th className="p-2.5">Môn Học</th>
                        <th className="p-2.5">Trình độ</th>
                        <th className="p-2.5">Ngày gửi</th>
                        <th className="p-2.5 text-center">Trạng thái xử lý</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {selectedStudent.requests.length > 0 ? (
                        selectedStudent.requests.map((req) => (
                          <tr key={req.id} className="hover:bg-slate-50/50">
                            <td className="p-2.5 pl-4 font-mono font-medium text-blue-600">{req.id}</td>
                            <td className="p-2.5 font-medium">{req.subject}</td>
                            <td className="p-2.5">{req.level}</td>
                            <td className="p-2.5 text-slate-500">{req.date}</td>
                            <td className="p-2.5 text-center">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                                req.status === 'WAITING_ASSIGNMENT' ? 'bg-amber-100 text-amber-800 animate-pulse' :
                                req.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-slate-100 text-slate-600'
                              }`}>
                                {req.status === 'WAITING_ASSIGNMENT' ? 'Chờ phân công' :
                                 req.status === 'COMPLETED' ? 'Đã xếp lớp' : 'Đã hủy đơn'}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="5" className="p-4 text-center text-slate-400">Chưa ghi nhận nhu cầu học nào.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Khối 3: Lớp học đang tham gia (Active Classes) */}
              <div>
                <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider mb-2">Các lớp học thực tế đang tham gia</h4>
                {selectedStudent.classes.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {selectedStudent.classes.map((cls) => (
                      <div key={cls.id} className="p-3 border border-green-200 bg-green-50/40 rounded-xl flex justify-between items-start">
                        <div>
                          <div className="text-xs font-mono font-bold text-green-700">{cls.id}</div>
                          <div className="text-sm font-semibold text-slate-900 mt-0.5">{cls.subject}</div>
                          <div className="text-xs text-slate-500 mt-1">Gia sư: <span className="text-slate-800 font-medium">{cls.tutor}</span></div>
                        </div>
                        <span className="bg-green-100 text-green-800 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                          {cls.status === 'ACTIVE' ? 'Đang học' : 'Kết thúc'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center p-4 border border-dashed border-slate-200 bg-slate-50 text-slate-400 text-xs rounded-xl">
                    ⚠️ Hiện tại học viên chưa có lịch xếp lớp học chính thức nào tại trung tâm.
                  </div>
                )}
              </div>

            </div>

            {/* Footer Modal */}
            <div className="bg-slate-50 px-6 py-3.5 flex justify-end border-t border-slate-200">
              <button
                onClick={() => setIsDetailOpen(false)}
                className="bg-slate-800 hover:bg-slate-900 text-white text-xs font-medium px-4 py-2 rounded-lg transition"
              >
                Đóng hồ sơ
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}