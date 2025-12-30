# Firebase Configuration Guide

## Get Your Firebase Web App Config

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **unied-911e3**
3. Click the gear icon ⚙️ next to "Project Overview"
4. Select **Project Settings**
5. Scroll down to **Your apps** section
6. If you don't have a web app yet:
   - Click **Add app** button
   - Select **Web** (</> icon)
   - Register your app with a nickname (e.g., "Lisa AI Web")
   - Click **Register app**
7. You'll see your Firebase configuration object:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "unied-911e3.firebaseapp.com",
  projectId: "unied-911e3",
  storageBucket: "unied-911e3.firebasestorage.app",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

## Update Local .env File

Copy the values from Firebase Console and update `aifrontend/.env`:

```env
VITE_FIREBASE_API_KEY="AIza..."
VITE_FIREBASE_AUTH_DOMAIN="unied-911e3.firebaseapp.com"
VITE_FIREBASE_PROJECT_ID="unied-911e3"
VITE_FIREBASE_STORAGE_BUCKET="unied-911e3.firebasestorage.app"
VITE_FIREBASE_MESSAGING_SENDER_ID="123456789"
VITE_FIREBASE_APP_ID="1:123456789:web:abc123"
```

## Add to Vercel Environment Variables

1. Go to your Vercel project dashboard
2. Click **Settings** tab
3. Click **Environment Variables** in the left sidebar
4. Add each variable:
   - Name: `VITE_FIREBASE_API_KEY`
   - Value: Your API key from Firebase
   - Environment: Production, Preview, Development (select all)
   - Click **Save**
5. Repeat for all Firebase variables:
   - `VITE_FIREBASE_AUTH_DOMAIN`
   - `VITE_FIREBASE_PROJECT_ID`
   - `VITE_FIREBASE_STORAGE_BUCKET`
   - `VITE_FIREBASE_MESSAGING_SENDER_ID`
   - `VITE_FIREBASE_APP_ID`

## Redeploy on Vercel

After adding all environment variables:

1. Go to **Deployments** tab
2. Click the **...** menu on the latest deployment
3. Click **Redeploy**
4. Select **Use existing Build Cache** (optional)
5. Click **Redeploy**

## Important Notes

- Firebase config values are **NOT secrets** - they're safe to use in client-side code
- The security comes from Firebase Security Rules, not hiding these values
- Make sure your Firebase project has proper security rules configured
- The backend uses Firebase Admin SDK with service account credentials (already configured)

## Verify Deployment

After deployment succeeds:
1. Visit your Vercel URL
2. Open browser console (F12)
3. Look for: `✅ Firebase initialized successfully`
4. If you see errors, check that all env vars are set correctly in Vercel
