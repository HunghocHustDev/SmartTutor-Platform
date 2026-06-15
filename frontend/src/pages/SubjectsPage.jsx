import React, { useEffect, useMemo, useState } from 'react';
import { createSubject, deleteSubject, listSubjects, updateSubject } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const emptyForm = {
  name: '',
  level: '',
  subject_group: '',
  description: '',
  status: 'ACTIVE',
};

export default function SubjectsPage() {
  const { user } = useAuth();
  const canManage = user?.role === 'staff';
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [search, setSearch] = useState('');

  useEffect(() => {
    if (!canManage) return;
    let active = true;
    setLoading(true);
    listSubjects()
      .then((data) => active && setSubjects(Array.isArray(data) ? data : []))
      .catch((err) => active && setError(err?.message || 'Không tải được danh sách môn học'))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [canManage]);

  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    if (!term) return subjects;
    return subjects.filter((item) =>
      [item.name, item.level, item.subject_group, item.description]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term))
    );
  }, [subjects, search]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      const payload = {
        ...form,
        level: form.level || null,
        subject_group: form.subject_group || null,
        description: form.description || null,
      };
      if (editingId) {
        const updated = await updateSubject(editingId, payload);
        setSubjects((prev) => prev.map((item) => (item.id === editingId ? updated : item)));
      } else {
        const created = await createSubject(payload);
        setSubjects((prev) => [created, ...prev]);
      }
      setForm(emptyForm);
      setEditingId(null);
      setShowForm(false);
    } catch (err) {
      setError(err?.message || 'Không lưu được môn học');
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      name: item.name || '',
      level: item.level || '',
      subject_group: item.subject_group || '',
      description: item.description || '',
      status: item.status || 'ACTIVE',
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có muốn ngừng hoạt động môn học này không?')) return;
    try {
      await deleteSubject(id);
      setSubjects((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'INACTIVE' } : item)));
    } catch (err) {
      setError(err?.message || 'Không ngừng hoạt động được môn học');
    }
  };

  if (!canManage) {
    return <div className="rounded-lg bg-red-50 p-4 text-red-600">Chỉ nhân viên trung tâm mới quản lý môn học.</div>;
  }

  if (loading) {
    return <div className="rounded-lg bg-white p-6 shadow">Đang tải môn học...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản lý môn học</h1>
          <p className="text-sm text-gray-500">Master data để staff tiếp nhận nhu cầu và match gia sư.</p>
        </div>
        <button
          className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          onClick={() => {
            setShowForm((prev) => !prev);
            if (showForm) {
              setEditingId(null);
              setForm(emptyForm);
            }
          }}
        >
          {showForm ? 'Đóng form' : 'Thêm môn học'}
        </button>
      </div>

      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      <div className="rounded-xl bg-white p-4 shadow-sm">
        <input
          className="w-full rounded-lg border border-gray-200 px-4 py-2"
          placeholder="Tìm theo tên môn, nhóm môn, cấp lớp..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 rounded-xl bg-white p-6 shadow-sm md:grid-cols-2">
          <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Tên môn học *" value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} required />
          <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Cấp lớp" value={form.level} onChange={(e) => setForm((prev) => ({ ...prev, level: e.target.value }))} />
          <input className="rounded-lg border border-gray-200 px-3 py-2" placeholder="Nhóm môn" value={form.subject_group} onChange={(e) => setForm((prev) => ({ ...prev, subject_group: e.target.value }))} />
          <select className="rounded-lg border border-gray-200 px-3 py-2" value={form.status} onChange={(e) => setForm((prev) => ({ ...prev, status: e.target.value }))}>
            <option value="ACTIVE">ACTIVE</option>
            <option value="INACTIVE">INACTIVE</option>
          </select>
          <textarea className="rounded-lg border border-gray-200 px-3 py-2 md:col-span-2" rows={3} placeholder="Mô tả" value={form.description} onChange={(e) => setForm((prev) => ({ ...prev, description: e.target.value }))} />
          <div className="md:col-span-2 flex gap-2">
            <button className="rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-700" disabled={saving} type="submit">
              {saving ? 'Đang lưu...' : editingId ? 'Cập nhật môn học' : 'Tạo môn học'}
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
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Tên môn</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Cấp lớp</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Nhóm môn</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Trạng thái</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((item) => (
              <tr key={item.id}>
                <td className="px-4 py-3">
                  <div className="font-medium text-gray-900">{item.name}</div>
                  <div className="text-sm text-gray-500">{item.description || '-'}</div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-700">{item.level || '-'}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{item.subject_group || '-'}</td>
                <td className="px-4 py-3 text-sm text-gray-700">{item.status}</td>
                <td className="px-4 py-3 text-sm">
                  <button className="mr-3 text-blue-600 hover:text-blue-800" onClick={() => startEdit(item)}>Sửa</button>
                  <button className="text-red-600 hover:text-red-800" onClick={() => handleDelete(item.id)}>Ngừng hoạt động</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <div className="p-6 text-center text-sm text-gray-400">Chưa có môn học nào phù hợp.</div>}
      </div>
    </div>
  );
}
