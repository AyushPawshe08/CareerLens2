import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { loginUser, registerUser, getMe } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState(null);
  // Starts true whenever there's a stored token, since we still need to
  // verify it against the backend before we know if the session is real.
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("access_token")));

  useEffect(() => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    getMe()
      .then((data) => {
        if (!cancelled) setUser(data);
      })
      .catch(() => {
        // Token is invalid/expired — client.js's response interceptor
        // already cleared it from localStorage on a 401; mirror that here.
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  const login = useCallback(async (email, password) => {
    const data = await loginUser({ email, password });
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    const data = await registerUser({ email, password, full_name: fullName });
    localStorage.setItem("access_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }, []);

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token),
    loading, // true while verifying a stored token against the backend
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return ctx;
}