Dưới đây là hướng dẫn chi tiết để bạn thực hiện **Task 2: Xử lý xác thực người dùng (Authentication)** một cách đầy đủ:

---

## 🚩 **Bước 1: Hoàn thiện giao diện SignIn và SignUp**

### ✅ **Component `SignIn.tsx`:**

Bạn đã có giao diện mẫu, hãy đảm bảo nó rõ ràng, dễ dùng:

```tsx
// src/pages/AuthPages/SignIn.tsx
import { useState, FormEvent } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { loginUsersLoginPost } from "../../client/sdk.gen";

export default function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { signIn } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const response = await loginUsersLoginPost({
        query: { username, password },
      });

      const token = (response as any).data.access_token;
      signIn(username, token);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid username or password");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-xl p-8 shadow-md w-full max-w-sm">
        <h2 className="text-white text-xl font-bold mb-6 text-center">
          Sign In
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
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
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100"
          />
          {error && <p className="text-red-400">{error}</p>}
          <button className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-500">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

### ✅ **Component `SignUp.tsx`:**

Tương tự SignIn, sử dụng hàm `registerUserUsersRegisterPost` đã được gen từ OpenAPI:

```tsx
// src/pages/AuthPages/SignUp.tsx
import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { registerUserUsersRegisterPost } from "../../client/sdk.gen";

export default function SignUp() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await registerUserUsersRegisterPost({
        query: { username, email, password },
      });

      navigate("/signin");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-xl p-8 shadow-md w-full max-w-sm">
        <h2 className="text-white text-xl font-bold">Create Account</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 rounded-md bg-gray-700 text-gray-100"
          />
          {error && <p className="text-red-400">{error}</p>}
          <button className="w-full bg-green-600 text-white py-2 rounded-md hover:bg-green-500">
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## 🚩 **Bước 2: Quản lý JWT (Token) và trạng thái đăng nhập**

Bạn đã có sẵn context AuthContext. Xác thực lại logic lưu trữ Token:

- Sử dụng localStorage để lưu JWT Token.
- Khi khởi động ứng dụng, kiểm tra token có hợp lệ hay không.

---

## 🚩 **Bước 3: Tích hợp kiểm tra trạng thái xác thực vào routing**

**File `App.tsx`** sửa thành:

```tsx
// src/App.tsx
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import AppLayout from "./layout/AppLayout";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";
import Home from "./pages/Dashboard/Home";

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
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </AppLayout>
            ) : (
              <Navigate to="/signin" replace />
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
```

---

## ✅ **Kiểm thử hoàn thiện:**

- Chạy backend FastAPI đảm bảo các endpoint (`/users/login`, `/users/register`) hoạt động tốt.
- Chạy frontend với `npm run dev` và kiểm thử:

| Case                             | Expectation                                 |
| -------------------------------- | ------------------------------------------- |
| Truy cập `/dashboard` chưa login | Redirect tới `/signin`                      |
| Đăng nhập đúng                   | Redirect tới Dashboard                      |
| Đăng nhập sai                    | Thông báo lỗi                               |
| Đăng ký user mới                 | Chuyển hướng về trang login sau khi đăng ký |

---

**🎯 Hoàn thành 3 bước này** sẽ hoàn thiện Task xác thực người dùng một cách chắc chắn và sẵn sàng cho các tính năng kế tiếp của dự án.
