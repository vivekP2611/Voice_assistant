# Render Deployment Guide for Voice Assistant

## ✅ Files Ready for Deployment
- ✓ Procfile (Contains: web: gunicorn voice:app)
- ✓ requirements.txt (Updated with gunicorn)
- ✓ runtime.txt (Python 3.11.7)
- ✓ .env (Environment variables)
- ✓ .gitignore (Excludes cache, venv, etc)
- ✓ voice.py (Fixed to listen on 0.0.0.0:PORT)
- ✓ database.py (SQLite - works on Render)

## 🚀 Render Configuration (Copy Exactly)

### Build Command:
```
pip install -r requirements.txt
```

### Start Command:
```
gunicorn voice:app
```

### Environment Variables:
Leave empty or set these (optional for basic testing):
```
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-production-secret-key-here-123456789
```

## 🎯 Step-by-Step Deployment

1. Push code to GitHub (git push)
2. Go to https://render.com
3. Create new Web Service
4. Select your GitHub repo: vivekP2611/Voice_assistant
5. Fill in:
   - Name: voice-assistant
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn voice:app
   - Plan: Free
6. Click "Deploy"
7. Wait 2-3 minutes
8. Access at: https://voice-assistant-xxxxx.onrender.com

## ⚠️ Important Notes
- Database (voice_assistant.db) is created automatically on first run
- SQLite works perfectly on Render
- Free tier may have inactivity spindown (add Uptime Kuma to keep alive)
- Audio generation (gTTS) works on Render servers

## 🔧 If You Get Errors:
- Check Render Logs (Render Dashboard → Logs)
- Look for "Port binding error" - means START COMMAND is wrong
- Look for "ModuleNotFoundError" - means missing in requirements.txt
- All should be fixed now!
