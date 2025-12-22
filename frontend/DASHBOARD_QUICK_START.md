# PulseB2B Global Dashboard - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
✅ Node.js 18+ installed  
✅ Frontend dependencies installed (`npm install`)  
✅ Supabase project with `oracle_predictions` table  
✅ Environment variables configured  

---

## 📦 Installation

All dependencies have been added to `package.json`. Run:

```bash
cd frontend
npm install
```

**New packages installed:**
- @tanstack/react-table (tables)
- @radix-ui/* (UI primitives)
- swr (real-time data)
- framer-motion (animations)
- recharts (charts)
- tailwind-merge (utility merging)
- next-themes (dark mode)

---

## 🏗️ Project Structure

```
frontend/src/
├── components/
│   ├── SignalTable.tsx              ← Main data table
│   ├── CompanyProfileModal.tsx      ← Slide-over company details
│   ├── SubscriptionModal.tsx        ← $49/mo pricing modal
│   └── ui/
│       ├── dialog.tsx               ← Radix Dialog component
│       ├── button.tsx               ← Button variants
│       ├── badge.tsx                ← Badge for tags
│       └── card.tsx                 ← Card layouts
├── hooks/
│   └── useFundingFeed.ts            ← SWR hook for real-time data
├── lib/
│   ├── cn.ts                        ← Tailwind class merger
│   └── supabase.ts                  ← Supabase client
└── app/
    └── dashboard/
        └── page.tsx                 ← Main dashboard page (to update)
```

---

## 🎯 Usage Examples

### 1. Basic Signal Table

```tsx
import { SignalTable } from "@/components/SignalTable"
import { useFundingFeed } from "@/hooks/useFundingFeed"

export default function DashboardPage() {
  const { signals, isLoading } = useFundingFeed()
  const isPremium = false // Replace with auth check

  return (
    <SignalTable 
      data={signals}
      isPremium={isPremium}
      onUpgrade={() => console.log("Open subscription modal")}
    />
  )
}
```

### 2. Company Profile Modal

```tsx
import { CompanyProfileModal } from "@/components/CompanyProfileModal"
import { useState } from "react"

function MyComponent() {
  const [selectedCompany, setSelectedCompany] = useState(null)
  const isPremium = false

  return (
    <>
      <button onClick={() => setSelectedCompany(company)}>
        View Details
      </button>

      {selectedCompany && (
        <CompanyProfileModal
          company={selectedCompany}
          isPremium={isPremium}
          open={!!selectedCompany}
          onClose={() => setSelectedCompany(null)}
          onUpgrade={() => console.log("Upgrade clicked")}
        />
      )}
    </>
  )
}
```

### 3. Subscription Modal

```tsx
import { SubscriptionModal } from "@/components/SubscriptionModal"
import { useState } from "react"

function MyComponent() {
  const [showSubscription, setShowSubscription] = useState(false)

  return (
    <>
      <button onClick={() => setShowSubscription(true)}>
        Upgrade to Premium
      </button>

      <SubscriptionModal
        open={showSubscription}
        onClose={() => setShowSubscription(false)}
      />
    </>
  )
}
```

### 4. Real-time Data Hooks

```tsx
import { 
  useFundingFeed,
  useCriticalSignals,
  useHighPrioritySignals,
  useCompanySignal 
} from "@/hooks/useFundingFeed"

// All signals (40+ score, 30s refresh)
const { signals, isLoading, refresh } = useFundingFeed()

// Critical signals (90+ score, 15s refresh)
const { signals: critical } = useCriticalSignals()

// High priority (60-89 score, 30s refresh)
const { signals: highPriority } = useHighPrioritySignals()

// Single company (60s refresh)
const { company } = useCompanySignal("company-id-here")

// Manual refresh
refresh()
```

---

## 🎨 Customization

### Change Table Columns

Edit `SignalTable.tsx` column definitions:

```tsx
const columns: ColumnDef<Company>[] = [
  {
    accessorKey: "company_name",
    header: "Company",
    cell: ({ row }) => {
      // Custom cell rendering
      return <span>{row.getValue("company_name")}</span>
    }
  },
  // Add more columns...
]
```

### Change Subscription Price

Edit `SubscriptionModal.tsx`:

```tsx
<span className="text-5xl font-bold">$49</span> {/* Change price here */}
```

### Change Paywall Threshold

Edit `SignalTable.tsx`:

```tsx
const isLocked = !isPremium && company.pulse_score >= 70 // Change 70 to new threshold
```

### Change Refresh Interval

Edit `useFundingFeed.ts`:

```tsx
export function useFundingFeed(options = {}) {
  const { refreshInterval = 30000 } = options // Change 30000 to new interval (ms)
  // ...
}
```

---

## 🔧 Configuration

### Environment Variables (.env.local)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Supabase Table Schema

Ensure your `oracle_predictions` table has these columns:

```sql
CREATE TABLE oracle_predictions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_name TEXT NOT NULL,
  pulse_score FLOAT NOT NULL,
  desperation_level TEXT CHECK (desperation_level IN ('CRITICAL', 'HIGH', 'MODERATE', 'LOW')),
  urgency TEXT,
  hiring_probability FLOAT,
  expansion_density FLOAT,
  tech_stack TEXT[],
  funding_amount BIGINT,
  funding_date DATE,
  last_seen TIMESTAMP DEFAULT NOW(),
  has_red_flags BOOLEAN DEFAULT FALSE,
  website_url TEXT,
  recommendation TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Required indexes
