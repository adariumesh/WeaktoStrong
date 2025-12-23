#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");
const cheerio = require("cheerio");

/**
 * Main test runner for web development challenges
 * Executes HTML/CSS/JavaScript in a secure sandbox environment
 */
class WebTestRunner {
  constructor() {
    this.browser = null;
    this.page = null;
    this.timeout = 30000; // 30 second timeout
  }

  async initialize() {
    console.log("🚀 Initializing Web Test Runner...");

    this.browser = await chromium.launch({
      headless: true,
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-accelerated-2d-canvas",
        "--disable-gpu",
        "--window-size=1280,720",
      ],
    });

    this.page = await this.browser.newPage();

    // Set viewport for consistent testing
    await this.page.setViewportSize({ width: 1280, height: 720 });

    console.log("✅ Browser initialized");
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close();
      console.log("🧹 Browser cleaned up");
    }
  }

  async runTests(userCode, testConfig) {
    try {
      console.log("📋 Starting test execution...");

      const results = {
        success: false,
        score: 0,
        maxScore: 0,
        tests: [],
        errors: [],
        metrics: {},
        timestamp: new Date().toISOString(),
      };

      // Validate HTML structure
      const htmlResults = await this.validateHTML(userCode);
      results.tests.push(...htmlResults.tests);
      results.errors.push(...htmlResults.errors);

      // Test CSS styling
      const cssResults = await this.validateCSS(userCode);
      results.tests.push(...cssResults.tests);
      results.errors.push(...cssResults.errors);

      // Test responsive design
      const responsiveResults = await this.testResponsive(userCode);
      results.tests.push(...responsiveResults.tests);

      // Test accessibility
      const a11yResults = await this.testAccessibility(userCode);
      results.tests.push(...a11yResults.tests);

      // Calculate final score
      const passedTests = results.tests.filter((t) => t.passed).length;
      results.maxScore = results.tests.length;
      results.score = passedTests;
      results.success = passedTests === results.maxScore;

      // Get performance metrics
      results.metrics = await this.getMetrics();

      console.log(
        `📊 Tests completed: ${passedTests}/${results.maxScore} passed`
      );
      return results;
    } catch (error) {
      console.error("❌ Test execution failed:", error.message);
      return {
        success: false,
        score: 0,
        maxScore: 0,
        tests: [],
        errors: [
          { message: `Test runner error: ${error.message}`, type: "system" },
        ],
        metrics: {},
        timestamp: new Date().toISOString(),
      };
    }
  }

  async validateHTML(userCode) {
    console.log("🔍 Validating HTML structure...");

    const tests = [];
    const errors = [];

    try {
      // Load HTML into page
      await this.page.setContent(userCode);
      await this.page.waitForLoadState("networkidle", { timeout: 5000 });

      // Check basic HTML structure
      const hasDoctype = userCode
        .trim()
        .toLowerCase()
        .startsWith("<!doctype html>");
      tests.push({
        name: "HTML5 Doctype",
        description: "Document should start with <!DOCTYPE html>",
        passed: hasDoctype,
        points: 1,
      });

      // Check for required elements
      const hasTitle = (await this.page.locator("title").count()) > 0;
      tests.push({
        name: "Page Title",
        description: "Document should have a <title> element",
        passed: hasTitle,
        points: 1,
      });

      const hasViewport =
        (await this.page.locator('meta[name="viewport"]').count()) > 0;
      tests.push({
        name: "Viewport Meta Tag",
        description:
          "Document should include viewport meta tag for responsive design",
        passed: hasViewport,
        points: 1,
      });

      // Check semantic HTML
      const semanticElements = await this.page
        .locator("header, main, section, article, nav, aside, footer")
        .count();
      tests.push({
        name: "Semantic HTML",
        description: "Document should use semantic HTML5 elements",
        passed: semanticElements > 0,
        points: 2,
      });
    } catch (error) {
      errors.push({
        message: `HTML validation error: ${error.message}`,
        type: "html",
      });
    }

    return { tests, errors };
  }

  async validateCSS(userCode) {
    console.log("🎨 Validating CSS styling...");

    const tests = [];
    const errors = [];

    try {
      // Check if CSS is present
      const hasStyleTag =
        userCode.includes("<style>") || userCode.includes("style=");
      const hasExternalCSS =
        userCode.includes("<link") && userCode.includes("stylesheet");

      tests.push({
        name: "CSS Present",
        description: "Document should include CSS styling",
        passed: hasStyleTag || hasExternalCSS,
        points: 1,
      });

      if (hasStyleTag || hasExternalCSS) {
        // Test color usage
        const styles = await this.page.evaluate(() => {
          const computedStyles = [];
          const elements = document.querySelectorAll("*");
          for (let elem of elements) {
            const style = window.getComputedStyle(elem);
            computedStyles.push({
              backgroundColor: style.backgroundColor,
              color: style.color,
              fontSize: style.fontSize,
              display: style.display,
            });
          }
          return computedStyles;
        });

        const hasCustomColors = styles.some(
          (s) =>
            s.backgroundColor !== "rgba(0, 0, 0, 0)" ||
            s.color !== "rgb(0, 0, 0)"
        );

        tests.push({
          name: "Custom Colors",
          description: "CSS should include custom colors",
          passed: hasCustomColors,
          points: 1,
        });
      }
    } catch (error) {
      errors.push({
        message: `CSS validation error: ${error.message}`,
        type: "css",
      });
    }

    return { tests, errors };
  }

  async testResponsive(userCode) {
    console.log("📱 Testing responsive design...");

    const tests = [];
    const viewports = [
      { name: "Mobile", width: 375, height: 667 },
      { name: "Tablet", width: 768, height: 1024 },
      { name: "Desktop", width: 1280, height: 720 },
    ];

    try {
      for (const viewport of viewports) {
        await this.page.setViewportSize({
          width: viewport.width,
          height: viewport.height,
        });
        await this.page.setContent(userCode);

        // Check if layout adapts to viewport
        const bodyWidth = await this.page.evaluate(
          () => document.body.scrollWidth
        );
        const fitsViewport = bodyWidth <= viewport.width + 50; // 50px tolerance

        tests.push({
          name: `${viewport.name} Layout`,
          description: `Layout should adapt to ${viewport.name.toLowerCase()} viewport`,
          passed: fitsViewport,
          points: 1,
        });
      }
    } catch (error) {
      tests.push({
        name: "Responsive Design",
        description: "Layout should be responsive",
        passed: false,
        points: 0,
        error: error.message,
      });
    }

    return { tests, errors: [] };
  }

  async testAccessibility(userCode) {
    console.log("♿ Testing accessibility...");

    const tests = [];

    try {
      await this.page.setContent(userCode);

      // Check for alt text on images
      const images = await this.page.locator("img").count();
      const imagesWithAlt = await this.page.locator("img[alt]").count();

      if (images > 0) {
        tests.push({
          name: "Image Alt Text",
          description: "All images should have alt text",
          passed: imagesWithAlt === images,
          points: 1,
        });
      }

      // Check heading structure
      const headings = await this.page
        .locator("h1, h2, h3, h4, h5, h6")
        .count();
      tests.push({
        name: "Heading Structure",
        description: "Document should use heading elements for structure",
        passed: headings > 0,
        points: 1,
      });

      // Check form labels
      const formInputs = await this.page
        .locator("input, select, textarea")
        .count();
      const labelsOrAriaLabels = await this.page
        .locator(
          "input[aria-label], select[aria-label], textarea[aria-label], label"
        )
        .count();

      if (formInputs > 0) {
        tests.push({
          name: "Form Labels",
          description: "Form inputs should have associated labels",
          passed: labelsOrAriaLabels >= formInputs,
          points: 1,
        });
      }
    } catch (error) {
      tests.push({
        name: "Accessibility",
        description: "Basic accessibility checks",
        passed: false,
        points: 0,
        error: error.message,
      });
    }

    return { tests, errors: [] };
  }

  async getMetrics() {
    try {
      const metrics = await this.page.evaluate(() => {
        return {
          loadTime: performance.now(),
          elements: document.querySelectorAll("*").length,
          scripts: document.scripts.length,
          stylesheets: document.styleSheets.length,
        };
      });
      return metrics;
    } catch (error) {
      return {};
    }
  }
}

// CLI execution
async function main() {
  const runner = new WebTestRunner();

  try {
    await runner.initialize();

    // Read user code from stdin or file
    const userCode = process.argv[2]
      ? fs.readFileSync(process.argv[2], "utf8")
      : await new Promise((resolve) => {
          let data = "";
          process.stdin.on("data", (chunk) => (data += chunk));
          process.stdin.on("end", () => resolve(data));
        });

    const results = await runner.runTests(userCode, {});

    // Output results as JSON
    console.log("📄 Test Results:");
    console.log(JSON.stringify(results, null, 2));

    // Exit with appropriate code
    process.exit(results.success ? 0 : 1);
  } catch (error) {
    console.error("💥 Fatal error:", error);
    process.exit(1);
  } finally {
    await runner.cleanup();
  }
}

if (require.main === module) {
  main();
}

module.exports = { WebTestRunner };
