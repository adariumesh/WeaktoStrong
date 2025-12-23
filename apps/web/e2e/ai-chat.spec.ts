import { test, expect } from "@playwright/test";

test.describe("AI Chat Flow", () => {
  // Helper function to sign in
  const signIn = async (page) => {
    await page.goto("/auth/signin");
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");
    await page.click('[data-testid="signin-button"]');
    await expect(page).toHaveURL("/dashboard");
  };

  test.beforeEach(async ({ page }) => {
    await signIn(page);
  });

  test("user can access AI chat from challenge page", async ({ page }) => {
    // Navigate to a challenge
    await page.goto("/challenges/test-challenge-1");

    // Should see AI chat interface
    await expect(
      page.locator('[data-testid="ai-chat-interface"]')
    ).toBeVisible();
    await expect(page.locator('[data-testid="chat-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="send-button"]')).toBeVisible();
  });

  test("AI chat validates prompts for anti-blind-prompting", async ({
    page,
  }) => {
    await page.goto("/challenges/test-challenge-1");

    // Try to send a lazy prompt
    await page.fill('[data-testid="chat-input"]', "just fix this code");
    await page.click('[data-testid="send-button"]');

    // Should show validation error
    await expect(page.locator('text="explain your approach"')).toBeVisible();

    // Message should not be sent
    await expect(
      page.locator('[data-testid="chat-messages"]')
    ).not.toContainText("just fix this code");
  });

  test("user can send valid prompt and receive AI response", async ({
    page,
  }) => {
    await page.goto("/challenges/test-challenge-1");

    // Send a valid prompt with reasoning
    const validPrompt =
      "I think the approach should be to use a for loop because it allows me to iterate through each element efficiently";

    await page.fill('[data-testid="chat-input"]', validPrompt);
    await page.click('[data-testid="send-button"]');

    // Should see user message in chat
    await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
      validPrompt
    );

    // Should see loading indicator
    await expect(page.locator('[data-testid="ai-thinking"]')).toBeVisible();

    // Should eventually receive AI response
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({
      timeout: 10000,
    });

    // Input should be cleared
    await expect(page.locator('[data-testid="chat-input"]')).toHaveValue("");
  });

  test("user can see different AI model tiers", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Should show current tier indicator
    await expect(
      page.locator('[data-testid="model-tier-indicator"]')
    ).toBeVisible();
    await expect(page.locator('text="Local AI"')).toBeVisible();

    // Click to see tier progression
    await page.click('[data-testid="model-tier-indicator"]');

    // Should show tier information
    await expect(page.locator('text="Claude Haiku"')).toBeVisible();
    await expect(page.locator('text="Complete 10 challenges"')).toBeVisible();
  });

  test("user can view token usage", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Should see token usage display
    await expect(page.locator('[data-testid="token-usage"]')).toBeVisible();

    // Send a message to consume tokens
    await page.fill(
      '[data-testid="chat-input"]',
      "I think the approach should be to use recursion because it simplifies the problem"
    );
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({
      timeout: 10000,
    });

    // Token usage should update
    await expect(page.locator('[data-testid="token-usage"]')).toContainText(
      "tokens"
    );
  });

  test("user can generate smart hints", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Click hints button
    await page.click('[data-testid="generate-hints-button"]');

    // Should see loading state
    await expect(page.locator('text="Generating"')).toBeVisible();

    // Should show hints
    await expect(page.locator('[data-testid="hint-item"]')).toBeVisible({
      timeout: 10000,
    });

    // Should see hint categories
    await expect(page.locator('[data-testid="hint-priority"]')).toBeVisible();
  });

  test("user can view learning path insights", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Should see learning path component
    await expect(page.locator('[data-testid="learning-path"]')).toBeVisible();

    // Should show difficulty assessment
    await expect(
      page.locator('[data-testid="difficulty-assessment"]')
    ).toBeVisible();

    // Should show track information
    await expect(page.locator('[data-testid="current-track"]')).toBeVisible();
  });

  test("chat interface handles errors gracefully", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Mock network error by intercepting API calls
    await page.route("**/api/v1/ai/chat", (route) => {
      route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Internal server error" }),
      });
    });

    // Send a message
    await page.fill(
      '[data-testid="chat-input"]',
      "I think the approach should be to use a function because it organizes the code better"
    );
    await page.click('[data-testid="send-button"]');

    // Should show error message
    await expect(page.locator('text="Error"')).toBeVisible();
    await expect(page.locator('text="try again"')).toBeVisible();
  });

  test("chat interface respects character limits", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Type very long message
    const longMessage = "I think the approach should be ".repeat(100); // Very long text
    await page.fill('[data-testid="chat-input"]', longMessage);

    // Should show character limit warning
    await expect(page.locator('text="character limit"')).toBeVisible();

    // Send button should be disabled
    await expect(page.locator('[data-testid="send-button"]')).toBeDisabled();
  });

  test("chat messages persist during session", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Send a message
    const message1 =
      "I think the approach should be to use an array because it stores multiple values";
    await page.fill('[data-testid="chat-input"]', message1);
    await page.click('[data-testid="send-button"]');

    // Wait for response
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({
      timeout: 10000,
    });

    // Send another message
    const message2 =
      "My strategy is to iterate through the array because I need to check each element";
    await page.fill('[data-testid="chat-input"]', message2);
    await page.click('[data-testid="send-button"]');

    // Both messages should be visible
    await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
      message1
    );
    await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
      message2
    );

    // Refresh page
    await page.reload();

    // Messages should persist
    await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
      message1
    );
    await expect(page.locator('[data-testid="chat-messages"]')).toContainText(
      message2
    );
  });

  test("AI chat works with challenge context", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Write some code in the editor first
    await page.fill(
      '[data-testid="code-editor"]',
      "function solve() {\n  // TODO: implement\n}"
    );

    // Send AI message
    await page.fill(
      '[data-testid="chat-input"]',
      "I want to implement this function because I need to solve the challenge"
    );
    await page.click('[data-testid="send-button"]');

    // AI should respond with context-aware answer
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({
      timeout: 10000,
    });

    // Response should reference the code or challenge context
    const response = await page
      .locator('[data-testid="ai-response"]')
      .textContent();
    expect(response).toMatch(/(function|solve|implement|challenge)/i);
  });

  test("streaming responses work correctly", async ({ page }) => {
    await page.goto("/challenges/test-challenge-1");

    // Send message
    await page.fill(
      '[data-testid="chat-input"]',
      "I think the approach should be to use a loop because it handles repetition well"
    );
    await page.click('[data-testid="send-button"]');

    // Should see streaming indicator
    await expect(page.locator('[data-testid="ai-thinking"]')).toBeVisible();

    // Should see response building up (streaming)
    await expect(page.locator('[data-testid="ai-response"]')).toBeVisible({
      timeout: 10000,
    });

    // Final response should be complete
    await expect(page.locator('[data-testid="ai-thinking"]')).not.toBeVisible({
      timeout: 15000,
    });
  });
});
