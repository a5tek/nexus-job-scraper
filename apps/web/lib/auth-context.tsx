"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { apiClient, ApiError } from "@/lib/api";

export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (data: { email: string; password: string; name: string }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const userData = await apiClient<User>("/auth/me");
      setUser(userData);
      const storedToken = typeof window !== "undefined" ? localStorage.getItem("nexus_token") : null;
      setToken(storedToken || "session-active");
    } catch (err: unknown) {
      // Only clear user session if unauthorized (401) or forbidden (403)
      // Never aggressively log user out on transient network error or 5xx server issues (SEC-008)
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        if (typeof window !== "undefined") {
          localStorage.removeItem("nexus_token");
        }
        setUser(null);
        setToken(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    const res = await apiClient<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("nexus_token", res.access_token);
    }
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (data: { email: string; password: string; name: string }) => {
    const res = await apiClient<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (typeof window !== "undefined") {
      localStorage.setItem("nexus_token", res.access_token);
    }
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = async () => {
    try {
      await apiClient("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors during logout
    } finally {
      if (typeof window !== "undefined") {
        localStorage.removeItem("nexus_token");
      }
      setToken(null);
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
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
