import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'; // nếu bạn dùng Heroicons (có thể cài npm install @heroicons/react)

// Dữ liệu mẫu – sau này thay bằng API
const sampleClasses = [
  { id: 1, code: 'LTO-2401', student: 'Nguyễn Khánh An', studentId: 101, tutor: 'Thầy Ngô Bảo', tutorId: 201, subject: 'Toán 12', level: 'Lớp 12', schedule: 'T2, T4 - 19h', fee: 250000, status: 'ACTIVE', startDate: '2024-03-01', nextLesson: '2024-06-17' },
  { id: 2, code: 'LNV-2402', student: 'Trần Thu Hà', studentId: 102, tutor: 'Cô Nguyễn Hoa', tutorId: 202, subject: 'Ngữ văn 9', level: 'Lớp 9', schedule: 'T3, T6 - 18h30', fee: 200000, status: 'ACTIVE', startDate: '2024-03-10', nextLesson: '2024-06-18' },
  { id: 3, code: 'LTA-2403', student: 'Phạm Minh Đức', studentId: 103, tutor: 'Thầy Lê Vũ', tutorId: 203, subject: 'Tiếng Anh 10', level: 'Lớp 10', schedule: 'T7, CN - 8h', fee: 300000, status: 'PAUSED', startDate: '2024-02-20', nextLesson: null },
  { id: 4, code: 'LHD-2404', student: 'Vũ Hoàng Duy', studentId: 104, tutor: 'Cô Trần Mai', tutorId: 204, subject: 'Hóa 11', level: 'Lớp 11', schedule: 'T5 - 14h', fee: 280000, status: 'FINISHED', startDate: '2023-09-01', endDate: '2024-05-30', nextLesson: null },
  { id: 5, code: 'LTN-2405', student: 'Đỗ Thúy Ngân', studentId: 105, tutor: 'Thầy Phạm Hùng', tutorId: 205, subject: 'Toán 9', level: 'Lớp 9', schedule: 'T2, T5 - 19h30', fee: 220000, status: 'ACTIVE', startDate: '2024-04-15', nextLesson: '2024-06-19' },
];

const statusConfig = {
  ACTIVE: { label: 'Đang diễn ra', color: 'bg-green-100 text-green-700', border: 'border-green-200' },
  PAUSED: { label: 'Tạm dừng', color: 'bg-yellow-100 text-yellow-700', border: 'border-yellow-200' },
  FINISHED: { label: 'Kết thúc', color: 'bg-gray-100 text-gray-600', border: 'border-gray-200' },
  CANCELED: { label: 'Hủy', color: 'bg-red-100 text-red-700', border: 'border-red-200' },
};

export default function ClassesPage() {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [filteredClasses, setFilteredClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  if (user?.role !== 'admin') {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg inline-block">
          ⚠️ Bạn không có quyền truy cập trang quản lý lớp học.
        </div>
      </div>
    );
  }

  useEffect(() => {
    // Giả lập API call
    setTimeout(() => {
      setClasses(sampleClasses);
      setFilteredClasses(sampleClasses);
      setLoading(false);
    }, 500);
  }, []);

  useEffect(() => {
    let result = classes;
    if (searchTerm) {
      result = result.filter(c => 
        c.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.student.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.tutor.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.subject.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== 'ALL') {
      result = result.filter(c => c.status === statusFilter);
    }
    setFilteredClasses(result);
  }, [searchTerm, statusFilter, classes]);

  // Thống kê
  const stats = {
    total: classes.length,
    active: classes.filter(c => c.status === 'ACTIVE').length,
    paused: classes.filter(c => c.status === 'PAUSED').length,
    finished: classes.filter(c => c.status === 'FINISHED').length,
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Đang tải danh sách lớp...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header + Thống kê */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">📚 Quản lý Lớp học</h1>
        <p className="text-gray-500">Theo dõi và quản lý tất cả các lớp học đang được tổ chức</p>
      </div>

      {/* Cards thống kê */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Tổng số lớp</p>
            <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
          </div>
          <div className="p-3 bg-blue-50 rounded-full">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 21v-4H7v4M7 3v4h10V3" /></svg>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Đang diễn ra</p>
            <p className="text-2xl font-bold text-green-600">{stats.active}</p>
          </div>
          <div className="p-3 bg-green-50 rounded-full">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Tạm dừng</p>
            <p className="text-2xl font-bold text-yellow-600">{stats.paused}</p>
          </div>
          <div className="p-3 bg-yellow-50 rounded-full">
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9l4 4-4 4m6-4H4" /></svg>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Kết thúc</p>
            <p className="text-2xl font-bold text-gray-500">{stats.finished}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-full">
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
          </div>
        </div>
      </div>

      {/* Thanh công cụ: Search + Filter */}
      <div className="flex flex-col md:flex-row justify-between gap-4 bg-white p-4 rounded-xl shadow-sm">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm kiếm theo mã lớp, học viên, gia sư, môn học..."
            className="pl-10 pr-4 py-2 w-full border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 transition"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <FunnelIcon className="h-5 w-5 text-gray-400" />
          <select
            className="border border-gray-200 rounded-lg px-3 py-2 bg-white focus:ring-blue-200"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">Tất cả trạng thái</option>
            <option value="ACTIVE">Đang diễn ra</option>
            <option value="PAUSED">Tạm dừng</option>
            <option value="FINISHED">Kết thúc</option>
            <option value="CANCELED">Hủy</option>
          </select>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Thêm lớp
          </button>
        </div>
      </div>

      {/* Bảng lớp học */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mã lớp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Học viên</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gia sư</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Môn học</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lịch học</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Học phí/buổi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredClasses.map((cls) => {
                const status = statusConfig[cls.status] || statusConfig.ACTIVE;
                return (
                  <tr key={cls.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-medium text-gray-900">{cls.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.student}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.tutor}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      <span className="font-medium">{cls.subject}</span>
                      <span className="text-gray-400 ml-1">({cls.level})</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.schedule}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">{cls.fee.toLocaleString()}đ</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${status.color}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button className="text-blue-600 hover:text-blue-800 font-medium mr-3">Xem</button>
                      <button className="text-gray-600 hover:text-gray-800">Sửa</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {filteredClasses.length === 0 && (
          <div className="text-center py-10 text-gray-400">
            Không tìm thấy lớp học nào phù hợp.
          </div>
        )}
      </div>
    </div>
  );
}