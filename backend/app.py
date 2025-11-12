"""
Enhanced FastAPI Web Application for React Frontend Integration
Provides comprehensive API endpoints for the React steganography application
with Supabase integration - SECURED WITH ENVIRONMENT VARIABLES
"""

# Load environment variables for local development
try:
    from .env_loader import load_env_file
    load_env_file()
except (ImportError, ValueError):
    # Try relative import first, then absolute
    try:
        from env_loader import load_env_file
        load_env_file()
    except ImportError:
        pass  # In production, environment variables are provided by the platform

import os
import tempfile
import uuid
import time
import secrets
import string
import hashlib
import zipfile
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import json
import shutil
from datetime import datetime
import asyncio
import concurrent.futures
import signal

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks, Depends
# from fastapi.staticfiles import StaticFiles  # Not needed in Vercel deployment
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn  # Used for local development server
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Try to import email config, fallback to default if not available
try:
    from .email_config import EMAIL_CONFIG
except ImportError:
    try:
        from email_config import EMAIL_CONFIG
    except ImportError:
        EMAIL_CONFIG = {
            'SMTP_SERVER': 'smtp.gmail.com',
            'SMTP_PORT': 587,
            'EMAIL_USER': '',
            'EMAIL_PASSWORD': '',
            'RECIPIENT_EMAIL': 'srushti_csd@ksit.edu.in',
            'SENDER_NAME': 'VeilForge Contact System',
        'SUBJECT_TEMPLATE': 'VeilForge Contact: {subject}',
        'ENABLE_EMAIL': False
    }

# Production optimization settings
IS_PRODUCTION = os.getenv('RENDER') is not None or os.getenv('RAILWAY') is not None
if IS_PRODUCTION:
    print("[INFO] Production environment detected - enabling optimizations")
    # Reduce memory usage in production
    import gc
    gc.set_threshold(100, 10, 10)  # More aggressive garbage collection
    
    # Set stricter limits for file processing
    MAX_FILE_SIZE_MB = 50  # Reduced from default for memory constraints
    MAX_OPERATION_TIMEOUT = 300  # 5 minutes max per operation
else:
    MAX_FILE_SIZE_MB = 100
    MAX_OPERATION_TIMEOUT = 600  # 10 minutes for local development

print(f"[CONFIG] Max file size: {MAX_FILE_SIZE_MB}MB, Max operation timeout: {MAX_OPERATION_TIMEOUT}s")

# Import steganography modules with fallbacks
steganography_managers = {}

# Video Steganography - Try existing modules
try:
    from final_video_steganography import FinalVideoSteganographyManager
    steganography_managers['video'] = FinalVideoSteganographyManager
    print("[OK] Final Video steganography module loaded")
except ImportError:
    try:
        try:
            from .modules.video_steganography import VideoSteganographyManager
        except ImportError:
            from modules.video_steganography import VideoSteganographyManager
        steganography_managers['video'] = VideoSteganographyManager
        print("[OK] Video steganography module loaded")
    except ImportError as e:
        print(f"[ERROR] Video steganography module not available: {e}")
        steganography_managers['video'] = None

# Image Steganography - Use multi-layer steganography with backward compatibility
try:
    try:
        from .modules.multi_layer_steganography import UniversalFileSteganography
    except ImportError:
        from modules.multi_layer_steganography import UniversalFileSteganography
    steganography_managers['image'] = UniversalFileSteganography
    print("[OK] Multi-layer steganography module loaded for images")
except ImportError as e:
    print(f"[ERROR] Image steganography module not available: {e}")
    steganography_managers['image'] = None

# Document Steganography - Use multi-layer steganography with backward compatibility  
try:
    try:
        from .modules.multi_layer_steganography import UniversalFileSteganography
    except ImportError:
        from modules.multi_layer_steganography import UniversalFileSteganography
    steganography_managers['document'] = UniversalFileSteganography
    print("[OK] Multi-layer steganography module loaded for documents")
except ImportError as e:
    print(f"[ERROR] Document steganography module not available: {e}")
    steganography_managers['document'] = None

# Audio Steganography - Use working module
try:
    try:
        from .modules.universal_file_audio import UniversalFileAudio
    except ImportError:
        from modules.universal_file_audio import UniversalFileAudio
    steganography_managers['audio'] = UniversalFileAudio
    print("[OK] Universal file audio steganography module loaded")
except ImportError as e:
    print(f"[ERROR] Audio steganography module not available: {e}")
    steganography_managers['audio'] = None

# Import Supabase service with fallback
database_available = False
try:
    try:
        from .supabase_service import get_database, SteganographyDatabase
    except ImportError:
        from supabase_service import get_database, SteganographyDatabase
    database_available = True
    print("[OK] Supabase database service loaded")
except ImportError as e:
    print(f"❌ Supabase database service not available: {e}")
    get_database = None
    SteganographyDatabase = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

# Text-to-Image Generation imports
try:
    from dotenv import load_dotenv
    from huggingface_hub import InferenceClient
    
    # Load environment variables for text-to-image
    load_dotenv()
    HF_TOKEN = os.getenv("HF_TOKEN")
    
    # Initialize Hugging Face Inference Client for text-to-image
    text_to_image_client = InferenceClient(
        model="black-forest-labs/FLUX.1-schnell",
        api_key=HF_TOKEN,
        provider="nebius"
    ) if HF_TOKEN else None
    
    print("[OK] Text-to-image functionality loaded")
except ImportError as e:
    print(f"[WARNING] Text-to-image functionality not available: {e}")
    text_to_image_client = None

class TextToImageRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    project_name: Optional[str] = Field(None, description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")

class UserModel(BaseModel):
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")

class EmbedRequest(BaseModel):
    carrier_type: str = Field(..., description="Type of carrier file: image, video, audio, document")
    content_type: str = Field(..., description="Type of content to hide: text, file")
    text_content: Optional[str] = Field(None, description="Text content to hide")
    password: str = Field(..., description="Password for encryption")
    encryption_type: str = Field(default="aes-256-gcm", description="Encryption algorithm")
    project_name: Optional[str] = Field(None, description="Project name")
    project_description: Optional[str] = Field(None, description="Project description")

class ExtractRequest(BaseModel):
    password: str = Field(..., description="Password for decryption")
    output_format: str = Field(default="auto", description="Output format preference")

class ProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    project_type: str = Field(default="general", description="Project type")

class ContactRequest(BaseModel):
    name: str = Field(..., description="Sender's name")
    email: str = Field(..., description="Sender's email")
    phone: Optional[str] = Field(None, description="Sender's phone")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., description="Message content")

class OperationResponse(BaseModel):
    success: bool
    operation_id: str
    message: str
    output_filename: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Steganography API",
    description="Advanced steganography API with React frontend integration",
    version="2.0.0"
)

# Enable CORS for React frontend - supports both development and production
allowed_origins = [
    "http://localhost:5173", 
    "http://localhost:3000", 
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "https://veilforge.vercel.app",  # Your production Vercel URL
    "https://veilforge-rctejq0kc-srushti-csd-3993s-projects.vercel.app",  # Your deployment URL
]

# Add production frontend URL from environment variable
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production compatibility
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
TEMP_DIR = Path("temp")

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Global variables for job tracking
active_jobs: Dict[str, Dict[str, Any]] = {}

# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Optional[SteganographyDatabase]:
    """Get database instance if available"""
    if get_database and callable(get_database):
        try:
            return get_database()
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    return None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """Generate unique filename with timestamp and UUID"""
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(original_filename)
    return f"{prefix}{name}_{timestamp}_{unique_id}{ext}"

def generate_clean_output_filename(original_filename: str, prefix: str = "stego_") -> str:
    """Generate clean, user-friendly output filename"""
    name, ext = os.path.splitext(original_filename)
    
    # Clean the name - remove any existing prefixes and timestamps
    clean_name = name
    
    # Remove common prefixes
    for old_prefix in ['stego_', 'carrier_', 'content_']:
        clean_name = clean_name.replace(old_prefix, '')
    
    # Remove timestamp_uuid patterns
    import re
    clean_name = re.sub(r'_\d{10}_[a-f0-9]{8}', '', clean_name)
    
    # Remove any leading/trailing underscores
    clean_name = clean_name.strip('_')
    
    # Ensure we have a name
    if not clean_name:
        clean_name = 'image'
    
    # If no extension, default to .png for images
    if not ext:
        ext = '.png'
    
    # Generate a simple unique suffix
    unique_suffix = str(uuid.uuid4())[:6]
    
    return f"{prefix}{clean_name}_{unique_suffix}{ext}"

def get_file_hash(file_path: str) -> str:
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """Clean up old files from directory"""
    try:
        current_time = time.time()
        for file_path in directory.glob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    file_path.unlink()
    except Exception as e:
        print(f"Cleanup error: {e}")

