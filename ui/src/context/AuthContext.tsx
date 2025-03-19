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