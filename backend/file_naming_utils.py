#!/usr/bin/env python3
"""
Improved File Naming Utilities for Steganography Application
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from datetime import datetime


def create_output_filename(container_filename: str, operation: str = "hidden", method: str = "") -> str:
    """
    Create a meaningful output filename for processed files
    
    Args:
        container_filename: Original container file name
        operation: Type of operation ("hidden", "extracted", etc.)
        method: Steganography method used ("video", "audio", "image")
    
    Returns:
        New filename with appropriate suffix
    """
    # Parse the original filename
    path = Path(container_filename)
    name_without_ext = path.stem
    extension = path.suffix.lower()
    
    # Create meaningful suffix based on operation and method
    if operation == "hidden":
        if method:
            suffix = f"_stego_{method}"
        else:
            suffix = "_stego"
    elif operation == "extracted":
        suffix = "_extracted"
    else:
        suffix = f"_{operation}"
    
    # Combine to create new filename
    new_filename = f"{name_without_ext}{suffix}{extension}"
    
    return new_filename


def create_extracted_filename(original_hidden_filename: Optional[str], 
                            data_type: str = "file",
                            file_extension: Optional[str] = None) -> str:
    """
    Create a meaningful filename for extracted content
    
    Args:
        original_hidden_filename: Original name of the hidden file (if known)
        data_type: Type of extracted data ("file", "text", "binary")
        file_extension: File extension if known
    
    Returns:
        Appropriate filename for extracted content
    """
    
    if original_hidden_filename and original_hidden_filename not in ["embedded_text.txt", "extracted_message.txt"]:
        # Use the original filename if it's meaningful
        return original_hidden_filename
    
    # Create meaningful names based on data type
    if data_type == "text":
        return "secret_message.txt"
    elif data_type == "file" and file_extension:
        return f"hidden_file{file_extension}"
    elif data_type == "binary":
        return "hidden_data.bin"
    else:
        # Default fallback
        return "extracted_content.txt"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to be safe for filesystem
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    
    sanitized = filename
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "file"
    
    # Limit length to reasonable size
    if len(sanitized) > 200:
        name_part = sanitized[:150]
        ext_part = sanitized[-50:] if '.' in sanitized[-50:] else ""
        sanitized = name_part + "..." + ext_part
    
    return sanitized


def get_file_type_from_extension(filename: str) -> str:
    """
    Determine file type category from extension
    
    Args:
        filename: File name with extension
        
    Returns:
        File type category ("image", "audio", "video", "document", "other")
    """
    extension = Path(filename).suffix.lower()
    
    image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff', '.gif'}
    audio_exts = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
    video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.wmv', '.flv'}
    document_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    
    if extension in image_exts:
        return "image"
    elif extension in audio_exts:
        return "audio"
    elif extension in video_exts:
        return "video"
    elif extension in document_exts:
        return "document"
    else:
        return "other"


def create_job_based_filename(job_id: str, base_filename: str, operation: str) -> str:
    """
    Create filename with job ID for uniqueness while maintaining readability
    
    Args:
        job_id: Unique job identifier
        base_filename: Base filename to use
        operation: Operation type
        
    Returns:
        Filename with job ID and meaningful name
    """
    # Use shorter job ID for readability
    short_job_id = job_id[:8] if len(job_id) >= 8 else job_id
    
    path = Path(base_filename)
    name_without_ext = path.stem
    extension = path.suffix
    
    return f"{short_job_id}_{name_without_ext}_{operation}{extension}"


# Test the naming functions
def test_file_naming():
    """Test the file naming functions"""
    print("🏷️ Testing File Naming Utilities")
    
    # Test output filename creation
    test_cases = [
        ("video.mp4", "hidden", "video"),
        ("audio.wav", "hidden", "audio"),
        ("image.png", "hidden", "image"),
        ("document.pdf", "hidden", ""),
    ]
    
    print("\n📁 Output Filename Tests:")
    for container, operation, method in test_cases:
        result = create_output_filename(container, operation, method)
        print(f"  {container} → {result}")
    
    # Test extracted filename creation
    print("\n📄 Extracted Filename Tests:")
    extract_tests = [
        ("secret_document.pdf", "file", None),
        (None, "text", None),
        ("image.jpg", "file", None),
        (None, "file", ".png"),
        ("embedded_text.txt", "text", None),
    ]
    
    for orig_name, data_type, ext in extract_tests:
        result = create_extracted_filename(orig_name, data_type, ext)
        print(f"  {orig_name} ({data_type}) → {result}")
    
    # Test file type detection
    print("\n🔍 File Type Detection Tests:")
    type_tests = ["image.jpg", "audio.mp3", "video.mp4", "document.pdf", "unknown.xyz"]
    for filename in type_tests:
        file_type = get_file_type_from_extension(filename)
        print(f"  {filename} → {file_type}")
    
    print("\n✅ File naming tests complete!")


if __name__ == "__main__":
    test_file_naming()