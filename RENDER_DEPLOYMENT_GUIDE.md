# 🚀 Render Deployment Guide - Environment Variables

**Project:** ProjectPilot Backend  
**Platform:** Render.com  
**Last Updated:** 2026-05-12

---

## 📋 Environment Variables Reference

Based on your backend code analysis (`backend/app/core/config.py`), here are the **EXACT** environment variable names your application expects:

---

## 🔴 MANDATORY Variables (Required for Deployment)

### 1. **API Key** (CRITICAL)
```
Variable Name: openai_api_key
Value: sk-or-v1-YOUR_NEW_OPENROUTER_KEY_HERE
```

**Important Notes:**
- ⚠️ **Variable name is lowercase:** `openai_api_key` (NOT `OPENAI_API_KEY`)
- Your code checks for `openai_api_key` first, then falls back to `OPENAI_API_KEY`
- For OpenRouter: Use format `sk-or-v1-...`
- For OpenAI: Use format `sk-proj-...` or `sk-...`
- For Google Gemini: Use format `AIza...`

**Where to get it:**
- OpenRouter: https://openrouter.ai/keys
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey

---

### 2. **AI Model Name**
```
Variable Name: OPENAI_MODEL
Value: gpt-3.5-turbo
```

**Recommended Values:**
- For OpenRouter: `gpt-3.5-turbo`, `gpt-4`, `claude-3-sonnet`, `gemini-2.0-flash`
- For OpenAI: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`
- For Google Gemini: `gemini-2.0-flash`, `gemini-1.5-pro`

**Default if not set:** `gemini-2.0-flash`

---

### 3. **Secret Key** (CRITICAL for Security)
```
Variable Name: SECRET_KEY
Value: YOUR_SUPER_SECRET_RANDOM_STRING_HERE
```

**How to generate a secure key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
xK9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL
```

**⚠️ NEVER use the default value:** `changeme-in-production`

---

### 4. **CORS Origins**
```
Variable Name: ALLOWED_ORIGINS
Value: https://your-frontend-domain.vercel.app,https://your-frontend-domain.com
```

**Format:** Comma-separated list of allowed frontend URLs (NO SPACES)

**Examples:**
```
# Single domain
ALLOWED_ORIGINS=https://projectpilot.vercel.app

# Multiple domains
ALLOWED_ORIGINS=https://projectpilot.vercel.app,https://www.projectpilot.com

# Include localhost for testing (NOT recommended for production)
ALLOWED_ORIGINS=https://projectpilot.vercel.app,http://localhost:3000
```

---

## 🟡 RECOMMENDED Variables (Strongly Recommended for Production)

### 5. **Debug Mode**
```
Variable Name: DEBUG
Value: False
```

**Important:**
- Set to `False` in production for security
- Set to `True` only for development/debugging
- Default: `True` (not secure for production)

---

### 6. **Database URL** (Recommended for Production)
```
Variable Name: DATABASE_URL
Value: postgresql://user:password@host:port/database
```

**Options:**

**Option A: Use Render PostgreSQL (Recommended)**
1. Create a PostgreSQL database in Render
2. Render will automatically provide the `DATABASE_URL`
3. Link it to your web service

**Option B: Use SQLite (Not Recommended for Production)**
```
DATABASE_URL=sqlite:///./projectpilot.db
```
⚠️ SQLite is NOT recommended for production (data loss on restart)

**Option C: External PostgreSQL**
```
DATABASE_URL=postgresql://username:password@hostname:5432/dbname
```

---

## 🟢 OPTIONAL Variables (Can Use Defaults)

### 7. **Application Name**
```
Variable Name: APP_NAME
Value: ProjectPilot
```
**Default:** `ProjectPilot`

---

### 8. **Application Version**
```
Variable Name: APP_VERSION
Value: 1.0.0
```
**Default:** `1.0.0`

---

