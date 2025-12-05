# 🚀 Crypto-Steganography Deployment Guide

## 3. Configure deployment:
   - **Name**: `crypto-steganography-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install --upgrade pip && pip install -r Backend/requirements.txt`
   - **Start Command**: `cd Backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Starter` (free tier)ject Structure (Deployment Ready)
```
Crypto-Steganography/
├── Frontend/          # React app for Vercel deployment
├── Backend/           # FastAPI server for Render deployment  
├── .gitignore         # Excludes "Not used/" and sensitive files
├── render.yaml        # Render deployment configuration
├── Procfile           # Backup process file for Render
├── requirements.txt   # Root requirements (points to Backend/)
├── README.md          # Project documentation
└── LICENSE            # MIT license
```

---

## 🎯 **STEP 1: Database Setup (Supabase)**

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create account
2. Click **"New Project"**
3. Choose organization and set project details:
   - **Name**: `veilforge-db`
   - **Database Password**: `[Generate strong password]`
   - **Region**: Choose closest to your users
4. Wait for project initialization (2-3 minutes)

### 1.2 Setup Database Schema
1. Go to **SQL Editor** in Supabase dashboard
2. Copy and paste the contents of `Backend/enhanced_database_schema.sql`
3. Click **"Run"** to create all tables
4. Go to **Settings → API** and note:
   - **Project URL** (starts with `https://`)
   - **Project API Keys → anon public** key
   - **Project API Keys → service_role** key (keep secret!)

---

## 🏗️ **STEP 2: Backend Deployment (Render)**

### 2.1 Prepare Repository
1. Ensure your code is pushed to GitHub: `https://github.com/srushti2026/Crypto-Steganography`
2. Repository should be public or Render should have access

### 2.2 Deploy to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure deployment:
   - **Name**: `veilforge-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install --upgrade pip && pip install -r Backend/requirements.txt`
   - **Start Command**: `cd Backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Starter` (free tier)

### 2.3 Set Environment Variables
In Render dashboard, go to **Environment** and add:

**REQUIRED:**
```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-from-supabase
PORT=10000
ENVIRONMENT=production
RENDER=true
PYTHONPATH=/opt/render/project/src/Backend
```

**OPTIONAL (for full functionality):**
```
SUPABASE_SERVICE_KEY=your-service-key-from-supabase
EMAIL_USER=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-specific-password
HF_TOKEN=your-hugging-face-token
```

### 2.4 Deploy and Test
1. Click **"Deploy"** 
2. Wait for build completion (5-10 minutes)
3. Your backend will be available at: `https://crypto-steganography-1.onrender.com`
4. Test health endpoint: `https://crypto-steganography-1.onrender.com/health`

---

## 🌐 **STEP 3: Frontend Deployment (Vercel)**

### 3.1 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign up/login with GitHub
2. Click **"New Project"**
3. Import your repository
4. Configure deployment:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `Frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 3.2 Set Environment Variables (Optional)
In Vercel dashboard → **Settings** → **Environment Variables**:
```
VITE_API_URL=https://your-render-backend-url.onrender.com
```

### 3.3 Deploy and Test
1. Click **"Deploy"**
2. Wait for deployment (2-3 minutes)
3. Your frontend will be available at: `https://your-project.vercel.app`

---

## 🔗 **STEP 4: Connect Frontend to Backend**

### 4.1 Update API URL in Vercel
1. In Vercel dashboard → **Settings** → **Environment Variables**
2. Add or update:
   ```
   VITE_API_URL=https://veilforge-backend.onrender.com
   ```
3. Redeploy: **Deployments** → **"Redeploy"**

### 4.2 Configure CORS in Backend
The backend is already configured to accept requests from Vercel domains.

---

## ✅ **STEP 5: Verification Checklist**

### 5.1 Database Verification
- [ ] Supabase project created and accessible
- [ ] Database schema applied successfully
- [ ] API keys copied to Render environment variables

### 5.2 Backend Verification
- [ ] Render deployment successful
- [ ] Health endpoint responds: `GET /health`
- [ ] API documentation accessible: `GET /docs`
- [ ] Environment variables set correctly

### 5.3 Frontend Verification
- [ ] Vercel deployment successful
- [ ] Website loads and displays properly
- [ ] API connection works (test with image upload)
- [ ] All steganography features functional

---

## 🛠️ **Troubleshooting**

### Backend Issues
```bash
# Check Render logs for errors
# Common issues:
1. Missing environment variables → Check Render Environment tab
2. Module import errors → Verify Backend/modules/ structure
3. Database connection → Check Supabase URL and keys
4. Port binding → Ensure PORT=10000 in environment
```

### Frontend Issues
```bash
# Check Vercel deployment logs
# Common issues:
1. Build failures → Check package.json dependencies
2. API connection → Verify VITE_API_URL in Vercel environment
3. CORS errors → Check backend CORS configuration
4. Route errors → Verify vercel.json rewrites
```

### Performance Optimization
1. **Backend**: Consider upgrading Render plan for better performance
2. **Frontend**: Vercel automatically optimizes for global CDN
3. **Database**: Monitor Supabase usage and consider upgrading for high traffic

---

## 🔐 **Security Notes**

1. **Never commit** `.env` files or secrets to repository
2. **Use strong passwords** for Supabase database
3. **Keep service keys secret** - only use anon keys in frontend
4. **Enable RLS** (Row Level Security) in Supabase for production
5. **Monitor usage** to prevent abuse

---

## 📞 **Support**

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)  
- **Supabase Documentation**: [supabase.com/docs](https://supabase.com/docs)

**Deployment completed successfully!** 🎉

Your VeilForge application is now live and ready to use with all steganography modules intact!