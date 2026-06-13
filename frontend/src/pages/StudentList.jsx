import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createStudent, deleteStudent, listStudents, updateStudent } from '../services/api';

export default function StudentList() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [saving, setSaving] = useState(false);
  const [savingId, setSavingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ full_name: '', phone: '', email: '', area: '', level: '' });

  const canView = user?.role === 'staff';

  useEffect(() => {
    if (!canView) {
      return;
    }
    let active = true;
    setLoading(true);
    setError('');
    listStudents()
      .then((data) => {
        if (active) {
          setStudents(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || 'Không tải được danh sách học viên');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [canView]);

  const filteredStudents = useMemo(() => {
    let result = students;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter((item) =>
        [item.full_name, item.phone, item.email, item.area]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(term))
      );
    }
    if (statusFilter !== 'ALL') {
      result = result.filter((item) => item.status === statusFilter);
    }
    return result;
  }, [students, searchTerm, statusFilter]);

  const stats = useMemo(() => ({
    total: students.length,
    active: students.filter((s) => s.status === 'ACTIVE').length,
    inactive: students.filter((s) => s.status === 'INACTIVE').length,
  }), [students]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      if (editingId) {
        const updated = await updateStudent(editingId, { ...formData });
        setStudents((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createStudent({
          ...formData,
        });
        setStudents((prev) => [created, ...prev]);
      }
      setFormData({ full_name: '', phone: '', email: '', area: '', level: '' });
      setEditingId(null);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không tạo được học viên');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (student) => {
    setEditingId(student.id);
    setFormData({
      full_name: student.full_name || '',
      phone: student.phone || '',
      email: student.email || '',
      area: student.area || '',
      level: student.level || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn ngừng hoạt động học viên này không?')) {
      return;
    }
    setSavingId(id);
    setError('');
    try {
      await deleteStudent(id);
      setStudents((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'INACTIVE' } : item)));
    } catch (err) {
      setError(err?.message || 'Không xóa được học viên');
    } finally {
      setSavingId(null);
    }
  };

  if (!canView) {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg inline-block">
          Bạn không có quyền truy cập trang quản lý học viên.
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Đang tải danh sách học viên...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Quản lý Học viên</h1>
        <p className="text-gray-500">Dữ liệu đang lấy trực tiếp từ backend.</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Tổng số học viên</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Đang hoạt động</p>
          <p className="text-2xl font-bold text-green-600">{stats.active}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Tạm ngưng</p>
          <p className="text-2xl font-bold text-gray-500">{stats.inactive}</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row justify-between gap-4 bg-white p-4 rounded-xl shadow-sm">
        <input
          type="text"
          placeholder="Tìm theo tên, SĐT, email, khu vực..."
          className="flex-1 border border-gray-200 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
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
            onClick={() => setShowForm((prev) => !prev)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          >
            {showForm ? 'Đóng form' : 'Thêm học viên'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">{editingId ? 'Cập nhật học viên' : 'Thêm học viên mới'}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" name="full_name" placeholder="Họ tên *" value={formData.full_name} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" required />
            <input type="text" name="phone" placeholder="Số điện thoại *" value={formData.phone} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" required />
            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="area" placeholder="Khu vực" value={formData.area} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="level" placeholder="Trình độ (VD: Lớp 10)" value={formData.level} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
          </div>
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700" disabled={saving}>
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật' : 'Lưu'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); setEditingId(null); setFormData({ full_name: '', phone: '', email: '', area: '', level: '' }); }} className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500">
              Hủy
            </button>
          </div>
        </form>
      )}

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
              {filteredStudents.map((student) => (
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
                    <button className="text-blue-600 hover:text-blue-800 font-medium mr-3" onClick={() => startEdit(student)}>Sửa</button>
                    <button
                      className="text-red-600 hover:text-red-800 disabled:opacity-50"
                      onClick={() => handleDelete(student.id)}
                      disabled={savingId === student.id}
                    >
                      {savingId === student.id ? 'Đang xóa...' : 'Xóa'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredStudents.length === 0 && <div className="text-center py-10 text-gray-400">Không tìm thấy học viên nào phù hợp.</div>}
      </div>
    </div>
  );
}
