import React, { useEffect, useState } from 'react';
import Banner from '../components/Banner';
import { useAuth } from '../contexts/AuthContext';
import { useModal } from '../contexts/ModalContext';
import { getDashboardSummary } from '../services/api';

function ProfileCard({ user }) {
  if (!user || !user.role || user.role === 'staff') {
    return null;
  }

  const isTutor = user.role === 'tutor';
  const rows = isTutor
    ? [
        { label: 'Khu vực', value: user.area },
        { label: 'Trường', value: user.university },
        { label: 'Chuyên ngành', value: user.major },
        { label: 'Kinh nghiệm', value: user.experience !== null && user.experience !== undefined ? `${user.experience} năm` : null },
      ]
    : [
        { label: 'Khu vực', value: user.area },
        { label: 'Trình độ', value: user.level },
        { label: 'Email', value: user.email },
      ];

  return (
    <div className="rounded-2xl bg-white p-5 shadow space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-sm uppercase tracking-wide text-gray-500">
            {isTutor ? 'Hồ sơ gia sư' : 'Thông tin học viên'}
          </div>
          <h2 className="mt-1 text-2xl font-semibold text-gray-900">{user.name}</h2>
          <div className="mt-1 text-sm text-gray-500">{user.email || 'Chưa có email'}</div>
        </div>
        <div className={`rounded-full px-3 py-1 text-xs font-semibold ${isTutor ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
          {isTutor ? 'Gia sư' : 'Học viên'}
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label} className="rounded-xl border border-gray-100 bg-gray-50 px-4 py-3">
            <div className="text-xs uppercase tracking-wide text-gray-500">{row.label}</div>
            <div className="mt-1 text-sm font-medium text-gray-800">{row.value || 'Chưa cập nhật'}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StaffSummary({ summary, loading, error }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-800">Tổng quan hệ thống</h2>
        {loading && <span className="text-sm text-gray-500">Đang tải...</span>}
      </div>
      {error && <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4 xl:grid-cols-7">
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Tổng số học viên</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.total_students ?? 0}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Tổng số gia sư</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.total_tutors ?? 0}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Nhu cầu chờ</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.pending_learning_requests ?? 0}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Lớp đang active</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.active_classes ?? 0}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Buổi hoàn thành</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.completed_sessions ?? 0}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Invoice chưa thu</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{(summary?.unpaid_invoices ?? 0) + (summary?.partially_paid_invoices ?? 0)}</div>
        </div>
        <div className="rounded-lg bg-white p-4 shadow">
          <div className="text-sm text-gray-500">Thanh toán thành công</div>
          <div className="mt-1 text-2xl font-bold text-gray-900">{summary?.successful_payments ?? 0}</div>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { openLogin, openRegister } = useModal();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user || user.role !== 'staff') {
      return;
    }
    let active = true;
    setLoading(true);
    setError('');
    getDashboardSummary()
      .then((data) => {
        if (active) {
          setSummary(data);
        }
      })
      .catch((err) => {
        if (active) {
          setError(err?.message || 'Không tải được thống kê tổng quan');
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
  }, [user]);

  return (
    <div className="space-y-6">
      <Banner onFindTutorClick={openLogin} onBeTutorClick={openRegister} />
      {user && user.role === 'staff' ? (
        <StaffSummary summary={summary} loading={loading} error={error} />
      ) : (
        <ProfileCard user={user} />
      )}
    </div>
  );
}
