import { createContext, useState, useContext, useEffect, ReactNode } from "react";
import { loginUsersLoginPost, readCurrentUserUsersMeGet, registerUserUsersRegisterPost } from "../client/sdk.gen";

interface AuthContextType {
  user: { id: number; username: string; email: string } | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<{ id: number; username: string; email: string } | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token") || null);

  useEffect(() => {
    if (token) {
      // Tại đây bạn có thể giải mã token hoặc gọi API lấy thông tin user chi tiết
      // setUser({ username: "loaded-from-token" });
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await readCurrentUserUsersMeGet({
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data as { id: number; username: string; email: string });
    } catch (error) {
      console.error("Failed to fetch user data", error);
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await loginUsersLoginPost({
        query: { username, password },
      });
      const { access_token } = response.data as { access_token: string };
      setToken(access_token);
      localStorage.setItem("token", access_token);
      await fetchUser(); // Lấy thông tin người dùng sau khi đăng nhập
    } catch (error) {
      throw new Error("Login failed");
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      await registerUserUsersRegisterPost({
        body: { username, email, password }, // Truyền qua body
      });
      // Tự động đăng nhập sau khi đăng ký (nếu cần)
      await login(username, password);
    } catch (error) {
      throw new Error("Registration failed");
    }
  };

  const signOut = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
