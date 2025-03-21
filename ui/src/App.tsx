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
import Home from "./pages/Dashboard/Home";
import Asset from "./pages/Asset/Asset";

function App() {
  const { token } = useAuth();
  const { user } = useAuth();
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
                  <Route path="/assets" element={<Asset />} />
                  <Route path="/" element={<Home />} />
                </Routes>
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

