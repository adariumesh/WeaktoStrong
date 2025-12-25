# UI Foundation Context

> **Domain:** UI Components & Layout System  
> **Context Size:** ~2K tokens  
> **Session Focus:** Component improvements, styling, responsive design

## 📁 Files in This Domain

### UI Components (Shadcn/ui)

```
apps/web/components/ui/
├── badge.tsx                    # Status badges and labels
├── button.tsx                   # Primary button component
├── card.tsx                     # Card container component
├── input.tsx                    # Form input component
├── scroll-area.tsx              # Custom scrollable areas
├── select.tsx                   # Dropdown select component
├── tabs.tsx                     # Tab navigation component
└── textarea.tsx                 # Multi-line text input
```

### Layout Components

```
apps/web/components/layout/
└── three-panel-layout.tsx       # Main resizable layout system

apps/web/components/common/
└── error-boundary.tsx           # React error boundary
```

### Styling System

```
apps/web/
├── app/globals.css              # Global styles & CSS variables
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
└── next.config.js               # Next.js configuration
```

## ⚡ Current Implementation Status

### ✅ Completed UI System

**Shadcn/ui Integration:**

- Professional component library with consistent design
- Tailwind CSS utility classes
- CSS custom properties for theming
- Responsive design patterns
- Accessibility-compliant components

**Three-Panel Layout:**

- Resizable panels: Challenge | Workspace | Resources
- Mobile-responsive with tab switching
- Persistent panel sizes with localStorage
- Keyboard navigation support

**Design System:**

- Consistent color palette
- Typography scale with Inter font
- Spacing and sizing tokens
- Component variants and states

## 🎨 Design System Overview

### Color Palette

```css
/* Primary Colors */
--primary: 222.2 84% 4.9%; /* Dark blue */
--primary-foreground: 210 40% 98%; /* Light text */

/* UI Colors */
--background: 0 0% 100%; /* White background */
--foreground: 222.2 84% 4.9%; /* Dark text */
--muted: 210 40% 96%; /* Light gray */
--border: 214.3 31.8% 91.4%; /* Light border */

/* Semantic Colors */
--destructive: 0 84.2% 60.2%; /* Red for errors */
--ring: 222.2 84% 4.9%; /* Focus ring */
```

### Typography Scale

```css
/* Font Sizes */
text-xs     /* 12px */
text-sm     /* 14px */
text-base   /* 16px */
text-lg     /* 18px */
text-xl     /* 20px */
text-2xl    /* 24px */
text-3xl    /* 30px */

/* Font Weights */
font-normal   /* 400 */
font-medium   /* 500 */
font-semibold /* 600 */
font-bold     /* 700 */
```

## 🧩 Component Library

### Button Component

```typescript
interface ButtonProps {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
  asChild?: boolean;
}

// Usage examples
<Button variant="default" size="lg">Primary Action</Button>
<Button variant="outline" size="sm">Secondary</Button>
<Button variant="ghost" size="icon"><Icon /></Button>
```

### Card Component

```typescript
// Composed card structure
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Main content area
  </CardContent>
  <CardFooter>
    Footer actions
  </CardFooter>
</Card>
```

### Tabs Component

```typescript
// Tab navigation pattern
<Tabs defaultValue="tab1" className="w-full">
  <TabsList className="grid w-full grid-cols-3">
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
    <TabsTrigger value="tab3">Tab 3</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Tab 1 content</TabsContent>
  <TabsContent value="tab2">Tab 2 content</TabsContent>
  <TabsContent value="tab3">Tab 3 content</TabsContent>
</Tabs>
```

## 📱 Responsive Design System

### Breakpoints

```css
/* Tailwind breakpoints */
sm: 640px    /* Small devices (landscape phones) */
md: 768px    /* Medium devices (tablets) */
lg: 1024px   /* Large devices (laptops) */
xl: 1280px   /* Extra large devices (desktops) */
2xl: 1536px  /* 2X large devices (large desktops) */
```

### Layout Patterns

