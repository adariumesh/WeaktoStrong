# WEAK-TO-STRONG: Challenge Content Specifications

> Detailed specs for the first 15 Web Track challenges. Use this to seed the database.
>
> **📁 Part of context package.** Load with CLAUDE_MEMORY.md during Phase 3, Chunk 3.4.
> Schema defined in CLAUDE_MEMORY.md. Implementation steps in DEVELOPMENT_PLAN.md.
>
> **⏳ Status:** Phase 3 content - Not yet implemented. Authentication system (Phase 1) complete.

---

## CHALLENGE STRUCTURE REMINDER

```json
{
  "id": "uuid",
  "track_id": "web-track-uuid",
  "title": "string",
  "description": "markdown",
  "difficulty": "beginner|intermediate|advanced",
  "order": 1,
  "model_tier": "local|haiku|sonnet",
  "points": 100,
  "estimated_time_minutes": 30,
  "requirements": [{ "id": "req1", "text": "...", "points": 20 }],
  "constraints": [
    {
      "id": "con1",
      "text": "...",
      "type": "accessibility|performance|security"
    }
  ],
  "test_config": {
    "type": "playwright",
    "timeout": 30000,
    "file": "tests/challenge-01.spec.ts"
  },
  "hints": ["hint1", "hint2", "hint3"],
  "is_red_team": false,
  "reference_solution": "code string"
}
```

---

## WEB TRACK CHALLENGES

### Challenge 1: Profile Card

**Difficulty:** beginner | **Model Tier:** local | **Points:** 100 | **Time:** 20 min

**Description:**

```markdown
Build a profile card component showing a user's avatar, name, title, and social links.

The card should be visually appealing and centered on the page.
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Display a circular avatar image (use placeholder) | 20 |
| req2 | Show user name in bold, title below in muted color | 20 |
| req3 | Include at least 3 social media icon links | 20 |
| req4 | Card has subtle shadow and rounded corners | 20 |
| req5 | Card is horizontally centered on page | 20 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | Must use semantic HTML (article, heading tags) | accessibility |
| con2 | Images must have alt text | accessibility |
| con3 | No external CSS frameworks (vanilla CSS only) | technical |

**Hints:**

1. "Think about flexbox or grid for centering. What CSS property centers a block element horizontally?"
2. "For the circular avatar, you'll need `border-radius: 50%`. The card container needs `display: flex` with `flex-direction: column`."
3. "`css\n.card {\n  max-width: 300px;\n  margin: 0 auto;\n  padding: 2rem;\n  border-radius: 12px;\n  box-shadow: 0 4px 6px rgba(0,0,0,0.1);\n  text-align: center;\n}\n.avatar {\n  width: 100px;\n  height: 100px;\n  border-radius: 50%;\n  object-fit: cover;\n}\n`"

**Test Config:**

```javascript
// tests/challenge-01.spec.ts
test("profile card displays correctly", async ({ page }) => {
  await page.goto("/");

  // Check avatar
  const avatar = page.locator("img");
  await expect(avatar).toBeVisible();
  await expect(avatar).toHaveAttribute("alt");

  // Check name and title
  await expect(page.locator("h1, h2, h3")).toBeVisible();

  // Check social links
  const links = page.locator("a");
  await expect(links).toHaveCount({ minimum: 3 });

  // Check centering (card should be in center of viewport)
  const card = page.locator('article, .card, [class*="card"]');
  const box = await card.boundingBox();
  const viewport = page.viewportSize();
  const centerX = viewport.width / 2;
  const cardCenterX = box.x + box.width / 2;
  expect(Math.abs(centerX - cardCenterX)).toBeLessThan(50);
});
```

---

### Challenge 2: Responsive Navigation Bar

**Difficulty:** beginner | **Model Tier:** local | **Points:** 100 | **Time:** 25 min

**Description:**

```markdown
Create a responsive navigation bar with a logo, menu items, and a mobile hamburger menu.

Desktop: Logo on left, horizontal menu on right.
Mobile: Logo centered, hamburger icon that reveals menu.
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Logo/brand name on the left (desktop) or centered (mobile) | 15 |
| req2 | At least 4 navigation links | 15 |
| req3 | Hamburger menu icon visible on screens < 768px | 20 |
| req4 | Clicking hamburger toggles mobile menu visibility | 25 |
| req5 | Smooth transition when menu opens/closes | 10 |
| req6 | Active link has visual indicator | 15 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | Navigation must be keyboard accessible | accessibility |
| con2 | Use semantic nav element | accessibility |
| con3 | No JavaScript frameworks (vanilla JS only) | technical |

