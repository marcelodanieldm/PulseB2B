# 🌎 PulseB2B Premium Dashboard

> **Global Venture Intelligence Platform** - Real-time hiring signals and offshore potential analysis for US, Brazil, and Mexico ventures.

![Next.js](https://img.shields.io/badge/Next.js-14.0.4-black?logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3.3-blue?logo=typescript)
![Vercel](https://img.shields.io/badge/Vercel-Deployed-black?logo=vercel)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🗺️ **Global Signal Map**
- Interactive Mapbox GL map with custom styling
- Real-time venture markers colored by signal strength:
  - 🟢 **Green (85%+)**: Critical signals - Act now
  - 🟡 **Amber (70-85%)**: High potential - Priority follow-up
  - 🔵 **Blue (50-70%)**: Medium opportunity - Monitor
  - ⚪ **Gray (<50%)**: Low priority

### 🎯 **Professional Terminology**
- **Ventures** - Not "companies" (B2B positioning)
- **Runway** - Total funding available
- **Scalability** - Job velocity metric
- **Offshore Potential** - ML-scored hiring probability

### 💳 **Monetization (Painted Door Test)**
- "Unlock Full Data" button triggers premium paywall
- Stripe test mode payment link integration
- Two-tier pricing:
  - **Monthly**: $299/month
  - **Annual**: $2,868/year (save $720)
- Locks high-value data (70%+ signals) behind paywall

### 📊 **Real-Time Intelligence**
- Automated data pipeline via GitHub Actions (12h cycle)
- Live stats: Active Ventures, Critical Signals, Total Runway, Avg Scalability
- Search functionality (ventures, cities, countries)
- Export to CSV (premium feature)

### 🌐 **Target Markets**
- **United States** - Tech hubs (SF, NY, Austin, Seattle, Boston)
- **Brazil** - São Paulo, Rio, Belo Horizonte, Brasília
- **Mexico** - Mexico City, Guadalajara, Monterrey, Puebla

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm 9+
- Supabase account (free tier)
- Mapbox account (free tier - 50k loads/month)
- Stripe account (test mode)

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/PulseB2B.git
cd PulseB2B/frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your credentials
nano .env.local
```

### Environment Variables

```bash
# Supabase (Required)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mapbox (Required)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1IjoieW91ci11c2VybmFtZSIsImEiOiJjbHZ...

# Stripe (Required for paywall)
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_xxxxxxxxxxxxx

# Optional
NEXT_PUBLIC_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

---

## 📦 Tech Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Framework** | Next.js | 14.0.4 | React framework with SSR |
| **Language** | TypeScript | 5.3.3 | Type-safe JavaScript |
| **Styling** | Tailwind CSS | 3.4.0 | Utility-first CSS |
| **Maps** | Mapbox GL JS | 3.1.0 | Interactive maps |
| **Database** | Supabase | 2.39.3 | PostgreSQL + REST API |
| **Animation** | Framer Motion | 10.18.0 | Smooth animations |
| **Icons** | Lucide React | 0.303.0 | Beautiful icons |
| **State** | Zustand | 4.4.7 | Lightweight state management |
| **Payments** | Stripe | - | Payment processing (test mode) |
| **Deployment** | Vercel | - | Serverless hosting |

---

## 🎨 Components

### Core Components

#### `GlobalSignalMap`
```typescript
<GlobalSignalMap
  companies={filteredCompanies}
  onCompanySelect={setSelectedCompany}
  isPremium={isPremium}
  onUnlockClick={() => setShowPaywall(true)}
/>
```

**Features:**
- Mapbox GL integration with dark theme
- Country quick navigation (US, Brazil, Mexico)
- Signal strength legend
- Hover tooltips with venture details
- Click to view full company profile
- Premium data locking (70%+ signals)

#### `PremiumPaywall`
```typescript
<PremiumPaywall 
  isOpen={showPaywall} 
  onClose={() => setShowPaywall(false)} 
/>
```

**Features:**
- Animated modal with Framer Motion
- Free vs Premium feature comparison
- Monthly/Annual toggle
- Stripe payment link integration
- Conversion tracking (GA4 events)

### Utility Functions

#### `formatCurrency(amount, decimals)`
```typescript
formatCurrency(450, 1) // "$450.0M"
formatCurrency(1500, 1) // "$1.5B"
```

#### `formatPercentage(value, decimals)`
```typescript
formatPercentage(87.5, 1) // "87.5%"
```

---

## 📂 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css           # Tailwind imports + custom styles
│   │   ├── layout.tsx             # Root layout with metadata
│   │   └── page.tsx               # Premium dashboard (main page)
│   ├── components/
│   │   ├── GlobalSignalMap.tsx   # Interactive map component
│   │   └── PremiumPaywall.tsx    # Stripe paywall modal
│   ├── lib/
│   │   ├── supabase.ts           # Supabase client
│   │   └── utils.ts              # Helper functions
│   └── types/
│       └── index.ts              # TypeScript interfaces
├── public/
│   └── og-image.png              # Open Graph image (1200x630)
├── .env.example                  # Environment variables template
├── .env.local                    # Local environment (gitignored)
├── package.json                  # Dependencies
├── tailwind.config.ts            # Tailwind configuration
├── tsconfig.json                 # TypeScript configuration
├── next.config.js                # Next.js configuration
├── vercel.json                   # Vercel deployment config
├── VERCEL_DEPLOYMENT.md          # Deployment guide
└── README_PREMIUM.md             # This file
```

---

## 🔧 Configuration

### Mapbox Styles

Edit [GlobalSignalMap.tsx](src/components/GlobalSignalMap.tsx#L186):

```typescript
// Dark theme (default)
mapStyle="mapbox://styles/mapbox/dark-v11"

// Light theme
mapStyle="mapbox://styles/mapbox/light-v11"

// Satellite
mapStyle="mapbox://styles/mapbox/satellite-streets-v12"

// Custom
mapStyle="mapbox://styles/username/custom-style-id"
```

### Stripe Payment Link

Update [PremiumPaywall.tsx](src/components/PremiumPaywall.tsx#L23):

```typescript
const STRIPE_PAYMENT_LINK = 'https://buy.stripe.com/test_xxxxxxxxxxxxx';
```

Or use environment variable (recommended):

```typescript
const STRIPE_PAYMENT_LINK = process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK || 'fallback-url';
```

### Premium Threshold

Change the hiring probability threshold for premium locking:

```typescript
// In GlobalSignalMap.tsx
const isLocked = !isPremium && company.hiring_probability >= 70; // Change 70 to your threshold
```

---

## 🚢 Deployment

### Vercel (Recommended)

**Automatic deployment on push:**

1. Connect GitHub repository to Vercel
2. Configure:
   - Root Directory: `frontend`
   - Framework: Next.js
   - Build Command: `npm run build`
3. Add environment variables
4. Deploy!

See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed instructions.

### Manual Deployment

```bash
# Build production bundle
npm run build

# Test production build locally
npm run start

# Deploy to Vercel
vercel --prod
```

---

## 🧪 Testing

### Run Type Checks

```bash
npm run type-check
```

### Run Linter

```bash
npm run lint
```

### Test Locally

```bash
# Development mode (hot reload)
npm run dev

# Production mode (optimized)
npm run build && npm run start
```

### Test Checklist

- [ ] Map loads successfully
- [ ] Markers appear for US, Brazil, Mexico
- [ ] Signal colors correct (green, amber, blue, gray)
- [ ] Hover shows company tooltip
- [ ] Click marker shows full details
- [ ] "Unlock Full Data" button opens paywall
- [ ] Paywall shows pricing correctly
- [ ] Stripe link opens in new tab
- [ ] Search works (ventures, locations)
- [ ] Stats update correctly
- [ ] Mobile responsive (test on iPhone/Android)
- [ ] No console errors

---

## 🎯 User Flow

### 1. **Landing**
- User sees Global Signal Map with all ventures
- Stats bar shows: Active Ventures, Critical Signals, High Potential, Total Runway, Avg Scalability

### 2. **Exploration (Free)**
- View all venture locations
- See signal strength up to 70%
- Search by venture name, city, country
- Hover for basic details

### 3. **Premium Trigger**
- Click on 70%+ signal venture
- "Unlock Full Data" paywall appears

### 4. **Conversion (Painted Door)**
- See pricing: $299/month or $2,868/year
- Click "Unlock Premium Access"
- Redirect to Stripe test mode
- Complete test payment (4242 4242 4242 4242)

### 5. **Post-Conversion**
- Track conversion in analytics
- Measure interest (painted door test)
- If 10+ conversions → Build real auth system

---

## 💰 Pricing Strategy

### Free Tier
- ✅ View all venture locations
- ✅ See signal strength (up to 70%)
- ✅ Limited company details
- ❌ High-priority signals (70%+)
- ❌ Real-time Telegram alerts
- ❌ Export & API access

### Premium Tier ($299/month)
- ✅ Everything in Free
- ✅ **Critical signals (85%+)** with full details
- ✅ **Telegram alerts** for hot opportunities
- ✅ **Tech stack analysis** (50+ technologies)
- ✅ **CSV/JSON exports** (unlimited)
- ✅ **REST API access** (1000 req/day)

### Annual Discount
- $299/month = $3,588/year
- $2,868/year = $239/month (save $720/year = 20% discount)

---

## 📊 Analytics & Tracking

### Conversion Events (GA4)

```typescript
// Track paywall view
gtag('event', 'view_item', {
  items: [{ item_name: 'PulseB2B Premium' }]
});

// Track checkout initiation
gtag('event', 'begin_checkout', {
  currency: 'USD',
  value: 299,
  items: [{ item_name: 'Premium Monthly' }]
});
```

### Key Metrics

1. **Acquisition**
   - Unique visitors
   - Traffic sources (organic, referral, direct)

2. **Engagement**
   - Time on page
   - Map interactions (clicks, zooms)
   - Search queries

3. **Conversion**
   - Paywall views
   - Stripe checkout initiations
   - Test payments completed

4. **Retention** (post-auth)
   - Daily active users
   - Feature usage (export, API calls)

---

## 🐛 Troubleshooting

### Map Not Loading

**Issue**: Blank white screen where map should be

**Solution**:
```bash
# Check Mapbox token
echo $NEXT_PUBLIC_MAPBOX_TOKEN

# Verify token starts with 'pk.'
# Check browser console for errors
# Verify token has correct scopes (styles:read, fonts:read)
```

### Supabase Connection Failed

**Issue**: "Error loading ventures" message

**Solution**:
```bash
# Test Supabase connection
curl https://your-project.supabase.co/rest/v1/oracle_predictions \
  -H "apikey: your-anon-key" \
  -H "Authorization: Bearer your-anon-key"

# Check RLS policies (ensure anon can SELECT)
# Verify table name (oracle_predictions)
```

### Stripe Link Not Working

**Issue**: 404 or "Link expired" when clicking payment button

**Solution**:
- Verify payment link is in **test mode**
- Check URL format: `https://buy.stripe.com/test_xxxxxxxxxxxxx`
- Ensure product is **active** in Stripe Dashboard
- Test with Stripe test card: `4242 4242 4242 4242`

### Build Errors

**Issue**: `npm run build` fails

**Solution**:
```bash
# Clear cache
rm -rf .next node_modules
npm install

# Check TypeScript errors
npm run type-check

# Fix import errors
# Verify all environment variables are set
```

---

## 🔐 Security

### Environment Variables
- ✅ All secrets in `.env.local` (gitignored)
- ✅ Only `NEXT_PUBLIC_*` exposed to client
- ✅ Supabase service_role key NOT in frontend

### API Security
- ✅ Supabase Row Level Security (RLS) enabled
- ✅ Anon key rate limited (Supabase)
- ✅ CORS headers configured
- ✅ XSS protection headers (Vercel)

### Payment Security
- ✅ Stripe Checkout (PCI compliant)
- ✅ Test mode for painted door test
- ✅ No card data stored in frontend

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README_PREMIUM.md](./README_PREMIUM.md) | This file (overview) |
| [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) | Deployment guide |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | Original implementation notes |
| [QUICK_START.md](./QUICK_START.md) | Quick start guide |

---

## 🤝 Contributing

### Branch Strategy
- `main` - Production (Vercel auto-deploys)
- `develop` - Development
- `feature/*` - New features
- `fix/*` - Bug fixes

### Commit Convention
```
feat: Add Global Signal Map with Mapbox integration
fix: Resolve Stripe payment link redirection
docs: Update VERCEL_DEPLOYMENT.md with Mapbox setup
style: Format PremiumPaywall component
refactor: Extract signal color logic to utils
```

---

## 📄 License

MIT License - See [LICENSE](../LICENSE)

---

## 🎉 Success Criteria

### Phase 1: Launch (Week 1)
- [ ] Deploy to Vercel
- [ ] 100+ unique visitors
- [ ] 10+ map interactions
- [ ] 5+ paywall views

### Phase 2: Validation (Week 2-4)
- [ ] 500+ unique visitors
- [ ] 50+ search queries
- [ ] 20+ paywall views
- [ ] **10+ Stripe checkout initiations** 🎯

### Phase 3: Monetization (Month 2)
- [ ] Implement real Stripe integration
- [ ] Add authentication (Auth0/Clerk)
- [ ] Build API endpoints
- [ ] Enable CSV exports
- [ ] **First paying customer** 💰

---

**Built with ❤️ for global market intelligence**  
**Stack**: Next.js 14 + TypeScript + Tailwind + Mapbox + Supabase + Stripe  
**Deployed on**: Vercel (Hobby Plan - $0/month)  
**Status**: ✅ Production Ready
