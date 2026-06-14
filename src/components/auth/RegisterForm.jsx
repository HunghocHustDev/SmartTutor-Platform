import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function RegisterForm({ onClose, switchToLogin }) {
  const { login } = useAuth(); // Đăng nhập luôn cho user sau khi đăng ký thành công
  const [role, setRole] = useState("student");
  const [phone, setPhone] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    // Giả lập ghi nhận tài khoản đăng ký thành công vào database
    const newUserData = {
      name: fullName || "Thành viên mới",
      role: role,
      token: "mock-jwt-token-after-registration",
    };

    alert(
      `Đăng ký thành công tài khoản ${role === "tutor" ? "Gia sư" : "Học viên"}! Thống tự động đăng nhập.`,
    );

    login(newUserData); // Kích hoạt trạng thái đăng nhập hệ thống ngay lập tức
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex justify-center items-center z-[1000]">
      <div className="bg-white p-10 rounded-xl w-[420px] shadow-2xl relative motion-safe:animate-fadeIn">
        {/* Nút đóng */}
        <button
          onClick={onClose}
          className="absolute top-2.5 right-[15px] bg-transparent border-none text-2xl cursor-pointer text-gray-400 hover:text-gray-600 transition-colors"
        >
          &times;
        </button>

        <h2 className="text-2xl font-bold mb-6 text-orange-500 text-center">
          Đăng Ký Tài Khoản
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
          <input
            type="text"
            placeholder="Họ và tên"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-sm outline-none focus:border-orange-500 w-full box-border"
            required
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-sm outline-none focus:border-orange-500 w-full box-border"
            required
          />

          <input
            type="tel"
            placeholder="Số điện thoại"
            pattern="[0-9]{10}"
            title="Số điện thoại phải gồm 10 chữ số"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-sm outline-none focus:border-orange-500 w-full box-border"
            required
          />

          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="p-3 border border-gray-300 rounded-md text-sm outline-none focus:border-orange-500 w-full box-border"
            required
          />

          {/* Chọn vai trò */}
          <div className="flex items-center gap-4 my-1.5 text-sm">
            <label className="font-semibold text-gray-600 mr-2">Bạn là:</label>

            <label className="flex items-center gap-1.5 cursor-pointer text-gray-700 select-none">
              <input
                type="radio"
                name="role"
                value="student"
                checked={role === "student"}
                onChange={() => setRole("student")}
                className="w-4 h-4 cursor-pointer accent-orange-500"
              />
              Học viên / Phụ huynh
            </label>

            <label className="flex items-center gap-1.5 cursor-pointer text-gray-700 select-none">
              <input
                type="radio"
                name="role"
                value="tutor"
                checked={role === "tutor"}
                onChange={() => setRole("tutor")}
                className="w-4 h-4 cursor-pointer accent-orange-500"
              />
              Gia sư
            </label>
          </div>

          <button
            type="submit"
            className="p-3 bg-orange-500 text-white border-none rounded-md text-base font-bold cursor-pointer hover:bg-orange-600 transition-colors mt-1"
          >
            Đăng Ký
          </button>
        </form>

        <p className="mt-5 text-sm text-gray-500 text-center">
          Đã có tài khoản?{" "}
          <span
            onClick={switchToLogin}
            className="text-blue-600 cursor-pointer font-bold hover:underline"
          >
            Đăng nhập
          </span>
        </p>
      </div>
    </div>
  );
}
