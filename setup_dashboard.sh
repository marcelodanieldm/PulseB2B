#!/bin/bash
# Setup script for PulseB2B Global Dashboard

echo "🚀 Setting up PulseB2B Global Dashboard..."

# Check Node.js version
echo "📦 Checking Node.js version..."
node_version=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)

if [ "$node_version" -lt 18 ]; then
    echo "❌ Node.js 18+ required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version OK: $(node -v)"

# Navigate to frontend directory
cd frontend || exit

# Install dependencies
echo "📥 Installing dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local from template..."
    cp .env.example .env.local
    echo ""
    echo "⚠️  IMPORTANT: Edit .env.local with your Supabase credentials!"
    echo ""
    echo "You need to add:"
    echo "  - NEXT_PUBLIC_SUPABASE_URL (from Supabase Settings → API)"
    echo "  - NEXT_PUBLIC_SUPABASE_ANON_KEY (from Supabase Settings → API)"
    echo ""
fi

# Install Vercel CLI (optional)
echo ""
read -p "📦 Install Vercel CLI for deployment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm install -g vercel
    echo "✅ Vercel CLI installed"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit frontend/.env.local with your Supabase credentials"
echo "2. Run 'cd frontend && npm run dev' to start development server"
echo "3. Visit http://localhost:3000/dashboard"
echo ""
echo "📖 Documentation:"
echo "  - Dashboard README: frontend/README_DASHBOARD.md"
echo "  - Deployment guide: frontend/DEPLOYMENT.md"
echo "  - Complete guide: frontend/IMPLEMENTATION_COMPLETE.md"
echo ""
echo "🚀 Ready to deploy? Run 'cd frontend && vercel --prod'"
