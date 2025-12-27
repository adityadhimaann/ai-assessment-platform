# Quick Deploy to Render - 5 Minutes

## Step 1: Go to Render
Visit: https://dashboard.render.com/select-repo?type=blueprint

## Step 2: Connect Repository
- Click "Connect" next to `adityadhimaann/ai-assessment-platform`
- If not listed, click "Configure account" and grant access

## Step 3: Set Environment Variables
Render will ask for these secrets:

```
OPENAI_API_KEY = your_openai_key_here
TTS_API_KEY = your_elevenlabs_key_here  
ELEVENLABS_VOICE_ID = xccfcojYYGnqTTxwZEDU
```

## Step 4: Deploy
- Click "Apply"
- Wait 5-10 minutes

## Step 5: Get Your URL
After deployment completes, you'll see:
```
https://lisa-ai-backend.onrender.com
```

## Step 6: Test It
Visit:
```
https://lisa-ai-backend.onrender.com/docs
```

## Step 7: Update Frontend
Edit `aifrontend/.env`:
```
VITE_API_BASE_URL=https://lisa-ai-backend.onrender.com/api
```

## Done! 🎉

Your backend is live and ready to use!

---

**Note**: Free tier spins down after 15 minutes of inactivity. First request after inactivity takes 30-60 seconds to wake up.

**Upgrade to $7/month** for always-on service with no cold starts.
