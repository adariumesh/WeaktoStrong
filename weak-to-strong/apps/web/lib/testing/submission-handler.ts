import {
  Challenge,
  Submission,
  TestResult,
  UserProgress,
} from "@/lib/types/challenge";
import { TestRunner, TestRunResult } from "./test-runner";

export interface SubmissionData {
  challengeId: string;
  code: string;
  language: string;
}

export interface SubmissionResult {
  submission: Submission;
  testResults: TestRunResult;
  progress: UserProgress;
  feedback: string;
  nextSteps?: string[];
}

export class SubmissionHandler {
  static async submitSolution(
    submissionData: SubmissionData,
    challenge: Challenge,
    userId: string = "demo-user"
  ): Promise<SubmissionResult> {
    // Run tests
    const testRunner = TestRunner.forChallenge(challenge);
    const testResults = await testRunner.runTests(submissionData.code);

    // Create submission record
    const submission: Submission = {
      id: this.generateId(),
      userId,
      challengeId: submissionData.challengeId,
      code: submissionData.code,
      language: submissionData.language,
      testResults: testResults.results,
      score: testResults.score,
      passed: testResults.passed,
      submittedAt: new Date().toISOString(),
      feedback: this.generateFeedback(testResults, challenge),
    };

    // Update user progress
    const progress = this.updateProgress(challenge, testResults, userId);

    // Generate feedback
    const feedback = this.generateDetailedFeedback(testResults, challenge);
    const nextSteps = this.generateNextSteps(testResults, challenge);

    return {
      submission,
      testResults,
      progress,
      feedback,
      nextSteps,
    };
  }

  private static generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private static updateProgress(
    challenge: Challenge,
    testResults: TestRunResult,
    userId: string
  ): UserProgress {
    // Calculate completion status
    const passRate = (testResults.score / testResults.maxScore) * 100;
    let status: UserProgress["status"] = "in_progress";

    if (passRate >= 80) {
      status = "completed";
    } else if (testResults.results.some((r) => r.passed)) {
      status = "in_progress";
    } else {
      status = "in_progress"; // Keep as in_progress rather than failed for learning
    }

    return {
      userId,
      challengeId: challenge.id,
      status,
      attempts: 1, // Would be incremented in real implementation
      hintsUsed: 0, // Would track hint usage
      bestScore: testResults.score,
      completedAt:
        status === "completed" ? new Date().toISOString() : undefined,
      timeSpent: testResults.executionTime,
      currentCode: testResults.passed ? undefined : challenge.starterCode,
    };
  }

  private static generateFeedback(
    testResults: TestRunResult,
    challenge: Challenge
  ): string {
    const passRate = (testResults.score / testResults.maxScore) * 100;

    if (testResults.error) {
      return `Test execution failed: ${testResults.error}`;
    }

    if (passRate >= 80) {
      return "🎉 Excellent work! Your solution meets all the requirements. Ready for the next challenge?";
    } else if (passRate >= 60) {
      return "👍 Good progress! A few more requirements to complete. You're on the right track!";
    } else if (passRate >= 40) {
      return "📚 Keep going! Review the requirements and try to implement the missing features.";
    } else {
      return "🔄 Let's try again! Check the requirements and use the hints if needed. You've got this!";
    }
  }

  private static generateDetailedFeedback(
    testResults: TestRunResult,
    challenge: Challenge
  ): string {
    const passedTests = testResults.results.filter((r) => r.passed);
    const failedTests = testResults.results.filter((r) => !r.passed);

    let feedback = `## Test Results: ${testResults.score}/${testResults.maxScore} points\n\n`;

    if (passedTests.length > 0) {
      feedback += `### ✅ Passed Tests (${passedTests.length})\n`;
      passedTests.forEach((test) => {
        feedback += `- **${test.name}**: ${test.points} points\n`;
      });
      feedback += "\n";
    }

    if (failedTests.length > 0) {
      feedback += `### ❌ Failed Tests (${failedTests.length})\n`;
      failedTests.forEach((test) => {
        feedback += `- **${test.name}**: ${test.error || "Test assertion failed"}\n`;
      });
      feedback += "\n";
    }

    // Add performance metrics if available
    const firstResult = testResults.results[0];
    if (firstResult?.metrics) {
      feedback += `### 📊 Performance Metrics\n`;
      feedback += `- Performance: ${firstResult.metrics.performance}/100\n`;
      feedback += `- Accessibility: ${firstResult.metrics.accessibility}/100\n`;
      feedback += `- Best Practices: ${firstResult.metrics.bestPractices}/100\n`;
      feedback += `- SEO: ${firstResult.metrics.seo}/100\n\n`;
    }

    return feedback;
  }

  private static generateNextSteps(
    testResults: TestRunResult,
    challenge: Challenge
  ): string[] {
    const failedTests = testResults.results.filter((r) => !r.passed);
    const nextSteps: string[] = [];

    if (failedTests.length === 0) {
      return [
        "🎯 Challenge completed! Review your solution to reinforce learning",
        "🚀 Ready for the next challenge? Check out the challenge list",
        "💡 Consider exploring advanced features or optimizations",
      ];
    }

    // Generate specific guidance based on failed tests
    failedTests.forEach((test) => {
      switch (test.testId) {
        case "test1":
          nextSteps.push(
            "📝 Review semantic HTML structure - use <article> and heading tags"
          );
          break;
        case "test2":
          nextSteps.push(
            "🖼️ Add an image element with proper alt text and avatar styling"
          );
          break;
        case "test3":
          nextSteps.push(
            "✏️ Implement proper typography with headings and paragraphs"
          );
          break;
        case "test4":
          nextSteps.push(
            "🔗 Add at least 3 social media links using anchor tags"
          );
          break;
        case "test5":
          nextSteps.push("🎨 Style the card with box-shadow and border-radius");
          break;
        default:
          nextSteps.push(`🔧 Address the issue in: ${test.name}`);
      }
    });

    // Add general guidance
    nextSteps.push(
      "💡 Use the hints if you're stuck - they provide helpful guidance"
    );
    nextSteps.push("📖 Check the resources panel for relevant documentation");

    return nextSteps;
  }

  // Helper method to get submission history (mock for now)
  static async getSubmissionHistory(
    challengeId: string,
    userId: string
  ): Promise<Submission[]> {
    // In real implementation, this would fetch from database
    return [];
  }

  // Helper method to get user progress
  static async getUserProgress(
    challengeId: string,
    userId: string
  ): Promise<UserProgress | null> {
    // In real implementation, this would fetch from database
    return null;
  }
}
