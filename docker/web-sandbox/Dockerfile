# Web Development Sandbox with Node.js + Playwright + Lighthouse
# Security-hardened environment for running user HTML/CSS/JavaScript

FROM node:18-alpine AS base

# Install system dependencies
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    bash \
    curl

# Create non-root user for security
RUN addgroup -g 1001 -S sandbox && \
    adduser -S sandbox -u 1001 -G sandbox

# Set up working directory
WORKDIR /sandbox

# Install Node.js dependencies for testing
COPY package.json package-lock.json ./
RUN npm ci --only=production && npm cache clean --force

# Install Playwright (browser automation for testing)
RUN npx playwright install --with-deps chromium

# Install Lighthouse (performance testing)
RUN npm install -g lighthouse

# Set up environment for Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Create directories for user code and test output
RUN mkdir -p /sandbox/user-code /sandbox/test-output /sandbox/test-results && \
    chown -R sandbox:sandbox /sandbox

# Copy test runner scripts
COPY test-runner.js ./
COPY html-validator.js ./
COPY css-validator.js ./

# Switch to non-root user
USER sandbox

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node --version || exit 1

# Default command
CMD ["node", "test-runner.js"]