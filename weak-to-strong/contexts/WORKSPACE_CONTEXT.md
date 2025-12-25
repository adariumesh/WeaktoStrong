# Workspace Context

> **Domain:** Code Editor & Development Environment  
> **Context Size:** ~2K tokens  
> **Session Focus:** Editor improvements, preview features, workspace layout

## 📁 Files in This Domain

### Core Workspace Components

```
apps/web/components/workspace/
└── workspace-panel.tsx          # Main 4-tab workspace layout

apps/web/components/editor/
├── monaco-editor-simple.tsx     # Code editor with SSR support
├── live-preview.tsx             # Live HTML/CSS preview
└── terminal.tsx                 # Test output terminal
```

### Editor Integration

```
apps/web/lib/
├── security/sanitization.ts     # XSS protection for preview
└── testing/test-runner.ts       # Local test execution utilities

apps/web/components/resources/
└── resources-panel.tsx          # Documentation and AI assistant
```

## ⚡ Current Implementation Status

### ✅ Completed Workspace Features

**4-Tab Workspace Layout:**

- Code Editor: Monaco Editor with syntax highlighting
- Live Preview: Responsive HTML/CSS preview with security
- Test Results: Comprehensive test execution and results
- Terminal: Real-time Docker execution logs

**Monaco Editor Integration:**

- Professional code editor with autocomplete
- Syntax highlighting for HTML/CSS/JavaScript
- "Run Tests" button integration
- Download code functionality
- Reset to starter code
- SSR-safe implementation

**Live Preview System:**

- Responsive viewport testing (mobile/tablet/desktop)
- Security validation and HTML sanitization
- Auto-refresh with debouncing
- Fullscreen mode
- Error state handling

**Terminal Integration:**

- Real-time test execution logs
- Color-coded output (info/success/warning/error)
- Docker container status monitoring
- Log download functionality

## 🎨 Workspace Layout Architecture

### Panel Structure

```typescript
// 4-tab workspace layout
<Tabs defaultValue="editor" className="flex-1 flex flex-col">
  <TabsList className="grid w-full grid-cols-4 rounded-none bg-muted/30">
    <TabsTrigger value="editor">
      <Code className="w-4 h-4" />
      Code Editor
    </TabsTrigger>
    <TabsTrigger value="preview">
      <Eye className="w-4 h-4" />
      Live Preview
    </TabsTrigger>
    <TabsTrigger value="results">
      <Play className="w-4 h-4" />
      Test Results
    </TabsTrigger>
    <TabsTrigger value="terminal">
      <Terminal className="w-4 h-4" />
      Terminal
    </TabsTrigger>
  </TabsList>

  {/* Tab content areas */}
</Tabs>
```

### State Management

```typescript
// Workspace state
const [code, setCode] = useState(challenge?.starterCode || "");
const [isTestRunning, setIsTestRunning] = useState(false);
const [testResult, setTestResult] = useState<TestResult | null>(null);
const [testError, setTestError] = useState<string | null>(null);

// Test execution handler
const handleRunTests = async () => {
  setIsTestRunning(true);
  setTestError(null);
  setTestResult(null);

  try {
    const result = await testRunnerAPI.runTests({
      challenge_id: challengeId,
      code: code,
      language: "html",
    });
    setTestResult(result);
  } catch (error) {
    setTestError(error.message);
  } finally {
    setIsTestRunning(false);
  }
};
```

## 🖥 Monaco Editor Configuration

### Editor Setup

```typescript
// SSR-safe dynamic import
const Editor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-gray-50">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-600">Loading editor...</p>
      </div>
    </div>
  )
});
```

### Editor Options

```typescript
const editorOptions = {
  readOnly: false,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  fontSize: 14,
  fontFamily:
    "'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace",
  lineNumbers: "on",
  renderWhitespace: "selection",
  automaticLayout: true,
  wordWrap: "on",
  bracketPairColorization: { enabled: true },
  suggest: {
    showKeywords: true,
    showSnippets: true,
  },
  quickSuggestions: {
    other: true,
    comments: true,
    strings: true,
  },
  parameterHints: { enabled: true },
  autoIndent: "full",
  formatOnPaste: true,
  formatOnType: true,
};
```

### Editor Toolbar

```typescript
// Professional editor toolbar
<div className="flex items-center justify-between px-3 py-2 bg-gray-50 border-b">
  <div className="flex items-center gap-3">
    <span className="text-sm font-medium text-gray-700">{fileName}</span>
    <span className="text-xs text-gray-500">{language.toUpperCase()}</span>
  </div>

  <div className="flex items-center gap-2">
    <Button size="sm" variant="ghost" onClick={downloadCode}>
      <Download size={14} />
    </Button>

    <Button size="sm" variant="outline" onClick={onReset}>
      <RotateCcw size={14} />
    </Button>

    <Button size="sm" onClick={onRun} className="bg-green-600 hover:bg-green-700">
      <Play size={14} className="mr-1" />
      Run Tests
    </Button>
  </div>
</div>
```

## 🖼 Live Preview System

### Security-First Preview

```typescript
// HTML sanitization for safe preview
const refreshPreview = useCallback(() => {
  if (iframeRef.current) {
    // Validate and sanitize the code
    const safety = validateHTMLSafety(code);
    setSecurityWarnings(safety.warnings);
    setHasSecurityErrors(!safety.isSafe);

    if (!safety.isSafe) {
      return; // Don't render unsafe content
    }

    // Sanitize the HTML content
    const sanitizedCode = sanitizeHTML(code);

    // Create blob URL for iframe
    const blob = new Blob([sanitizedCode], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    iframeRef.current.src = url;
  }
}, [code]);
```

