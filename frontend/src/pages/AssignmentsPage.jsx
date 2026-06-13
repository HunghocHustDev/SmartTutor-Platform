import React, { useEffect, useMemo, useState } from 'react';
import {
  cancelAssignment,
  createAssignment,
  listAssignments,
  listClasses,
  listLearningRequests,
  listTutors,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { formatDateTime, learningRequestStatusLabel } from '../utils/formatting';

const emptyForm = {
  request_id: '',
  tutor_id: '',
  note: '',
};

export default function AssignmentsPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'staff';
  const [assignments, setAssignments] = useState([]);
  const [requests, setRequests] = useState([]);
  const [tutors, setTutors] = useState([]);
  const [classes, setClasses] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (!canManage) return;
    let active = true;
    Promise.all([listAssignments(), listLearningRequests(), listTutors({ status: 'ACTIVE' }), listClasses()])
      .then(([assignmentData, requestData, tutorData, classData]) => {
        if (!active) return;
        setAssignments(Array.isArray(assignmentData) ? assignmentData : []);
        setRequests(Array.isArray(requestData) ? requestData : []);
        setTutors(Array.isArray(tutorData) ? tutorData : []);
        setClasses(Array.isArray(classData) ? classData : []);
      })
      .catch((err) => active && setError(err?.message || 'Không tải được dữ liệu phân công'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [canManage]);

  const requestMap = useMemo(() => Object.fromEntries(requests.map((item) => [item.id, item])), [requests]);
  const tutorMap = useMemo(() => Object.fromEntries(tutors.map((item) => [item.id, item])), [tutors]);
  const classAssignmentIds = useMemo(() => new Set(classes.map((item) => item.assignment_id).filter(Boolean)), [classes]);

  const filteredAssignments = useMemo(() => {
    if (statusFilter === 'ALL') return assignments;
    return assignments.filter((item) => item.status === statusFilter);
  }, [assignments, statusFilter]);

  const pendingRequests = useMemo(
    () => requests.filter((item) => item.status === 'PENDING'),
    [requests]
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const created = await createAssignment({
        request_id: Number(form.request_id),
        tutor_id: Number(form.tutor_id),
        staff_id: user.id,
        note: form.note || null,
      });
      setAssignments((prev) => [created, ...prev]);
      setRequests((prev) => prev.map((item) => (item.id === created.request_id ? { ...item, status: 'ASSIGNED' } : item)));
      setForm(emptyForm);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không tạo được phân công');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = async (assignment) => {
    if (!window.confirm('Bạn có muốn hủy phân công này không?')) return;
    try {
      await cancelAssignment(assignment.id);
      setAssignments((prev) => prev.map((item) => (item.id === assignment.id ? { ...item, status: 'CANCELED' } : item)));
      setRequests((prev) => prev.map((item) => (item.id === assignment.request_id ? { ...item, status: 'PENDING' } : item)));
    } catch (err) {
      setError(err?.message || 'Không hủy được phân công');
    }
  };

  if (!canManage) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-600">Chỉ nhân viên mới được phân công gia sư.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải dữ liệu phân công...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Phân công gia sư</h1>
          <p className="text-sm text-gray-500">Bước tách biệt giữa yêu cầu học và lớp học chính thức.</p>
        </div>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={() => setShowForm((prev) => !prev)}>
          {showForm ? 'Đóng form' : 'Tạo phân công'}
        </button>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <StatCard label="Request chờ" value={pendingRequests.length} />
        <StatCard label="Phân công đang hiệu lực" value={assignments.filter((item) => item.status === 'ASSIGNED').length} />
        <StatCard label="Đã có lớp" value={classes.length} />
        <div className="rounded-xl bg-white p-4 shadow-sm">
          <label className="text-sm text-gray-500">Lọc trạng thái</label>
          <select className="mt-2 w-full rounded-lg border border-gray-200 px-3 py-2" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="ALL">Tất cả</option>
            <option value="ASSIGNED">ASSIGNED</option>
            <option value="CANCELED">CANCELED</option>
          </select>
        </div>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.request_id} onChange={(e) => setForm((prev) => ({ ...prev, request_id: e.target.value }))} required>
            <option value="">Chọn request PENDING</option>
            {pendingRequests.map((item) => (
              <option key={item.id} value={item.id}>
                #{item.id} - {item.student} - {item.subject} - {item.area || 'Không rõ khu vực'}
              </option>
            ))}
          </select>
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.tutor_id} onChange={(e) => setForm((prev) => ({ ...prev, tutor_id: e.target.value }))} required>
            <option value="">Chọn gia sư ACTIVE</option>
            {tutors.map((item) => (
              <option key={item.id} value={item.id}>
                #{item.id} - {item.full_name} - {item.subjects || 'Chưa khai báo môn'}
              </option>
            ))}
          </select>
          <textarea className="rounded-lg border border-gray-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Ghi chú phân công" value={form.note} onChange={(e) => setForm((prev) => ({ ...prev, note: e.target.value }))} />
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">
              {saving ? 'Đang tạo...' : 'Tạo assignment'}
            </button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => setShowForm(false)}>
              Hủy
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Assignment</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Request</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Gia sư</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Đã gắn lớp</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thời gian</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredAssignments.map((item) => {
              const request = requestMap[item.request_id];
              const tutor = tutorMap[item.tutor_id];
              const hasClass = classAssignmentIds.has(item.id);
              return (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.id}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <div className="font-medium">{request ? `${request.student} - ${request.subject}` : `Request #${item.request_id}`}</div>
                    <div className="text-xs text-gray-500">{request ? learningRequestStatusLabel(request.status) : '-'}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">{tutor ? tutor.full_name : `Tutor #${item.tutor_id}`}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.status}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{hasClass ? 'Đã tạo lớp' : 'Chưa có lớp'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{formatDateTime(item.assigned_at)}</td>
                  <td className="px-4 py-3 text-sm">
                    {!hasClass && item.status === 'ASSIGNED' ? (
                      <button className="text-red-600 hover:text-red-800" onClick={() => handleCancel(item)}>Hủy phân công</button>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {filteredAssignments.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có assignment nào.</div>}
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="rounded-xl bg-white p-4 shadow-sm">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}
