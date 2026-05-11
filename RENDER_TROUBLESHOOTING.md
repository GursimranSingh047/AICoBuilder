# 🔧 Render Deployment Troubleshooting Guide

**Project:** ProjectPilot Backend  
**Platform:** Render.com  
**Last Updated:** 2026-05-12

---

## 🚨 Common Render Deployment Issues & Fixes

### Issue 1: Python 3.14 Compatibility Error ✅ FIXED

**Error Messages:**
```
- maturin
- metadata-generation-failed
- subprocess-exited-with-error
- Read-only file system
- Python 3.14
```

**Root Cause:**
- Render was using Python 3.14 (too new)
- Some dependencies don't have compatible wheels for Python 3.14
- Packages requiring compilation (like `psycopg2-binary`) fail on read-only filesystem

**✅ Solution Applied:**

1. **Created `backend/runtime.txt`:**
   ```
   python-3.11.9
   ```
   This locks Python to version 3.11.9 (stable and well-supported)

2. **Updated `backend/requirements.txt`:**
   - Added comments and organization
   - All dependencies are compatible with Python 3.11.9
   - Using `psycopg2-binary` (pre-compiled, no build needed)

3. **Created `backend/.renderignore`:**
   - Excludes unnecessary files from deployment
   - Reduces build time and deployment size

**Verification:**
- ✅ Python 3.11.9 is specified in `runtime.txt`
- ✅ All dependencies have wheels for Python 3.11.9
- ✅ No compilation required during build

---

### Issue 2: Missing Environment Variables

**Error Messages:**
```
- "openai_api_key is not set"
- "KeyError: 'SECRET_KEY'"
- "CORS error"
```

**✅ Solution:**

Add these environment variables in Render dashboard:

**Mandatory:**
```bash
openai_api_key=sk-or-v1-YOUR_KEY_HERE
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=YOUR_GENERATED_SECRET
ALLOWED_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
```

**See:** `RENDER_DEPLOYMENT_GUIDE.md` for complete list

---

### Issue 3: Database Connection Failed

**Error Messages:**
```
- "could not connect to server"
- "database does not exist"
- "SQLite database is locked"
```

**Root Cause:**
- SQLite doesn't work well on Render (ephemeral filesystem)
- PostgreSQL not configured

**✅ Solution:**

**Option A: Add PostgreSQL Database (Recommended)**
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Create database (free tier available)
3. Link database to your web service
4. Render automatically provides `DATABASE_URL`

**Option B: Use SQLite (Development Only)**
- SQLite works but data is lost on every restart
- Not recommended for production

---

### Issue 4: Build Command Fails

**Error Messages:**
```
- "pip install failed"
- "No module named 'X'"
- "Could not find a version that satisfies the requirement"
```

**✅ Solution:**

**Verify Render Configuration:**
```
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port 10000
```

**Check `requirements.txt`:**
- All packages are pinned to specific versions
- No conflicting dependencies
- All packages available on PyPI

---

### Issue 5: Application Won't Start

**Error Messages:**
```
- "Address already in use"
- "ModuleNotFoundError"
- "ImportError"
```

**✅ Solution:**

**Verify Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port 10000
```

**Important:**
- Port must be `10000` (Render's default)
- Host must be `0.0.0.0` (not `localhost` or `127.0.0.1`)
- Command runs from `backend/` directory

**Check Logs:**
```
Render Dashboard → Your Service → Logs
```

Look for:
- ✅ "Starting ProjectPilot v1.0.0"
- ✅ "GeminiService ready"
- ✅ "Application startup complete"

---

### Issue 6: Health Check Failing

**Error Messages:**
```
- "Health check failed"
- "Service is not responding"
- "502 Bad Gateway"
```

**✅ Solution:**

**Verify Health Check Endpoint:**
```bash
curl https://your-app.onrender.com/health
# Expected: {"status":"ok"}
```

**Check Render Configuration:**
```
Health Check Path: /health
```

**Common Causes:**
- Application not starting (check logs)
- Wrong port (must be 10000)
- Environment variables missing

---

### Issue 7: CORS Errors in Frontend

**Error Messages:**
```
- "Access-Control-Allow-Origin"
- "CORS policy blocked"
- "No 'Access-Control-Allow-Origin' header"
```

**✅ Solution:**

**Add Frontend URL to ALLOWED_ORIGINS:**
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

**Multiple Origins:**
```bash
ALLOWED_ORIGINS=https://app1.com,https://app2.com
```

**Important:**
- NO SPACES between URLs
- Use HTTPS in production
- Include all frontend domains

---

### Issue 8: Slow Build Times

**Symptoms:**
- Build takes 5+ minutes
- Timeout errors
- "Build exceeded time limit"

**✅ Solution:**

**Optimize Build:**

1. **Use `.renderignore`:**
   - Excludes unnecessary files
   - Reduces upload time

2. **Pin Dependencies:**
   - All versions are pinned in `requirements.txt`
   - Faster dependency resolution

3. **Use Binary Packages:**
   - `psycopg2-binary` instead of `psycopg2`
   - No compilation needed

4. **Upgrade Plan (if needed):**
   - Free tier: 512 MB RAM, slower builds
   - Starter tier: 512 MB RAM, faster builds
   - Standard tier: 2 GB RAM, much faster

---

### Issue 9: Application Crashes After Deploy

**Error Messages:**
```
- "Out of memory"
- "Killed"
- "Application exited"
```

**Root Cause:**
- Free tier: 512 MB RAM limit
- ML models (scikit-learn) can be memory-intensive

**✅ Solution:**

**Option A: Optimize Memory Usage**
```python
# In ml_service.py, load model lazily
# Only load when needed, not at startup
```

**Option B: Upgrade Plan**
- Starter: 512 MB RAM ($7/month)
- Standard: 2 GB RAM ($25/month)

**Option C: Disable ML Features**
```python
# Comment out ML model loading if not critical
```

---

### Issue 10: Files Not Persisting

**Symptoms:**
- Generated projects disappear after restart
- Database resets
- Uploaded files lost

**Root Cause:**
- Free tier has ephemeral filesystem
- Files are lost on every restart/deploy

**✅ Solution:**

**Option A: Use Persistent Disk (Paid)**
```yaml
# In render.yaml
disk:
  name: projectpilot-storage
  mountPath: /opt/render/project/src/backend/generated_projects
  sizeGB: 1
