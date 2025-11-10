# VeilForge Deployment Guide

## Project Structure
The project is now ready for deployment with all necessary files migrated to the main directories:

- `backend/` - FastAPI application ready for Render deployment
- `frontend/` - React/Vite application ready for Vercel deployment

## Backend Deployment (Render)

### Prerequisites
1. Push your code to GitHub
2. Sign up for a Render account
3. Have the following environment variables ready:
   - `HF_TOKEN` - Hugging Face API token for text-to-image generation
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_ANON_KEY` - Your Supabase anonymous key
   - `EMAIL_USER` - SMTP email for contact form
   - `EMAIL_PASSWORD` - SMTP password
   - `FRONTEND_URL` - Your frontend URL (for CORS)

### Deployment Steps
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - **Name**: `veilforge-backend` (or your preferred name)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Starter` (free tier available)

5. Add environment variables in the "Environment" section
6. Deploy!

### Health Check
The backend includes a `/health` endpoint for monitoring.

## Frontend Deployment (Vercel)

### Prerequisites
1. Sign up for a Vercel account
2. Have your backend URL ready from Render deployment

### Deployment Steps
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

5. Add environment variables:
   - `VITE_API_URL`: Your Render backend URL (e.g., `https://veilforge-backend.onrender.com`)
   - `VITE_SUPABASE_URL`: Your Supabase URL
   - `VITE_SUPABASE_ANON_KEY`: Your Supabase anonymous key

6. Deploy!

## Environment Variables Summary

### Backend (Render)
```
HF_TOKEN=your_hugging_face_token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
FRONTEND_URL=https://your-app.vercel.app
```

### Frontend (Vercel)
```
VITE_API_URL=https://veilforge-backend.onrender.com
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

## Features Included

✅ **Steganography Operations**
- Image, Video, Audio steganography
- Multi-layer file embedding
- Encryption and password protection
- Batch processing

✅ **Text-to-Image Generation**
- FLUX.1-schnell model integration
- Batch image generation
- Project management

✅ **Security Features**
- Password generation
- Encryption options
- Forensic evidence protection

✅ **User Management**
- Supabase authentication
- Operation tracking
- Project organization

✅ **Contact System**
- Email integration
- Form validation

## Troubleshooting

### Backend Issues
- Check Render logs for errors
- Verify environment variables are set
- Test `/health` endpoint

### Frontend Issues
- Check Vercel deployment logs
- Verify API URL environment variable
- Test in browser developer tools

### CORS Issues
- Ensure `FRONTEND_URL` is set in backend
- Check allowed origins in `app.py`

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## File Structure Cleanup

The `text_to_image/` directory can now be safely deleted as all functionality has been integrated into the main application.