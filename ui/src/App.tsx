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
