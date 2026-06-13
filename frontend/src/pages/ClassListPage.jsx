// pages/ClassListPage.jsx
import React from 'react';
import ClassList from '../components/ClassList';
import { useModal } from '../contexts/ModalContext';

export default function ClassListPage() {
  const { openLogin } = useModal();

  const handleClassApply = (cls) => {
    alert(`Bạn đang đăng ký nhận lớp ${cls.id} - ${cls.subject}. Vui lòng đăng nhập tài khoản gia sư!`);
    openLogin();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">📋 Danh sách lớp mới tuyển</h1>
        <p className="text-gray-500">
          Các lớp học đang cần gia sư. Đăng ký ngay để nhận lớp phù hợp với bạn.
        </p>
      </div>

      {/* Danh sách lớp (component ClassList đã có card và phân quyền nút đăng ký) */}
      <ClassList onClassClick={handleClassApply} />
    </div>
  );
}