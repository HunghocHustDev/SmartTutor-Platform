import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  createLearningRequest,
  deleteLearningRequest,
  listLearningRequests,
  listSubjects,
  updateLearningRequest,
} from '../services/api';

export default function LearningRequestsPage() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [savingId, setSavingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [subjects, setSubjects] = useState([]);
  const [formData, setFormData] = useState({
    student_id: '',
    subject_id: '',
    target: '',
    requested_level: '',
    area: '',
    teaching_mode: 'OFFLINE',
    preferred_schedule: '',
    expected_fee: '',
  });

  const isStudent = user?.role === 'student';
  const isStaff = user?.role === 'staff';
  const studentIdFilter = isStudent ? user?.id : null;
  const canCreate = isStudent;

  useEffect(() => {
    if (isStudent && user?.id) {
      setFormData((prev) => ({ ...prev, student_id: String(user.id) }));
    }
  }, [isStudent, user]);

  useEffect(() => {
    if (!user) {
      return;
    }
    let active = true;
    setLoading(true);
    setError('');

    listLearningRequests(studentIdFilter ? { student_id: studentIdFilter } : {})
      .then((data) => {
        if (active) {
          setRequests(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || 'Không tải được danh sách yêu cầu học');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    listSubjects({ status: 'ACTIVE' })
      .then((data) => {
        if (active) {
          setSubjects(Array.isArray(data) ? data : []);
        }
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, [studentIdFilter, user]);

  const filteredRequests = useMemo(() => {
    if (statusFilter === 'ALL') {
      return requests;
    }
    return requests.filter((item) => item.status === statusFilter);
  }, [requests, statusFilter]);

  const resetForm = () => {
    setFormData({
      student_id: String(user?.id || ''),
      subject_id: '',
      target: '',
      requested_level: '',
      area: '',
      teaching_mode: 'OFFLINE',
      preferred_schedule: '',
      expected_fee: '',
    });
    setEditingId(null);
    setShowForm(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const payload = {
        ...formData,
        student_id: Number(user.id),
        subject_id: Number(formData.subject_id),
        expected_fee: formData.expected_fee ? Number(formData.expected_fee) : null,
      };

      if (editingId) {
        const updated = await updateLearningRequest(editingId, payload);
        setRequests((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createLearningRequest(payload);
        setRequests((prev) => [created, ...prev]);
      }

      resetForm();
    } catch (err) {
      setError(err?.message || 'Không lưu được yêu cầu học');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn hủy yêu cầu học này không?')) {
      return;
    }

    setSavingId(id);
    setError('');
    try {
      await deleteLearningRequest(id);
      setRequests((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'CANCELED' } : item)));
    } catch (err) {
      setError(err?.message || 'Không hủy được yêu cầu học');
    } finally {
      setSavingId(null);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setFormData({
      student_id: String(item.student_id || user?.id || ''),
      subject_id: String(item.subject_id || ''),
      target: item.target || item.learning_goal || '',
      requested_level: item.requested_level || '',
      area: item.area || '',
      teaching_mode: item.teaching_mode || 'OFFLINE',
      preferred_schedule: item.preferred_schedule || '',
      expected_fee: item.expected_fee ? String(item.expected_fee) : '',
    });
    setShowForm(true);
  };

  if (!user) {
    return <div className="bg-white p-6 rounded-lg shadow">Vui lòng đăng nhập để xem yêu cầu học.</div>;
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Đang tải danh sách yêu cầu học...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{isStaff ? 'Xử lý nhu cầu học' : 'Yêu cầu học'}</h1>
        <p className="text-gray-500">
          {isStaff
            ? 'Nhân viên tiếp nhận và xử lý các nhu cầu do học viên gửi lên hệ thống.'
            : 'Theo dõi và cập nhật các nhu cầu học do bạn đã gửi lên hệ thống.'}
        </p>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="flex items-center gap-2">
        <select
          className="border border-gray-200 rounded-lg px-3 py-2 bg-white focus:ring-blue-200"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="ALL">Tất cả trạng thái</option>
          <option value="PENDING">Chờ xử lý</option>
          <option value="ASSIGNED">Đã phân công</option>
          <option value="CANCELED">Đã hủy</option>
        </select>
        {canCreate && (
          <button
            onClick={() => setShowForm((prev) => !prev)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
          >
            {showForm ? 'Đóng form' : 'Tạo yêu cầu'}
          </button>
        )}
      </div>

      {showForm && canCreate && (
        <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">{editingId ? 'Cập nhật yêu cầu học' : 'Tạo yêu cầu học mới'}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select
              name="subject_id"
              value={formData.subject_id}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              required
            >
              <option value="">Chọn môn học</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name} {subject.level ? `- ${subject.level}` : ''}
                </option>
              ))}
            </select>
            <input
              name="requested_level"
              value={formData.requested_level}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              placeholder="Trình độ mong muốn"
              required
            />
            <input
              name="target"
              value={formData.target}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              placeholder="Mục tiêu học tập"
            />
            <input
              name="area"
              value={formData.area}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              placeholder="Khu vực"
            />
            <input
              name="preferred_schedule"
              value={formData.preferred_schedule}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              placeholder="Lịch mong muốn"
            />
            <input
              name="expected_fee"
              value={formData.expected_fee}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
              placeholder="Học phí mong muốn"
              type="number"
            />
            <select
              name="teaching_mode"
              value={formData.teaching_mode}
              onChange={handleInputChange}
              className="border border-gray-200 p-2 rounded-lg"
            >
              <option value="OFFLINE">OFFLINE</option>
              <option value="ONLINE">ONLINE</option>
              <option value="BOTH">BOTH</option>
            </select>
          </div>
          <div className="mt-4 flex gap-2">
            <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700" disabled={saving}>
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật' : 'Lưu'}
            </button>
            <button type="button" onClick={resetForm} className="bg-gray-400 text-white px-4 py-2 rounded-lg hover:bg-gray-500">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Môn học</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mục tiêu</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Khu vực</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lịch</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredRequests.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.subject || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{item.target || item.learning_goal || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{item.area || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{item.preferred_schedule || '-'}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{item.status}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {(isStaff || isStudent) && (
                      <button className="text-blue-600 hover:text-blue-800 font-medium mr-3" onClick={() => startEdit(item)}>
                        Sửa
                      </button>
                    )}
                    <button
                      className="text-red-600 hover:text-red-800 disabled:opacity-50"
                      onClick={() => handleDelete(item.id)}
                      disabled={savingId === item.id}
                    >
                      {savingId === item.id ? 'Đang hủy...' : 'Hủy'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredRequests.length === 0 && <div className="text-center py-10 text-gray-400">Không có yêu cầu học nào.</div>}
      </div>
    </div>
  );
}
