import React, { createContext, useContext, useState } from "react";

// Khởi tạo ngữ cảnh Context toàn cục
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Đọc dữ liệu từ localStorage duy nhất một lần khi khởi tạo ứng dụng
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem("user");
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (error) {
      console.error("Lỗi khi đọc user từ localStorage:", error);
      return null;
    }
  });

  /**
   * Hàm Đăng Nhập Toàn Cục
   * @param {Object} userData - Thông tin user bao gồm { name, role, token, ... }
   */
  const login = (userData) => {
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
  };

  /**
   * Hàm Đăng Xuất Toàn Cục
   * Xóa sạch vết đăng nhập trong bộ nhớ và state
   */
  const logout = () => {
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    // Cung cấp các trạng thái và hàm xử lý nghiệp vụ xuống toàn bộ cây Component
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook giúp gọi Context ngắn gọn, an toàn ở mọi nơi (như Header, Pages, Sidebars)
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth phải được sử dụng bên trong một AuthProvider");
  }
  return context;
};