def update_job_status(job_id: str, status: str, progress: int = None, 
                     message: str = None, error: str = None, result: Dict = None,
                     output_files: List[str] = None, extracted_data: str = None,
                     original_filename: str = None, is_multi_layer: bool = False,
                     layer_details: List[Dict] = None):
    """Update job status in memory with multi-layer support"""
    if job_id in active_jobs:
        update_data = {
            "status": status,
            "progress": progress,
            "message": message,
            "error": error,
            "result": result,
            "updated_at": datetime.now().isoformat()
        }
        
        # Add multi-layer specific data if provided
        if output_files is not None:
            update_data["output_files"] = output_files
        if extracted_data is not None:
            update_data["extracted_data"] = extracted_data
        if original_filename is not None:
            update_data["original_filename"] = original_filename
        if is_multi_layer:
            update_data["is_multi_layer"] = is_multi_layer
        if layer_details is not None:
            update_data["layer_details"] = layer_details
            
        active_jobs[job_id].update(update_data)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to be safe for filesystem operations"""
    if not filename:
        return "unnamed_file"
    
    # Remove or replace unsafe characters
    import re
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    
    # Handle reserved names on Windows
    reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
    if safe_name.upper() in reserved_names:
        safe_name = f"_{safe_name}"
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    # Limit length
    if len(safe_name) > 250:
        safe_name = safe_name[:250]
    
    return safe_name

def _is_likely_text_content(data):
    """Check if bytes data is likely UTF-8 text content"""
    if not isinstance(data, bytes) or len(data) == 0:
        return False
    
    try:
        # Try to decode as UTF-8
        decoded = data.decode('utf-8')
        
        # Check if it contains mostly printable characters
        printable_ratio = sum(1 for c in decoded if c.isprintable() or c.isspace()) / len(decoded)
        
        # If >80% printable characters and no null bytes, likely text
        return printable_ratio > 0.8 and b'\x00' not in data[:min(100, len(data))]
        
    except UnicodeDecodeError:
        return False

def detect_file_format_from_binary(binary_content):
    """Detect file format from binary content and return appropriate extension"""
    if not binary_content or not isinstance(binary_content, bytes):
        return None
    
    # Check various file signatures
    if binary_content.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif binary_content.startswith(b'\xff\xd8\xff'):
        return '.jpg'
    elif binary_content.startswith(b'GIF87a') or binary_content.startswith(b'GIF89a'):
        return '.gif'
    elif binary_content.startswith(b'BM'):
        return '.bmp'
    elif binary_content.startswith(b'RIFF') and len(binary_content) > 12 and b'WEBP' in binary_content[8:12]:
        return '.webp'
    elif binary_content.startswith(b'RIFF') and len(binary_content) > 12 and b'WAVE' in binary_content[8:12]:
        return '.wav'
    elif binary_content.startswith(b'ID3') or binary_content[0:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
        return '.mp3'
    elif binary_content.startswith(b'%PDF'):
        return '.pdf'
    elif binary_content.startswith(b'PK\x03\x04'):
        # ZIP-based formats
        if b'word/' in binary_content[:1000]:
            return '.docx'
        elif b'xl/' in binary_content[:1000]:
            return '.xlsx'
        else:
            return '.zip'
    
    # If no format detected, return None to keep original filename
    return None

def create_layered_data_container(layers_info):
    """Create a container that holds multiple data layers with proper format preservation
    
    Args:
        layers_info: List of tuples (data, filename, is_binary) or just data items
    
    Returns:
        JSON string containing the layered container
    """
    import json
    import base64
    import mimetypes
    
    container = {
        "version": "1.0",
        "type": "layered_container", 
        "created_at": datetime.now().isoformat(),
        "layers": []
    }
    
    for i, layer_item in enumerate(layers_info):
        # Defensive check for None or invalid layer items
        if layer_item is None:
            print(f"Warning: None layer item at index {i}, skipping")
            continue
            
        # Handle different input formats
        if isinstance(layer_item, tuple) and len(layer_item) >= 2:
            # Format: (data, filename) or (data, filename, is_binary)
            layer_content = layer_item[0]
            original_filename = layer_item[1]
            is_binary = layer_item[2] if len(layer_item) > 2 else isinstance(layer_content, bytes)
            
            # Check for None content in tuple
            if layer_content is None:
                print(f"Warning: None content in layer tuple at index {i}, skipping")
                continue
        else:
            # Just data, infer format
            layer_content = layer_item
            original_filename = None
            is_binary = isinstance(layer_content, bytes)
            
            # Check for None content
            if layer_content is None:
                print(f"Warning: None content at index {i}, skipping")
                continue
        
        # Determine data type and filename
        if isinstance(layer_content, str):
            encoded_content = base64.b64encode(layer_content.encode('utf-8')).decode('ascii')
            data_type = "text"
            if not original_filename:
                original_filename = f"layer_{i+1}.txt"
        elif isinstance(layer_content, bytes):
            encoded_content = base64.b64encode(layer_content).decode('ascii')
            data_type = "binary"
            
            # Enhanced filename detection for binary data
            if not original_filename or original_filename in ["existing_data", "extracted_data.bin", "layer_data"]:
                # Check for common binary file signatures to determine proper extension
                if layer_content.startswith(b'\x89PNG\r\n\x1a\n'):
                    original_filename = f"layer_{i+1}.png"
                elif layer_content.startswith(b'\xff\xd8\xff'):
                    original_filename = f"layer_{i+1}.jpg"
                elif layer_content.startswith(b'GIF87a') or layer_content.startswith(b'GIF89a'):
                    original_filename = f"layer_{i+1}.gif"
                elif layer_content.startswith(b'BM'):
                    original_filename = f"layer_{i+1}.bmp"
                elif layer_content.startswith(b'RIFF') and b'WEBP' in layer_content[:12]:
                    original_filename = f"layer_{i+1}.webp"
                elif layer_content.startswith(b'RIFF') and b'WAVE' in layer_content[:12]:
                    original_filename = f"layer_{i+1}.wav"
                elif layer_content.startswith(b'ID3') or layer_content[0:2] == b'\xff\xfb' or layer_content[0:2] == b'\xff\xf3':
                    original_filename = f"layer_{i+1}.mp3"
                elif layer_content.startswith(b'%PDF'):
                    original_filename = f"layer_{i+1}.pdf"
                elif layer_content.startswith(b'PK\x03\x04'):  # ZIP file
                    # Could be DOCX, XLSX, etc.
                    if b'word/' in layer_content[:1000]:
                        original_filename = f"layer_{i+1}.docx"
                    elif b'xl/' in layer_content[:1000]:
                        original_filename = f"layer_{i+1}.xlsx"
                    else:
                        original_filename = f"layer_{i+1}.zip"
                else:
                    original_filename = f"layer_{i+1}.bin"
            
            # If we have a filename but it doesn't have proper extension, try to fix it
            elif original_filename and not any(original_filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.wav', '.mp3', '.pdf', '.docx', '.xlsx', '.zip', '.bin']):
                # Add proper extension based on content
                if layer_content.startswith(b'\x89PNG\r\n\x1a\n'):
                    original_filename += ".png"
                elif layer_content.startswith(b'\xff\xd8\xff'):
                    original_filename += ".jpg"
                elif layer_content.startswith(b'GIF87a') or layer_content.startswith(b'GIF89a'):
                    original_filename += ".gif"
                elif layer_content.startswith(b'BM'):
                    original_filename += ".bmp"
                elif layer_content.startswith(b'RIFF') and b'WAVE' in layer_content[:12]:
                    original_filename += ".wav"
                elif layer_content.startswith(b'ID3') or layer_content[0:2] in [b'\xff\xfb', b'\xff\xf3']:
                    original_filename += ".mp3"
                elif layer_content.startswith(b'%PDF'):
                    original_filename += ".pdf"
                else:
                    original_filename += ".bin"
        else:
            # Convert other types to string
            encoded_content = base64.b64encode(str(layer_content).encode('utf-8')).decode('ascii')
            data_type = "text"
            if not original_filename:
                original_filename = f"layer_{i+1}.txt"
        
        container["layers"].append({
            "index": i,
            "filename": original_filename,
            "type": data_type,
            "content": encoded_content,
            "size": len(layer_content) if isinstance(layer_content, (str, bytes)) else len(str(layer_content))
        })
    
    return json.dumps(container)

def extract_layered_data_container(container_data):
    """Extract all layers from a layered data container"""
    import json
    import base64
    
    try:
        if isinstance(container_data, bytes):
            container_json = container_data.decode('utf-8')
        else:
            container_json = container_data
        
        container = json.loads(container_json)
        
        if container.get("type") != "layered_container":
            # Not a layered container, return as-is
            return [(container_data, "extracted_data.bin")]
        
        extracted_layers = []
        for layer in container.get("layers", []):
            # Add defensive check for None layer
            if layer is None:
                print(f"Warning: None layer found in container, skipping")
                continue
            
            # Ensure layer is a dictionary
            if not isinstance(layer, dict):
                print(f"Warning: Invalid layer type {type(layer)}, skipping")
                continue
                
            filename = layer.get("filename", f"layer_{layer.get('index', 0)}.bin")
            content_b64 = layer.get("content", "")
            content_type = layer.get("type", "binary")
            
            # Defensive check for None or empty content
            if not content_b64:
                print(f"Warning: Empty content in layer {layer.get('index', 0)}, skipping")
                continue
            
            try:
                decoded_content = base64.b64decode(content_b64)
                if content_type == "text":
                    # Convert back to string for text content
                    decoded_content = decoded_content.decode('utf-8')
                else:
                    # For binary content, detect file format and fix filename
                    if isinstance(decoded_content, bytes) and decoded_content:
                        detected_extension = detect_file_format_from_binary(decoded_content)
                        if detected_extension and (filename.endswith('.bin') or 'layer_' in filename):
                            # Replace generic filename with detected format
                            layer_num = layer.get('index', len(extracted_layers) + 1)
                            filename = f"layer_{layer_num}{detected_extension}"
                            print(f"[EXTRACT] Detected format for layer {layer_num}: {detected_extension}")
                
                extracted_layers.append((decoded_content, filename))
            except Exception as decode_error:
                print(f"Error decoding layer {layer.get('index', 0)}: {decode_error}")
                continue
        
        return extracted_layers
        
    except Exception as e:
        print(f"Error extracting layered container: {e}")
        # Return original data if parsing fails
        return [(container_data, "extracted_data.bin")]

def is_layered_container(data):
    """Check if the data is a layered container"""
    try:
        if isinstance(data, bytes):
            data_str = data.decode('utf-8')
        else:
            data_str = str(data)
        
        parsed = json.loads(data_str)
        return parsed.get("type") == "layered_container"
    except:
        return False

def translate_error_message(error_msg: str, carrier_type: str) -> str:
    """Translate technical error messages to user-friendly ones"""
    
    error_lower = error_msg.lower()
    
    # Capacity issues
    if "data too large" in error_lower or "need" in error_lower and "bytes" in error_lower:
        if carrier_type == "audio":
            return "The audio file is too small to hide this much data. Please use a larger audio file or reduce the file size you're trying to hide."
        elif carrier_type == "video":
            return "The video file is too small to hide this much data. Please use a longer video file or reduce the file size you're trying to hide."
        elif carrier_type == "image":
            return "The image file is too small to hide this much data. Please use a larger image or reduce the file size you're trying to hide."
        else:
            return "The carrier file is too small to hide this much data. Please use a larger file or reduce the content size."
    
    # File type issues
    if "not supported" in error_lower or "unsupported" in error_lower:
        return f"File type not supported for {carrier_type} steganography. Please try with a different file format."
    
    # Decryption issues
    if "decryption" in error_lower or "wrong password" in error_lower:
        return "Failed to extract data. Please check your password or ensure the file contains hidden data."
    
    # Bool encoding (shouldn't happen now but just in case)
    if "bool" in error_lower and "encode" in error_lower:
        return f"File type not supported for {carrier_type} steganography. Please try with a different file format."
        
    # File format issues
    if "format" in error_lower and ("corrupt" in error_lower or "invalid" in error_lower):
        return f"The {carrier_type} file appears to be corrupted or in an unsupported format. Please try with a different file."
    
    # Generic fallback for other technical errors
    if len(error_msg) > 100 or any(word in error_lower for word in ['exception', 'traceback', 'error:', 'failed:']):
        return f"Unable to process the {carrier_type} file. Please ensure the file is valid and try again."
    
    # If it's already user-friendly, return as-is
    return error_msg

def get_steganography_manager(carrier_type: str, password: str = ""):
    """Get the appropriate steganography manager for the carrier type"""
    if carrier_type not in steganography_managers or steganography_managers[carrier_type] is None:
        return None
    
    try:
        manager_class = steganography_managers[carrier_type]
        
        # Handle different initialization patterns for different managers
        if carrier_type == "audio":
            # UniversalFileAudio now takes password in __init__
            return manager_class(password=password)
        else:
            # Other managers take password in __init__
            return manager_class(password=password)
            
    except Exception as e:
        print(f"Error creating {carrier_type} manager: {e}")
        return None

# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/users/register", response_model=Dict[str, Any])
async def register_user(user: UserModel, db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Register a new user"""
    try:
        if db:
            # Check if user already exists
            existing_user = db.get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            user_id = db.create_user(user.email, user.username)
            if user_id:
                return {
                    "success": True,
                    "user_id": user_id,
                    "message": "User registered successfully"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to create user")
        else:
            return {
                "success": True,
                "user_id": str(uuid.uuid4()),
                "message": "User registered (no database)"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint providing API information and status"""
    return {
        "message": "Welcome to VeilForge API",
        "description": "Comprehensive steganography and security services",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Image Steganography",
            "Text Steganography", 
            "Audio Steganography",
            "Video Steganography",
            "Document Steganography",
            "Text-to-Image Generation",
            "Batch Processing",
            "Password Generation",
            "File Format Support"
        ],
        "endpoints": {
            "health": "/health",
            "documentation": "/docs",
            "test": "/api/test",
            "image": "/api/embed-image, /api/extract-image",
            "text": "/api/embed-text, /api/extract-text",
            "audio": "/api/embed-audio, /api/extract-audio",
            "video": "/api/embed-video, /api/extract-video",
            "document": "/api/embed-document, /api/extract-document",
            "text_to_image": "/api/generate-image",
            "batch": "/api/batch-embed, /api/batch-extract",
            "utilities": "/api/supported-formats, /api/generate-password"
        },
        "support": {
            "frontend": "React TypeScript with Vite",
            "cors": "Configured for production deployment",
            "formats": "Images, Audio, Video, Documents, Text"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Add aliases for frontend compatibility (without /api prefix)
@app.get("/supported-formats")
async def supported_formats_alias():
    """Alias for /api/supported-formats - Frontend compatibility"""
    return {
        "image": {
            "carrier_formats": ["png", "jpg", "jpeg", "bmp", "tiff", "gif"],
            "content_formats": ["txt", "png", "jpg", "pdf", "docx"],
            "max_size_mb": 50
        },
        "audio": {
            "carrier_formats": ["wav", "mp3", "flac"],
            "content_formats": ["txt", "png", "jpg", "pdf", "docx"],
            "max_size_mb": 100
        },
        "video": {
            "carrier_formats": ["mp4", "avi", "mov"],
            "content_formats": ["txt", "png", "jpg", "pdf", "docx"],
            "max_size_mb": 500
        },
        "document": {
            "carrier_formats": ["pdf", "docx", "txt"],
            "content_formats": ["txt", "png", "jpg", "pdf"],
            "max_size_mb": 25
        }
    }

@app.get("/generate-password")
async def generate_password_alias(length: int = 16, include_symbols: bool = True):
    """Alias for /api/generate-password - Frontend compatibility"""
    import secrets
    import string
    
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return {"password": password, "length": length, "strength": "strong"}

@app.post("/embed")
async def embed_alias():
    """Alias for embed operations - Frontend compatibility"""
    return {
        "success": False,
        "error": "Invalid embed endpoint",
        "message": "Please use specific embed endpoints",
        "available_endpoints": [
            "/api/embed-image",
            "/api/embed-audio", 
            "/api/embed-video",
            "/api/embed-document"
        ]
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify backend is working"""
    return {"status": "Backend is working!", "timestamp": datetime.now().isoformat()}

@app.post("/api/contact")
async def send_contact_message(contact: ContactRequest):
    """
    Send contact form message via email
    """
    print("=" * 50)
    print("🚀 BACKEND: Contact API endpoint hit!")
    print("=" * 50)
    
    try:
        # Log the message
        print(f"📧 Contact message received:")
        print(f"Name: {contact.name}")
        print(f"Email: {contact.email}")
        print(f"Phone: {contact.phone}")
        print(f"Subject: {contact.subject}")
        print(f"Message: {contact.message}")
        print("-" * 30)
        
        # Try to send actual email using SMTP
        email_sent = False
        
        # Try simple direct email sending
        try:
            print("🚀 Attempting direct email sending...")
            
            # Simple email setup - REPLACE THESE WITH REAL CREDENTIALS
            gmail_user = "your_actual_gmail@gmail.com"  # CHANGE THIS
            gmail_app_password = "your_16_char_app_password"  # CHANGE THIS
            
            if gmail_user != "your_actual_gmail@gmail.com" and gmail_app_password != "your_16_char_app_password":
                print("📧 Trying to send email with configured credentials...")
                
                # Create the email
                msg = MIMEMultipart()
                msg['From'] = f"VeilForge Contact <{gmail_user}>"
                msg['To'] = "srushti_csd@ksit.edu.in"
                msg['Subject'] = f"VeilForge Contact: {contact.subject}"
                msg['Reply-To'] = contact.email
                
                email_body = f"""
NEW CONTACT FORM MESSAGE:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Subject: {contact.subject}

Message:
{contact.message}

---
Sent from VeilForge Contact Form
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reply directly to: {contact.email}
"""
                
                msg.attach(MIMEText(email_body, 'plain'))
                
                # Send via Gmail SMTP
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(gmail_user, gmail_app_password)
                
                text = msg.as_string()
                server.sendmail(gmail_user, "srushti_csd@ksit.edu.in", text)
                server.quit()
                
                email_sent = True
                print("✅ EMAIL SENT SUCCESSFULLY!")
                print(f"   From: {gmail_user}")
                print(f"   To: srushti_csd@ksit.edu.in")
                print(f"   Subject: VeilForge Contact: {contact.subject}")
                
            else:
                print("⚠️ Email credentials not configured")
                print("📧 To enable email sending:")
                print("   1. Edit enhanced_app.py")
                print("   2. Replace gmail_user with your Gmail address")
                print("   3. Replace gmail_app_password with your Gmail App Password")
                print("   4. Restart the server")
                
        except Exception as email_error:
            print(f"❌ Email sending failed: {email_error}")
            print(f"   Error type: {type(email_error).__name__}")
            email_sent = False
        
        # Try SMTP if configured and Formspree didn't work
        if not email_sent and EMAIL_CONFIG['ENABLE_EMAIL'] and EMAIL_CONFIG['EMAIL_USER'] != 'your_actual_email@gmail.com':
            try:
                print("🚀 Attempting SMTP email sending...")
                
                # Create email content
                subject = EMAIL_CONFIG['SUBJECT_TEMPLATE'].format(subject=contact.subject)
                
                # Create message
                msg = MIMEMultipart()
                msg['From'] = f"{EMAIL_CONFIG['SENDER_NAME']} <{EMAIL_CONFIG['EMAIL_USER']}>"
                msg['To'] = EMAIL_CONFIG['RECIPIENT_EMAIL']
                msg['Subject'] = subject
                msg['Reply-To'] = contact.email
                
                # Email body
                email_body = f"""
New Contact Form Submission from VeilForge:

Name: {contact.name}
Email: {contact.email}
Phone: {contact.phone or 'Not provided'}
Subject: {contact.subject}

Message:
{contact.message}

---
This message was sent through the VeilForge contact form.
You can reply directly to: {contact.email}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                
                msg.attach(MIMEText(email_body, 'plain'))
                
                # Connect to SMTP server and send
                server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
                server.starttls()
                server.login(EMAIL_CONFIG['EMAIL_USER'], EMAIL_CONFIG['EMAIL_PASSWORD'])
                
                text = msg.as_string()
                server.sendmail(EMAIL_CONFIG['EMAIL_USER'], EMAIL_CONFIG['RECIPIENT_EMAIL'], text)
                server.quit()
                
                email_sent = True
                print("✅ Email sent successfully via SMTP!")
                print(f"  To: {EMAIL_CONFIG['RECIPIENT_EMAIL']}")
                print(f"  Subject: {subject}")
                
            except Exception as smtp_error:
                print(f"❌ SMTP email failed: {smtp_error}")
                email_sent = False
        else:
            print("⚠️ SMTP not configured or credentials not set")
            print("📧 Message details logged:")
            print(f"  Name: {contact.name}")
            print(f"  Email: {contact.email}")
            print(f"  Subject: {contact.subject}")
            print(f"  Message: {contact.message[:100]}...")
            
        # Try alternative email service if SMTP fails
        if not email_sent:
            try:
                print("🚀 Trying alternative email notification...")
                
                # You could integrate with services like:
                # - Formspree
                # - EmailJS
                # - SendGrid
                # - Mailgun
                # - AWS SES
                
                # For now, we'll create a detailed log
                email_log = {
                    'timestamp': datetime.now().isoformat(),
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'subject': contact.subject,
                    'message': contact.message,
                    'status': 'logged_only'
                }
                
                print("📝 Contact message logged for manual processing:")
                print(json.dumps(email_log, indent=2))
                
            except Exception as alt_error:
                print(f"❌ Alternative email service failed: {alt_error}")
        
        # Return appropriate response based on email status
        if email_sent:
            return {
                "success": True,
                "message": f"Message sent successfully! We received your inquiry and sent a confirmation to {EMAIL_CONFIG['RECIPIENT_EMAIL']}. We'll get back to you at {contact.email} soon!",
                "email_sent": True
            }
        else:
            return {
                "success": True,
                "message": f"Message received successfully! We have logged your inquiry and will get back to you at {contact.email} within 24 hours.",
                "email_sent": False,
                "note": "Email service is currently being configured. Your message has been logged for manual processing."
            }
        
    except Exception as e:
        print(f"Error processing contact message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@app.get("/api/users/{user_id}/operations")
async def get_user_operations(user_id: str, limit: int = 50, 
                             db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Get user's operation history"""
    try:
        if db:
            operations = db.get_user_operations(user_id, limit)
            return {"success": True, "operations": operations}
        else:
            return {"success": True, "operations": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/users/{user_id}/stats")
async def get_user_stats(user_id: str, db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Get user operation statistics"""
    try:
        if db:
            stats = db.get_operation_stats(user_id)
            return {"success": True, "stats": stats}
        else:
            return {"success": True, "stats": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/projects", response_model=Dict[str, Any])
async def create_project(project: ProjectRequest):
    """Create a new steganography project"""
    try:
        project_id = str(uuid.uuid4())
        
        # Create project directory
        project_dir = OUTPUT_DIR / project_id
        project_dir.mkdir(exist_ok=True)
        
        project_data = {
            "id": project_id,
            "name": project.name,
            "description": project.description,
            "type": project.project_type,
            "created_at": datetime.now().isoformat(),
            "directory": str(project_dir)
        }
        
        return {
            "success": True,
            "project": project_data,
            "message": "Project created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEXT-TO-IMAGE GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/generate-image", response_model=Dict[str, Any])
async def generate_image_from_text(request: TextToImageRequest):
    """Generate an image from text prompt using FLUX.1-schnell model"""
    try:
        if not text_to_image_client:
            print(f"[WARNING] Text-to-image client not available. HF_TOKEN: {'SET' if os.getenv('HF_TOKEN') else 'NOT SET'}")
            print(f"[INFO] Using fallback placeholder image generator")
            
            # Create a simple placeholder image when HF service is not available
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a 512x512 image with a gradient background
            image = Image.new('RGB', (512, 512), color=(70, 130, 180))
            draw = ImageDraw.Draw(image)
            
            # Add some visual elements
            for i in range(10):
                x = i * 51
                draw.rectangle([x, 0, x + 25, 512], fill=(100 + i * 15, 150 + i * 10, 200 + i * 5))
            
            # Try to add text
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            if font:
                text = f"Generated Image\n{request.prompt[:30]}"
                draw.text((50, 250), text, fill=(255, 255, 255), font=font)
            
            print(f"[INFO] Created placeholder image")
        else:
            print(f"[INFO] Generating image for prompt: {request.prompt[:50]}...")
            # Generate image using Hugging Face API
            print(f"[INFO] Calling Hugging Face API...")
            image = text_to_image_client.text_to_image(request.prompt)
            print(f"[INFO] Image generated successfully, type: {type(image)}")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        operation_id = str(uuid.uuid4())
        filename = f"generated_{timestamp}_{operation_id}.png"
        
        # Create output path
        output_path = OUTPUT_DIR / filename
        OUTPUT_DIR.mkdir(exist_ok=True)
        
        try:
            # Save the generated image
            image.save(str(output_path))
            print(f"[INFO] Image saved to: {output_path}")
            
            # Verify the file was saved correctly
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"[INFO] Saved image size: {file_size} bytes")
                if file_size == 0:
                    print(f"[ERROR] Saved image file is empty!")
                    raise Exception("Generated image file is empty")
            else:
                print(f"[ERROR] Image file was not saved to expected path")
                raise Exception("Image file was not saved")
            
            # Create project data if project name is provided
            project_data = None
            if request.project_name:
                project_id = str(uuid.uuid4())
                project_dir = OUTPUT_DIR / project_id
                project_dir.mkdir(exist_ok=True)
                
                project_data = {
                    "id": project_id,
                    "name": request.project_name,
                    "description": request.project_description or f"Generated image from prompt: {request.prompt[:50]}...",
                    "type": "pixelvault",
                    "created_at": datetime.now().isoformat(),
                    "directory": str(project_dir),
                    "generated_image": filename,
                    "prompt": request.prompt
                }
            
            return {
                "success": True,
                "operation_id": operation_id,
                "message": "Image generated successfully",
                "image_filename": filename,
                "image_url": f"/api/download/{filename}",
                "prompt": request.prompt,
                "project": project_data
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Image generation failed: {str(e)}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STEGANOGRAPHY ENDPOINTS
# ============================================================================

@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get supported file formats for each steganography type"""
    return {
        "image": {
            "carrier_formats": ["png", "jpg", "jpeg", "bmp", "tiff", "gif"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "video": {
            "carrier_formats": ["mp4", "avi", "mov", "mkv", "wmv", "flv"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "audio": {
            "carrier_formats": ["wav", "mp3", "flac", "ogg", "aac", "m4a"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        },
        "document": {
            "carrier_formats": ["pdf", "docx", "txt", "rtf"],
            "content_formats": ["text", "file"],
            "max_size_mb": 0  # No limit
        }
    }

@app.get("/api/generate-password")
async def generate_password(length: int = 16, include_symbols: bool = True):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return {
        "password": password,
        "length": length,
        "strength": "strong" if length >= 12 else "medium" if length >= 8 else "weak"
    }

@app.post("/api/embed", response_model=OperationResponse)
async def embed_data(
    carrier_file: UploadFile = File(...),
    content_file: Optional[UploadFile] = File(None),
    carrier_type: Optional[str] = Form(None),
    content_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    password: str = Form(...),
    encryption_type: str = Form("aes-256-gcm"),
    project_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Embed data into carrier file"""
    
    # Generate operation ID
    operation_id = str(uuid.uuid4())
    
    try:
        # Auto-detect carrier type if not provided
        if not carrier_type:
            file_extension = Path(carrier_file.filename).suffix.lower()
            if file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                carrier_type = "image"
            elif file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                carrier_type = "video"
            elif file_extension in ['.wav', '.mp3', '.flac', '.ogg', '.aac', '.m4a']:
                carrier_type = "audio"
            elif file_extension in ['.pdf', '.docx', '.txt', '.doc']:
                carrier_type = "document"
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        print(f"[API] Detected carrier type: {carrier_type} for file: {carrier_file.filename}")
        print(f"[API] Original filename: {carrier_file.filename}")
        print(f"[API] File extension: {Path(carrier_file.filename).suffix.lower()}")
        
        # Validate inputs
        if content_type == "text" and not text_content:
            raise HTTPException(status_code=400, detail="Text content required for text embedding")
        
        if content_type == "file" and not content_file:
            raise HTTPException(status_code=400, detail="File required for file embedding")
        
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting embedding process",
            "created_at": datetime.now().isoformat(),
            "carrier_type": carrier_type,
            "content_type": content_type
        }
        
        # Save carrier file synchronously
        carrier_filename = generate_unique_filename(carrier_file.filename, "carrier_")
        carrier_path = UPLOAD_DIR / carrier_filename
        
        print(f"[API] Generated carrier filename: {carrier_filename}")
        print(f"[API] Carrier path: {carrier_path}")
        
        # Read carrier file content and save it
        content = await carrier_file.read()
        with open(carrier_path, "wb") as f:
            f.write(content)
            
        print(f"[API] Carrier file saved successfully: {os.path.getsize(carrier_path)} bytes")
        
        # If the uploaded filename lacked an extension, try to detect it from the binary
        if not carrier_path.suffix:
            detected_ext = detect_file_format_from_binary(content)
            if detected_ext:
                # Rename carrier file to include the detected extension
                new_carrier_filename = f"{carrier_path.name}{detected_ext}"
                new_carrier_path = UPLOAD_DIR / new_carrier_filename
                try:
                    os.rename(carrier_path, new_carrier_path)
                    carrier_path = new_carrier_path
                    carrier_filename = carrier_path.name
                    print(f"[API] Renamed carrier file to include detected extension: {carrier_filename}")
                except Exception as e:
                    print(f"[API] Failed to rename carrier file to add extension: {e}")
            else:
                print(f"[API] Could not detect file format for extensionless file")
        else:
            print(f"[API] Carrier file already has extension: {carrier_path.suffix}")
        
        # Save content file if provided
        content_file_path = None
        if content_file:
            content_filename = generate_unique_filename(content_file.filename, "content_")
            content_file_path = UPLOAD_DIR / content_filename
            
            with open(content_file_path, "wb") as f:
                content = await content_file.read()
                f.write(content)
        
        # Log operation start in database - completely optional, don't let it fail the main operation
        db_operation_id = None
        if db:
            try:
                # Only attempt database logging if we have a valid user_id
                # If user_id is invalid or missing, just skip database logging entirely
                if user_id and user_id.strip():
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="hide",
                        media_type=carrier_type,
                        original_filename=carrier_file.filename,
                        password=password
                    )
                else:
                    print(f"[INFO] Skipping database logging - no valid user_id provided")
                        
            except Exception as e:
                # Database logging is completely optional - continue without it
                print(f"[INFO] Database logging failed, continuing without it: {e}")
                db_operation_id = None
        
        # Start background processing with file paths instead of UploadFile objects
        # Generate output filename early so we can return it in the response
        # Use clean filename generation for better user experience
        # Use the actual saved carrier filename (may have been renamed to include extension)
        expected_output_filename = generate_clean_output_filename(carrier_filename, "stego_")
        
        print(f"[API] Expected output filename: {expected_output_filename}")
        print(f"[API] Output extension: {Path(expected_output_filename).suffix}")
        print(f"[API] Original carrier filename: {carrier_file.filename}")
        print(f"[API] Generated carrier filename: {carrier_filename}")
        
        background_tasks.add_task(
            process_embed_operation,
            operation_id,
            str(carrier_path),
            str(content_file_path) if content_file_path else None,
            carrier_type,
            content_type,
            text_content,
            password,
            encryption_type,
            project_name,
            user_id,
            db,
            expected_output_filename,  # Pass the expected filename
            db_operation_id  # Pass the database operation ID separately
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Embedding operation started",
            output_filename=expected_output_filename
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forensic-embed", response_model=OperationResponse)
async def forensic_embed_data(
    carrier_file: UploadFile = File(...),
    content_file: UploadFile = File(...),
    password: str = Form(...),
    forensic_metadata: str = Form(...),
    content_type: str = Form("forensic"),
    encryption_type: str = Form("aes-256-gcm"),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Embed forensic evidence with metadata into carrier file"""
    
    # Generate operation ID
    operation_id = str(uuid.uuid4())
    
    try:
        # Parse forensic metadata
        try:
            metadata = json.loads(forensic_metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid forensic metadata JSON")
        
        # Auto-detect carrier type
        file_extension = Path(carrier_file.filename).suffix.lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            carrier_type = "image"
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            carrier_type = "video"
        elif file_extension in ['.wav', '.mp3', '.flac', '.ogg', '.aac', '.m4a']:
            carrier_type = "audio"
        elif file_extension in ['.pdf', '.docx', '.txt', '.doc']:
            carrier_type = "document"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_extension}")
        
        print(f"[FORENSIC API] Detected carrier type: {carrier_type} for file: {carrier_file.filename}")
        print(f"[FORENSIC API] Forensic metadata: {metadata}")
        
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting forensic embedding process",
            "created_at": datetime.now().isoformat(),
            "carrier_type": carrier_type,
            "content_type": "forensic",
            "forensic_metadata": metadata
        }
        
        # Save carrier file synchronously
        carrier_filename = f"{operation_id}_{carrier_file.filename}"
        carrier_path = UPLOAD_DIR / carrier_filename
        
        with open(carrier_path, "wb") as buffer:
            shutil.copyfileobj(carrier_file.file, buffer)
        
        # Save content file
        content_filename = f"{operation_id}_content_{content_file.filename}"
        content_file_path = UPLOAD_DIR / content_filename
        
        with open(content_file_path, "wb") as buffer:
            shutil.copyfileobj(content_file.file, buffer)
        
        # Create combined forensic content that includes both file and metadata
        forensic_content = {
            "forensic_metadata": metadata,
            "original_filename": content_file.filename,
            "content_type": "file_with_metadata"
        }
        
        # Save forensic metadata as text content alongside the file
        forensic_text = json.dumps(forensic_content, indent=2)
        
        # Database logging
        db_operation_id = None
        if db:
            try:
                db_operation_id = db.log_operation(
                    operation_id=operation_id,
                    operation_type="forensic_embed",
                    carrier_filename=carrier_file.filename,
                    content_filename=content_file.filename,
                    user_id=user_id,
                    project_name=metadata.get('case_id', 'Forensic Evidence'),
                    status="processing",
                    progress=0
                )
            except Exception as db_error:
                print(f"[WARNING] Database logging failed: {db_error}")
        
        # Start background processing
        expected_output_filename = generate_unique_filename(carrier_filename, "forensic_")
        
        background_tasks.add_task(
            process_forensic_embed_operation,
            operation_id,
            str(carrier_path),
            str(content_file_path),
            carrier_type,
            forensic_text,
            password,
            encryption_type,
            metadata,
            user_id,
            db,
            expected_output_filename,
            db_operation_id
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Forensic embedding operation started",
            output_filename=expected_output_filename
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/embed-batch", response_model=OperationResponse)
async def embed_data_batch(
    carrier_files: List[UploadFile] = File(...),
    content_file: Optional[UploadFile] = File(None),
    content_type: str = Form(...),
    text_content: Optional[str] = Form(None),
    password: str = Form(...),
    encryption_type: str = Form("aes-256-gcm"),
    project_name: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """
    Embed the same data/message into multiple carrier files
    Returns a batch operation ID that manages all individual operations
    """
    try:
        batch_operation_id = str(uuid.uuid4())
        
        # Validate that we have carrier files
        if not carrier_files or len(carrier_files) == 0:
            raise HTTPException(status_code=400, detail="At least one carrier file is required")
        
        # Validate that all carrier files are properly uploaded
        for i, carrier_file in enumerate(carrier_files):
            if not carrier_file.filename:
                raise HTTPException(status_code=400, detail=f"Carrier file {i+1} has no filename")
        
        # Initialize batch job tracking
        batch_jobs = {
            "batch_id": batch_operation_id,
            "total_files": len(carrier_files),
            "completed_files": 0,
            "failed_files": 0,
            "individual_operations": [],
            "output_files": [],
            "status": "starting",
            "created_at": datetime.now().isoformat()
        }
        
        active_jobs[batch_operation_id] = batch_jobs
        
        # Process each carrier file
        for i, carrier_file in enumerate(carrier_files):
            try:
                # Auto-detect carrier type if not provided
                file_extension = Path(carrier_file.filename).suffix.lower()
                carrier_type = None
                
                # Detect carrier type based on file extension
                if file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
                    carrier_type = "video"
                elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    carrier_type = "image"
                elif file_extension in ['.wav', '.mp3', '.flac', '.ogg']:
                    carrier_type = "audio"
                elif file_extension in ['.pdf', '.doc', '.docx']:
                    carrier_type = "document"
                else:
                    # Default to document for unknown types
                    carrier_type = "document"
                
                print(f"[BATCH] Processing carrier file {i+1}/{len(carrier_files)}: {carrier_file.filename} as {carrier_type}")
                
                # Generate unique filenames for this carrier file
                carrier_filename = generate_unique_filename(carrier_file.filename, f"batch_{i+1}_carrier_")
                carrier_path = UPLOAD_DIR / carrier_filename
                
                # Save carrier file
                with open(carrier_path, "wb") as f:
                    content = await carrier_file.read()
                    f.write(content)
                
                # Handle content file for this iteration (need to read it fresh each time)
                content_file_path = None
                if content_file and content_type == "file":
                    content_filename = generate_unique_filename(content_file.filename, f"batch_{i+1}_content_")
                    content_file_path = UPLOAD_DIR / content_filename
                    
                    # Read the content file (need to reset the read position)
                    await content_file.seek(0)  # Reset file position
                    with open(content_file_path, "wb") as f:
                        content = await content_file.read()
                        f.write(content)
                
                # Create individual operation ID
                individual_operation_id = str(uuid.uuid4())
                
                # Log operation start in database for each file
                db_operation_id = None
                if db and user_id:
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="hide",
                        media_type=carrier_type,
                        original_filename=carrier_file.filename,
                        password=password
                    )
                
                # Generate expected output filename from actual saved carrier filename with clean naming
                expected_output_filename = generate_clean_output_filename(carrier_filename, "stego_")
                
                # Add to batch tracking
                batch_jobs["individual_operations"].append({
                    "operation_id": individual_operation_id,
                    "carrier_filename": carrier_filename,
                    "carrier_type": carrier_type,
                    "status": "pending",
                    "expected_output": expected_output_filename
                })
                
                # Start background processing for this file
                background_tasks.add_task(
                    process_batch_embed_operation,
                    individual_operation_id,
                    batch_operation_id,
                    i,  # file index
                    str(carrier_path),
                    str(content_file_path) if content_file_path else None,
                    carrier_type,
                    content_type,
                    text_content,
                    password,
                    encryption_type,
                    project_name,
                    user_id,
                    db,
                    expected_output_filename,
                    db_operation_id
                )
                
            except Exception as e:
                print(f"[BATCH ERROR] Failed to process carrier file {i+1}: {str(e)}")
                batch_jobs["failed_files"] += 1
                batch_jobs["individual_operations"].append({
                    "operation_id": "failed",
                    "carrier_filename": carrier_file.filename if hasattr(carrier_file, 'filename') else f"file_{i+1}",
                    "carrier_type": "unknown",
                    "status": "failed",
                    "error": str(e),
                    "expected_output": None
                })
        
        # Update batch status
        active_jobs[batch_operation_id]["status"] = "processing"
        
        return OperationResponse(
            success=True,
            operation_id=batch_operation_id,
            message=f"Batch embedding started for {len(carrier_files)} files",
            output_filename=f"batch_{len(carrier_files)}_files"
        )
        
    except Exception as e:
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["status"] = "failed"
            active_jobs[batch_operation_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/extract", response_model=OperationResponse)
async def extract_data(
    stego_file: UploadFile = File(...),
    password: str = Form(...),
    output_format: str = Form("auto"),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Extract hidden data from steganographic file"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting extraction process",
            "created_at": datetime.now().isoformat(),
            "operation_type": "extract"
        }
        
        # Determine file type
        file_extension = Path(stego_file.filename).suffix.lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
            carrier_type = "image"
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            carrier_type = "video"
        elif file_extension in ['.wav', '.mp3', '.flac']:
            carrier_type = "audio"
        elif file_extension in ['.pdf', '.docx', '.txt']:
            carrier_type = "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save stego file synchronously
        stego_filename = generate_unique_filename(stego_file.filename, "stego_")
        stego_file_path = UPLOAD_DIR / stego_filename
        
        with open(stego_file_path, "wb") as f:
            content = await stego_file.read()
            f.write(content)
        
        # Log operation start in database - completely optional, don't let it fail the main operation
        db_operation_id = None
        if db:
            try:
                # Only attempt database logging if we have a valid user_id
                # If user_id is invalid or missing, just skip database logging entirely
                if user_id and user_id.strip():
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="extract",
                        media_type=carrier_type,
                        original_filename=stego_file.filename,
                        password=password
                    )
                else:
                    print(f"[INFO] Skipping database logging - no valid user_id provided")
                        
            except Exception as e:
                # Database logging is completely optional - continue without it
                print(f"[INFO] Database logging failed, continuing without it: {e}")
                db_operation_id = None
        
        # Start background processing with file path instead of UploadFile
        background_tasks.add_task(
            process_extract_operation,
            operation_id,
            str(stego_file_path),
            carrier_type,
            password,
            output_format,
            user_id,
            db,
            db_operation_id  # Pass the database operation ID
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Extraction operation started"
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forensic-extract", response_model=OperationResponse)
async def forensic_extract_data(
    stego_file: UploadFile = File(...),
    password: str = Form(...),
    output_format: str = Form("forensic"),
    user_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Optional[SteganographyDatabase] = Depends(get_db)
):
    """Extract forensic evidence with metadata from steganographic file"""
    
    operation_id = str(uuid.uuid4())
    
    try:
        # Initialize job tracking
        active_jobs[operation_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting forensic extraction process",
            "created_at": datetime.now().isoformat(),
            "operation_type": "forensic_extract"
        }
        
        # Determine file type
        file_extension = Path(stego_file.filename).suffix.lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
            carrier_type = "image"
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            carrier_type = "video"
        elif file_extension in ['.wav', '.mp3', '.flac']:
            carrier_type = "audio"
        elif file_extension in ['.pdf', '.docx', '.txt']:
            carrier_type = "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save stego file synchronously
        stego_filename = generate_unique_filename(stego_file.filename, "forensic_")
        stego_file_path = UPLOAD_DIR / stego_filename
        
        with open(stego_file_path, "wb") as f:
            content = await stego_file.read()
            f.write(content)
        
        # Log operation start in database
        db_operation_id = None
        if db:
            try:
                if user_id and user_id.strip():
                    db_operation_id = db.log_operation_start(
                        user_id=user_id,
                        operation_type="forensic_extract",
                        media_type=carrier_type,
                        file_name=stego_file.filename
                    )
                    print(f"[FORENSIC EXTRACT] Database operation logged: {db_operation_id}")
                else:
                    print(f"[FORENSIC EXTRACT] No user_id provided, skipping database logging")
            except Exception as db_error:
                print(f"[WARNING] Database logging failed: {db_error}")
        
        # Start background processing
        background_tasks.add_task(
            process_forensic_extract_operation,
            operation_id,
            str(stego_file_path),
            carrier_type,
            password,
            output_format,
            user_id,
            db,
            db_operation_id
        )
        
        return OperationResponse(
            success=True,
            operation_id=operation_id,
            message="Forensic extraction operation started"
        )
        
    except Exception as e:
        if operation_id in active_jobs:
            update_job_status(operation_id, "failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    """Analyze a file to check for existing hidden data"""
    try:
        # Determine file type
        file_extension = Path(file.filename).suffix.lower()
        if file_extension in ['.png', '.jpg', '.jpeg', '.bmp']:
            carrier_type = "image"
        elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
            carrier_type = "video"
        elif file_extension in ['.wav', '.mp3', '.flac']:
            carrier_type = "audio"
        elif file_extension in ['.pdf', '.docx', '.txt']:
            carrier_type = "document"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Save file temporarily
        temp_filename = generate_unique_filename(file.filename, "analyze_")
        temp_file_path = UPLOAD_DIR / temp_filename
        
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise HTTPException(status_code=500, detail=f"No manager available for {carrier_type}")
        
        # Try to extract existing data
        analysis_result = {
            "has_hidden_data": False,
            "is_layered": False,
            "layer_count": 0,
            "data_preview": None,
            "error": None
        }
        
        try:
            extracted_data = manager.extract_data(str(temp_file_path))
            
            if extracted_data and extracted_data.strip():
                analysis_result["has_hidden_data"] = True
                
                # Check if it's layered data
                data_to_check = extracted_data
                if isinstance(extracted_data, tuple):
                    data_to_check = extracted_data[0]
                
                if isinstance(data_to_check, bytes):
                    try:
                        data_to_check = data_to_check.decode('utf-8')
                    except UnicodeDecodeError:
                        data_to_check = str(data_to_check)
                
                if is_layered_container(data_to_check):
                    analysis_result["is_layered"] = True
                    layers = extract_layered_data_container(data_to_check)
                    analysis_result["layer_count"] = len(layers)
                    analysis_result["data_preview"] = f"Layered container with {len(layers)} layers"
                else:
                    analysis_result["layer_count"] = 1
                    # Provide safe preview
                    if isinstance(data_to_check, str):
                        analysis_result["data_preview"] = data_to_check[:100] + "..." if len(data_to_check) > 100 else data_to_check
                    else:
                        analysis_result["data_preview"] = f"Binary data ({len(data_to_check)} bytes)"
        
        except Exception as e:
            analysis_result["error"] = f"Failed to extract data: {str(e)}"
        
        finally:
            # Clean up temporary file
            if temp_file_path.exists():
                os.remove(temp_file_path)
        
        return {
            "success": True,
            "analysis": analysis_result
        }
        
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals() and temp_file_path.exists():
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# JOB STATUS AND DOWNLOAD ENDPOINTS
# ============================================================================

@app.get("/api/operations/{operation_id}/status", response_model=StatusResponse)
async def get_operation_status(operation_id: str):
    """Get status of a steganography operation (regular or batch)"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    
    # Handle batch operations
    if "batch_id" in job:
        total_files = job.get("total_files", 0)
        completed_files = job.get("completed_files", 0)
        failed_files = job.get("failed_files", 0)
        
        # Calculate overall progress
        progress = 0
        if total_files > 0:
            progress = int((completed_files + failed_files) * 100 / total_files)
        
        # Create batch-specific result
        batch_result = {
            "batch_operation": True,
            "total_files": total_files,
            "completed_files": completed_files,
            "failed_files": failed_files,
            "output_files": job.get("output_files", []),
            "individual_operations": job.get("individual_operations", [])
        }
        
        # Convert error to string if it's a dict
        error = job.get("error")
        if isinstance(error, dict):
            error = str(error)
        
        return StatusResponse(
            status=job["status"],
            progress=progress,
            message=f"Processed {completed_files + failed_files}/{total_files} files",
            error=error,
            result=batch_result
        )
    else:
        # Handle regular operations
        # Convert error to string if it's a dict
        error = job.get("error")
        if isinstance(error, dict):
            error = str(error)
        
        return StatusResponse(
            status=job["status"],
            progress=job.get("progress"),
            message=job.get("message"),
            error=error,
            result=job.get("result")
        )

@app.get("/api/operations/{operation_id}/download")
async def download_result(operation_id: str):
    """Download the result file of an operation"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Operation not completed")
    
    result = job.get("result")
    if not result or not result.get("output_file"):
        raise HTTPException(status_code=404, detail="Result file not found")
    
    output_file = result["output_file"]
    if not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    filename = result.get("filename", os.path.basename(output_file))
    
    # Determine media type based on file extension
    file_ext = Path(filename).suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    media_type = media_type_map.get(file_ext, "application/octet-stream")
    
    return FileResponse(
        output_file,
        filename=filename,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename=\"{filename}\""}
    )

@app.get("/api/operations/{operation_id}/download-batch")
async def download_batch_result(operation_id: str):
    """Download all result files from a batch operation as a ZIP archive"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Batch operation not found")
    
    job = active_jobs[operation_id]
    
    # Check if this is a batch operation
    if "batch_id" not in job:
        raise HTTPException(status_code=400, detail="This is not a batch operation")
    
    if job["status"] not in ["completed", "completed_with_errors"]:
        raise HTTPException(status_code=400, detail="Batch operation not completed")
    
    output_files = job.get("output_files", [])
    if not output_files:
        raise HTTPException(status_code=404, detail="No output files found")
    
    # Create a temporary ZIP file
    zip_filename = f"batch_results_{operation_id[:8]}.zip"
    zip_path = OUTPUT_DIR / zip_filename
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file_info in enumerate(output_files):
                output_file_path = file_info["output_path"]
                if os.path.exists(output_file_path):
                    # Use original filename or create a numbered filename
                    archive_filename = file_info["output_filename"]
                    
                    # Add file to ZIP with the proper name
                    zipf.write(output_file_path, archive_filename)
                    print(f"[BATCH ZIP] Added {archive_filename} to archive")
                else:
                    print(f"[BATCH ZIP] Warning: File not found: {output_file_path}")
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=500, detail="Failed to create ZIP archive")
        
        # Return the ZIP file
        return FileResponse(
            zip_path,
            filename=zip_filename,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=\"{zip_filename}\""}
        )
        
    except Exception as e:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP archive: {str(e)}")

@app.get("/api/operations/{operation_id}/download-forensic")
async def download_forensic_result(operation_id: str):
    """Download forensic evidence as a ZIP containing the extracted file and metadata.txt"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Operation not completed")
    
    result = job.get("result")
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # Check if this is a forensic extraction with metadata
    forensic_metadata = result.get("forensic_metadata")
    if not forensic_metadata:
        # Fallback to regular download for non-forensic files
        return await download_result(operation_id)
    
    # The output_path already points to the correctly created forensic ZIP file
    output_file = result.get("output_path")
    if not output_file or not os.path.exists(output_file):
        raise HTTPException(status_code=404, detail="Output file not found")
    
    # Get the filename from result or generate based on case info
    zip_filename = result.get("filename")
    if not zip_filename:
        case_id = forensic_metadata.get('case_id', 'evidence')
        zip_filename = f"forensic_evidence_{case_id}_{operation_id[:8]}.zip"
    
    print(f"[FORENSIC DOWNLOAD] Serving forensic ZIP: {zip_filename}")
    
    # Return the already correctly created ZIP file
    return FileResponse(
        output_file,
        filename=zip_filename,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=\"{zip_filename}\""}
    )

@app.delete("/api/operations/{operation_id}")
async def delete_operation(operation_id: str):
    """Delete an operation and its files"""
    if operation_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    job = active_jobs[operation_id]
    
    # Clean up files
    result = job.get("result", {})
    if result.get("output_file") and os.path.exists(result["output_file"]):
        os.remove(result["output_file"])
    
    # Remove from active jobs
    del active_jobs[operation_id]
    
    return {"success": True, "message": "Operation deleted"}

# ============================================================================
# BACKGROUND PROCESSING FUNCTIONS
# ============================================================================

def run_with_timeout(func, args, kwargs, timeout_seconds):
    """Run a function with a timeout to prevent hanging in production"""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            return future.result(timeout=timeout_seconds)
    except concurrent.futures.TimeoutError:
        raise Exception(f"Operation timed out after {timeout_seconds} seconds")

async def process_embed_operation(
    operation_id: str,
    carrier_file_path: str,
    content_file_path: Optional[str],
    carrier_type: str,
    content_type: str,
    text_content: Optional[str],
    password: str,
    encryption_type: str,
    project_name: Optional[str],
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    expected_output_filename: Optional[str] = None,
    db_operation_id: Optional[str] = None
):
    """Background task to process embedding operation"""
    
    import json
    start_time = time.time()
    
    print(f"[EMBED] Starting embedding operation {operation_id}")
    print(f"[EMBED] Carrier: {carrier_type}, Content: {content_type}")
    
    try:
        update_job_status(operation_id, "processing", 30, "Preparing content")
        
        # Prepare content to hide
        if content_type == "text":
            content_to_hide = text_content
        else:
            # Read content from file
            with open(content_file_path, "rb") as f:
                content_to_hide = f.read()
        
        update_job_status(operation_id, "processing", 50, "Performing steganography")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        update_job_status(operation_id, "processing", 40, "Checking for existing hidden data")
        
        # Check if carrier already contains hidden data
        existing_data = None
        original_filename = None
        try:
            print(f"[EMBED] Checking if carrier file already contains hidden data...")
            # Try to extract existing data (this will show extraction logs but failure is normal for clean files)
            extraction_result = manager.extract_data(carrier_file_path)
            
            # Handle tuple return (data, filename) from some managers
            if isinstance(extraction_result, tuple):
                existing_data, original_filename = extraction_result
            else:
                existing_data = extraction_result
                original_filename = None
            
            # Check if we found meaningful existing data
            if existing_data:
                print(f"[EMBED] ✅ Found existing data: type={type(existing_data)}, size={len(existing_data) if hasattr(existing_data, '__len__') else 'unknown'}")
                
                # Check if existing data is already a layered container
                is_existing_layered = False
                existing_data_for_check = existing_data
                
                # Add comprehensive debugging for second embedding attempt
                print(f"[EMBED DEBUG] Processing existing data - Type: {type(existing_data)}")
                print(f"[EMBED DEBUG] Current operation - content_type: {content_type}")
                print(f"[EMBED DEBUG] Current operation - content_file_path: {content_file_path}")
                print(f"[EMBED DEBUG] Current operation - text_content: {text_content is not None}")
                
                if isinstance(existing_data, bytes):
                    print(f"[EMBED DEBUG] Bytes data length: {len(existing_data)}")
                    print(f"[EMBED DEBUG] First 100 bytes: {existing_data[:100]}")
                
                # Only try to decode bytes to string if it looks like JSON
                if isinstance(existing_data, bytes):
                    try:
                        # Only decode if it starts with { (JSON indicator)
                        if existing_data.startswith(b'{'):
                            decoded_str = existing_data.decode('utf-8')
                            print(f"[EMBED DEBUG] Decoded string length: {len(decoded_str)}")
                            print(f"[EMBED DEBUG] First 200 chars: {decoded_str[:200]}")
                            
                            is_existing_layered = is_layered_container(decoded_str)
                            print(f"[EMBED DEBUG] is_layered_container result: {is_existing_layered}")
                            
                            if is_existing_layered:
                                existing_data_for_check = decoded_str
                                print(f"[EMBED DEBUG] Set existing_data_for_check to decoded string")
                            else:
                                print(f"[EMBED DEBUG] Not a layered container, treating as binary data")
                    except (UnicodeDecodeError, json.JSONDecodeError) as decode_error:
                        # Not a layered container, treat as binary data
                        print(f"[EMBED DEBUG] Decode error: {decode_error}, treating as binary data")
                        pass
                elif isinstance(existing_data, str):
                    print(f"[EMBED DEBUG] String data length: {len(existing_data)}")
                    print(f"[EMBED DEBUG] First 200 chars: {existing_data[:200]}")
                    is_existing_layered = is_layered_container(existing_data)
                    print(f"[EMBED DEBUG] is_layered_container result for string: {is_existing_layered}")
                
                print(f"[EMBED DEBUG] Final check - is_existing_layered: {is_existing_layered}, existing_data_for_check type: {type(existing_data_for_check)}")
                
                # Only proceed with layering if we have non-empty data
                should_create_layer = False
                if isinstance(existing_data, str) and existing_data.strip():
                    should_create_layer = True
                elif isinstance(existing_data, bytes) and len(existing_data) > 0:
                    should_create_layer = True
                
                print(f"[EMBED DEBUG] should_create_layer: {should_create_layer}")
                
                if should_create_layer:
                    update_job_status(operation_id, "processing", 45, f"Found existing data, creating layered container")
                    
                    # Prepare existing layers
                    existing_layers = []  # Initialize to prevent NoneType errors
                    
                    if is_existing_layered:
                        # Extract existing layers from layered container
                        print(f"[EMBED DEBUG] Attempting to extract existing layers from layered container")
                        print(f"[EMBED DEBUG] existing_data_for_check type: {type(existing_data_for_check)}")
                        print(f"[EMBED DEBUG] existing_data_for_check value preview: {str(existing_data_for_check)[:500] if existing_data_for_check else 'None'}")
                        
                        try:
                            # Add extra safety check before calling extraction
                            if existing_data_for_check is None:
                                print(f"[EMBED ERROR] existing_data_for_check is None before extraction!")
                                existing_layers = []
                            else:
                                extracted_layers = extract_layered_data_container(existing_data_for_check)
                                print(f"[EMBED DEBUG] extract_layered_data_container returned: {type(extracted_layers)}")
                                
                                if extracted_layers is not None and isinstance(extracted_layers, list):
                                    existing_layers = extracted_layers
                                    print(f"[EMBED DEBUG] Successfully extracted {len(existing_layers)} existing layers")
                                    update_job_status(operation_id, "processing", 47, f"Extracted {len(existing_layers)} existing layers")
                                    
                                    # Debug each extracted layer
                                    for idx, layer in enumerate(existing_layers):
                                        if layer is None:
                                            print(f"[EMBED ERROR] Layer {idx} is None!")
                                        elif not isinstance(layer, tuple) or len(layer) != 2:
                                            print(f"[EMBED ERROR] Layer {idx} has invalid format: {type(layer)}, length: {len(layer) if hasattr(layer, '__len__') else 'no length'}")
                                        else:
                                            print(f"[EMBED DEBUG] Layer {idx}: content type={type(layer[0])}, filename='{layer[1]}'")
                                else:
                                    print(f"[EMBED WARNING] extract_layered_data_container returned {type(extracted_layers)}, using empty list")
                                    existing_layers = []
                        except Exception as e:
                            print(f"[EMBED ERROR] Failed to extract existing layers: {e}")
                            print(f"[EMBED ERROR] Exception type: {type(e)}")
                            import traceback
                            print(f"[EMBED ERROR] Traceback: {traceback.format_exc()}")
                            existing_layers = []
                    else:
                        # Convert existing single data to first layer
                        # Determine appropriate filename for existing data
                        if original_filename and original_filename.strip():
                            existing_filename = original_filename
                        else:
                            # Auto-detect filename based on content type
                            if isinstance(existing_data, bytes):
                                detected_ext = detect_file_format_from_binary(existing_data)
                                if detected_ext:
                                    existing_filename = f"existing_file{detected_ext}"
                                else:
                                    existing_filename = "existing_file.bin"
                            else:
                                existing_filename = "existing_text.txt"
                        
                        existing_layers = [(existing_data, existing_filename)]
                        update_job_status(operation_id, "processing", 47, f"Converting existing data to layer: {existing_filename}")
                    
                    # Prepare new content layer
                    new_layer_info = None
                    try:
                        if content_type == "text":
                            new_layer_info = (content_to_hide, "new_message.txt")
                            print(f"[EMBED DEBUG] Created text layer: new_message.txt")
                        else:
                            # For file content, preserve original filename
                            new_filename = "new_file.bin"  # Default fallback
                            
                            if content_file_path and Path(content_file_path).exists():
                                new_filename = Path(content_file_path).name
                                print(f"[EMBED DEBUG] Using original filename: {new_filename}")
                            else:
                                # Detect format if no filename available or file doesn't exist
                                if isinstance(content_to_hide, bytes):
                                    detected_ext = detect_file_format_from_binary(content_to_hide)
                                    new_filename = f"new_file{detected_ext}" if detected_ext else "new_file.bin"
                                    print(f"[EMBED DEBUG] Detected filename: {new_filename}")
                                else:
                                    print(f"[EMBED DEBUG] Using default filename: {new_filename}")
                            
                            new_layer_info = (content_to_hide, new_filename)
                            print(f"[EMBED DEBUG] Created file layer: {new_filename}")
                    except Exception as e:
                        print(f"[EMBED ERROR] Failed to create new layer info: {e}")
                        print(f"[EMBED ERROR] content_file_path: {content_file_path}")
                        print(f"[EMBED ERROR] content_to_hide type: {type(content_to_hide)}")
                        import traceback
                        print(f"[EMBED ERROR] Traceback: {traceback.format_exc()}")
                        new_layer_info = (content_to_hide, "error_recovery.bin")
                    
                    # Add new layer to existing layers only if valid AND we have enough capacity
                    if new_layer_info is not None and existing_layers is not None:
                        # CAPACITY CHECK: For document steganography with small containers, 
                        # skip layered containers due to JSON overhead
                        carrier_size = os.path.getsize(carrier_file_path) if os.path.exists(carrier_file_path) else 0
                        is_small_container = carrier_size < 1000  # Less than 1KB
                        is_document = carrier_type == "document"
                        
                        if is_small_container and is_document:
                            print(f"[EMBED] CAPACITY OPTIMIZATION: Skipping layered container for small document ({carrier_size} bytes)")
                            print(f"[EMBED] Using direct embedding to avoid JSON overhead")
                            update_job_status(operation_id, "processing", 48, f"Using direct embedding for small document")
                        else:
                            existing_layers.append(new_layer_info)
                            update_job_status(operation_id, "processing", 48, f"Added new content as layer {len(existing_layers)}: {new_layer_info[1]}")
                            
                            # Create layered container with all layers
                            try:
                                layered_container = create_layered_data_container(existing_layers)
                                if layered_container is not None:
                                    # Replace content with layered container (as string since it's JSON)
                                    content_to_hide = layered_container
                                    # Update content type since we're now embedding JSON text, not the original file
                                    content_type = "text"
                                    original_filename = None
                                    
                                    update_job_status(operation_id, "processing", 49, f"Created layered container with {len(existing_layers)} layers")
                                    print(f"[EMBED] Successfully created layered container with {len(existing_layers)} layers")
                                else:
                                    print("[EMBED ERROR] create_layered_data_container returned None, falling back to normal embedding")
                            except Exception as e:
                                print(f"[EMBED ERROR] Failed to create layered container: {e}, falling back to normal embedding")
                    
        except Exception as e:
            # If extraction fails, it means no hidden data exists (this is normal for clean files)
            update_job_status(operation_id, "processing", 42, "No existing data found - ready for fresh embedding")
            print(f"[EMBED] ✅ No existing data detected (normal for clean files) - proceeding with fresh embedding")
            # Continue with normal embedding
            pass
        
        # Generate output filename
        carrier_filename = Path(carrier_file_path).name
        if expected_output_filename:
            output_filename = expected_output_filename
            print(f"[EMBED] Using expected output filename: {output_filename}")
        else:
            # Fallback: use clean filename generation
            output_filename = generate_clean_output_filename(carrier_filename, "stego_")
            print(f"[EMBED] Generated fallback output filename: {output_filename}")
        output_path = OUTPUT_DIR / output_filename
        
        print(f"[EMBED] Final output path: {output_path}")
        
        # Perform embedding
        # After layered container creation, content_type might have been changed to "text"
        # So we need to determine is_file and original_filename based on the current state
        is_file = content_type == "file"
        original_filename = None
        
        # Only set original_filename if we're still dealing with a file (not layered container)
        if is_file and content_file_path and Path(content_file_path).exists():
            original_filename = Path(content_file_path).name
        
        print(f"[EMBED DEBUG] Final embedding parameters:")
        print(f"  content_type: {content_type}")
        print(f"  is_file: {is_file}")
        print(f"  original_filename: {original_filename}")
        print(f"  content_file_path: {content_file_path}")
        print(f"  content_to_hide type: {type(content_to_hide)}")
        print(f"  content_to_hide size: {len(content_to_hide) if hasattr(content_to_hide, '__len__') else 'unknown'}")
        
        if carrier_type == "video":
            # Video manager returns a dict result
            try:
                print(f"[DEBUG VIDEO] About to call video manager.hide_data")
                print(f"[DEBUG VIDEO] Parameters: video_path={carrier_file_path}, output_path={str(output_path)}")
                manager_result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    password,
                    is_file,
                    original_filename
                )
                print(f"[DEBUG VIDEO] Video manager returned: {manager_result}")
                success = manager_result.get("success", False)
                # Get actual output path from result if available
                actual_output_path = manager_result.get("output_path", str(output_path))
                print(f"[DEBUG VIDEO] Expected path: {output_path}")
                print(f"[DEBUG VIDEO] Video result output_path: {manager_result.get('output_path')}")
                print(f"[DEBUG VIDEO] Actual output path: {actual_output_path}")
                print(f"[DEBUG VIDEO] File exists check: {os.path.exists(actual_output_path)}")
            except Exception as e:
                print(f"[DEBUG VIDEO] Exception in video manager: {e}")
                print(f"[DEBUG VIDEO] Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # Other managers (image, audio, document) return dict results too
            # Check if manager supports original_filename parameter and call with correct parameters
            import inspect
            sig = inspect.signature(manager.hide_data)
            
            update_job_status(operation_id, "processing", 80, "Performing steganography operation")
            
            # Wrap steganography operation with timeout in production
            try:
                if IS_PRODUCTION:
                    print(f"[EMBED] Running with production timeout: {MAX_OPERATION_TIMEOUT}s")
                    if 'original_filename' in sig.parameters:
                        manager_result = run_with_timeout(
                            manager.hide_data,
                            (carrier_file_path, content_to_hide, str(output_path)),
                            {'password': password, 'is_file': is_file, 'original_filename': original_filename},
                            MAX_OPERATION_TIMEOUT
                        )
                    else:
                        manager_result = run_with_timeout(
                            manager.hide_data,
                            (carrier_file_path, content_to_hide, str(output_path)),
                            {'password': password, 'is_file': is_file},
                            MAX_OPERATION_TIMEOUT
                        )
                else:
                    # Local development - no timeout
                    if 'original_filename' in sig.parameters:
                        manager_result = manager.hide_data(
                            carrier_file_path,
                            content_to_hide,
                            str(output_path),
                            password=password,  # Fix: pass password correctly
                            is_file=is_file,
                            original_filename=original_filename
                        )
                    else:
                        manager_result = manager.hide_data(
                            carrier_file_path,
                            content_to_hide,
                            str(output_path),
                            password=password,  # Fix: pass password correctly  
                            is_file=is_file
                        )
            except Exception as embed_error:
                if "timed out" in str(embed_error).lower():
                    raise Exception(f"Operation timed out - file may be too large or complex for current server capacity")
                else:
                    raise embed_error
            success = manager_result.get("success", False)
            # Get actual output path from result if available
            actual_output_path = manager_result.get("output_path", str(output_path))
        
        if not success:
            error_msg = manager_result.get("error", "Embedding operation failed") if isinstance(manager_result, dict) else "Embedding operation failed"
            raise Exception(error_msg)
        
        # Use actual output path instead of expected path
        if actual_output_path != str(output_path):
            output_path = Path(actual_output_path)
            output_filename = output_path.name
        
        update_job_status(operation_id, "processing", 90, "Finalizing")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        update_job_status(operation_id, "processing", 95, "Saving results")
        
        # Log completion in database with timeout protection
        if db and user_id and db_operation_id:
            try:
                message_preview = text_content[:100] if content_type == "text" else f"File: {Path(content_file_path).name if content_file_path else 'unknown'}"
                db.log_operation_complete(
                    db_operation_id,
                    success=True,
                    output_filename=output_filename,
                    file_size=os.path.getsize(output_path),
                    message_preview=message_preview,
                    processing_time=processing_time
                )
            except Exception as db_error:
                print(f"[WARNING] Database logging failed but operation completed successfully: {db_error}")
                # Don't let database errors prevent operation completion
        
        # Update job status with result
        result = {
            "output_file": str(output_path),
            "filename": output_filename,
            "file_size": os.path.getsize(output_path),
            "processing_time": processing_time,
            "carrier_type": carrier_type,
            "content_type": content_type
        }
        
        # Add format-specific warnings for video files
        if carrier_type == "video" and 'manager_result' in locals() and isinstance(manager_result, dict):
            if manager_result.get('video_format') == 'AVI':
                result["format_warning"] = "AVI format detected - audio may not play properly. Consider using MP4 format for better compatibility."
            elif manager_result.get('compatibility_warning'):
                result["format_warning"] = manager_result['compatibility_warning']
        
        update_job_status(operation_id, "completed", 100, "Embedding completed successfully", result=result)
        
        # Cleanup input files
        os.remove(carrier_file_path)
        if content_type == "file" and content_file_path and os.path.exists(content_file_path):
            os.remove(content_file_path)
            
        # Memory cleanup for production environment
        if IS_PRODUCTION:
            import gc
            gc.collect()
            print(f"[EMBED] Memory cleanup completed for operation {operation_id}")
            
    except Exception as e:
        error_msg = translate_error_message(str(e), carrier_type)
        update_job_status(operation_id, "failed", error=error_msg)
        
        # Log failure in database with timeout protection
        if db and user_id and db_operation_id:
            try:
                db.log_operation_complete(
                    db_operation_id,
                    success=False,
                    error_message=error_msg,
                    processing_time=time.time() - start_time
                )
            except Exception as db_error:
                print(f"[WARNING] Database error logging failed: {db_error}")
                # Don't let database errors mask the original error

async def process_batch_embed_operation(
    individual_operation_id: str,
    batch_operation_id: str,
    file_index: int,
    carrier_file_path: str,
    content_file_path: Optional[str],
    carrier_type: str,
    content_type: str,
    text_content: Optional[str],
    password: str,
    encryption_type: str,
    project_name: Optional[str],
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    expected_output_filename: Optional[str] = None,
    db_operation_id: Optional[str] = None
):
    """Background task to process embedding operation for one file in a batch"""
    
    import json
    start_time = time.time()
    
    try:
        print(f"[BATCH] Starting processing for file {file_index + 1} - {individual_operation_id}")
        
        # Update batch status
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "processing"
        
        # Prepare content to hide (same logic as regular embed)
        if content_type == "text":
            content_to_hide = text_content
        else:
            # Read content from file
            with open(content_file_path, "rb") as f:
                content_to_hide = f.read()
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Check if carrier already contains hidden data (same logic as regular embed)
        existing_data = None
        original_filename = None
        try:
            extraction_result = manager.extract_data(carrier_file_path)
            
            if isinstance(extraction_result, tuple):
                existing_data, original_filename = extraction_result
            else:
                existing_data = extraction_result
                original_filename = None
            
            if existing_data:
                print(f"[BATCH] Found existing data in carrier file {file_index + 1}")
                
                # Handle layered containers (same logic as regular embed)
                if isinstance(existing_data, str):
                    try:
                        layered_data = json.loads(existing_data)
                        if isinstance(layered_data, dict) and layered_data.get("type") == "layered_container":
                            existing_layers = layered_data.get("layers", [])
                            print(f"[BATCH] Found {len(existing_layers)} existing layers")
                            
                            # Add new layer
                            if content_type == "text":
                                new_layer_info = (content_to_hide, "new_message.txt")
                            else:
                                new_filename = Path(content_file_path).name if content_file_path else "new_file.bin"
                                new_layer_info = (content_to_hide, new_filename)
                            
                            existing_layers.append(new_layer_info)
                            layered_container = create_layered_data_container(existing_layers)
                            
                            if layered_container:
                                content_to_hide = layered_container
                                content_type = "text"
                                original_filename = None
                                print(f"[BATCH] Created layered container with {len(existing_layers)} layers")
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"[BATCH] No existing data detected in file {file_index + 1}: {e}")
            pass
        
        # Generate output filename
        carrier_filename = Path(carrier_file_path).name
        if expected_output_filename:
            output_filename = expected_output_filename
        else:
            output_filename = generate_unique_filename(carrier_filename, "stego_")
        output_path = OUTPUT_DIR / output_filename
        
        # Perform embedding
        is_file = content_type == "file"
        original_filename = None
        
        if is_file and content_file_path and Path(content_file_path).exists():
            original_filename = Path(content_file_path).name
        
        print(f"[BATCH] Embedding in file {file_index + 1}: {carrier_type}, is_file: {is_file}")
        
        if carrier_type == "video":
            result = manager.hide_data(
                carrier_file_path,
                content_to_hide,
                str(output_path),
                is_file,
                original_filename
            )
            success = result.get("success", False)
            actual_output_path = result.get("output_path", str(output_path))
        else:
            import inspect
            sig = inspect.signature(manager.hide_data)
            if 'original_filename' in sig.parameters:
                result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    password,  # Pass password as 4th parameter
                    is_file,
                    original_filename
                )
            else:
                result = manager.hide_data(
                    carrier_file_path,
                    content_to_hide,
                    str(output_path),
                    password,  # Pass password as 4th parameter
                    is_file
                )
            success = result.get("success", False)
            actual_output_path = result.get("output_path", str(output_path))
        
        if not success:
            error_msg = result.get("error", "Embedding operation failed") if isinstance(result, dict) else "Embedding operation failed"
            raise Exception(error_msg)
        
        # Use actual output path
        if actual_output_path != str(output_path):
            output_path = Path(actual_output_path)
            output_filename = output_path.name
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log completion in database
        if db and user_id and db_operation_id:
            message_preview = text_content[:100] if content_type == "text" else f"File: {Path(content_file_path).name if content_file_path else 'unknown'}"
            db.log_operation_complete(
                db_operation_id,
                success=True,
                output_filename=output_filename,
                file_size=os.path.getsize(output_path),
                message_preview=message_preview,
                processing_time=processing_time
            )
        
        # Update batch tracking
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["completed_files"] += 1
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "completed"
            active_jobs[batch_operation_id]["individual_operations"][file_index]["output_file"] = str(output_path)
            active_jobs[batch_operation_id]["individual_operations"][file_index]["processing_time"] = processing_time
            active_jobs[batch_operation_id]["output_files"].append({
                "original_filename": Path(carrier_file_path).name,
                "output_filename": output_filename,
                "output_path": str(output_path),
                "file_size": os.path.getsize(output_path),
                "carrier_type": carrier_type
            })
            
            # Check if batch is complete
            total_files = active_jobs[batch_operation_id]["total_files"]
            completed_files = active_jobs[batch_operation_id]["completed_files"]
            failed_files = active_jobs[batch_operation_id]["failed_files"]
            
            if completed_files + failed_files >= total_files:
                if failed_files == 0:
                    active_jobs[batch_operation_id]["status"] = "completed"
                else:
                    active_jobs[batch_operation_id]["status"] = "completed_with_errors"
                
                print(f"[BATCH] Batch {batch_operation_id} completed: {completed_files} success, {failed_files} failed")
        
        # Cleanup input files for this operation
        os.remove(carrier_file_path)
        if content_type == "file" and content_file_path and os.path.exists(content_file_path):
            os.remove(content_file_path)
            
        print(f"[BATCH] Successfully completed file {file_index + 1}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"[BATCH ERROR] Failed to process file {file_index + 1}: {error_msg}")
        
        # Log failure in database
        if db and user_id and db_operation_id:
            db.log_operation_complete(
                db_operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )
        
        # Update batch tracking
        if batch_operation_id in active_jobs:
            active_jobs[batch_operation_id]["failed_files"] += 1
            active_jobs[batch_operation_id]["individual_operations"][file_index]["status"] = "failed"
            active_jobs[batch_operation_id]["individual_operations"][file_index]["error"] = error_msg
            
            # Check if batch is complete
            total_files = active_jobs[batch_operation_id]["total_files"]
            completed_files = active_jobs[batch_operation_id]["completed_files"]
            failed_files = active_jobs[batch_operation_id]["failed_files"]
            
            if completed_files + failed_files >= total_files:
                if failed_files == total_files:
                    active_jobs[batch_operation_id]["status"] = "failed"
                else:
                    active_jobs[batch_operation_id]["status"] = "completed_with_errors"

async def process_forensic_embed_operation(
    operation_id: str,
    carrier_file_path: str,
    content_file_path: str,
    carrier_type: str,
    forensic_text: str,
    password: str,
    encryption_type: str,
    metadata: dict,
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    expected_output_filename: str,
    db_operation_id: Optional[str] = None
):
    """Background task to process forensic embedding operation"""
    
    import json
    start_time = time.time()
    
    try:
        update_job_status(operation_id, "processing", 30, "Preparing forensic content")
        
        # Read the file to hide
        with open(content_file_path, "rb") as f:
            file_content = f.read()
        
        print(f"[FORENSIC EMBED DEBUG] Original file size: {len(file_content)} bytes")
        print(f"[FORENSIC EMBED DEBUG] Original file first 20 bytes: {file_content[:20]}")
        
        # Create forensic container with both file and metadata
        file_data_b64 = base64.b64encode(file_content).decode('utf-8')
        print(f"[FORENSIC EMBED DEBUG] Base64 encoded length: {len(file_data_b64)}")
        print(f"[FORENSIC EMBED DEBUG] Base64 first 100 chars: {file_data_b64[:100]}")
        
        forensic_container = {
            "type": "forensic_evidence",
            "metadata": metadata,
            "file_data": file_data_b64,
            "original_filename": metadata.get('name', os.path.basename(content_file_path)),
            "timestamp": datetime.now().isoformat(),
            "embedded_by": user_id or "unknown"
        }
        
        # Verify base64 round-trip integrity
        try:
            verification_decode = base64.b64decode(file_data_b64)
            if verification_decode == file_content:
                print(f"[FORENSIC EMBED DEBUG] ✅ Base64 round-trip verification successful")
            else:
                print(f"[FORENSIC EMBED ERROR] ❌ Base64 round-trip verification failed!")
                print(f"  Original size: {len(file_content)}, Decoded size: {len(verification_decode)}")
        except Exception as verify_error:
            print(f"[FORENSIC EMBED ERROR] Base64 verification error: {verify_error}")
        
        # Convert to JSON string to embed as text
        forensic_content = json.dumps(forensic_container, indent=2)
        
        update_job_status(operation_id, "processing", 50, "Performing forensic steganography")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Generate output path
        output_path = OUTPUT_DIR / expected_output_filename
        
        update_job_status(operation_id, "processing", 70, "Embedding forensic evidence")
        
        # Perform the embedding using text mode since we're embedding JSON
        if carrier_type == "video":
            manager_result = manager.hide_data(
                carrier_file_path,
                forensic_content,
                str(output_path),
                password,
                is_file=False,  # Embedding as text
                original_filename=f"forensic_case_{metadata.get('case_id', 'unknown')}.json"
            )
        else:
            # Check if manager supports original_filename parameter
            import inspect
            sig = inspect.signature(manager.hide_data)
            if 'original_filename' in sig.parameters:
                manager_result = manager.hide_data(
                    carrier_file_path,
                    forensic_content,
                    str(output_path),
                    password=password,
                    is_file=False,  # Embedding as text
                    original_filename=f"forensic_case_{metadata.get('case_id', 'unknown')}.json"
                )
            else:
                manager_result = manager.hide_data(
                    carrier_file_path,
                    forensic_content,
                    str(output_path),
                    password=password,
                    is_file=False  # Embedding as text
                )
        
        success = manager_result.get("success", False)
        
        if not success:
            error_msg = manager_result.get("error", "Forensic embedding failed")
            raise Exception(f"Forensic embedding failed: {error_msg}")
        
        # Check if output file exists
        if not output_path.exists():
            # Check for alternative output path from manager result
            actual_output_path = manager_result.get("output_path")
            if actual_output_path and os.path.exists(actual_output_path):
                output_path = Path(actual_output_path)
            else:
                raise Exception("Output file was not created")
        
        update_job_status(operation_id, "processing", 90, "Finalizing forensic evidence")
        
        # Update job with results including forensic metadata
        result_data = {
            "success": True,
            "output_path": str(output_path),
            "output_file": str(output_path),  # Add this field for download endpoint compatibility
            "filename": output_path.name,
            "file_size": output_path.stat().st_size,
            "forensic_metadata": metadata,
            "case_id": metadata.get('case_id'),
            "embedded_owner": metadata.get('embedded_owner'),
            "processing_time": time.time() - start_time
        }
        
        update_job_status(operation_id, "completed", 100, "Forensic evidence embedded successfully", result=result_data)
        
        # Update database
        if db and db_operation_id:
            try:
                db.update_operation_status(
                    db_operation_id,
                    "completed",
                    100,
                    output_filename=output_path.name,
                    file_size=output_path.stat().st_size
                )
                print(f"[FORENSIC] Database updated for operation {db_operation_id}")
            except Exception as db_error:
                print(f"[WARNING] Database update failed: {db_error}")
        
        print(f"[FORENSIC] Operation {operation_id} completed successfully")
        
    except Exception as e:
        print(f"[FORENSIC ERROR] Operation {operation_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_message = translate_error_message(str(e), carrier_type)
        update_job_status(operation_id, "failed", error=error_message)
        
        # Update database
        if db and db_operation_id:
            try:
                db.update_operation_status(db_operation_id, "failed", error=error_message)
            except Exception as db_error:
                print(f"[WARNING] Database update failed: {db_error}")

def detect_filename_from_content(data):
    """Detect appropriate filename and extension based on file content"""
    if not data:
        return "extracted_file.bin"
    
    # Convert to bytes if it's a string
    if isinstance(data, str):
        try:
            data_bytes = data.encode('utf-8')
        except:
            return "extracted_file.txt"
    else:
        data_bytes = data
    
    # Check for common file signatures
    if data_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return "extracted_image.png"
    elif data_bytes.startswith(b'\xFF\xD8\xFF'):
        return "extracted_image.jpg"
    elif data_bytes.startswith(b'GIF8'):
        return "extracted_image.gif"
    elif data_bytes.startswith(b'%PDF'):
        return "extracted_document.pdf"
    elif data_bytes.startswith(b'PK\x03\x04'):
        # Could be ZIP, DOCX, XLSX, etc.
        if b'word/' in data_bytes[:1024]:
            return "extracted_document.docx"
        elif b'xl/' in data_bytes[:1024]:
            return "extracted_document.xlsx"
        else:
            return "extracted_archive.zip"
    elif data_bytes.startswith(b'RIFF') and b'WAVE' in data_bytes[:20]:
        return "extracted_audio.wav"
    elif data_bytes.startswith(b'ID3') or data_bytes.startswith(b'\xFF\xFB'):
        return "extracted_audio.mp3"
    elif data_bytes.startswith(b'fLaC'):
        return "extracted_audio.flac"
    elif data_bytes.startswith(b'\x00\x00\x00\x18ftypmp4') or data_bytes.startswith(b'\x00\x00\x00\x20ftypmp4'):
        return "extracted_video.mp4"
    else:
        # Check if it looks like text content
        try:
            if isinstance(data, str):
                return "extracted_text.txt"
            else:
                decoded = data_bytes.decode('utf-8', errors='ignore')
                if all(ord(c) < 128 or c.isspace() for c in decoded[:100]):  # ASCII-like content
                    return "extracted_text.txt"
        except:
            pass
    
    return "extracted_file.bin"

async def process_forensic_extract_operation(
    operation_id: str,
    stego_file_path: str,
    carrier_type: str,
    password: str,
    output_format: str,
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    db_operation_id: Optional[str] = None
):
    """Background task to process forensic extraction operation"""
    
    import json
    start_time = time.time()
    
    try:
        update_job_status(operation_id, "processing", 30, "Starting forensic extraction")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        update_job_status(operation_id, "processing", 50, "Extracting forensic evidence")
        
        # Extract data
        print(f"[FORENSIC EXTRACT DEBUG] About to call manager.extract_data() with password")
        extraction_result = manager.extract_data(stego_file_path, password=password)
        print(f"[FORENSIC EXTRACT DEBUG] Manager returned: {type(extraction_result)}")
        
        # Handle tuple return (data, filename) from some managers
        if isinstance(extraction_result, tuple):
            extracted_data, original_filename = extraction_result
            print(f"[FORENSIC EXTRACT DEBUG] Tuple result - data: {type(extracted_data)}, filename: {original_filename}")
        else:
            extracted_data = extraction_result
            original_filename = None
            print(f"[FORENSIC EXTRACT DEBUG] Single result - data: {type(extracted_data)}")
        
        if not extracted_data:
            raise Exception("No hidden data found in the file")
        
        update_job_status(operation_id, "processing", 70, "Parsing forensic metadata")
        
        # Debug: Check what we extracted
        print(f"[FORENSIC EXTRACT DEBUG] Extracted data type: {type(extracted_data)}")
        print(f"[FORENSIC EXTRACT DEBUG] Extracted data length: {len(extracted_data) if extracted_data else 0}")
        if isinstance(extracted_data, str):
            print(f"[FORENSIC EXTRACT DEBUG] First 500 chars: {repr(extracted_data[:500])}")
            # Check if it looks like JSON
            if extracted_data.strip().startswith('{'):
                print("[FORENSIC EXTRACT DEBUG] ✅ Looks like JSON - starts with {")
            else:
                print("[FORENSIC EXTRACT DEBUG] ❌ Does not look like JSON")
        elif isinstance(extracted_data, bytes):
            try:
                decoded_preview = extracted_data.decode('utf-8', errors='replace')[:500] 
                print(f"[FORENSIC EXTRACT DEBUG] First 500 chars (decoded): {repr(decoded_preview)}")
                # Check if decoded looks like JSON
                if decoded_preview.strip().startswith('{'):
                    print("[FORENSIC EXTRACT DEBUG] ✅ Decoded looks like JSON - starts with {")
                else:
                    print("[FORENSIC EXTRACT DEBUG] ❌ Decoded does not look like JSON")
            except:
                print(f"[FORENSIC EXTRACT DEBUG] Binary data, first 100 bytes: {extracted_data[:100]}")
        
        # Try to parse as forensic evidence
        forensic_metadata = None
        extracted_file_data = None
        extracted_filename = original_filename if original_filename else "extracted_evidence"
        forensic_parsing_success = False
        
        try:
            forensic_container = None
            
            # If extracted data is text, try to parse as JSON
            if isinstance(extracted_data, str):
                print(f"[FORENSIC EXTRACT DEBUG] Trying to parse string as JSON...")
                forensic_container = json.loads(extracted_data)
                print(f"[FORENSIC EXTRACT DEBUG] JSON parsing successful")
            elif isinstance(extracted_data, bytes):
                # Try to decode as UTF-8 and parse as JSON
                try:
                    print(f"[FORENSIC EXTRACT DEBUG] Trying to decode bytes and parse as JSON...")
                    decoded_str = extracted_data.decode('utf-8')
                    forensic_container = json.loads(decoded_str)
                    print(f"[FORENSIC EXTRACT DEBUG] Bytes decode and JSON parsing successful")
                except UnicodeDecodeError as ue:
                    print(f"[FORENSIC EXTRACT DEBUG] Unicode decode error: {ue}")
                    # Not UTF-8 text, treat as binary file
                    forensic_container = None
            else:
                print(f"[FORENSIC EXTRACT DEBUG] Extracted data is neither string nor bytes")
                forensic_container = None
            
            print(f"[FORENSIC EXTRACT DEBUG] forensic_container type: {type(forensic_container)}")
            if forensic_container:
                print(f"[FORENSIC EXTRACT DEBUG] forensic_container keys: {list(forensic_container.keys()) if isinstance(forensic_container, dict) else 'not a dict'}")
                print(f"[FORENSIC EXTRACT DEBUG] container type field: {forensic_container.get('type') if isinstance(forensic_container, dict) else 'N/A'}")
            
            # Check if this is a forensic evidence container
            if forensic_container and forensic_container.get("type") == "forensic_evidence":
                forensic_metadata = forensic_container.get("metadata", {})
                file_data_b64 = forensic_container.get("file_data")
                extracted_filename = forensic_container.get("original_filename", "extracted_evidence")
                
                if file_data_b64:
                    print(f"[FORENSIC EXTRACT DEBUG] Base64 data length: {len(file_data_b64)}")
                    print(f"[FORENSIC EXTRACT DEBUG] Base64 first 100 chars: {file_data_b64[:100]}")
                    try:
                        extracted_file_data = base64.b64decode(file_data_b64)
                        forensic_parsing_success = True
                        print(f"[FORENSIC EXTRACT DEBUG] ✅ Forensic base64 decode successful!")
                        print(f"[FORENSIC EXTRACT DEBUG] Decoded binary data length: {len(extracted_file_data)}")
                        print(f"[FORENSIC EXTRACT DEBUG] Decoded first 20 bytes: {extracted_file_data[:20]}")
                    except Exception as decode_error:
                        print(f"[FORENSIC EXTRACT ERROR] Base64 decode failed: {decode_error}")
                        extracted_file_data = None
                        forensic_parsing_success = False
                else:
                    print(f"[FORENSIC EXTRACT ERROR] No file_data found in forensic container")
                    forensic_parsing_success = False
                
                print(f"[FORENSIC EXTRACT] Found forensic evidence: {forensic_metadata}")
            else:
                # Not forensic evidence, treat as regular extraction
                print(f"[FORENSIC EXTRACT] No forensic container found, treating as regular extraction")
                forensic_parsing_success = False
                
        except (json.JSONDecodeError, Exception) as parse_error:
            # Failed to parse as forensic evidence, treat as regular file
            print(f"[FORENSIC EXTRACT] Failed to parse as forensic evidence: {parse_error}")
            forensic_parsing_success = False
        
        # Handle fallback for non-forensic or failed forensic parsing
        if not forensic_parsing_success and extracted_file_data is None:
            print(f"[FORENSIC EXTRACT] Using raw extracted data as fallback")
            extracted_file_data = extracted_data
            if original_filename:
                extracted_filename = original_filename
            else:
                # Try to detect file type from content
                extracted_filename = detect_filename_from_content(extracted_data)
        
        # Final validation
        if extracted_file_data is None:
            raise Exception("No valid file data could be extracted")
            
        print(f"[FORENSIC EXTRACT] Final extracted_file_data type: {type(extracted_file_data)}")
        print(f"[FORENSIC EXTRACT] Final extracted_file_data size: {len(extracted_file_data) if extracted_file_data else 0}")
        print(f"[FORENSIC EXTRACT] Forensic parsing successful: {forensic_parsing_success}")
        
        update_job_status(operation_id, "processing", 90, "Creating forensic evidence package")
        
        # Create ZIP file containing extracted file and forensic metadata
        import zipfile
        import tempfile
        
        zip_filename = f"{operation_id}_forensic_evidence_package.zip"
        zip_path = OUTPUT_DIR / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add the extracted file to ZIP
            print(f"[FORENSIC EXTRACT DEBUG] Adding file to ZIP: {extracted_filename}")
            print(f"[FORENSIC EXTRACT DEBUG] File data type: {type(extracted_file_data)}")
            print(f"[FORENSIC EXTRACT DEBUG] File data length: {len(extracted_file_data) if extracted_file_data else 0}")
            
            if isinstance(extracted_file_data, str):
                # For text files, write as string
                print(f"[FORENSIC EXTRACT DEBUG] Writing as text to ZIP")
                zip_file.writestr(extracted_filename, extracted_file_data)
            else:
                # For binary files, write as bytes
                print(f"[FORENSIC EXTRACT DEBUG] Writing as binary to ZIP")
                print(f"[FORENSIC EXTRACT DEBUG] Binary first 20 bytes: {extracted_file_data[:20] if extracted_file_data else 'None'}")
                zip_file.writestr(extracted_filename, extracted_file_data)
            
            # Create and add forensic metadata text file
            if forensic_metadata:
                metadata_content = f"""FORENSIC EVIDENCE METADATA
================================

Case ID: {forensic_metadata.get('case_id', 'N/A')}
Embedded Owner: {forensic_metadata.get('embedded_owner', 'N/A')}
Timestamp: {forensic_metadata.get('timestamp', 'N/A')}
Description: {forensic_metadata.get('description', 'N/A')}

File Details:
- Original Filename: {forensic_metadata.get('name', extracted_filename)}
- File Size: {forensic_metadata.get('file_size', 'Unknown')} bytes
- File Type: {forensic_metadata.get('file_type', 'Unknown')}
- Carrier File: {forensic_metadata.get('carrier_name', 'Unknown')}

Processing Details:
- Extracted At: {datetime.now().isoformat()}
- Operation ID: {operation_id}
- Created By: {forensic_metadata.get('created_by', 'Unknown')}

================================
This file contains forensic evidence extracted from steganographic carrier media.
Handle according to your organization's evidence management procedures.
"""
                zip_file.writestr("forensic_metadata.txt", metadata_content)
            else:
                # Even for non-forensic extractions, add basic metadata
                basic_metadata = f"""EXTRACTION METADATA
===================

Extracted File: {extracted_filename}
Extraction Time: {datetime.now().isoformat()}
Operation ID: {operation_id}
Source: Standard steganographic extraction

Note: No forensic metadata was embedded with this file.
This appears to be a standard hidden file without forensic context.
"""
                zip_file.writestr("extraction_info.txt", basic_metadata)
        
        # Update paths to point to ZIP file
        output_path = zip_path
        
        # Prepare result data
        result_data = {
            "success": True,
            "output_path": str(output_path),
            "output_file": str(output_path),  # Add output_file for download compatibility
            "filename": output_path.name,
            "file_size": output_path.stat().st_size,
            "extracted_content": extracted_filename,
            "processing_time": time.time() - start_time
        }
        
        # Add forensic metadata to result if found
        if forensic_metadata:
            result_data["forensic_metadata"] = forensic_metadata
            result_data["is_forensic_evidence"] = True
        else:
            result_data["is_forensic_evidence"] = False
        
        update_job_status(operation_id, "completed", 100, "Forensic extraction completed successfully", result=result_data)
        
        # Update database
        if db and db_operation_id:
            try:
                db.update_operation_status(
                    db_operation_id,
                    "completed",
                    100,
                    output_filename=output_path.name,
                    file_size=output_path.stat().st_size
                )
                print(f"[FORENSIC EXTRACT] Database updated for operation {db_operation_id}")
            except Exception as db_error:
                print(f"[WARNING] Database update failed: {db_error}")
        
        print(f"[FORENSIC EXTRACT] Operation {operation_id} completed successfully")
        
    except Exception as e:
        print(f"[FORENSIC EXTRACT ERROR] Operation {operation_id} failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        error_message = translate_error_message(str(e), carrier_type)
        update_job_status(operation_id, "failed", error=error_message)
        
        # Update database
        if db and db_operation_id:
            try:
                db.update_operation_status(db_operation_id, "failed", error=error_message)
            except Exception as db_error:
                print(f"[WARNING] Database update failed: {db_error}")

async def process_extract_operation(
    operation_id: str,
    stego_file_path: str,
    carrier_type: str,
    password: str,
    output_format: str,
    user_id: Optional[str],
    db: Optional[SteganographyDatabase],
    db_operation_id: Optional[str] = None
):
    """Background task to process extraction operation"""
    
    start_time = time.time()
    
    try:
        update_job_status(operation_id, "processing", 50, "Extracting hidden data")
        
        # Get appropriate steganography manager
        manager = get_steganography_manager(carrier_type, password)
        if not manager:
            raise Exception(f"No manager available for {carrier_type}")
        
        # Extract data
        print(f"[DEBUG EXTRACT] About to call manager.extract_data for {carrier_type}")
        print(f"[DEBUG EXTRACT] Password received: {repr(password)}")
        if hasattr(manager, 'safe_stego') and hasattr(manager.safe_stego, 'password'):
            print(f"[DEBUG EXTRACT] Manager password set to: {repr(manager.safe_stego.password)}")
        
        # Call extract_data with password parameter (now supports multi-layer)
        try:
            extraction_result = manager.extract_data(stego_file_path, password=password, output_dir=str(OUTPUT_DIR))
        except TypeError:
            # Fallback for managers that don't accept output_dir parameter
            try:
                extraction_result = manager.extract_data(stego_file_path, password=password)
            except TypeError:
                # Ultimate fallback for old managers
                extraction_result = manager.extract_data(stego_file_path)
        
        # DEBUG: Log extraction result details
        print(f"[DEBUG EXTRACT] extraction_result type: {type(extraction_result)}")
        print(f"[DEBUG EXTRACT] extraction_result: {repr(extraction_result)[:500]}")
        
        if extraction_result is None:
            raise Exception("Extraction failed - wrong password or no hidden data")
        
        update_job_status(operation_id, "processing", 70, "Processing extraction results")
        
        # Handle new multi-layer response format
        if isinstance(extraction_result, dict):
            # Multi-layer steganography response
            if extraction_result.get('multi_layer_extraction', False):
                print(f"[MULTI-LAYER] Detected multi-layer extraction: {extraction_result.get('total_layers_extracted', 0)} layers")
                
                # The zip file is already created by the multi-layer module
                zip_path = extraction_result.get('zip_file')
                if zip_path and os.path.exists(zip_path):
                    zip_filename = os.path.basename(zip_path)
                    
                    # Move zip file to output directory if it's not already there
                    final_zip_path = OUTPUT_DIR / zip_filename
                    if zip_path != str(final_zip_path):
                        import shutil
                        shutil.move(zip_path, final_zip_path)
                    
                    output_files = [str(final_zip_path)]
                    
                    # Create proper result format for multi-layer extraction
                    processing_time = time.time() - start_time
                    
                    result = {
                        "output_file": str(final_zip_path),
                        "filename": zip_filename,
                        "extracted_filename": zip_filename,  # Frontend expects this field
                        "file_size": os.path.getsize(final_zip_path),
                        "processing_time": processing_time,
                        "content_type": "application/zip",  # Frontend expects this field
                        "data_type": "zip",
                        "preview": f"Multi-layer ZIP containing {extraction_result.get('total_layers_extracted', 0)} layers",
                        "text_content": extraction_result.get('extracted_data', ''),  # Frontend expects this field
                        "original_filename": zip_filename,
                        "download_url": f"/api/operations/{operation_id}/download",  # Frontend expects this field
                        # Multi-layer specific fields
                        "is_multi_layer": True,
                        "multi_layer_extraction": True,
                        "total_layers_extracted": extraction_result.get('total_layers_extracted', 0),
                        "layer_details": extraction_result.get('layer_details', [])
                    }
                    
                    update_job_status(
                        operation_id,
                        "completed",
                        100,
                        f"Multi-layer extraction completed: {extraction_result.get('total_layers_extracted', 0)} layers extracted",
                        result=result
                    )
                    
                    return
                else:
                    raise Exception("Multi-layer extraction failed - zip file not created")
            
            elif extraction_result.get('single_extraction', False):
                # Single layer from multi-layer capable module
                print(f"[MULTI-LAYER] Single layer extraction from multi-layer file")
                extracted_data = extraction_result.get('extracted_data', '')
                # Detect proper filename from content if not provided
                original_filename = extraction_result.get('filename')
                if not original_filename:
                    original_filename = detect_filename_from_content(extracted_data)
                output_path = extraction_result.get('saved_to')
                
                if output_path and os.path.exists(output_path):
                    final_output_path = output_path
                else:
                    # Fallback: save the extracted data
                    safe_filename = sanitize_filename(original_filename)
                    final_output_path = OUTPUT_DIR / safe_filename
                    
                    if isinstance(extracted_data, str):
                        with open(final_output_path, 'w', encoding='utf-8') as f:
                            f.write(extracted_data)
                    else:
                        with open(final_output_path, 'wb') as f:
                            f.write(extracted_data)
                
                # Create proper result format for single extraction
                processing_time = time.time() - start_time
                
                # Determine content type and preview
                if isinstance(extracted_data, str):
                    preview = extracted_data[:200]
                    data_type = "text"
                    text_content = extracted_data
                else:
                    preview = f"Binary file ({len(extracted_data)} bytes)"
                    data_type = "binary"
                    text_content = None
                
                result = {
                    "output_file": str(final_output_path),
                    "filename": os.path.basename(final_output_path),
                    "extracted_filename": original_filename,  # Frontend expects this field
                    "file_size": os.path.getsize(final_output_path),
                    "processing_time": processing_time,
                    "content_type": data_type,  # Frontend expects this field
                    "data_type": data_type,
                    "preview": preview,
                    "text_content": text_content,  # Frontend expects this field
                    "original_filename": original_filename,
                    "download_url": f"/api/operations/{operation_id}/download"  # Frontend expects this field
                }
                
                update_job_status(
                    operation_id,
                    "completed",
                    100,
                    "Single layer extraction completed successfully",
                    result=result
                )
                
                # Cleanup input file
                if os.path.exists(stego_file_path):
                    os.remove(stego_file_path)
                
                return
            
            elif extraction_result.get('success', False):
                # Legacy dict format - should not normally happen with new multi-layer system
                extracted_data = extraction_result.get('extracted_data', '')
                # Detect proper filename from content if not provided
                original_filename = extraction_result.get('filename')
                if not original_filename:
                    original_filename = detect_filename_from_content(extracted_data) 
                output_path = extraction_result.get('saved_to')
                
                if output_path and os.path.exists(output_path):
                    final_output_path = output_path
                else:
                    # Fallback: save the extracted data
                    if not original_filename:
                        original_filename = detect_filename_from_content(extracted_data)
                    safe_filename = sanitize_filename(original_filename)
                    final_output_path = OUTPUT_DIR / safe_filename
                    
                    with open(final_output_path, 'w', encoding='utf-8') as f:
                        f.write(str(extracted_data))
                
                # Create proper result format for legacy extraction
                processing_time = time.time() - start_time
                
                result = {
                    "output_file": str(final_output_path),
                    "filename": os.path.basename(final_output_path),
                    "extracted_filename": original_filename,  # Frontend expects this field
                    "file_size": os.path.getsize(final_output_path),
                    "processing_time": processing_time,
                    "content_type": "text",  # Frontend expects this field
                    "data_type": "text",
                    "preview": str(extracted_data)[:200],
                    "text_content": str(extracted_data),  # Frontend expects this field
                    "original_filename": original_filename,
                    "download_url": f"/api/operations/{operation_id}/download"  # Frontend expects this field
                }
                
                update_job_status(
                    operation_id,
                    "completed", 
                    100,
                    "Legacy extraction completed successfully",
                    result=result
                )
                
                # Cleanup input file
                if os.path.exists(stego_file_path):
                    os.remove(stego_file_path)
                
                return
            
            else:
                raise Exception("Extraction failed - invalid response format")
        
        # Handle tuple return (data, filename) from legacy managers
        elif isinstance(extraction_result, tuple):
            extracted_data, original_filename = extraction_result
            print(f"[DEBUG EXTRACT] Tuple unpacked - data type: {type(extracted_data)}, filename: {original_filename}")
            
            # Detect proper filename from content if not provided or generic
            if not original_filename or original_filename in ['extracted_data.txt', 'extracted_data.bin']:
                original_filename = detect_filename_from_content(extracted_data)
            
            # Save extracted data to file
            safe_filename = sanitize_filename(original_filename)
            output_path = OUTPUT_DIR / safe_filename
            
            if isinstance(extracted_data, str):
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_data)
                text_content = extracted_data
                preview = extracted_data[:200]
                data_type = "text"
            elif isinstance(extracted_data, bytes):
                with open(output_path, 'wb') as f:
                    f.write(extracted_data)
                if _is_likely_text_content(extracted_data):
                    try:
                        text_content = extracted_data.decode('utf-8')
                        preview = text_content[:200]
                        data_type = "text"
                    except UnicodeDecodeError:
                        text_content = None
                        preview = f"Binary file ({len(extracted_data)} bytes)"
                        data_type = "binary"
                else:
                    text_content = None
                    preview = f"Binary file ({len(extracted_data)} bytes)"
                    data_type = "binary"
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(extracted_data))
                text_content = str(extracted_data)
                preview = text_content[:200]
                data_type = "text"
            
            # Create proper result format for tuple extraction
            processing_time = time.time() - start_time
            
            result = {
                "output_file": str(output_path),
                "filename": os.path.basename(output_path),
                "extracted_filename": original_filename,  # Frontend expects this field
                "file_size": os.path.getsize(output_path),
                "processing_time": processing_time,
                "content_type": data_type,  # Frontend expects this field
                "data_type": data_type,
                "preview": preview,
                "text_content": text_content,  # Frontend expects this field
                "original_filename": original_filename,
                "download_url": f"/api/operations/{operation_id}/download"  # Frontend expects this field
            }
            
            update_job_status(
                operation_id,
                "completed",
                100,
                "Tuple extraction completed successfully", 
                result=result
            )
            
            # Cleanup input file
            if os.path.exists(stego_file_path):
                os.remove(stego_file_path)
                
            return
        
        # Handle direct data return
        else:
            extracted_data = extraction_result
            # Detect proper filename from content instead of defaulting to txt
            original_filename = detect_filename_from_content(extracted_data)
            print(f"[DEBUG EXTRACT] Direct result - data type: {type(extracted_data)}, detected filename: {original_filename}")
            
            # Save extracted data to file
            safe_filename = sanitize_filename(original_filename)
            output_path = OUTPUT_DIR / safe_filename
            
            if isinstance(extracted_data, str):
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_data)
                text_content = extracted_data
                preview = extracted_data[:200]
                data_type = "text"
            elif isinstance(extracted_data, bytes):
                with open(output_path, 'wb') as f:
                    f.write(extracted_data)
                if _is_likely_text_content(extracted_data):
                    try:
                        text_content = extracted_data.decode('utf-8')
                        preview = text_content[:200]
                        data_type = "text"
                    except UnicodeDecodeError:
                        text_content = None
                        preview = f"Binary file ({len(extracted_data)} bytes)"
                        data_type = "binary"
                else:
                    text_content = None
                    preview = f"Binary file ({len(extracted_data)} bytes)"
                    data_type = "binary"
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(extracted_data))
                text_content = str(extracted_data)
                preview = text_content[:200]
                data_type = "text"
            
            # Create proper result format for direct extraction
            processing_time = time.time() - start_time
            
            result = {
                "output_file": str(output_path),
                "filename": os.path.basename(output_path),
                "extracted_filename": original_filename,  # Frontend expects this field
                "file_size": os.path.getsize(output_path),
                "processing_time": processing_time,
                "content_type": data_type,  # Frontend expects this field
                "data_type": data_type,
                "preview": preview,
                "text_content": text_content,  # Frontend expects this field
                "original_filename": original_filename,
                "download_url": f"/api/operations/{operation_id}/download"  # Frontend expects this field
            }
            
            update_job_status(
                operation_id,
                "completed",
                100,
                "Direct extraction completed successfully",
                result=result
            )
            
            # Cleanup input file
            if os.path.exists(stego_file_path):
                os.remove(stego_file_path)
                
            return
        
        # This line should never be reached since all extraction paths return early
        raise Exception("Unexpected code path reached in extraction processing")
        
    except Exception as e:
        error_msg = translate_error_message(str(e), carrier_type)
        update_job_status(operation_id, "failed", error=error_msg)
        
        # Log failure in database
        if db and user_id and db_operation_id:
            db.log_operation_complete(
                db_operation_id,
                success=False,
                error_message=error_msg,
                processing_time=time.time() - start_time
            )

def get_steganography_manager(carrier_type: str, password: str = ""):
    """Get appropriate steganography manager based on carrier type"""
    manager_class = steganography_managers.get(carrier_type)
    if manager_class:
        # Different managers have different constructor signatures
        if carrier_type in ['image', 'document']:
            # UniversalFileSteganography doesn't take password in constructor
            return manager_class()
        elif carrier_type == 'audio':
            # UniversalFileAudio may take password in constructor
            try:
                return manager_class(password=password)
            except TypeError:
                return manager_class()
        elif carrier_type == 'video':
            # FinalVideoSteganographyManager doesn't take password in constructor
            return manager_class()
        else:
            # Fallback - try with password first, then without
            try:
                return manager_class(password=password)
            except TypeError:
                return manager_class()
    return None

# ============================================================================
# DIRECT FILE DOWNLOAD ENDPOINT
# ============================================================================

@app.get("/api/download/{filename}")
async def download_file_by_name(filename: str):
    """Download a file by filename from outputs directory"""
    
    # Security check - prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Check outputs directory first
    output_file = OUTPUT_DIR / filename
    if not output_file.exists():
        # Fallback to uploads directory (for testing)
        output_file = UPLOAD_DIR / filename
        if not output_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    file_ext = Path(filename).suffix.lower()
    media_type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg', 
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.aac': 'audio/aac',
        '.m4a': 'audio/mp4',
        '.pdf': 'application/pdf',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.rtf': 'application/rtf',
        '.doc': 'application/msword'
    }
    
    media_type = media_type_map.get(file_ext, 'application/octet-stream')
    
    # Debug: Log file info
    print(f"[DOWNLOAD] File: {filename}")
    print(f"[DOWNLOAD] Extension: {file_ext}")
    print(f"[DOWNLOAD] Media Type: {media_type}")
    print(f"[DOWNLOAD] File Size: {output_file.stat().st_size} bytes")
    
    # Create FileResponse with proper headers for download
    response = FileResponse(
        path=str(output_file),
        filename=filename,
        media_type=media_type
    )
    
    # Ensure Content-Disposition header is set properly for proper downloading
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    
    # Add additional headers to ensure proper file handling
    response.headers["Content-Type"] = media_type
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check(db: Optional[SteganographyDatabase] = Depends(get_db)):
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "active_jobs": len(active_jobs),
        "available_managers": {
            "image": steganography_managers['image'] is not None,
            "video": steganography_managers['video'] is not None,
            "audio": steganography_managers['audio'] is not None,
            "document": steganography_managers['document'] is not None
        },
        "database_available": database_available
    }
    
    if db:
        db_health = db.health_check()
        health_data["database"] = db_health
    else:
        health_data["database"] = {"status": "not_configured"}
    
    return health_data

@app.get("/api/status")
async def simple_status():
    """Simple status endpoint without database dependencies"""
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/operations")
async def list_operations(limit: int = 100):
    """List recent operations"""
    operations = []
    for op_id, job in list(active_jobs.items())[-limit:]:
        operations.append({
            "operation_id": op_id,
            "status": job["status"],
            "progress": job.get("progress"),
            "created_at": job["created_at"],
            "carrier_type": job.get("carrier_type"),
            "content_type": job.get("content_type"),
            "operation_type": job.get("operation_type", "hide")
        })
    
    return {"operations": operations}

# @app.get("/forensic-evidence")
# async def serve_forensic_evidence():
#     """Serve the forensic evidence page"""
#     return FileResponse("templates/index.html")
# NOTE: Commented out for Vercel deployment - frontend handles all UI routing

# ============================================================================
# CLEANUP AND MAINTENANCE
# ============================================================================

# @app.on_event("startup")
# async def startup_event():
#     """Application startup tasks"""
#     print("🚀 Enhanced Steganography API starting up...")
    
#     # Clean up old files
#     cleanup_old_files(UPLOAD_DIR, 2)  # 2 hours for uploads
#     cleanup_old_files(OUTPUT_DIR, 24)  # 24 hours for outputs
    
#     print("✅ Startup complete!")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """Application shutdown tasks"""
#     print("🛑 Enhanced Steganography API shutting down...")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

# Local development server - runs when executed directly
# In Vercel, this is imported as a module so __name__ != "__main__"
if __name__ == "__main__":
    try:
        # Import uvicorn for local development
        # import uvicorn  # Already imported at top (commented out)
        import uvicorn
        
        print("🚀 Starting VeilForge backend server...")
        print("📍 Backend API: http://localhost:8000")
        print("📍 Frontend URL: http://localhost:8080")
        print("📍 API Documentation: http://localhost:8000/docs")
        print("🔄 Press Ctrl+C to stop the server")
        
        # Import config for server settings
        try:
            from .config import HOST, PORT, DEBUG
        except ImportError:
            from config import HOST, PORT, DEBUG
        
        uvicorn.run(
            "app:app",  # Updated to use app.py instead of enhanced_app.py
            host=HOST,
            port=PORT,
            reload=DEBUG,  # Enable reload only in debug mode
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not available - install with: pip install uvicorn[standard]")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")