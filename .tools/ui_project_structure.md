# Cấu trúc Dự án như sau:

```
.\ui
├── .devcontainer
│   └── devcontainer.json
├── Dockerfile
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── App.tsx
│   ├── components
│   │   ├── Header.tsx
│   │   ├── Layout.tsx
│   │   └── Sidebar.tsx
│   ├── context
│   │   └── AuthContext.tsx
│   ├── index.css
│   ├── layout
│   │   ├── AppHeader.tsx
│   │   ├── AppLayout.tsx
│   │   └── AppSidebar.tsx
│   ├── main.tsx
│   ├── pages
│   │   ├── AuthPages
│   │   │   ├── SignIn.tsx
│   │   │   └── SignUp.tsx
│   │   └── Dashboard
│   │       └── Home.tsx
│   └── vite-env.d.ts
├── tsconfig.app.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

# Danh sách chi tiết các file:

## File .\ui\eslint.config.js:

```javascript
import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  }
);
```

## File .\ui\vite.config.ts:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // host:"0.0.0.0",
    // port:3000
  },
});
```

## File .\ui\src\App.tsx:

```
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router";
import { useAuth } from "./context/AuthContext";
import AppLayout from "./layout/AppLayout";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";

// Định nghĩa kiểu cho props của Layout (nếu cần trong tương lai)
interface LayoutProps {
  children: React.ReactNode;
}

function App() {
  const { token } = useAuth();

  return (
    <Router>
      <Routes>
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route
          path="/*"
          element={
            token ? (
              <AppLayout>
                <div className="p-6 text-white">
                  <h2 className="text-2xl font-semibold">
                    Welcome to CryptoNav
                  </h2>
                  <p>Your crypto portfolio management dashboard.</p>
                </div>
              </AppLayout>
            ) : (
              <Navigate to="/signin" />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

// Import các component SignIn và SignUp (giả định chúng đã được chuyển sang .tsx)

```

## File .\ui\src\main.tsx:

```
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from "./context/AuthContext.tsx";
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)

```

## File .\ui\src\vite-env.d.ts:

```typescript
/// <reference types="vite/client" />
```

## File .\ui\src\components\Header.tsx:

```

```

## File .\ui\src\components\Layout.tsx:

```

```

## File .\ui\src\components\Sidebar.tsx:

```
export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800">
      <nav className="mt-4">
        <ul>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Dashboard
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Portfolio
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Transactions
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              AI Analytics
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Settings
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
```

## File .\ui\src\context\AuthContext.tsx:

```
import { createContext, useState, useContext, useEffect, ReactNode } from "react";

interface AuthContextType {
  user: { username: string } | null;
  token: string | null;
  signIn: (username: string, jwtToken: string) => void;
  signUp: (username: string, jwtToken: string) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("token") || null);

  useEffect(() => {
    if (token) {
      setUser({ username: "loaded-from-token" });
    }
  }, [token]);

  const signIn = (username: string, jwtToken: string) => {
    setUser({ username });
    setToken(jwtToken);
    localStorage.setItem("token", jwtToken);
  };

  const signUp = (username: string, jwtToken: string) => {
    setUser({ username });
    setToken(jwtToken);
    localStorage.setItem("token", jwtToken);
  };

  const signOut = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider value={{ user, token, signIn, signUp, signOut }}>
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
```

## File .\ui\src\layout\AppHeader.tsx:

```
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router";

export default function Header() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleSignOut = () => {
    signOut();
    navigate("/signin");
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex items-center justify-between">
      <h1 className="text-white text-xl font-semibold">CryptoNav</h1>
      <nav>
        <a href="#" className="text-gray-300 hover:text-white px-3">
          Dashboard
        </a>
        <a href="#" className="text-gray-500 hover:text-white ml-4">
          Portfolio
        </a>
        <a href="#" className="text-gray-500 hover:text-white ml-4">
          Settings
        </a>
        {user && (
          <button
            onClick={handleSignOut}
            className="text-gray-500 hover:text-white ml-4"
          >
            Sign Out
          </button>
        )}
      </nav>
    </header>
  );
}
```

