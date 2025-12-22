# 🚀 Deploy to Vercel - Quick Guide

## Prerequisites

- GitHub account
- Supabase project setup (see main README)
- Vercel account (free tier)

## Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Next.js 14 dashboard with Bento Grid"
git push origin main
```

## Step 2: Import to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect Next.js

## Step 3: Configure Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

**Where to find these:**
- Go to your Supabase project
- Settings → API
- Copy Project URL and anon/public key

## Step 4: Deploy

Click **Deploy** button. First deployment takes ~2-3 minutes.

## Step 5: Verify

Once deployed:

1. **Test the dashboard:**
   - Visit your Vercel URL (e.g., `your-project.vercel.app`)
   - Check that opportunity cards load
   - Verify blur effect on contact info

2. **Run Lighthouse:**
   - Open Chrome DevTools → Lighthouse
   - Run audit on mobile + desktop
   - Should score 95-100/100

3. **Check Supabase connection:**
   - Open browser console
   - Look for any Supabase errors
   - Verify data loads from database

## Step 6: Custom Domain (Optional)

1. Vercel Dashboard → Settings → Domains
2. Add your custom domain
3. Configure DNS records
4. Wait for SSL certificate (~10 minutes)

## Troubleshooting

### "Environment variables not found"

**Solution:** Make sure you added env vars in Vercel Dashboard, not `.env.local`

### "Supabase connection failed"

**Solutions:**
- Check Supabase project is not paused
- Verify anon key (not service_role key)
- Check Supabase URL format: `https://xxx.supabase.co`

### "Build failed"

**Solutions:**
- Check `package.json` dependencies match
- Run `npm install` locally first
- Verify `next.config.js` syntax

### "Low Lighthouse score"

**Solutions:**
- Enable production mode (not dev)
- Check image optimization is enabled
- Verify fonts are preloaded
- Check for console errors

## Performance Checklist

- ✅ Meta tags for SEO
- ✅ Font preconnect
- ✅ Image optimization (Next.js Image)
- ✅ Code splitting (automatic)
- ✅ CSS minification
- ✅ JavaScript minification
- ✅ Lazy loading (Suspense)
- ✅ Caching headers

## Post-Deployment

### Monitor Performance

```bash
# Install Vercel CLI
npm i -g vercel

# View analytics
vercel analytics

# View logs
vercel logs
```

### Update Deployment

```bash
# Push changes to GitHub
git push

# Auto-deploys on Vercel
# Check deployment status in dashboard
```

### Rollback if needed

1. Vercel Dashboard → Deployments
2. Find previous working deployment
3. Click "..." → Promote to Production

## Free Tier Limits

Vercel Free Tier includes:
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Preview deployments
- ✅ Analytics (basic)

## Next Steps

1. **Add authentication:**
   - Supabase Auth
   - NextAuth.js
   - Clerk

2. **Add analytics:**
   - Vercel Analytics
   - Google Analytics
   - PostHog

3. **Optimize further:**
   - Add service worker
   - Implement ISR (Incremental Static Regeneration)
   - Add Redis caching

---

**Deployment time:** ~5 minutes  
**Lighthouse score:** 95-100/100  
**Cost:** $0/month on free tier