```
Cost: $0.25/GB/month

**Option B: Use External Storage**
- AWS S3
- Cloudinary
- Google Cloud Storage

**Option C: Use PostgreSQL**
- Store data in database instead of files
- Database is persistent (even on free tier)

---

## 🔍 Debugging Checklist

Before asking for help, verify:

### ✅ Configuration Files
- [ ] `backend/runtime.txt` exists with `python-3.11.9`
- [ ] `backend/requirements.txt` has all dependencies
- [ ] `backend/.env.example` is up to date
- [ ] `render.yaml` is in repository root (optional)

### ✅ Render Dashboard Settings
- [ ] Root Directory: `backend`
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
- [ ] Health Check Path: `/health`

### ✅ Environment Variables
- [ ] `openai_api_key` is set (lowercase!)
- [ ] `OPENAI_MODEL` is set
- [ ] `SECRET_KEY` is set (strong random string)
- [ ] `ALLOWED_ORIGINS` includes frontend URL
- [ ] `DEBUG` is set to `False`

### ✅ Health Checks
- [ ] `/health` endpoint returns `{"status":"ok"}`
- [ ] `/` endpoint returns app info
- [ ] `/docs` loads API documentation

### ✅ Logs
- [ ] No error messages in Render logs
- [ ] "Starting ProjectPilot" appears in logs
- [ ] "GeminiService ready" appears in logs
- [ ] No "ModuleNotFoundError" or "ImportError"

---

## 📊 Render Free Tier Limitations

Be aware of these limits:

| Resource | Free Tier Limit | Notes |
|----------|----------------|-------|
| RAM | 512 MB | May need optimization |
| CPU | Shared | Slower than paid tiers |
| Storage | Ephemeral | Files lost on restart |
| Build Time | ~15 minutes | Slower builds |
| Sleep | After 15 min inactivity | First request slow |
| Bandwidth | 100 GB/month | Usually sufficient |
| PostgreSQL | 90 days free | Then $7/month |

**Recommendations:**
- ✅ Free tier works for development/testing
- ✅ Upgrade to Starter ($7/month) for production
- ✅ Use PostgreSQL for data persistence
- ✅ Consider external storage for files

---

## 🧪 Testing Your Deployment

### 1. Health Check
```bash
curl https://your-app.onrender.com/health
# Expected: {"status":"ok"}
```

### 2. Root Endpoint
```bash
curl https://your-app.onrender.com/
# Expected: {"app":"ProjectPilot","version":"1.0.0",...}
```

### 3. API Documentation
```
https://your-app.onrender.com/docs
```

### 4. Test API Endpoint
```bash
curl -X POST https://your-app.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"testuser"}'
```

### 5. Check Logs
```
Render Dashboard → Your Service → Logs
```

Look for:
- ✅ "Starting ProjectPilot v1.0.0"
- ✅ "GeminiService ready | provider=OpenRouter"
- ✅ "Application startup complete"
- ❌ Any error messages

---

## 📞 Getting Help

### Render Support
- Documentation: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Project Documentation
- `RENDER_DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `RENDER_ENV_QUICK_REFERENCE.txt` - Environment variables
- `SECURITY.md` - Security best practices
- `DEPLOYMENT.md` - General deployment guide

### Common Commands
```bash
# View logs
render logs -s your-service-name

# Restart service
render restart -s your-service-name

# Check service status
render status -s your-service-name
```

---

## ✅ Success Indicators

Your deployment is successful when:

1. ✅ Build completes without errors
2. ✅ Service shows "Live" status in Render dashboard
3. ✅ Health check passes (green checkmark)
4. ✅ `/health` endpoint returns `{"status":"ok"}`
5. ✅ `/docs` loads API documentation
6. ✅ Logs show "Starting ProjectPilot"
7. ✅ No error messages in logs
8. ✅ Frontend can connect to backend
9. ✅ API requests work correctly
10. ✅ Database operations succeed

---

## 🎯 Quick Fix Summary

| Issue | Quick Fix |
|-------|-----------|
| Python 3.14 error | ✅ Created `runtime.txt` with `python-3.11.9` |
| Build fails | ✅ Updated `requirements.txt` with compatible versions |
| Missing env vars | ✅ Add in Render dashboard (see guide) |
| CORS error | ✅ Set `ALLOWED_ORIGINS` to frontend URL |
| Health check fails | ✅ Verify `/health` endpoint works |
| Database error | ✅ Link PostgreSQL or use SQLite (dev only) |
| Out of memory | ✅ Optimize code or upgrade plan |
| Files disappear | ✅ Use persistent disk or external storage |

---

**Your deployment should now work correctly!** 🚀

If you still encounter issues, check the Render logs for specific error messages and refer to the relevant section above.

---

**Last Updated:** 2026-05-12  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION READY