## File .\ui\src\layout\AppLayout.tsx:

```
import { ReactNode } from "react";
import AppSidebar from "./AppSidebar";
import AppHeader from "./AppHeader";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col h-screen bg-gray-950">
      <AppHeader />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
```

## File .\ui\src\layout\AppSidebar.tsx:

```
export default function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 border-r border-gray-800">
      <nav className="mt-4">
        <ul>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Dashboard
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Portfolio
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Transactions
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              AI Analytics
            </a>
          </li>
          <li>
            <a
              href="#"
              className="block px-4 py-2 text-gray-300 hover:bg-gray-800"
            >
              Settings
            </a>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
```

## File .\ui\src\pages\AuthPages\SignIn.tsx:

```
import { useState, FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router";
import axios from "axios";

export default function SignIn() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await axios.post(
        "http://localhost:8000/api/auth/token",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      const { access_token } = response.data;
      signIn(username, access_token);
      localStorage.setItem("token", access_token);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid username or password");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-xl p-8 shadow-md w-full max-w-sm">
        <h2 className="text-white text-xl font-bold mb-6 text-center">Sign In</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full p-3 rounded-md bg-gray-700 text-gray-200"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100 mt-4"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full mt-4 bg-blue-600 text-white py-2 rounded-md hover:bg-blue-500"
          >
            Sign In
          </button>
          <p className="mt-4 text-center text-gray-400">
            Don't have an account?{" "}
            <a href="/signup" className="text-blue-400 hover:underline">
              Sign Up
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
```

## File .\ui\src\pages\AuthPages\SignUp.tsx:

```
import { useState, FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router";

export default function SignUp() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    // Gọi hàm signUp từ AuthContext (giả định trả về void hoặc boolean)
    signUp(email, password); // Trong thực tế, bạn có thể cần điều chỉnh logic này nếu signUp trả về Promise hoặc giá trị khác
    navigate("/"); // Chuyển hướng sau khi đăng ký thành công
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-xl p-8 shadow-md w-full max-w-sm">
        <h2 className="text-white text-xl font-bold">Create an Account</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100 mt-4"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100 mt-4"
          />
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100 mt-4"
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            className="w-full mt-4 bg-green-600 text-white py-2 rounded-md hover:bg-green-500"
          >
            Sign Up
          </button>
          <p className="text-gray-400 text-sm text-center mt-4">
            Already have an account?{" "}
            <a href="/signin" className="text-blue-400 hover:underline">
              Sign In
            </a>
          </p>
        </form>
      </div>
    </div>
  );
}
```

## File .\ui\src\pages\Dashboard\Home.tsx:

```
import { useAuth } from "../../context/AuthContext";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="p-6 text-white">
      <h2 className="text-2xl font-semibold mb-4">
        Welcome to CryptoNav, {user?.username || "User"}!
      </h2>
      <p className="text-gray-300 mb-6">
        Your crypto portfolio management dashboard.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Card 1: Portfolio Overview */}
        <div className="bg-gray-800 rounded-lg p-4 shadow-md">
          <h3 className="text-lg font-medium text-white">Portfolio Overview</h3>
          <p className="text-gray-400 mt-2">
            Total Value: <span className="text-green-400">$12,345.67</span>
          </p>
          <p className="text-gray-400">
            24h Change: <span className="text-red-400">-2.5%</span>
          </p>
        </div>
        {/* Card 2: Quick Stats */}
        <div className="bg-gray-800 rounded-lg p-4 shadow-md">
          <h3 className="text-lg font-medium text-white">Quick Stats</h3>
          <p className="text-gray-400 mt-2">Assets: 5</p>
          <p className="text-gray-400">Transactions: 12</p>
        </div>
      </div>
    </div>
  );
}
```
