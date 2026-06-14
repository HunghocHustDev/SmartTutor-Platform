// src/constants/navigation.js

/**
 * Danh sách các mục hiển thị ở Sidebar dành cho Học viên
 * Được đồng bộ chính xác theo luồng định tuyến (Routing) trong App.jsx
 */
export const STUDENT_MENU = [
  { label: "Tạo yêu cầu", path: "/student/requests", icon: "➕" },
  { label: "Lớp của tôi", path: "/student/classes", icon: "📚" },
  { label: "Lịch học", path: "/student/schedule", icon: "📅" },
  { label: "Học phí", path: "/student/tuition", icon: "💵" },
];

/**
 * Danh sách các mục hiển thị ở Sidebar dành cho Gia sư
 * Đã cấu hình đồng bộ chuẩn SPA tràn lề và tích hợp nút Nhật ký & Điểm danh
 */
export const TUTOR_MENU = [
  { label: "Lịch dạy tuần này", path: "/tutor/schedule", icon: "📅" },
  { label: "Lớp học đang dạy", path: "/tutor/classes", icon: "💼" },
  { label: "Nhật ký & Điểm danh", path: "/tutor/reports", icon: "📝" },
];