### 9. **JWT Algorithm**
```
Variable Name: JWT_ALGORITHM
Value: HS256
```
**Default:** `HS256` (recommended, no need to change)

---

### 10. **JWT Token Expiration**
```
Variable Name: ACCESS_TOKEN_EXPIRE_MINUTES
Value: 60
```
**Default:** `60` (1 hour)
**Options:** `30` (30 min), `120` (2 hours), `1440` (24 hours)

---

### 11. **Projects Directory**
```
Variable Name: PROJECTS_DIR
Value: ./generated_projects
```
**Default:** `./generated_projects`
**Note:** Render uses ephemeral storage, so generated files will be lost on restart unless you use persistent storage

---

## 📝 Complete Render Environment Variables Setup

### Step-by-Step Instructions:

1. **Go to your Render Dashboard**
   - Navigate to your web service
   - Click on "Environment" tab

2. **Add these variables ONE BY ONE:**

```bash
# ============================================================================
# MANDATORY VARIABLES (Add these first)
# ============================================================================

# 1. API Key (CRITICAL - Use your NEW key, not the exposed one)
openai_api_key=sk-or-v1-YOUR_NEW_KEY_HERE

# 2. AI Model
OPENAI_MODEL=gpt-3.5-turbo

# 3. Secret Key (Generate a new one!)
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# 4. CORS Origins (Replace with your actual frontend URL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app

# ============================================================================
# RECOMMENDED VARIABLES (Add these for production)
# ============================================================================

# 5. Debug Mode (Set to False for production)
DEBUG=False

# 6. Database URL (If using Render PostgreSQL, this is auto-provided)
# DATABASE_URL=postgresql://user:pass@host:5432/db
# (Skip this if linking Render PostgreSQL - it's automatic)

# ============================================================================
# OPTIONAL VARIABLES (Only add if you want to override defaults)
# ============================================================================

# 7. App Name (optional)
# APP_NAME=ProjectPilot

# 8. App Version (optional)
# APP_VERSION=1.0.0

# 9. JWT Settings (optional)
# JWT_ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=60

# 10. Projects Directory (optional)
# PROJECTS_DIR=./generated_projects
```

---

## ✅ Verification Checklist

Before deploying, verify:

- [ ] `openai_api_key` is set (lowercase, with your NEW key)
- [ ] `OPENAI_MODEL` is set to a valid model name
- [ ] `SECRET_KEY` is set to a strong random string (NOT the default)
- [ ] `ALLOWED_ORIGINS` includes your frontend URL
- [ ] `DEBUG` is set to `False`
- [ ] Database is configured (PostgreSQL recommended)

---

## 🔍 How Your Code Reads Environment Variables

Based on `backend/app/core/config.py`:

```python
# Your code checks in this order:
1. GEMINI_API_KEY (from Pydantic Settings)
2. openai_api_key (from os.getenv)
3. OPENAI_API_KEY (from os.getenv)

# For model name:
1. OPENAI_MODEL (from os.getenv)
2. GEMINI_MODEL (from Pydantic Settings)
3. Default: "gemini-2.0-flash"
```

**This means:**
- ✅ Use `openai_api_key` (lowercase) for the API key
- ✅ Use `OPENAI_MODEL` (uppercase) for the model name
- ✅ Both will work correctly with your code

---

## 🚨 Common Mistakes to Avoid

### ❌ WRONG:
```bash
# Wrong variable name (uppercase)
OPENAI_API_KEY=sk-or-v1-...

# Wrong: Using exposed key
openai_api_key=sk-or-v1-d44427a0aa30d890...

# Wrong: Using default secret
SECRET_KEY=changeme-in-production

# Wrong: Spaces in ALLOWED_ORIGINS
ALLOWED_ORIGINS=https://app1.com, https://app2.com

# Wrong: Debug mode in production
DEBUG=True
```

