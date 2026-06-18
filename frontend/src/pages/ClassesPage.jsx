import React, { useEffect, useMemo, useState } from 'react';
import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { createClass, deleteClass, listAssignments, listClasses, listLearningRequests, updateClass } from '../services/api';
import { formatDate } from '../utils/formatting';

const statusConfig = {
  ACTIVE: { label: 'Đang diễn ra', color: 'bg-green-100 text-green-700' },
  PAUSED: { label: 'Tạm dừng', color: 'bg-yellow-100 text-yellow-700' },
  COMPLETED: { label: 'Hoàn thành', color: 'bg-blue-100 text-blue-700' },
  CANCELED: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' },
  FINISHED: { label: 'Hoàn thành', color: 'bg-blue-100 text-blue-700' },
};

export default function ClassesPage() {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [savingId, setSavingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [assignments, setAssignments] = useState([]);
  const [requests, setRequests] = useState([]);
  const [formData, setFormData] = useState({
    assignment_id: '',
    class_code: '',
    tuition_fee_per_session: '',
    teaching_mode: 'OFFLINE',
    location: '',
    start_date: '',
    end_date: '',
    status: 'ACTIVE',
  });

  const canView = user?.role === 'staff' || user?.role === 'tutor' || user?.role === 'student';
  const canManage = user?.role === 'staff';

  useEffect(() => {
    if (!canView) {
      return;
    }
    let active = true;
    setLoading(true);
    setError('');
    const filters = user?.role === 'student'
      ? { student_id: user.id }
      : user?.role === 'tutor'
        ? { tutor_id: user.id }
        : {};
    listClasses(filters)
      .then((data) => {
        if (active) {
          setClasses(Array.isArray(data) ? data : []);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || 'Không tải được danh sách lớp học');
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    if (user?.role === 'staff') {
      listAssignments({ status: 'ASSIGNED' }).then((data) => active && setAssignments(Array.isArray(data) ? data : [])).catch(() => {});
      listLearningRequests().then((data) => active && setRequests(Array.isArray(data) ? data : [])).catch(() => {});
    }
    return () => {
      active = false;
    };
  }, [canView, user]);

  const filteredClasses = useMemo(() => {
    let result = classes;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter((item) =>
        [item.code, item.student, item.tutor, item.subject, item.location]
          .filter(Boolean)
          .some((value) => String(value).toLowerCase().includes(term))
      );
    }
    if (statusFilter !== 'ALL') {
      result = result.filter((item) => item.status === statusFilter);
    }
    return result;
  }, [classes, searchTerm, statusFilter]);

  const requestMap = useMemo(() => Object.fromEntries(requests.map((r) => [r.id, r])), [requests]);

  const stats = useMemo(() => ({
    total: classes.length,
    active: classes.filter((c) => c.status === 'ACTIVE').length,
    paused: classes.filter((c) => c.status === 'PAUSED').length,
    completed: classes.filter((c) => c.status === 'COMPLETED' || c.status === 'FINISHED').length,
  }), [classes]);

  const handleDelete = async (classId) => {
    if (!window.confirm('Bạn có muốn hủy lớp này không?')) {
      return;
    }
    setSavingId(classId);
    setError('');
    try {
      await deleteClass(classId);
      setClasses((prev) => prev.map((item) => (item.id === classId ? { ...item, status: 'CANCELED' } : item)));
    } catch (err) {
      setError(err?.message || 'Không hủy được lớp học');
    } finally {
      setSavingId(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        assignment_id: Number(formData.assignment_id),
        class_code: formData.class_code || null,
        tuition_fee_per_session: Number(formData.tuition_fee_per_session || 0),
        teaching_mode: formData.teaching_mode,
        location: formData.location || null,
        start_date: formData.start_date,
        end_date: formData.end_date || null,
        status: formData.status,
      };
      if (editingId) {
        const updated = await updateClass(editingId, payload);
        setClasses((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createClass(payload);
        setClasses((prev) => [created, ...prev]);
      }
      setShowForm(false);
      setEditingId(null);
      setFormData({
        assignment_id: '',
        class_code: '',
        tuition_fee_per_session: '',
        teaching_mode: 'OFFLINE',
        location: '',
        start_date: '',
        end_date: '',
        status: 'ACTIVE',
      });
    } catch (err) {
      setError(err?.message || 'Không lưu được lớp học');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (cls) => {
    setEditingId(cls.id);
    setFormData({
      assignment_id: '',
      class_code: cls.code || '',
      tuition_fee_per_session: String(cls.tuition_fee_per_session ?? cls.fee ?? ''),
      teaching_mode: cls.teaching_mode || 'OFFLINE',
      location: cls.location || '',
      start_date: cls.startDate || '',
      end_date: cls.endDate || '',
      status: cls.status || 'ACTIVE',
    });
    setShowForm(true);
  };

  if (!canView) {
    return (
      <div className="p-6 text-center">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg inline-block">
          Bạn không có quyền truy cập trang quản lý lớp học.
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        <span className="ml-3 text-gray-600">Đang tải danh sách lớp...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Quản lý Lớp học</h1>
        <p className="text-gray-500">Dữ liệu đang được lấy trực tiếp từ backend SQL Server.</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Tổng số lớp</p>
          <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Đang diễn ra</p>
          <p className="text-2xl font-bold text-green-600">{stats.active}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Tạm dừng</p>
          <p className="text-2xl font-bold text-yellow-600">{stats.paused}</p>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <p className="text-sm text-gray-500">Hoàn thành</p>
          <p className="text-2xl font-bold text-blue-600">{stats.completed}</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row justify-between gap-4 bg-white p-4 rounded-xl shadow-sm">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Tìm theo mã lớp, học viên, gia sư, môn học..."
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
            <option value="COMPLETED">Hoàn thành</option>
            <option value="CANCELED">Đã hủy</option>
          </select>
          {canManage && (
            <button onClick={() => setShowForm((prev) => !prev)} className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700">
              {showForm ? 'Đóng form' : editingId ? 'Đang sửa lớp' : 'Tạo lớp'}
            </button>
          )}
        </div>
      </div>

      {showForm && canManage && (
        <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow-sm border border-gray-100 space-y-4">
          {!editingId && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Phân công <span className="text-red-500">*</span>
              </label>
              <select
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                value={formData.assignment_id}
                onChange={(e) => setFormData((prev) => ({ ...prev, assignment_id: e.target.value }))}
                required
              >
                <option value="">-- Chọn phân công đã được assign --</option>
                {assignments.map((item) => {
                  const req = requestMap[item.request_id];
                  return (
                    <option key={item.id} value={item.id}>
                      #{item.id} · {req?.student || `HS #${item.request_id}`} · {req?.subject || `Môn #${req?.subject_id || item.request_id}`} · {req?.area || 'Khu vực khác'}
                    </option>
                  );
                })}
              </select>
              {formData.assignment_id && requestMap[formData.assignment_id] && (() => {
                const info = requestMap[formData.assignment_id];
                return (
                  <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-100 text-sm">
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                      <div><span className="text-gray-500">Học sinh:</span> <span className="font-medium">{info.student || '-'}</span></div>
                      <div><span className="text-gray-500">Gia sư:</span> <span className="font-medium">{info.tutor || `GS #${info.assignment_tutor_id || info.tutor_id || '-'}`}</span></div>
                      <div><span className="text-gray-500">Môn:</span> <span className="font-medium">{info.subject || '-'}</span></div>
                      <div><span className="text-gray-500">Khu vực:</span> <span className="font-medium">{info.area || '-'}</span></div>
                      <div><span className="text-gray-500">Hình thức:</span> <span className="font-medium">{info.teaching_mode || 'OFFLINE'}</span></div>
                      {info.expected_fee && <div><span className="text-gray-500">Học phí mong muốn:</span> <span className="font-medium">{Number(info.expected_fee).toLocaleString()}đ/buổi</span></div>}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Mã lớp <span className="text-gray-400 font-normal">(tự sinh nếu bỏ trống)</span>
              </label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                placeholder="VD: LOP-001"
                value={formData.class_code}
                onChange={(e) => setFormData((prev) => ({ ...prev, class_code: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Học phí / buổi <span className="text-red-500">*</span> <span className="text-gray-400 font-normal">(VNĐ)</span>
              </label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                type="number"
                placeholder="VD: 150000"
                value={formData.tuition_fee_per_session}
                onChange={(e) => setFormData((prev) => ({ ...prev, tuition_fee_per_session: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Hình thức dạy</label>
              <select
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                value={formData.teaching_mode}
                onChange={(e) => setFormData((prev) => ({ ...prev, teaching_mode: e.target.value }))}
              >
                <option value="OFFLINE">Offline (Gặp trực tiếp)</option>
                <option value="ONLINE">Online (Trực tuyến)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Địa điểm <span className="text-gray-400 font-normal">(nếu offline)</span>
              </label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                placeholder="VD: 123 Nguyễn Trãi, Quận 1"
                value={formData.location}
                onChange={(e) => setFormData((prev) => ({ ...prev, location: e.target.value }))}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Ngày bắt đầu <span className="text-red-500">*</span>
              </label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData((prev) => ({ ...prev, start_date: e.target.value }))}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Ngày kết thúc <span className="text-gray-400 font-normal">(tùy chọn)</span>
              </label>
              <input
                className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData((prev) => ({ ...prev, end_date: e.target.value }))}
              />
            </div>
            {editingId && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Trạng thái</label>
                <select
                  className="w-full rounded-lg border border-gray-200 px-3 py-2.5 focus:ring-2 focus:ring-blue-200 focus:border-blue-400"
                  value={formData.status}
                  onChange={(e) => setFormData((prev) => ({ ...prev, status: e.target.value }))}
                >
                  <option value="ACTIVE">ACTIVE - Đang diễn ra</option>
                  <option value="PAUSED">PAUSED - Tạm dừng</option>
                  <option value="COMPLETED">COMPLETED - Hoàn thành</option>
                  <option value="CANCELED">CANCELED - Đã hủy</option>
                </select>
              </div>
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <button
              className="rounded-lg bg-green-600 px-6 py-2.5 text-white font-medium hover:bg-green-700 disabled:opacity-50"
              disabled={saving}
              type="submit"
            >
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật lớp' : 'Tạo lớp học'}
            </button>
            <button
              className="rounded-lg bg-gray-200 px-6 py-2.5 text-gray-700 font-medium hover:bg-gray-300"
              type="button"
              onClick={() => { setShowForm(false); setEditingId(null); }}
            >
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mã lớp</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Học viên</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gia sư</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Môn học</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lịch học</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Bắt đầu</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Học phí/buổi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trạng thái</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredClasses.map((cls) => {
                const status = statusConfig[cls.status] || statusConfig.ACTIVE;
                const feeValue = Number(cls.fee ?? cls.tuition_fee_per_session ?? 0);
                return (
                  <tr key={cls.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap font-mono text-sm font-medium text-gray-900">{cls.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.student || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.tutor || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      <span className="font-medium">{cls.subject || '-'}</span>
                      <span className="text-gray-400 ml-1">{cls.level ? `(${cls.level})` : ''}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{cls.schedule || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{formatDate(cls.startDate)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-800">{feeValue.toLocaleString()}đ</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${status.color}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button className="text-blue-600 hover:text-blue-800 font-medium mr-3">Xem</button>
                      {canManage && <button className="text-blue-600 hover:text-blue-800 font-medium mr-3" onClick={() => startEdit(cls)}>Sửa</button>}
                      {canManage && (
                        <button
                          className="text-red-600 hover:text-red-800 disabled:opacity-50"
                          onClick={() => handleDelete(cls.id)}
                          disabled={savingId === cls.id}
                        >
                          {savingId === cls.id ? 'Đang hủy...' : 'Hủy'}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {filteredClasses.length === 0 && (
          <div className="text-center py-10 text-gray-400">Không tìm thấy lớp học nào phù hợp.</div>
        )}
      </div>
    </div>
  );
}
