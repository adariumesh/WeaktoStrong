import { Challenge, TestResult, TestCase } from "@/lib/types/challenge";

export interface TestRunnerOptions {
  timeout?: number;
  verbose?: boolean;
  stopOnFirstFailure?: boolean;
}

export interface TestRunResult {
  passed: boolean;
  score: number;
  maxScore: number;
  results: TestResult[];
  executionTime: number;
  error?: string;
}

export class TestRunner {
  private challenge: Challenge;
  private options: TestRunnerOptions;

  constructor(challenge: Challenge, options: TestRunnerOptions = {}) {
    this.challenge = challenge;
    this.options = {
      timeout: 30000,
      verbose: false,
      stopOnFirstFailure: false,
      ...options,
    };
  }

  async runTests(code: string): Promise<TestRunResult> {
    const startTime = Date.now();
    const results: TestResult[] = [];
    let totalScore = 0;
    const maxScore = this.challenge.testConfig.tests.reduce(
      (sum, test) => sum + test.points,
      0
    );

    try {
      // Run each test case
      for (const testCase of this.challenge.testConfig.tests) {
        const result = await this.runSingleTest(testCase, code);
        results.push(result);

        if (result.passed) {
          totalScore += result.points;
        }

        // Stop on first failure if configured
        if (!result.passed && this.options.stopOnFirstFailure) {
          break;
        }
      }

      const executionTime = Date.now() - startTime;
      const passed = results.every((r) => r.passed);

      return {
        passed,
        score: totalScore,
        maxScore,
        results,
        executionTime,
      };
    } catch (error) {
      return {
        passed: false,
        score: 0,
        maxScore,
        results,
        executionTime: Date.now() - startTime,
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
      };
    }
  }

  private async runSingleTest(
    testCase: TestCase,
    code: string
  ): Promise<TestResult> {
    const result: TestResult = {
      testId: testCase.id,
      name: testCase.name,
      passed: false,
      points: 0,
    };

    try {
      switch (this.challenge.testConfig.type) {
        case "playwright":
          return await this.runPlaywrightTest(testCase, code);
        case "jest":
          return await this.runJestTest(testCase, code);
        case "pytest":
          return await this.runPytestTest(testCase, code);
        case "custom":
        default:
          return await this.runCustomTest(testCase, code);
      }
    } catch (error) {
      result.error =
        error instanceof Error ? error.message : "Test execution failed";
      return result;
    }
  }

  private async runPlaywrightTest(
    testCase: TestCase,
    code: string
  ): Promise<TestResult> {
    // Simulate Playwright test execution
    return new Promise((resolve) => {
      setTimeout(
        () => {
          const result = this.simulateHTMLTest(testCase, code);
          resolve(result);
        },
        Math.random() * 1000 + 500
      );
    });
  }

  private async runJestTest(
    testCase: TestCase,
    code: string
  ): Promise<TestResult> {
    // Simulate Jest test execution for JavaScript
    return new Promise((resolve) => {
      setTimeout(
        () => {
          const result: TestResult = {
            testId: testCase.id,
            name: testCase.name,
            passed: Math.random() > 0.3,
            points: Math.random() > 0.3 ? testCase.points : 0,
          };
          resolve(result);
        },
        Math.random() * 800 + 300
      );
    });
  }

  private async runPytestTest(
    testCase: TestCase,
    code: string
  ): Promise<TestResult> {
    // Simulate PyTest execution for Python
    return new Promise((resolve) => {
      setTimeout(
        () => {
          const result: TestResult = {
            testId: testCase.id,
            name: testCase.name,
            passed: Math.random() > 0.2,
            points: Math.random() > 0.2 ? testCase.points : 0,
          };
          resolve(result);
        },
        Math.random() * 1200 + 400
      );
    });
  }

  private async runCustomTest(
    testCase: TestCase,
    code: string
  ): Promise<TestResult> {
    return this.simulateHTMLTest(testCase, code);
  }

