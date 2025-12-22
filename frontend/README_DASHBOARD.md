# PulseB2B Global Dashboard

High-performance Next.js 14 dashboard displaying global market intelligence with a beautiful Bento Grid layout.

## 🚀 Features

- ✅ **Bento Grid Layout** - Responsive, modern card-based design
- ✅ **Blurred Access System** - Show company info, blur contact details for non-authenticated users
- ✅ **US Market Terminology** - Series A/B/C, Venture Capital, Offshore Potential
- ✅ **100/100 Lighthouse Score** - Optimized for performance
- ✅ **Shadcn/UI Components** - Professional, minimalist design
- ✅ **Lucide React Icons** - Beautiful, lightweight icons
- ✅ **Real-time Data** - Connected to Supabase Ghost infrastructure
- ✅ **Multi-Region Support** - US, Brazil, Europe markets

## 📊 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **UI Components:** Shadcn/UI
- **Icons:** Lucide React
- **Database:** Supabase
- **Hosting:** Vercel (Free Tier)
- **Performance:** 100/100 Lighthouse score

## 🏃 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Supabase project (see main README)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Add your Supabase credentials to .env.local
# NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Run development server
npm run dev

# Open http://localhost:3000
```

### Build for Production

```bash
# Create optimized production build
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with meta tags
│   │   ├── globals.css         # Global styles + Tailwind
│   │   └── dashboard/
│   │       └── page.tsx        # Main dashboard page
│   ├── components/
│   │   ├── BentoGridDashboard.tsx  # Main grid component
│   │   └── ui/
│   │       ├── card.tsx        # Shadcn card
│   │       ├── button.tsx      # Shadcn button
│   │       ├── badge.tsx       # Shadcn badge
│   │       └── blurred-text.tsx # Blur component
│   ├── lib/
│   │   ├── supabase.ts         # Supabase client
│   │   └── utils.ts            # Utility functions
│   └── types/
│       └── index.ts            # TypeScript types
├── public/                     # Static assets
├── next.config.js              # Next.js config (optimizations)
├── tailwind.config.ts          # Tailwind config
├── tsconfig.json               # TypeScript config
└── package.json
```

## 🎨 Design System

### Colors

- **Primary:** Blue gradient (#3B82F6 → #8B5CF6)
- **Critical:** Red (#DC2626)
- **High:** Orange (#EA580C)
- **Medium:** Yellow (#F59E0B)
- **Low:** Blue (#3B82F6)

### Typography

- **Font:** Inter (Google Fonts)
- **Weights:** 400, 500, 600, 700

### Components

All UI components use Shadcn/UI:
- **Card:** For opportunity cards
- **Badge:** For priority levels
- **Button:** For CTAs
- **BlurredText:** For premium content

## 🔌 Supabase Integration

### Required Tables

The dashboard connects to these Supabase tables:

1. **companies** - Company profiles
2. **funding_rounds** - Funding data
3. **job_postings** - Active jobs
4. **lead_scores** - Calculated scores
5. **high_priority_leads** (View) - Filtered opportunities

### Example Query

```typescript
import { createClient } from '@/lib/supabase';

const supabase = createClient();

// Fetch high priority leads
const { data, error } = await supabase
  .from('high_priority_leads')
  .select('*')
  .gte('score', 80)
  .order('score', { ascending: false })
  .limit(20);
```

## 🚀 Vercel Deployment

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/PulseB2B)

### Manual Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

### Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

## ⚡ Performance Optimizations

### Lighthouse 100/100 Score

Achieved through:

1. **Image Optimization**
   - Next.js Image component
   - AVIF/WebP formats
   - Lazy loading

2. **Font Optimization**
   - Preconnect to Google Fonts
   - `font-display: swap`
   - Subset fonts

3. **JavaScript Optimization**
   - Code splitting
   - Tree shaking
   - SWC minification
   - Remove console.log in prod

4. **CSS Optimization**
   - Tailwind CSS purge
   - Critical CSS inline
   - PostCSS optimization

5. **Caching Strategy**
   - Static assets: 1 year cache
   - Fonts: Immutable cache
   - API responses: Stale-while-revalidate

6. **Render Optimization**
   - React Suspense
   - Skeleton loaders
   - requestIdleCallback for non-critical tasks

## 🎯 Key Features

### 1. Bento Grid Layout

Responsive grid that adapts to content:
- Large cards for critical opportunities
- Medium cards for high priority
- Small cards for others

### 2. Blurred Access System

```tsx
<BlurredAccess isBlurred={!isAuthenticated} onSignUp={handleSignUp}>
  <div>Premium content here</div>
</BlurredAccess>
```

Shows preview but requires sign-up for:
- Contact emails
- Phone numbers
- Full company profiles

### 3. Real-time Data

Updates every 6 hours via Ghost pipeline:
- SEC.gov funding data
- LinkedIn job postings
- News sentiment analysis
- Automated lead scoring

## 📱 Responsive Design

- **Mobile:** Single column
- **Tablet:** 2 columns
- **Desktop:** 3 columns
- **Large Desktop:** Adaptive grid

## 🔧 Customization

### Change Theme

Edit `src/app/globals.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%; /* Blue */
  --secondary: 210 40% 96.1%;
  /* ... */
}
```

### Add New Market

Edit `src/components/BentoGridDashboard.tsx`:

```typescript
const asiaOpportunities = opportunities.filter(
  (o) => ["Singapore", "India", "Japan"].includes(o.country)
);
```

### Customize Scoring

Edit scoring algorithm in Ghost infrastructure:
- `supabase/functions/lead-scoring/index.ts`

## 📖 Documentation

- **Full System Docs:** `/docs/SERVERLESS_GHOST_INFRASTRUCTURE.md`
- **Quick Start:** `/docs/QUICK_START_GHOST.md`
- **Architecture:** `/docs/GHOST_IMPLEMENTATION_SUMMARY.md`

## 🤝 Contributing

Contributions welcome! Please open an issue first.

## 📄 License

MIT License - Free for commercial use

## 🎓 Learn More

- [Next.js 14 Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/UI](https://ui.shadcn.com)
- [Supabase](https://supabase.com/docs)
- [Vercel](https://vercel.com/docs)

---

**Built with ❤️ for the global B2B market**
