#!/bin/bash
# Setup script for Ghost Infrastructure (Linux/macOS)

echo "🚀 Setting up Ghost Infrastructure..."

# Check Python version
echo "📦 Checking Python version..."
python3 --version || { echo "❌ Python 3.9+ required"; exit 1; }

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data for sentiment analysis..."
python3 << EOF
import nltk
nltk.download('vader_lexicon')
nltk.download('punkt')
print("✅ NLTK data downloaded")
EOF

# Check for Supabase CLI
echo "🔍 Checking for Supabase CLI..."
if ! command -v supabase &> /dev/null; then
    echo "⚠️  Supabase CLI not found. Installing..."
    npm install -g supabase
fi

# Verify installation
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Create Supabase project at https://supabase.com"
echo "2. Run database schema: supabase/schema.sql"
echo "3. Deploy Edge Functions:"
echo "   supabase functions deploy news-webhook"
echo "   supabase functions deploy lead-scoring"
echo "4. Add GitHub Secrets (SUPABASE_URL, SUPABASE_KEY)"
echo "5. Trigger workflow: Actions → Ghost Pipeline → Run workflow"
echo ""
echo "📖 Full documentation: docs/QUICK_START_GHOST.md"
