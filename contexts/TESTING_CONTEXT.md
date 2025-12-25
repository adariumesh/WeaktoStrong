# Testing Infrastructure Context

> **Domain:** Code Execution & Testing System  
> **Context Size:** ~4K tokens  
> **Session Focus:** Docker sandbox, test execution, results UI

## 📁 Files in This Domain

### Docker Sandbox

```
docker/web-sandbox/
├── Dockerfile                   # Security-hardened container
├── test-runner.js               # Node.js testing framework
├── package.json                 # Testing dependencies
├── html-validator.js            # HTML validation module
├── css-validator.js             # CSS validation module
└── build.sh                     # Container build script
```

### Backend Testing Service

```
backend/app/services/
└── test_runner.py               # Docker SDK integration

backend/app/api/v1/
└── challenges.py                # Testing endpoints (/test, /submit)
```

### Frontend Testing Components

```
apps/web/components/testing/
├── test-results.tsx             # Results visualization
└── test-status.tsx              # Service health monitoring

apps/web/lib/api/
└── test-runner.ts               # TypeScript API client
```

### Integration Points

```
apps/web/components/workspace/
└── workspace-panel.tsx          # Test Results tab integration

apps/web/components/editor/
├── monaco-editor-simple.tsx     # "Run Tests" button
└── terminal.tsx                 # Docker execution logs
```

## ⚡ Current Implementation Status

### ✅ Phase 4 Complete: Sandbox & Test Execution

**4.1: Docker Sandbox Infrastructure**

- Security-hardened Alpine Linux container
- Node.js 18 + Playwright + Lighthouse
- Resource constraints: 256MB RAM, 0.5 CPU, 30s timeout
- Network isolation, non-root execution
- Comprehensive HTML/CSS/JavaScript validation

**4.2: Test Runner Service**

- FastAPI service with Docker SDK
- Secure container lifecycle management
- JSON-based result communication
- Robust error handling for all failure modes

**4.3: Test Results UI Components**

- Real-time progress indicators
- Expandable test case details
- Performance metrics display
- Error categorization and reporting

**4.4: Enhanced Workspace Integration**

- 4-tab workspace layout with dedicated Test Results tab
- Enhanced terminal with Docker execution logs
- Complete API integration with error handling

## 🐳 Docker Sandbox Architecture

### Container Security

```dockerfile
# Security hardening
USER sandbox:sandbox             # Non-root execution (uid: 1001)
SECURITY_OPT=no-new-privileges   # Prevent privilege escalation
CAP_DROP=ALL                     # Drop all Linux capabilities
READ_ONLY=true                   # Read-only root filesystem
NETWORK_MODE=none                # No network access
TMPFS=/tmp,/sandbox/test-output  # Temporary filesystems only
```

### Test Runner Framework

```javascript
// Comprehensive web testing
class WebTestRunner {
  async runTests(userCode, testConfig) {
    return {
      htmlValidation: await this.validateHTML(userCode),
      cssValidation: await this.validateCSS(userCode),
      responsiveTest: await this.testResponsive(userCode),
      accessibilityTest: await this.testA11y(userCode),
      performanceTest: await this.testPerformance(userCode),
    };
  }
}
```

## 🔌 API Endpoints

```python
# Testing Endpoints
POST /api/v1/challenges/{id}/test         # Run tests immediately
POST /api/v1/challenges/{id}/submit       # Submit and run tests
GET  /api/v1/challenges/{id}/results/{submission_id}  # Get results
GET  /api/v1/test-runner/status           # Service health check
POST /api/v1/test-runner/cleanup          # Admin container cleanup
```

### API Request/Response Examples

**Test Execution Request:**

```typescript
interface TestRequest {
  challenge_id: string;
  code: string;
  language: "html" | "css" | "javascript";
  test_config?: {
    timeout?: number;
    responsive?: boolean;
    accessibility?: boolean;
  };
}
```

**Test Result Response:**

```typescript
interface TestResult {
  test_id: string;
  success: boolean;
  score: number;
  max_score: number;
  tests: TestCase[];
  errors: { message: string; type: string }[];
  metrics: {
    loadTime?: number;
    elements?: number;
    stylesheets?: number;
    scripts?: number;
  };
  execution_time_ms: number;
  timestamp: string;
}
```

