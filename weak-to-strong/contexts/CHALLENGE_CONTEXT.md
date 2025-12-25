# Challenge System Context

> **Domain:** Challenge Management & Data  
> **Context Size:** ~3K tokens  
> **Session Focus:** Challenge creation, data management, requirements

## 📁 Files in This Domain

### Frontend Components

```
apps/web/components/challenge/
└── challenge-panel.tsx          # Challenge display and navigation

apps/web/app/
├── challenge/page.tsx           # Single challenge page
└── challenges/page.tsx          # Challenge list page
```

### Challenge Data & Types

```
apps/web/lib/data/
└── challenges.ts                # Challenge data and utilities

apps/web/lib/types/
└── challenge.ts                 # TypeScript interfaces
```

### Backend Challenge API

```
backend/app/api/v1/
└── challenges.py                # Challenge endpoints (subset)

backend/app/models/
└── [future: challenge.py]       # Challenge database model

backend/app/schemas/
└── [future: challenge.py]       # Challenge Pydantic schemas
```

### External References

```
CHALLENGE_CONTENT.md             # Complete challenge specifications
AI_PROMPTS.md                    # Challenge-specific prompts
```

## ⚡ Current Implementation Status

### ✅ Completed Features

**Challenge Display System:**

- Challenge panel with requirements, constraints, hints
- Professional UI with progress tracking
- Responsive design for mobile and desktop
- Integration with workspace and testing system

**Challenge Data Structure:**

- Complete TypeScript interfaces
- 15 web development challenges defined
- Structured requirements and test configurations
- Difficulty progression system

**Challenge Navigation:**

- Challenge list page with filtering
- Individual challenge pages
- URL routing with Next.js App Router

### 🏗 Challenge Data Architecture

```typescript
interface Challenge {
  id: string; // Unique identifier (e.g., "web-001")
  title: string; // Display name
  description: string; // Markdown description
  difficulty: "beginner" | "intermediate" | "advanced";
  track: "web" | "data" | "cloud";
  order: number; // Sequence in track
  points: number; // Score value
  estimatedTime: string; // "30-45 minutes"

  // Learning objectives
  requirements: Requirement[]; // What to build
  constraints: Constraint[]; // Technical limitations
  hints: string[]; // Progressive hints (3 levels)

  // Technical configuration
  starterCode: string; // Initial code template
  testConfig: TestConfiguration; // How to evaluate submission

  // Metadata
  tags: string[]; // Searchable tags
  prerequisites: string[]; // Required prior knowledge
  resources: Resource[]; // Learning materials
}
```

### Requirements & Constraints

```typescript
interface Requirement {
  id: string;
  text: string; // Human-readable requirement
  points: number; // Point value for this requirement
  testable: boolean; // Can be automatically tested
  category: "functional" | "visual" | "technical" | "accessibility";
}

interface Constraint {
  id: string;
  text: string; // Constraint description
  type: "technical" | "accessibility" | "performance" | "security";
  enforcement: "strict" | "recommended";
}
```

## 🎯 Current Challenge Collection

### Web Development Track (15 challenges)

**Beginner Level (5 challenges):**

1. **Personal Landing Page** - HTML structure, CSS basics
2. **Product Card** - Flexbox layout, hover effects
3. **Contact Form** - Form elements, basic validation
4. **Navigation Menu** - CSS navigation, responsive design
5. **Image Gallery** - Grid layout, responsive images

**Intermediate Level (7 challenges):** 6. **Weather Dashboard** - API integration, dynamic content 7. **Task Manager** - Local storage, CRUD operations 8. **Pricing Table** - Advanced CSS, animations 9. **Blog Layout** - Complex layouts, typography 10. **Shopping Cart** - State management, calculations 11. **Modal System** - JavaScript interactions, accessibility 12. **Data Visualization** - Charts, responsive graphics

