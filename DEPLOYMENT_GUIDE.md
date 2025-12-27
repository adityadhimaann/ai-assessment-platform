# Complete Deployment Guide - Lisa AI Platform

## Overview

This guide covers deploying:
- **Backend**: FastAPI on Render
- **Frontend**: React on Vercel

## Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### Step 2: Deploy Backend
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `adityadhimaann/ai-assessment-platform`
4. Configure:
   ```
   Name: lisa-ai-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: aibackend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

5. Add Environment Variables:
   ```
   OPENAI_API_KEY=your_openai_key
   TTS_API_KEY=your_elevenlabs_key
   TTS_SERVICE=elevenlabs
   ELEVENLABS_VOICE_ID=xccfcojYYGnqTTxwZEDU
   ELEVENLABS_MODEL_ID=eleven_turbo_v2
   DEV_MODE=false
   GPT_MODEL=gpt-4o
   LOG_LEVEL=INFO
   MAX_AUDIO_SIZE_MB=25
   SESSION_STORE_TYPE=memory
   ```

6. Click "Create Web Service"
7. Wait 5-10 minutes for deployment
8. **Save your backend URL**: `https://lisa-ai-backend.onrender.com`

### Step 3: Test Backend
Visit: `https://lisa-ai-backend.onrender.com/docs`

You should see the API documentation.

## Part 2: Deploy Frontend to Vercel

### Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### Step 2: Import Project
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select `adityadhimaann/ai-assessment-platform`
4. Configure:
   ```
   Framework Preset: Vite
   Root Directory: aifrontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

### Step 3: Add Environment Variable
1. Click "Environment Variables"
2. Add:
   ```
   Name: VITE_API_BASE_URL
   Value: https://lisa-ai-backend.onrender.com/api
   ```
   (Replace with your actual Render backend URL)

3. Click "Deploy"
4. Wait 2-3 minutes

### Step 4: Get Your Frontend URL
After deployment: `https://lisa-ai-platform.vercel.app`

### Step 5: Test Complete Application
1. Visit your Vercel URL
2. Start an assessment
3. Answer a question
4. Hear Lisa's voice!

## Part 3: Update Backend CORS

After deploying frontend, update backend to allow your frontend domain:

1. Go to Render dashboard
2. Select your backend service
3. Go to "Environment"
4. Add:
   ```
   ALLOWED_ORIGINS=https://lisa-ai-platform.vercel.app
   ```
5. Save (service will redeploy)

## Troubleshooting

### Backend Issues

**Problem**: Backend won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Check API keys are valid

**Problem**: Cold starts (slow first request)
- Free tier spins down after 15 minutes
- Upgrade to $7/month for always-on
- Or use UptimeRobot to ping every 10 minutes

### Frontend Issues

**Problem**: 404 errors
- Check build logs in Vercel
- Verify `aifrontend` is set as root directory
- Check `vercel.json` is present

**Problem**: API calls fail
- Verify `VITE_API_BASE_URL` is correct
- Check backend is running
- Check CORS settings

**Problem**: Environment variables not working
- Redeploy after adding variables
- Variables must start with `VITE_`
- Check spelling and format

## Custom Domains (Optional)

### Backend (Render)
1. Go to service settings
2. Add custom domain: `api.yourdomain.com`
3. Update DNS records
4. SSL is automatic

### Frontend (Vercel)
1. Go to project settings
2. Add domain: `yourdomain.com`
3. Update DNS records
4. SSL is automatic

## Monitoring

### Backend (Render)
- View logs: Dashboard → Service → Logs
- View metrics: Dashboard → Service → Metrics
- Set up alerts: Dashboard → Service → Settings

### Frontend (Vercel)
- View deployments: Dashboard → Project → Deployments
- View analytics: Dashboard → Project → Analytics
- View logs: Click on deployment → View Function Logs

## Cost Summary

### Free Tier
- **Render Backend**: Free (with cold starts)
- **Vercel Frontend**: Free (100GB bandwidth)
- **Total**: $0/month

### Recommended Production
- **Render Backend**: $7/month (always-on)
- **Vercel Frontend**: Free
- **Total**: $7/month

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test complete application
4. ✅ Set up custom domain (optional)
5. ✅ Monitor usage and performance
6. ✅ Upgrade to paid plans as needed

## Support

- **Render**: https://render.com/docs
- **Vercel**: https://vercel.com/docs
- **GitHub Issues**: Create issue in your repository

Your Lisa AI platform is now live! 🚀