```typescript
// Three-panel desktop layout
<div className="hidden md:grid md:grid-cols-3 md:gap-4">
  <ChallengePanel />
  <WorkspacePanel />
  <ResourcesPanel />
</div>

// Mobile tab layout
<div className="md:hidden">
  <Tabs defaultValue="workspace">
    <TabsList>
      <TabsTrigger value="challenge">Challenge</TabsTrigger>
      <TabsTrigger value="workspace">Workspace</TabsTrigger>
      <TabsTrigger value="resources">Resources</TabsTrigger>
    </TabsList>
    <TabsContent value="challenge"><ChallengePanel /></TabsContent>
    <TabsContent value="workspace"><WorkspacePanel /></TabsContent>
    <TabsContent value="resources"><ResourcesPanel /></TabsContent>
  </Tabs>
</div>
```

## 🔧 Development Commands

### UI Development Session

```bash
npm run ctx ui                   # Load UI context
cd apps/web && npm run dev       # Start dev server
open http://localhost:3001       # View in browser
```

### Component Development

```bash
# Create new component using shadcn/ui
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add toast

# Test component in Storybook (if available)
npm run storybook
```

### Styling Tasks

```bash
# Check Tailwind classes
npm run build                    # Verify no CSS conflicts
npx tailwindcss --watch          # Watch CSS changes

# Responsive testing
# Use browser dev tools device emulation
# Test breakpoints: 640px, 768px, 1024px, 1280px
```

## 🎯 Component Usage Patterns

### Form Components

```typescript
// Consistent form layout
<div className="grid gap-4">
  <div className="grid gap-2">
    <Label htmlFor="email">Email</Label>
    <Input
      id="email"
      type="email"
      placeholder="Enter your email"
      className="w-full"
    />
  </div>
  <div className="grid gap-2">
    <Label htmlFor="message">Message</Label>
    <Textarea
      id="message"
      placeholder="Type your message..."
      className="min-h-[100px]"
    />
  </div>
  <Button type="submit" className="w-full">
    Submit
  </Button>
</div>
```

### Loading States

```typescript
// Loading button pattern
<Button disabled={isLoading}>
  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isLoading ? "Loading..." : "Submit"}
</Button>

// Loading skeleton pattern
<div className="space-y-2">
  <div className="h-4 bg-gray-200 rounded animate-pulse" />
  <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
  <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
</div>
```

### Error States

```typescript
// Error message pattern
{error && (
  <div className="bg-red-50 border border-red-200 rounded p-3">
    <div className="flex items-center gap-2">
      <AlertTriangle className="h-4 w-4 text-red-500" />
      <p className="text-sm text-red-700">{error}</p>
    </div>
  </div>
)}
```

## 🎨 Dark Mode Preparation

### CSS Variables Setup

```css
/* Light mode (default) */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}

/* Dark mode */
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}
```

### Component Dark Mode Support

```typescript
// Use CSS variables for theming
<div className="bg-background text-foreground border-border">
  Content that adapts to theme
</div>

// Conditional dark mode classes
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Theme-aware content
</div>
```

## 📊 Accessibility Standards

### ARIA Labels

```typescript
// Proper labeling
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>

// Form accessibility
<Label htmlFor="search">Search</Label>
<Input
  id="search"
  role="searchbox"
  aria-describedby="search-help"
/>
<p id="search-help" className="text-sm text-gray-600">
  Enter keywords to search
</p>
```

### Keyboard Navigation

```typescript
// Focus management
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === "Escape") {
    onClose();
  }
  if (e.key === "Tab") {
    // Handle tab navigation
  }
};
```

## 🐛 Common UI Issues & Solutions

### Issue: Layout Shift on Mobile

```css
/* Solution: Proper min-height */
.mobile-tabs {
  min-height: calc(100vh - 60px);
}
```

### Issue: Button Focus Ring Cut Off

```css
/* Solution: Add focus-visible outline */
.button:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}
```

### Issue: Text Overflow

```css
/* Solution: Proper text truncation */
.truncate-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

---

**Quick Start:** `npm run ctx ui` to load this context for UI component development.
