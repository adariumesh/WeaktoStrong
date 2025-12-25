#!/bin/bash

# Smart Context Management - Load focused development context
# Usage: ./scripts/load-context.sh <domain>

DOMAIN=$1
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== WEAK-TO-STRONG DEVELOPMENT SESSION ===${NC}"
echo -e "${BLUE}Project:${NC} Weak-to-Strong AI Training Platform"
echo -e "${BLUE}Domain:${NC} ${DOMAIN:-'full'}"
echo -e "${BLUE}Date:${NC} $(date '+%Y-%m-%d %H:%M')"
echo ""

# Function to count tokens (rough estimate: 1 token ≈ 1.3 words)
count_tokens() {
    local file=$1
    if [ -f "$file" ]; then
        local words=$(wc -w < "$file" 2>/dev/null || echo 0)
        echo $((words * 13 / 10))
    else
        echo 0
    fi
}

# Always load core context (architecture overview)
echo -e "${YELLOW}📋 CORE ARCHITECTURE CONTEXT${NC}"
echo "----------------------------------------"
if [ -f "$PROJECT_ROOT/claude_memory.md" ]; then
    # Load first 150 lines of claude_memory.md (core architecture)
    head -150 "$PROJECT_ROOT/claude_memory.md"
    core_tokens=$(count_tokens <(head -150 "$PROJECT_ROOT/claude_memory.md"))
    echo ""
    echo -e "${BLUE}Core context loaded:${NC} ~${core_tokens} tokens"
else
    echo -e "${RED}Warning: claude_memory.md not found${NC}"
fi

echo ""
echo -e "${YELLOW}🎯 DOMAIN-SPECIFIC CONTEXT${NC}"
echo "----------------------------------------"

