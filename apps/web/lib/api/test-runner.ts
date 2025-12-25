/**
 * API client for test runner service
 */

export interface TestCase {
  name: string;
  description: string;
  passed: boolean;
  points: number;
  error?: string;
}

export interface TestResult {
  test_id: string;
  challenge_id: string;
  success: boolean;
  score: number;
  max_score: number;
  tests: TestCase[];
  errors: Array<{
    message: string;
    type: string;
  }>;
  metrics: {
    loadTime?: number;
    elements?: number;
    scripts?: number;
    stylesheets?: number;
  };
  execution_time_ms: number;
  timestamp: string;
}

// New unified execution result format from backend
export interface ExecutionResult {
  challenge_id: string;
  user_id: string;
  track_type: string; // "web", "data", "cloud"
  success: boolean;
  score: number;
  max_score: number;
  execution_time_ms: number;
  output: string;
  errors: string[];
  test_details: Record<string, any>;
  validation_results: Array<Record<string, any>>;
  insights_found?: boolean; // Data analysis specific
}

export interface SubmissionRequest {
  challenge_id: string;
  code: string;
  language?: string;
  test_config?: Record<string, any>;
}

class TestRunnerAPI {
  private baseUrl: string;

  constructor() {
    this.baseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
  }

  private getAuthToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("auth_token");
    }
    return null;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    const token = this.getAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  async runTests(submission: SubmissionRequest): Promise<TestResult> {
    try {
      const response = await fetch(
        `${this.baseUrl}/challenges/${submission.challenge_id}/test`,
        {
          method: "POST",
          headers: this.getHeaders(),
          body: JSON.stringify(submission),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Test execution failed: ${response.status} ${errorText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  // New unified execution method for all track types
  async executeChallenge(
    submission: SubmissionRequest
  ): Promise<ExecutionResult> {
    try {
      const response = await fetch(
        `${this.baseUrl}/challenges/${submission.challenge_id}/execute`,
        {
          method: "POST",
          headers: this.getHeaders(),
          body: JSON.stringify(submission),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Challenge execution failed: ${response.status} ${errorText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  async submitChallenge(submission: SubmissionRequest): Promise<{
    submission_id: string;
    challenge_id: string;
    status: string;
    message: string;
  }> {
    try {
      const response = await fetch(
        `${this.baseUrl}/challenges/${submission.challenge_id}/submit`,
        {
          method: "POST",
          headers: this.getHeaders(),
          body: JSON.stringify(submission),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Submission failed: ${response.status} ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  async getTestRunnerStatus(): Promise<{
    status: string;
    service: string;
    stats?: any;
    error?: string;
    timestamp: string;
  }> {
    try {
      const response = await fetch(`${this.baseUrl}/test-runner/status`, {
        method: "GET",
        headers: this.getHeaders(),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Status check failed: ${response.status} ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }
}

export const testRunnerAPI = new TestRunnerAPI();
