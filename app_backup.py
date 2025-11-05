"""
FastAPI Web Application for Steganography Operations
Provides a web interface for the advanced steganography functions.
"""

import os
import tempfile
import uuid
import time
import secrets
import string
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import shutil

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our steganography modules
try:
    from final_video_steganography import FinalVideoSteganographyManager
except ImportError:
    FinalVideoSteganographyManager = None

try:
    from enhanced_web_video_stego import EnhancedWebVideoSteganographyManager
except ImportError:
    EnhancedWebVideoSteganographyManager = None

try:
    from enhanced_web_image_stego import EnhancedWebImageSteganographyManager
except ImportError:
    EnhancedWebImageSteganographyManager = None

try:
    from enhanced_web_document_stego import EnhancedWebDocumentSteganographyManager
except ImportError:
    EnhancedWebDocumentSteganographyManager = None

try:
    from video_steganography import VideoSteganographyManager
except ImportError:
    VideoSteganographyManager = None

try:
    from universal_file_audio import UniversalFileAudio
except ImportError:
    UniversalFileAudio = None

try:
    from universal_file_steganography import UniversalFileSteganography
except ImportError:
    UniversalFileSteganography = None

try:
    from universal_text_audio_stego import UniversalTextAudioSteganographyManager
except ImportError:
    UniversalTextAudioSteganographyManager = None

try:
    from enhanced_web_audio_stego import EnhancedWebAudioSteganographyManager
except ImportError:
    EnhancedWebAudioSteganographyManager = None

try:
    from reliable_audio_stego import ReliableAudioSteganographyManager
except ImportError:
    ReliableAudioSteganographyManager = None

try:
    from simple_text_audio_stego import SimpleTextAudioSteganographyManager
except ImportError:
    SimpleTextAudioSteganographyManager = None

try:
    from working_audio_stego import WorkingAudioSteganographyManager
except ImportError:
    WorkingAudioSteganographyManager = None

try:
    from final_audio_stego import FinalAudioSteganographyManager
except ImportError:
    FinalAudioSteganographyManager = None

try:
    from simple_audio_stego import SimpleAudioSteganographyManager
except ImportError:
    SimpleAudioSteganographyManager = None

# Import file naming utilities
try:
    from file_naming_utils import (
        create_output_filename, 
        create_extracted_filename, 
        sanitize_filename,
        get_file_type_from_extension,
        create_job_based_filename
    )
except ImportError:
    # Fallback functions if file naming utils are not available
    def create_output_filename(container_filename, operation="hidden", method=""):
        return f"{Path(container_filename).stem}_stego{Path(container_filename).suffix}"
    
    def create_extracted_filename(original_filename, data_type="file", file_extension=None):
        return original_filename or "extracted_content.txt"
    
    def sanitize_filename(filename):
        return filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    def get_file_type_from_extension(filename):
        return "other"
    
    def create_job_based_filename(job_id, base_filename, operation):
        return f"{job_id}_{operation}_{base_filename}"

# Create dummy classes for missing modules to prevent import errors
class DummySteganographyManager:
    def __init__(self, *args, **kwargs):
        pass
    def hide_data(self, *args, **kwargs):
        raise NotImplementedError("This steganography method is not available")
    def extract_data(self, *args, **kwargs):
        raise NotImplementedError("This steganography method is not available")

# Assign dummy classes for missing modules
SteganographyManager = DummySteganographyManager
ContainerAnalyzer = DummySteganographyManager  
SteganographyManagerEnhanced = DummySteganographyManager
SimpleSteganographyManager = DummySteganographyManager
FastVideoSteganographyManager = DummySteganographyManager

# Use enhanced image steganography if available
if EnhancedWebImageSteganographyManager is not None:
    SimpleSteganographyManager = EnhancedWebImageSteganographyManager
    print("✅ Using EnhancedWebImageSteganographyManager - supports both text and file content!")

# Use enhanced document steganography if available
if EnhancedWebDocumentSteganographyManager is not None:
    SteganographyManagerEnhanced = EnhancedWebDocumentSteganographyManager
    print("✅ Using EnhancedWebDocumentSteganographyManager - supports both text and file content!")

