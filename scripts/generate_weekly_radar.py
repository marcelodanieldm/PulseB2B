import os
import requests
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_KEY']

regions = ['US', 'Canada', 'Argentina', 'Mexico', 'Chile', 'Uruguay', 'Colombia', 'Costa Rica']

# Get last Sunday
now = datetime.utcnow()
last_sunday = now - timedelta(days=now.weekday() + 1)
last_sunday_str = last_sunday.strftime('%Y-%m-%d')

leads_by_region = {}
for region in regions:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        },
        params={
            "region": f"eq.{region}",
            "created_at": f"gte.{last_sunday_str}",
            "order": "score.desc",
            "limit": 10
        }
    )
    leads_by_region[region] = resp.json() if resp.ok else []

# Generate PDF
pdf_path = "/tmp/weekly_radar.pdf"
c = canvas.Canvas(pdf_path, pagesize=letter)
y = 750
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y, "Weekly Radar Report")
y -= 30
c.setFont("Helvetica", 12)
for region, leads in leads_by_region.items():
    c.drawString(50, y, f"Region: {region}")
    y -= 20
    for lead in leads:
        c.drawString(70, y, f"{lead['company']} (Score: {lead['score']})")
        y -= 15
    y -= 10
c.save()

# Upload to Supabase Storage
with open(pdf_path, "rb") as f:
    resp = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/weekly_radar/{now.strftime('%Y-%m-%d')}.pdf",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/pdf"
        },
        data=f.read()
    )
    print("Upload status:", resp.status_code)