**Advanced Level (3 challenges):** 13. **E-commerce Checkout** - Multi-step forms, validation 14. **Real-time Chat** - WebSocket integration, performance 15. **Portfolio Website** - Complete application, optimization

## 🔌 Challenge API Integration

### Current Endpoints

```typescript
// Challenge-related endpoints in challenges.py
POST /api/v1/challenges/{id}/test      # Execute challenge tests
POST /api/v1/challenges/{id}/submit    # Submit challenge solution

// Future endpoints (planned)
GET  /api/v1/challenges                # List all challenges
GET  /api/v1/challenges/{id}           # Get specific challenge
GET  /api/v1/challenges/{id}/hints/{n} # Get progressive hints
```

### Challenge Test Configuration

```typescript
interface TestConfiguration {
  type: "playwright" | "jest" | "manual";
  timeout: number; // Execution timeout in ms
  tests: TestCase[]; // Individual test cases

  // Web-specific configuration
  viewport?: {
    mobile: { width: 375; height: 667 };
    tablet: { width: 768; height: 1024 };
    desktop: { width: 1920; height: 1080 };
  };

  // Accessibility testing
  accessibility?: {
    enabled: boolean;
    rules: string[]; // WCAG rules to check
    minScore: number; // Lighthouse accessibility score
  };

  // Performance testing
  performance?: {
    enabled: boolean;
    metrics: string[]; // Core Web Vitals
    thresholds: Record<string, number>;
  };
}
```

## 🎨 Challenge Panel UI

### Component Structure

```typescript
// Challenge Panel Layout
<Card className="h-full overflow-hidden">
  <CardHeader>
    <div className="flex items-center justify-between">
      <Badge variant="outline">{challenge.track}</Badge>
      <Badge variant="default">{challenge.difficulty}</Badge>
    </div>
    <CardTitle>{challenge.title}</CardTitle>
    <div className="flex items-center gap-4 text-sm text-gray-600">
      <span>📊 {challenge.points} points</span>
      <span>⏱️ {challenge.estimatedTime}</span>
    </div>
  </CardHeader>

  <CardContent>
    <Tabs defaultValue="description">
      <TabsList>
        <TabsTrigger value="description">Description</TabsTrigger>
        <TabsTrigger value="requirements">Requirements</TabsTrigger>
        <TabsTrigger value="hints">Hints</TabsTrigger>
      </TabsList>

      <TabsContent value="description">
        <ReactMarkdown>{challenge.description}</ReactMarkdown>
      </TabsContent>

      <TabsContent value="requirements">
        <RequirementsList requirements={challenge.requirements} />
        <ConstraintsList constraints={challenge.constraints} />
      </TabsContent>

      <TabsContent value="hints">
        <ProgressiveHints hints={challenge.hints} />
      </TabsContent>
    </Tabs>
  </CardContent>
</Card>
```

### Requirements Display

```typescript
const RequirementsList = ({ requirements }: { requirements: Requirement[] }) => (
  <div className="space-y-3">
    <h3 className="font-semibold">Requirements</h3>
    {requirements.map((req) => (
      <div key={req.id} className="flex items-start gap-3 p-3 border rounded">
        <div className="w-5 h-5 border-2 rounded border-gray-300" />
        <div className="flex-1">
          <p className="text-sm">{req.text}</p>
          <div className="flex items-center gap-2 mt-1">
            <Badge variant="outline" className="text-xs">
              {req.points} pts
            </Badge>
            <Badge variant="outline" className="text-xs">
              {req.category}
            </Badge>
          </div>
        </div>
      </div>
    ))}
  </div>
);
```

## 🔧 Development Commands

### Challenge Development Session

```bash
npm run ctx challenges           # Load challenge context
npm run find challenge          # Find challenge-related files
open http://localhost:3001/challenge  # View challenge page
```

### Challenge Data Management

