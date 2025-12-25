import { Challenge, Track } from "@/lib/types/challenge";

// Web Development Track Challenges
export const webTrackChallenges: Challenge[] = [
  {
    id: "web-001",
    trackId: "web",
    title: "Profile Card Component",
    description: `Build a visually appealing profile card component that displays user information in a clean, modern design. This challenge will test your HTML structure, CSS styling, and layout skills.

The card should showcase a user's avatar, name, title, and social links with proper spacing, typography, and visual hierarchy.`,
    difficulty: "beginner",
    order: 1,
    modelTier: "local",
    points: 100,
    estimatedTime: 20,
    tags: ["html", "css", "layout", "styling"],
    requirements: [
      {
        id: "req1",
        text: "Display a circular avatar image (use placeholder)",
        points: 20,
        completed: false,
      },
      {
        id: "req2",
        text: "Show user name in bold, title below in muted color",
        points: 20,
        completed: false,
      },
      {
        id: "req3",
        text: "Include at least 3 social media icon links",
        points: 20,
        completed: false,
      },
      {
        id: "req4",
        text: "Card has subtle shadow and rounded corners",
        points: 20,
        completed: false,
      },
      {
        id: "req5",
        text: "Card is horizontally centered on page",
        points: 20,
        completed: false,
      },
    ],
    constraints: [
      {
        id: "con1",
        text: "Must use semantic HTML (article, heading tags)",
        type: "accessibility",
      },
      {
        id: "con2",
        text: "Images must have alt text",
        type: "accessibility",
      },
      {
        id: "con3",
        text: "No external CSS frameworks (vanilla CSS only)",
        type: "technical",
      },
    ],
    testConfig: {
      type: "playwright",
      timeout: 30000,
      tests: [
        {
          id: "test1",
          name: "Profile Card Structure",
          description: "Checks for proper HTML structure",
          selector: "article",
          assertion: "should have article element",
          points: 20,
        },
        {
          id: "test2",
          name: "Avatar Image",
          description: "Verifies avatar image is present and circular",
          selector: "img",
          assertion: "should have circular avatar image",
          points: 20,
        },
        {
          id: "test3",
          name: "Typography",
          description: "Checks name and title styling",
          selector: "h1, h2",
          assertion: "should have proper heading hierarchy",
          points: 20,
        },
        {
          id: "test4",
          name: "Social Links",
          description: "Verifies social media links",
          selector: "a",
          assertion: "should have at least 3 social links",
          points: 20,
        },
        {
          id: "test5",
          name: "Card Styling",
          description: "Checks for shadow and centering",
          selector: ".card",
          assertion: "should have shadow and be centered",
          points: 20,
        },
      ],
    },
    hints: [
      {
        id: "hint1",
        level: 1,
        text: "Start with a semantic HTML structure using <article> for the card container. Use heading tags (h1, h2) for the name and title.",
      },
      {
        id: "hint2",
        level: 2,
        text: "Use CSS Flexbox or Grid to center the card on the page. Apply border-radius: 50% to make the avatar circular.",
      },
      {
        id: "hint3",
        level: 3,
        text: "Use box-shadow property for the card effect (try: box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1)). Center the card with margin: 0 auto and max-width.",
      },
    ],
    isRedTeam: false,
    starterCode: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile Card</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            max-width: 300px;
            text-align: center;
        }
        
        .avatar {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 1rem;
        }
        
        /* Add your styles here */
    </style>
</head>
<body>
    <article class="card">
        <img src="https://via.placeholder.com/100" alt="Profile picture" class="avatar">
        <h1>Your Name</h1>
        <p>Your Title</p>
        <!-- Add social links here -->
    </article>
</body>
</html>`,
    resources: [
      {
        id: "res1",
        type: "documentation",
        title: "HTML Semantic Elements",
        description: "Learn about article, header, section tags",
        url: "https://developer.mozilla.org/en-US/docs/Web/HTML/Element",
      },
      {
        id: "res2",
        type: "documentation",
        title: "CSS Flexbox Guide",
        description: "Complete guide to flexbox centering",
        url: "https://css-tricks.com/snippets/css/a-guide-to-flexbox/",
      },
      {
        id: "res3",
        type: "documentation",
        title: "CSS Box Shadow",
        description: "Creating beautiful shadows",
        url: "https://developer.mozilla.org/en-US/docs/Web/CSS/box-shadow",
      },
    ],
  },
  {
    id: "web-002",
    trackId: "web",
    title: "Responsive Navigation Bar",
    description: `Create a responsive navigation bar that works seamlessly across desktop and mobile devices. This challenge focuses on responsive design, CSS media queries, and JavaScript interactions.

Build a navigation that transforms from a horizontal menu on desktop to a hamburger menu on mobile, with smooth animations and accessibility features.`,
    difficulty: "beginner",
    order: 2,
    modelTier: "local",
    points: 150,
    estimatedTime: 35,
    tags: ["html", "css", "javascript", "responsive", "navigation"],
    requirements: [
      {
        id: "req1",
        text: "Horizontal navigation menu on desktop (>768px)",
        points: 25,
        completed: false,
      },
      {
        id: "req2",
        text: "Hamburger menu on mobile (<768px)",
        points: 25,
        completed: false,
      },
      {
        id: "req3",
        text: "Smooth toggle animation for mobile menu",
        points: 25,
        completed: false,
      },
      {
        id: "req4",
        text: "Logo/brand name on the left side",
        points: 25,
        completed: false,
      },
      {
        id: "req5",
        text: "At least 4 navigation links",
        points: 25,
        completed: false,
      },
      {
        id: "req6",
        text: "Active/hover states for all links",
        points: 25,
        completed: false,
      },
    ],
    constraints: [
      {
        id: "con1",
        text: "Must be keyboard navigable",
        type: "accessibility",
      },
      {
        id: "con2",
        text: "Hamburger button must have aria-label",
        type: "accessibility",
      },
      {
        id: "con3",
        text: "Mobile menu should close when clicking outside",
        type: "technical",
      },
    ],
    testConfig: {
      type: "playwright",
      timeout: 30000,
      tests: [
        {
          id: "test1",
          name: "Desktop Navigation",
          description: "Checks horizontal menu on desktop",
          selector: "nav",
          assertion: "should show horizontal menu on desktop",
          points: 25,
        },
        {
          id: "test2",
          name: "Mobile Hamburger",
          description: "Verifies hamburger menu on mobile",
          selector: ".hamburger",
          assertion: "should show hamburger on mobile",
          points: 25,
        },
        {
          id: "test3",
          name: "Menu Toggle",
          description: "Tests mobile menu toggle functionality",
          selector: ".mobile-menu",
          assertion: "should toggle mobile menu",
          points: 25,
        },
        {
          id: "test4",
          name: "Navigation Links",
          description: "Verifies presence of navigation links",
          selector: "nav a",
          assertion: "should have at least 4 nav links",
          points: 25,
        },
        {
          id: "test5",
          name: "Responsive Behavior",
          description: "Tests responsive breakpoints",
          selector: "nav",
          assertion: "should respond to screen size changes",
          points: 25,
        },
        {
          id: "test6",
          name: "Accessibility",
          description: "Checks keyboard navigation and ARIA labels",
          selector: "button[aria-label]",
          assertion: "should have proper accessibility attributes",
          points: 25,
        },
      ],
    },
    hints: [
      {
        id: "hint1",
        level: 1,
        text: "Use CSS media queries (@media) to show/hide different menu styles. Start with desktop-first or mobile-first approach.",
      },
      {
        id: "hint2",
        level: 2,
        text: "Create a hamburger icon with three div elements or CSS pseudo-elements. Use JavaScript to toggle a class that shows/hides the mobile menu.",
      },
      {
        id: "hint3",
        level: 3,
        text: "Use CSS transforms (translateX) for smooth slide animations. Add event listeners for clicks outside the menu to close it automatically.",
      },
    ],
    isRedTeam: false,
    starterCode: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Responsive Navigation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f8f9fa;
        }
        
        nav {
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1rem 2rem;
        }
        
        /* Add your styles here */
        
        @media (max-width: 768px) {
            /* Mobile styles */
        }
    </style>
</head>
<body>
    <nav>
        <div class="nav-container">
            <div class="logo">
                <h2>Brand</h2>
            </div>
            
            <!-- Desktop Menu -->
            <ul class="nav-menu">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
            
            <!-- Mobile Hamburger -->
            <button class="hamburger" aria-label="Toggle navigation menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <main>
        <div style="padding: 2rem; text-align: center;">
            <h1>Responsive Navigation Demo</h1>
            <p>Resize your browser window to see the navigation adapt!</p>
        </div>
    </main>

    <script>
        // Add your JavaScript here
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        hamburger.addEventListener('click', () => {
            // Toggle mobile menu
        });
    </script>
</body>
</html>`,
    resources: [
      {
        id: "res1",
        type: "documentation",
        title: "CSS Media Queries",
        description: "Guide to responsive design with media queries",
        url: "https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries",
      },
      {
        id: "res2",
        type: "documentation",
        title: "CSS Transforms",
        description: "Using CSS transforms for animations",
        url: "https://developer.mozilla.org/en-US/docs/Web/CSS/transform",
      },
      {
        id: "res3",
        type: "video",
        title: "Building Responsive Navigation",
        description: "Step-by-step responsive navigation tutorial",
        url: "#",
        duration: 720,
      },
    ],
  },
];

