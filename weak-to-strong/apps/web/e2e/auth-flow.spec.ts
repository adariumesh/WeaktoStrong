import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test.beforeEach(async ({ page }) => {
    // Reset any existing auth state
    await page.context().clearCookies();
  });

  test("user can sign up with email and password", async ({ page }) => {
    await page.goto("/auth/signup");

    // Fill sign up form
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");
    await page.fill(
      '[data-testid="confirm-password-input"]',
      "SecurePassword123!"
    );
    await page.fill('[data-testid="full-name-input"]', "E2E Test User");

    // Submit form
    await page.click('[data-testid="signup-button"]');

    // Should redirect to dashboard after successful signup
    await expect(page).toHaveURL("/dashboard");

    // Should see welcome message or user name
    await expect(page.locator('text="E2E Test User"')).toBeVisible();
  });

  test("user can sign in with email and password", async ({ page }) => {
    // Assuming user already exists from previous test or setup
    await page.goto("/auth/signin");

    // Fill sign in form
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");

    // Submit form
    await page.click('[data-testid="signin-button"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL("/dashboard");

    // Should see authenticated state
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test("user can sign in with GitHub OAuth", async ({ page }) => {
    await page.goto("/auth/signin");

    // Click GitHub OAuth button
    await page.click('[data-testid="github-signin-button"]');

    // Note: In a real E2E environment, you'd need to handle OAuth flow
    // For now, we just check that it redirects to GitHub
    await page.waitForURL(/github\.com/);

    // In production tests, you'd complete the OAuth flow and verify redirect back
  });

  test("shows validation errors for invalid input", async ({ page }) => {
    await page.goto("/auth/signin");

    // Try to submit empty form
    await page.click('[data-testid="signin-button"]');

    // Should show validation errors
    await expect(page.locator('text="Email is required"')).toBeVisible();
    await expect(page.locator('text="Password is required"')).toBeVisible();

    // Try invalid email format
    await page.fill('[data-testid="email-input"]', "invalid-email");
    await page.click('[data-testid="signin-button"]');

    await expect(page.locator('text="Invalid email address"')).toBeVisible();
  });

  test("shows error for invalid credentials", async ({ page }) => {
    await page.goto("/auth/signin");

    // Fill form with invalid credentials
    await page.fill('[data-testid="email-input"]', "nonexistent@example.com");
    await page.fill('[data-testid="password-input"]', "wrongpassword");

    // Submit form
    await page.click('[data-testid="signin-button"]');

    // Should show error message
    await expect(page.locator('text="Invalid credentials"')).toBeVisible();

    // Should stay on sign in page
    await expect(page).toHaveURL("/auth/signin");
  });

  test("user can sign out", async ({ page }) => {
    // First sign in
    await page.goto("/auth/signin");
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");
    await page.click('[data-testid="signin-button"]');

    await expect(page).toHaveURL("/dashboard");

    // Click user menu
    await page.click('[data-testid="user-menu"]');

    // Click sign out
    await page.click('[data-testid="signout-button"]');

    // Should redirect to home or sign in page
    await expect(page).toHaveURL(/\/(auth\/signin|$)/);

    // Should no longer be authenticated
    await expect(page.locator('[data-testid="user-menu"]')).not.toBeVisible();
  });

  test("protected routes redirect to sign in", async ({ page }) => {
    // Try to access protected route without auth
    await page.goto("/dashboard");

    // Should redirect to sign in
    await expect(page).toHaveURL("/auth/signin");
  });

  test("authenticated users can access protected routes", async ({ page }) => {
    // Sign in first
    await page.goto("/auth/signin");
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");
    await page.click('[data-testid="signin-button"]');

    // Navigate to protected routes
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/dashboard");

    await page.goto("/challenges");
    await expect(page).toHaveURL("/challenges");
  });

  test("session persists across page reloads", async ({ page }) => {
    // Sign in
    await page.goto("/auth/signin");
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");
    await page.fill('[data-testid="password-input"]', "SecurePassword123!");
    await page.click('[data-testid="signin-button"]');

    await expect(page).toHaveURL("/dashboard");

    // Reload page
    await page.reload();

    // Should still be authenticated
    await expect(page).toHaveURL("/dashboard");
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test("password reset flow works", async ({ page }) => {
    await page.goto("/auth/signin");

    // Click forgot password link
    await page.click('[data-testid="forgot-password-link"]');

    await expect(page).toHaveURL("/auth/forgot-password");

    // Fill email
    await page.fill('[data-testid="email-input"]', "e2e-test@example.com");

    // Submit form
    await page.click('[data-testid="reset-password-button"]');

    // Should show success message
    await expect(
      page.locator('text="Password reset email sent"')
    ).toBeVisible();
  });

  test("handles rate limiting gracefully", async ({ page }) => {
    await page.goto("/auth/signin");

    // Make multiple rapid invalid login attempts
    for (let i = 0; i < 6; i++) {
      await page.fill('[data-testid="email-input"]', "test@example.com");
      await page.fill('[data-testid="password-input"]', "wrongpassword");
      await page.click('[data-testid="signin-button"]');

      if (i < 5) {
        await expect(page.locator('text="Invalid credentials"')).toBeVisible();
      }
    }

    // Should eventually show rate limiting message
    await expect(page.locator('text="Too many attempts"')).toBeVisible();
  });
});
