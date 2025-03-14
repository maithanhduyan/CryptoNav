# Cấu trúc Dự án như sau:

```
../ui
├── .devcontainer
│   └── devcontainer.json
├── Dockerfile
├── eslint.config.js
├── index.html
├── package-lock.json
├── package.json
├── src
│   ├── App.jsx
│   ├── components
│   │   ├── Header.jsx
│   │   ├── Layout.jsx
│   │   └── Sidebar.jsx
│   ├── context
│   │   └── AuthContext.jsx
│   ├── index.css
│   ├── main.jsx
│   └── pages
│       ├── AuthPages
│       │   ├── SignIn.jsx
│       │   └── SignUp.jsx
│       ├── Dashboard
│       │   └── Home.jsx
│       └── Login.jsx
└── vite.config.js
```

# Danh sách chi tiết các file:

## File ../ui/eslint.config.js:
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
]

```

## File ../ui/vite.config.js:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 3000
  }
})

```

## File ../ui/src/App.jsx:
```
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Layout from "./components/Layout";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";

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
              <Layout>
                <div className="p-6 text-white">
                  <h2 className="text-2xl font-semibold">
                    Welcome to CryptoNav
                  </h2>
                  <p>Your crypto portfolio management dashboard.</p>
                </div>
              </Layout>
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

```

## File ../ui/src/main.jsx:
```
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./context/AuthContext";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
);

```

## File ../ui/src/components/Header.jsx:
```
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

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

## File ../ui/src/components/Layout.jsx:
```
// Layout.jsx
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout({ children }) {
  return (
    <div className="flex flex-col h-screen bg-gray-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}

```

## File ../ui/src/components/Sidebar.jsx:
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

## File ../ui/src/context/AuthContext.jsx:
```
import { createContext, useState, useContext, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);

  useEffect(() => {
    console.log("Token in AuthContext:", token); // Kiểm tra token
    if (token) {
      setUser({ email: "loaded-from-token" });
    }
  }, [token]);

  const signIn = (email, jwtToken) => {
    console.log("Signing in with:", { email, jwtToken }); // Log để kiểm tra
    setUser({ email });
    setToken(jwtToken);
    localStorage.setItem("token", jwtToken);
  };

  const signUp = (email, jwtToken) => {
    setUser({ email });
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

export function useAuth() {
  return useContext(AuthContext);
}

```

## File ../ui/src/pages/Login.jsx:
```

```

## File ../ui/src/pages/AuthPages/SignIn.jsx:
```
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function SignIn() {
  const [username, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8000/api/auth/token",
        {
          username,
          password,
        }
      );
      console.log("Login response:", response.data);

      const { access_token } = response.data;
      signIn(username, access_token);
      localStorage.setItem("token", access_token);
      navigate("/dashboard"); // Chuyển hướng tới dashboard
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid email or password");
      console.error("Login error:", err.response?.data);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-xl p-8 shadow-md w-full max-w-sm">
        <h2 className="text-white text-xl font-bold mb-6 text-center">
          Sign In
        </h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={username}
            onChange={(e) => setEmail(e.target.value)}
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

## File ../ui/src/pages/AuthPages/SignUp.jsx:
```
import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function SignUp() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const { signUp } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    const success = signUp(email, password);
    if (success) {
      navigate("/"); // Chuyển hướng sau khi đăng ký
    } else {
      setError("Sign up failed");
    }
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

## File ../ui/src/pages/Dashboard/Home.jsx:
```
export default function Home() {
  <>
    <div>Home</div>
  </>;
}

```