# Use real video steganography if available - prioritize EnhancedWebVideoSteganographyManager
if EnhancedWebVideoSteganographyManager is not None:
    RobustVideoSteganographyManager = EnhancedWebVideoSteganographyManager
    print("✅ Using EnhancedWebVideoSteganographyManager - supports both text and file content!")
else:
    try:
        from final_web_video_text_stego import FinalWebVideoTextSteganographyManager
        RobustVideoSteganographyManager = FinalWebVideoTextSteganographyManager
        print("✅ Using FinalWebVideoTextSteganographyManager (text only)")
    except ImportError:
        try:
            from reliable_web_video_text_stego import ReliableWebVideoTextSteganographyManager
            RobustVideoSteganographyManager = ReliableWebVideoTextSteganographyManager
            print("✅ Using ReliableWebVideoTextSteganographyManager")
        except ImportError:
            try:
                from robust_web_video_text_stego import RobustWebVideoTextSteganographyManager
                RobustVideoSteganographyManager = RobustWebVideoTextSteganographyManager
                print("✅ Using RobustWebVideoTextSteganographyManager")
            except ImportError:
                try:
                    from working_video_text_stego import WorkingVideoTextSteganographyManager
                    RobustVideoSteganographyManager = WorkingVideoTextSteganographyManager
                    print("✅ Using WorkingVideoTextSteganographyManager")
                except ImportError:
                    try:
                        from web_video_text_stego import WebVideoTextSteganographyManager
                        RobustVideoSteganographyManager = WebVideoTextSteganographyManager
                        print("✅ Using WebVideoTextSteganographyManager")
                    except ImportError:
                        if VideoSteganographyManager is not None:
                            RobustVideoSteganographyManager = VideoSteganographyManager
                            print("✅ Using VideoSteganographyManager")
                        elif FinalVideoSteganographyManager is not None:
                            RobustVideoSteganographyManager = FinalVideoSteganographyManager
                            print("✅ Using FinalVideoSteganographyManager")
                        else:
                            RobustVideoSteganographyManager = DummySteganographyManager
                            print("⚠️ Using DummySteganographyManager - no video steganography available")

# Use real classes for audio if available, otherwise use dummy - prioritize EnhancedWebAudioSteganographyManager
if EnhancedWebAudioSteganographyManager is not None:
    UniversalTextAudioSteganographyManager = EnhancedWebAudioSteganographyManager
    print("✅ Using EnhancedWebAudioSteganographyManager - supports both text and file content!")
elif UniversalTextAudioSteganographyManager is None:
    UniversalTextAudioSteganographyManager = DummySteganographyManager
if ReliableAudioSteganographyManager is None:
    ReliableAudioSteganographyManager = DummySteganographyManager
if SimpleTextAudioSteganographyManager is None:
    SimpleTextAudioSteganographyManager = DummySteganographyManager
if SimpleAudioSteganographyManager is None:
    SimpleAudioSteganographyManager = DummySteganographyManager
if WorkingAudioSteganographyManager is None:
    WorkingAudioSteganographyManager = DummySteganographyManager
if FinalAudioSteganographyManager is None:
    FinalAudioSteganographyManager = DummySteganographyManager

# Utility functions for user-friendly file naming
def generate_user_friendly_name(operation_type: str, container_name: str, payload_name: str = None) -> str:
    """
    Generate user-friendly download filenames based on operation type and original filenames.
    
    Args:
        operation_type: "hide" or "extract"
        container_name: Original name of the carrier/container file
        payload_name: Original name of the payload file (for extract operations)
    
    Returns:
        User-friendly filename for download
    """
    if operation_type == "hide":
        # For hide operations: use container name with suffix
        container_stem = Path(container_name).stem
        container_ext = Path(container_name).suffix
        return f"{container_stem}_with_hidden_data{container_ext}"
    
    elif operation_type == "extract":
        # For extract operations: prefer original payload name if available
        if payload_name and payload_name != "unknown":
            return payload_name
        else:
            # Fallback to generic name if original payload name unknown
            return "extracted_file"
    
    # Fallback
    return container_name

