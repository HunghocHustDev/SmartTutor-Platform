import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createTutor, deleteTutor, listTutors, updateTutor } from '../services/api';

export default function TutorsPage() {
  const { user } = useAuth();
  const [tutors, setTutors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [saving, setSaving] = useState(false);
  const [savingId, setSavingId] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    full_name: '',
    phone: '',
    email: '',
    area: '',
    subjects: '',
    experience: '',
  });

  const canView = user?.role === 'staff';

  useEffect(() => {
    if (!canView) {
      return;
    }
    let active = true;
    setLoading(true);
    setError('');
    listTutors()
      .then((data) => {
        if (active) {
          setTutors(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || 'Không tải được danh sách gia sư');
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

  const filteredTutors = useMemo(() => {
    let result = tutors;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter((item) =>
        [item.full_name, item.phone, item.email, item.area, item.subjects]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(term))
      );
    }
    if (statusFilter !== 'ALL') {
      result = result.filter((item) => item.status === statusFilter);
    }
    return result;
  }, [tutors, searchTerm, statusFilter]);

  const stats = useMemo(() => ({
    total: tutors.length,
    active: tutors.filter((t) => t.status === 'ACTIVE').length,
    inactive: tutors.filter((t) => t.status === 'INACTIVE').length,
  }), [tutors]);

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
        const updated = await updateTutor(editingId, {
          ...formData,
          experience: Number(formData.experience || 0),
        });
        setTutors((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createTutor({
          ...formData,
          experience: Number(formData.experience || 0),
        });
        setTutors((prev) => [created, ...prev]);
      }
      setFormData({ full_name: '', phone: '', email: '', area: '', subjects: '', experience: '' });
      setEditingId(null);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không tạo được gia sư');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (tutor) => {
    setEditingId(tutor.id);
    setFormData({
      full_name: tutor.full_name || '',
      phone: tutor.phone || '',
      email: tutor.email || '',
      area: tutor.area || '',
      subjects: tutor.subjects || '',
      experience: String(tutor.experience ?? ''),
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn ngừng hoạt động gia sư này không?')) {
      return;
    }
    setSavingId(id);
    setError('');
    try {
      await deleteTutor(id);
      setTutors((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'INACTIVE' } : item)));
    } catch (err) {
      setError(err?.message || 'Không xóa được gia sư');
    } finally {
      setSavingId(null);
    }
  };

  if (!canView) {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg inline-block">
          Bạn không có quyền truy cập trang quản lý gia sư.
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Đang tải danh sách gia sư...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Quản lý Gia sư</h1>
        <p className="text-gray-500">Dữ liệu đang lấy trực tiếp từ backend.</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Tổng số gia sư</p>
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
          placeholder="Tìm theo tên, SĐT, email, khu vực, môn dạy..."
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
            {showForm ? 'Đóng form' : 'Thêm gia sư'}
          </button>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">{editingId ? 'Cập nhật gia sư' : 'Thêm gia sư mới'}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input type="text" name="full_name" placeholder="Họ tên *" value={formData.full_name} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" required />
            <input type="text" name="phone" placeholder="Số điện thoại *" value={formData.phone} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" required />
            <input type="email" name="email" placeholder="Email" value={formData.email} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="area" placeholder="Khu vực" value={formData.area} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="text" name="subjects" placeholder="Môn dạy (vd: Toán, Lý)" value={formData.subjects} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
            <input type="number" name="experience" placeholder="Số năm kinh nghiệm" value={formData.experience} onChange={handleInputChange} className="border border-gray-200 p-2 rounded-lg" />
          </div>
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700" disabled={saving}>
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật' : 'Lưu'}
            </button>
            <button type="button" onClick={() => { setShowForm(false); setEditingId(null); setFormData({ full_name: '', phone: '', email: '', area: '', subjects: '', experience: '' }); }} className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Môn dạy</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kinh nghiệm</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredTutors.map((tutor) => (
                <tr key={tutor.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{tutor.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{tutor.full_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{tutor.phone}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{tutor.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{tutor.area}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{tutor.subjects || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{tutor.experience} năm</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${tutor.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {tutor.status === 'ACTIVE' ? 'Đang hoạt động' : 'Tạm ngưng'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button className="text-blue-600 hover:text-blue-800 font-medium mr-3" onClick={() => startEdit(tutor)}>Sửa</button>
                    <button
                      className="text-red-600 hover:text-red-800 disabled:opacity-50"
                      onClick={() => handleDelete(tutor.id)}
                      disabled={savingId === tutor.id}
                    >
                      {savingId === tutor.id ? 'Đang xóa...' : 'Xóa'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredTutors.length === 0 && <div className="text-center py-10 text-gray-400">Không tìm thấy gia sư nào phù hợp.</div>}
      </div>
    </div>
  );
}
