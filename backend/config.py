# VeilForge Web Application Configuration
import os

# Server settings
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))  # Use environment PORT or default to 8000
DEBUG = os.getenv("DEBUG", "false").lower() == "true"  # Production should be false

# Directory settings
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs" 
TEMP_DIR = "temp"

# File settings
# MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB - REMOVED: No file size limit
MAX_FILE_SIZE = None  # No limit
ALLOWED_EXTENSIONS = {
    'image': ['.png', '.jpg', '.jpeg', '.bmp'],
    'audio': ['.wav', '.mp3', '.flac'],
    'video': ['.mp4', '.avi', '.mov', '.mkv'],
    'document': ['.pdf', '.docx', '.xml'],
    'text': ['.txt', '.py', '.js', '.html', '.css', '.json']
}

# Job settings
JOB_TIMEOUT = 3600  # 1 hour
CLEANUP_INTERVAL = 1800  # 30 minutes
MAX_CONCURRENT_JOBS = 5

# Security settings
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128