CREATE INDEX idx_pulse_score ON oracle_predictions(pulse_score DESC);
CREATE INDEX idx_last_seen ON oracle_predictions(last_seen DESC);
```

---

## 🐛 Troubleshooting

### Issue: "Cannot find module '@/lib/cn'"

**Solution**: Make sure `frontend/src/lib/cn.ts` exists with:

```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Issue: Table not rendering data

**Solution**: Check Supabase connection and table name:

```typescript
// In useFundingFeed.ts
const { data, error } = await supabase
  .from("oracle_predictions") // Verify table name
  .select("*")
  
console.log("Data:", data, "Error:", error) // Debug
```

### Issue: Animations not working

**Solution**: Ensure Framer Motion is installed:

```bash
npm install framer-motion
```

### Issue: Modal not closing

**Solution**: Check `onClose` handler is properly connected:

```tsx
<CompanyProfileModal
  open={!!selectedCompany}
  onClose={() => setSelectedCompany(null)} // Must reset state
/>
```

---

## 📊 Data Flow Diagram

```
User Opens Dashboard
       ↓
Next.js Server Component fetches initial data (SSR)
       ↓
Page renders with SignalTable
       ↓
SWR hook starts polling (30s interval)
       ↓
New data arrives → Table re-renders
       ↓
User clicks row → CompanyProfileModal opens
       ↓
User sees contact info (blurred if free user)
       ↓
User clicks "Upgrade" → SubscriptionModal opens
       ↓
User selects plan → Payment flow (future)
```

---

## 🎯 Feature Flags

You can add feature flags for gradual rollout:

```tsx
const FEATURES = {
  showContactInfo: isPremium,
  showGrowthChart: true,
  showTechStack: true,
  enableRealTimeUpdates: true,
  showSubscriptionModal: true,
}

// Use in components
{FEATURES.showGrowthChart && <GrowthChart />}
```

---

## 🚢 Deployment Checklist

Before deploying to production:

- [ ] Set environment variables in Vercel/hosting provider
- [ ] Test Supabase connection with production credentials
- [ ] Verify SWR polling doesn't exceed API rate limits
- [ ] Test all modals open/close correctly
- [ ] Test table sorting, search, pagination
- [ ] Test on mobile devices (responsive design)
- [ ] Add error boundaries for production errors
- [ ] Enable analytics tracking
- [ ] Set up error logging (Sentry)
- [ ] Test payment flow (Stripe integration)

---

## 📝 Common Tasks

### Add a new column to the table

1. Update `Company` interface in `SignalTable.tsx`
2. Add column definition to `columns` array
3. Add custom cell renderer if needed

### Change color scheme

Edit Tailwind classes throughout components:
- `bg-purple-500` → `bg-blue-500` (change primary color)
- `from-purple-500 to-blue-500` → new gradient colors

### Add authentication

1. Install Supabase Auth: `npm install @supabase/auth-helpers-nextjs`
2. Create auth context
3. Replace `isPremium` hardcoded value with auth check

### Integrate Stripe

1. Install: `npm install @stripe/stripe-js stripe`
2. Create checkout session in Server Action
3. Handle webhook for subscription updates
4. Update `isPremium` based on subscription status

---

## 🎓 Learning Resources

- **TanStack Table**: https://tanstack.com/table/latest
- **Radix UI**: https://www.radix-ui.com/
- **Shadcn/UI**: https://ui.shadcn.com/
- **SWR**: https://swr.vercel.app/
- **Recharts**: https://recharts.org/
- **Framer Motion**: https://www.framer.com/motion/

---

## 🆘 Getting Help

If you encounter issues:

1. Check browser console for errors
2. Verify Supabase connection (Network tab)
3. Check component props are correct types
4. Review DASHBOARD_IMPLEMENTATION.md for architecture details
5. Check GitHub issues for TanStack Table / Radix UI

---

## ✅ Quick Test

Run this to verify everything works:

```bash
cd frontend
npm run dev
```

Then visit `http://localhost:3000/dashboard` and check:

1. ✅ Table renders with data
2. ✅ Search box filters companies
3. ✅ Click row opens modal
4. ✅ Modal slides in from right
5. ✅ Contact info is blurred (free user)
6. ✅ Click "Upgrade" opens subscription modal
7. ✅ Close modal with X button or backdrop click

---

## 🎉 You're Ready!

All components are built and ready to integrate. Next steps:

1. **Create new dashboard route** at `frontend/src/app/signals/page.tsx`
2. **Import components**: SignalTable, SubscriptionModal
3. **Add Server Component** for initial data fetch
4. **Test the full flow** from table → profile → subscription

Happy coding! 🚀

---

**Built with ❤️ for PulseB2B**
