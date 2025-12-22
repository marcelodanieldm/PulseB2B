#!/bin/bash
# Telegram Bot Setup for Oracle Ghost
# Interactive script to create and configure Telegram bot

echo ""
echo "================================================================"
echo "🤖 TELEGRAM BOT SETUP - Oracle Ghost Alerts"
echo "================================================================"
echo ""
echo "This script will help you set up a FREE Telegram bot for"
echo "receiving critical lead alerts (Hiring Probability > 85%)."
echo ""
echo "================================================================"
echo ""

read -p "Press Enter to continue..."

echo ""
echo "================================================================"
echo "STEP 1: Create Your Telegram Bot"
echo "================================================================"
echo ""
echo "1. Open Telegram and search for '@BotFather'"
echo "2. Send /newbot command"
echo "3. Follow instructions to name your bot"
echo "   Example: 'My Oracle Ghost Bot'"
echo "4. Username must end in 'bot'"
echo "   Example: 'MyOracleGhostBot' or 'my_oracle_bot'"
echo ""
echo "BotFather will give you a TOKEN like:"
echo "  123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789"
echo ""
echo "Copy this token and paste it below:"
echo ""

read -p "Enter BOT TOKEN: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Token cannot be empty!"
    exit 1
fi

echo ""
echo "✅ Bot Token saved: ${BOT_TOKEN:0:10}..."
echo ""

echo "================================================================"
echo "STEP 2: Get Your Chat ID"
echo "================================================================"
echo ""
echo "1. Open Telegram and search for '@userinfobot'"
echo "2. Send /start command"
echo "3. The bot will reply with your User ID"
echo "   Example: 'Your user ID: 123456789'"
echo ""
echo "Alternatively, you can:"
echo "1. Search for your new bot in Telegram"
echo "2. Send /start to your bot"
echo "3. Visit: https://api.telegram.org/bot${BOT_TOKEN}/getUpdates"
echo "4. Look for \"chat\":{\"id\":123456789}"
echo ""

read -p "Enter CHAT ID: " CHAT_ID

if [ -z "$CHAT_ID" ]; then
    echo "❌ Chat ID cannot be empty!"
    exit 1
fi

echo ""
echo "✅ Chat ID saved: $CHAT_ID"
echo ""

echo "================================================================"
echo "STEP 3: Test Connection"
echo "================================================================"
echo ""
echo "Testing bot connection..."

python3 -c "import requests; r=requests.get('https://api.telegram.org/bot$BOT_TOKEN/getMe'); print('✅ Bot is valid!' if r.status_code==200 else '❌ Bot token invalid')"

echo ""
echo "Sending test message..."

python3 -c "import requests; r=requests.post('https://api.telegram.org/bot$BOT_TOKEN/sendMessage', json={'chat_id':'$CHAT_ID', 'text':'🔮 Oracle Ghost Bot activated! You will receive critical lead alerts here.'}); print('✅ Test message sent!' if r.status_code==200 else '❌ Message failed - check Chat ID')"

echo ""

echo "================================================================"
echo "STEP 4: Save Configuration"
echo "================================================================"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    touch .env
fi

# Remove old Telegram config if exists
grep -v "TELEGRAM_BOT_TOKEN" .env > .env.tmp || true
grep -v "TELEGRAM_CHAT_ID" .env.tmp > .env || true
rm -f .env.tmp

# Append new values
echo "TELEGRAM_BOT_TOKEN=$BOT_TOKEN" >> .env
echo "TELEGRAM_CHAT_ID=$CHAT_ID" >> .env

echo ""
echo "✅ Configuration saved to .env file"
echo ""

echo "================================================================"
echo "STEP 5: GitHub Secrets (For Automation)"
echo "================================================================"
echo ""
echo "To use with GitHub Actions, add these as secrets:"
echo ""
echo "1. Go to: https://github.com/YOUR_USERNAME/PulseB2B/settings/secrets/actions"
echo "2. Click 'New repository secret'"
echo "3. Add two secrets:"
echo ""
echo "   Name: TELEGRAM_BOT_TOKEN"
echo "   Value: $BOT_TOKEN"
echo ""
echo "   Name: TELEGRAM_CHAT_ID"
echo "   Value: $CHAT_ID"
echo ""

echo "================================================================"
echo "✅ SETUP COMPLETE!"
echo "================================================================"
echo ""
echo "Your Telegram bot is ready! 🎉"
echo ""
echo "📱 Bot Token: ${BOT_TOKEN:0:15}..."
echo "💬 Chat ID: $CHAT_ID"
echo ""
echo "🔔 You will now receive alerts when:"
echo "   • Companies exceed 85% hiring probability"
echo "   • Daily summary of Oracle Ghost runs"
echo ""
echo "🧪 Test the notifier manually:"
echo "   python3 scripts/telegram_notifier.py"
echo ""
