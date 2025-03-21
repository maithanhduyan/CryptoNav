import React from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export const AppHeader: React.FC = () => {
  const { user, signOut } = useAuth(); // Lấy user và hàm signOut từ AuthContext
  const navigate = useNavigate(); // Hook để điều hướng

  // Hàm xử lý đăng xuất
  const handleLogout = () => {
    signOut(); // Xóa user và token khỏi AuthContext
    navigate("/signin"); // Chuyển hướng về trang đăng nhập
  };

  return (
    <header className="w-full h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4">
      {/* Tiêu đề bên trái */}
      <div className="text-xl font-semibold text-gray-800">
        CryptoNav
      </div>

      {/* Thanh công cụ bên phải */}
      <div className="flex items-center space-x-4">
        {/* Hiển thị tên người dùng nếu đã đăng nhập */}
        {user && (
          <span className="text-gray-700">
            Xin chào, {user.username || "User"}
          </span>
        )}

        {/* Nút đăng xuất */}
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-3 py-1 rounded-md hover:bg-red-600 transition-colors"
        >
          Sign Out
        </button>
      </div>
    </header>
  );
};

export default AppHeader;