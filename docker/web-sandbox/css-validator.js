#!/usr/bin/env node

const css = require("css-tree");
const cheerio = require("cheerio");

/**
 * CSS Validation Utilities
 * Validates CSS syntax, properties, and best practices
 */
class CSSValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
  }

  validate(htmlContent) {
    try {
      const $ = cheerio.load(htmlContent);

      // Extract CSS from style tags
      const styleTags = $("style");
      let cssContent = "";

      styleTags.each((i, style) => {
        cssContent += $(style).html() + "\n";
      });

      // Extract inline styles
      const inlineStyles = [];
      $("[style]").each((i, el) => {
        inlineStyles.push($(el).attr("style"));
      });

      if (cssContent.trim().length === 0 && inlineStyles.length === 0) {
        this.warnings.push("No CSS found in document");
        return {
          valid: true,
          errors: this.errors,
          warnings: this.warnings,
          score: 50, // Partial score for no CSS
        };
      }

      // Validate CSS syntax
      if (cssContent.trim().length > 0) {
        this.validateCSSSyntax(cssContent);
        this.validateCSSProperties(cssContent);
        this.checkBestPractices(cssContent);
      }

      // Validate inline styles
      if (inlineStyles.length > 0) {
        this.validateInlineStyles(inlineStyles);
      }

      return {
        valid: this.errors.length === 0,
        errors: this.errors,
        warnings: this.warnings,
        score: this.calculateScore(),
      };
    } catch (error) {
      this.errors.push(`CSS validation error: ${error.message}`);
      return {
        valid: false,
        errors: this.errors,
        warnings: this.warnings,
        score: 0,
      };
    }
  }

  validateCSSSyntax(cssContent) {
    try {
      const ast = css.parse(cssContent);

      // Check for parsing errors
      if (ast.children.isEmpty()) {
        this.warnings.push("CSS appears to be empty");
      }

      // Walk through the AST to find syntax issues
      css.walk(ast, (node) => {
        if (node.type === "Raw") {
          this.warnings.push("Potentially malformed CSS detected");
        }
      });
    } catch (parseError) {
      this.errors.push(`CSS syntax error: ${parseError.message}`);
    }
  }

  validateCSSProperties(cssContent) {
    try {
      const ast = css.parse(cssContent);

      // Common CSS properties to check
      const requiredProperties = [
        "color",
        "background-color",
        "font-size",
        "margin",
        "padding",
      ];
      const foundProperties = new Set();

      css.walk(ast, (node) => {
        if (node.type === "Declaration") {
          foundProperties.add(node.property);

          // Check for vendor prefixes without fallbacks
          if (
            node.property.startsWith("-webkit-") ||
            node.property.startsWith("-moz-") ||
            node.property.startsWith("-ms-")
          ) {
            const baseProperty = node.property.replace(/^-\w+-/, "");
            if (!foundProperties.has(baseProperty)) {
              this.warnings.push(
                `Vendor prefix ${node.property} used without fallback`
              );
            }
          }

          // Check for deprecated properties
          const deprecatedProperties = ["float", "clear"];
          if (deprecatedProperties.includes(node.property)) {
            this.warnings.push(
              `Consider using modern alternatives to ${node.property}`
            );
          }
        }
      });

      // Check if basic styling properties are used
      const basicStyling = ["color", "background-color", "font-size"].some(
        (prop) => foundProperties.has(prop)
      );

      if (!basicStyling) {
        this.warnings.push(
          "Consider adding basic styling (colors, fonts, etc.)"
        );
      }
    } catch (error) {
      this.errors.push(`Property validation error: ${error.message}`);
    }
  }

  checkBestPractices(cssContent) {
    try {
      const ast = css.parse(cssContent);

      // Check for overly specific selectors
      css.walk(ast, (node) => {
        if (node.type === "Rule") {
          node.prelude.children.forEach((selector) => {
            if (selector.type === "Selector") {
              const selectorText = css.generate(selector);

              // Count specificity indicators
              const idCount = (selectorText.match(/#/g) || []).length;
              const classCount = (selectorText.match(/\./g) || []).length;

              if (idCount > 2) {
                this.warnings.push(
                  `High specificity selector: ${selectorText}`
                );
              }

              if (selectorText.includes("!important")) {
                this.warnings.push(`Avoid !important in: ${selectorText}`);
              }
            }
          });
        }
      });

      // Check for responsive design indicators
      const hasMediaQueries = cssContent.includes("@media");
      const hasFlexbox =
        cssContent.includes("display: flex") ||
        cssContent.includes("display:flex");
      const hasGrid =
        cssContent.includes("display: grid") ||
        cssContent.includes("display:grid");

      if (!hasMediaQueries && !hasFlexbox && !hasGrid) {
        this.warnings.push(
          "Consider adding responsive design features (media queries, flexbox, or grid)"
        );
      }

      // Check for accessibility considerations
      const hasHover = cssContent.includes(":hover");
      const hasFocus = cssContent.includes(":focus");

      if (hasHover && !hasFocus) {
        this.warnings.push(
          "Consider adding :focus styles for keyboard accessibility"
        );
      }
    } catch (error) {
      this.warnings.push(`Best practices check failed: ${error.message}`);
    }
  }

  validateInlineStyles(inlineStyles) {
    let inlineCount = 0;

    inlineStyles.forEach((style) => {
      if (style && style.trim().length > 0) {
        inlineCount++;

        // Check for inline style syntax
        if (!style.includes(":")) {
          this.errors.push(`Malformed inline style: ${style}`);
        }
      }
    });

    if (inlineCount > 5) {
      this.warnings.push(
        "Consider moving inline styles to CSS classes for better maintainability"
      );
    }
  }

  calculateScore() {
    const maxPoints = 100;
    const errorPenalty = 20;
    const warningPenalty = 5;

    const deductions =
      this.errors.length * errorPenalty + this.warnings.length * warningPenalty;
    return Math.max(0, maxPoints - deductions);
  }
}

// CLI usage
if (require.main === module) {
  const fs = require("fs");
  const htmlFile = process.argv[2];

  if (!htmlFile) {
    console.error("Usage: node css-validator.js <html-file>");
    process.exit(1);
  }

  try {
    const htmlContent = fs.readFileSync(htmlFile, "utf8");
    const validator = new CSSValidator();
    const result = validator.validate(htmlContent);

    console.log(JSON.stringify(result, null, 2));
    process.exit(result.valid ? 0 : 1);
  } catch (error) {
    console.error("Error reading file:", error.message);
    process.exit(1);
  }
}

module.exports = { CSSValidator };
