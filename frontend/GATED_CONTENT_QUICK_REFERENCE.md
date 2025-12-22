# Gated Content Quick Reference

## 🚀 Quick Start (5 minutes)

```bash
# 1. Run setup script
cd frontend
./setup_gated_content.sh  # or setup_gated_content.bat on Windows

# 2. Add environment variables to .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_STRIPE_PAYMENT_LINK=https://buy.stripe.com/test_xxx

# 3. Update Supabase schema
# Run in Supabase SQL Editor:
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;

# 4. Start dev server
npm run dev
```

---

## 🔐 Usage Examples

### **Check Authentication**
```typescript
import { useAuth } from '@/hooks/useAuth';

const { user, isPremium, isAuthenticated, isLoading } = useAuth();

if (isLoading) return <LoadingSpinner />;
if (!isAuthenticated) return <LoginPrompt />;
if (isPremium) return <PremiumContent />;
```

### **Gate Content in Component**
```typescript
import { GatedContent } from '@/components/GatedContent';

<GatedContent
  isLocked={!isPremium}
  onUnlock={() => setShowModal(true)}
>
  <div>Sensitive content here</div>
</GatedContent>
```

### **Gate Table Column**
```typescript
import { GatedTableCell } from '@/components/GatedContent';

<GatedTableCell
  value={<a href={`mailto:${email}`}>{email}</a>}
  isLocked={!isPremium}
  onUnlock={() => setShowModal(true)}
  placeholder="•••@company.com"
/>
```

### **Gate Inline Text**
```typescript
import { GatedInline } from '@/components/GatedContent';

<p>
  Raised <GatedInline value="$50M" isLocked={!isPremium} onUnlock={handleUnlock} /> in funding
</p>
```

### **Show Premium Modal**
```typescript
import { UnlockPremiumModal } from '@/components/UnlockPremiumModal';

const [showModal, setShowModal] = useState(false);

<UnlockPremiumModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  stripePaymentLink={process.env.NEXT_PUBLIC_STRIPE_PAYMENT_LINK}
/>
```

---

## 🗄️ Database Queries

### **Check Premium Status**
```sql
SELECT email, is_premium FROM users WHERE email = 'user@example.com';
```

### **Grant Premium Access**
```sql
UPDATE users 
SET is_premium = TRUE, updated_at = NOW() 
WHERE email = 'user@example.com';
```

### **Revoke Premium Access**
```sql
UPDATE users 
SET is_premium = FALSE, updated_at = NOW() 
WHERE email = 'user@example.com';
```

### **List All Premium Users**
```sql
SELECT email, first_name, last_name, created_at 
FROM users 
WHERE is_premium = TRUE 
ORDER BY created_at DESC;
```

### **Count Premium vs Free**
```sql
SELECT 
  COUNT(CASE WHEN is_premium = TRUE THEN 1 END) as premium_users,
  COUNT(CASE WHEN is_premium = FALSE THEN 1 END) as free_users
FROM users;
```

---

## 🎨 CSS Classes Reference

### **Blur Effect**
```css
blur-sm          /* 4px blur (default) */
blur-md          /* 12px blur (stronger) */
blur-lg          /* 16px blur (strongest) */
```

### **Disable Interactions**
```css
pointer-events-none   /* Disables clicks */
select-none           /* Prevents text selection */
```

### **Gradient Buttons**
```css
bg-gradient-to-r from-amber-500 to-orange-500  /* Premium gold */
bg-gradient-to-r from-blue-500 to-purple-500   /* Tech blue */
```

---

## 🧪 Testing Commands

### **Test with Free User**
```sql
UPDATE users SET is_premium = FALSE WHERE email = 'test@example.com';
```
Expected: Email, phone, funding columns blurred with unlock buttons

### **Test with Premium User**
```sql
UPDATE users SET is_premium = TRUE WHERE email = 'test@example.com';
```
Expected: All columns visible, no blur, PREMIUM badge in header

