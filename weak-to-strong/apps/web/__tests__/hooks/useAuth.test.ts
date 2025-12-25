/**
 * @jest-environment jsdom
 */
import { renderHook, act, waitFor } from "@testing-library/react";
import { useAuth } from "@/hooks/useAuth";

// Mock next-auth
const mockSession = {
  data: null,
  status: "unauthenticated",
};

jest.mock("next-auth/react", () => ({
  useSession: jest.fn(() => mockSession),
  signIn: jest.fn(),
  signOut: jest.fn(),
}));

// Mock the auth client
const mockAuthClient = {
  getCurrentUser: jest.fn(),
  refreshToken: jest.fn(),
  getValidToken: jest.fn(),
};

jest.mock("@/lib/api/auth-client", () => ({
  authClient: mockAuthClient,
}));

describe("useAuth Hook", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSession.data = null;
    mockSession.status = "unauthenticated";
  });

  it("returns unauthenticated state by default", () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBe(null);
    expect(result.current.isLoading).toBe(false);
  });

  it("returns authenticated state when session exists", () => {
    const { useSession } = require("next-auth/react");

    useSession.mockReturnValue({
      data: {
        user: {
          id: "1",
          email: "test@example.com",
          name: "Test User",
        },
        expires: "2024-12-31",
      },
      status: "authenticated",
    });

    const { result } = renderHook(() => useAuth());

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual({
      id: "1",
      email: "test@example.com",
      name: "Test User",
    });
  });

  it("returns loading state when session is loading", () => {
    const { useSession } = require("next-auth/react");

    useSession.mockReturnValue({
      data: null,
      status: "loading",
    });

    const { result } = renderHook(() => useAuth());

    expect(result.current.isLoading).toBe(true);
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("fetches additional user profile when authenticated", async () => {
    const { useSession } = require("next-auth/react");

    useSession.mockReturnValue({
      data: {
        user: {
          id: "1",
          email: "test@example.com",
          name: "Test User",
        },
        expires: "2024-12-31",
      },
      status: "authenticated",
    });

    mockAuthClient.getCurrentUser.mockResolvedValue({
      id: "1",
      email: "test@example.com",
      full_name: "Test User",
      tier: "pro",
      subscription_tier: "pro",
    });

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.user?.tier).toBe("pro");
    });

    expect(mockAuthClient.getCurrentUser).toHaveBeenCalled();
  });

  it("handles sign in", async () => {
    const { signIn } = require("next-auth/react");
    signIn.mockResolvedValue({ ok: true });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.signIn("test@example.com", "password");
    });

    expect(signIn).toHaveBeenCalledWith("credentials", {
      email: "test@example.com",
      password: "password",
      redirect: false,
    });
  });

  it("handles sign out", async () => {
    const { signOut } = require("next-auth/react");
    signOut.mockResolvedValue({ url: "http://localhost:3000/auth/signin" });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.signOut();
    });

    expect(signOut).toHaveBeenCalledWith({ redirect: false });
  });

  it("refreshes user profile", async () => {
    mockAuthClient.getCurrentUser.mockResolvedValue({
      id: "1",
      email: "test@example.com",
      full_name: "Updated User",
      tier: "pro",
    });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.refreshUser();
    });

    expect(mockAuthClient.getCurrentUser).toHaveBeenCalled();
    expect(result.current.user?.full_name).toBe("Updated User");
  });

  it("handles API errors gracefully", async () => {
    const { useSession } = require("next-auth/react");

    useSession.mockReturnValue({
      data: {
        user: { id: "1", email: "test@example.com" },
        expires: "2024-12-31",
      },
      status: "authenticated",
    });

    mockAuthClient.getCurrentUser.mockRejectedValue(new Error("API Error"));

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.user).toBeTruthy(); // Should still have basic session data
    });

    // Should not crash and should handle error gracefully
    expect(result.current.user?.email).toBe("test@example.com");
  });

  it("automatically refreshes token when needed", async () => {
    const { useSession } = require("next-auth/react");

    useSession.mockReturnValue({
      data: {
        user: { id: "1", email: "test@example.com" },
        expires: "2024-12-31",
      },
      status: "authenticated",
    });

    mockAuthClient.getValidToken.mockResolvedValue("new-token");

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      const token = await result.current.getValidToken();
      expect(token).toBe("new-token");
    });

    expect(mockAuthClient.getValidToken).toHaveBeenCalled();
  });

  it("updates user subscription tier", async () => {
    mockAuthClient.getCurrentUser
      .mockResolvedValueOnce({
        id: "1",
        email: "test@example.com",
        tier: "free",
        subscription_tier: "free",
      })
      .mockResolvedValueOnce({
        id: "1",
        email: "test@example.com",
        tier: "pro",
        subscription_tier: "pro",
      });

    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.refreshUser();
    });

    expect(result.current.user?.tier).toBe("free");

    await act(async () => {
      await result.current.refreshUser();
    });

    expect(result.current.user?.tier).toBe("pro");
  });
});
