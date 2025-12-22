#!/bin/bash

# PulseB2B - Pre-Deployment Verification Script
# Run this before deploying to Vercel to catch issues early

set -e  # Exit on any error

echo "🔍 PulseB2B Pre-Deployment Verification"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counters
ERRORS=0
WARNINGS=0
PASSED=0

# Check if we're in frontend directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found${NC}"
    echo "Please run this script from the frontend directory"
    exit 1
fi

echo "📦 Step 1: Checking Dependencies"
echo "--------------------------------"

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 18 ]; then
    echo -e "${GREEN}✅ Node.js version: $(node -v)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Node.js version too old: $(node -v) (requires 18+)${NC}"
    ((ERRORS++))
fi

# Check npm version
NPM_VERSION=$(npm -v | cut -d'.' -f1)
if [ "$NPM_VERSION" -ge 9 ]; then
    echo -e "${GREEN}✅ npm version: $(npm -v)${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  npm version: $(npm -v) (recommended 9+)${NC}"
    ((WARNINGS++))
fi

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ node_modules directory exists${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ node_modules not found. Run: npm install${NC}"
    ((ERRORS++))
fi

echo ""
echo "🔐 Step 2: Checking Environment Variables"
echo "----------------------------------------"

# Check .env.local exists
if [ -f ".env.local" ]; then
    echo -e "${GREEN}✅ .env.local file found${NC}"
    ((PASSED++))
    
    # Check required variables
    source .env.local 2>/dev/null || true
    
    if [ -n "$NEXT_PUBLIC_SUPABASE_URL" ]; then
        echo -e "${GREEN}✅ NEXT_PUBLIC_SUPABASE_URL is set${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ NEXT_PUBLIC_SUPABASE_URL is missing${NC}"
        ((ERRORS++))
    fi
    
    if [ -n "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ]; then
        echo -e "${GREEN}✅ NEXT_PUBLIC_SUPABASE_ANON_KEY is set${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ NEXT_PUBLIC_SUPABASE_ANON_KEY is missing${NC}"
        ((ERRORS++))
    fi
    
    if [ -n "$NEXT_PUBLIC_MAPBOX_TOKEN" ]; then
        if [[ $NEXT_PUBLIC_MAPBOX_TOKEN == pk.* ]]; then
            echo -e "${GREEN}✅ NEXT_PUBLIC_MAPBOX_TOKEN is valid (starts with pk.)${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ NEXT_PUBLIC_MAPBOX_TOKEN should start with 'pk.'${NC}"
            ((ERRORS++))
        fi
    else
        echo -e "${RED}❌ NEXT_PUBLIC_MAPBOX_TOKEN is missing${NC}"
        ((ERRORS++))
    fi
    
    if [ -n "$NEXT_PUBLIC_STRIPE_PAYMENT_LINK" ]; then
        if [[ $NEXT_PUBLIC_STRIPE_PAYMENT_LINK == https://buy.stripe.com/* ]]; then
            echo -e "${GREEN}✅ NEXT_PUBLIC_STRIPE_PAYMENT_LINK is valid${NC}"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠️  NEXT_PUBLIC_STRIPE_PAYMENT_LINK format may be incorrect${NC}"
            ((WARNINGS++))
        fi
    else
        echo -e "${RED}❌ NEXT_PUBLIC_STRIPE_PAYMENT_LINK is missing${NC}"
        ((ERRORS++))
    fi
    
else
    echo -e "${RED}❌ .env.local file not found${NC}"
    echo "   Copy .env.example to .env.local and fill in your values"
    ((ERRORS++))
fi

echo ""
echo "📝 Step 3: TypeScript Type Checking"
echo "----------------------------------"

if npm run type-check > /dev/null 2>&1; then
    echo -e "${GREEN}✅ TypeScript compilation successful (no type errors)${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ TypeScript compilation failed${NC}"
    echo "   Run: npm run type-check to see errors"
    ((ERRORS++))
fi

echo ""
echo "🏗️  Step 4: Build Test"
echo "--------------------"

echo "Building production bundle... (this may take 30-60 seconds)"
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Production build successful${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ Production build failed${NC}"
    echo "   Run: npm run build to see errors"
    ((ERRORS++))
fi

echo ""
echo "🎨 Step 5: Required Files Check"
echo "------------------------------"

# Check critical files exist
CRITICAL_FILES=(
    "src/app/page.tsx"
    "src/app/layout.tsx"
    "src/components/GlobalSignalMap.tsx"
    "src/components/PremiumPaywall.tsx"
    "src/lib/supabase.ts"
    "src/lib/utils.ts"
    "src/types/index.ts"
    "next.config.js"
    "tailwind.config.ts"
    "tsconfig.json"
    "vercel.json"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $file is missing${NC}"
        ((ERRORS++))
    fi
done

echo ""
echo "📋 Step 6: Configuration Validation"
echo "----------------------------------"

# Check vercel.json exists and is valid JSON
if [ -f "vercel.json" ]; then
    if python3 -m json.tool vercel.json > /dev/null 2>&1; then
        echo -e "${GREEN}✅ vercel.json is valid JSON${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ vercel.json has invalid JSON syntax${NC}"
        ((ERRORS++))
    fi
else
    echo -e "${YELLOW}⚠️  vercel.json not found (optional)${NC}"
    ((WARNINGS++))
fi

# Check package.json scripts
if grep -q "\"build\": \"next build\"" package.json; then
    echo -e "${GREEN}✅ Build script configured${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Build script may not be standard${NC}"
    ((WARNINGS++))
fi

if grep -q "\"start\": \"next start\"" package.json; then
    echo -e "${GREEN}✅ Start script configured${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Start script may not be standard${NC}"
    ((WARNINGS++))
fi

echo ""
echo "========================================"
echo "📊 Verification Summary"
echo "========================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo -e "${RED}Errors: $ERRORS${NC}"
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical checks passed!${NC}"
    echo ""
    echo "🚀 Ready to deploy to Vercel!"
    echo ""
    echo "Next steps:"
    echo "1. Commit your changes: git add . && git commit -m 'feat: Premium dashboard ready'"
    echo "2. Push to GitHub: git push origin main"
    echo "3. Deploy to Vercel:"
    echo "   - Option A: Connect GitHub repo in Vercel Dashboard"
    echo "   - Option B: Run 'vercel --prod' (requires Vercel CLI)"
    echo ""
    echo "Don't forget to add environment variables in Vercel Dashboard!"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Deployment blocked due to $ERRORS error(s)${NC}"
    echo ""
    echo "Please fix the errors above before deploying."
    echo ""
    
    if [ $ERRORS -gt 0 ]; then
        echo "Common fixes:"
        echo "- Missing environment variables? Copy .env.example to .env.local"
        echo "- TypeScript errors? Run: npm run type-check"
        echo "- Build errors? Run: npm run build"
        echo "- Missing dependencies? Run: npm install"
    fi
    echo ""
    exit 1
fi