## 🎯 Test Execution Flow

```
1. User clicks "Run Tests"
   ├── Monaco Editor → WorkspacePanel
   └── API call to /api/v1/challenges/{id}/test

2. Backend Processing
   ├── Validate request (auth, size limits)
   ├── Create temporary file with user code
   ├── Spin up Docker container
   └── Execute test-runner.js in sandbox

3. Container Execution
   ├── HTML validation with Cheerio
   ├── CSS validation with css-tree
   ├── Responsive testing with Playwright
   ├── Accessibility testing with Lighthouse
   └── Performance metrics collection

4. Results Processing
   ├── Parse JSON output from container
   ├── Calculate scores and metrics
   ├── Format errors and feedback
   └── Return structured TestResult

5. Frontend Display
   ├── TestResults component renders progress
   ├── Individual test case details
   ├── Performance metrics visualization
   └── Success/error state handling
```

## 🔧 Development Commands

### Container Management

```bash
# Build sandbox image
docker build -t weak-to-strong/web-sandbox:latest docker/web-sandbox/

# Test container locally
echo '<h1>Test</h1>' > test.html
docker run --rm -v $(pwd)/test.html:/sandbox/user-code/index.html:ro \
  weak-to-strong/web-sandbox:latest node test-runner.js /sandbox/user-code/index.html

# Check container security
docker run --rm weak-to-strong/web-sandbox:latest whoami  # Should output: sandbox
docker run --rm weak-to-strong/web-sandbox:latest id      # Should show uid=1001
```

### Backend Testing

```bash
# Start test runner service
cd backend && uvicorn main:app --reload

# Test API endpoints
curl -X POST localhost:8000/api/v1/challenges/web-001/test \
  -H "Content-Type: application/json" \
  -d '{"challenge_id":"web-001","code":"<h1>Hello</h1>","language":"html"}'

# Check service status
curl localhost:8000/api/v1/test-runner/status
```

### Frontend Testing

```bash
# Start frontend dev server
cd apps/web && npm run dev

# Navigate to challenge page
open http://localhost:3001/challenge

# Test workspace integration
# 1. Write code in Monaco Editor
# 2. Click "Run Tests"
# 3. Check Test Results tab
```

## 📊 Performance Metrics

### Execution Performance

- **Container startup:** ~1 second
- **Test execution:** 2-5 seconds typical
- **Memory usage:** <100MB per container
- **CPU usage:** Burst to 0.5 cores during testing

### Resource Limits

```python
CONTAINER_CONFIG = {
    "memory_limit": "256m",
    "cpu_quota": 50000,  # 0.5 CPU
    "timeout_seconds": 30,
    "network_mode": "none",
    "read_only": True
}
```

## 🐛 Common Issues & Solutions

### Issue: Container Build Fails

```bash
# Solution: Check Docker daemon and build logs
docker info
docker build --no-cache docker/web-sandbox/
```

### Issue: Test Execution Timeout

```bash
# Check container logs
docker logs <container_id>
# Increase timeout in test_runner.py: timeout_seconds=60
```

### Issue: "Permission Denied" in Container

```bash
# Verify sandbox user setup
docker run --rm weak-to-strong/web-sandbox:latest ls -la /sandbox
# Should show sandbox:sandbox ownership
```

### Issue: Frontend Not Showing Results

```bash
# Check API connectivity
curl localhost:8000/api/v1/test-runner/status
# Check browser console for JS errors
# Verify API_URL environment variable
```

## 🔐 Security Considerations

### Container Security

- Non-root user execution (uid: 1001)
- All Linux capabilities dropped
- Read-only root filesystem
- No network access
- Resource limits enforced
- Temporary filesystems only

### Code Safety

- Input size limits (100KB max)
- Execution timeout (30 seconds)
- Memory limits (256MB)
- No external resource access
- HTML/CSS/JS sanitization

### API Security

- JWT authentication required
- Rate limiting by user
- Input validation with Pydantic
- Error message sanitization

---

**Quick Start:** `npm run ctx testing` to load this context for testing infrastructure development.
