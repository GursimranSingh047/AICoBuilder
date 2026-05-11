# 🚀 Deployment Guide - ProjectPilot

Complete guide for deploying ProjectPilot to production.

---

## 📋 Pre-Deployment Checklist

- [ ] All API keys are in `.env` files (not hardcoded)
- [ ] `.env` files are in `.gitignore`
- [ ] Old API keys from Git history have been revoked
- [ ] New API keys generated for production
- [ ] `DEBUG=False` set for production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database configured (PostgreSQL recommended)
- [ ] CORS origins updated for production domain

---

## 🎯 Deployment Options

### Option 1: Vercel (Frontend) + Render (Backend) ⭐ Recommended

#### Backend on Render.com

1. **Create Account & New Web Service**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**
   ```
   Name: projectpilot-backend
   Environment: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Add Environment Variables**
   Go to "Environment" tab and add:
   ```
   openai_api_key=sk-or-v1-YOUR_PRODUCTION_KEY
   OPENAI_MODEL=gpt-3.5-turbo
   SECRET_KEY=YOUR_SECURE_SECRET_KEY_HERE
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@host:5432/db
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment
   - Note your backend URL: `https://projectpilot-backend.onrender.com`

#### Frontend on Vercel

1. **Create Account & Import Project**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"
   - Import your GitHub repository

2. **Configure Project**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   ```

3. **Add Environment Variables**
   Go to Settings → Environment Variables:
   ```
   VITE_API_URL=https://projectpilot-backend.onrender.com
   VITE_APP_NAME=ProjectPilot
   VITE_ENABLE_ANALYTICS=true
   ```

4. **Deploy**
   - Click "Deploy"
   - Your app will be live at: `https://your-project.vercel.app`

---

### Option 2: Railway (Full Stack)

1. **Create Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy Backend**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login
   railway login
   
   # Initialize project
   cd backend
   railway init
   
   # Add environment variables
   railway variables set openai_api_key=sk-or-v1-YOUR_KEY
   railway variables set SECRET_KEY=YOUR_SECRET
   railway variables set DEBUG=False
   
   # Deploy
   railway up
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend
   railway init
   railway variables set VITE_API_URL=https://your-backend.railway.app
   railway up
   ```

---

### Option 3: Netlify (Frontend) + Fly.io (Backend)

#### Backend on Fly.io

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Or use install script
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login & Initialize**
   ```bash
   fly auth login
   cd backend
   fly launch
   ```

3. **Set Secrets**
   ```bash
   fly secrets set openai_api_key=sk-or-v1-YOUR_KEY
   fly secrets set SECRET_KEY=YOUR_SECRET
   fly secrets set DEBUG=False
   ```

4. **Deploy**
   ```bash
   fly deploy
   ```

#### Frontend on Netlify

1. **Create `netlify.toml` in frontend directory**
   ```toml
   [build]
     command = "npm run build"
     publish = "dist"
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

2. **Deploy via Netlify CLI**
   ```bash
   npm install -g netlify-cli
   cd frontend
   netlify deploy --prod
   ```

3. **Or Deploy via Dashboard**
   - Go to [netlify.com](https://netlify.com)
   - Drag & drop your `dist` folder
   - Add environment variables in Site settings

---

## 🗄️ Database Setup (Production)

### PostgreSQL on Render

1. **Create PostgreSQL Database**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Choose a name: `projectpilot-db`
   - Select region close to your backend

2. **Get Connection String**
   - Copy the "External Database URL"
   - Format: `postgresql://user:pass@host:5432/dbname`

3. **Update Backend Environment**
   - Add `DATABASE_URL` to your backend environment variables
   - Restart your backend service

4. **Run Migrations**
   ```bash
   # Connect to your backend shell
   # Tables will be created automatically on first run
   ```

---

## 🔒 Security Configuration

### 1. Update CORS Origins

In your backend `.env`:
```env
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-custom-domain.com
```

### 2. Set DEBUG to False

```env
DEBUG=False
```

### 3. Use Strong SECRET_KEY

```bash
# Generate a new one
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Enable HTTPS Only

Most platforms (Vercel, Render, Netlify) provide HTTPS automatically.

---

## 🧪 Post-Deployment Testing

### 1. Test Backend Health

```bash
curl https://your-backend.onrender.com/health
# Expected: {"status":"ok"}
```

### 2. Test API Docs

Visit: `https://your-backend.onrender.com/docs`

### 3. Test Frontend

1. Open your frontend URL
2. Try generating a project
3. Check browser console for errors
4. Verify API calls are going to production backend

### 4. Test Full Flow

1. Sign up for a new account
2. Generate a project
3. Download the project
4. Check activity tracking
5. View analytics

---

## 📊 Monitoring & Logs

### Render Logs

```bash
# View logs in dashboard or via CLI
render logs -s your-service-name
```

### Vercel Logs

```bash
# View logs in dashboard
vercel logs your-deployment-url
```

### Railway Logs

```bash
railway logs
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Automatic Deployment)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 🆘 Troubleshooting

### Backend Issues

**"Application failed to start"**
- Check logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` is complete

**"Database connection failed"**
- Verify `DATABASE_URL` is correct
- Check if database is running
- Ensure database allows external connections

### Frontend Issues

**"Network Error" when calling API**
- Verify `VITE_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running

**"Environment variables not working"**
- Ensure variables start with `VITE_`
- Rebuild and redeploy after adding variables
- Check build logs for errors

---

## 📈 Scaling Considerations

### Backend Scaling

- **Render**: Upgrade to paid plan for auto-scaling
- **Railway**: Increase resources in project settings
- **Fly.io**: Use `fly scale` command

### Database Scaling

- Start with smallest PostgreSQL instance
- Monitor query performance
- Add indexes for frequently queried fields
- Consider read replicas for high traffic

### Frontend Scaling

- Vercel/Netlify handle scaling automatically
- Use CDN for static assets
- Enable caching headers

---

## 💰 Cost Estimates

### Free Tier (Development)

- **Render**: Free tier available (sleeps after inactivity)
- **Vercel**: Free for personal projects
- **Netlify**: Free tier with 100GB bandwidth
- **Railway**: $5 credit/month free

### Production (Estimated Monthly)

- **Backend (Render)**: $7-25/month
- **Database (Render)**: $7-15/month
- **Frontend (Vercel)**: Free-$20/month
- **Total**: ~$15-60/month

---

## 📞 Support & Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs

---

**Last Updated:** 2026-05-11
**Version:** 1.0.0
