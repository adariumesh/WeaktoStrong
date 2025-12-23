#!/bin/bash

# Quick file finder for domain-specific development
# Usage: ./scripts/find-domain.sh <query>

QUERY=$1
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

if [ -z "$QUERY" ]; then
    echo -e "${YELLOW}🔍 Quick File Finder${NC}"
    echo "Usage: ./scripts/find-domain.sh <query>"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  ./scripts/find-domain.sh auth        # Find auth-related files"
    echo "  ./scripts/find-domain.sh challenge   # Find challenge files"
    echo "  ./scripts/find-domain.sh test        # Find testing files"
    echo "  ./scripts/find-domain.sh ui          # Find UI components"
    echo "  ./scripts/find-domain.sh monaco      # Find Monaco editor files"
    exit 1
fi

echo -e "${GREEN}🔍 Finding files matching: '${QUERY}'${NC}"
echo "----------------------------------------"

# Search for files by name (case-insensitive)
echo -e "${BLUE}📁 Files by name:${NC}"
find "$PROJECT_ROOT" -type f -iname "*${QUERY}*" \
    -not -path "*/node_modules/*" \
    -not -path "*/venv/*" \
    -not -path "*/.next/*" \
    -not -path "*/.git/*" \
    -not -path "*/dist/*" \
    | head -10 \
    | sed "s|$PROJECT_ROOT/||" \
    | while read -r file; do
        echo -e "  ${GRAY}•${NC} $file"
    done

echo ""

# Search for files containing the query in content
echo -e "${BLUE}📄 Files containing '${QUERY}':${NC}"
grep -r -l -i "$QUERY" "$PROJECT_ROOT" \
    --exclude-dir=node_modules \
    --exclude-dir=venv \
    --exclude-dir=.next \
    --exclude-dir=.git \
    --exclude-dir=dist \
    --exclude="*.log" \
    --exclude="*.lock" \
    2>/dev/null \
    | head -8 \
    | sed "s|$PROJECT_ROOT/||" \
    | while read -r file; do
        echo -e "  ${GRAY}•${NC} $file"
    done

echo ""

# Domain-specific quick suggestions
case "$QUERY" in
    "auth"|"authentication"|"user"|"login"|"jwt")
        echo -e "${YELLOW}💡 Auth-related files:${NC}"
        echo -e "  ${GRAY}•${NC} apps/web/app/auth/ (auth pages)"
        echo -e "  ${GRAY}•${NC} backend/app/api/v1/auth.py (auth API)"
        echo -e "  ${GRAY}•${NC} backend/app/core/auth.py (JWT utilities)"
        echo -e "  ${GRAY}•${NC} apps/web/lib/auth.ts (NextAuth config)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh auth"
        ;;
    "challenge"|"challenges"|"content")
        echo -e "${YELLOW}💡 Challenge-related files:${NC}"
        echo -e "  ${GRAY}•${NC} apps/web/components/challenge/ (challenge UI)"
        echo -e "  ${GRAY}•${NC} apps/web/lib/data/challenges.ts (challenge data)"
        echo -e "  ${GRAY}•${NC} CHALLENGE_CONTENT.md (challenge specs)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh challenges"
        ;;
    "test"|"testing"|"docker"|"sandbox")
        echo -e "${YELLOW}💡 Testing-related files:${NC}"
        echo -e "  ${GRAY}•${NC} docker/web-sandbox/ (Docker testing environment)"
        echo -e "  ${GRAY}•${NC} backend/app/services/test_runner.py (test execution)"
        echo -e "  ${GRAY}•${NC} apps/web/components/testing/ (test UI)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh testing"
        ;;
    "ui"|"component"|"design"|"button"|"card")
        echo -e "${YELLOW}💡 UI-related files:${NC}"
        echo -e "  ${GRAY}•${NC} apps/web/components/ui/ (Shadcn/ui components)"
        echo -e "  ${GRAY}•${NC} apps/web/components/layout/ (layout components)"
        echo -e "  ${GRAY}•${NC} apps/web/app/globals.css (global styles)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh ui"
        ;;
    "editor"|"monaco"|"workspace"|"preview")
        echo -e "${YELLOW}💡 Workspace-related files:${NC}"
        echo -e "  ${GRAY}•${NC} apps/web/components/workspace/ (workspace layout)"
        echo -e "  ${GRAY}•${NC} apps/web/components/editor/ (Monaco editor, preview)"
        echo -e "  ${GRAY}•${NC} apps/web/lib/security/ (preview security)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh workspace"
        ;;
    "api"|"backend"|"fastapi"|"python")
        echo -e "${YELLOW}💡 Backend-related files:${NC}"
        echo -e "  ${GRAY}•${NC} backend/app/api/v1/ (API endpoints)"
        echo -e "  ${GRAY}•${NC} backend/app/models/ (database models)"
        echo -e "  ${GRAY}•${NC} backend/app/services/ (business logic)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh full"
        ;;
    "ai"|"artificial"|"intelligence"|"llm")
        echo -e "${YELLOW}💡 AI-related files (Phase 5):${NC}"
        echo -e "  ${GRAY}•${NC} AI_DEVELOPMENT_CONTEXT.md (Phase 5 context)"
        echo -e "  ${GRAY}•${NC} AI_PROMPTS.md (AI system prompts)"
        echo -e "  ${GRAY}•${NC} [Future] apps/web/components/ai/ (AI UI)"
        echo ""
        echo -e "${BLUE}Load context:${NC} ./scripts/load-context.sh ai"
        ;;
esac

# Show quick navigation commands
echo -e "${GREEN}🚀 Quick commands:${NC}"
echo -e "  ${GRAY}•${NC} code <filename>                    # Open in VS Code"
echo -e "  ${GRAY}•${NC} ls -la <directory>                # List directory contents"
echo -e "  ${GRAY}•${NC} grep -r '${QUERY}' <directory>     # Search in directory"
echo ""