# 🚀 PulseB2B - Quick Deploy Card

## 15-Minute Deployment Checklist

### ✅ Step 1: Get API Keys (10 min)

#### Mapbox (2 min) - FREE 50k loads/month
```
1. Sign up: https://mapbox.com
2. Copy token: https://account.mapbox.com/access-tokens/
3. Format: pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOiJjbHZ...
```

#### Stripe (3 min) - FREE test mode
```
1. Sign up: https://stripe.com
2. Products → Add Product:
   - Name: PulseB2B Premium
   - Price: $299/month (or custom)
3. Create Payment Link → Copy URL
4. Format: https://buy.stripe.com/test_xxxxxxxxxxxxx
```

#### Supabase (5 min) - Already setup
```
1. Project → Settings → API
2. Copy URL: https://your-project.supabase.co
3. Copy anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### ✅ Step 2: Deploy to Vercel (5 min)

#### Option A: Dashboard (Easiest)
```
1. Go to: https://vercel.com
2. New Project → Import from GitHub
3. Root Directory: frontend
4. Add Environment Variables:
   - NEXT_PUBLIC_SUPABASE_URL
   - NEXT_PUBLIC_SUPABASE_ANON_KEY
   - NEXT_PUBLIC_MAPBOX_TOKEN
   - NEXT_PUBLIC_STRIPE_PAYMENT_LINK
5. Click "Deploy"
```

#### Option B: CLI (Fastest)
```bash
npm i -g vercel
vercel login
cd frontend
vercel

# Add environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
vercel env add NEXT_PUBLIC_MAPBOX_TOKEN production
vercel env add NEXT_PUBLIC_STRIPE_PAYMENT_LINK production

vercel --prod
```

---

## 🎯 Testing Checklist (5 min)

### Map Test
- [ ] Map loads (dark theme)
- [ ] Markers visible (US, Brazil, Mexico)
- [ ] Colors correct:
  - 🟢 Green (85%+)
  - 🟡 Amber (70-85%)
  - 🔵 Blue (50-70%)
  - ⚪ Gray (<50%)

### Premium Test
- [ ] Click 70%+ marker
- [ ] Paywall opens
- [ ] Pricing shows: $299/month, $2,868/year
- [ ] Stripe link opens

### Search Test
- [ ] Type "San Francisco" → Results filter
- [ ] Stats update
- [ ] Map stays interactive

---

## 🐛 Quick Fixes

### Map Blank
```bash
# Check Mapbox token
echo $NEXT_PUBLIC_MAPBOX_TOKEN
# Should start with 'pk.'
```

### No Data
```bash
# Test Supabase
curl https://YOUR-PROJECT.supabase.co/rest/v1/oracle_predictions \
  -H "apikey: YOUR-ANON-KEY"
# Should return JSON array
```

### Stripe 404
```
1. Stripe Dashboard → Payment Links
2. Verify link status: "Active"
3. Check URL format: https://buy.stripe.com/test_xxxxx
```

---

## 📊 Success Metrics (30 Days)

| Metric | Target | How to Track |
|--------|--------|-------------|
| Unique Visitors | 1,000+ | Vercel Analytics |
| Map Interactions | 200+ | GA4 Events |
| Paywall Views | 50+ | Console logs |
| Stripe Clicks | 10+ | Stripe Dashboard |

**If 10+ Stripe clicks → Build real auth system!**

---

## 💰 Cost (Hobby Plan)

| Service | Cost |
|---------|------|
| Vercel | $0/month |
| Supabase | $0/month |
| Mapbox | $0/month |
| Stripe (test) | $0/month |
| **Total** | **$0/month** 🎉 |

---

## 📞 Support

| Issue | Fix |
|-------|-----|
| Build errors | `rm -rf .next && npm run build` |
| TypeScript errors | `npm run type-check` |
| Environment variables | Check Vercel Dashboard → Settings → Environment Variables |

---

## 🎉 You're Live!

```
✅ Deployed to Vercel
✅ Map working
✅ Premium paywall active
✅ $0/month cost
✅ Ready for users!
```

**Share your URL:**  
`https://your-project.vercel.app`

**Next:** Track conversions for 30 days!

---

**Questions?** See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed guide.
