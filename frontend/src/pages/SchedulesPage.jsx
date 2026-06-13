import React, { useEffect, useMemo, useState } from 'react';
import { createSchedule, deleteSchedule, listClasses, listSchedules, updateSchedule } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { DAY_LABELS, formatDate, formatTime } from '../utils/formatting';

const emptyForm = {
  class_id: '',
  day_of_week: '1',
  start_time: '19:00',
  end_time: '20:30',
  effective_from: '',
  effective_to: '',
  status: 'ACTIVE',
  note: '',
};

export default function SchedulesPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'staff';
  const [schedules, setSchedules] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (!user) return;
    let active = true;
    const filters = user.role === 'student' ? { student_id: user.id } : user.role === 'tutor' ? { tutor_id: user.id } : {};
    Promise.all([listSchedules(filters), listClasses(filters)])
      .then(([scheduleData, classData]) => {
        if (!active) return;
        setSchedules(Array.isArray(scheduleData) ? scheduleData : []);
        setClasses(Array.isArray(classData) ? classData : []);
      })
      .catch((err) => active && setError(err?.message || 'Không tải được lịch học'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [user]);

  const classMap = useMemo(() => Object.fromEntries(classes.map((item) => [item.id, item])), [classes]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    const payload = {
      class_id: Number(form.class_id),
      day_of_week: Number(form.day_of_week),
      start_time: form.start_time,
      end_time: form.end_time,
      effective_from: form.effective_from || null,
      effective_to: form.effective_to || null,
      status: form.status,
      note: form.note || null,
    };
    try {
      if (editingId) {
        const updated = await updateSchedule(editingId, payload);
        setSchedules((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createSchedule(payload);
        setSchedules((prev) => [created, ...prev]);
      }
      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không lưu được lịch học');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      class_id: String(item.class_id),
      day_of_week: String(item.day_of_week),
      start_time: formatTime(item.start_time),
      end_time: formatTime(item.end_time),
      effective_from: item.effective_from || '',
      effective_to: item.effective_to || '',
      status: item.status,
      note: item.note || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn ngừng hiệu lực lịch học này không?')) return;
    try {
      await deleteSchedule(id);
      setSchedules((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'INACTIVE' } : item)));
    } catch (err) {
      setError(err?.message || 'Không ngừng hiệu lực được lịch học');
    }
  };

  if (!user) {
    return <div className="rounded-lg bg-white p-6 shadow">Vui lòng đăng nhập để xem lịch học.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải lịch học...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{canManage ? 'Quản lý lịch học cố định' : user.role === 'tutor' ? 'Lịch dạy của tôi' : 'Lịch học của tôi'}</h1>
          <p className="text-sm text-gray-500">Lấy từ `CLASS_SCHEDULE`, có filter theo actor hiện tại.</p>
        </div>
        {canManage && (
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={() => setShowForm((prev) => !prev)}>
            {showForm ? 'Đóng form' : 'Thêm lịch học'}
          </button>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {showForm && canManage && (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.class_id} onChange={(e) => setForm((prev) => ({ ...prev, class_id: e.target.value }))} required>
            <option value="">Chọn lớp học</option>
            {classes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.code} - {item.subject} - {item.student}
              </option>
            ))}
          </select>
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.day_of_week} onChange={(e) => setForm((prev) => ({ ...prev, day_of_week: e.target.value }))}>
            {Object.entries(DAY_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={form.start_time} onChange={(e) => setForm((prev) => ({ ...prev, start_time: e.target.value }))} />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={form.end_time} onChange={(e) => setForm((prev) => ({ ...prev, end_time: e.target.value }))} />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={form.effective_from} onChange={(e) => setForm((prev) => ({ ...prev, effective_from: e.target.value }))} />
          <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={form.effective_to} onChange={(e) => setForm((prev) => ({ ...prev, effective_to: e.target.value }))} />
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}>
            <option value="ACTIVE">ACTIVE</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
          <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Ghi chú" value={form.note} onChange={(e) => setForm((prev) => ({ ...prev, note: e.target.value }))} />
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật lịch học' : 'Tạo lịch học'}
            </button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => { setShowForm(false); setEditingId(null); setForm(emptyForm); }}>
              Hủy
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Khung giờ</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Hiệu lực</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Ghi chú</th>
              {canManage && <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {schedules.map((item) => {
              const classItem = classMap[item.class_id];
              return (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <div className="font-medium text-gray-900">{classItem ? classItem.code : `Class #${item.class_id}`}</div>
                    <div className="text-xs text-gray-500">{classItem ? `${classItem.subject} - ${classItem.student}` : '-'}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.display_text}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{formatDate(item.effective_from)} - {formatDate(item.effective_to)}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.status}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.note || '-'}</td>
                  {canManage && (
                    <td className="px-4 py-3 text-sm">
                      <button className="mr-3 text-blue-600 hover:text-blue-800" onClick={() => startEdit(item)}>Sửa</button>
                      <button className="text-red-600 hover:text-red-800" onClick={() => handleDelete(item.id)}>Deactivate</button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
        {schedules.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có lịch học nào.</div>}
      </div>
    </div>
  );
}