```bash
# Edit challenge data
code apps/web/lib/data/challenges.ts

# Add new challenge
npm run find challenge-template  # Find template structure

# Test challenge display
curl localhost:3001/api/challenges  # Future endpoint
```

### Challenge Testing

```bash
# Test challenge component
cd apps/web && npm run dev
# Navigate to /challenge or /challenges

# Test challenge integration with workspace
# 1. Load challenge in Challenge Panel
# 2. Verify workspace loads starter code
# 3. Test "Run Tests" integration
```

## 📊 Challenge Progression System

### Difficulty Mapping

```typescript
const DIFFICULTY_CONFIG = {
  beginner: {
    points: 50 - 100,
    estimatedTime: "15-30 minutes",
    concepts: ["HTML basics", "CSS fundamentals", "Basic JavaScript"],
    unlockRequirement: "none",
  },
  intermediate: {
    points: 100 - 200,
    estimatedTime: "30-60 minutes",
    concepts: ["API integration", "State management", "Responsive design"],
    unlockRequirement: "80% pass rate on beginner challenges",
  },
  advanced: {
    points: 200 - 300,
    estimatedTime: "60-120 minutes",
    concepts: [
      "Performance optimization",
      "Accessibility",
      "Advanced patterns",
    ],
    unlockRequirement: "80% pass rate on intermediate challenges",
  },
};
```

### Challenge Dependencies

```typescript
// Challenge prerequisite system
const CHALLENGE_DEPENDENCIES = {
  "web-006": ["web-001", "web-002"], // Weather Dashboard needs basics
  "web-010": ["web-006", "web-007"], // Shopping Cart needs API + forms
  "web-015": ["web-012", "web-013", "web-014"], // Portfolio needs all advanced
};
```

## 🎯 Content Management

### Challenge Creation Process

```typescript
// Template for new challenges
const newChallenge: Challenge = {
  id: "web-016",
  title: "New Challenge Title",
  description: `## Challenge Description\n\nBuild a...`,
  difficulty: "intermediate",
  track: "web",
  order: 16,
  points: 150,
  estimatedTime: "45-60 minutes",

  requirements: [
    {
      id: "req1",
      text: "Create...",
      points: 50,
      testable: true,
      category: "functional",
    },
  ],
  constraints: [
    {
      id: "con1",
      text: "Must be...",
      type: "accessibility",
      enforcement: "strict",
    },
  ],
  hints: [
    "Start by considering...",
    "You might want to use...",
    "The solution involves...",
  ],

  starterCode: "<!-- Your starter HTML here -->",
  testConfig: {
    /* test configuration */
  },

  tags: ["html", "css", "javascript"],
  prerequisites: ["HTML basics", "CSS layout"],
  resources: [],
};
```

### Content Validation

```typescript
// Ensure challenge data integrity
const validateChallenge = (challenge: Challenge): ValidationResult => {
  const errors = [];

  if (!challenge.id.match(/^[a-z]+-\d{3}$/)) {
    errors.push("Invalid ID format");
  }

  if (challenge.requirements.length === 0) {
    errors.push("Challenge must have at least one requirement");
  }

  if (challenge.hints.length !== 3) {
    errors.push("Challenge must have exactly 3 progressive hints");
  }

  return { isValid: errors.length === 0, errors };
};
```

## 🐛 Common Issues & Solutions

### Issue: Challenge Not Loading

```typescript
// Check challenge exists in data file
const challenge = getChallengeById("web-001");
if (!challenge) {
  console.error("Challenge not found");
}
```

### Issue: Starter Code Not Appearing

```typescript
// Verify workspace integration
useEffect(() => {
  if (challenge?.starterCode) {
    setCode(challenge.starterCode);
  }
}, [challenge]);
```

### Issue: Requirements Not Updating

```typescript
// Check React key prop for list rendering
{requirements.map((req) => (
  <RequirementItem key={req.id} requirement={req} />
))}
```

---

**Quick Start:** `npm run ctx challenges` to load this context for challenge system development.