  private simulateHTMLTest(testCase: TestCase, code: string): TestResult {
    const result: TestResult = {
      testId: testCase.id,
      name: testCase.name,
      passed: false,
      points: 0,
    };

    // Simulate specific HTML/CSS tests based on test ID
    switch (testCase.id) {
      case "test1": // Profile Card Structure
        result.passed = this.checkHTMLStructure(code);
        break;
      case "test2": // Avatar Image
        result.passed = this.checkAvatarImage(code);
        break;
      case "test3": // Typography
        result.passed = this.checkTypography(code);
        break;
      case "test4": // Social Links
        result.passed = this.checkSocialLinks(code);
        break;
      case "test5": // Card Styling
        result.passed = this.checkCardStyling(code);
        break;
      default:
        // Generic test - pass 70% of the time for demo
        result.passed = Math.random() > 0.3;
    }

    if (result.passed) {
      result.points = testCase.points;
    } else {
      result.error = this.getTestFailureReason(testCase.id, code);
    }

    // Add performance metrics for web tests
    if (this.challenge.trackId === "web") {
      result.metrics = {
        performance: Math.floor(Math.random() * 40) + 60, // 60-100
        accessibility: Math.floor(Math.random() * 30) + 70, // 70-100
        bestPractices: Math.floor(Math.random() * 20) + 80, // 80-100
        seo: Math.floor(Math.random() * 35) + 65, // 65-100
      };
    }

    return result;
  }

  private checkHTMLStructure(code: string): boolean {
    // Check for semantic HTML elements
    const hasArticle = code.includes("<article");
    const hasHeading = code.includes("<h1") || code.includes("<h2");
    return hasArticle && hasHeading;
  }

  private checkAvatarImage(code: string): boolean {
    // Check for image with alt text and CSS classes
    const hasImage = code.includes("<img");
    const hasAltText = code.includes("alt=");
    const hasAvatarClass = code.includes("avatar") || code.includes("profile");
    return hasImage && hasAltText && hasAvatarClass;
  }

  private checkTypography(code: string): boolean {
    // Check for proper heading hierarchy
    const hasH1 = code.includes("<h1");
    const hasH2 = code.includes("<h2");
    const hasParagraph = code.includes("<p");
    return (hasH1 || hasH2) && hasParagraph;
  }

  private checkSocialLinks(code: string): boolean {
    // Count anchor tags (simple approximation)
    const linkMatches = code.match(/<a\s+[^>]*href/g);
    return linkMatches ? linkMatches.length >= 3 : false;
  }

  private checkCardStyling(code: string): boolean {
    // Check for CSS styling properties
    const hasBoxShadow = code.includes("box-shadow") || code.includes("shadow");
    const hasBorderRadius =
      code.includes("border-radius") || code.includes("rounded");
    const hasCardClass = code.includes("card");
    return hasBoxShadow && hasBorderRadius && hasCardClass;
  }

  private getTestFailureReason(testId: string, code: string): string {
    switch (testId) {
      case "test1":
        if (!code.includes("<article"))
          return "Missing <article> element for semantic structure";
        if (!code.includes("<h1") && !code.includes("<h2"))
          return "Missing heading elements (h1 or h2)";
        return "HTML structure validation failed";

      case "test2":
        if (!code.includes("<img")) return "No image element found";
        if (!code.includes("alt="))
          return "Image missing alt attribute for accessibility";
        return "Avatar image validation failed";

      case "test3":
        return "Typography hierarchy validation failed. Ensure proper use of heading tags and paragraph elements.";

      case "test4":
        const linkCount = (code.match(/<a\s+[^>]*href/g) || []).length;
        return `Found ${linkCount} social links, expected at least 3`;

      case "test5":
        if (!code.includes("box-shadow") && !code.includes("shadow"))
          return "Card missing box-shadow styling";
        if (!code.includes("border-radius") && !code.includes("rounded"))
          return "Card missing border-radius styling";
        return "Card styling validation failed";

      default:
        return "Test assertion failed. Please check the requirements and try again.";
    }
  }

  // Static helper method to get test runner for a challenge
  static forChallenge(
    challenge: Challenge,
    options?: TestRunnerOptions
  ): TestRunner {
    return new TestRunner(challenge, options);
  }
}
