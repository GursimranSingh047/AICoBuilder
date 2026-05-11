#!/bin/bash

# ============================================================================
# ProjectPilot - Security Verification Script
# ============================================================================
# This script verifies that your repository is secure and ready for GitHub
# Run this before pushing to GitHub: bash verify_security.sh
# ============================================================================

echo "🔍 ProjectPilot Security Verification"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_CHECKS_PASSED=true

# ============================================================================
# Check 1: Verify .env is NOT tracked by Git
# ============================================================================
echo "📋 Check 1: Verify backend/.env is NOT tracked by Git"
if git ls-files | grep -q "^backend/.env$"; then
    echo -e "${RED}❌ FAIL: backend/.env is still tracked by Git!${NC}"
    echo "   Run: git rm --cached backend/.env"
    ALL_CHECKS_PASSED=false
else
    echo -e "${GREEN}✅ PASS: backend/.env is NOT tracked by Git${NC}"
fi
echo ""

# ============================================================================
# Check 2: Verify .env exists locally
# ============================================================================
echo "📋 Check 2: Verify backend/.env exists locally"
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✅ PASS: backend/.env exists locally${NC}"
else
    echo -e "${RED}❌ FAIL: backend/.env does NOT exist locally!${NC}"
    echo "   Create it from: cp backend/.env.example backend/.env"
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 3: Verify node_modules is NOT tracked by Git
# ============================================================================
echo "📋 Check 3: Verify frontend/node_modules is NOT tracked by Git"
NODE_MODULES_COUNT=$(git ls-files | grep "^frontend/node_modules" | wc -l | tr -d ' ')
if [ "$NODE_MODULES_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ PASS: frontend/node_modules is NOT tracked by Git${NC}"
else
    echo -e "${RED}❌ FAIL: frontend/node_modules is still tracked ($NODE_MODULES_COUNT files)!${NC}"
    echo "   Run: git rm -r --cached frontend/node_modules"
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 4: Verify node_modules exists locally
# ============================================================================
echo "📋 Check 4: Verify frontend/node_modules exists locally"
if [ -d "frontend/node_modules" ]; then
    echo -e "${GREEN}✅ PASS: frontend/node_modules exists locally${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: frontend/node_modules does NOT exist locally${NC}"
    echo "   Run: cd frontend && npm install"
fi
echo ""

# ============================================================================
# Check 5: Verify .gitignore contains .env
# ============================================================================
echo "📋 Check 5: Verify .gitignore contains .env rule"
if grep -q "^\.env$" .gitignore; then
    echo -e "${GREEN}✅ PASS: .gitignore contains .env rule${NC}"
else
    echo -e "${RED}❌ FAIL: .gitignore does NOT contain .env rule!${NC}"
    echo "   Add: echo '.env' >> .gitignore"
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 6: Verify .gitignore contains node_modules
# ============================================================================
echo "📋 Check 6: Verify .gitignore contains node_modules rule"
if grep -q "node_modules/" .gitignore; then
    echo -e "${GREEN}✅ PASS: .gitignore contains node_modules rule${NC}"
else
    echo -e "${RED}❌ FAIL: .gitignore does NOT contain node_modules rule!${NC}"
    echo "   Add: echo 'node_modules/' >> .gitignore"
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 7: Verify .env.example files exist
# ============================================================================
echo "📋 Check 7: Verify .env.example templates exist"
EXAMPLE_FILES_MISSING=false

if [ -f "backend/.env.example" ]; then
    echo -e "${GREEN}✅ PASS: backend/.env.example exists${NC}"
else
    echo -e "${RED}❌ FAIL: backend/.env.example does NOT exist!${NC}"
    EXAMPLE_FILES_MISSING=true
    ALL_CHECKS_PASSED=false
fi

if [ -f "frontend/.env.example" ]; then
    echo -e "${GREEN}✅ PASS: frontend/.env.example exists${NC}"
else
    echo -e "${RED}❌ FAIL: frontend/.env.example does NOT exist!${NC}"
    EXAMPLE_FILES_MISSING=true
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 8: Verify working tree is clean
# ============================================================================
echo "📋 Check 8: Verify Git working tree is clean"
if git diff-index --quiet HEAD --; then
    echo -e "${GREEN}✅ PASS: Git working tree is clean${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: You have uncommitted changes${NC}"
    echo "   Run: git status"
fi
echo ""

# ============================================================================
# Check 9: Verify API key is configured
# ============================================================================
echo "📋 Check 9: Verify API key is configured in backend/.env"
if [ -f "backend/.env" ]; then
    if grep -q "openai_api_key=sk-" backend/.env; then
        echo -e "${GREEN}✅ PASS: API key is configured${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: API key may not be configured correctly${NC}"
        echo "   Check: backend/.env contains openai_api_key=sk-..."
    fi
else
    echo -e "${RED}❌ FAIL: backend/.env does not exist${NC}"
    ALL_CHECKS_PASSED=false
fi
echo ""

# ============================================================================
# Check 10: Verify frontend .env is configured
# ============================================================================
echo "📋 Check 10: Verify frontend/.env is configured"
if [ -f "frontend/.env" ]; then
    if grep -q "VITE_API_URL=" frontend/.env; then
        echo -e "${GREEN}✅ PASS: Frontend environment variables configured${NC}"
    else
        echo -e "${YELLOW}⚠️  WARNING: VITE_API_URL may not be configured${NC}"
        echo "   Check: frontend/.env contains VITE_API_URL=..."
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: frontend/.env does not exist${NC}"
    echo "   Create it from: cp frontend/.env.example frontend/.env"
fi
echo ""

# ============================================================================
# Final Summary
# ============================================================================
echo "======================================"
echo "📊 Security Verification Summary"
echo "======================================"
echo ""

if [ "$ALL_CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}✅ ALL CRITICAL CHECKS PASSED!${NC}"
    echo ""
    echo "🎉 Your repository is SECURE and ready for GitHub!"
    echo ""
    echo "Next steps:"
    echo "1. 🚨 Revoke your old API key (if exposed)"
    echo "2. 🔑 Generate a new API key"
    echo "3. 📝 Update backend/.env with new key"
    echo "4. 🚀 Push to GitHub: git push origin main"
    echo ""
else
    echo -e "${RED}❌ SOME CHECKS FAILED!${NC}"
    echo ""
    echo "⚠️  Please fix the issues above before pushing to GitHub."
    echo ""
    echo "Common fixes:"
    echo "- git rm --cached backend/.env"
    echo "- git rm -r --cached frontend/node_modules"
    echo "- git add .gitignore"
    echo "- git commit -m 'Security: Fix .gitignore'"
    echo ""
fi

# ============================================================================
# Additional Information
# ============================================================================
echo "======================================"
echo "📚 Additional Information"
echo "======================================"
echo ""
echo "Documentation:"
echo "- SECURITY.md - Complete security guide"
echo "- DEPLOYMENT.md - Deployment instructions"
echo "- SECURITY_FIXES_APPLIED.md - What was fixed"
echo "- GIT_CLEANUP_COMPLETE.md - Git cleanup summary"
echo ""
echo "Useful commands:"
echo "- git status - Check current status"
echo "- git ls-files | grep .env - Check if .env is tracked"
echo "- git check-ignore -v backend/.env - Verify .gitignore rules"
echo ""

exit 0