### Responsive Testing

```typescript
// Viewport dimension configuration
const getViewportDimensions = () => {
  switch (viewport) {
    case "mobile":
      return { width: "375px", height: "667px" };
    case "tablet":
      return { width: "768px", height: "1024px" };
    case "desktop":
    default:
      return { width: "100%", height: "100%" };
  }
};

// Viewport controls
<div className="flex items-center bg-white border border-gray-200 rounded-md p-0.5">
  {["mobile", "tablet", "desktop"].map((view) => (
    <Button
      key={view}
      variant={viewport === view ? "default" : "ghost"}
      onClick={() => setViewport(view)}
      className="h-6 px-2"
    >
      {getViewportIcon(view)}
    </Button>
  ))}
</div>
```

### Preview Security Features

```typescript
// Security warning display
{securityWarnings.length > 0 && (
  <div className="absolute top-4 right-4 bg-orange-50 border border-orange-200 rounded-lg p-3">
    <div className="flex items-center gap-2 mb-2">
      <Shield className="w-4 h-4 text-orange-500" />
      <span className="text-sm font-medium text-orange-800">Security Warnings</span>
    </div>
    <div className="space-y-1">
      {securityWarnings.map((warning, index) => (
        <div key={index} className="text-xs text-orange-600">{warning}</div>
      ))}
    </div>
  </div>
)}
```

## 🔧 Development Commands

### Workspace Development Session

```bash
npm run ctx workspace           # Load workspace context
cd apps/web && npm run dev      # Start development server
open http://localhost:3001/challenge  # Open workspace
```

### Editor Testing

```bash
# Test Monaco Editor loading
# 1. Open browser dev tools
# 2. Navigate to challenge page
# 3. Check for "Loading editor..." message
# 4. Verify editor loads without errors

# Test SSR compatibility
npm run build                   # Verify no SSR errors
npm start                       # Test production build
```

### Preview Testing

```bash
# Test security validation
# 1. Enter HTML with <script> tags
# 2. Verify security warning appears
# 3. Test sanitization works

# Test responsive modes
# 1. Switch between mobile/tablet/desktop
# 2. Verify viewport dimensions change
# 3. Test fullscreen mode
```

### Terminal Integration

```bash
# Test terminal output
# 1. Run tests from editor
# 2. Check terminal tab shows logs
# 3. Verify real-time updates
# 4. Test log download functionality
```

## 🎯 Editor Features

### Code Intelligence

```typescript
// Autocomplete configuration
const suggest = {
  showKeywords: true, // HTML/CSS keywords
  showSnippets: true, // Code snippets
  showProperties: true, // CSS properties
  showValues: true, // CSS values
  showClasses: true, // CSS classes
  showIds: true, // CSS IDs
  showColors: true, // Color values
};

// Format on save
const handleSave = () => {
  monaco.editor.getModel()?.getAction("editor.action.formatDocument")?.run();
};
```

### File Operations

```typescript
// Download code functionality
const downloadCode = () => {
  const blob = new Blob([code], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Reset to starter code
const handleResetCode = () => {
  if (challenge?.starterCode) {
    setCode(challenge.starterCode);
  }
};
```

## 📱 Mobile Responsiveness

### Mobile Workspace Layout

```typescript
// Responsive tab layout for mobile
<div className="md:hidden">
  <Tabs defaultValue="editor" className="h-full">
    <TabsList className="w-full grid grid-cols-2">
      <TabsTrigger value="editor">Code</TabsTrigger>
      <TabsTrigger value="preview">Preview</TabsTrigger>
    </TabsList>
    {/* Simplified mobile tabs */}
  </Tabs>
</div>

// Full desktop layout
<div className="hidden md:block">
  <Tabs defaultValue="editor" className="h-full">
    <TabsList className="grid grid-cols-4">
      {/* All 4 tabs */}
    </TabsList>
    {/* Full desktop workspace */}
  </Tabs>
</div>
```

### Touch-Friendly Controls

```typescript
// Larger touch targets for mobile
const mobileButtonClass = "h-10 px-4 text-base"; // Larger than desktop
const desktopButtonClass = "h-7 px-3 text-sm"; // Standard size

const buttonClass = isMobile ? mobileButtonClass : desktopButtonClass;
```

## 🐛 Common Issues & Solutions

### Issue: Monaco Editor Not Loading

```typescript
// Check dynamic import
useEffect(() => {
  import("@monaco-editor/react")
    .then((module) => {
      console.log("Monaco loaded:", module.default);
    })
    .catch(console.error);
}, []);
```

### Issue: Preview Security Errors

```typescript
// Debug sanitization
const debugSanitization = (code: string) => {
  console.log("Original code:", code);
  const sanitized = sanitizeHTML(code);
  console.log("Sanitized code:", sanitized);
  return sanitized;
};
```

### Issue: Test Integration Not Working

```typescript
// Verify API integration
const testAPIConnection = async () => {
  try {
    const status = await testRunnerAPI.getTestRunnerStatus();
    console.log("Test runner status:", status);
  } catch (error) {
    console.error("API connection failed:", error);
  }
};
```

---

**Quick Start:** `npm run ctx workspace` to load this context for workspace development.
