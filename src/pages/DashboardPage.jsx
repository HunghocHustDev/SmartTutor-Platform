import React from 'react';
import Banner from '../components/Banner';
import { useAuth } from '../contexts/AuthContext';
import { useModal } from '../contexts/ModalContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const { openLogin, openRegister } = useModal();

  return (
    <div>
      <Banner
        onFindTutorClick={openLogin}
        onBeTutorClick={openRegister}
      />
      {user && user.role === 'admin' && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">Tổng số học viên: 128</div>
          <div className="bg-white p-4 rounded-lg shadow">Tổng số gia sư: 45</div>
          <div className="bg-white p-4 rounded-lg shadow">Nhu cầu chờ: 12</div>
        </div>
      )}
      {/* Có thể thêm các thống kê khác cho từng role */}
    </div>
  );
}