# Configuration
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
TEMP_DIR = Path("temp")

# Create directories if they don't exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    directory.mkdir(exist_ok=True)

# Initialize FastAPI
app = FastAPI(
    title="VeilForge - Advanced Steganography Web Interface",
    description="Hide and extract data in images, audio, video, and documents",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.1.6:8080",
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://192.168.1.6:8081"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models for API
class HideRequest(BaseModel):
    password: str
    data: Optional[str] = None
    is_enhanced: bool = False

class ExtractRequest(BaseModel):
    password: str
    is_enhanced: bool = False

class AnalyzeRequest(BaseModel):
    pass

class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    result: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    error: Optional[str] = None
    # New fields for better download naming
    operation_type: Optional[str] = None  # "hide" or "extract"
    original_container_name: Optional[str] = None  # Name of carrier file
    original_payload_name: Optional[str] = None  # Name of hidden file (for extract operations)
    user_friendly_name: Optional[str] = None  # Computed user-friendly download name

# In-memory job storage (in production, use Redis or database)
jobs: Dict[str, JobStatus] = {}

def cleanup_old_files():
    """Clean up old temporary files"""
    try:
        for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    # Remove files older than 1 hour
                    if (file_path.stat().st_mtime < (time.time() - 3600)):
                        file_path.unlink()
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.get("/")
async def index(request: Request):
    """Main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats"""
    return {
        "image": ["png", "jpg", "jpeg", "bmp"],
        "audio": ["wav", "mp3", "flac"],
        "video": ["mp4", "avi", "mov", "mkv"],
        "document": ["pdf", "docx", "xml"],
        "text": ["txt", "py", "js", "html", "css", "json"]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for frontend"""
    available_managers = []
    
    # Check if manager classes are available (not None and not DummySteganographyManager)
    if EnhancedWebImageSteganographyManager is not None and EnhancedWebImageSteganographyManager != DummySteganographyManager:
        available_managers.append("image")
    if SteganographyManagerEnhanced is not None and SteganographyManagerEnhanced != DummySteganographyManager:
        available_managers.append("document") 
    if RobustVideoSteganographyManager is not None and RobustVideoSteganographyManager != DummySteganographyManager:
        available_managers.append("video")
    if UniversalTextAudioSteganographyManager is not None and UniversalTextAudioSteganographyManager != DummySteganographyManager:
        available_managers.append("audio")
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "available_managers": available_managers
    }

def generate_strong_password(length: int = 16) -> str:
    """Generate a strong, cryptographically secure password"""
    # Use a mix of uppercase, lowercase, digits, and special characters
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure at least one character from each category
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase), 
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    
    # Fill the rest with random characters
    for _ in range(length - 4):
        password.append(secrets.choice(characters))
    
    # Shuffle the password to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

@app.get("/api/generate-password")
async def generate_password():
    """Generate a strong password for steganography"""
    try:
        password = generate_strong_password(16)
        return {
            "success": True,
            "password": password,
            "length": len(password),
            "strength": "Strong",
            "message": "Auto-generated secure password. Please copy and save this password for extraction."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate password: {str(e)}"
        }

@app.post("/api/analyze")
async def analyze_container(
    file: UploadFile = File(...),
    request_data: str = Form(...)
):
    """Analyze container file capacity"""
    try:
        request_obj = AnalyzeRequest.parse_raw(request_data)
        
        # Save uploaded file
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Analyze capacity using enhanced manager
        manager = SteganographyManagerEnhanced("dummy_password")
        analysis_result = manager.analyze_capacity(str(file_path))
        
        # Clean up
        file_path.unlink()
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size": len(content),
            "container_type": analysis_result.get("container_type", "unknown"),
            "estimated_capacity": analysis_result.get("estimated_capacity", 0),
            "safe_capacity": analysis_result.get("safe_capacity", 0),
            "recommendations": analysis_result.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")

@app.post("/api/hide")
async def hide_data(
    background_tasks: BackgroundTasks,
    container_file: UploadFile = File(...),
    secret_file: Optional[UploadFile] = File(None),
    request_data: str = Form(...)
):
    """Hide data or file in container"""
    try:
        request_obj = HideRequest.parse_raw(request_data)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="pending",
            message="Job queued for processing"
        )
        
        # Read file contents before starting background task
        print(f"[DEBUG] Reading container file: {container_file.filename}")
        container_content = await container_file.read()
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        
        secret_content = None
        if secret_file:
            print(f"[DEBUG] Reading secret file: {secret_file.filename}")
            secret_content = await secret_file.read()
            print(f"[DEBUG] Secret content size: {len(secret_content)} bytes")
        
        # Start background task with file contents
        background_tasks.add_task(
            process_hide_job,
            job_id,
            container_file.filename,
            container_content,
            secret_file.filename if secret_file else None,
            secret_content,
            request_obj
        )
        
        return {"job_id": job_id, "status": "pending"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Hide operation failed: {str(e)}")

@app.post("/api/extract")
async def extract_data(
    background_tasks: BackgroundTasks,
    container_file: UploadFile = File(...),
    request_data: str = Form(...)
):
    """Extract data from container file"""
    try:
        request_obj = ExtractRequest.parse_raw(request_data)
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        jobs[job_id] = JobStatus(
            job_id=job_id,
            status="pending",
            message="Job queued for processing"
        )
        
        # Read file content before starting background task
        print(f"[DEBUG] Reading container file for extraction: {container_file.filename}")
        container_content = await container_file.read()
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        
        # Start background task with file content
        background_tasks.add_task(
            process_extract_job,
            job_id,
            container_file.filename,
            container_content,
            request_obj
        )
        
        return {"job_id": job_id, "status": "pending"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Extract operation failed: {str(e)}")

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and result"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs[job_id]

@app.get("/api/download/{job_id}")
async def download_result(job_id: str):
    """Download the result file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job.status != "completed" or not job.download_url:
        raise HTTPException(status_code=400, detail="No file available for download")
    
    # Handle both absolute and relative paths
    file_path = Path(job.download_url)
    print(f"[DEBUG] Download requested for job {job_id}, download_url: {job.download_url}")
    
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    
    print(f"[DEBUG] Trying absolute path: {file_path}")
    if not file_path.exists():
        # Try without the full path, just the filename in outputs
        filename = file_path.name
        file_path = OUTPUT_DIR / filename
        print(f"[DEBUG] Trying outputs directory: {file_path}")
        
    if not file_path.exists():
        print(f"[DEBUG] File not found in either location")
        print(f"[DEBUG] Checked paths:")
        print(f"  1. {Path(job.download_url)}")
        print(f"  2. {Path.cwd() / job.download_url}")
        print(f"  3. {OUTPUT_DIR / Path(job.download_url).name}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    print(f"[DEBUG] File found at: {file_path}")
    
    # Use user-friendly filename if available, otherwise fall back to original filename
    download_filename = job.user_friendly_name if job.user_friendly_name else file_path.name
    print(f"[DEBUG] Serving file with name: {download_filename}")
    
    return FileResponse(
        path=str(file_path),
        filename=download_filename,
        media_type='application/octet-stream'
    )

async def process_hide_job(
    job_id: str,
    container_filename: str,
    container_content: bytes,
    secret_filename: Optional[str],
    secret_content: Optional[bytes],
    request_obj: HideRequest
):
    """Background task to process hide operation"""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].message = "Processing hide operation..."
        
        # Save container file
        container_path = UPLOAD_DIR / f"{job_id}_container_{container_filename}"
        print(f"[DEBUG] Saving container to: {container_path}")
        print(f"[DEBUG] Container content size: {len(container_content)} bytes")
        with open(container_path, "wb") as buffer:
            buffer.write(container_content)
        print(f"[DEBUG] Container file saved successfully")
        
        # Determine payload
        if secret_content is not None:
            # Hide file
            secret_path = UPLOAD_DIR / f"{job_id}_secret_{secret_filename}"
            print(f"[DEBUG] Saving secret file to: {secret_path}")
            print(f"[DEBUG] Secret content size: {len(secret_content)} bytes")
            with open(secret_path, "wb") as buffer:
                buffer.write(secret_content)
            print(f"[DEBUG] Secret file saved successfully")
            payload = str(secret_path)
            is_file = True
        else:
            # Hide text data
            payload = request_obj.data
            is_file = False
        
        # Output path with improved naming
        file_type = get_file_type_from_extension(container_filename)
        improved_output_filename = create_output_filename(container_filename, "stego", file_type)
        output_path = OUTPUT_DIR / f"{job_id[:8]}_{improved_output_filename}"
        
        print(f"[DEBUG] Improved output filename: {improved_output_filename}")
        print(f"[DEBUG] Full output path: {output_path}")
        
        # Simple file type detection from filename for reliability
        file_ext = container_filename.lower().split('.')[-1] if '.' in container_filename else ''
        
        # Use simple steganography for images to ensure reliability
        if file_ext in ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff']:
            # Use simple, reliable steganography for images
            print(f"[DEBUG] Using simple steganography for image file: {file_ext}")
            print(f"[DEBUG] Container path: {container_path}")
            print(f"[DEBUG] Payload: {payload}")
            print(f"[DEBUG] Output path: {output_path}")
            print(f"[DEBUG] Is file: {is_file}")
            
            try:
                manager = SimpleSteganographyManager(request_obj.password)
                print(f"[DEBUG] Created SimpleSteganographyManager")
                
                result_dict = manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Hide operation completed: {result_dict}")
            except Exception as e:
                print(f"[ERROR] SimpleSteganographyManager failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
            
            # Ensure output is PNG for data preservation
            actual_output = result_dict.get('output_path', str(output_path))
            if actual_output != str(output_path):
                # Update output path if it was changed (e.g., converted to PNG)
                import shutil
                final_output = OUTPUT_DIR / f"{job_id}_output.png"
                shutil.move(actual_output, final_output)
                output_path = final_output
                
        elif file_ext in ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac']:
            # Use Universal Text Audio Steganography (uses working UniversalFileAudio logic)
            print(f"[DEBUG] Using Universal Text Audio Steganography for: {file_ext}")
            
            try:
                # Use the universal text audio steganography that works
                audio_manager = UniversalTextAudioSteganographyManager(request_obj.password)
                
                # Pass the original filename when embedding files to preserve extension
                original_filename = None
                if is_file and isinstance(payload, str) and os.path.isfile(payload):
                    original_filename = os.path.basename(payload)
                    print(f"[DEBUG] Preserving original filename for file embedding: {original_filename}")
                
                # Perform steganography directly (handles all audio formats and preserves format)
                result_dict = audio_manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Final audio hide operation completed: {result_dict}")
                
                # Use the actual output path returned by the steganography function
                actual_output = result_dict.get('output_path', str(output_path))
                
                # Update output path to match what was actually created
                if actual_output != str(output_path):
                    print(f"[DEBUG] Output path updated from {output_path} to {actual_output}")
                    # Determine the final output name based on the actual output
                    actual_ext = os.path.splitext(actual_output)[1]
                    final_output = OUTPUT_DIR / f"{job_id}_output{actual_ext}"
                    
                    if actual_output != str(final_output):
                        import shutil
                        if os.path.exists(actual_output):
                            shutil.move(actual_output, str(final_output))
                            print(f"[DEBUG] Moved output from {actual_output} to: {final_output}")
                        else:
                            print(f"[WARNING] Expected output file not found: {actual_output}")
                    output_path = final_output
                else:
                    output_path = Path(actual_output)
                
            except Exception as e:
                error_msg = f"Audio steganography failed: {str(e)}. The audio file may be too short or incompatible. Please try with a longer audio file for best results."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                
        elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv']:
            # Use Robust Video Steganography for reliable performance
            print(f"[DEBUG] Using Robust Video Steganography for: {file_ext}")
            
            # For file hiding (especially images), prefer AVI format for lossless compression
            if is_file and file_ext != 'avi':
                base_name = output_path.stem
                output_path = output_path.parent / f"{base_name}.avi"
                print(f"[DEBUG] Using AVI format for better lossless compression: {output_path}")
            
            try:
                video_manager = RobustVideoSteganographyManager(request_obj.password)
                
                # Pass the original filename when embedding files to preserve extension
                original_filename = None
                if is_file and isinstance(payload, str) and os.path.isfile(payload):
                    original_filename = os.path.basename(payload)
                    print(f"[DEBUG] Preserving original filename for file embedding: {original_filename}")
                
                # Perform robust video steganography
                result_dict = video_manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Robust video hide operation completed: {result_dict}")
                
                # The robust video steganography creates the file directly at the specified path
                actual_output = result_dict.get('output_path', str(output_path))
                
                # Verify the file was created where expected
                if os.path.exists(actual_output):
                    output_path = Path(actual_output)
                    print(f"[DEBUG] Robust video output verified at: {output_path}")
                else:
                    print(f"[ERROR] Robust video output not found at: {actual_output}")
                    raise Exception(f"Output file not created: {actual_output}")
                
            except Exception as e:
                error_msg = f"Video steganography failed: {str(e)}. The video file may be too short or the data too large. Try with a longer video or smaller file."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                
        elif file_ext in ['pdf', 'docx', 'doc', 'txt', 'rtf', 'odt', 'md', 'rst']:
            # Use Enhanced Document Steganography for documents
            print(f"[DEBUG] Using Enhanced Document Steganography for: {file_ext}")
            
            try:
                document_manager = SteganographyManagerEnhanced(request_obj.password)
                
                result_dict = document_manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Document hide operation completed: {result_dict}")
            except Exception as e:
                print(f"[ERROR] Document steganography failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
                
        else:
            # For non-image, non-audio files, use basic steganography to avoid file handling issues
            print(f"[DEBUG] Using basic steganography for non-image, non-audio file: {file_ext}")
            try:
                manager = SteganographyManager(request_obj.password)
                print(f"[DEBUG] Created SteganographyManager")
                
                result_dict = manager.hide_data(str(container_path), payload, str(output_path), is_file)
                print(f"[DEBUG] Basic hide operation completed: {result_dict}")
            except Exception as e:
                print(f"[ERROR] SteganographyManager failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Hide operation completed successfully"
        jobs[job_id].result = result_dict
        jobs[job_id].download_url = output_path.name  # Store just the filename
        
        # Set filename metadata for user-friendly downloads
        jobs[job_id].operation_type = "hide"
        jobs[job_id].original_container_name = container_filename
        jobs[job_id].user_friendly_name = generate_user_friendly_name("hide", container_filename)
        
        # Clean up input files
        container_path.unlink()
        if secret_content is not None and secret_path.exists():
            secret_path.unlink()
            
    except Exception as e:
        print(f"[ERROR] Exception in process_hide_job: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Hide operation failed: {str(e)}"

async def process_extract_job(
    job_id: str,
    container_filename: str,
    container_content: bytes,
    request_obj: ExtractRequest
):
    """Background task to process extract operation"""
    try:
        jobs[job_id].status = "processing"
        jobs[job_id].message = "Processing extract operation..."
        
        # Save container file
        container_path = UPLOAD_DIR / f"{job_id}_extract_{container_filename}"
        print(f"[DEBUG] Saving container for extraction to: {container_path}")
        with open(container_path, "wb") as buffer:
            buffer.write(container_content)
        print(f"[DEBUG] Container file saved for extraction")
        
        # Simple file type detection from filename for reliability
        file_ext = container_filename.lower().split('.')[-1] if '.' in container_filename else ''
        
        # Use simple steganography for images to ensure reliability
        if file_ext in ['png', 'jpg', 'jpeg', 'bmp', 'webp', 'tiff']:
            # Use simple, reliable steganography for images
            manager = SimpleSteganographyManager(request_obj.password)
            extracted_data, filename = manager.extract_data(str(container_path))
            result_dict = {
                "success": True,
                "data_size": len(extracted_data),
                "filename": filename,
                "method": "Simple LSB"
            }
            
        elif file_ext in ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac']:
            # Use Universal Text Audio Steganography for extraction
            print(f"[DEBUG] Using Universal Text Audio Steganography extraction for: {file_ext}")
            
            try:
                # Use the universal text audio steganography
                audio_manager = UniversalTextAudioSteganographyManager(request_obj.password)
                extracted_data, filename = audio_manager.extract_data(str(container_path))
                result_dict = {
                    "success": True,
                    "data_size": len(extracted_data),
                    "filename": filename,
                    "method": "Final PCM Audio Steganography"
                }
                print(f"[DEBUG] Final audio extraction completed: {result_dict}")
            except Exception as e:
                error_msg = f"Audio extraction failed: {str(e)}. Please ensure the audio file contains hidden data created with this system."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
                # Don't raise, just mark as failed and return
        
        elif file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'wmv', 'flv']:
            # Use Robust Video Steganography for extraction
            print(f"[DEBUG] Using Robust Video Steganography extraction for: {file_ext}")
            
            try:
                print(f"[DEBUG] Creating RobustVideoSteganographyManager with password: '{request_obj.password}'")
                video_manager = RobustVideoSteganographyManager(request_obj.password)
                print(f"[DEBUG] Manager created: {type(video_manager).__name__}")
                print(f"[DEBUG] Manager password: '{video_manager.password if hasattr(video_manager, 'password') else 'NO PASSWORD ATTR'}'")
                
                print(f"[DEBUG] Calling extract_data on file: {container_path}")
                
                # CRITICAL SECURITY FIX: Add explicit password validation
                try:
                    extracted_data, filename = video_manager.extract_data(str(container_path))
                    print(f"[DEBUG] Extract result: data={type(extracted_data) if extracted_data else None}, size={len(extracted_data) if extracted_data else 0}, filename={filename}")
                    
                    # SECURITY CHECK: If data was extracted, verify it's not due to a bypass
                    if extracted_data and filename:
                        # Double-check by attempting extraction with a known wrong password
                        print(f"[SECURITY] Performing additional password validation...")
                        test_wrong_manager = RobustVideoSteganographyManager("__INTENTIONALLY_WRONG_PASSWORD__")
                        try:
                            test_data, test_filename = test_wrong_manager.extract_data(str(container_path))
                            if test_data and test_filename:
                                # If wrong password also succeeds, there's a vulnerability!
                                print(f"[SECURITY] ❌ CRITICAL: Wrong password also extracted data - REJECTING!")
                                error_msg = "Security validation failed: Password protection may be compromised"
                                print(f"[ERROR] {error_msg}")
                                jobs[job_id].status = "failed"
                                jobs[job_id].message = error_msg
                                jobs[job_id].error = "Security validation failed"
                                return
                            else:
                                print(f"[SECURITY] ✅ Password validation passed - wrong password properly failed")
                        except Exception as security_e:
                            print(f"[SECURITY] ✅ Password validation passed - wrong password raised error: {security_e}")
                    
                except ValueError as ve:
                    # This should be a password error - let it propagate
                    if "Data corruption detected or wrong password" in str(ve):
                        print(f"[DEBUG] Proper password validation error: {ve}")
                        raise ve
                    else:
                        print(f"[DEBUG] Other ValueError: {ve}")
                        raise ve
                
                if extracted_data and filename:
                    result_dict = {
                        "success": True,
                        "data_size": len(extracted_data),
                        "filename": filename,
                        "method": "Robust Video Steganography"
                    }
                    print(f"[DEBUG] Robust video extraction completed: {result_dict}")
                else:
                    # No data found
                    error_msg = "No hidden data found in video. The video may not contain steganographic data, may have been compressed, or was created with a different system."
                    print(f"[ERROR] {error_msg}")
                    jobs[job_id].status = "failed"
                    jobs[job_id].message = error_msg
                    jobs[job_id].error = "No data found"
                    return
                    
            except Exception as e:
                print(f"[DEBUG] Exception type: {type(e).__name__}")
                print(f"[DEBUG] Exception message: {str(e)}")
                print(f"[DEBUG] Exception details: {repr(e)}")
                
                # Check if this is a password validation error
                if "Data corruption detected or wrong password" in str(e):
                    error_msg = f"Password validation failed: {str(e)}"
                    print(f"[ERROR] {error_msg}")
                    jobs[job_id].status = "failed"
                    jobs[job_id].message = error_msg
                    jobs[job_id].error = str(e)
                    return
                
                error_msg = f"Video extraction failed: {str(e)}. Please ensure the video file contains hidden data created with this system."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
        
        elif file_ext in ['pdf', 'docx', 'doc', 'txt', 'rtf', 'odt', 'md', 'rst']:
            # Use Enhanced Document Steganography for extraction
            print(f"[DEBUG] Using Enhanced Document Steganography extraction for: {file_ext}")
            
            try:
                document_manager = SteganographyManagerEnhanced(request_obj.password)
                extracted_data, filename = document_manager.extract_data(str(container_path))
                result_dict = {
                    "success": True,
                    "data_size": len(extracted_data),
                    "filename": filename,
                    "method": "Enhanced Document Steganography"
                }
                print(f"[DEBUG] Document extraction completed: {result_dict}")
            except Exception as e:
                error_msg = f"Document extraction failed: {str(e)}. Please ensure the document contains hidden data created with this system."
                print(f"[ERROR] {error_msg}")
                jobs[job_id].status = "failed"
                jobs[job_id].message = error_msg
                jobs[job_id].error = str(e)
                return
        
        elif request_obj.is_enhanced:
            # Use enhanced manager for non-images, non-audio
            manager = SteganographyManagerEnhanced(request_obj.password)
            try:
                result = manager.extract_data_robust(str(container_path))
                extracted_data = result.data
                filename = result.filename
                result_dict = {
                    "success": result.success,
                    "data_size": len(extracted_data) if extracted_data else 0,
                    "filename": filename,
                    "verification_passed": result.verification_passed,
                    "error_correction_applied": result.error_correction_applied
                }
            except ValueError as e:
                if "empty range" in str(e):
                    # Fallback to regular manager for small images
                    manager = SteganographyManager(request_obj.password)
                    extracted_data, filename = manager.extract_data(str(container_path))
                    result_dict = {
                        "success": True,
                        "data_size": len(extracted_data),
                        "filename": filename
                    }
                else:
                    raise e
        else:
            manager = SteganographyManager(request_obj.password)
            extracted_data, filename = manager.extract_data(str(container_path))
            result_dict = {
                "success": True,
                "data_size": len(extracted_data),
                "filename": filename
            }
        
        # Save extracted data with improved filename
        if filename and filename != "embedded_text.txt":
            # Use the original filename with extension
            improved_extracted_filename = create_extracted_filename(filename, "file")
        else:
            # Default meaningful name for text data
            improved_extracted_filename = create_extracted_filename(None, "text")
            
        output_path = OUTPUT_DIR / f"{job_id[:8]}_{improved_extracted_filename}"
        
        print(f"[DEBUG] Improved extracted filename: {improved_extracted_filename}")
        print(f"[DEBUG] Full extracted output path: {output_path}")
        
        with open(output_path, "wb") as f:
            f.write(extracted_data)
        
        jobs[job_id].status = "completed"
        jobs[job_id].message = "Extract operation completed successfully"
        jobs[job_id].result = result_dict
        jobs[job_id].download_url = output_path.name  # Store just the filename
        
        # Set filename metadata for user-friendly downloads
        jobs[job_id].operation_type = "extract"
        jobs[job_id].original_container_name = container_filename
        # Use the extracted filename if available, otherwise use generic name
        original_payload_name = result_dict.get('filename', 'unknown')
        jobs[job_id].original_payload_name = original_payload_name
        jobs[job_id].user_friendly_name = generate_user_friendly_name("extract", container_filename, original_payload_name)
        
        # Clean up input file
        container_path.unlink()
        
    except Exception as e:
        jobs[job_id].status = "failed"
        jobs[job_id].message = f"Extract operation failed: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    import time
    
    # Cleanup old files on startup
    cleanup_old_files()
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)