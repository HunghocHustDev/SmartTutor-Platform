import React, { useEffect, useMemo, useState } from 'react';
import {
  cancelAssignment,
  createAssignment,
  getSuggestedTutors,
  listAssignments,
  listLearningRequests,
  listTutors,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { formatDateTime, formatDate } from '../utils/formatting';

const DAY_OPTIONS = [
  { value: 1, label: 'T2' },
  { value: 2, label: 'T3' },
  { value: 3, label: 'T4' },
  { value: 4, label: 'T5' },
  { value: 5, label: 'T6' },
  { value: 6, label: 'T7' },
  { value: 7, label: 'CN' },
];

const MODE_LABELS = { ONLINE: 'Online', OFFLINE: 'Offline', BOTH: 'Cả hai' };
const STATUS_CONFIG = {
  PENDING: { label: 'Chờ phân công', color: 'bg-yellow-100 text-yellow-700' },
  ASSIGNED: { label: 'Đã phân công', color: 'bg-green-100 text-green-700' },
  CANCELED: { label: 'Đã hủy', color: 'bg-red-100 text-red-700' },
};

const STATUS_BAR_CONFIG = {
  PENDING: { label: 'Chờ phân công', bg: 'bg-yellow-50 border-yellow-200 text-yellow-700' },
  ASSIGNED: { label: 'Đã phân công', bg: 'bg-green-50 border-green-200 text-green-700' },
  CANCELED: { label: 'Đã hủy', bg: 'bg-red-50 border-red-200 text-red-700' },
};

function AvailabilityBadge({ availability }) {
  if (!availability || !availability.length) return null;
  const modes = { ONLINE: 'bg-blue-100 text-blue-700', OFFLINE: 'bg-green-100 text-green-700', BOTH: 'bg-purple-100 text-purple-700' };
  return (
    <div className="flex flex-wrap gap-1 mt-1">
      {availability.map((a, i) => (
        <span key={i} className={`text-xs px-1.5 py-0.5 rounded ${modes[a.teaching_mode] || 'bg-gray-100 text-gray-600'}`}>
          {a.day_label} {a.start_time}-{a.end_time}
        </span>
      ))}
    </div>
  );
}

export default function AssignmentsPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'staff';

  const [assignments, setAssignments] = useState([]);
  const [requests, setRequests] = useState([]);
  const [tutors, setTutors] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Panel state
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [rightTab, setRightTab] = useState('assign'); // 'assign' | 'history'

  // Filters
  const [filterSubject, setFilterSubject] = useState('');
  const [filterArea, setFilterArea] = useState('');
  const [filterMinExp, setFilterMinExp] = useState('');
  const [filterDays, setFilterDays] = useState([]);
  const [filterMode, setFilterMode] = useState('');
  const [filterSearch, setFilterSearch] = useState('');

  // Assignment form
  const [selectedTutorId, setSelectedTutorId] = useState(null);
  const [assignNote, setAssignNote] = useState('');
  const [saving, setSaving] = useState(false);

  // Suggestion state
  const [suggestResult, setSuggestResult] = useState({ status: 'idle', suggestions: [], error: null });

  useEffect(() => {
    if (!canManage) return;
    let active = true;
    setLoading(true);
    Promise.all([listAssignments(), listLearningRequests(), listTutors({ status: 'ACTIVE' })])
      .then(([aData, rData, tData]) => {
        if (!active) return;
        setAssignments(Array.isArray(aData) ? aData : []);
        setRequests(Array.isArray(rData) ? rData : []);
        setTutors(Array.isArray(tData) ? tData : []);
      })
      .catch((err) => active && setError(err?.message || 'Không tải được dữ liệu'))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [canManage]);

  const requestMap = useMemo(() => Object.fromEntries(requests.map((r) => [r.id, r])), [requests]);
  const tutorMap = useMemo(() => Object.fromEntries(tutors.map((t) => [t.id, t])), [tutors]);

  const pendingRequests = useMemo(
    () => requests.filter((r) => r.status === 'PENDING'),
    [requests]
  );

  const selectedRequest = selectedRequestId ? requestMap[selectedRequestId] : null;

  const assignmentHistory = useMemo(() => {
    if (!selectedRequestId) return [];
    return assignments.filter((a) => a.request_id === selectedRequestId);
  }, [assignments, selectedRequestId]);

  const hasActiveAssignment = useMemo(() => {
    if (!selectedRequestId) return false;
    return assignments.some((a) => a.request_id === selectedRequestId && a.status === 'ASSIGNED');
  }, [assignments, selectedRequestId]);

  const handleDayToggle = (val) => {
    setFilterDays((prev) => prev.includes(val) ? prev.filter((d) => d !== val) : [...prev, val]);
  };

  const handleSuggest = async () => {
    if (!selectedRequestId) return;
    setSuggestResult((prev) => ({ ...prev, status: 'loading', error: null }));
    setRightTab('assign');
    try {
      const data = await getSuggestedTutors(selectedRequestId);
      setSuggestResult({
        status: 'ok',
        suggestions: data.suggestions || [],
        error: null,
      });
      if (data.suggestions?.length > 0) {
        setSelectedTutorId(data.suggestions[0].tutor_id);
      } else {
        setSelectedTutorId(null);
      }
    } catch (err) {
      setSuggestResult({
        status: 'error',
        suggestions: [],
        error: err?.message || 'Lỗi gợi ý gia sư',
      });
      setSelectedTutorId(null);
    }
  };

  const handleAssign = async () => {
    if (!selectedRequestId || !selectedTutorId) return;
    setSaving(true);
    setError('');
    try {
      const created = await createAssignment({
        request_id: Number(selectedRequestId),
        tutor_id: Number(selectedTutorId),
        staff_id: user.id,
        note: assignNote || null,
      });
      setAssignments((prev) => [created, ...prev]);
      setRequests((prev) => prev.map((r) => r.id === selectedRequestId ? { ...r, status: 'ASSIGNED' } : r));
      setSelectedTutorId(null);
      setAssignNote('');
      setSuggestedTutors([]);
      setShowSuggest(false);
      setRightTab('history');
    } catch (err) {
      setError(err?.message || 'Không tạo được phân công');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = async (assignmentId) => {
    if (!window.confirm('Bạn có muốn hủy phân công này không?')) return;
    let assignment = null;
    try {
      assignment = assignments.find((a) => a.id === assignmentId);
    } catch (_) {
      assignment = null;
    }
    try {
      await cancelAssignment(assignmentId);
      setAssignments((prev) => prev.map((a) => a.id === assignmentId ? { ...a, status: 'CANCELED' } : a));
      setRequests((prev) => prev.map((r) => r.id === assignment?.request_id ? { ...r, status: 'PENDING' } : r));
    } catch (err) {
      setError(err?.message || 'Không hủy được');
    }
  };

  if (!canManage) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-600">Chỉ nhân viên mới được phân công gia sư.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow text-center text-gray-500">Đang tải dữ liệu phân công...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Phân công gia sư</h1>
          <p className="text-sm text-gray-500 mt-1">Chọn yêu cầu → Lọc và chọn gia sư phù hợp → Phân công.</p>
        </div>
        <div className="flex gap-3 text-sm">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-yellow-400 inline-block" />
            <span className="text-gray-600">{pendingRequests.length} chờ</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full bg-green-400 inline-block" />
            <span className="text-gray-600">{assignments.filter((a) => a.status === 'ASSIGNED').length} đã phân công</span>
          </div>
        </div>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4" style={{ minHeight: '70vh' }}>
        {/* === LEFT: Request list === */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
            <h2 className="font-semibold text-gray-800 text-sm">Yêu cầu chờ phân công</h2>
            <p className="text-xs text-gray-400 mt-0.5">{pendingRequests.length} yêu cầu</p>
          </div>
          <div className="flex-1 overflow-y-auto divide-y divide-gray-50">
            {pendingRequests.length === 0 ? (
              <div className="p-6 text-center text-sm text-gray-400">Không có yêu cầu nào chờ phân công.</div>
            ) : (
              pendingRequests.map((req) => (
                <button
                  key={req.id}
                  onClick={() => {
                    setSelectedRequestId(req.id);
                    setSelectedTutorId(null);
                    setAssignNote('');
                    setSuggestResult({ status: 'idle', suggestions: [], error: null });
                    setRightTab('assign');
                  }}
                  className={`w-full text-left px-4 py-3 transition-all ${
                    selectedRequestId === req.id
                      ? 'bg-blue-50 border-l-4 border-blue-600'
                      : 'hover:bg-gray-50 border-l-4 border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-400">#{req.id}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_BAR_CONFIG[req.status]?.bg} ${STATUS_BAR_CONFIG[req.status]?.label ? '' : ''}`}>
                      {STATUS_CONFIG[req.status]?.label || req.status}
                    </span>
                  </div>
                  <div className="text-sm font-medium text-gray-900">{req.student || `Học sinh #${req.student_id}`}</div>
                  <div className="text-xs text-gray-600 mt-0.5">{req.subject || `Môn #${req.subject_id}`}</div>
                  {req.area && <div className="text-xs text-gray-400 mt-0.5">📍 {req.area}</div>}
                  {(req.preferred_schedule_display || req.preferred_schedule) && (
                    <div className="text-xs text-blue-600 mt-0.5 font-mono bg-blue-50 inline-block px-1.5 py-0.5 rounded">
                      {req.preferred_schedule_display || req.preferred_schedule}
                    </div>
                  )}
                  <div className="text-xs text-gray-400 mt-1">
                    {req.teaching_mode ? MODE_LABELS[req.teaching_mode] || req.teaching_mode : 'Offline'}
                    {req.expected_fee ? ` · ${Number(req.expected_fee).toLocaleString()}đ/buổi` : ''}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* === RIGHT: Assignment panel === */}
        <div className="lg:col-span-3 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
          {!selectedRequest ? (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400 p-8">
              <svg className="w-16 h-16 mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
              </svg>
              <p className="text-center text-sm">Chọn một yêu cầu bên trái<br />để bắt đầu phân công gia sư.</p>
            </div>
          ) : hasActiveAssignment ? (
            <div className="flex-1 flex flex-col">
              {/* Request summary header */}
              <div className="px-5 py-4 border-b border-gray-100 bg-gray-50">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h2 className="font-semibold text-gray-900">
                      {selectedRequest.student || `Học sinh #${selectedRequest.student_id}`}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {selectedRequest.subject} · {selectedRequest.area || 'Không rõ khu vực'}
                    </p>
                  </div>
                  <span className={`text-sm px-3 py-1 rounded-full font-medium ${STATUS_BAR_CONFIG.ASSIGNED?.bg}`}>
                    Đã phân công
                  </span>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                <button onClick={() => setRightTab('assign')} className={`px-5 py-2.5 text-sm font-medium border-b-2 transition-colors ${rightTab === 'assign' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                  Phân công mới
                </button>
                <button onClick={() => setRightTab('history')} className={`px-5 py-2.5 text-sm font-medium border-b-2 transition-colors ${rightTab === 'history' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}>
                  Lịch sử phân công ({assignmentHistory.length})
                </button>
              </div>

              <div className="flex-1 overflow-y-auto">
                {rightTab === 'history' ? (
                  <div className="p-4">
                    {assignmentHistory.length === 0 ? (
                      <p className="text-center text-sm text-gray-400 py-8">Chưa có phân công nào.</p>
                    ) : (
                      <div className="space-y-3">
                        {assignmentHistory.map((a) => {
                          const t = tutorMap[a.tutor_id];
                          return (
                            <div key={a.id} className={`rounded-lg border p-4 ${a.status === 'ASSIGNED' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white'}`}>
                              <div className="flex items-start justify-between">
                                <div>
                                  <div className="font-medium text-sm text-gray-900">{t?.full_name || `Gia sư #${a.tutor_id}`}</div>
                                  <div className="text-xs text-gray-500 mt-0.5">
                                    Ngày: {formatDateTime(a.assigned_at)}
                                    {a.note && <span className="ml-2 text-gray-400">· {a.note}</span>}
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${a.status === 'ASSIGNED' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                    {a.status}
                                  </span>
                                  {a.status === 'ASSIGNED' && (
                                    <button onClick={() => handleCancel(a.id)} className="text-xs text-red-600 hover:text-red-800 hover:underline">
                                      Hủy
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-4 text-center text-sm text-gray-500">
                    <p>Yêu cầu này đã được phân công. Chuyển sang tab "Lịch sử" để xem hoặc hủy phân công hiện tại.</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Request summary header */}
              <div className="px-5 py-4 border-b border-gray-100 bg-blue-50">
                <div className="flex items-start justify-between mb-1">
                  <div>
                    <h2 className="font-semibold text-gray-900 text-base">
                      {selectedRequest.student || `Học sinh #${selectedRequest.student_id}`}
                    </h2>
                    <p className="text-sm text-gray-600">{selectedRequest.subject}</p>
                  </div>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 font-medium">
                    Chờ phân công
                  </span>
                </div>
                <div className="flex flex-wrap gap-2 mt-2 text-xs">
                  {selectedRequest.area && (
                    <span className="bg-white border border-gray-200 text-gray-600 px-2 py-1 rounded">
                      📍 {selectedRequest.area}
                    </span>
                  )}
                  <span className="bg-white border border-gray-200 text-gray-600 px-2 py-1 rounded">
                    {MODE_LABELS[selectedRequest.teaching_mode] || selectedRequest.teaching_mode || 'Offline'}
                  </span>
                  {(selectedRequest.preferred_schedule_display || selectedRequest.preferred_schedule) && (
                    <span className="bg-blue-100 border border-blue-200 text-blue-700 px-2 py-1 rounded font-mono">
                      📅 {selectedRequest.preferred_schedule_display || selectedRequest.preferred_schedule}
                    </span>
                  )}
                  {selectedRequest.expected_fee && (
                    <span className="bg-white border border-gray-200 text-gray-600 px-2 py-1 rounded">
                      {Number(selectedRequest.expected_fee).toLocaleString()}đ/buổi
                    </span>
                  )}
                </div>
              </div>

              {/* Action bar */}
              <div className="px-4 py-3 border-b border-gray-100 flex flex-wrap items-center gap-2">
                <button
                  onClick={handleSuggest}
                  disabled={suggestResult.status === 'loading'}
                  className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 transition"
                >
                  {suggestResult.status === 'loading' ? 'Đang gợi ý...' : '✨ Gợi ý gia sư'}
                </button>
                <span className="text-xs text-gray-400">hoặc lọc thủ công bên dưới</span>
              </div>

              {/* Filters */}
              <div className="px-4 py-3 border-b border-gray-100 bg-gray-50">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Bộ lọc gia sư</p>
                <div className="flex flex-wrap gap-2 mb-2">
                  {DAY_OPTIONS.map((d) => (
                    <label
                      key={d.value}
                      className={`cursor-pointer px-2.5 py-1 rounded text-xs font-medium border transition-colors ${
                        filterDays.includes(d.value)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-600 border-gray-200 hover:border-blue-400'
                      }`}
                    >
                      <input className="sr-only" type="checkbox" checked={filterDays.includes(d.value)} onChange={() => handleDayToggle(d.value)} />
                      {d.label}
                    </label>
                  ))}
                </div>
                <div className="flex flex-wrap gap-2">
                  <input
                    type="text"
                    placeholder="Tìm tên gia sư..."
                    className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm flex-1 min-w-32"
                    value={filterSearch}
                    onChange={(e) => setFilterSearch(e.target.value)}
                  />
                  <input
                    type="text"
                    placeholder="Khu vực"
                    className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-32"
                    value={filterArea}
                    onChange={(e) => setFilterArea(e.target.value)}
                  />
                  <select
                    className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
                    value={filterMinExp}
                    onChange={(e) => setFilterMinExp(e.target.value)}
                  >
                    <option value="">Kinh nghiệm</option>
                    <option value="0">Tất cả</option>
                    <option value="1">≥ 1 năm</option>
                    <option value="2">≥ 2 năm</option>
                    <option value="3">≥ 3 năm</option>
                  </select>
                  <select
                    className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
                    value={filterMode}
                    onChange={(e) => setFilterMode(e.target.value)}
                  >
                    <option value="">Hình thức</option>
                    <option value="OFFLINE">Offline</option>
                    <option value="ONLINE">Online</option>
                  </select>
                </div>
              </div>

              {/* Tutor list */}
              <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {suggestResult.status === 'loading' ? (
                  <div className="text-center text-sm text-gray-400 py-8">Đang tìm gia sư phù hợp...</div>
                ) : suggestResult.suggestions.length > 0 ? (
                  suggestResult.suggestions.map((tutor) => {
                    const isSelected = selectedTutorId === tutor.tutor_id;
                    const scoreColor = tutor.schedule_level >= 3 ? 'text-green-600' : tutor.schedule_level >= 2 ? 'text-blue-600' : tutor.schedule_level === 1 ? 'text-yellow-600' : 'text-gray-400';
                    return (
                      <label
                        key={tutor.tutor_id}
                        className={`block rounded-lg border p-3 cursor-pointer transition-all ${
                          isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <input
                            type="radio"
                            name="tutor_selection"
                            className="mt-1 accent-blue-600"
                            checked={isSelected}
                            onChange={() => setSelectedTutorId(tutor.tutor_id)}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-semibold text-gray-900 truncate">{tutor.full_name}</span>
                              <span className={`text-xs font-bold ${scoreColor}`}>
                                ★ {tutor.score}
                              </span>
                              {tutor.schedule_level >= 2 && (
                                <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">Lịch phù hợp</span>
                              )}
                            </div>
                            <div className="flex flex-wrap gap-x-3 gap-y-0.5 mt-1 text-xs text-gray-500">
                              <span>🎓 {tutor.experience_years} năm</span>
                              <span>📍 {tutor.area || '—'}</span>
                              <span>📚 {tutor.current_classes}/{tutor.max_classes} lớp</span>
                            </div>
                            {tutor.availability && tutor.availability.length > 0 && (
                              <AvailabilityBadge availability={tutor.availability} />
                            )}
                            {tutor.match_reasons && tutor.match_reasons.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1.5">
                                {tutor.match_reasons.slice(0, 4).map((r, i) => (
                                  <span key={i} className="text-xs bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded">{r}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </label>
                    );
                  })
                ) : (
                  <div className="text-center text-sm text-gray-400 py-8">
                    {suggestResult.status === 'error'
                      ? `Lỗi: ${suggestResult.error}`
                      : suggestResult.status === 'ok'
                        ? 'Không có gia sư gợi ý cho yêu cầu này.'
                        : 'Nhấn "Gợi ý gia sư" để đề xuất, hoặc chọn gia sư từ danh sách.'}
                  </div>
                )}
              </div>

              {/* Assignment form */}
              {selectedRequestId && (
                <div className="border-t border-gray-200 p-4 bg-gray-50">
                  {selectedTutorId ? (
                    <>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-sm font-medium text-gray-700">Đã chọn:</span>
                        <span className="text-sm font-semibold text-gray-900">
                          {tutorMap[selectedTutorId]?.full_name || `Gia sư #${selectedTutorId}`}
                        </span>
                      </div>
                      <textarea
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-3"
                        rows={2}
                        placeholder="Ghi chú phân công (tùy chọn)"
                        value={assignNote}
                        onChange={(e) => setAssignNote(e.target.value)}
                      />
                    </>
                  ) : (
                    <p className="text-sm text-gray-500 mb-3">
                      Chọn một gia sư từ danh sách bên trên hoặc bấm <strong>Gợi ý gia sư</strong> để hệ thống đề xuất phù hợp.
                    </p>
                  )}
                  <div className="flex gap-2">
                    <button
                      className="flex-1 rounded-lg bg-green-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50 transition"
                      onClick={handleAssign}
                      disabled={saving || !selectedTutorId}
                    >
                      {saving ? 'Đang phân công...' : '✅ Phân công gia sư'}
                    </button>
                    {selectedTutorId && (
                      <button
                        className="rounded-lg bg-gray-200 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-300 transition"
                        onClick={() => { setSelectedTutorId(null); setAssignNote(''); }}
                      >
                        Hủy chọn
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
