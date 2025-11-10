#!/bin/bash
# VeilForge Backend Deployment Helper
# This script helps with backend deployment to Render

echo "🚀 VeilForge Backend Deployment Helper"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

echo "📋 Pre-deployment checklist:"
echo "✅ Root endpoint added to app.py"
echo "✅ Requirements.txt updated with audio dependencies"
echo "✅ CORS configured for production"
echo "✅ Environment variables ready"

echo ""
echo "🔧 Deployment Configuration:"
echo "- Platform: Render.com"
echo "- Start Command: python app.py"
echo "- Environment: Python 3.11+"
echo "- Port: Auto-detected by Render"

echo ""
echo "📝 Required Environment Variables for Render:"
echo "- HUGGING_FACE_API_KEY (for text-to-image generation)"
echo "- FRONTEND_URL (will be your Vercel URL)"
echo "- Any additional email/database configs if needed"

echo ""
echo "🌐 After deployment, your API will be available at:"
echo "- Root: https://your-app.onrender.com/"
echo "- Health: https://your-app.onrender.com/health"
echo "- Docs: https://your-app.onrender.com/docs"

echo ""
echo "📡 Next Steps:"
echo "1. Commit and push your changes to GitHub"
echo "2. Trigger redeploy on Render (or it will auto-deploy)"
echo "3. Test the root endpoint once deployed"
echo "4. Deploy frontend to Vercel with VITE_API_URL set to your Render URL"

echo ""
echo "✨ Deployment ready! Push your changes to GitHub."