"use client";

import { useState, useEffect, useCallback } from "react";
import {
  authClient,
  type LoginCredentials,
  type RegisterData,
  type UserProfile,
} from "@/lib/api/auth-client";

interface UseAuthReturn {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  clearError: () => void;
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (authClient.isAuthenticated()) {
          const profile = await authClient.getProfile();
          setUser(profile);
        }
      } catch (err) {
        console.error("Failed to initialize auth:", err);
        // Clear invalid tokens
        authClient.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true);
      setError(null);

      await authClient.login(credentials);
      const profile = await authClient.getProfile();
      setUser(profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Register function
  const register = useCallback(async (data: RegisterData) => {
    try {
      setIsLoading(true);
      setError(null);

      await authClient.register(data);
      const profile = await authClient.getProfile();
      setUser(profile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Logout function
  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      await authClient.logout();
    } catch (err) {
      console.error("Logout error:", err);
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  // Refresh profile function
  const refreshProfile = useCallback(async () => {
    try {
      setError(null);
      if (authClient.isAuthenticated()) {
        const profile = await authClient.getProfile();
        setUser(profile);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to refresh profile"
      );
      console.error("Failed to refresh profile:", err);
    }
  }, []);

  // Clear error function
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    user,
    isAuthenticated: user !== null,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshProfile,
    clearError,
  };
}
