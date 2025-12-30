# D-ID Real AI Avatar Setup Guide

## What You Get

✅ **Real human face** with natural expressions
✅ **Lip-sync** perfectly matched to speech
✅ **Emotional expressions** (asking, listening, thinking, happy, encouraging)
✅ **Professional quality** AI-generated talking avatar
✅ **Seamless integration** with your existing ElevenLabs voice

## Quick Setup (5 minutes)

### Step 1: Sign Up for D-ID

1. Go to [D-ID Studio](https://studio.d-id.com/)
2. Click **Sign Up** (Free trial available - 20 credits)
3. Verify your email

### Step 2: Get Your API Key

1. Go to [Account Settings](https://studio.d-id.com/account-settings)
2. Click on **API Key** tab
3. Click **Create API Key**
4. Copy your API key (starts with `Basic ...`)

### Step 3: Add API Key to Backend

Open `aibackend/.env` and add:

```env
DID_API_KEY=Basic_your_api_key_here
```

Replace `Basic_your_api_key_here` with your actual API key from D-ID.

### Step 4: Test It!

1. Start your backend:
   ```bash
   cd aibackend
   python3 main.py
   ```

2. Start your frontend:
   ```bash
   cd aifrontend
   npm run dev
   ```

3. Start an assessment - Lisa will now appear as a **real AI face** with lip-sync!

## How It Works

1. **Question Asked**: When Lisa asks a question, the text is sent to D-ID
2. **Video Generated**: D-ID creates a realistic video of Lisa speaking with perfect lip-sync
3. **Video Displayed**: The video plays in the avatar component
4. **Fallback**: If D-ID is not configured, it uses a professional static avatar image

## Pricing

| Plan | Credits/Month | Cost | Videos |
|------|---------------|------|--------|
| **Trial** | 20 credits | FREE | ~20 videos |
| **Lite** | 100 credits | $5.90 | ~100 videos |
| **Basic** | 500 credits | $29 | ~500 videos |
| **Pro** | 1500 credits | $89 | ~1500 videos |

**Note:** Each question = 1 video = ~1 credit

For 10 questions per assessment:
- Trial: 2 full assessments
- Lite: 10 assessments/month
- Basic: 50 assessments/month

## Customization Options

### Use Your Own Avatar Image

Replace the default avatar in `aibackend/app/services/did_avatar_service.py`:

```python
# Line 22 - Replace with your own image URL
self.lisa_avatar_url = "https://your-image-url.jpg"
```

**Requirements:**
- Professional headshot photo
- Clear face, looking at camera
- Good lighting
- JPG or PNG format
- Recommended: 512x512px or larger

### Adjust Emotions

The avatar supports these emotions:
- `neutral` - Default calm expression
- `happy` - Smiling, cheerful
- `serious` - Focused, professional
- `friendly` - Warm, welcoming

Emotions are automatically set based on Lisa's state:
- **Asking** → Curious, engaged
- **Listening** → Attentive
- **Thinking** → Thoughtful
- **Encouraging** → Supportive, positive

## Troubleshooting

### Avatar Not Showing

1. **Check API Key**: Make sure `DID_API_KEY` is set in `.env`
2. **Check Credits**: Log into D-ID dashboard to verify you have credits
3. **Check Console**: Look for errors in browser console (F12)
4. **Fallback Mode**: If D-ID fails, it automatically uses a static professional avatar

### Video Takes Too Long

- D-ID typically generates videos in 5-10 seconds
- The app shows a loading spinner while generating
- If it takes longer, check your internet connection

### API Errors

Common errors:
- `401 Unauthorized` → Check your API key
- `402 Payment Required` → Out of credits, upgrade plan
- `429 Too Many Requests` → Rate limit, wait a moment

## Alternative: Use Custom Videos

If you don't want to use D-ID, you can use pre-recorded videos:

1. Record 6 short videos of a person:
   - `lisa-neutral.mp4`
   - `lisa-asking.mp4`
   - `lisa-listening.mp4`
   - `lisa-thinking.mp4`
   - `lisa-happy.mp4`
   - `lisa-encouraging.mp4`

2. Place them in `aifrontend/public/avatars/`

3. Update `RealisticLisaAvatar.tsx` to use local videos instead of D-ID

## Production Deployment

For Vercel deployment, add environment variable:

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add: `DID_API_KEY` with your API key
3. Redeploy

For Render/other platforms, add the same environment variable.

## Support

- **D-ID Documentation**: https://docs.d-id.com/
- **D-ID Support**: support@d-id.com
- **Community**: https://discord.gg/d-id

## What's Next?

Once D-ID is set up, Lisa will have:
- ✅ Real human face
- ✅ Natural lip movements
- ✅ Emotional expressions
- ✅ Professional appearance
- ✅ Synchronized with voice

Your AI assessment platform will look incredibly professional and engaging!
