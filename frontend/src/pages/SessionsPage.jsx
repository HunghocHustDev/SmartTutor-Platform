import React, { useEffect, useMemo, useState } from 'react';
import {
  createSession,
  deleteSession,
  generateSessionsFromSchedules,
  listClasses,
  listSchedules,
  listSessions,
  previewSessionsFromSchedules,
  updateSessionStatus,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { formatDate, formatTime } from '../utils/formatting';

const emptyForm = {
  class_id: '',
  schedule_id: '',
  session_number: '',
  date: '',
  start_time: '',
  end_time: '',
  status: 'SCHEDULED',
  content_note: '',
};

export default function SessionsPage() {
  const { user } = useAuth();
  const canCreate = user?.role === 'staff';
  const canUpdateStatus = user?.role === 'staff' || user?.role === 'tutor';
  const [sessions, setSessions] = useState([]);
  const [classes, setClasses] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingId, setSavingId] = useState(null);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [form, setForm] = useState(emptyForm);
  const [showGenerate, setShowGenerate] = useState(false);
  const [generateClassId, setGenerateClassId] = useState('');
  const [generateStart, setGenerateStart] = useState('');
  const [generateEnd, setGenerateEnd] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatePreview, setGeneratePreview] = useState(null);
  const [generateError, setGenerateError] = useState('');
  const [completingSession, setCompletingSession] = useState(null);
  const [completingNote, setCompletingNote] = useState('');

  useEffect(() => {
    if (!user) return;
    let active = true;
    const filters = user.role === 'student' ? { student_id: user.id } : user.role === 'tutor' ? { tutor_id: user.id } : {};
    Promise.all([listSessions(filters), listClasses(filters), listSchedules(filters)])
      .then(([sessionData, classData, scheduleData]) => {
        if (!active) return;
        setSessions(Array.isArray(sessionData) ? sessionData : []);
        setClasses(Array.isArray(classData) ? classData : []);
        setSchedules(Array.isArray(scheduleData) ? scheduleData : []);
      })
      .catch((err) => active && setError(err?.message || 'Không tải được buổi học'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [user]);

  const classMap = useMemo(() => Object.fromEntries(classes.map((item) => [item.id, item])), [classes]);
  const filteredSessions = useMemo(() => {
    if (statusFilter === 'ALL') return sessions;
    return sessions.filter((item) => item.status === statusFilter);
  }, [sessions, statusFilter]);
  const scheduleOptions = useMemo(
    () => schedules.filter((item) => !form.class_id || String(item.class_id) === String(form.class_id)),
    [schedules, form.class_id]
  );

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const created = await createSession({
        class_id: Number(form.class_id),
        schedule_id: form.schedule_id ? Number(form.schedule_id) : null,
        session_number: form.session_number ? Number(form.session_number) : null,
        date: form.date,
        start_time: form.start_time || null,
        end_time: form.end_time || null,
        status: form.status,
        content_note: form.content_note || null,
      });
      setSessions((prev) => [created, ...prev]);
      setForm(emptyForm);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không tạo được buổi học');
    } finally {
      setSaving(false);
    }
  };

  const handleQuickStatus = async (session, status) => {
    if (status === 'COMPLETED') {
      setCompletingSession(session);
      setCompletingNote(session.content || '');
      return;
    }
    await submitStatus(session, status, session.content || '');
  };

  const submitStatus = async (session, status, content) => {
    setSavingId(session.id);
    setError('');
    try {
      const updated = await updateSessionStatus(session.id, {
        status,
        content_note: content || null,
      });
      setSessions((prev) => prev.map((item) => (item.id === session.id ? updated : item)));
    } catch (err) {
      setError(err?.message || 'Không cập nhật được trạng thái buổi học');
    } finally {
      setSavingId(null);
    }
  };

  const confirmComplete = async () => {
    if (!completingSession) return;
    const session = completingSession;
    setCompletingSession(null);
    setCompletingNote('');
    await submitStatus(session, 'COMPLETED', completingNote);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn hủy buổi học này không?')) return;
    try {
      await deleteSession(id);
      setSessions((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'CANCELED' } : item)));
    } catch (err) {
      setError(err?.message || 'Không hủy được buổi học');
    }
  };

  const handlePreviewGenerate = async () => {
    setGenerateError('');
    if (!generateClassId) {
      setGenerateError('Vui lòng chọn lớp học.');
      return;
    }
    setGenerating(true);
    try {
      const preview = await previewSessionsFromSchedules({
        class_id: Number(generateClassId),
        range_start: generateStart || null,
        range_end: generateEnd || null,
      });
      setGeneratePreview(preview);
    } catch (err) {
      setGenerateError(err?.message || 'Không xem trước được');
      setGeneratePreview(null);
    } finally {
      setGenerating(false);
    }
  };

  const handleConfirmGenerate = async () => {
    setGenerateError('');
    setGenerating(true);
    try {
      const result = await generateSessionsFromSchedules({
        class_id: Number(generateClassId),
        range_start: generateStart || null,
        range_end: generateEnd || null,
      });
      if (result.created_count > 0) {
        const fresh = await listSessions(filters);
        setSessions(Array.isArray(fresh) ? fresh : sessions);
      }
      setGeneratePreview(null);
      setShowGenerate(false);
      setGenerateClassId('');
      setGenerateStart('');
      setGenerateEnd('');
    } catch (err) {
      setGenerateError(err?.message || 'Không tạo được buổi học tự động');
    } finally {
      setGenerating(false);
    }
  };

  if (!user) {
    return <div className="rounded-lg bg-white p-6 shadow">Vui lòng đăng nhập để xem buổi học.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải buổi học...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{user.role === 'student' ? 'Lịch sử buổi học' : 'Quản lý buổi học'}</h1>
          <p className="text-sm text-gray-500">Theo dõi session thực tế từ `LESSON_SESSION`.</p>
        </div>
        {canCreate && (
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" onClick={() => setShowForm((prev) => !prev)}>
            {showForm ? 'Đóng form' : 'Tạo buổi học'}
          </button>
        )}
        {canCreate && (
          <button className="rounded-lg bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700" onClick={() => setShowGenerate((prev) => !prev)}>
            {showGenerate ? 'Đóng auto-gen' : 'Tạo buổi tự động từ lịch cố định'}
          </button>
        )}
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="rounded-xl bg-white p-4 shadow-sm">
        <select className="rounded-lg border border-gray-200 px-3 py-2" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="ALL">Tất cả trạng thái</option>
          <option value="SCHEDULED">SCHEDULED</option>
          <option value="COMPLETED">COMPLETED</option>
          <option value="STUDENT_ABSENT">STUDENT_ABSENT</option>
          <option value="TUTOR_ABSENT">TUTOR_ABSENT</option>
          <option value="CANCELED">CANCELED</option>
        </select>
      </div>

      {showForm && canCreate && (
        <form onSubmit={handleCreate} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Lớp học</span>
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.class_id} onChange={(e) => setForm((prev) => ({ ...prev, class_id: e.target.value, schedule_id: '' }))} required>
              <option value="">-- Chọn lớp --</option>
              {classes.map((item) => (
                <option key={item.id} value={item.id}>{item.code} - {item.subject} - {item.student}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Lịch cố định (tuỳ chọn)</span>
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.schedule_id} onChange={(e) => setForm((prev) => ({ ...prev, schedule_id: e.target.value }))}>
              <option value="">-- Không gắn --</option>
              {scheduleOptions.map((item) => (
                <option key={item.id} value={item.id}>{item.display_text}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Số buổi</span>
            <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Số buổi" value={form.session_number} onChange={(e) => setForm((prev) => ({ ...prev, session_number: e.target.value }))} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Ngày <span className="text-red-500">*</span></span>
            <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={form.date} onChange={(e) => setForm((prev) => ({ ...prev, date: e.target.value }))} required />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Giờ bắt đầu</span>
            <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={form.start_time} onChange={(e) => setForm((prev) => ({ ...prev, start_time: e.target.value }))} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Giờ kết thúc</span>
            <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={form.end_time} onChange={(e) => setForm((prev) => ({ ...prev, end_time: e.target.value }))} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Trạng thái</span>
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}>
              <option value="SCHEDULED">SCHEDULED</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="STUDENT_ABSENT">STUDENT_ABSENT</option>
              <option value="TUTOR_ABSENT">TUTOR_ABSENT</option>
              <option value="CANCELED">CANCELED</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-gray-700">Nội dung buổi học</span>
            <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Nội dung buổi học" value={form.content_note} onChange={(e) => setForm((prev) => ({ ...prev, content_note: e.target.value }))} />
          </label>
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">
              {saving ? 'Đang tạo...' : 'Tạo session'}
            </button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => setShowForm(false)}>Hủy</button>
          </div>
        </form>
      )}

      {completingSession && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg space-y-4 rounded-2xl bg-white p-6 shadow-xl">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Hoàn thành buổi học #{completingSession.id}</h3>
              <p className="text-sm text-gray-500">Vui lòng nhập nội dung buổi học để ghi nhận.</p>
            </div>
            <textarea
              className="h-32 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              placeholder="Nhập nội dung buổi học..."
              value={completingNote}
              onChange={(e) => setCompletingNote(e.target.value)}
              autoFocus
            />
            <div className="flex justify-end gap-2">
              <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => { setCompletingSession(null); setCompletingNote(''); }}>Hủy</button>
              <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" type="button" onClick={confirmComplete}>Xác nhận hoàn thành</button>
            </div>
          </div>
        </div>
      )}

      {showGenerate && canCreate && (
        <div className="space-y-3 rounded-xl bg-white p-6 shadow-sm">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Tạo buổi học tự động từ lịch cố định</h2>
            <p className="text-sm text-gray-500">Hệ thống sẽ quét các schedule ACTIVE của lớp và sinh ra các buổi SCHEDULED, bỏ qua các buổi đã tồn tại.</p>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-gray-700">Lớp học</span>
              <select className="rounded-lg border border-gray-200 px-3 py-2" value={generateClassId} onChange={(e) => setGenerateClassId(e.target.value)}>
                <option value="">-- Chọn lớp --</option>
                {classes.map((item) => (
                  <option key={item.id} value={item.id}>{item.code} - {item.subject} - {item.student}</option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-gray-700">Từ ngày</span>
              <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={generateStart} onChange={(e) => setGenerateStart(e.target.value)} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-gray-700">Đến ngày</span>
              <input className="rounded-lg border border-gray-200 px-3 py-2" type="date" value={generateEnd} onChange={(e) => setGenerateEnd(e.target.value)} />
            </label>
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50" type="button" disabled={generating || !generateClassId} onClick={handlePreviewGenerate}>
              {generating ? 'Đang xử lý...' : 'Xem trước'}
            </button>
            <button className="rounded-lg bg-emerald-600 px-4 py-2 text-white hover:bg-emerald-700 disabled:opacity-50" type="button" disabled={generating || !generatePreview || generatePreview.preview_count === 0} onClick={handleConfirmGenerate}>
              Xác nhận tạo ({generatePreview?.preview_count ?? 0} buổi)
            </button>
            <button className="rounded-lg bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300" type="button" onClick={() => { setShowGenerate(false); setGeneratePreview(null); setGenerateError(''); }}>Đóng</button>
          </div>
          {generateError && <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{generateError}</div>}
          {generatePreview && (
            <div className="rounded-lg border border-gray-200">
              <div className="border-b bg-gray-50 px-4 py-2 text-sm text-gray-700">
                Khoảng: {generatePreview.range_start} - {generatePreview.range_end} · Số buổi dự kiến: <span className="font-semibold">{generatePreview.preview_count}</span>
              </div>
              {generatePreview.preview.length === 0 ? (
                <div className="p-4 text-sm text-gray-500">Không có buổi mới nào được sinh ra (lớp không có schedule ACTIVE trong khoảng đã chọn, hoặc các buổi đã tồn tại).</div>
              ) : (
                <div className="max-h-64 overflow-y-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-gray-500">Buổi</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-gray-500">Ngày</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold uppercase text-gray-500">Giờ</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {generatePreview.preview.map((item, idx) => (
                        <tr key={`${item.date}-${item.start_time}-${idx}`}>
                          <td className="px-3 py-2">#{item.session_number}</td>
                          <td className="px-3 py-2">{item.date}</td>
                          <td className="px-3 py-2">{item.start_time} - {item.end_time}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Lớp</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Buổi</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Ngày giờ</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Nội dung</th>
              {(canUpdateStatus || canCreate) && <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filteredSessions.map((item) => {
              const classItem = classMap[item.class_id];
              return (
                <tr key={item.id}>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    <div className="font-medium text-gray-900">{classItem ? classItem.code : `Class #${item.class_id}`}</div>
                    <div className="text-xs text-gray-500">{item.class || classItem?.subject || '-'}</div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">Buổi {item.session_number || '-'}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{formatDate(item.date)} {item.start_time ? `- ${formatTime(item.start_time)}` : ''}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.status}</td>
                  <td className="px-4 py-3 text-sm text-gray-700">{item.content || '-'}</td>
                  {(canUpdateStatus || canCreate) && (
                    <td className="px-4 py-3 text-sm">
                      {canUpdateStatus && item.status !== 'COMPLETED' && (
                        <button className="mr-3 text-green-600 hover:text-green-800 disabled:opacity-50" disabled={savingId === item.id} onClick={() => handleQuickStatus(item, 'COMPLETED')}>
                          Hoàn thành
                        </button>
                      )}
                      {canUpdateStatus && item.status !== 'STUDENT_ABSENT' && (
                        <button className="mr-3 text-yellow-600 hover:text-yellow-800 disabled:opacity-50" disabled={savingId === item.id} onClick={() => handleQuickStatus(item, 'STUDENT_ABSENT')}>
                          HV vắng
                        </button>
                      )}
                      {canCreate && <button className="text-red-600 hover:text-red-800" onClick={() => handleDelete(item.id)}>Hủy</button>}
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
        {filteredSessions.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có buổi học nào.</div>}
      </div>
    </div>
  );
}