**Hints:**

1. "Media queries let you change styles at different screen widths. What breakpoint makes sense for mobile?"
2. "The hamburger menu needs a click event listener that toggles a class. `element.classList.toggle('active')` is your friend."
3. "`javascript\nconst hamburger = document.querySelector('.hamburger');\nconst menu = document.querySelector('.nav-menu');\nhamburger.addEventListener('click', () => {\n  menu.classList.toggle('active');\n});\n`\n\n`css\n@media (max-width: 768px) {\n  .nav-menu { display: none; }\n  .nav-menu.active { display: flex; flex-direction: column; }\n  .hamburger { display: block; }\n}\n`"

**Test Config:**

```javascript
// tests/challenge-02.spec.ts
test("responsive navigation works", async ({ page }) => {
  // Desktop test
  await page.setViewportSize({ width: 1024, height: 768 });
  await page.goto("/");

  const nav = page.locator("nav");
  await expect(nav).toBeVisible();

  const links = nav.locator("a");
  await expect(links).toHaveCount({ minimum: 4 });

  // Mobile test
  await page.setViewportSize({ width: 375, height: 667 });

  const hamburger = page.locator(
    '.hamburger, [class*="hamburger"], button[aria-label*="menu"]'
  );
  await expect(hamburger).toBeVisible();

  // Menu should be hidden initially
  const menu = page.locator('.nav-menu, [class*="menu"]');
  await expect(menu).not.toBeVisible();

  // Click hamburger, menu should appear
  await hamburger.click();
  await expect(menu).toBeVisible();
});
```

---

### Challenge 3: Pricing Table

**Difficulty:** beginner | **Model Tier:** local | **Points:** 100 | **Time:** 30 min

**Description:**

