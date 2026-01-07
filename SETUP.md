# 🛡️ VeilForge - Complete Setup Guide

VeilForge is an advanced steganography platform that allows you to securely hide sensitive data inside everyday digital files. This guide provides comprehensive instructions for setting up and running the application.

## 📋 Table of Contents

- [Application Overview](#-application-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Local Development Setup](#-local-development-setup)
- [Production Deployment](#-production-deployment)
- [Environment Configuration](#-environment-configuration)
- [Usage Instructions](#-usage-instructions)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Security Considerations](#-security-considerations)

## 🌟 Application Overview

VeilForge is a **state-of-the-art steganography platform** built with modern web technologies, designed for secure data concealment in digital media files. The application provides enterprise-grade capabilities through an intuitive web interface.

### What is Steganography?
Steganography is the practice of hiding information within other non-secret data or physical media. Unlike cryptography, which scrambles data, steganography conceals the very existence of the hidden information.

### Primary Use Cases
- **Cybersecurity Research**: Test detection algorithms and security measures
- **Digital Forensics**: Maintain evidence chain integrity with embedded metadata
- **Privacy Protection**: Secure communication and data storage
- **Copyright Protection**: Embed ownership information in digital content
- **Secure Data Storage**: Hide sensitive information in plain sight

## ✨ Features

### 🎯 Core Capabilities
- **Multi-Format Support**: Images (PNG, JPEG), Videos (MP4, AVI, MOV), Audio (WAV, MP3, FLAC), Documents (PDF, DOCX, TXT)
- **Advanced Encryption**: AES-256-GCM encryption with password protection
- **Batch Processing**: Process multiple files simultaneously
- **Real-Time Progress**: Live status updates and operation tracking
- **Modern UI/UX**: Responsive design with dark/light theme support

### 🕵️ Specialized Modes
1. **General Steganography**: Standard embedding and extraction operations
2. **Copyright Protection**: Embed copyright metadata with authorship information
3. **Forensic Evidence**: Advanced embedding with tamper detection and chain of custody

### 🔧 Technical Features
- **Memory Management**: Automatic cleanup and memory optimization
- **Database Integration**: Operation logging with Supabase
- **Secure File Handling**: Temporary file processing with automatic cleanup
- **Error Recovery**: Comprehensive error handling and fallback mechanisms
- **Cross-Platform**: Web-based interface accessible from any device

## 🏗 Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance API
- **Steganography Engines**: Custom implementations for each media type
- **Database**: Supabase (PostgreSQL) for operation logging
- **File Processing**: Specialized managers for different file types
- **Security**: Encrypted operations with secure temporary storage

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: Shadcn/ui components with Tailwind CSS
- **State Management**: React hooks and context
- **Routing**: React Router for navigation
- **Build Tool**: Vite for fast development and building

### Deployment
- **Backend**: Render.com (Python runtime)
- **Frontend**: Vercel (Static hosting)
- **Database**: Supabase (Managed PostgreSQL)
- **Storage**: Temporary file processing (no permanent storage)

## 📋 Prerequisites

### System Requirements
- **Node.js**: Version 18.0 or higher
- **Python**: Version 3.11 or higher
- **Package Managers**: npm/yarn (Frontend), pip (Backend)
- **Git**: For version control and deployment

### Development Tools (Optional)
- **VS Code**: Recommended IDE with extensions
- **Docker**: For containerized development
- **Postman**: For API testing

### Accounts Required
- **Supabase Account**: For database and authentication
- **Render Account**: For backend deployment
- **Vercel Account**: For frontend deployment

## 🚀 Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/srushti2026/Crypto-Steganography.git
cd Crypto-Steganography
```

### 2. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Install Python dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Using virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create environment file:
```bash
cp .env.example .env
```

Configure environment variables in `.env`:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Application Settings
FRONTEND_URL=http://localhost:5173
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your_secret_key
```

Start the backend server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
# or
yarn install
```

Create environment file:
```bash
cp .env.example .env
```

Configure environment variables in `.env`:
```env
VITE_API_URL=http://localhost:8000/api
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Start the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at: `http://localhost:5173`

### 4. Database Setup (Supabase)

1. Create a new Supabase project at https://supabase.com
2. Navigate to the SQL Editor in your Supabase dashboard
3. Create the required tables by running the SQL schema (see `Backend/database/schema.sql`)
4. Configure Row Level Security (RLS) policies as needed
5. Copy your project URL and anon key to the environment files

## 🌐 Production Deployment

### Backend Deployment (Render)

1. **Create Render Account**: Sign up at https://render.com
2. **Connect Repository**: Link your GitHub repository
3. **Configure Service**:
   - Service Type: Web Service
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Python Version: 3.11

4. **Set Environment Variables**:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_JWT_SECRET=your_jwt_secret
   FRONTEND_URL=https://your-frontend-domain.vercel.app
   ```

5. **Deploy**: Render will automatically build and deploy your backend

### Frontend Deployment (Vercel)

1. **Create Vercel Account**: Sign up at https://vercel.com
2. **Import Project**: Connect your GitHub repository
3. **Configure Build Settings**:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

4. **Set Environment Variables**:
   ```env
   VITE_API_URL=https://your-backend-domain.render.com/api
   VITE_SUPABASE_URL=your_supabase_url
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
   ```

5. **Deploy**: Vercel will automatically build and deploy your frontend

## ⚙️ Environment Configuration

### Backend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_KEY` | Supabase anon key | Yes | - |
| `SUPABASE_JWT_SECRET` | JWT secret for authentication | Yes | - |
| `FRONTEND_URL` | Frontend domain for CORS | Yes | - |
| `PORT` | Server port | No | 8000 |
| `DEBUG` | Enable debug mode | No | False |
| `SECRET_KEY` | Application secret key | Yes | - |

### Frontend Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | Yes | - |
| `VITE_SUPABASE_URL` | Supabase project URL | Yes | - |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key | Yes | - |

## 🎯 Usage Instructions

### 1. General Steganography

#### Embedding Data
1. Navigate to the **General** page
2. Select **Embed** tab
3. Upload a carrier file (image, video, audio, or document)
4. Upload or type the content to hide
5. Enter a secure password
6. Click **Embed Data**
7. Download the steganographic file

#### Extracting Data
1. Navigate to the **General** page
2. Select **Extract** tab
3. Upload the steganographic file
4. Enter the password used for embedding
5. Click **Extract Data**
6. View or download the extracted content

### 2. Copyright Protection

#### Embedding Copyright Information
1. Navigate to the **Copyright Protection** page
2. Select **Embed** tab
3. Upload a carrier file
4. Fill in copyright details:
   - Author Name
   - Copyright Alias
   - Additional Copyright Info
5. Enter a secure password
6. Click **Embed Copyright**
7. Download the protected file

#### Extracting Copyright Information
1. Navigate to the **Copyright Protection** page
2. Select **Extract** tab
3. Upload the copyrighted file
4. Enter the password
5. Click **Extract Copyright**
6. View the copyright metadata

### 3. Forensic Evidence

#### Embedding Forensic Evidence
1. Navigate to the **Forensic Evidence** page
2. Select **Embed** tab
3. Upload a carrier file
4. Upload the evidence file or enter evidence text
5. Fill in forensic metadata:
   - Case ID
   - Evidence Description
   - Investigator Information
   - Chain of Custody details
6. Enter a secure password
7. Click **Embed Evidence**
8. Download the forensic container

#### Extracting Forensic Evidence
1. Navigate to the **Forensic Evidence** page
2. Select **Extract** tab
3. Upload the forensic container
4. Enter the password
5. Click **Extract Evidence**
6. View the extracted evidence and metadata

### 4. Batch Operations

1. Navigate to any page and select the **Batch** tab
2. Upload multiple carrier files
3. Upload corresponding content files or enter text
4. Configure batch settings
5. Enter a password for all operations
6. Click **Process Batch**
7. Monitor progress and download results

## 📚 API Documentation

### Core Endpoints

#### Embedding Endpoints
- `POST /api/embed` - General data embedding
- `POST /api/embed-batch` - Batch embedding operations
- `POST /api/forensic-embed` - Forensic evidence embedding

#### Extraction Endpoints
- `POST /api/extract` - General data extraction
- `POST /api/forensic-extract` - Forensic evidence extraction

#### Status and Management
- `GET /api/operations/{operation_id}/status` - Check operation status
- `GET /api/operations/{operation_id}/download` - Download results
- `POST /api/analyze` - Analyze files for hidden data

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `POST /api/auth/refresh` - Token refresh

### Request/Response Examples

#### Embed Data Request
```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: multipart/form-data" \
  -F "carrier_file=@image.png" \
  -F "content_file=@secret.txt" \
  -F "password=secure_password"
```

#### Extract Data Request
```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "stego_file=@stego_image.png" \
  -F "password=secure_password"
```

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues

**Issue**: `ModuleNotFoundError` for Python packages
**Solution**: 
```bash
pip install -r requirements.txt
# or reinstall specific package
pip install package_name
```

**Issue**: Port already in use
**Solution**:
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
# or use different port
uvicorn app:app --port 8001
```

**Issue**: Database connection errors
**Solution**:
- Verify Supabase credentials in `.env`
- Check network connectivity
- Ensure database tables exist

#### Frontend Issues

**Issue**: `Cannot resolve module` errors
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Environment variables not loading
**Solution**:
- Ensure `.env` file exists in frontend directory
- Restart development server
- Check variable names start with `VITE_`

**Issue**: API connection errors
**Solution**:
- Verify backend is running
- Check API URL in environment variables
- Verify CORS configuration

#### Deployment Issues

**Issue**: Build failures on Render/Vercel
**Solution**:
- Check build logs for specific errors
- Verify all dependencies in requirements.txt/package.json
- Ensure environment variables are set

**Issue**: Memory limit exceeded (Render)
**Solution**:
- The application includes automatic memory management
- Monitor memory usage in Render dashboard
- Consider upgrading to paid tier for more memory

### Performance Optimization

#### File Size Limits
- **Images**: Recommended max 50MB
- **Videos**: Recommended max 100MB
- **Audio**: Recommended max 50MB
- **Documents**: Recommended max 25MB

#### Best Practices
1. Use appropriate file formats for your use case
2. Compress large files before embedding
3. Use strong but reasonable passwords (12-20 characters)
4. Monitor operation status for long-running processes
5. Clean up temporary files regularly

## 🔒 Security Considerations

### Password Security
- Use strong, unique passwords for each operation
- Store passwords securely (use password managers)
- Never share passwords through insecure channels

### File Handling
- All uploaded files are processed temporarily and deleted
- No files are permanently stored on servers
- Use HTTPS for all communications

### Data Privacy
- The application doesn't log sensitive data
- User authentication is optional but recommended
- All operations are logged with minimal metadata

### Operational Security
- Regularly update dependencies
- Monitor for security advisories
- Use environment variables for sensitive configuration
- Enable proper logging and monitoring in production

## 📞 Support and Contributing

### Getting Help
- **Issues**: Report bugs on the GitHub repository
- **Documentation**: Check the README and API docs
- **Community**: Join discussions in GitHub Issues

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow existing code style
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**🛡️ VeilForge** - *Hide your secrets in plain sight*

For the latest updates and documentation, visit: https://github.com/srushti2026/Crypto-Steganography