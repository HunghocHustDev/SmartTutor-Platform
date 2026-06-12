// pages/StudentList.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

// Dữ liệu mẫu (sau này thay bằng API)
const sampleStudents = [
  { id: 1, full_name: 'Nguyễn Văn A', phone: '0987654321', email: 'a.nguyen@example.com', area: 'Cầu Giấy', level: 'Lớp 10', status: 'ACTIVE' },
  { id: 2, full_name: 'Trần Thị B', phone: '0912345678', email: 'b.tran@example.com', area: 'Đống Đa', level: 'Lớp 12', status: 'ACTIVE' },
  { id: 3, full_name: 'Lê Văn C', phone: '0977778888', email: 'c.le@example.com', area: 'Thanh Xuân', level: 'Lớp 8', status: 'INACTIVE' },
  { id: 4, full_name: 'Phạm Thị D', phone: '0966667777', email: 'd.pham@example.com', area: 'Hoàn Kiếm', level: 'Lớp 11', status: 'ACTIVE' },
  { id: 5, full_name: 'Hoàng Văn E', phone: '0933334444', email: 'e.hoang@example.com', area: 'Ba Đình', level: 'Lớp 9', status: 'INACTIVE' },
];

export default function StudentList() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [formData, setFormData] = useState({ full_name: '', phone: '', email: '', area: '', level: '' });

  // Kiểm tra quyền admin
  if (user?.role !== 'admin') {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg inline-block">
          ⚠️ Bạn không có quyền truy cập trang quản lý học viên.
        </div>
      </div>
    );
  }

  // Load dữ liệu mẫu
  useEffect(() => {
    setTimeout(() => {
      setStudents(sampleStudents);
      setFilteredStudents(sampleStudents);
      setLoading(false);
    }, 500);
  }, []);

  // Lọc theo search và status
  useEffect(() => {
    let result = students;
    if (searchTerm) {
      result = result.filter(s =>
        s.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.phone.includes(searchTerm) ||
        s.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.area.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (statusFilter !== 'ALL') {
      result = result.filter(s => s.status === statusFilter);
    }
    setFilteredStudents(result);
  }, [searchTerm, statusFilter, students]);

  const stats = {
    total: students.length,
    active: students.filter(s => s.status === 'ACTIVE').length,
    inactive: students.filter(s => s.status === 'INACTIVE').length,
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newStudent = { id: students.length + 1, ...formData, status: 'ACTIVE' };
    setStudents([...students, newStudent]);
    setFormData({ full_name: '', phone: '', email: '', area: '', level: '' });
    setShowForm(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Đang tải danh sách học viên...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">👨‍🎓 Quản lý Học viên</h1>
        <p className="text-gray-500">Quản lý thông tin học viên, theo dõi trạng thái và lịch sử đăng ký</p>
      </div>

      {/* Cards thống kê */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Tổng số học viên</p>
            <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
          </div>
          <div className="p-3 bg-blue-50 rounded-full">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Đang hoạt động</p>
            <p className="text-2xl font-bold text-green-600">{stats.active}</p>
          </div>
          <div className="p-3 bg-green-50 rounded-full">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500">Tạm ngưng</p>
            <p className="text-2xl font-bold text-gray-500">{stats.inactive}</p>
          </div>
          <div className="p-3 bg-gray-50 rounded-full">
            <svg className="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
        </div>
      </div>

      {/* Thanh công cụ tìm kiếm + lọc + nút thêm */}
      <div className="flex flex-col md:flex-row justify-between gap-4 bg-white p-4 rounded-xl shadow-sm">
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          <input
            type="text"
            placeholder="Tìm kiếm theo tên, SĐT, email, khu vực..."
            className="pl-10 pr-4 py-2 w-full border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-200 focus:border-blue-400 transition"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <select
            className="border border-gray-200 rounded-lg px-3 py-2 bg-white focus:ring-blue-200"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="ALL">Tất cả trạng thái</option>
            <option value="ACTIVE">Đang hoạt động</option>
            <option value="INACTIVE">Tạm ngưng</option>
          </select>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-1"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
            Thêm học viên
          </button>
        </div>
      </div>

      {/* Form thêm học viên (hiện khi showForm = true) */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Thêm học viên mới</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" name="full_name" placeholder="Họ tên *" value={formData.full_name} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg focus:ring-blue-200" required />
            <input type="text" name="phone" placeholder="Số điện thoại *" value={formData.phone} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" required />
            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="area" placeholder="Khu vực" value={formData.area} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="level" placeholder="Trình độ (VD: Lớp 10)" value={formData.level} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
          </div>
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">Lưu</button>
            <button type="button" onClick={() => setShowForm(false)} className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500">Hủy</button>
          </div>
        </form>
      )}

      {/* Bảng danh sách học viên */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Họ tên</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SĐT</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khu vực</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trình độ</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredStudents.map(student => (
                <tr key={student.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{student.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{student.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{student.phone}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{student.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{student.area}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{student.level}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${student.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {student.status === 'ACTIVE' ? 'Đang hoạt động' : 'Tạm ngưng'}
                    </span>
                   </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button className="text-blue-600 hover:text-blue-800 font-medium mr-3">Sửa</button>
                    <button className="text-red-600 hover:text-red-800">Xóa</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredStudents.length === 0 && (
          <div className="text-center py-10 text-gray-400">
            Không tìm thấy học viên nào phù hợp.
          </div>
        )}
      </div>
    </div>
  );
}