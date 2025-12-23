/**
 * Authentication API Client and Token Management
 */

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface UserProfile {
  id: string;
  email: string;
  name: string;
  tier: string;
  tokens_used_today: number;
  is_active: boolean;
  created_at: string;
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class AuthClient {
  private baseUrl = API_BASE;
  private refreshPromise: Promise<string> | null = null;

  /**
   * Get stored auth token
   */
  getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth_token");
  }

  /**
   * Get stored refresh token
   */
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("refresh_token");
  }

  /**
   * Store auth tokens
   */
  setTokens(authResponse: AuthResponse): void {
    if (typeof window === "undefined") return;

    localStorage.setItem("auth_token", authResponse.access_token);
    localStorage.setItem("refresh_token", authResponse.refresh_token);
    localStorage.setItem(
      "token_expires_at",
      (Date.now() + authResponse.expires_in * 1000).toString()
    );
  }

  /**
   * Clear all auth tokens
   */
  clearTokens(): void {
    if (typeof window === "undefined") return;

    localStorage.removeItem("auth_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("token_expires_at");
  }

  /**
   * Check if token is expired or about to expire
   */
  isTokenExpired(): boolean {
    if (typeof window === "undefined") return true;

    const expiresAt = localStorage.getItem("token_expires_at");
    if (!expiresAt) return true;

    // Consider expired if less than 5 minutes remaining
    return Date.now() > parseInt(expiresAt) - 5 * 60 * 1000;
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(): Promise<string> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performTokenRefresh();

    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      this.clearTokens();
      throw new Error("No refresh token available");
    }

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Token refresh failed: ${response.status}`);
      }

      const authResponse: AuthResponse = await response.json();
      this.setTokens(authResponse);

      return authResponse.access_token;
    } catch (error) {
      this.clearTokens();
      throw error;
    }
  }

  /**
   * Get valid auth token, refreshing if necessary
   */
  async getValidToken(): Promise<string | null> {
    const token = this.getToken();

    if (!token) {
      return null;
    }

    if (this.isTokenExpired()) {
      try {
        return await this.refreshAccessToken();
      } catch (error) {
        console.error("Token refresh failed:", error);
        return null;
      }
    }

    return token;
  }

  /**
   * Make authenticated API request with automatic token refresh
   */
  async fetchWithAuth(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<Response> {
    const token = await this.getValidToken();

    if (!token) {
      throw new Error("No valid authentication token");
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });

    // If token expired during request, try once more with refresh
    if (response.status === 401) {
      try {
        const newToken = await this.refreshAccessToken();

        return fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${newToken}`,
            ...options.headers,
          },
        });
      } catch (error) {
        // Refresh failed, clear tokens and re-throw
        this.clearTokens();
        throw error;
      }
    }

    return response;
  }

  /**
   * User registration
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Registration failed");
    }

    const authResponse: AuthResponse = await response.json();
    this.setTokens(authResponse);

    return authResponse;
  }

  /**
   * User login
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Login failed");
    }

    const authResponse: AuthResponse = await response.json();
    this.setTokens(authResponse);

    return authResponse;
  }

  /**
   * User logout
   */
  async logout(): Promise<void> {
    try {
      // Try to logout on server
      await this.fetchWithAuth("/auth/logout", {
        method: "POST",
      });
    } catch (error) {
      // Continue even if server logout fails
      console.warn("Server logout failed:", error);
    } finally {
      // Always clear local tokens
      this.clearTokens();
    }
  }

  /**
   * Get current user profile
   */
  async getProfile(): Promise<UserProfile> {
    const response = await this.fetchWithAuth("/auth/me");

    if (!response.ok) {
      throw new Error(`Failed to get profile: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null && !this.isTokenExpired();
  }
}

// Global auth client instance
export const authClient = new AuthClient();

// Export types
export type { LoginCredentials, RegisterData, AuthResponse, UserProfile };
