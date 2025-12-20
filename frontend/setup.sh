#!/bin/bash

# PulseB2B Frontend Setup Script
# Automatiza la instalación y configuración del dashboard

set -e

echo "🚀 PulseB2B Frontend Setup"
echo "=========================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓ Node.js detected: $(node --version)${NC}"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ npm detected: $(npm --version)${NC}"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "🔧 Creating .env.local..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠️  Please edit .env.local with your credentials:${NC}"
    echo "   - NEXT_PUBLIC_MAPBOX_TOKEN (required for map)"
    echo "   - NEXT_PUBLIC_SUPABASE_URL (optional - uses mock data if not set)"
    echo "   - NEXT_PUBLIC_SUPABASE_ANON_KEY (optional)"
    echo ""
else
    echo -e "${GREEN}✓ .env.local already exists${NC}"
    echo ""
fi

# Check if Mapbox token is set
if [ -f .env.local ]; then
    source .env.local
    if [ -z "$NEXT_PUBLIC_MAPBOX_TOKEN" ] || [ "$NEXT_PUBLIC_MAPBOX_TOKEN" = "your_mapbox_token_here" ]; then
        echo -e "${YELLOW}⚠️  Mapbox token not configured${NC}"
        echo "Get your free token at: https://account.mapbox.com/"
        echo ""
    else
        echo -e "${GREEN}✓ Mapbox token configured${NC}"
    fi
fi

# Run type check
echo "🔍 Running TypeScript type check..."
npm run type-check

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Type check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Type check failed (this is okay for initial setup)${NC}"
fi

echo ""
echo "=========================="
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env.local with your Mapbox token"
echo "2. Run: npm run dev"
echo "3. Open: http://localhost:3000"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICK_START.md"
echo "   - Full Docs: README.md"
echo ""
echo "Happy coding! 🎉"
