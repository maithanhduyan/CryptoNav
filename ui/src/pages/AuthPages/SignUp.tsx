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