```markdown
Build a pricing table with 3 tiers: Basic, Pro, and Enterprise.

Each tier shows: name, price, feature list, and CTA button.
The "Pro" tier should be visually highlighted as recommended.
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Three pricing cards side by side (stacked on mobile) | 20 |
| req2 | Each card has: tier name, price, 4+ features, CTA button | 25 |
| req3 | Pro/middle tier visually highlighted (different color, badge, or scale) | 20 |
| req4 | CTA buttons have hover effects | 15 |
| req5 | Responsive: cards stack vertically on mobile | 20 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | Price must be readable by screen readers (use proper markup) | accessibility |
| con2 | Feature lists use semantic ul/li elements | accessibility |

**Hints:**

1. "CSS Grid or Flexbox can create the three-column layout. Which one feels more natural for equal-width columns?"
2. "To highlight the Pro card, you can: increase its size with `transform: scale(1.05)`, add a colored border, or use a 'Recommended' badge positioned absolutely."
3. "`css\n.pricing-container {\n  display: grid;\n  grid-template-columns: repeat(3, 1fr);\n  gap: 2rem;\n}\n.card.featured {\n  transform: scale(1.05);\n  border: 2px solid #6366f1;\n  position: relative;\n}\n.card.featured::before {\n  content: 'Recommended';\n  position: absolute;\n  top: -12px;\n  left: 50%;\n  transform: translateX(-50%);\n  background: #6366f1;\n  color: white;\n  padding: 4px 12px;\n  border-radius: 12px;\n  font-size: 12px;\n}\n@media (max-width: 768px) {\n  .pricing-container { grid-template-columns: 1fr; }\n}\n`"

---

### Challenge 4: Hero Section with CTA

**Difficulty:** beginner | **Model Tier:** local | **Points:** 100 | **Time:** 25 min

**Description:**

```markdown
Create a hero section for a landing page with:

- Large headline
- Subheadline/description
- Primary and secondary CTA buttons
- Background image or gradient
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Full-width hero section with background | 20 |
| req2 | Prominent headline (h1) with clear hierarchy | 20 |
| req3 | Supporting text paragraph | 15 |
| req4 | Primary CTA button (filled, contrasting color) | 20 |
| req5 | Secondary CTA button (outlined or ghost style) | 15 |
| req6 | Content vertically centered in hero | 10 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | Text must be readable over background (contrast ratio 4.5:1+) | accessibility |
| con2 | Hero height at least 60vh | design |

**Hints:**

1. "For background images, `background-size: cover` ensures the image fills the space. You may need a dark overlay to make text readable."
2. "Flexbox with `justify-content: center` and `align-items: center` on a container with `min-height: 60vh` handles vertical centering."
3. "`css\n.hero {\n  min-height: 60vh;\n  background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('hero-bg.jpg');\n  background-size: cover;\n  display: flex;\n  flex-direction: column;\n  justify-content: center;\n  align-items: center;\n  text-align: center;\n  color: white;\n}\n.btn-primary {\n  background: #6366f1;\n  color: white;\n  padding: 12px 24px;\n  border-radius: 8px;\n}\n.btn-secondary {\n  background: transparent;\n  border: 2px solid white;\n  color: white;\n}\n`"

---

### Challenge 5: Accessibility Audit (RED TEAM)

**Difficulty:** beginner | **Model Tier:** local | **Points:** 150 | **Time:** 30 min
**is_red_team:** true

**Description:**

```markdown
🔴 **RED TEAM CHECKPOINT**

You're given AI-generated code for a contact form. It works visually, but has accessibility issues.

**Your mission:**

1. Identify at least 3 accessibility violations
2. Explain why each is a problem
3. Fix all issues in the code
```

**Provided Code:**

```html
<div class="form">
  <div class="title">Contact Us</div>
  <input placeholder="Your name" />
  <input placeholder="Email" />
  <div class="area" contenteditable="true">Message...</div>
  <div class="btn" onclick="submit()">Send</div>
</div>
<style>
  .btn {
    background: #ccc;
    color: #999;
    padding: 10px;
    cursor: pointer;
  }
</style>
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Use semantic form element with proper submission | 30 |
| req2 | All inputs have associated labels (visible or sr-only) | 30 |
| req3 | Use proper input types (email, textarea) | 20 |
| req4 | Button is actual button element with sufficient color contrast | 30 |
| req5 | Form has clear focus indicators | 20 |
| req6 | Error messages are announced to screen readers | 20 |

**Hints:**

1. "Look at the HTML elements used. Are they semantic? What should a 'button' actually be? What about that contenteditable div?"
2. "Form inputs need labels. The `placeholder` attribute is NOT a substitute for a `<label>`. Also check: is the button color contrast sufficient for readability?"
3. "Key fixes needed:\n- `<div class='form'>` → `<form>`\n- Add `<label for='name'>` for each input\n- `contenteditable div` → `<textarea>`\n- `<div class='btn'>` → `<button type='submit'>`\n- Button needs contrast ratio 4.5:1 minimum"

---

### Challenge 6: Form Validation with Error Messages

**Difficulty:** intermediate | **Model Tier:** local | **Points:** 100 | **Time:** 35 min

**Description:**

```markdown
Build a signup form with real-time validation:

- Email field (valid format)
- Password field (8+ chars, 1 uppercase, 1 number)
- Confirm password (must match)
- Show/hide password toggle
- Clear error messages for each validation rule
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Email validates on blur with regex pattern | 20 |
| req2 | Password shows strength requirements, updates in real-time | 25 |
| req3 | Confirm password shows match/mismatch status | 20 |
| req4 | Show/hide password toggle works for both fields | 15 |
| req5 | Submit disabled until all validations pass | 10 |
| req6 | Error messages are specific and helpful | 10 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | No form submission on invalid data | security |
| con2 | Error messages associated with inputs via aria-describedby | accessibility |

---

### Challenge 7: Interactive Accordion Component

**Difficulty:** intermediate | **Model Tier:** local | **Points:** 100 | **Time:** 30 min

**Description:**

```markdown
Create an FAQ accordion where:

- Clicking a question reveals its answer
- Only one answer visible at a time (optional: allow multiple)
- Smooth expand/collapse animation
- Arrow icon rotates when expanded
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | At least 4 accordion items | 15 |
| req2 | Clicking header toggles content visibility | 25 |
| req3 | Only one item open at a time | 20 |
| req4 | Smooth height transition animation | 20 |
| req5 | Visual indicator (arrow/icon) shows open/closed state | 10 |
| req6 | Keyboard accessible (Enter/Space to toggle) | 10 |

---

### Challenge 8: Modal Popup with Keyboard Navigation

**Difficulty:** intermediate | **Model Tier:** local | **Points:** 100 | **Time:** 35 min

**Description:**

```markdown
Build an accessible modal dialog that:

- Opens on button click
- Closes on Escape key, outside click, or close button
- Traps focus inside modal when open
- Returns focus to trigger button when closed
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Modal opens centered with backdrop overlay | 20 |
| req2 | Close on: X button, Escape key, backdrop click | 25 |
| req3 | Focus trapped inside modal (Tab cycles through modal elements only) | 25 |
| req4 | Focus returns to trigger button after close | 15 |
| req5 | Body scroll locked when modal is open | 15 |

**Constraints:**
| ID | Text | Type |
|----|------|------|
| con1 | Must use role="dialog" and aria-modal="true" | accessibility |
| con2 | Modal must have accessible name (aria-labelledby) | accessibility |

---

### Challenge 9: Dark Mode Toggle with LocalStorage

**Difficulty:** intermediate | **Model Tier:** local | **Points:** 100 | **Time:** 30 min

**Description:**

```markdown
Implement a dark mode toggle that:

- Switches between light and dark themes
- Persists preference in localStorage
- Respects system preference on first visit
- Smooth transition between themes
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Toggle button switches between light/dark themes | 25 |
| req2 | Theme preference saved to localStorage | 20 |
| req3 | On load, check localStorage first, then system preference | 25 |
| req4 | Smooth color transitions when toggling | 15 |
| req5 | Toggle icon/label reflects current state | 15 |

---

### Challenge 10: XSS Vulnerability Fix (RED TEAM)

**Difficulty:** intermediate | **Model Tier:** local | **Points:** 150 | **Time:** 35 min
**is_red_team:** true

**Description:**

```markdown
🔴 **RED TEAM CHECKPOINT**

You're given a comment system that's vulnerable to XSS attacks.

**Your mission:**

1. Identify the XSS vulnerability
2. Demonstrate how it could be exploited
3. Fix the code to prevent the attack
```

**Provided Code:**

```javascript
function addComment(text) {
  const commentDiv = document.createElement("div");
  commentDiv.innerHTML = text; // Dangerous!
  document.getElementById("comments").appendChild(commentDiv);
}

// Called when user submits
document.getElementById("submit").onclick = () => {
  const userInput = document.getElementById("comment-input").value;
  addComment(userInput);
};
```

**Requirements:**
| ID | Text | Points |
|----|------|--------|
| req1 | Identify innerHTML as the vulnerability source | 30 |
| req2 | Show exploit example: `<img src=x onerror="alert('XSS')">` | 30 |
| req3 | Fix: use textContent instead of innerHTML | 30 |
| req4 | Alternative fix: sanitize HTML with DOMPurify or similar | 30 |
| req5 | Explain why innerHTML is dangerous with user input | 30 |

---

### Challenge 11: React Card Component with Props

**Difficulty:** intermediate | **Model Tier:** haiku | **Points:** 100 | **Time:** 30 min

**Description:**

```markdown
Create a reusable React Card component that accepts props for:

- title, description, image, tags, and onClick handler
- Has a default state and loading skeleton
- Properly typed with TypeScript
```

_[Continue with similar detail for challenges 12-15...]_

---

## DATA TRACK CHALLENGES (Preview)

### Challenge D-1: Handle Missing Values

**Track:** Data | **Difficulty:** beginner | **Model Tier:** local

**Dataset:** `sales_data.csv` with intentional NaN values

**Requirements:**

1. Identify columns with missing values
2. Decide strategy per column (drop, fill with mean/median/mode, forward fill)
3. Justify each decision
4. Export cleaned dataset

---

## CLOUD TRACK CHALLENGES (Preview)

### Challenge C-1: Deploy Static Site to S3

**Track:** Cloud | **Difficulty:** beginner | **Model Tier:** local

**LocalStack Setup:**

- S3 bucket with static website hosting enabled

**Requirements:**

1. Create S3 bucket via AWS CLI (pointing to LocalStack)
2. Upload HTML/CSS files
3. Configure bucket for static website hosting
4. Access site via LocalStack URL

---

## NOTES FOR CLAUDE CODE

When seeding challenges:

1. Store challenge content as JSON in `backend/data/challenges/`
2. Create migration script to load challenges into database
3. Include test files in `backend/tests/challenges/`
4. Reference solutions stored separately (not exposed to users)
5. Hints should be stored as JSONB array in database
