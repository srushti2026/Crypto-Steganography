# VeilForge Backend

This is the backend API for the VeilForge steganography platform, built with FastAPI.

## Project Structure

```
backend/
├── app.py                          # Main FastAPI application
├── config.py                       # Configuration and environment variables
├── env_loader.py                   # Environment variable loader
├── email_config.py                 # Email configuration
├── supabase_config.py              # Supabase database configuration
├── supabase_service.py             # Database service layer
├── file_naming_utils.py            # File naming utilities
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render deployment configuration
├── .env.template                   # Environment variables template
├── modules/                        # Steganography processing modules
│   ├── video_steganography.py      # Video processing
│   ├── universal_file_steganography.py  # Image/document processing
│   ├── universal_file_audio.py     # Audio processing
│   ├── audio_capacity_manager.py   # Audio capacity management
│   └── safe_*.py                   # Safe processing variants
└── uploads/                        # File upload directory (created at runtime)
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/supported-formats` - Get supported file formats
- `POST /api/embed` - Embed data into carrier files
- `POST /api/extract` - Extract data from files
- `POST /api/forensic-embed` - Forensic embedding with metadata
- `POST /api/forensic-extract` - Forensic extraction
- `GET /api/operations/{id}/status` - Check operation status
- `GET /api/operations/{id}/download` - Download results

## Environment Variables

Required environment variables (add these in Render dashboard):

### Core Configuration
- `PORT=10000` (Render requirement)
- `DEBUG=false`

### Database (Required)
- `SUPABASE_URL=https://your-project.supabase.co`
- `SUPABASE_KEY=your_supabase_anon_key`

### CORS (Required for Production)
- `FRONTEND_URL=https://your-frontend-domain.vercel.app`

### Email (Optional)
- `SMTP_SERVER=smtp.gmail.com`
- `SMTP_PORT=587`
- `EMAIL_USER=your_email@gmail.com`
- `EMAIL_PASSWORD=your_app_password`
- `RECIPIENT_EMAIL=contact@yourdomain.com`

## Local Development

1. Copy `.env.template` to `.env` and fill in your values
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python app.py`
4. API will be available at `http://localhost:8000`
5. Documentation at `http://localhost:8000/docs`

## Render Deployment

1. Create a new Web Service on Render.com
2. Connect your GitHub repository
3. Set the following:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 10000`
4. Add environment variables in the Render dashboard
5. Deploy

## Features

- **Multi-format Steganography**: Images, videos, audio, documents
- **Forensic Mode**: Enhanced security with metadata embedding
- **Batch Processing**: Multiple files in one operation  
- **Real-time Status**: WebSocket-like status updates
- **Secure Upload**: Temporary file handling with cleanup
- **Database Integration**: Operation logging with Supabase
- **CORS Enabled**: Ready for frontend integration

## Security

- All sensitive data in environment variables
- No hardcoded credentials
- Temporary file cleanup
- Input validation and sanitization
- Rate limiting ready
- HTTPS recommended for production