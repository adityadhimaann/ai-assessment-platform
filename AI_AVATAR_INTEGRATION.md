# AI Avatar Integration Guide

## Current Implementation

The app now uses `RealisticLisaAvatar` component with:
- ✅ Emotional states (neutral, asking, listening, thinking, happy, encouraging)
- ✅ Animated visual effects (rings, glows, audio waves)
- ✅ Smooth transitions between states
- ✅ Audio wave visualization when speaking
- ✅ Emotion indicators

## Upgrade to Real AI Video Avatar

To use a real AI face with lip-sync and emotions, you have several options:

### Option 1: D-ID (Recommended - Easy Integration)

**Features:**
- Realistic AI avatars with lip-sync
- Text-to-speech with facial animations
- Multiple avatar options
- Good pricing

**Integration Steps:**

1. Sign up at [D-ID](https://www.d-id.com/)

2. Get API key from dashboard

3. Add to backend `.env`:
```env
DID_API_KEY=your_did_api_key
```

4. Create backend endpoint (`aibackend/app/routers/avatar.py`):
```python
import requests
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/api/avatar/speak")
async def create_talking_avatar(text: str):
    """Generate talking avatar video with D-ID"""
    
    url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Bearer {os.getenv('DID_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "elevenlabs",
                "voice_id": "xccfcojYYGnqTTxwZEDU"  # Your Lisa voice
            }
        },
        "source_url": "https://your-avatar-image.jpg",  # Lisa's base image
        "config": {
            "stitch": True
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

5. Update `RealisticLisaAvatar.tsx`:
```typescript
const [videoUrl, setVideoUrl] = useState<string | null>(null);

useEffect(() => {
  if (isSpeaking && currentQuestion) {
    // Fetch video from D-ID
    fetch('/api/avatar/speak', {
      method: 'POST',
      body: JSON.stringify({ text: currentQuestion })
    })
    .then(res => res.json())
    .then(data => setVideoUrl(data.result_url));
  }
}, [isSpeaking, currentQuestion]);

// Replace img with video
<video 
  src={videoUrl || getAvatarSource()}
  autoPlay
  loop={!isSpeaking}
  className="w-full h-full object-cover"
/>
```

### Option 2: HeyGen

**Features:**
- Ultra-realistic avatars
- Custom avatar creation
- Multiple languages
- Premium quality

**Steps:**
1. Sign up at [HeyGen](https://www.heygen.com/)
2. Create custom avatar or use stock avatars
3. Use their API similar to D-ID
4. Pricing: ~$24/month for API access

### Option 3: Synthesia

**Features:**
- Professional AI avatars
- 140+ languages
- Custom avatar creation
- Enterprise-grade

**Steps:**
1. Sign up at [Synthesia](https://www.synthesia.io/)
2. Higher pricing but best quality
3. API integration available

### Option 4: Custom Video Files (Budget Option)

**If you want to avoid API costs:**

1. Record or generate 6 video clips of a person:
   - `lisa-neutral.mp4` - Idle state
   - `lisa-asking.mp4` - Asking question (nodding, curious)
   - `lisa-listening.mp4` - Listening (attentive)
   - `lisa-thinking.mp4` - Processing (thoughtful)
   - `lisa-happy.mp4` - Celebrating (smiling)
   - `lisa-encouraging.mp4` - Encouraging (thumbs up)

2. Place in `aifrontend/public/avatars/`

3. Update `RealisticLisaAvatar.tsx`:
```typescript
const getAvatarSource = () => {
  const videos = {
    neutral: "/avatars/lisa-neutral.mp4",
    asking: "/avatars/lisa-asking.mp4",
    listening: "/avatars/lisa-listening.mp4",
    thinking: "/avatars/lisa-thinking.mp4",
    happy: "/avatars/lisa-happy.mp4",
    encouraging: "/avatars/lisa-encouraging.mp4"
  };
  
  return videos[currentEmotion];
};

// Use video element
<video 
  src={getAvatarSource()}
  autoPlay
  loop
  muted
  playsInline
  className="w-full h-full object-cover"
/>
```

### Option 5: Ready Player Me (3D Avatar)

**Features:**
- 3D customizable avatars
- Free tier available
- Good for gaming/interactive apps

**Steps:**
1. Create avatar at [Ready Player Me](https://readyplayer.me/)
2. Get avatar GLB file
3. Use Three.js or React Three Fiber
4. Animate with morph targets

## Recommended Approach

**For Production:**
1. Start with **D-ID** - Best balance of quality, ease, and cost
2. Use your existing ElevenLabs voice for consistency
3. Create a professional photo of "Lisa" as the base avatar
4. D-ID will animate it with lip-sync

**For Development/Testing:**
- Current implementation with animated SVG avatars works great
- Add custom video files when ready
- Upgrade to D-ID when launching

## Cost Comparison

| Service | Monthly Cost | Quality | Ease |
|---------|-------------|---------|------|
| D-ID | $5-50 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| HeyGen | $24+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Synthesia | $89+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Custom Videos | $0 | ⭐⭐⭐ | ⭐⭐⭐ |
| Ready Player Me | Free-$10 | ⭐⭐⭐ | ⭐⭐⭐ |

## Next Steps

1. Choose your avatar solution
2. Get API keys if using a service
3. Update backend with avatar generation endpoint
4. Update frontend to use video instead of static images
5. Test with different emotions and questions

The current implementation is production-ready and looks professional. Upgrade to video avatars when you're ready to take it to the next level!
