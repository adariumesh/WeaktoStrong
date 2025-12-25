/**
 * @jest-environment jsdom
 */
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ChatInterface } from "@/components/ai/chat-interface";

// Mock the useAuth hook
jest.mock("@/hooks/useAuth", () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: true,
    user: {
      id: "1",
      email: "test@example.com",
      full_name: "Test User",
    },
  })),
}));

// Mock the AI client
const mockSendMessage = jest.fn();
jest.mock("@/lib/api/ai-client", () => ({
  aiClient: {
    sendMessage: mockSendMessage,
    generateSmartHints: jest.fn(),
    getChallengeContext: jest.fn(),
  },
}));

describe("ChatInterface", () => {
  const defaultProps = {
    challengeId: "test-challenge-1",
    className: "",
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders chat interface", () => {
    render(<ChatInterface {...defaultProps} />);

    expect(
      screen.getByPlaceholderText(/describe your approach/i)
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
    expect(screen.getByText(/ai assistant/i)).toBeInTheDocument();
  });

  it("shows authentication message when not authenticated", () => {
    const { useAuth } = require("@/hooks/useAuth");
    useAuth.mockReturnValue({
      isAuthenticated: false,
      user: null,
    });

    render(<ChatInterface {...defaultProps} />);

    expect(
      screen.getByText(/sign in to access ai assistance/i)
    ).toBeInTheDocument();
  });

  it("validates prompt before sending", async () => {
    const user = userEvent.setup();
    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    // Try to send empty message
    await user.click(sendButton);

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it("validates prompt content for anti-blind-prompting", async () => {
    const user = userEvent.setup();
    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    // Enter lazy prompt
    await user.type(input, "just fix this code");
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/explain your approach/i)).toBeInTheDocument();
    });

    expect(mockSendMessage).not.toHaveBeenCalled();
  });

  it("accepts valid prompt with reasoning", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockResolvedValue({
      content: "Here is my response",
      model_used: "local",
      tokens_used: 50,
    });

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    // Enter valid prompt
    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith({
        prompt:
          "I think the approach should be to use a loop because it handles iteration efficiently",
        challengeId: "test-challenge-1",
        preferred_tier: "local",
        temperature: 0.7,
        max_tokens: 1000,
        enforce_validation: true,
      });
    });
  });

  it("displays AI response in chat", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockResolvedValue({
      content:
        "That's a good approach! Using a loop is indeed efficient for iteration.",
      model_used: "local",
      tokens_used: 50,
    });

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/that's a good approach/i)).toBeInTheDocument();
    });
  });

  it("shows loading state while waiting for response", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockImplementation(() => new Promise(() => {})); // Never resolves

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/thinking/i)).toBeInTheDocument();
    });

    expect(sendButton).toBeDisabled();
  });

  it("handles API errors gracefully", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockRejectedValue(new Error("API Error"));

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/error.*try again/i)).toBeInTheDocument();
    });
  });

  it("clears input after successful send", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockResolvedValue({
      content: "Response",
      model_used: "local",
      tokens_used: 50,
    });

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(input).toHaveValue("");
    });
  });

  it("shows model tier indicator", () => {
    render(<ChatInterface {...defaultProps} />);

    expect(screen.getByText(/local ai/i)).toBeInTheDocument();
  });

  it("allows switching model tiers", async () => {
    const user = userEvent.setup();
    render(<ChatInterface {...defaultProps} />);

    const tierButton = screen.getByText(/local ai/i);
    await user.click(tierButton);

    // Should show tier selection options
    expect(screen.getByText(/claude haiku/i)).toBeInTheDocument();
  });

  it("respects character limit", async () => {
    const user = userEvent.setup();
    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const longText = "a".repeat(1001); // Assuming 1000 char limit

    await user.type(input, longText);

    expect(screen.getByText(/character limit/i)).toBeInTheDocument();
  });

  it("shows token usage information", async () => {
    const user = userEvent.setup();
    mockSendMessage.mockResolvedValue({
      content: "Response",
      model_used: "local",
      tokens_used: 150,
    });

    render(<ChatInterface {...defaultProps} />);

    const input = screen.getByPlaceholderText(/describe your approach/i);
    const sendButton = screen.getByRole("button", { name: /send/i });

    await user.type(
      input,
      "I think the approach should be to use a loop because it handles iteration efficiently"
    );
    await user.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(/150.*tokens/i)).toBeInTheDocument();
    });
  });
});
