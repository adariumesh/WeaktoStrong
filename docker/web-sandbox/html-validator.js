#!/usr/bin/env node

const cheerio = require("cheerio");

/**
 * HTML Validation Utilities
 * Validates HTML structure, semantics, and best practices
 */
class HTMLValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
  }

  validate(htmlContent) {
    try {
      const $ = cheerio.load(htmlContent);

      this.checkDoctype(htmlContent);
      this.checkBasicStructure($);
      this.checkSemanticElements($);
      this.checkAccessibility($);
      this.checkSEO($);

      return {
        valid: this.errors.length === 0,
        errors: this.errors,
        warnings: this.warnings,
        score: this.calculateScore(),
      };
    } catch (error) {
      this.errors.push(`Parse error: ${error.message}`);
      return {
        valid: false,
        errors: this.errors,
        warnings: this.warnings,
        score: 0,
      };
    }
  }

  checkDoctype(html) {
    if (!html.trim().toLowerCase().startsWith("<!doctype html>")) {
      this.errors.push("Missing HTML5 doctype declaration");
    }
  }

  checkBasicStructure($) {
    // Check for required elements
    if ($("html").length === 0) {
      this.errors.push("Missing <html> element");
    }

    if ($("head").length === 0) {
      this.errors.push("Missing <head> element");
    }

    if ($("body").length === 0) {
      this.errors.push("Missing <body> element");
    }

    if ($("title").length === 0) {
      this.errors.push("Missing <title> element");
    } else if ($("title").text().trim().length === 0) {
      this.warnings.push("Title element is empty");
    }

    // Check meta viewport
    if ($('meta[name="viewport"]').length === 0) {
      this.warnings.push("Missing viewport meta tag for responsive design");
    }

    // Check charset
    if ($("meta[charset]").length === 0) {
      this.warnings.push("Missing charset declaration");
    }
  }

  checkSemanticElements($) {
    const semanticElements = [
      "header",
      "main",
      "section",
      "article",
      "nav",
      "aside",
      "footer",
    ];
    const foundElements = semanticElements.filter((tag) => $(tag).length > 0);

    if (foundElements.length === 0) {
      this.warnings.push(
        "No semantic HTML5 elements found. Consider using header, main, section, etc."
      );
    }

    // Check heading hierarchy
    const headings = $("h1, h2, h3, h4, h5, h6");
    if (headings.length === 0) {
      this.warnings.push("No heading elements found");
    } else {
      const h1Count = $("h1").length;
      if (h1Count === 0) {
        this.warnings.push("Missing h1 element");
      } else if (h1Count > 1) {
        this.warnings.push(
          "Multiple h1 elements found - consider using only one per page"
        );
      }
    }
  }

  checkAccessibility($) {
    // Check images for alt text
    const images = $("img");
    images.each((i, img) => {
      const $img = $(img);
      if (!$img.attr("alt")) {
        this.warnings.push(
          `Image missing alt attribute: ${$img.attr("src") || "unknown src"}`
        );
      }
    });

    // Check form inputs for labels
    const inputs = $('input[type!="hidden"], select, textarea');
    inputs.each((i, input) => {
      const $input = $(input);
      const id = $input.attr("id");
      const ariaLabel = $input.attr("aria-label");
      const ariaLabelledby = $input.attr("aria-labelledby");

      if (id) {
        const hasLabel = $(`label[for="${id}"]`).length > 0;
        if (!hasLabel && !ariaLabel && !ariaLabelledby) {
          this.warnings.push(
            `Form input missing label: ${$input.attr("name") || "unnamed input"}`
          );
        }
      } else if (!ariaLabel && !ariaLabelledby) {
        this.warnings.push(
          `Form input missing id and label: ${$input.attr("name") || "unnamed input"}`
        );
      }
    });

    // Check links for descriptive text
    const links = $("a[href]");
    links.each((i, link) => {
      const $link = $(link);
      const text = $link.text().trim();
      const ariaLabel = $link.attr("aria-label");

      if (!text && !ariaLabel) {
        this.warnings.push("Link without descriptive text found");
      } else if (
        text &&
        ["click here", "read more", "link"].includes(text.toLowerCase())
      ) {
        this.warnings.push(`Link with non-descriptive text: "${text}"`);
      }
    });
  }

  checkSEO($) {
    // Check meta description
    if ($('meta[name="description"]').length === 0) {
      this.warnings.push("Missing meta description");
    }

    // Check for multiple h1s (SEO best practice)
    if ($("h1").length > 1) {
      this.warnings.push("Multiple h1 elements may impact SEO");
    }

    // Check for empty elements
    const importantElements = ["title", "h1", "h2", "h3", "p"];
    importantElements.forEach((tag) => {
      $(tag).each((i, el) => {
        if ($(el).text().trim().length === 0) {
          this.warnings.push(`Empty ${tag} element found`);
        }
      });
    });
  }

  calculateScore() {
    const maxPoints = 100;
    const errorPenalty = 15;
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
    console.error("Usage: node html-validator.js <html-file>");
    process.exit(1);
  }

  try {
    const htmlContent = fs.readFileSync(htmlFile, "utf8");
    const validator = new HTMLValidator();
    const result = validator.validate(htmlContent);

    console.log(JSON.stringify(result, null, 2));
    process.exit(result.valid ? 0 : 1);
  } catch (error) {
    console.error("Error reading file:", error.message);
    process.exit(1);
  }
}

module.exports = { HTMLValidator };
