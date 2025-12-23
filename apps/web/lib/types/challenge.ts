export interface ChallengeRequirement {
  id: string;
  text: string;
  points: number;
  completed?: boolean;
}

export interface ChallengeConstraint {
  id: string;
  text: string;
  type: "accessibility" | "performance" | "security" | "technical";
}

export interface TestConfig {
  type: "playwright" | "pytest" | "jest" | "custom";
  timeout: number;
  tests: TestCase[];
}

export interface TestCase {
  id: string;
  name: string;
  description: string;
  selector?: string;
  assertion: string;
  points: number;
}

export interface ChallengeHint {
  id: string;
  level: 1 | 2 | 3;
  text: string;
  revealed?: boolean;
}

export interface Challenge {
  id: string;
  trackId: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  order: number;
  modelTier: "local" | "haiku" | "sonnet";
  points: number;
  estimatedTime: number; // in minutes
  tags: string[];
  requirements: ChallengeRequirement[];
  constraints: ChallengeConstraint[];
  testConfig: TestConfig;
  hints: ChallengeHint[];
  isRedTeam: boolean;
  starterCode?: string;
  solution?: string; // For development/testing only
  resources: ChallengeResource[];
}

export interface ChallengeResource {
  id: string;
  type: "documentation" | "video" | "example" | "tool";
  title: string;
  description: string;
  url: string;
  duration?: number; // for videos, in seconds
}

export interface Track {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  order: number;
  challenges: Challenge[];
  totalChallenges: number;
  totalPoints: number;
}

export interface UserProgress {
  userId: string;
  challengeId: string;
  status: "not_started" | "in_progress" | "completed" | "failed";
  attempts: number;
  hintsUsed: number;
  bestScore: number;
  completedAt?: string;
  timeSpent: number; // in seconds
  currentCode?: string;
}

export interface Submission {
  id: string;
  userId: string;
  challengeId: string;
  code: string;
  language: string;
  testResults: TestResult[];
  score: number;
  passed: boolean;
  submittedAt: string;
  feedback?: string;
}

export interface TestResult {
  testId: string;
  name: string;
  passed: boolean;
  points: number;
  error?: string;
  screenshot?: string;
  metrics?: {
    performance?: number;
    accessibility?: number;
    bestPractices?: number;
    seo?: number;
  };
}
