# Deploy Lisa AI Frontend to Vercel

## Quick Fix for Root Directory Issue

The project has a monorepo structure with `aifrontend` and `aibackend` folders. Vercel needs to know to build from the `aifrontend` folder.

## Deployment Steps

### Option 1: Using Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/new
   - Import your GitHub repository: `adityadhimaann/ai-assessment-platform`

2. **Configure Build Settings**
   ```
   Framework Preset: Vite
   Root Directory: aifrontend (IMPORTANT!)
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   Node Version: 18.x
   ```

3. **Add Environment Variable**
   - Click "Environment Variables"
   - Add:
     ```
     Name: VITE_API_BASE_URL
     Value: https://your-backend-url.onrender.com/api
     ```
   - Replace with your actual Render backend URL

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes

### Option 2: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend folder
cd aifrontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Confirm settings
# - Deploy
```

### Option 3: Redeploy Current Failed Build

If you already created a project on Vercel:

1. Go to your project settings
2. Click "General"
3. Scroll to "Root Directory"
4. Set to: `aifrontend`
5. Click "Save"
6. Go to "Deployments"
7. Click "Redeploy" on the latest deployment

## After Deployment

### 1. Get Your Frontend URL
After successful deployment: `https://your-project.vercel.app`

### 2. Update Backend CORS (Important!)

Your backend needs to allow requests from your Vercel domain:

1. Go to Render dashboard
2. Select your backend service
3. Go to "Environment"
4. Add or update:
   ```
   ALLOWED_ORIGINS=https://your-project.vercel.app,http://localhost:5173
   ```
5. Save (service will redeploy)

### 3. Test Your Application

1. Visit your Vercel URL
2. Click "Start Assessment"
3. Select a topic
4. Answer questions
5. Hear Lisa's voice!

## Troubleshooting

### Build Still Fails

**Error**: `Cannot find package.json`

**Solution**: Make sure "Root Directory" is set to `aifrontend` in project settings

### Environment Variables Not Working

**Error**: API calls fail with CORS or 404

**Solution**:
1. Verify `VITE_API_BASE_URL` is set correctly
2. Must include `/api` at the end
3. Redeploy after adding variables

### Backend URL Not Set

**Error**: API calls go to localhost

**Solution**:
1. Get your Render backend URL
2. Add to Vercel environment variables
3. Format: `https://lisa-ai-backend.onrender.com/api`
4. Redeploy

## Vercel Configuration Files

The project includes:
- `/vercel.json` - Root config for monorepo
- `/aifrontend/vercel.json` - Frontend-specific config

Both are needed for proper deployment.

## Cost

- **Free Tier**: 100GB bandwidth, unlimited deployments
- **Pro**: $20/month for more bandwidth and features

## Next Steps

1. ✅ Set Root Directory to `aifrontend`
2. ✅ Add `VITE_API_BASE_URL` environment variable
3. ✅ Deploy
4. ✅ Update backend CORS settings
5. ✅ Test complete application

Your Lisa AI frontend is now live! 🚀
