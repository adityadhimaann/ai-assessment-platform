# Vercel Deployment Fix for Lisa AI Frontend

## ⚠️ IMPORTANT: Set Root Directory First!

The build is failing because Vercel is trying to build from the wrong directory.

## Quick Fix (Do This First!)

1. Go to your Vercel project → **Settings** → **General**
2. Scroll to **Root Directory**
3. Click **Edit**
4. Enter: `aifrontend`
5. Click **Save**
6. Go to **Deployments** tab
7. Click **Redeploy** on the latest deployment

**This is the most important step!** Without setting the root directory, Vercel will try to build from the monorepo root and fail.

## Build Settings (After Setting Root Directory)

Once root directory is set to `aifrontend`, use these settings:

**Framework Preset:** Vite

**Build Command:** `npm run build` (default)

**Output Directory:** `dist` (default)

**Install Command:** `npm install` (default)

**Environment Variables:**
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
```

## Why This Happens

Your project is a monorepo with both `aifrontend` and `aibackend` folders. Vercel needs to know which folder to build. Without setting the root directory:
- Vercel tries to build from the repository root
- Path aliases like `@/lib/api-client` don't resolve correctly
- Build fails with "could not load" errors

## Alternative: Deploy from aifrontend Folder Only

If you keep having issues, the cleanest solution is:

1. Create a new Vercel project
2. When importing, select **only the aifrontend folder**
3. Or use Vercel CLI from the aifrontend directory:
   ```bash
   cd aifrontend
   vercel --prod
   ```

## After Successful Deployment

1. Get your Vercel URL: `https://your-project.vercel.app`
2. Update backend CORS to allow your Vercel domain
3. Test the application

## Still Having Issues?

If the build still fails after setting root directory:
1. Check that `aifrontend/package.json` exists
2. Check that `aifrontend/vite.config.ts` exists  
3. Try deleting the Vercel project and creating a new one with root directory set from the start

The root directory setting is crucial for monorepo projects!
