import React, { useEffect, useMemo, useState } from 'react';
import {
  addTutorCapability,
  createTutorAvailability,
  deleteTutorAvailability,
  deleteTutorCapability,
  listSubjects,
  listTutorAvailability,
  listTutorCapabilities,
  listTutors,
  updateTutor,
  updateTutorAvailability,
} from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { DAY_LABELS, formatTime } from '../utils/formatting';

const emptyCapability = {
  subject_id: '',
  teaching_level: '',
  years_experience: '',
  note: '',
};

const emptyAvailability = {
  day_of_week: '1',
  start_time: '19:00',
  end_time: '20:30',
  teaching_mode: 'OFFLINE',
  area: '',
  status: 'AVAILABLE',
};

export default function TutorProfilePage() {
  const { user, login } = useAuth();
  const tutorId = user?.role === 'tutor' ? user.id : null;
  const [profile, setProfile] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [capabilities, setCapabilities] = useState([]);
  const [availability, setAvailability] = useState([]);
  const [basicForm, setBasicForm] = useState({ full_name: '', phone: '', email: '', area: '', experience: '', status: 'ACTIVE' });
  const [capabilityForm, setCapabilityForm] = useState(emptyCapability);
  const [availabilityForm, setAvailabilityForm] = useState(emptyAvailability);
  const [editingAvailabilityId, setEditingAvailabilityId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!tutorId || !user?.email) return;
    let active = true;
    Promise.all([
      listTutors({ email: user.email }),
      listTutorCapabilities(tutorId),
      listTutorAvailability(tutorId),
      listSubjects({ status: 'ACTIVE' }),
    ])
      .then(([tutorData, capabilityData, availabilityData, subjectData]) => {
        if (!active) return;
        const currentTutor = Array.isArray(tutorData) ? tutorData[0] : null;
        setProfile(currentTutor);
        setCapabilities(Array.isArray(capabilityData) ? capabilityData : []);
        setAvailability(Array.isArray(availabilityData) ? availabilityData : []);
        setSubjects(Array.isArray(subjectData) ? subjectData : []);
        if (currentTutor) {
          setBasicForm({
            full_name: currentTutor.full_name || '',
            phone: currentTutor.phone || '',
            email: currentTutor.email || '',
            area: currentTutor.area || '',
            experience: String(currentTutor.experience ?? 0),
            status: currentTutor.status || 'ACTIVE',
          });
        }
      })
      .catch((err) => active && setError(err?.message || 'Không tải được hồ sơ gia sư'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [tutorId, user?.email]);

  const subjectMap = useMemo(() => Object.fromEntries(subjects.map((item) => [item.id, item])), [subjects]);

  const handleBasicSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const updated = await updateTutor(tutorId, {
        full_name: basicForm.full_name,
        phone: basicForm.phone,
        email: basicForm.email,
        area: basicForm.area,
        experience: Number(basicForm.experience || 0),
        status: basicForm.status,
      });
      setProfile(updated);
      login({
        ...user,
        name: updated.full_name,
        email: updated.email,
        area: updated.area,
        experience: updated.experience,
      });
    } catch (err) {
      setError(err?.message || 'Không cập nhật được hồ sơ');
    } finally {
      setSaving(false);
    }
  };

  const handleCapabilitySave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const created = await addTutorCapability(tutorId, {
        subject_id: Number(capabilityForm.subject_id),
        teaching_level: capabilityForm.teaching_level || null,
        years_experience: Number(capabilityForm.years_experience || 0),
        note: capabilityForm.note || null,
      });
      setCapabilities((prev) => {
        const withoutOld = prev.filter((item) => item.subject_id !== created.subject_id || item.teaching_level !== created.teaching_level);
        return [created, ...withoutOld];
      });
      setCapabilityForm(emptyCapability);
    } catch (err) {
      setError(err?.message || 'Không lưu được năng lực dạy');
    } finally {
      setSaving(false);
    }
  };

  const handleCapabilityDelete = async (item) => {
    try {
      await deleteTutorCapability(tutorId, item.capability_id);
      setCapabilities((prev) => prev.filter((cap) => cap.capability_id !== item.capability_id));
    } catch (err) {
      setError(err?.message || 'Không xóa được năng lực dạy');
    }
  };

  const handleAvailabilitySave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        day_of_week: Number(availabilityForm.day_of_week),
        start_time: availabilityForm.start_time,
        end_time: availabilityForm.end_time,
        teaching_mode: availabilityForm.teaching_mode,
        area: availabilityForm.area || null,
        status: availabilityForm.status,
      };
      const saved = editingAvailabilityId
        ? await updateTutorAvailability(tutorId, editingAvailabilityId, payload)
        : await createTutorAvailability(tutorId, payload);
      setAvailability((prev) => {
        if (editingAvailabilityId) {
          return prev.map((item) => (item.id === editingAvailabilityId ? saved : item));
        }
        return [saved, ...prev];
      });
      setAvailabilityForm(emptyAvailability);
      setEditingAvailabilityId(null);
    } catch (err) {
      setError(err?.message || 'Không lưu được lịch rảnh');
    } finally {
      setSaving(false);
    }
  };

  const startAvailabilityEdit = (item) => {
    setEditingAvailabilityId(item.id);
    setAvailabilityForm({
      day_of_week: String(item.day_of_week),
      start_time: formatTime(item.start_time),
      end_time: formatTime(item.end_time),
      teaching_mode: item.teaching_mode,
      area: item.area || '',
      status: item.status,
    });
  };

  const handleAvailabilityDelete = async (item) => {
    try {
      await deleteTutorAvailability(tutorId, item.id);
      setAvailability((prev) => prev.filter((row) => row.id !== item.id));
    } catch (err) {
      setError(err?.message || 'Không xóa được lịch rảnh');
    }
  };

  if (!tutorId) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-600">Trang này chỉ dành cho tài khoản gia sư.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải hồ sơ gia sư...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Hồ sơ gia sư</h1>
        <p className="text-sm text-gray-500">Tự cập nhật hồ sơ, năng lực dạy và lịch rảnh để staff có dữ liệu match lớp.</p>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <form onSubmit={handleBasicSave} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
        <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Họ và tên" value={basicForm.full_name} onChange={(e) => setBasicForm((prev) => ({ ...prev, full_name: e.target.value }))} />
        <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Số điện thoại" value={basicForm.phone} onChange={(e) => setBasicForm((prev) => ({ ...prev, phone: e.target.value }))} />
        <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Email" value={basicForm.email} onChange={(e) => setBasicForm((prev) => ({ ...prev, email: e.target.value }))} />
        <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Khu vực" value={basicForm.area} onChange={(e) => setBasicForm((prev) => ({ ...prev, area: e.target.value }))} />
        <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Kinh nghiệm" value={basicForm.experience} onChange={(e) => setBasicForm((prev) => ({ ...prev, experience: e.target.value }))} />
        <select className="rounded-lg border border-gray-200 px-3 py-2" value={basicForm.status} onChange={(e) => setBasicForm((prev) => ({ ...prev, status: e.target.value }))}>
          <option value="ACTIVE">ACTIVE</option>
          <option value="PAUSED">PAUSED</option>
          <option value="INACTIVE">INACTIVE</option>
        </select>
        <div className="md:col-span-2">
          <button className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700" disabled={saving} type="submit">
            {saving ? 'Đang lưu...' : 'Cập nhật hồ sơ'}
          </button>
        </div>
      </form>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Năng lực dạy</h2>
          <form onSubmit={handleCapabilitySave} className="grid grid-cols-1 gap-3">
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={capabilityForm.subject_id} onChange={(e) => setCapabilityForm((prev) => ({ ...prev, subject_id: e.target.value }))} required>
              <option value="">Chọn môn học</option>
              {subjects.map((item) => (
                <option key={item.id} value={item.id}>{item.name} {item.level ? `- ${item.level}` : ''}</option>
              ))}
            </select>
            <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Trình độ dạy" value={capabilityForm.teaching_level} onChange={(e) => setCapabilityForm((prev) => ({ ...prev, teaching_level: e.target.value }))} />
            <input className="rounded-lg border border-gray-200 px-3 py-2" type="number" placeholder="Số năm kinh nghiệm" value={capabilityForm.years_experience} onChange={(e) => setCapabilityForm((prev) => ({ ...prev, years_experience: e.target.value }))} />
            <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Ghi chú" value={capabilityForm.note} onChange={(e) => setCapabilityForm((prev) => ({ ...prev, note: e.target.value }))} />
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">Lưu năng lực dạy</button>
          </form>
          <div className="space-y-3">
            {capabilities.map((item) => (
              <div key={item.capability_id || `${item.subject_id}-${item.teaching_level}`} className="rounded-lg border border-gray-100 p-4">
                <div className="font-medium text-gray-900">{item.name} {item.level ? `- ${item.level}` : ''}</div>
                <div className="text-sm text-gray-500">Trình độ dạy: {item.teaching_level || '-'}</div>
                <div className="text-sm text-gray-500">Kinh nghiệm: {item.years_experience} năm</div>
                <button className="mt-2 text-sm text-red-600 hover:text-red-800" onClick={() => handleCapabilityDelete(item)}>Xóa năng lực</button>
              </div>
            ))}
            {capabilities.length === 0 && <div className="text-sm text-gray-400">Chưa có capability nào.</div>}
          </div>
        </div>

        <div className="space-y-4 rounded-xl bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Lịch rảnh</h2>
          <form onSubmit={handleAvailabilitySave} className="grid grid-cols-1 gap-3">
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={availabilityForm.day_of_week} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, day_of_week: e.target.value }))}>
              {Object.entries(DAY_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            <div className="grid grid-cols-2 gap-3">
              <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={availabilityForm.start_time} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, start_time: e.target.value }))} />
              <input className="rounded-lg border border-gray-200 px-3 py-2" type="time" value={availabilityForm.end_time} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, end_time: e.target.value }))} />
            </div>
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={availabilityForm.teaching_mode} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, teaching_mode: e.target.value }))}>
              <option value="OFFLINE">OFFLINE</option>
              <option value="ONLINE">ONLINE</option>
              <option value="BOTH">BOTH</option>
            </select>
            <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Khu vực" value={availabilityForm.area} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, area: e.target.value }))} />
            <select className="rounded-lg border border-gray-200 px-3 py-2" value={availabilityForm.status} onChange={(e) => setAvailabilityForm((prev) => ({ ...prev, status: e.target.value }))}>
              <option value="AVAILABLE">AVAILABLE</option>
              <option value="UNAVAILABLE">UNAVAILABLE</option>
            </select>
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">
              {editingAvailabilityId ? 'Cập nhật lịch rảnh' : 'Thêm lịch rảnh'}
            </button>
          </form>
          <div className="space-y-3">
            {availability.map((item) => (
              <div key={item.id} className="rounded-lg border border-gray-100 p-4">
                <div className="font-medium text-gray-900">{DAY_LABELS[item.day_of_week]} - {formatTime(item.start_time)} đến {formatTime(item.end_time)}</div>
                <div className="text-sm text-gray-500">{item.teaching_mode} - {item.area || 'Không giới hạn khu vực'}</div>
                <div className="text-sm text-gray-500">{item.status}</div>
                <div className="mt-2 flex gap-3 text-sm">
                  <button className="text-blue-600 hover:text-blue-800" onClick={() => startAvailabilityEdit(item)}>Sửa</button>
                  <button className="text-red-600 hover:text-red-800" onClick={() => handleAvailabilityDelete(item)}>Xóa</button>
                </div>
              </div>
            ))}
            {availability.length === 0 && <div className="text-sm text-gray-400">Chưa có lịch rảnh nào.</div>}
          </div>

          <WeeklyAvailabilityGrid availability={availability} />
        </div>
      </div>
    </div>
  );
}