// Web Development Track
export const webTrack: Track = {
  id: "web",
  name: "Web Development",
  description:
    "Master modern web development with HTML, CSS, JavaScript, and frameworks. Build real-world projects from static pages to dynamic web applications.",
  icon: "🌐",
  color: "blue",
  order: 1,
  challenges: webTrackChallenges,
  totalChallenges: webTrackChallenges.length,
  totalPoints: webTrackChallenges.reduce(
    (sum, challenge) => sum + challenge.points,
    0
  ),
};

// Data Analysis Track Challenges
export const dataTrackChallenges: Challenge[] = [
  {
    id: "data-001",
    trackId: "data",
    title: "Data Analysis Fundamentals",
    description: `Learn to analyze datasets using pandas. Extract insights from CSV data, perform basic statistics, and create visualizations. Practice WeaktoStrong methodology by starting with simple analysis before complex modeling.`,
    difficulty: "beginner",
    order: 1,
    modelTier: "local",
    points: 100,
    estimatedTime: 30,
    tags: ["pandas", "data-analysis", "python"],
    requirements: [
      {
        id: "req1",
        text: "Calculate total revenue from sales data",
        points: 25,
        completed: false,
      },
      {
        id: "req2",
        text: "Find best selling product",
        points: 25,
        completed: false,
      },
      {
        id: "req3",
        text: "Calculate average order value",
        points: 25,
        completed: false,
      },
      {
        id: "req4",
        text: "Create summary analysis",
        points: 25,
        completed: false,
      },
    ],
    constraints: [
      {
        id: "con1",
        text: "Must use pandas for data manipulation",
        type: "technical",
      },
      {
        id: "con2",
        text: "Results must be stored in variables",
        type: "technical",
      },
    ],
    testConfig: {
      type: "pytest",
      timeout: 30000,
      tests: [
        {
          id: "test1",
          name: "Total Revenue",
          description: "Checks if total_revenue variable exists",
          assertion: "variable 'total_revenue' should exist",
          points: 25,
        },
        {
          id: "test2",
          name: "Best Product",
          description: "Checks if best_selling_product variable exists",
          assertion: "variable 'best_selling_product' should exist",
          points: 25,
        },
        {
          id: "test3",
          name: "Average Order",
          description: "Checks if avg_order_value variable exists",
          assertion: "variable 'avg_order_value' should exist",
          points: 25,
        },
        {
          id: "test4",
          name: "Summary Data",
          description: "Checks if result_summary variable exists",
          assertion: "variable 'result_summary' should exist",
          points: 25,
        },
      ],
    },
    hints: [
      {
        id: "hint1",
        level: 1,
        text: "The dataset 'df' is already loaded for you. Use df['column_name'] to access columns.",
      },
      {
        id: "hint2",
        level: 2,
        text: "Calculate revenue by multiplying quantity and price columns: df['revenue'] = df['quantity'] * df['price']",
      },
      {
        id: "hint3",
        level: 3,
        text: "Use df.groupby('product_name')['quantity'].sum() to find product sales, then .idxmax() to get the best seller.",
      },
    ],
    isRedTeam: false,
    starterCode: `# WeaktoStrong Data Analysis Challenge 1: Fundamentals\n\n# The dataset 'df' is already loaded for you\n# Columns: product_name, quantity, price, sale_date\n\n# TODO 1: Calculate total revenue\n# Hint: revenue = quantity * price\n\n# TODO 2: Find the product with highest total sales\n# Hint: Group by product_name and sum quantities  \n\n# TODO 3: Calculate average order value\n\n# TODO 4: Create a summary with your findings\n\nprint("Analysis complete!")`,
    resources: [
      {
        id: "res1",
        type: "documentation",
        title: "Pandas Documentation",
        description: "Official pandas library documentation",
        url: "https://pandas.pydata.org/docs/",
      },
      {
        id: "res2",
        type: "documentation",
        title: "Data Analysis with Python",
        description: "Guide to data analysis techniques",
        url: "https://www.python.org/about/success/dabeaz/",
      },
    ],
  },
];

