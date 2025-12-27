import os
import requests

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

# Fetch top lead (score > 90)
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/leads",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    },
    params={
        "score": "gt.90",
        "order": "score.desc",
        "limit": 1
    }
)
lead = resp.json()[0] if resp.ok and resp.json() else None

if lead:
    message = f"🔥 Daily Signal: {lead['company']}\nScore: {lead['score']}\nRegion: {lead['region']}\nMore info: https://pulseb2b.com/lead/{lead['id']}"
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
    )
else:
    print("No lead found with score > 90.")