### **Test Modal**
1. Visit dashboard as free user
2. Click any "Unlock" button
3. Verify modal opens with 6 features
4. Click "Upgrade to Premium Now"
5. Verify Stripe link opens in new tab

---

## 🔧 Customization Quick Tips

### **Change Gated Fields**
Edit `SignalTable.tsx`, add new column:
```typescript
{
  accessorKey: "new_field",
  header: "New Field",
  cell: ({ row }) => (
    <GatedTableCell
      value={row.original.new_field}
      isLocked={!isPremium}
      onUnlock={onUpgrade}
      placeholder="••••"
    />
  )
}
```

### **Change Pricing**
Edit `UnlockPremiumModal.tsx`:
```typescript
const pricingTier = {
  price: '$149',  // Change here
  period: 'month',
  // ...
};
```

### **Add Premium Feature**
Edit `UnlockPremiumModal.tsx`:
```typescript
const premiumFeatures = [
  {
    icon: NewIcon,
    title: 'New Feature',
    description: 'Description',
    badge: 'Hot',
  },
  // ...
];
```

---

## 🚨 Common Issues & Fixes

### **Columns not blurred**
```typescript
// Add console.log to debug
const { isPremium } = useAuth();
console.log('Premium status:', isPremium);  // Should be false for free users
```

### **Modal doesn't open**
```typescript
// Verify callback is passed
<SignalTable 
  onUpgrade={() => {
    console.log('Unlock clicked');
    setShowPremiumModal(true);
  }} 
/>
```

### **Stripe link broken**
```bash
# Check environment variable
echo $NEXT_PUBLIC_STRIPE_PAYMENT_LINK

# Should start with: https://buy.stripe.com/
```

### **Auth not working**
```typescript
// Check Supabase connection
const { data, error } = await supabase.auth.getSession();
console.log('Session:', data, 'Error:', error);
```

---

## 📊 Tracking & Analytics

### **Events to Track**
```typescript
// Track unlock button clicks
analytics.track('unlock_button_clicked', {
  column: 'email',
  isPremium: false,
  timestamp: new Date()
});

// Track modal opens
analytics.track('premium_modal_opened', {
  source: 'table_unlock_button'
});

// Track Stripe link clicks
analytics.track('upgrade_cta_clicked', {
  plan: 'premium',
  price: 99
});
```

### **Key Metrics**
- Unlock button CTR: `unlock_clicks / page_views`
- Modal conversion: `stripe_clicks / modal_opens`
- Overall conversion: `subscriptions / unlock_clicks`

---

## 🎯 A/B Test Ideas

### **Test 1: Button Copy**
```typescript
// Variant A
buttonText="Unlock Now"

// Variant B
buttonText="View Details"

// Variant C
buttonText="Get Premium Access"
```

### **Test 2: Pricing**
```typescript
// Variant A: $99/month
// Variant B: $79/month
// Variant C: $149/month
```

### **Test 3: Modal Timing**
```typescript
// Variant A: Immediate
onClick={() => setShowModal(true)}

// Variant B: 2-second delay
onClick={() => setTimeout(() => setShowModal(true), 2000)}
```

---

## 📞 Support

**Documentation:** [GATED_CONTENT_IMPLEMENTATION.md](GATED_CONTENT_IMPLEMENTATION.md)  
**Demo Component:** [GatedContentDemo.tsx](src/components/GatedContentDemo.tsx)  
**Setup Script:** `setup_gated_content.bat` or `setup_gated_content.sh`

---

## ✅ Pre-Launch Checklist

- [ ] Environment variables configured
- [ ] Supabase schema updated (is_premium column)
- [ ] Stripe payment link created
- [ ] Tested with free user (blurred columns)
- [ ] Tested with premium user (unlocked columns)
- [ ] Modal opens on unlock click
- [ ] Stripe link works in modal
- [ ] Analytics tracking implemented
- [ ] Premium badge shows for premium users
- [ ] Mobile responsive (test on phone)

**Ready to launch!** 🚀
