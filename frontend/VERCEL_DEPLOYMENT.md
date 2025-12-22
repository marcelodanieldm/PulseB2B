# PulseB2B Premium Dashboard - Vercel Deployment

## 🚀 Deploy to Vercel (Hobby Plan)

### Prerequisites
- GitHub account
- Vercel account (free Hobby plan)
- Supabase project
- Mapbox account (free tier)
- Stripe account (test mode)

---

## 📋 Step-by-Step Deployment

### 1. **Prepare Environment Variables**

Create `.env.local` in `/frontend`:

```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mapbox (Free Tier)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOiJjbHZ...

# Stripe (Test Mode)
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_xxxxxxxxxxxxx

# Optional: Analytics
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### 2. **Push to GitHub**

```bash
cd frontend
git add .
git commit -m "feat: Premium dashboard with Global Signal Map and Stripe integration"
git push origin main
```

### 3. **Deploy on Vercel**

#### Option A: Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

5. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_MAPBOX_TOKEN`
   - `NEXT_PUBLIC_STRIPE_PAYMENT_LINK`

6. Click "Deploy"

#### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: pulseb2b-dashboard
# - In which directory is your code located? ./
# - Want to override settings? No

# Add environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
vercel env add NEXT_PUBLIC_MAPBOX_TOKEN production
vercel env add NEXT_PUBLIC_STRIPE_PAYMENT_LINK production

# Deploy to production
vercel --prod
```

---

## 🗺️ Get Mapbox Token (Free)

### 1. Create Mapbox Account
- Go to [mapbox.com](https://www.mapbox.com/)
- Sign up (free tier includes 50,000 map loads/month)

### 2. Get Access Token
1. Navigate to [Account → Tokens](https://account.mapbox.com/access-tokens/)
2. Create new token or use default public token
3. Copy token starting with `pk.eyJ...`
4. Add to Vercel environment variables

### 3. Configure Token Permissions
- Public scopes needed:
  - ✅ `styles:read`
  - ✅ `fonts:read`
  - ✅ `datasets:read`

---

## 💳 Setup Stripe Payment Link (Test Mode)

### 1. Create Stripe Account
- Go to [stripe.com](https://stripe.com)
- Sign up (free forever, no credit card required for test mode)

### 2. Create Product
1. Dashboard → Products → Add Product
   - **Name**: PulseB2B Premium
   - **Description**: Unlimited access to premium venture data
   - **Pricing**: 
     - Monthly: $299/month
     - Annual: $2,868/year (save $720)

### 3. Create Payment Link
1. Products → PulseB2B Premium → Create payment link
2. Configure:
   - **Collect customer information**: Email address
   - **After payment**: Redirect to `https://your-domain.vercel.app/success`
   - **Test mode**: Enabled ✅
3. Copy payment link: `https://buy.stripe.com/test_xxxxxxxxxxxxx`

### 4. Add to Vercel
```bash
vercel env add NEXT_PUBLIC_STRIPE_PAYMENT_LINK production
# Paste: https://buy.stripe.com/test_xxxxxxxxxxxxx
```

### 5. Test Payment (Painted Door)
Use Stripe test card:
- **Card number**: `4242 4242 4242 4242`
- **Expiry**: Any future date
- **CVC**: Any 3 digits
- **ZIP**: Any 5 digits

---

## 🎨 Update Mapbox Styles (Optional)

### Dark Theme (Default)
```typescript
mapStyle="mapbox://styles/mapbox/dark-v11"
```

### Light Theme
```typescript
mapStyle="mapbox://styles/mapbox/light-v11"
```

### Satellite
```typescript
mapStyle="mapbox://styles/mapbox/satellite-streets-v12"
```

