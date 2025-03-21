import { createContext, useState, useContext, useEffect, ReactNode } from "react";
import { loginUsersLoginPost, registerUserUsersRegisterPost } from "../client/sdk.gen";

interface AuthContextType {
  user: { username: string } | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token") || null);

  useEffect(() => {
    if (token) {
      // Tại đây bạn có thể giải mã token hoặc gọi API lấy thông tin user chi tiết
      // setUser({ username: "loaded-from-token" });
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    try {
      // Gọi endpoint đăng nhập sử dụng openapi-ts
      const response = await loginUsersLoginPost({
        query: { username, password },
      });
      // Giả sử API trả về access_token trong response.data
      const { access_token } = response.data as { access_token: string };
      setUser({ username });
      setToken(access_token);
      localStorage.setItem("token", access_token);
    } catch (error) {
      throw new Error("Login failed");
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      // Gọi endpoint đăng ký sử dụng openapi-ts
      await registerUserUsersRegisterPost({
        query: { username, email, password },
      });
      // Sau khi đăng ký thành công, tự động đăng nhập
      // await login(username, password);
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
