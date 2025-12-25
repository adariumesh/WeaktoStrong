/**
 * @jest-environment jsdom
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useRouter } from "next/navigation";
import SignInPage from "@/app/auth/signin/page";

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: jest.fn(),
}));

// Mock next-auth
jest.mock("next-auth/react", () => ({
  signIn: jest.fn(),
  useSession: () => ({
    data: null,
    status: "unauthenticated",
  }),
}));

const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  refresh: jest.fn(),
};

describe("SignIn Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
  });

  it("renders sign in form", () => {
    render(<SignInPage />);

    expect(
      screen.getByRole("heading", { name: /sign in/i })
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /sign in/i })
    ).toBeInTheDocument();
  });

  it("displays validation errors for empty form", async () => {
    const user = userEvent.setup();
    render(<SignInPage />);

    const submitButton = screen.getByRole("button", { name: /sign in/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it("displays validation error for invalid email", async () => {
    const user = userEvent.setup();
    render(<SignInPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    await user.type(emailInput, "invalid-email");
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });
  });

  it("submits form with valid data", async () => {
    const user = userEvent.setup();
    const { signIn } = require("next-auth/react");

    render(<SignInPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    await waitFor(() => {
      expect(signIn).toHaveBeenCalledWith("credentials", {
        email: "test@example.com",
        password: "password123",
        redirect: false,
      });
    });
  });

  it("shows GitHub OAuth button", () => {
    render(<SignInPage />);

    const githubButton = screen.getByText(/continue with github/i);
    expect(githubButton).toBeInTheDocument();
  });

  it("handles GitHub OAuth sign in", async () => {
    const user = userEvent.setup();
    const { signIn } = require("next-auth/react");

    render(<SignInPage />);

    const githubButton = screen.getByText(/continue with github/i);
    await user.click(githubButton);

    expect(signIn).toHaveBeenCalledWith("github");
  });

  it("shows link to sign up page", () => {
    render(<SignInPage />);

    const signUpLink = screen.getByText(/don't have an account/i);
    expect(signUpLink).toBeInTheDocument();
  });

  it("shows loading state during submission", async () => {
    const user = userEvent.setup();
    const { signIn } = require("next-auth/react");

    // Mock signIn to return a pending promise
    signIn.mockImplementation(() => new Promise(() => {}));

    render(<SignInPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  it("shows error message on sign in failure", async () => {
    const user = userEvent.setup();
    const { signIn } = require("next-auth/react");

    // Mock signIn to return error
    signIn.mockResolvedValue({
      error: "CredentialsSignin",
      status: 401,
      ok: false,
    });

    render(<SignInPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "wrongpassword");
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });

  it("redirects to dashboard on successful sign in", async () => {
    const user = userEvent.setup();
    const { signIn } = require("next-auth/react");

    // Mock successful signIn
    signIn.mockResolvedValue({
      error: null,
      status: 200,
      ok: true,
      url: "http://localhost:3000/dashboard",
    });

    render(<SignInPage />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /sign in/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith("/dashboard");
    });
  });
});
