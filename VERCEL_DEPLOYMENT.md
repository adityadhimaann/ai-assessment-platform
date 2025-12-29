# Vercel Deployment Fix for Lisa AI Frontend

## Problem
Vercel is running out of memory because it's installing dependencies multiple times due to the monorepo structure.

## Solution

### Option 1: Set Root Directory in Vercel Dashboard (Recommended)

1. Go to your Vercel project settings
2. Navigate to **Settings** → **General**
3. Find **Root Directory**
4. Set it to: `aifrontend`
5. Click **Save**
6. Go to **Deployments** and click **Redeploy**

This tells Vercel to treat `aifrontend` as the project root, avoiding the monorepo complexity.

### Option 2: Use Vercel CLI with Root Directory

```bash
cd aifrontend
vercel --prod
```

This deploys only the frontend folder.

### Option 3: Update Build Settings

If you can't change the root directory, update these settings in Vercel:

**Build & Development Settings:**
- Framework Preset: `Vite`
- Build Command: `cd aifrontend && npm install && npm run build`
- Output Directory: `aifrontend/dist`
- Install Command: `npm install --prefix aifrontend`

**Environment Variables:**
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
```

## Why This Happens

The root `package.json` has scripts that run `cd aifrontend && npm install`, which causes:
1. Vercel runs `npm install` at root
2. Root package.json runs `cd aifrontend && npm install`
3. This happens multiple times, filling up memory

## Recommended Structure

For Vercel, the cleanest approach is:
- Set **Root Directory** to `aifrontend` in project settings
- This makes Vercel treat it as a standalone project
- No monorepo complexity, no memory issues

## After Deployment

Your frontend will be at: `https://your-project.vercel.app`

Don't forget to:
1. Update `VITE_API_BASE_URL` environment variable with your Render backend URL
2. Update backend CORS to allow your Vercel domain

## Alternative: Deploy Frontend Separately

If issues persist, consider:
1. Create a separate GitHub repo for just the `aifrontend` folder
2. Deploy that repo to Vercel
3. Much simpler, no monorepo issues

This is actually the recommended approach for production!
