import { createContext, useState, useContext, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token") || null);

  useEffect(() => {
    console.log("Token in AuthContext:", token);
    if (token) {
      setUser({ username: "loaded-from-token" }); // Thay email bằng username
    }
  }, [token]);

  const signIn = (username, jwtToken) => {
    console.log("Signing in with:", { username, jwtToken });
    setUser({ username });
    setToken(jwtToken);
    localStorage.setItem("token", jwtToken);
  };

  const signUp = (username, jwtToken) => {
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

export function useAuth() {
  return useContext(AuthContext);
}