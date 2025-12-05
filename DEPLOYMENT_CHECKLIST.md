# 📋 VeilForge Deployment Checklist

## Pre-Deployment ✅
- [ ] All code committed and pushed to GitHub
- [ ] "Not used/" folder is gitignored 
- [ ] All steganography modules present in Backend/modules/
- [ ] Database schema files in Backend/
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Backend imports work without errors

## Database Setup (Supabase) ✅
- [ ] Supabase project created
- [ ] Database schema applied from `Backend/enhanced_database_schema.sql`
- [ ] API keys noted (URL, anon key, service key)

## Backend Deployment (Render) ✅
- [ ] Render web service created
- [ ] Repository connected
- [ ] Build command: `pip install --upgrade pip && pip install -r Backend/requirements.txt`
- [ ] Start command: `cd Backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables set:
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_ANON_KEY` 
  - [ ] `PORT=10000`
  - [ ] `ENVIRONMENT=production`
  - [ ] `RENDER=true`
  - [ ] `PYTHONPATH=/opt/render/project/src/Backend`
- [ ] Deployment successful
- [ ] Health endpoint works: `/health`

## Frontend Deployment (Vercel) ✅
- [ ] Vercel project created
- [ ] Repository imported
- [ ] Root Directory: `Frontend`
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`
- [ ] Environment variables (optional):
  - [ ] `VITE_API_URL=https://your-backend.onrender.com`
- [ ] Deployment successful
- [ ] Website loads correctly

## Final Testing ✅
- [ ] Frontend connects to backend
- [ ] Image steganography works (embed/extract)
- [ ] Video steganography works
- [ ] Audio steganography works
- [ ] Document steganography works
- [ ] User authentication works (if enabled)
- [ ] File download works
- [ ] No console errors

## Performance & Security ✅
- [ ] Backend responds within acceptable time
- [ ] Frontend loads quickly
- [ ] HTTPS enabled on both services
- [ ] Environment variables secure
- [ ] Database access properly configured

**🎉 Deployment Complete!**