### Custom Style
1. Create custom style in [Mapbox Studio](https://studio.mapbox.com/)
2. Get style URL: `mapbox://styles/username/style-id`
3. Update [GlobalSignalMap.tsx](src/components/GlobalSignalMap.tsx#L186)

---

## 🔒 Supabase Row Level Security (RLS)

Enable RLS for `oracle_predictions` table:

```sql
-- Enable RLS
ALTER TABLE oracle_predictions ENABLE ROW LEVEL SECURITY;

-- Allow public read access (for anonymous users)
CREATE POLICY "Allow public read access"
ON oracle_predictions
FOR SELECT
TO anon, authenticated
USING (true);

-- Restrict premium data (hiring_probability >= 70)
-- This should be enforced in your app logic, not RLS
-- RLS should allow all reads, premium check happens client-side
```

---

## 📊 Analytics Setup (Optional)

### Google Analytics 4

1. Create GA4 property at [analytics.google.com](https://analytics.google.com)
2. Get Measurement ID (format: `G-XXXXXXXXXX`)
3. Add to [layout.tsx](src/app/layout.tsx):

```tsx
export const metadata = {
  // ... existing metadata
  openGraph: {
    // ... existing openGraph
  },
  other: {
    'google-site-verification': 'your-verification-code',
  },
};
```

4. Add Google Analytics script:

```tsx
// app/layout.tsx
import Script from 'next/script';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`}
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}');
          `}
        </Script>
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

## 🧪 Test Before Production

### Local Testing

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Test on http://localhost:3000
```

### Checklist

- [ ] Map loads successfully
- [ ] US, Brazil, Mexico markers visible
- [ ] Signal colors correct (green, amber, blue, gray)
- [ ] "Unlock Full Data" button triggers paywall
- [ ] Paywall shows pricing ($299/month, $2,868/year)
- [ ] Stripe link opens in new tab
- [ ] Search works (ventures, locations)
- [ ] Stats update correctly
- [ ] Mobile responsive
- [ ] Console has no errors

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Vercel Dashboard → Project → Settings → Domains
2. Add domain: `pulseb2b.com` or `app.pulseb2b.com`
3. Update DNS records (provided by Vercel):
   - Type: `A` | Name: `@` | Value: `76.76.21.21`
   - Type: `CNAME` | Name: `www` | Value: `cname.vercel-dns.com`
4. Wait for SSL certificate (automatic)

### Update Stripe Redirect
- Change redirect URL to your custom domain
- Stripe Dashboard → Payment Links → Edit → After payment → `https://pulseb2b.com/success`

---

## 🚨 Troubleshooting

### Issue: Map not loading

**Solution:**
```bash
# Check Mapbox token
echo $NEXT_PUBLIC_MAPBOX_TOKEN

# Verify token starts with 'pk.'
# Add to Vercel environment variables
```

### Issue: Supabase data not loading

**Solution:**
```bash
# Test Supabase connection
curl https://your-project.supabase.co/rest/v1/oracle_predictions \
  -H "apikey: your-anon-key"

# Check RLS policies
# Ensure anon role has SELECT permission
```

### Issue: Stripe link not working

**Solution:**
- Verify test mode enabled
- Check payment link URL format
- Ensure product is active
- Test with Stripe test card

### Issue: Build fails on Vercel

**Solution:**
```bash
# Check TypeScript errors locally
npm run type-check

# Check build locally
npm run build

# Fix errors and redeploy
```

---

## 📈 Performance Optimization

### Vercel Settings

- **Analytics**: Enable (Vercel Dashboard → Analytics)
- **Speed Insights**: Enable (automatic)
- **Image Optimization**: Enabled by default
- **Edge Functions**: Not needed (using Hobby plan)

### Next.js Optimizations

Already configured:
- ✅ Font optimization (Inter via Google Fonts)
- ✅ Image optimization (`next/image`)
- ✅ Code splitting (automatic)
- ✅ Static generation where possible

---

## 💰 Cost Breakdown

| Service | Plan | Monthly Cost | Usage |
|---------|------|-------------|-------|
| **Vercel** | Hobby (Free) | **$0** | Unlimited bandwidth |
| **Supabase** | Free Tier | **$0** | 500MB database, 1GB bandwidth |
| **Mapbox** | Free Tier | **$0** | 50,000 map loads |
| **Stripe** | Free | **$0** | Test mode (no processing) |
| **Total** | | **$0/month** 🎉 | |

**Production costs** (if scaled):
- Vercel Pro: $20/month (team features, analytics)
- Supabase Pro: $25/month (8GB database, 50GB bandwidth)
- Mapbox Pay-as-you-go: $0.50 per 1,000 loads after free tier
- Stripe: 2.9% + $0.30 per transaction (only if users pay)

---

## 🎯 Success Metrics

Track these metrics in your first 30 days:

1. **Unique visitors** (GA4)
2. **Map interactions** (click tracking)
3. **"Unlock Full Data" clicks** (Stripe payment link conversions)
4. **Search queries** (analytics)
5. **Time on page** (engagement)

### Painted Door Test Goal
- **Target**: 10+ Stripe checkout initiations
- **Success**: 5+ completed test payments
- **Conversion**: 2-5% visitor-to-checkout rate

If achieved → Real Stripe integration with MRR tracking

---

## ✅ Post-Deployment Checklist

- [ ] Production URL live
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] Mapbox map renders
- [ ] Supabase data loads
- [ ] Stripe payment link opens
- [ ] Mobile responsive tested
- [ ] SEO metadata verified
- [ ] Analytics tracking active
- [ ] Social media cards working
- [ ] Error monitoring enabled (Vercel)

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [Mapbox GL JS Documentation](https://docs.mapbox.com/mapbox-gl-js/)
- [Supabase Documentation](https://supabase.com/docs)
- [Stripe Payment Links](https://stripe.com/docs/payment-links)

---

**Deployment Time**: ~15 minutes  
**Monthly Cost**: $0 (Hobby plan)  
**Scalability**: Ready for 10,000+ monthly visitors  
**Status**: ✅ Production Ready
