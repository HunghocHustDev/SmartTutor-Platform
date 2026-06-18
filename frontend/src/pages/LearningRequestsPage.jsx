import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import {
  createLearningRequest,
  deleteLearningRequest,
  getSuggestedTutors,
  listLearningRequests,
  listSubjects,
  updateLearningRequest,
} from '../services/api';

const DAY_OPTIONS = [
  { value: 1, label: 'T2' },
  { value: 2, label: 'T3' },
  { value: 3, label: 'T4' },
  { value: 4, label: 'T5' },
  { value: 5, label: 'T6' },
  { value: 6, label: 'T7' },
  { value: 7, label: 'CN' },
];

function buildScheduleString(days, startTime, endTime) {
  if (!days.length) return '';
  const dayStr = [...days].sort((a, b) => a - b).map((d) => DAY_OPTIONS.find((o) => o.value === d)?.label || d).join(',');
  if (startTime && endTime) {
    return `${dayStr} ${startTime}-${endTime}`;
  }
  return dayStr;
}

function parseScheduleToForm(raw) {
  if (!raw) return { days: [], startTime: '', endTime: '' };
  const dayMap = { T2: 1, T3: 2, T4: 3, T5: 4, T6: 5, T7: 6, CN: 7 };
  const match = raw.match(/^([A-Z0-9,]+)\s*(\d{2}:\d{2})?-(\d{2}:\d{2})?$/i);
  if (!match) return { days: [], startTime: '', endTime: '' };
  const matched = match[1].split(',').map((d) => dayMap[d?.toUpperCase()?.trim()]).filter(Boolean);
  return { days: matched, startTime: match[2] || '', endTime: match[3] || '' };
}

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
    preferred_days: [],
    preferred_start_time: '',
    preferred_end_time: '',
    preferred_schedule: '',
    expected_fee: '',
  });

  // Tutor suggestion modal state
  const [showSuggestion, setShowSuggestion] = useState(false);
  const [suggestionRequest, setSuggestionRequest] = useState(null);
  const [suggestedTutors, setSuggestedTutors] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [suggestionError, setSuggestionError] = useState('');

  const isStudent = user?.role === 'student';
  const isStaff = user?.role === 'staff';
  const studentIdFilter = isStudent ? user?.id : null;
  const canCreate = isStudent;
  const canEdit = isStudent || isStaff;

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
      preferred_days: [],
      preferred_start_time: '',
      preferred_end_time: '',
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

  const handleDayToggle = (dayValue) => {
    setFormData((prev) => {
      const days = prev.preferred_days.includes(dayValue)
        ? prev.preferred_days.filter((d) => d !== dayValue)
        : [...prev.preferred_days, dayValue];
      return {
        ...prev,
        preferred_days: days,
        preferred_schedule: buildScheduleString(days, prev.preferred_start_time, prev.preferred_end_time),
      };
    });
  };

  const handleTimeChange = (field, value) => {
    setFormData((prev) => {
      const updated = { ...prev, [field]: value };
      updated.preferred_schedule = buildScheduleString(updated.preferred_days, updated.preferred_start_time, updated.preferred_end_time);
      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      const schedule = buildScheduleString(
        formData.preferred_days,
        formData.preferred_start_time,
        formData.preferred_end_time,
      );
      const payload = {
        ...formData,
        student_id: Number(user.id),
        subject_id: Number(formData.subject_id),
        preferred_schedule: schedule || null,
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

  const handleSuggestTutors = async (requestItem) => {
    setSuggestionRequest(requestItem);
    setShowSuggestion(true);
    setLoadingSuggestions(true);
    setSuggestionError('');
    setSuggestedTutors([]);

    try {
      const data = await getSuggestedTutors(requestItem.id);
      setSuggestedTutors(data.suggestions || []);
    } catch (err) {
      setSuggestionError(err?.message || 'Không tải được gợi ý gia sư');
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const startEdit = (item) => {
    const parsed = parseScheduleToForm(item.preferred_schedule);
    setEditingId(item.id);
    setFormData({
      student_id: String(item.student_id || user?.id || ''),
      subject_id: String(item.subject_id || ''),
      target: item.target || item.learning_goal || '',
      requested_level: item.requested_level || '',
      area: item.area || '',
      teaching_mode: item.teaching_mode || 'OFFLINE',
      preferred_days: parsed.days,
      preferred_start_time: parsed.startTime,
      preferred_end_time: parsed.endTime,
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

      {showForm && canEdit && (
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
            <div className="border border-gray-200 p-3 rounded-lg">
              <label className="block text-sm font-medium text-gray-700 mb-2">Ngày học trong tuần</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {DAY_OPTIONS.map((opt) => (
                  <label
                    key={opt.value}
                    className={`cursor-pointer px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                      formData.preferred_days.includes(opt.value)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'bg-white text-gray-600 border-gray-200 hover:border-blue-400'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={formData.preferred_days.includes(opt.value)}
                      onChange={() => handleDayToggle(opt.value)}
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <label className="text-sm text-gray-500">Từ giờ:</label>
                  <input
                    type="time"
                    className="border border-gray-200 rounded px-2 py-1 text-sm"
                    value={formData.preferred_start_time}
                    onChange={(e) => handleTimeChange('preferred_start_time', e.target.value)}
                  />
                </div>
                <div className="flex items-center gap-1">
                  <label className="text-sm text-gray-500">Đến giờ:</label>
                  <input
                    type="time"
                    className="border border-gray-200 rounded px-2 py-1 text-sm"
                    value={formData.preferred_end_time}
                    onChange={(e) => handleTimeChange('preferred_end_time', e.target.value)}
                  />
                </div>
              </div>
              {formData.preferred_schedule && (
                <p className="mt-2 text-xs text-blue-600 font-mono bg-blue-50 px-2 py-1 rounded inline-block">
                  {formData.preferred_schedule}
                </p>
              )}
            </div>
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
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {item.preferred_schedule_display || item.preferred_schedule || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{item.status}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {canEdit && (
                      <button className="text-blue-600 hover:text-blue-800 font-medium mr-3" onClick={() => startEdit(item)}>
                        Sửa
                      </button>
                    )}
                    {isStaff && item.status === 'PENDING' && (
                      <button className="text-green-600 hover:text-green-800 font-medium mr-3" onClick={() => handleSuggestTutors(item)}>
                        Gợi ý gia sư
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

      {/* Tutor Suggestion Modal */}
      {showSuggestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Gợi ý gia sư</h2>
                  <p className="text-sm text-gray-500 mt-1">
                    Request #{suggestionRequest?.id} - {suggestionRequest?.subject}
                  </p>
                </div>
                <button onClick={() => setShowSuggestion(false)} className="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
              </div>
            </div>
            <div className="p-6 overflow-y-auto flex-1">
              {loadingSuggestions ? (
                <div className="flex justify-center items-center py-10">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                  <span className="ml-3 text-gray-600">Đang tải gợi ý...</span>
                </div>
              ) : suggestionError ? (
                <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{suggestionError}</div>
              ) : suggestedTutors.length === 0 ? (
                <div className="text-center py-10 text-gray-400">
                  Không có gia sư phù hợp cho yêu cầu này.
                </div>
              ) : (
                <div className="space-y-4">
                  {suggestedTutors.map((tutor, index) => (
                    <div key={tutor.tutor_id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-sm font-bold">
                              {index + 1}
                            </span>
                            <h3 className="font-semibold text-gray-900">{tutor.full_name}</h3>
                            <span className={`text-sm px-2 py-0.5 rounded font-medium ${
                              tutor.schedule_level >= 3 ? 'bg-green-100 text-green-700' :
                              tutor.schedule_level >= 2 ? 'bg-blue-100 text-blue-700' :
                              tutor.schedule_level === 1 ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              Score: {tutor.score}
                            </span>
                          </div>
                          <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-gray-600">
                            <div>Kinh nghiệm: <span className="font-medium">{tutor.experience_years} năm</span></div>
                            <div>Khu vực: <span className="font-medium">{tutor.area || 'Không rõ'}</span></div>
                            <div>Lớp hiện tại: <span className="font-medium">{tutor.current_classes}/{tutor.max_classes}</span></div>
                            <div>Điện thoại: <span className="font-medium">{tutor.phone || 'Không có'}</span></div>
                          </div>
                          {tutor.availability && tutor.availability.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-500 mb-1 font-medium">Lịch rảnh:</p>
                              <div className="flex flex-wrap gap-1">
                                {tutor.availability.map((a, i) => (
                                  <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                    {a.day_label} {a.start_time}-{a.end_time} {a.teaching_mode !== 'BOTH' ? `(${a.teaching_mode})` : ''}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          {tutor.match_reasons && tutor.match_reasons.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-2">
                              {tutor.match_reasons.map((reason, i) => (
                                <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                                  {reason}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-4 border-t border-gray-100 flex justify-end">
              <button onClick={() => setShowSuggestion(false)} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300">
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
