# Deploy Lisa AI Backend to Render

This guide will help you deploy the Lisa AI backend to Render.

## Prerequisites

- GitHub account with your repository
- Render account (sign up at https://render.com)
- OpenAI API key
- ElevenLabs API key
- Lisa voice ID from ElevenLabs

## Deployment Steps

### Option 1: Deploy with render.yaml (Recommended)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect Your Repository**
   - Select "Connect a repository"
   - Choose your GitHub repository: `adityadhimaann/ai-assessment-platform`
   - Render will detect the `render.yaml` file

3. **Configure Environment Variables**
   
   Render will prompt you to set these secret variables:
   
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TTS_API_KEY=your_elevenlabs_api_key_here
   ELEVENLABS_VOICE_ID=your_lisa_voice_id_here
   ```

4. **Deploy**
   - Click "Apply"
   - Render will build and deploy your backend
   - Wait 5-10 minutes for the first deployment

5. **Get Your Backend URL**
   - After deployment, you'll get a URL like: `https://lisa-ai-backend.onrender.com`
   - Save this URL for frontend configuration

### Option 2: Manual Deployment

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect Repository**
   - Select your GitHub repository
   - Choose the `main` branch

3. **Configure Service**
   ```
   Name: lisa-ai-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: aibackend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Select Plan**
   - Choose "Free" plan (or paid for better performance)

5. **Add Environment Variables**
   
   Click "Advanced" → "Add Environment Variable":
   
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   TTS_API_KEY=your_elevenlabs_api_key_here
   TTS_SERVICE=elevenlabs
   ELEVENLABS_VOICE_ID=your_lisa_voice_id_here
   ELEVENLABS_MODEL_ID=eleven_turbo_v2
   DEV_MODE=false
   GPT_MODEL=gpt-4o
   LOG_LEVEL=INFO
   MAX_AUDIO_SIZE_MB=25
   SESSION_STORE_TYPE=memory
   ```

6. **Create Web Service**
   - Click "Create Web Service"
   - Wait for deployment to complete

## After Deployment

### 1. Test Your Backend

Visit these URLs (replace with your actual URL):

```bash
# Health check
https://lisa-ai-backend.onrender.com/health

# API documentation
https://lisa-ai-backend.onrender.com/docs

# Root endpoint
https://lisa-ai-backend.onrender.com/
```

### 2. Update Frontend Configuration

Update `aifrontend/.env`:

```env
VITE_API_BASE_URL=https://lisa-ai-backend.onrender.com/api
```

### 3. Redeploy Frontend

If your frontend is also on Render or Vercel:
- Update the environment variable
- Trigger a new deployment

## Important Notes

### Free Tier Limitations

- **Spin down after 15 minutes of inactivity**
  - First request after inactivity takes 30-60 seconds
  - Consider upgrading to paid plan for always-on service

- **750 hours/month free**
  - Enough for development and testing
  - Monitor usage in Render dashboard

### Performance Tips

1. **Keep Service Warm**
   - Use a service like UptimeRobot to ping your backend every 10 minutes
   - Prevents cold starts

2. **Upgrade to Paid Plan**
   - $7/month for always-on service
   - Better performance and no cold starts

3. **Use Redis for Sessions**
   - Add Redis database on Render
   - Update `SESSION_STORE_TYPE=redis`
   - Add `REDIS_URL` environment variable

## Monitoring

### View Logs

1. Go to your service in Render dashboard
2. Click "Logs" tab
3. Monitor real-time logs

### Check Metrics

1. Click "Metrics" tab
2. View:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

## Troubleshooting

### Build Fails

**Issue**: Dependencies fail to install

**Solution**:
```bash
# Check requirements.txt is valid
# Ensure Python version is 3.10+
```

### Service Won't Start

**Issue**: Application crashes on startup

**Solution**:
1. Check logs for errors
2. Verify all environment variables are set
3. Ensure API keys are valid

### API Calls Fail

**Issue**: OpenAI or ElevenLabs API errors

**Solution**:
1. Verify API keys are correct
2. Check API quotas/limits
3. Enable `DEV_MODE=true` for testing without API calls

### Cold Starts

**Issue**: First request is very slow

**Solution**:
1. Use UptimeRobot to keep service warm
2. Upgrade to paid plan
3. Accept 30-60s delay for free tier

## Updating Your Deployment

### Automatic Deploys

Render automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Render will detect the push and redeploy automatically.

### Manual Deploy

1. Go to your service in Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

## Custom Domain (Optional)

1. Go to service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `api.yourdomain.com`)
4. Update DNS records as instructed
5. SSL certificate is automatic

## Environment Variables Management

### Update Variables

1. Go to service → "Environment"
2. Edit or add variables
3. Click "Save Changes"
4. Service will automatically redeploy

### Secure Secrets

- Never commit API keys to GitHub
- Use Render's environment variables
- Rotate keys regularly

## Cost Estimation

### Free Tier
- **Cost**: $0/month
- **Limitations**: Spins down after 15 minutes
- **Best for**: Development, testing, demos

### Starter Plan
- **Cost**: $7/month
- **Benefits**: Always-on, no cold starts
- **Best for**: Production, small apps

### Standard Plan
- **Cost**: $25/month
- **Benefits**: More resources, better performance
- **Best for**: High-traffic production apps

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Test all endpoints
3. ✅ Update frontend with backend URL
4. ✅ Deploy frontend (Vercel/Netlify/Render)
5. ✅ Test full application
6. ✅ Monitor logs and performance

Your Lisa AI backend is now live! 🚀
