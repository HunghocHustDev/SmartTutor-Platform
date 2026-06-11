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
    <div>
      <h1 className="text-2xl font-bold mb-4">Danh sách lớp mới tuyển</h1>
      <ClassList onClassClick={handleClassApply} />
    </div>
  );
}