### ✅ CORRECT:
```bash
# Correct variable name (lowercase)
openai_api_key=sk-or-v1-YOUR_NEW_KEY

# Correct: New, secure key
openai_api_key=sk-or-v1-8e919c3fbeafe82b...

# Correct: Strong secret key
SECRET_KEY=xK9mP2vN8qR5tY7wZ3aB6cD1eF4gH0jL

# Correct: No spaces in ALLOWED_ORIGINS
ALLOWED_ORIGINS=https://app1.com,https://app2.com

# Correct: Debug off in production
DEBUG=False
```

---

## 🧪 Testing Your Deployment

After deploying to Render:

### 1. **Check Health Endpoint**
```bash
curl https://your-app.onrender.com/health
# Expected: {"status":"ok"}
```

### 2. **Check Root Endpoint**
```bash
curl https://your-app.onrender.com/
# Expected: {"app":"ProjectPilot","version":"1.0.0","status":"running","docs":"/docs"}
```

### 3. **Check API Documentation**
```
https://your-app.onrender.com/docs
```

### 4. **Check Logs in Render Dashboard**
Look for:
```
✅ "GeminiService ready | provider=OpenRouter model=gpt-3.5-turbo"
✅ "Starting ProjectPilot v1.0.0"
❌ "openai_api_key is not set" (means API key is missing)
```

---

## 📊 Summary Table

| Variable Name | Required? | Default Value | Your Value |
|--------------|-----------|---------------|------------|
| `openai_api_key` | ✅ MANDATORY | None | `sk-or-v1-...` |
| `OPENAI_MODEL` | ✅ MANDATORY | `gemini-2.0-flash` | `gpt-3.5-turbo` |
| `SECRET_KEY` | ✅ MANDATORY | `changeme-in-production` | Generate new! |
| `ALLOWED_ORIGINS` | ✅ MANDATORY | `http://localhost:3000` | Your frontend URL |
| `DEBUG` | 🟡 RECOMMENDED | `True` | `False` |
| `DATABASE_URL` | 🟡 RECOMMENDED | `sqlite:///./projectpilot.db` | PostgreSQL URL |
| `APP_NAME` | 🟢 OPTIONAL | `ProjectPilot` | (use default) |
| `APP_VERSION` | 🟢 OPTIONAL | `1.0.0` | (use default) |
| `JWT_ALGORITHM` | 🟢 OPTIONAL | `HS256` | (use default) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 🟢 OPTIONAL | `60` | (use default) |
| `PROJECTS_DIR` | 🟢 OPTIONAL | `./generated_projects` | (use default) |

---

## 🎯 Quick Copy-Paste for Render

**Minimum Required Variables:**
```bash
openai_api_key=sk-or-v1-YOUR_NEW_KEY_HERE
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=GENERATE_A_STRONG_RANDOM_KEY
ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
```

**With PostgreSQL:**
```bash
openai_api_key=sk-or-v1-YOUR_NEW_KEY_HERE
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=GENERATE_A_STRONG_RANDOM_KEY
ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## 📞 Troubleshooting

### Issue: "openai_api_key is not set"
**Solution:** Add `openai_api_key` (lowercase) to Render environment variables

### Issue: "API error 401 Unauthorized"
**Solution:** Your API key is invalid or expired. Generate a new one.

### Issue: "CORS error" in frontend
**Solution:** Add your frontend URL to `ALLOWED_ORIGINS`

### Issue: "Database connection failed"
**Solution:** Check `DATABASE_URL` format or link Render PostgreSQL

### Issue: "Internal Server Error"
**Solution:** Check Render logs for detailed error messages

---

## 🔗 Related Documentation

- `SECURITY.md` - Security best practices
- `DEPLOYMENT.md` - Full deployment guide
- `backend/.env.example` - Environment variables template
- `GIT_CLEANUP_COMPLETE.md` - Git security status

---

**Last Updated:** 2026-05-12  
**Version:** 1.0.0  
**Status:** ✅ READY FOR DEPLOYMENT