# Load domain-specific context
case $DOMAIN in
    "auth"|"authentication")
        if [ -f "$PROJECT_ROOT/contexts/AUTH_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/contexts/AUTH_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/contexts/AUTH_CONTEXT.md")
            echo ""
            echo -e "${BLUE}Auth context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: AUTH_CONTEXT.md not found${NC}"
            exit 1
        fi
        ;;
    "ui"|"components"|"design")
        if [ -f "$PROJECT_ROOT/contexts/UI_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/contexts/UI_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/contexts/UI_CONTEXT.md")
            echo ""
            echo -e "${BLUE}UI context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: UI_CONTEXT.md not found${NC}"
            exit 1
        fi
        ;;
    "challenge"|"challenges"|"content")
        if [ -f "$PROJECT_ROOT/contexts/CHALLENGE_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/contexts/CHALLENGE_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/contexts/CHALLENGE_CONTEXT.md")
            echo ""
            echo -e "${BLUE}Challenge context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: CHALLENGE_CONTEXT.md not found${NC}"
            exit 1
        fi
        ;;
    "testing"|"test"|"docker"|"sandbox")
        if [ -f "$PROJECT_ROOT/contexts/TESTING_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/contexts/TESTING_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/contexts/TESTING_CONTEXT.md")
            echo ""
            echo -e "${BLUE}Testing context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: TESTING_CONTEXT.md not found${NC}"
            exit 1
        fi
        ;;
    "workspace"|"editor"|"monaco"|"preview")
        if [ -f "$PROJECT_ROOT/contexts/WORKSPACE_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/contexts/WORKSPACE_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/contexts/WORKSPACE_CONTEXT.md")
            echo ""
            echo -e "${BLUE}Workspace context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: WORKSPACE_CONTEXT.md not found${NC}"
            exit 1
        fi
        ;;
    "ai"|"artificial-intelligence")
        echo -e "${YELLOW}🤖 AI Development Context (Phase 5)${NC}"
        if [ -f "$PROJECT_ROOT/AI_DEVELOPMENT_CONTEXT.md" ]; then
            cat "$PROJECT_ROOT/AI_DEVELOPMENT_CONTEXT.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/AI_DEVELOPMENT_CONTEXT.md")
            echo ""
            echo -e "${BLUE}AI context loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Note: AI_DEVELOPMENT_CONTEXT.md - ready for Phase 5${NC}"
            domain_tokens=0
        fi
        ;;
    "full"|"complete"|"all")
        echo -e "${YELLOW}📖 COMPLETE PROJECT CONTEXT${NC}"
        if [ -f "$PROJECT_ROOT/claude_memory.md" ]; then
            # Skip first 150 lines (already loaded) and load the rest
            tail -n +151 "$PROJECT_ROOT/claude_memory.md"
            full_tokens=$(count_tokens "$PROJECT_ROOT/claude_memory.md")
            domain_tokens=$((full_tokens - core_tokens))
            echo ""
            echo -e "${BLUE}Full context loaded:${NC} ~${full_tokens} tokens"
        else
            echo -e "${RED}Error: claude_memory.md not found${NC}"
            exit 1
        fi
        ;;
    "plan"|"planning"|"development")
        echo -e "${YELLOW}📋 DEVELOPMENT PLAN CONTEXT${NC}"
        if [ -f "$PROJECT_ROOT/DEVELOPMENT_PLAN.md" ]; then
            cat "$PROJECT_ROOT/DEVELOPMENT_PLAN.md"
            domain_tokens=$(count_tokens "$PROJECT_ROOT/DEVELOPMENT_PLAN.md")
            echo ""
            echo -e "${BLUE}Development plan loaded:${NC} ~${domain_tokens} tokens"
        else
            echo -e "${RED}Error: DEVELOPMENT_PLAN.md not found${NC}"
            exit 1
        fi
        ;;
    "help"|"--help"|"-h")
        echo -e "${YELLOW}📚 Available domains:${NC}"
        echo "  auth          - Authentication system (users, JWT, OAuth)"
        echo "  ui            - UI components and design system"
        echo "  challenges    - Challenge management and data"
        echo "  testing       - Docker sandbox and test execution"
        echo "  workspace     - Code editor and preview system"
        echo "  ai            - AI integration (Phase 5 - upcoming)"
        echo "  plan          - Development plan and roadmap"
        echo "  full          - Complete project context"
        echo ""
        echo -e "${YELLOW}📖 Usage examples:${NC}"
        echo "  ./scripts/load-context.sh auth      # Load auth development context"
        echo "  ./scripts/load-context.sh testing   # Load testing infrastructure context"
        echo "  ./scripts/load-context.sh full      # Load complete project context"
        echo ""
        echo -e "${YELLOW}💡 Tips:${NC}"
        echo "  • Use focused contexts (auth, ui, etc.) for efficient development"
        echo "  • Use 'full' context only when working across multiple domains"
        echo "  • Each focused context is 15-25K tokens (optimal for Claude)"
        echo "  • Full context is ~50K tokens (use sparingly)"
        exit 0
        ;;
    "")
        echo -e "${RED}Error: No domain specified${NC}"
        echo "Use './scripts/load-context.sh help' to see available domains"
        exit 1
        ;;
    *)
        echo -e "${RED}Error: Unknown domain '${DOMAIN}'${NC}"
        echo "Use './scripts/load-context.sh help' to see available domains"
        exit 1
        ;;
esac

# Calculate total context size
total_tokens=$((core_tokens + domain_tokens))

echo ""
echo -e "${GREEN}✅ CONTEXT SUMMARY${NC}"
echo "----------------------------------------"
echo -e "${BLUE}Core architecture:${NC} ~${core_tokens} tokens"
echo -e "${BLUE}Domain-specific:${NC} ~${domain_tokens} tokens"
echo -e "${BLUE}Total context:${NC} ~${total_tokens} tokens"

# Context size recommendations
if [ $total_tokens -lt 20000 ]; then
    echo -e "${GREEN}✅ Optimal context size${NC} (efficient development)"
elif [ $total_tokens -lt 50000 ]; then
    echo -e "${YELLOW}⚠️ Moderate context size${NC} (good for complex tasks)"
elif [ $total_tokens -lt 80000 ]; then
    echo -e "${YELLOW}⚠️ Large context size${NC} (consider focused domain)"
else
    echo -e "${RED}❌ Very large context${NC} (may impact performance)"
fi

echo ""
echo -e "${GREEN}🚀 Ready for ${DOMAIN} development!${NC}"
echo ""