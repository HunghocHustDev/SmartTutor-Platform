import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function LoginForm({ onClose, switchToRegister }) {
  const { login } = useAuth(); // Gọi hàm login từ Context toàn cục
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // --- LOGIC GIẢ LẬP ĐĂNG NHẬP THỰC TẾ ---
    // Sau này anh kết nối API gọi đến SQL Server ở chỗ này
    if (email && password) {
      let role = "student";
      let name = "Nguyễn Khánh An";

      // Giả lập phân tách vai trò theo ký tự email để anh dễ demo bài tập
      if (email.includes("tutor")) {
        role = "tutor";
        name = "Thầy giáo Ngô Bảo";
      } else if (email.includes("admin")) {
        role = "admin";
        name = "Admin Hệ Thống";
      }

      const userData = {
        name: name,
        role: role,
        token: "mock-jwt-token-from-sql-server",
      };

      login(userData); // Đẩy lên Context toàn cục quản lý
      onClose(); // Đóng modal trạng thái tạm thời
    } else {
      setError("Vui lòng nhập đầy đủ tài khoản và mật khẩu!");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-[1000]">
      <div className="bg-white p-10 rounded-xl w-[400px] shadow-2xl relative text-center motion-safe:animate-fadeIn">
        {/* Nút đóng */}
        <button
          onClick={onClose}
          className="absolute top-2.5 right-[15px] bg-transparent border-none text-2xl cursor-pointer text-gray-400 hover:text-gray-600 transition-colors"
        >
          &times;
        </button>

        <h2 className="text-2xl font-bold mb-5 text-blue-600">
          Đăng Nhập Giao Diện
        </h2>

        {error && (
          <p className="text-red-500 text-sm mb-3 text-left">{error}</p>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            placeholder="Email đăng nhập (chứa 'tutor' để làm gia sư)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-base outline-none focus:border-blue-600 w-full box-border"
            required
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-base outline-none focus:border-blue-600 w-full box-border"
            required
          />
          <button
            type="submit"
            className="p-3 bg-blue-600 text-white border-none rounded-md text-base font-bold cursor-pointer hover:bg-blue-700 transition-colors"
          >
            Đăng Nhập
          </button>
        </form>

        <p className="mt-5 text-sm text-gray-500">
          Chưa có tài khoản?{" "}
          <span
            onClick={switchToRegister}
            className="text-orange-500 cursor-pointer font-bold hover:underline"
          >
            Đăng ký ngay
          </span>
        </p>
      </div>
    </div>
  );
}