function WeeklyAvailabilityGrid({ availability }) {
  const grouped = useMemo(() => {
    const slots = Array.from({ length: 7 }, () => []);
    for (const item of availability) {
      const day = Number(item.day_of_week);
      if (slots[day - 1]) {
        slots[day - 1].push(item);
      }
    }
    return slots.map((items) => items.sort((a, b) => (a.start_time || '').localeCompare(b.start_time || '')));
  }, [availability]);

  return (
    <div className="rounded-lg border border-gray-200">
      <div className="grid grid-cols-7 border-b bg-gray-50 text-xs font-semibold uppercase text-gray-500">
        {Object.entries(DAY_LABELS).map(([value, label]) => (
          <div key={value} className="border-r px-2 py-2 text-center last:border-r-0">{label}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 min-h-[120px]">
        {grouped.map((items, idx) => (
          <div key={idx} className="space-y-1 border-r px-2 py-2 last:border-r-0">
            {items.length === 0 && <div className="text-xs italic text-gray-300">--</div>}
            {items.map((item) => (
              <div
                key={item.id}
                className={`rounded px-1.5 py-1 text-xs ${item.status === 'AVAILABLE' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-500 line-through'}`}
                title={`${item.teaching_mode}${item.area ? ' - ' + item.area : ''}`}
              >
                <div className="font-medium">{formatTime(item.start_time)} - {formatTime(item.end_time)}</div>
                <div className="truncate text-[10px]">{item.teaching_mode}</div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