// Data Analysis Track
export const dataTrack: Track = {
  id: "data",
  name: "Data Analysis",
  description:
    "Master data analysis with Python, pandas, and machine learning. Build insights from real datasets using WeaktoStrong methodology.",
  icon: "📊",
  color: "green",
  order: 2,
  challenges: dataTrackChallenges,
  totalChallenges: dataTrackChallenges.length,
  totalPoints: dataTrackChallenges.reduce(
    (sum, challenge) => sum + challenge.points,
    0
  ),
};

// All tracks
export const tracks: Track[] = [webTrack, dataTrack];

// Helper functions
export function getChallengeById(challengeId: string): Challenge | undefined {
  for (const track of tracks) {
    const challenge = track.challenges.find((c) => c.id === challengeId);
    if (challenge) return challenge;
  }
  return undefined;
}

export function getTrackByChallenge(challengeId: string): Track | undefined {
  for (const track of tracks) {
    const challenge = track.challenges.find((c) => c.id === challengeId);
    if (challenge) return track;
  }
  return undefined;
}

export function getTrackById(trackId: string): Track | undefined {
  return tracks.find((t) => t.id === trackId);
}

export function getChallengesByDifficulty(
  difficulty: Challenge["difficulty"]
): Challenge[] {
  return tracks.flatMap((track) =>
    track.challenges.filter((challenge) => challenge.difficulty === difficulty)
  );
}

export function getChallengesByTrack(trackId: string): Challenge[] {
  const track = getTrackById(trackId);
  return track ? track.challenges : [];
}
