import DOMPurify from "dompurify";

// Security configuration for HTML sanitization
const ALLOWED_TAGS = [
  // Basic HTML structure
  "html",
  "head",
  "body",
  "title",
  "meta",

  // Content tags
  "div",
  "span",
  "p",
  "br",
  "hr",
  "h1",
  "h2",
  "h3",
  "h4",
  "h5",
  "h6",
  "article",
  "section",
  "header",
  "footer",
  "main",
  "nav",
  "aside",

  // Lists
  "ul",
  "ol",
  "li",
  "dl",
  "dt",
  "dd",

  // Links and media
  "a",
  "img",
  "figure",
  "figcaption",

  // Tables
  "table",
  "thead",
  "tbody",
  "tfoot",
  "tr",
  "th",
  "td",

  // Forms (disabled scripts)
  "form",
  "input",
  "button",
  "label",
  "fieldset",
  "legend",

  // Text formatting
  "strong",
  "b",
  "em",
  "i",
  "mark",
  "small",
  "del",
  "ins",
  "sub",
  "sup",

  // Style tag for CSS
  "style",
];

const ALLOWED_ATTRIBUTES = [
  "class",
  "id",
  "style",
  "href",
  "target",
  "rel",
  "src",
  "alt",
  "width",
  "height",
  "type",
  "name",
  "value",
  "placeholder",
  "aria-*",
  "data-*",
  "lang",
  "dir",
  "title",
];

const FORBIDDEN_PATTERNS = [
  // JavaScript execution patterns
  /javascript:/gi,
  /vbscript:/gi,
  /data:.*script/gi,
  /on\w+\s*=/gi, // Event handlers like onclick, onload, etc.

  // Dangerous protocols
  /file:/gi,
  /ftp:/gi,

  // Script injection patterns
  /<script/gi,
  /<iframe(?![^>]*sandbox="[^"]*")/gi, // iframes without sandbox
  /<object/gi,
  /<embed/gi,
  /<link.*stylesheet/gi, // External stylesheets
  /<meta.*http-equiv/gi, // Meta redirects
];

/**
 * Sanitizes HTML code for safe rendering in live preview
 * Removes dangerous scripts while preserving educational HTML/CSS
 */
export function sanitizeHTML(html: string): string {
  // Quick check for obviously dangerous patterns
  for (const pattern of FORBIDDEN_PATTERNS) {
    if (pattern.test(html)) {
      console.warn("Potentially dangerous content detected and sanitized");
      break;
    }
  }

  // Configure DOMPurify
  const config = {
    ALLOWED_TAGS,
    ALLOWED_ATTR: ALLOWED_ATTRIBUTES,
    ALLOW_DATA_ATTR: true,
    ALLOW_ARIA_ATTR: true,
    FORBID_SCRIPT: true,
    FORBID_TAGS: ["script", "iframe", "object", "embed", "base"],
    FORBID_ATTR: ["onerror", "onload", "onclick", "onmouseover"],
    KEEP_CONTENT: true,
    FORCE_BODY: false,
    WHOLE_DOCUMENT: true,
    SANITIZE_DOM: true,
    SANITIZE_NAMED_PROPS: true,
    IN_PLACE: false,
  };

  // Sanitize the HTML
  const sanitized = DOMPurify.sanitize(html, config);

  // Additional manual checks for CSS injection
  const safeCss = sanitizeCSSContent(sanitized);

  return safeCss;
}

/**
 * Sanitizes CSS content within style tags
 */
function sanitizeCSSContent(html: string): string {
  // Pattern to match style tag content
  const styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/gi;

  return html.replace(styleRegex, (match, cssContent) => {
    // Remove dangerous CSS patterns
    const safeCss = cssContent
      // Remove javascript: urls
      .replace(/javascript\s*:/gi, "")
      // Remove expression() (IE specific)
      .replace(/expression\s*\(/gi, "")
      // Remove @import statements (prevent external CSS)
      .replace(/@import\s+/gi, "")
      // Remove behavior property (IE specific)
      .replace(/behavior\s*:/gi, "")
      // Remove -moz-binding (Firefox specific)
      .replace(/-moz-binding\s*:/gi, "");

    return `<style>${safeCss}</style>`;
  });
}

/**
 * Validates if HTML content is safe for educational purposes
 */
export function validateHTMLSafety(html: string): {
  isSafe: boolean;
  warnings: string[];
  errors: string[];
} {
  const warnings: string[] = [];
  const errors: string[] = [];

  // Check for dangerous patterns
  for (const pattern of FORBIDDEN_PATTERNS) {
    if (pattern.test(html)) {
      errors.push(`Detected potentially dangerous pattern: ${pattern.source}`);
    }
  }

  // Check for external resources
  if (html.includes("http://") || html.includes("https://")) {
    warnings.push(
      "External resources detected - these may not load in preview"
    );
  }

  // Check for complex JavaScript-like patterns in CSS
  if (html.includes("expression(") || html.includes("javascript:")) {
    errors.push("Detected JavaScript execution attempts in CSS");
  }

  return {
    isSafe: errors.length === 0,
    warnings,
    errors,
  };
}
