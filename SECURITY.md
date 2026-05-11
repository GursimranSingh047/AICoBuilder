# 🔒 Security & Environment Configuration Guide

## ⚠️ CRITICAL SECURITY NOTICE

**Your API keys were previously committed to Git history!**

### Immediate Actions Required:

1. **Revoke Exposed API Keys**
   - Go to your API provider (OpenRouter/OpenAI/Gemini)
   - Revoke the old API key immediately
   - Generate a new API key
   - Update your `.env` file with the new key

2. **Clean Git History** (Optional but Recommended)
   ```bash
   # WARNING: This rewrites Git history. Coordinate with your team first!
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push to remote (if you have permission)
   git push origin --force --all
   ```

---

## 📁 Environment Files Structure

```
projectpilot_backend-2/
├── backend/
│   ├── .env                 # ❌ NEVER commit (gitignored)
│   └── .env.example         # ✅ Safe to commit (template only)
└── frontend/
    ├── .env                 # ❌ NEVER commit (gitignored)
    └── .env.example         # ✅ Safe to commit (template only)
```

---

## 🚀 Local Development Setup

### Backend Setup

1. **Copy the example file:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```env
   # Get your API key from https://openrouter.ai/keys
   openai_api_key=sk-or-v1-YOUR_ACTUAL_KEY_HERE
   OPENAI_MODEL=gpt-3.5-turbo
   
   # Generate a secure secret key
   SECRET_KEY=your-super-secret-key-here
   ```

3. **Generate a secure SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Frontend Setup

1. **Copy the example file:**
   ```bash
   cd frontend
   cp .env.example .env
   ```

2. **The default values should work for local development:**
   ```env
   VITE_API_URL=http://localhost:8000
   ```

---

## 🌐 Production Deployment

### Backend Deployment (Render/Railway/Fly.io)

#### Option 1: Render.com

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add these variables:

```
openai_api_key=sk-or-v1-YOUR_PRODUCTION_KEY
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=YOUR_SECURE_SECRET_KEY
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

#### Option 2: Railway.app

1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Add the same variables as above

#### Option 3: Fly.io

```bash
# Set secrets via CLI
fly secrets set openai_api_key=sk-or-v1-YOUR_KEY
fly secrets set SECRET_KEY=YOUR_SECRET
fly secrets set DEBUG=False
```

### Frontend Deployment (Vercel/Netlify)

#### Option 1: Vercel

1. Go to your Vercel project
2. Settings → Environment Variables
3. Add:

```
VITE_API_URL=https://your-backend-domain.com
VITE_APP_NAME=ProjectPilot
VITE_ENABLE_ANALYTICS=true
```

4. Redeploy your application

#### Option 2: Netlify

1. Go to Site settings → Build & deploy → Environment
2. Add the same variables as Vercel
3. Trigger a new deploy

---

## 🔐 Security Best Practices

### ✅ DO:

- ✅ Use `.env` files for all secrets
- ✅ Keep `.env` in `.gitignore`
- ✅ Use different API keys for development and production
- ✅ Rotate API keys regularly
- ✅ Use strong, random SECRET_KEY values
- ✅ Set `DEBUG=False` in production
- ✅ Use HTTPS in production
- ✅ Limit CORS origins to your actual domains

### ❌ DON'T:

- ❌ Commit `.env` files to Git
- ❌ Share API keys in chat/email
- ❌ Use the same keys across environments
- ❌ Hardcode secrets in source code
- ❌ Expose backend API keys in frontend code
- ❌ Use weak SECRET_KEY values
- ❌ Leave DEBUG=True in production

---

## 🧪 Testing Your Setup

### Backend Test:
```bash
cd backend
source .venv/bin/activate
python -c "from app.core.config import settings; print(f'API Key loaded: {bool(settings.GEMINI_API_KEY)}')"
```

### Frontend Test:
```bash
cd frontend
npm run dev
# Check browser console for: import.meta.env.VITE_API_URL
```

### Full Integration Test:
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Open http://localhost:3000/generator
4. Try generating a project
5. Check if API calls work

---

## 📋 Environment Variables Reference

### Backend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `openai_api_key` | ✅ Yes | - | API key for AI provider |
| `OPENAI_MODEL` | ✅ Yes | `gpt-3.5-turbo` | AI model to use |
| `SECRET_KEY` | ✅ Yes | `changeme-in-production` | JWT secret key |
| `DEBUG` | No | `True` | Debug mode (set False in prod) |
| `DATABASE_URL` | No | `sqlite:///./projectpilot.db` | Database connection |
| `ALLOWED_ORIGINS` | No | `http://localhost:3000` | CORS allowed origins |

### Frontend Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ✅ Yes | `http://localhost:8000` | Backend API URL |
| `VITE_APP_NAME` | No | `ProjectPilot` | Application name |
| `VITE_ENABLE_ANALYTICS` | No | `true` | Enable analytics |

---

## 🆘 Troubleshooting

### "API key not configured" error
- Check if `.env` file exists in `backend/` directory
- Verify `openai_api_key` is set correctly
- Restart the backend server

### "Network Error" in frontend
- Check if `VITE_API_URL` matches your backend URL
- Verify backend is running
- Check CORS settings in backend

### "Invalid API key" error
- Your API key may be expired or revoked
- Generate a new key from your provider
- Update `.env` file and restart

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify all environment variables are set
3. Check server logs for detailed errors
4. Ensure API keys are valid and not expired

---

**Last Updated:** 2026-05-11
**Version:** 1.0.0
