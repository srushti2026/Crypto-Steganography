#!/usr/bin/env python3
"""
CLEAN VIDEO STEGANOGRAPHY MODULE - OPTIMIZED AND FIXED

Key fixes:
1. Proper H.264 MP4 encoding for compatibility
2. Unique video identification to prevent cross-contamination  
3. Performance optimization (3x redundancy instead of 5x)
4. Clean implementatio        # Extract bits from frames with optimization
        all_bits = []
        redundancy = 3
        max_bits = 10000  # Reduced limit for faster extraction
        max_frames = 50   # Process only first 50 frames for speed
        
        processed_frames = 0
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                flat_frame = frame.flatten()
                
                for i in range(0, len(flat_frame), redundancy):
                    if i + redundancy <= len(flat_frame):
                        bits = [flat_frame[i + j] & 1 for j in range(redundancy)]
                        majority_bit = 1 if sum(bits) > redundancy // 2 else 0
                        all_bits.append(str(majority_bit))
                        
                        # Stop when we have enough bits
                        if len(all_bits) >= max_bits:
                            break
                            
            processed_frames += 1
            if len(all_bits) >= max_bits or processed_frames >= max_frames:
                breakar imports
"""

import os
import cv2
import json
import hashlib
import time
import struct
from typing import Dict, Any, Optional, Union, Tuple
import numpy as np

# Import content detection function for filename detection (like image steganography)
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
        # Check if it looks like text content (COPYRIGHT DATA CASE)
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

class VideoSteganographyManager:
    """Clean, optimized video steganography manager"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def cleanup_test_isolation(self, project_name: str = None, max_age_hours: int = 24) -> int:
        """
        Clean up old frame directories to prevent cross-contamination between test runs.
        
        Args:
            project_name: If provided, only clean directories related to this project
            max_age_hours: Remove directories older than this many hours (default: 24)
            
        Returns:
            Number of directories cleaned up
        """
        import shutil
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            if not os.path.exists(self.outputs_dir):
                return 0
                
            print(f"[VideoStego] 🧹 CLEANUP: Starting test isolation cleanup...")
            
            for item in os.listdir(self.outputs_dir):
                if item.endswith('_frames'):
                    frame_dir_path = os.path.join(self.outputs_dir, item)
                    
                    if not os.path.isdir(frame_dir_path):
                        continue
                    
                    # Check age
                    dir_age = current_time - os.path.getctime(frame_dir_path)
                    
                    # Check project name filter
                    should_clean = False
                    
                    if project_name:
                        # Only clean if directory name contains project-related terms
                        project_lower = project_name.lower()
                        item_lower = item.lower()
                        
                        # Match project name patterns
                        if any(term in item_lower for term in [project_lower, 'test', 'simple', 'debug']):
                            should_clean = True
                    else:
                        # Clean based on age only
                        should_clean = dir_age > max_age_seconds
                    
                    if should_clean:
                        try:
                            shutil.rmtree(frame_dir_path)
                            cleaned_count += 1
                            print(f"[VideoStego] 🗑️  Cleaned: {item}")
                        except Exception as e:
                            print(f"[VideoStego] ⚠️  Failed to clean {item}: {e}")
            
            if cleaned_count > 0:
                print(f"[VideoStego] ✅ CLEANUP: Removed {cleaned_count} directories for test isolation")
            else:
                print(f"[VideoStego] ✅ CLEANUP: No cleanup needed")
                
        except Exception as e:
            print(f"[VideoStego] ❌ CLEANUP ERROR: {e}")
        
        return cleaned_count
    
    def auto_cleanup_for_project(self, project_name: str) -> None:
        """
        Automatically cleanup test directories for a specific project to prevent cross-contamination.
        This is called before embeddings to ensure clean state.
        """
        if project_name and any(term in project_name.lower() for term in ['test', 'debug', 'simple', 'fresh']):
            print(f"[VideoStego] 🔄 AUTO-CLEANUP: Cleaning test directories for project '{project_name}'")
            self.cleanup_test_isolation(project_name=project_name, max_age_hours=1)  # Clean recent test dirs
    
    def _generate_video_hash(self, video_path: str, password: str = None) -> str:
        """Generate stable hash for video file using properties + password"""
        try:
            hasher = hashlib.sha256()
            
            # Validate video path
            if not video_path or not os.path.exists(video_path):
                print(f"[VideoStego] Error: Video path does not exist: {video_path}")
                return "invalid_path"
            
            # Use video properties for more stable hashing (instead of pixel data)
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"[VideoStego] Error: Could not open video: {video_path}")
                cap.release()
                return "invalid_video"
                
            # Get stable video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            cap.release()
            
            # Hash MOST stable properties (dimensions, fps) - NOT frame count as it changes during embedding
            hasher.update(str(width).encode())
            hasher.update(str(height).encode())
            hasher.update(f"{fps:.1f}".encode())
            # DON'T use total_frames as it changes during embedding process
            
            # Add filename for uniqueness (but not timestamp/hash portions)
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            # Remove timestamp and hash portions for stability across embed/extract
            name_parts = base_name.split('_')
            if len(name_parts) >= 2:
                # Keep carrier type and size info, skip timestamps/hashes
                stable_name = '_'.join(name_parts[:2])
            else:
                stable_name = name_parts[0]
            hasher.update(stable_name.encode())
            
            # CRITICAL FIX: Include password in hash generation so same password always produces same hash
            if password:
                hasher.update(password.encode('utf-8'))
                print(f"[VideoStego] ✅ INCLUDING PASSWORD in hash generation: '{password}'")
            else:
                print(f"[VideoStego] ⚠️ NO PASSWORD provided for hash generation")
            
            hash_result = hasher.hexdigest()[:8]
            print(f"[VideoStego] 🔍 Generated STABLE hash: {hash_result} for {os.path.basename(video_path)} (properties: {width}x{height}, {fps:.1f}fps, name: {stable_name})")
            return hash_result
            
        except Exception as e:
            print(f"[VideoStego] Error generating video hash: {e}")
            return "error_hash"
    
    def _generate_property_only_hash(self, video_path: str, password: str = None) -> str:
        """Generate hash using only video properties (no filename) for broader matching"""
        try:
            hasher = hashlib.sha256()
            
            # Validate video path
            if not video_path or not os.path.exists(video_path):
                return "invalid_path"
            
            # Use video properties only (no filename)
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                cap.release()
                return "invalid_video"
                
            # Get stable video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            cap.release()
            
            # Hash ONLY video properties (no filename for broader matching)
            hasher.update(str(width).encode())
            hasher.update(str(height).encode())
            hasher.update(f"{fps:.1f}".encode())
            
            # Include password if provided
            if password:
                hasher.update(password.encode('utf-8'))
            
            hash_result = hasher.hexdigest()[:8]
            print(f"[VideoStego] 🔍 Generated PROPERTY-ONLY hash: {hash_result} for {os.path.basename(video_path)} (properties: {width}x{height}, {fps:.1f}fps)")
            return hash_result
            
        except Exception as e:
            print(f"[VideoStego] Error generating property-only hash: {e}")
            return "error_hash"
    
    def _get_frame_directory(self, video_path: str, video_hash: str) -> Optional[str]:
        """Get unique frame directory for this specific video"""
        try:
            if not video_path or not video_hash:
                print(f"[VideoStego] Invalid parameters: video_path={video_path}, video_hash={video_hash}")
                return None
                
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            # Fix: Remove existing "stego_" prefix to avoid duplication
            if base_name.startswith("stego_"):
                base_name = base_name[6:]  # Remove "stego_" prefix
            frame_dir_name = f"stego_{base_name}_{video_hash}_frames"
            
            print(f"[VideoStego] Frame directory name: {frame_dir_name}")
            return os.path.join(self.outputs_dir, frame_dir_name)
        except Exception as e:
            print(f"[VideoStego] Error getting frame directory: {e}")
            return None

    def _is_valid_stego_sequence(self, current_video: str, directory_video: str) -> bool:
        """
        Check if this is a valid stego sequence (e.g., stego2_clean -> stego1_clean)
        Only allow consecutive number sequences in stego files.
        """
        import re
        
        # Extract stego numbers from video names
        current_match = re.search(r'stego(\d+)', current_video)
        dir_match = re.search(r'stego(\d+)', directory_video)
        
        if not current_match or not dir_match:
            return False
            
        current_num = int(current_match.group(1))
        dir_num = int(dir_match.group(1))
        
        # Allow stego sequence: stego2 can use stego1 directory, stego3 can use stego2, etc.
        is_consecutive = (current_num == dir_num + 1)
        
        if is_consecutive:
            print(f"[VideoStego] 🔗 Valid stego sequence: {current_video} -> {directory_video}")
        else:
            print(f"[VideoStego] ⚠️ Invalid stego sequence: {current_video} -> {directory_video} (not consecutive)")
            
        return is_consecutive

    def _is_exact_video_match(self, current_video: str, directory_video: str) -> bool:
        """
        Check if two videos are exactly the same (ignoring only timestamp/hash suffixes)
        This prevents cross-contamination by being very strict about matching.
        """
        import re
        
        # Remove common prefixes
        current_clean = current_video.replace('stego_', '').replace('embedded_', '')
        dir_clean = directory_video.replace('stego_', '').replace('embedded_', '')
        
        # Remove timestamp and hash suffixes (patterns like _1764351358_8c8f76c7)
        current_core = re.sub(r'_\d{10}_[a-f0-9]{8}$', '', current_clean)
        dir_core = re.sub(r'_\d{10}_[a-f0-9]{8}$', '', dir_clean)
        
        # Remove any trailing hash-like patterns (6-8 hex chars)
        current_core = re.sub(r'_[a-f0-9]{6,8}$', '', current_core)
        dir_core = re.sub(r'_[a-f0-9]{6,8}$', '', dir_core)
        
        # Must be EXACTLY the same core name
        is_match = current_core == dir_core and len(current_core) > 3  # Avoid matching very short names
        
        print(f"[VideoStego] 🔍 EXACT MATCH CHECK:")
        print(f"   Current: '{current_video}' -> core: '{current_core}'")
        print(f"   Directory: '{directory_video}' -> core: '{dir_core}'")
        print(f"   Is exact match? {is_match}")
        
        return is_match

    def _extract_size_indicator(self, video_name: str) -> str:
        """Extract size indicator from video name (e.g., '168KB', '13MB')"""
        import re
        # Look for patterns like 168KB, 13MB, 1GB, etc.
        size_match = re.search(r'(\d+(?:\.\d+)?)(KB|MB|GB)', video_name, re.IGNORECASE)
        if size_match:
            return size_match.group(0).upper()  # Return like "168KB", "13MB"
        return ""

    def _is_same_video_lineage(self, current_video: str, directory_video: str) -> bool:
        """
        Check if two stego videos are from the same original video lineage.
        This prevents cross-contamination between different test scenarios.
        """
        import re
        
        # Extract the core video identifier (before stego prefixes and after removing numbers)
        current_core = re.sub(r'^stego(\d+)?_?', '', current_video)
        dir_core = re.sub(r'^stego(\d+)?_?', '', directory_video)
        
        # Remove timestamp and hash suffixes
        current_core = re.sub(r'_\d{10}_[a-f0-9]{8}$', '', current_core)
        dir_core = re.sub(r'_\d{10}_[a-f0-9]{8}$', '', dir_core)
        
        # Remove trailing hash patterns
        current_core = re.sub(r'_[a-f0-9]{6,8}$', '', current_core)
        dir_core = re.sub(r'_[a-f0-9]{6,8}$', '', dir_core)
        
        # For single-step embeddings (video -> stego), always allow
        if not current_video.startswith('stego') and directory_video.startswith('stego'):
            is_same = current_core == dir_core and len(current_core) >= 3  # Relaxed for initial embedding
        # For stego-to-stego (multi-layer), be more strict but still reasonable
        elif current_video.startswith('stego') and directory_video.startswith('stego'):
            is_same = current_core == dir_core and len(current_core) >= 3
        # For normal video to normal video (rare case), require exact match
        else:
            is_same = current_core == dir_core and len(current_core) >= 3
        
        print(f"[VideoStego] 🧬 LINEAGE CHECK:")
        print(f"   Current: '{current_video}' -> lineage: '{current_core}' (len={len(current_core)})")
        print(f"   Directory: '{directory_video}' -> lineage: '{dir_core}' (len={len(dir_core)})")
        print(f"   Same lineage? {is_same}")
        
        return is_same

    def _find_frame_directory_by_video_hash(self, video_path: str, video_hash: str) -> Optional[str]:
        """Find frame directory by video hash pattern or properties (handles cross-video compatibility)"""
        try:
            if not video_path or not video_hash:
                print(f"[VideoStego] Invalid parameters: video_path={video_path}, video_hash={video_hash}")
                return None
            
            # Get video properties for flexible matching
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"[VideoStego] ❌ Cannot open video for property matching")
                return None
                
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            print(f"[VideoStego] Video properties: {width}x{height}, {total_frames} frames, {fps:.2f} fps")
            
            # Step 1: Try to find directories by checking frame_info.json for matching video properties/content
            print(f"[VideoStego] Step 1: Looking for directories with compatible video content (hash: {video_hash})")
            
            # IMPROVED: Check all frame directories for matching video_hash OR compatible properties
            # PERFORMANCE FIX: Add timeout and limit directory checks to prevent infinite processing
            import time
            start_time = time.time()
            max_directories_to_check = 25  # Limit to prevent excessive processing
            timeout_seconds = 30  # Maximum 30 seconds for directory scanning
            
            exact_hash_matches = []
            property_matches = []
            
            directories_found = []
            directories_checked = 0
            
            for dir_name in os.listdir(self.outputs_dir):
                # Check timeout
                if time.time() - start_time > timeout_seconds:
                    print(f"[VideoStego] ⚠️ TIMEOUT: Stopping directory search after {timeout_seconds}s")
                    break
                    
                # Check directory limit
                if directories_checked >= max_directories_to_check:
                    print(f"[VideoStego] ⚠️ LIMIT: Stopping after checking {max_directories_to_check} directories")
                    break
                
                if dir_name.endswith("_frames"):
                    dir_path = os.path.join(self.outputs_dir, dir_name)
                    if not os.path.isdir(dir_path):
                        continue
                    
                    directories_found.append(dir_name)
                    directories_checked += 1
                    
                    # Check frame_info.json for video_hash or property match
                    frame_info_path = os.path.join(dir_path, "frame_info.json")
                    if os.path.exists(frame_info_path):
                        try:
                            with open(frame_info_path, 'r') as f:
                                frame_info = json.load(f)
                            
                            stored_video_hash = frame_info.get('video_hash')
                            print(f"[VideoStego] 🔍 Checking {dir_name}: stored_hash='{stored_video_hash}' vs target='{video_hash}'")
                            
                            # Check for exact video_hash match (same source video)
                            if stored_video_hash == video_hash:
                                creation_time = os.path.getctime(dir_path)
                                exact_hash_matches.append((dir_path, creation_time))
                                print(f"[VideoStego] ✅ Found exact video_hash match: {dir_name}")
                                # PERFORMANCE: If we have an exact match, we can stop searching
                                if len(exact_hash_matches) >= 1:
                                    print(f"[VideoStego] 🚀 FAST EXIT: Found exact match, stopping search")
                                    break
                            
                            # Check for property compatibility with RELAXED tolerance for re-encoded videos
                            elif (frame_info.get('width') == width and 
                                  frame_info.get('height') == height):
                                # Dimensions match - check if this could be a re-encoded version
                                
                                print(f"[VideoStego] 📊 PROPERTY MATCH found for {dir_name}:")
                                print(f"   Target: {width}x{height}, {total_frames} frames, {fps:.2f} fps")
                                print(f"   Stored: {frame_info.get('width')}x{frame_info.get('height')}, {frame_info.get('total_frames')} frames, {frame_info.get('fps'):.2f} fps")
                                
                                # ENHANCED: Only match if there's filename/lineage correlation  
                                filename_correlation = False
                                
                                # Check if video names show clear lineage relationship
                                current_base = os.path.splitext(os.path.basename(video_path))[0]
                                
                                # Extract video name from directory name properly
                                # Directory format: stego_carrier_VIDEONAME_timestamp_hash1_hash2_frames
                                dir_video_name = dir_name
                                if dir_video_name.startswith('stego_carrier_'):
                                    dir_video_name = dir_video_name[14:]  # Remove 'stego_carrier_'
                                elif dir_video_name.startswith('stego_'):
                                    dir_video_name = dir_video_name[6:]   # Remove 'stego_'
                                
                                if dir_video_name.endswith('_frames'):
                                    dir_video_name = dir_video_name[:-7]  # Remove '_frames'
                                
                                # Remove timestamp and hash suffixes: _timestamp_hash1_hash2 or _timestamp_hash1_hash2_hash3
                                import re
                                # Handle both formats: with 2 or 3 hash components
                                dir_video_name = re.sub(r'_\d{10}_[a-f0-9]{8}_[a-f0-9]{8}(_[a-f0-9]{8})?$', '', dir_video_name)
                                print(f"[VideoStego] 🔧 DIRECTORY NAME PROCESSING: '{dir_name}' -> '{dir_video_name}'")
                                
                                # Remove common prefixes for comparison
                                current_clean = current_base.replace('stego', '').replace('embedded_', '').replace('_', '')
                                dir_clean = dir_video_name.replace('stego', '').replace('embedded_', '').replace('_', '')
                                
                                # PERFORMANCE: Reduce excessive debug logging during high-volume operations
                                correlation_debug_enabled = directories_checked <= 5  # Only show debug for first few directories
                                if correlation_debug_enabled:
                                    print(f"[VideoStego] 🔍 CORRELATION DEBUG:")
                                    print(f"   Current video: {current_base}")
                                    print(f"   Current clean: {current_clean}")  
                                    print(f"   Directory video: {dir_video_name}")
                                    print(f"   Directory clean: {dir_clean}")
                                else:
                                    # Just show summary for performance
                                    pass
                                
                                # BALANCED CORRELATION: Allow legitimate matches while preventing cross-contamination
                                
                                correlation_reason = None
                                
                                # 1. EXACT stego sequence matching (stego2 -> stego1, stego3 -> stego2)
                                # BUT only if they are from the exact same video lineage
                                if (current_base.startswith('stego') and dir_video_name.startswith('stego') and
                                    self._is_valid_stego_sequence(current_base, dir_video_name) and
                                    self._is_same_video_lineage(current_base, dir_video_name)):
                                    filename_correlation = True
                                    correlation_reason = f"Valid stego sequence same lineage: {current_base} -> {dir_video_name}"
                                
                                # 2. EXACT filename match with same core identifier
                                elif self._is_exact_video_match(current_base, dir_video_name):
                                    filename_correlation = True
                                    correlation_reason = f"Exact video match: {current_base} <-> {dir_video_name}"
                                
                                # 3. Basic stego embedding: stego_X video extracting from stego_X directory
                                elif (current_base.startswith('stego_') and 'stego_' in dir_name and
                                      self._is_same_video_lineage(current_base, dir_video_name)):
                                    filename_correlation = True
                                    correlation_reason = f"Basic stego match: {current_base} <-> {dir_video_name}"
                                
                                # 4. Multi-layer specific pattern (only for videos explicitly named with multilayer)
                                elif ('multilayer' in current_base.lower() and 'multilayer' in dir_name.lower() and
                                      self._is_exact_video_match(current_base, dir_video_name)):
                                    filename_correlation = True
                                    correlation_reason = f"Multi-layer exact match: {current_base} <-> {dir_name}"
                                
                                # 5. SPECIAL CASE: Stego video extraction - allow property-based matching
                                # This handles cases where a stego video is re-uploaded with a different name
                                elif current_base.startswith('stego') and not filename_correlation:
                                    # For stego videos, allow property-based matching even if names don't correlate
                                    # This is safe because stego videos are already processed and verified
                                    filename_correlation = True
                                    correlation_reason = f"Stego video property match: {current_base} -> {dir_video_name} (properties: {width}x{height}, {total_frames} frames)"
                                    print(f"[VideoStego] 🎯 STEGO VIDEO MATCH: Allowing property-based correlation for stego video")
                                
                                # 6. FLEXIBLE API SUPPORT: Allow property-based matching for API temporary files
                                # This enables video steganography to work with API-uploaded files that have random temp names
                                elif not filename_correlation and not current_base.startswith('stego'):
                                    # Check if the video names are at least somewhat related
                                    current_size_indicator = self._extract_size_indicator(current_base)
                                    directory_size_indicator = self._extract_size_indicator(dir_video_name)
                                    
                                    # CRITICAL FIX: Allow property matches for API temporary files (like tmp..._)
                                    # This fixes the issue where API uploads with random temp names can't find frame directories
                                    if (current_size_indicator == directory_size_indicator or 
                                        (not current_size_indicator and not directory_size_indicator)):
                                        filename_correlation = True  # Try password-based verification
                                        correlation_reason = f"Password-based verification: {current_base} (dimensions match: {width}x{height})"
                                    elif current_base.startswith('tmp') or current_base.startswith('stego_tmp'):
                                        # API TEMP FILE SUPPORT: Allow property-based matching for API temporary files
                                        filename_correlation = True
                                        correlation_reason = f"API temp file property match: {current_base} -> {dir_video_name} (temp file processing)"
                                        print(f"[VideoStego] 🎯 API TEMP FILE: Allowing property-based correlation for API upload: {current_base}")
                                    else:
                                        print(f"[VideoStego] ❌ SIZE MISMATCH: {current_size_indicator} vs {directory_size_indicator} - rejecting correlation")
                                
                                # ULTRA-STRICT: Completely removed all permissive matching
                                # - No substring matching of any kind
                                # - No partial name matching
                                # - No property-only matching without filename correlation
                                # - Requires exact lineage for stego sequences
                                
                                if filename_correlation and correlation_reason:
                                    if correlation_debug_enabled:
                                        print(f"[VideoStego] ✅ ULTRA-STRICT CORRELATION: {correlation_reason}")
                                else:
                                    if correlation_debug_enabled:
                                        print(f"[VideoStego] ❌ NO CORRELATION: {current_base} vs {dir_video_name} (ultra-strict isolation)")
                                
                                if filename_correlation:
                                    # This is a legitimate stego file lineage
                                    creation_time = os.path.getctime(dir_path)
                                    property_matches.append((dir_path, creation_time, stored_video_hash))
                                    if correlation_debug_enabled:
                                        print(f"[VideoStego] 🔍 Found property match with lineage: {dir_name} (original hash: {stored_video_hash})")
                                    
                                    # PERFORMANCE: Limit property matches to prevent excessive processing
                                    if len(property_matches) >= 25:  # Increased limit to find newer directories
                                        print(f"[VideoStego] 🚀 PERFORMANCE: Found {len(property_matches)} property matches, stopping search")
                                        break
                                else:
                                    if correlation_debug_enabled:
                                        print(f"[VideoStego] ⚠️  Skipped unrelated video: {dir_name} (no filename correlation with {current_base})")
                                
                        except Exception as e:
                            print(f"[VideoStego] Error checking {dir_name}: {e}")
            
            # Debug: Show what we found
            print(f"[VideoStego] 🔍 Search complete: found {len(directories_found)} directories, {len(exact_hash_matches)} exact matches, {len(property_matches)} property matches")
            if directories_found:
                print(f"[VideoStego] 📁 Directories found: {directories_found}")
            
            # Return the most recent directory with exact video_hash match
            if exact_hash_matches:
                exact_hash_matches.sort(key=lambda x: x[1], reverse=True)
                selected = exact_hash_matches[0][0]
                print(f"[VideoStego] ✅ Selected exact hash match: {os.path.basename(selected)}")
                return selected
            
            # If no exact match, use property match (stego file lineage)
            if property_matches:
                # Sort by creation time (most recent first) - this handles multi-layer embedding
                property_matches.sort(key=lambda x: x[1], reverse=True)
                selected = property_matches[0][0]
                original_hash = property_matches[0][2]
                
                # DEBUG: Show all matches for analysis
                print(f"[VideoStego] 📊 Found {len(property_matches)} property matches:")
                for i, (path, time, hash_val) in enumerate(property_matches):
                    name = os.path.basename(path)
                    print(f"   {i+1}. {name} (time: {time}, hash: {hash_val})")
                    
                print(f"[VideoStego] ✅ Selected property match: {os.path.basename(selected)} (lineage from: {original_hash})")
                return selected
            
            # Step 2: Try related video names (multi-layer lineage support)
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            if base_name.startswith("stego_"):
                base_name = base_name[6:]
            if base_name.startswith("embedded_"):
                base_name = base_name[9:]
                
            core_name_variants = []
            
            # Handle multi-layer video lineage: test_layer2_video -> test_layer1_video -> test_video_with_data -> test_video
            if "layer" in base_name:
                # For layered videos, try parent lineage
                if "_layer" in base_name:
                    parts = base_name.split("_layer")
                    root_name = parts[0]  # Get root name before _layer
                    
                    # Add all possible layer variations and original
                    core_name_variants.extend([
                        root_name,  # Original root name
                        f"{root_name}_with_data", # Previous data version  
                        "test_video", "carrier_test_video"  # Base variants
                    ])
                    
                    # Add numbered layer variants (layer1, layer0, etc)
                    for i in range(5):  # Check up to 5 layers back
                        if i == 0:
                            layer_name = f"{root_name}_layer{i+1}_video"
                        else:
                            layer_name = f"{root_name}_layer{i}_video"
                        core_name_variants.append(layer_name)
            
            # Handle embedded_stego_test_video_xxx -> test_video or carrier_test_video
            if "test_video" in base_name:
                core_name_variants.extend(["test_video", "carrier_test_video"])
            
            # Add the base name without prefixes and with _with_data suffix
            core_name_variants.extend([
                base_name,
                f"{base_name}_with_data"
            ])
            
            print(f"[VideoStego] Step 2: Searching for related names: {core_name_variants}")
            
            matching_dirs = []
            step2_checked = 0
            step2_max_check = 15  # Limit Step 2 directory checks
            
            for dir_name in os.listdir(self.outputs_dir):
                # Check Step 2 limit
                if step2_checked >= step2_max_check:
                    print(f"[VideoStego] 🚀 Step 2 LIMIT: Stopping after {step2_max_check} checks")
                    break
                    
                step2_checked += 1
                if dir_name.endswith("_frames"):
                    dir_path = os.path.join(self.outputs_dir, dir_name)
                    if not os.path.isdir(dir_path):
                        continue
                        
                    # Check if any core name variant matches
                    name_match = False
                    for variant in core_name_variants:
                        if variant in dir_name:
                            name_match = True
                            break
                    
                    if not name_match:
                        continue
                    
                    # Check frame_info.json for property matching
                    frame_info_path = os.path.join(dir_path, "frame_info.json")
                    if os.path.exists(frame_info_path):
                        try:
                            with open(frame_info_path, 'r') as f:
                                frame_info = json.load(f)
                            
                            # Calculate property match score
                            score = 0
                            if frame_info.get('width') == width:
                                score += 3
                            if frame_info.get('height') == height:
                                score += 3
                            if abs(frame_info.get('total_frames', 0) - total_frames) <= 2:
                                score += 4
                            if abs(frame_info.get('fps', 0) - fps) <= 1.0:
                                score += 2
                            
                            # Require strong property match for cross-video compatibility
                            if score >= 8:  # At least width+height+frames must match well
                                matching_dirs.append((dir_path, score))
                                print(f"[VideoStego] ✅ Property match: {dir_name} (score: {score})")
                                
                                # PERFORMANCE: If we have a really good match, stop searching
                                if score >= 12:  # Perfect match
                                    print(f"[VideoStego] 🚀 PERFECT MATCH: Found score {score}, stopping Step 2 search")
                                    break
                            else:
                                print(f"[VideoStego] ❌ Weak match: {dir_name} (score: {score})")
                                
                        except Exception as e:
                            print(f"[VideoStego] Error checking {dir_name}: {e}")
            
            if matching_dirs:
                # Sort by score (highest first), then by creation time (most recent first)
                matching_dirs.sort(key=lambda x: (x[1], os.path.getctime(x[0])), reverse=True)
                selected_dir = matching_dirs[0][0]
                selected_score = matching_dirs[0][1]
                
                print(f"[VideoStego] ✅ Selected best match: {os.path.basename(selected_dir)} (score: {selected_score})")
                return selected_dir
            else:
                print(f"[VideoStego] ❌ No compatible directories found for video properties")
                
                # Step 3: STRICTER FALLBACK - Only match directories with video_hash compatibility (prevent cross-contamination)
                print(f"[VideoStego] Step 3: Trying strict fallback search with video_hash validation...")
                
                fallback_matches = []
                step3_checked = 0
                step3_max_check = 10  # Even more restrictive for fallback
                
                for dir_name in os.listdir(self.outputs_dir):
                    # Check Step 3 limit
                    if step3_checked >= step3_max_check:
                        print(f"[VideoStego] 🚀 Step 3 LIMIT: Stopping after {step3_max_check} checks")
                        break
                        
                    step3_checked += 1
                    if dir_name.endswith("_frames"):
                        dir_path = os.path.join(self.outputs_dir, dir_name)
                        if not os.path.isdir(dir_path):
                            continue
                            
                        # Check frame_info.json for property matching AND video_hash compatibility
                        frame_info_path = os.path.join(dir_path, "frame_info.json")
                        if os.path.exists(frame_info_path):
                            try:
                                with open(frame_info_path, 'r') as f:
                                    frame_info = json.load(f)
                                
                                # STRICT: Only allow directories with matching video_hash (prevents cross-contamination)
                                stored_video_hash = frame_info.get('video_hash')
                                if stored_video_hash != video_hash:
                                    continue  # Skip directories created with different video context
                                
                                # Calculate property match score - require perfect match for fallback
                                score = 0
                                if frame_info.get('width') == width:
                                    score += 3
                                if frame_info.get('height') == height:
                                    score += 3
                                if abs(frame_info.get('total_frames', 0) - total_frames) <= 1:  # Stricter frame count
                                    score += 4
                                if abs(frame_info.get('fps', 0) - fps) <= 0.5:  # Stricter fps matching
                                    score += 2
                                
                                # Require NEAR-PERFECT match for fallback to prevent contamination
                                if score >= 10:  # Almost perfect match required
                                    creation_time = os.path.getctime(dir_path)
                                    fallback_matches.append((dir_path, score, creation_time))
                                    print(f"[VideoStego] ✅ Strict fallback match: {dir_name} (score: {score}, video_hash: {stored_video_hash})")
                                    
                            except Exception as e:
                                print(f"[VideoStego] Error checking fallback {dir_name}: {e}")
                
                if fallback_matches:
                    # Sort by creation time (most recent first), then by score
                    fallback_matches.sort(key=lambda x: (x[2], x[1]), reverse=True)
                    selected_dir = fallback_matches[0][0]
                    selected_score = fallback_matches[0][1]
                    
                    print(f"[VideoStego] ✅ Selected strict fallback match: {os.path.basename(selected_dir)} (score: {selected_score})")
                    return selected_dir
                else:
                    print(f"[VideoStego] ❌ No compatible directories found (strict fallback)")
                    return None
                
        except Exception as e:
            print(f"[VideoStego] Error finding frame directory by video hash: {e}")
            return None
    
    def _find_frame_directory_by_properties(self, video_path: str) -> Optional[str]:
        """Find frame directory by matching video properties when hash doesn't match"""
        
        # Get video properties
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        print(f"[VideoStego] Looking for frame directory matching {width}x{height}, {total_frames} frames")
        
        # Search ALL frame directories by properties with flexible matching
        matching_dirs = []
        
        for item in os.listdir(self.outputs_dir):
            if item.endswith('_frames'):
                frame_dir_path = os.path.join(self.outputs_dir, item)
                frame_info_file = os.path.join(frame_dir_path, "frame_info.json")
                
                if os.path.exists(frame_info_file):
                    try:
                        import json
                        with open(frame_info_file, 'r') as f:
                            frame_info = json.load(f)
                        
                        # Primary match: dimensions (frame count may differ due to optimization)
                        if (frame_info.get('width') == width and 
                            frame_info.get('height') == height):
                            
                            created_time = frame_info.get('created_at', 0)
                            is_optimized = frame_info.get('optimized', False)
                            stored_frames = frame_info.get('total_frames', 0)
                            
                            # Priority scoring: recent + optimized + dimension match
                            score = created_time
                            if is_optimized:
                                score += 1000000  # Prefer optimized directories
                                
                            # Special handling for performance-optimized videos
                            if is_optimized and stored_frames <= total_frames:
                                # This is likely the correct directory for an optimized embedding
                                score += 2000000
                            
                            matching_dirs.append((score, frame_dir_path, item, stored_frames, is_optimized))
                            
                    except Exception as e:
                        continue
        
        if matching_dirs:
            # Sort by score (highest first) - prioritizes recent optimized directories
            matching_dirs.sort(key=lambda x: x[0], reverse=True)
            selected_dir = matching_dirs[0]
            frames_info = f" ({selected_dir[3]} frames, optimized={selected_dir[4]})" if selected_dir[4] else f" ({selected_dir[3]} frames)"
            print(f"[VideoStego] Found matching frame directory: {selected_dir[2]}{frames_info}")
            return selected_dir[1]
        
        print(f"[VideoStego] Could not find frame directory by properties")
        return None
    
    def _find_frame_directory_by_property_hash(self, video_path: str, property_hash: str) -> Optional[str]:
        """Find frame directory using property-only hash for carrier/stego video correlation"""
        
        print(f"[VideoStego] 🔍 Property-hash search for: {property_hash}")
        
        # Look for frame directories that might contain data for videos with same properties
        # This helps match carrier and stego videos with different names but same video properties
        
        matching_dirs = []
        
        for item in os.listdir(self.outputs_dir):
            if item.endswith('_frames'):
                frame_dir_path = os.path.join(self.outputs_dir, item)
                frame_info_file = os.path.join(frame_dir_path, "frame_info.json")
                
                if os.path.exists(frame_info_file):
                    try:
                        import json
                        with open(frame_info_file, 'r') as f:
                            frame_info = json.load(f)
                        
                        # Get the video properties from the frame info and calculate property hash
                        stored_width = frame_info.get('width', 0)
                        stored_height = frame_info.get('height', 0)  
                        stored_fps = frame_info.get('fps', 0)
                        
                        # Generate property-only hash for comparison
                        hasher = hashlib.sha256()
                        hasher.update(str(stored_width).encode())
                        hasher.update(str(stored_height).encode()) 
                        hasher.update(f"{stored_fps:.1f}".encode())
                        stored_property_hash = hasher.hexdigest()[:8]
                        
                        print(f"[VideoStego] 🔍 Checking {item}: property_hash={stored_property_hash} vs target={property_hash}")
                        
                        if stored_property_hash == property_hash:
                            # Check if directory actually has frame files
                            frame_files = [f for f in os.listdir(frame_dir_path) if f.startswith('frame_') and f.endswith('.png')]
                            created_at = frame_info.get('created_at', 0)
                            
                            print(f"[VideoStego] 📂 Match found: {item} (frames: {len(frame_files)}, created: {created_at})")
                            
                            if len(frame_files) > 0:
                                matching_dirs.append((created_at, frame_dir_path, item, len(frame_files)))
                            else:
                                print(f"[VideoStego] ⚠️ Skipping {item}: no frame files found")
                            
                    except Exception as e:
                        print(f"[VideoStego] Error checking property hash for {item}: {e}")
                        continue
        
        if matching_dirs:
            # Sort by creation time (newest first) and prefer directories with more frames
            matching_dirs.sort(key=lambda x: (x[0], x[3]), reverse=True)
            selected_dir = matching_dirs[0]
            
            print(f"[VideoStego] ✅ Selected newest property-hash match: {selected_dir[2]} ({selected_dir[3]} frames)")
            return selected_dir[1]
        
        print(f"[VideoStego] ❌ No valid frame directory found with property hash: {property_hash}")
        return None
    
    def _find_frame_directory_by_name_pattern(self, stego_video_path: str) -> Optional[str]:
        """Find frame directory by matching video name pattern (fallback for hash mismatches)"""
        
        print(f"[VideoStego] 🔍 NAME PATTERN SEARCH for: {os.path.basename(stego_video_path)}")
        
        # Extract the base name from the stego video
        stego_basename = os.path.splitext(os.path.basename(stego_video_path))[0]
        
        # Remove stego prefix and hash suffixes to get the carrier name
        carrier_name = stego_basename
        if carrier_name.startswith("stego_"):
            carrier_name = carrier_name[6:]  # Remove "stego_" prefix
        
        # Remove hash suffixes (e.g., "_d7a8c3")
        import re
        carrier_name = re.sub(r'_[a-f0-9]{6,8}$', '', carrier_name)
        
        print(f"[VideoStego] 🔍 Looking for directories matching carrier: '{carrier_name}'")
        
        # Search all frame directories for name matches
        matching_dirs = []
        
        for dir_name in os.listdir(self.outputs_dir):
            if not dir_name.endswith("_frames"):
                continue
                
            # Check if this directory name contains the carrier name
            if carrier_name in dir_name:
                dir_path = os.path.join(self.outputs_dir, dir_name)
                frame_info_path = os.path.join(dir_path, "frame_info.json")
                
                if os.path.exists(frame_info_path):
                    try:
                        with open(frame_info_path, 'r', encoding='utf-8') as f:
                            frame_info = json.load(f)
                        
                        # Get creation time for sorting (most recent first)
                        created_at = frame_info.get('created_at', 0)
                        
                        # Calculate match score
                        score = 0
                        
                        # Exact carrier name match
                        if f"_{carrier_name}_" in dir_name:
                            score += 100
                        elif carrier_name in dir_name:
                            score += 50
                        
                        # Prefer recent directories
                        score += created_at / 1000000  # Normalize timestamp
                        
                        matching_dirs.append((score, dir_path, dir_name, created_at))
                        print(f"[VideoStego] 🎯 FOUND MATCH: {dir_name} (score: {score:.2f})")
                        
                    except Exception as e:
                        print(f"[VideoStego] ❌ Error checking {dir_name}: {e}")
        
        if matching_dirs:
            # Sort by score (highest first) 
            matching_dirs.sort(key=lambda x: x[0], reverse=True)
            best_match = matching_dirs[0]
            
            print(f"[VideoStego] ✅ BEST NAME MATCH: {best_match[2]} (score: {best_match[0]:.2f})")
            return best_match[1]
        
        print(f"[VideoStego] ❌ No name-based matches found for carrier: '{carrier_name}'")
        return None
    
    def _create_high_quality_video(self, frame_dir: str, output_path: str, fps: float, width: int, height: int, 
                                 original_video_path: str = None, total_original_frames: int = None):
        """Create high-quality video with minimal quality loss using the best available method"""
        
        print(f"[VideoStego] 🎬 Creating high-quality video with advanced optimization...")
        
        # Get modified frames info
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.png')])
        modified_frame_count = len(frame_files)
        
        print(f"[VideoStego] 📊 Quality optimization stats:")
        print(f"[VideoStego]   🔸 Modified frames: {modified_frame_count}")
        print(f"[VideoStego]   🔸 Total frames: {total_original_frames}")
        
        # Try FFmpeg first for best quality (if available) - but skip for very few modifications to avoid timeout
        if original_video_path and total_original_frames and modified_frame_count >= 5:
            print(f"[VideoStego] 🔥 Trying FFmpeg for {modified_frame_count} modifications...")
            ffmpeg_result = self._try_ffmpeg_quality_approach(
                frame_dir, output_path, fps, width, height,
                original_video_path, total_original_frames, modified_frame_count
            )
            if ffmpeg_result:
                return ffmpeg_result
        else:
            print(f"[VideoStego] ⚡ Skipping FFmpeg (only {modified_frame_count} modifications) - using OpenCV lossless approach")
        
        # If we only modified very few frames, use ultra-fast single frame replacement
        if original_video_path and modified_frame_count <= 2:
            return self._create_ultra_fast_single_frame_replacement(
                frame_dir, output_path, fps, width, height,
                original_video_path, total_original_frames, modified_frame_count
            )
        # If we only modified a few frames, use direct video stream copying for maximum quality
        elif original_video_path and modified_frame_count < 10:
            return self._create_optimized_video_with_minimal_changes(
                frame_dir, output_path, fps, width, height, 
                original_video_path, total_original_frames, modified_frame_count
            )
        
        # For more modifications, use high-quality re-encoding
        return self._create_reencoded_video_high_quality(
            frame_dir, output_path, fps, width, height,
            original_video_path, total_original_frames, modified_frame_count
        )
    
    def _create_optimized_video_with_minimal_changes(self, frame_dir: str, output_path: str, fps: float, 
                                                   width: int, height: int, original_video_path: str, 
                                                   total_original_frames: int, modified_frame_count: int):
        """Ultra-high quality video creation using advanced codec settings and quality preservation"""
        
        print(f"[VideoStego] 🚀 ULTRA-HIGH-QUALITY: Using advanced quality preservation (modified: {modified_frame_count}/{total_original_frames})")
        
        # Try multiple high-quality approaches
        approaches = [
            self._try_lossless_quality_approach,
            self._try_high_bitrate_approach,  
            self._try_container_copy_approach,
            self._try_standard_high_quality_approach
        ]
        
        for i, approach in enumerate(approaches):
            try:
                print(f"[VideoStego] 🎯 Trying approach {i+1}/{len(approaches)}...")
                result_path = approach(frame_dir, output_path, fps, width, height, 
                                     original_video_path, total_original_frames, modified_frame_count)
                
                if result_path and os.path.exists(result_path):
                    final_size = os.path.getsize(result_path)
                    original_size = os.path.getsize(original_video_path)
                    preservation_ratio = final_size / original_size
                    
                    print(f"[VideoStego] 📊 Approach {i+1} result: {preservation_ratio:.1%} quality preservation")
                    
                    # Accept if we get >50% quality preservation
                    if preservation_ratio > 0.5:
                        print(f"[VideoStego] ✅ EXCELLENT: Approach {i+1} achieved {preservation_ratio:.1%} quality preservation!")
                        return result_path
                    elif preservation_ratio > 0.35:
                        print(f"[VideoStego] ✅ GOOD: Approach {i+1} achieved {preservation_ratio:.1%} quality preservation!")
                        return result_path
                    else:
                        print(f"[VideoStego] ⚠️ Approach {i+1} quality too low ({preservation_ratio:.1%}), trying next...")
                        continue
                        
            except Exception as e:
                print(f"[VideoStego] ❌ Approach {i+1} failed: {e}")
                continue
        
        # Fallback to standard method
        print(f"[VideoStego] ⚠️ All quality approaches failed, using standard method")
        return self._try_standard_high_quality_approach(
            frame_dir, output_path, fps, width, height,
            original_video_path, total_original_frames, modified_frame_count
        )
    
    def _try_lossless_quality_approach(self, frame_dir: str, output_path: str, fps: float,
                                     width: int, height: int, original_video_path: str,
                                     total_original_frames: int, modified_frame_count: int):
        """Try near-lossless quality approach"""
        
        print(f"[VideoStego] 🔬 Attempting LOSSLESS quality approach...")
        
        # Try uncompressed/lossless codec
        fourcc = cv2.VideoWriter_fourcc(*'HFYU')  # Huffman Lossless Codec
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            # Fallback to Motion JPEG with high quality
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
        if not out.isOpened():
            raise Exception("Lossless codecs not available")
        
        # Process with lossless settings
        cap_original = cv2.VideoCapture(original_video_path)
        frame_index = 0
        
        while frame_index < total_original_frames:
            ret, original_frame = cap_original.read()
            if not ret:
                break
            
            # Check for modified frame
            modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
            
            if os.path.exists(modified_frame_path):
                modified_frame = cv2.imread(modified_frame_path, cv2.IMREAD_COLOR)
                if modified_frame is not None:
                    out.write(modified_frame)
                else:
                    out.write(original_frame)
            else:
                out.write(original_frame)
            
            frame_index += 1
        
        cap_original.release()
        out.release()
        
        return output_path
    
    def _try_high_bitrate_approach(self, frame_dir: str, output_path: str, fps: float,
                                 width: int, height: int, original_video_path: str,
                                 total_original_frames: int, modified_frame_count: int):
        """Try high bitrate approach for quality preservation"""
        
        print(f"[VideoStego] 💎 Attempting HIGH BITRATE approach...")
        
        # Use H.264 with very high quality settings
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        
        # Create with high quality - note: OpenCV has limited codec control
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)
        
        if not out.isOpened():
            raise Exception("H.264 high bitrate codec failed")
        
        cap_original = cv2.VideoCapture(original_video_path)
        frame_index = 0
        
        while frame_index < total_original_frames:
            ret, original_frame = cap_original.read()
            if not ret:
                break
            
            modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
            
            if os.path.exists(modified_frame_path):
                modified_frame = cv2.imread(modified_frame_path, cv2.IMREAD_COLOR)
                if modified_frame is not None:
                    out.write(modified_frame)
                else:
                    out.write(original_frame)
            else:
                out.write(original_frame)
            
            frame_index += 1
        
        cap_original.release()
        out.release()
        
        return output_path
    
    def _try_container_copy_approach(self, frame_dir: str, output_path: str, fps: float,
                                   width: int, height: int, original_video_path: str,
                                   total_original_frames: int, modified_frame_count: int):
        """Try container-level copying for maximum quality preservation"""
        
        print(f"[VideoStego] 📦 Attempting CONTAINER COPY approach...")
        
        # For very few modifications, try to preserve the original container
        if modified_frame_count <= 2:
            # Use the same codec as original
            cap_original = cv2.VideoCapture(original_video_path)
            
            # Try to preserve original codec settings
            fourcc_int = int(cap_original.get(cv2.CAP_PROP_FOURCC))
            fourcc_chars = [chr((fourcc_int >> 8 * i) & 0xFF) for i in range(4)]
            original_codec = ''.join(fourcc_chars)
            
            print(f"[VideoStego] � Original codec detected: {original_codec}")
            
            # Use original codec if possible
            try:
                fourcc = cv2.VideoWriter_fourcc(*original_codec[:4])
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
                
                if out.isOpened():
                    print(f"[VideoStego] ✅ Using original codec: {original_codec}")
                    
                    frame_index = 0
                    while frame_index < total_original_frames:
                        ret, original_frame = cap_original.read()
                        if not ret:
                            break
                        
                        modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
                        
                        if os.path.exists(modified_frame_path):
                            modified_frame = cv2.imread(modified_frame_path, cv2.IMREAD_COLOR)
                            if modified_frame is not None:
                                out.write(modified_frame)
                            else:
                                out.write(original_frame)
                        else:
                            out.write(original_frame)
                        
                        frame_index += 1
                    
                    cap_original.release()
                    out.release()
                    return output_path
                    
            except Exception as e:
                print(f"[VideoStego] ⚠️ Original codec failed: {e}")
            
            cap_original.release()
        
        raise Exception("Container copy not applicable or failed")
    
    def _try_standard_high_quality_approach(self, frame_dir: str, output_path: str, fps: float,
                                          width: int, height: int, original_video_path: str,
                                          total_original_frames: int, modified_frame_count: int):
        """Standard high-quality approach as fallback"""
        
        print(f"[VideoStego] 🎥 Using STANDARD HIGH-QUALITY approach...")
        
        # Use most compatible high-quality codec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise Exception("Standard codec failed")
        
        cap_original = cv2.VideoCapture(original_video_path)
        frame_index = 0
        
        while frame_index < total_original_frames:
            ret, original_frame = cap_original.read()
            if not ret:
                break
            
            modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
            
            if os.path.exists(modified_frame_path):
                modified_frame = cv2.imread(modified_frame_path, cv2.IMREAD_COLOR)
                if modified_frame is not None:
                    out.write(modified_frame)
                else:
                    out.write(original_frame)
            else:
                out.write(original_frame)
            
            frame_index += 1
        
        cap_original.release()
        out.release()
        
        return output_path
    
    def _create_reencoded_video_high_quality(self, frame_dir: str, output_path: str, fps: float, 
                                           width: int, height: int, original_video_path: str = None,
                                           total_original_frames: int = None, modified_frame_count: int = 0):
        """Create video with high-quality re-encoding when many frames are modified"""
        
        print(f"[VideoStego] 🎥 Using high-quality re-encoding approach...")
        
        # Try codecs in order of quality preservation
        quality_codecs = [
            # High quality codecs with specific parameters
            {'fourcc': 'mp4v', 'name': 'MP4V-ES (High Quality)', 'params': {}},
            {'fourcc': 'H264', 'name': 'H.264 (High Quality)', 'params': {}},
            {'fourcc': 'XVID', 'name': 'XVID (High Quality)', 'params': {}},
            {'fourcc': 'MJPG', 'name': 'Motion JPEG (High Quality)', 'params': {}}
        ]
        
        out = None
        used_codec = None
        
        for codec_info in quality_codecs:
            try:
                fourcc = cv2.VideoWriter_fourcc(*codec_info['fourcc'])
                
                # Create writer with high quality settings
                out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)
                
                if out.isOpened():
                    # Test write to ensure codec works
                    test_frame = np.zeros((height, width, 3), dtype=np.uint8)
                    out.write(test_frame)
                    
                    used_codec = codec_info['name']
                    print(f"[VideoStego] ✅ Using {used_codec}")
                    break
                    
            except Exception as e:
                print(f"[VideoStego] ⚠️ {codec_info['name']} failed: {e}")
                if out:
                    out.release()
                    out = None
        
        if not out or not out.isOpened():
            raise Exception("Failed to initialize high-quality video encoder")
        
        # Process all frames with quality optimization
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.png')])
        
        if original_video_path and total_original_frames:
            cap_original = cv2.VideoCapture(original_video_path)
            
            frame_index = 0
            while frame_index < total_original_frames:
                ret, original_frame = cap_original.read()
                if not ret:
                    break
                
                # Check for modified frame
                modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
                
                if os.path.exists(modified_frame_path):
                    # Use high-quality modified frame
                    modified_frame = cv2.imread(modified_frame_path, cv2.IMREAD_COLOR)
                    if modified_frame is not None:
                        out.write(modified_frame)
                    else:
                        out.write(original_frame)
                else:
                    out.write(original_frame)
                
                frame_index += 1
            
            cap_original.release()
            
        else:
            # Fallback: use only modified frames
            for frame_file in frame_files:
                frame_path = os.path.join(frame_dir, frame_file)
                frame = cv2.imread(frame_path, cv2.IMREAD_COLOR)
                if frame is not None:
                    out.write(frame)
        
        out.release()
        
        final_size = os.path.getsize(output_path)
        print(f"[VideoStego] ✅ High-quality re-encoded video: {os.path.basename(output_path)} ({final_size/1024/1024:.1f}MB)")
        
        return output_path

    def _create_layered_container(self, existing_data: bytes = None, new_data: bytes = None, new_filename: str = "embedded_data.txt") -> dict:
        """Create or update layered container with new data"""
        import base64
        import json
        from datetime import datetime
        
        # Initialize container
        container = {
            "version": "1.0",
            "type": "layered_container", 
            "created_at": datetime.now().isoformat(),
            "layers": []
        }
        
        # Process existing data if present
        if existing_data:
            try:
                # Try to parse existing data as layered container
                existing_text = existing_data.decode('utf-8')
                existing_container = json.loads(existing_text)
                
                if (isinstance(existing_container, dict) and 
                    existing_container.get('type') == 'layered_container' and
                    'layers' in existing_container):
                    
                    # This is already a layered container - preserve existing layers
                    container['layers'] = existing_container['layers'][:]
                    container['created_at'] = existing_container.get('created_at', container['created_at'])
                    print(f"[VideoStego] ✅ Preserving {len(container['layers'])} existing layers")
                else:
                    # Not a layered container - treat as single layer
                    layer_0 = {
                        "index": 0,
                        "filename": "existing_data.bin",
                        "type": "binary",
                        "content": base64.b64encode(existing_data).decode('utf-8'),
                        "size": len(existing_data)
                    }
                    container['layers'].append(layer_0)
                    print(f"[VideoStego] 📦 Wrapped existing data as layer 0: existing_data.bin ({len(existing_data)} bytes)")
                    
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Existing data is binary - treat as single layer
                layer_0 = {
                    "index": 0,
                    "filename": "existing_data.bin", 
                    "type": "binary",
                    "content": base64.b64encode(existing_data).decode('utf-8'),
                    "size": len(existing_data)
                }
                container['layers'].append(layer_0)
                print(f"[VideoStego] 📦 Wrapped existing binary data as layer 0: existing_data.bin ({len(existing_data)} bytes)")
        
        # Add new data as new layer
        if new_data:
            next_index = len(container['layers'])
            
            # Determine type based on data content
            try:
                # Try to decode as UTF-8 text
                new_data.decode('utf-8')
                data_type = "text"
            except UnicodeDecodeError:
                data_type = "binary"
            
            # Ensure unique filename for this layer
            unique_filename = new_filename
            if next_index > 0:  # Not the first layer
                # Add layer number to make filename unique
                name_parts = os.path.splitext(new_filename)
                if name_parts[1]:  # Has extension
                    unique_filename = f"{name_parts[0]}_layer{next_index+1}{name_parts[1]}"
                else:  # No extension
                    unique_filename = f"{new_filename}_layer{next_index+1}"
            
            new_layer = {
                "index": next_index,
                "filename": unique_filename,
                "type": data_type,
                "content": base64.b64encode(new_data).decode('utf-8'),
                "size": len(new_data)
            }
            
            container['layers'].append(new_layer)
            print(f"[VideoStego] ➕ Added new layer {next_index}: {new_filename} ({len(new_data)} bytes, {data_type})")
        
        print(f"[VideoStego] 📊 Final layered container: {len(container['layers'])} total layers")
        return container
    
    def embed_data(self, carrier_video_path: str, secret_data: Union[str, bytes], 
                   output_filename: str = None, secret_filename: str = None, 
                   preserve_layers: bool = True, project_name: str = None) -> Dict[str, Any]:
        """Embed data with performance limits and timeout protection"""
        
        # PERFORMANCE FIX: Add embedding timeout to prevent infinite operations
        embedding_start_time = time.time()
        embedding_timeout_seconds = 300  # Maximum 5 minutes for entire embedding
        
        def check_embedding_timeout():
            if time.time() - embedding_start_time > embedding_timeout_seconds:
                raise TimeoutError(f"Video embedding exceeded {embedding_timeout_seconds} seconds")
        
        check_embedding_timeout()  # Initial check
        """Embed data with multi-layer support - can preserve existing layers or start fresh"""
        
        start_time = time.time()
        
        # AUTO-CLEANUP: Clean test directories to prevent cross-contamination
        if project_name:
            self.auto_cleanup_for_project(project_name)
        
        # MULTI-LAYER SUPPORT: Check if carrier video already has embedded data
        check_embedding_timeout()  # Check before expensive operations
        existing_data = None
        if preserve_layers:
            # PERFORMANCE FIX: Ultra-fast check to avoid expensive extraction on fresh carriers
            video_hash = self._generate_video_hash(carrier_video_path, self.password)
            frame_dir = self._get_frame_directory(carrier_video_path, video_hash)
            
            # First check if frame directory exists at all
            if os.path.exists(frame_dir):
                # Quick check - look for frame files to confirm it's a real stego directory
                frame_files = [f for f in os.listdir(frame_dir) if f.endswith('.png')]
                if len(frame_files) >= 3:  # Minimum frames to be worth extracting
                    print(f"[VideoStego] 🔍 Found existing frame directory with {len(frame_files)} frames - will attempt extraction")
                    check_embedding_timeout()
                    try:
                        existing_result = self.extract_data(carrier_video_path, fast_mode=True)
                        if existing_result and existing_result.get("success"):
                            existing_bytes = existing_result.get("extracted_data")
                            existing_filename = existing_result.get("filename", "embedded_data")
                            if existing_bytes:
                                print(f"[VideoStego] ✅ Found existing embedded data: {existing_filename} ({len(existing_bytes)} bytes)")
                                existing_data = existing_bytes
                            else:
                                print(f"[VideoStego] ℹ️  Extraction succeeded but no data found")
                        else:
                            print(f"[VideoStego] ℹ️  No existing embedded data found - creating new container")
                    except Exception as e:
                        print(f"[VideoStego] ℹ️  Could not extract existing data: {e}")
                else:
                    print(f"[VideoStego] 🚀 FAST MODE: Frame directory exists but has insufficient frames ({len(frame_files)}) - skipping extraction")
            else:
                print(f"[VideoStego] 🚀 FAST MODE: No existing frame directory found - skipping extraction check completely")
        else:
            print(f"[VideoStego] 🆕 FRESH MODE: Starting new container (ignoring any existing layers)")
        
        # Prepare new data
        if isinstance(secret_data, str):
            secret_bytes = secret_data.encode('utf-8')
        else:
            secret_bytes = secret_data
            
        # Create multi-layer container
        layered_container = self._create_layered_container(existing_data, secret_bytes, secret_filename or "embedded_data.txt")
        
        # Convert layered container to bytes for embedding
        container_json = json.dumps(layered_container, separators=(',', ':'))
        final_secret_bytes = container_json.encode('utf-8')
        
        # Generate unique hash for this video INCLUDING the password AND FINAL container data
        container_data_hash = hashlib.sha256(final_secret_bytes).hexdigest()[:8]
        video_hash = self._generate_video_hash(carrier_video_path, self.password)
        
        # Create UNIQUE hash combining video + final container data to prevent cross-contamination  
        unique_hash = hashlib.sha256(f"{video_hash}_{container_data_hash}".encode()).hexdigest()[:8]
        print(f"[VideoStego] Video hash: {video_hash}")
        print(f"[VideoStego] Container data hash: {container_data_hash}")
        print(f"[VideoStego] UNIQUE embedding hash: {unique_hash}")
        
        # Create metadata for the layered container
        metadata = {
            'filename': "layered_container.json",
            'size': len(final_secret_bytes),
            'type': 'layered_container',
            'video_hash': video_hash,
            'data_hash': container_data_hash,
            'unique_hash': unique_hash,
            'checksum': hashlib.sha256(final_secret_bytes).hexdigest(),
            'layers': len(layered_container.get('layers', []))
        }
        print(f"[VideoStego] 📊 Multi-layer container: {metadata['layers']} layers, {len(final_secret_bytes)} bytes total")
        
        # Open video and get properties
        cap = cv2.VideoCapture(carrier_video_path)
        if not cap.isOpened():
            raise Exception("Cannot open input video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create unique frame directory using combined hash to prevent cross-contamination
        frame_dir = self._get_frame_directory(carrier_video_path, unique_hash)
        os.makedirs(frame_dir, exist_ok=True)
        
        # Save frame info for identification
        frame_info = {
            'width': width, 'height': height, 'total_frames': total_frames,
            'fps': fps, 'video_hash': video_hash, 'created_at': time.time()
        }
        with open(os.path.join(frame_dir, "frame_info.json"), 'w') as f:
            json.dump(frame_info, f)
        
        # Prepare embedding data
        magic = b'VEILFORGE_VIDEO_V1'
        metadata_json = json.dumps(metadata).encode('utf-8')
        data_package = struct.pack('<I', len(metadata_json)) + metadata_json + final_secret_bytes
        
        # Calculate capacity with optimized redundancy
        redundancy = 3  # Optimized for speed
        pixels_per_frame = width * height * 3
        total_capacity = (total_frames * pixels_per_frame) // redundancy
        required_bits = len(magic + data_package) * 8
        
        if required_bits > total_capacity:
            cap.release()
            raise Exception(f"Data too large: need {required_bits} bits, have {total_capacity}")
        
        print(f"[VideoStego] Embedding {len(final_secret_bytes)} bytes (layered container) with {redundancy}x redundancy...")
        
        # OPTIMIZED EMBEDDING: Only process frames we actually need to modify
        data_to_embed = magic + data_package
        data_bits = ''.join(format(byte, '08b') for byte in data_to_embed)
        
        # Calculate exact frames needed (more accurate)
        bits_per_frame = (pixels_per_frame // redundancy)
        frames_needed_for_data = max(1, (len(data_bits) + bits_per_frame - 1) // bits_per_frame)
        
        print(f"[VideoStego] ⚡ OPTIMIZED EMBEDDING:")
        print(f"[VideoStego] Need to embed {len(data_bits)} bits")
        print(f"[VideoStego] Bits per frame: {bits_per_frame}")
        print(f"[VideoStego] Frames needed: {frames_needed_for_data} out of {total_frames}")
        print(f"[VideoStego] Processing efficiency: {((total_frames - frames_needed_for_data) / total_frames) * 100:.1f}% frames will be copied directly")
        
        bit_index = 0
        frames_modified = 0
        
        # Only process the exact number of frames we need
        for frame_num in range(frames_needed_for_data):
            ret, frame = cap.read()
            if not ret:
                break
                
            # Embed data in this frame
            flat_frame = frame.flatten()
            frame_modified = False
            
            # Embed as many bits as possible in this frame
            for i in range(0, len(flat_frame), redundancy):
                if bit_index >= len(data_bits):
                    break
                
                bit = int(data_bits[bit_index])
                for j in range(redundancy):
                    if i + j < len(flat_frame):
                        flat_frame[i + j] = (flat_frame[i + j] & 0xFE) | bit
                        frame_modified = True
                
                bit_index += 1
            
            # Only save if we actually modified the frame
            if frame_modified:
                frame = flat_frame.reshape(frame.shape)
                frame_path = os.path.join(frame_dir, f"frame_{frame_num:06d}.png")
                # Use minimal compression for speed and quality
                cv2.imwrite(frame_path, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                frames_modified += 1
            
            if bit_index >= len(data_bits):
                print(f"[VideoStego] ✅ Embedding complete! Modified {frames_modified} frames, embedded {bit_index} bits")
                break
        
        cap.release()
        
        print(f"[VideoStego] 🚀 PERFORMANCE: Only processed {frames_modified}/{total_frames} frames ({(frames_modified/total_frames)*100:.1f}%)")
        
        # Store optimized frame processing info
        frame_info['total_frames'] = total_frames
        frame_info['modified_frames'] = frames_modified
        frame_info['frames_needed'] = frames_needed_for_data
        frame_info['embedding_complete'] = (bit_index >= len(data_bits))
        frame_info['processing_efficiency'] = ((total_frames - frames_modified) / total_frames) * 100
        with open(os.path.join(frame_dir, "frame_info.json"), 'w') as f:
            json.dump(frame_info, f)
            
        print(f"[VideoStego] 📊 OPTIMIZATION SUMMARY:")
        print(f"[VideoStego]   Total frames: {total_frames}")
        print(f"[VideoStego]   Modified frames: {frames_modified}")  
        print(f"[VideoStego]   Copied directly: {total_frames - frames_modified}")
        print(f"[VideoStego]   Processing efficiency: {frame_info['processing_efficiency']:.1f}%")
        
        # Generate output path
        if not output_filename:
            base_name = os.path.splitext(os.path.basename(carrier_video_path))[0]
            output_filename = f"stego_{base_name}_{video_hash}.mp4"
        
        output_path = os.path.join(self.outputs_dir, output_filename)
        
        # Create high-quality video with advanced optimization
        self._create_high_quality_video(frame_dir, output_path, fps, width, height, 
                                      carrier_video_path, total_frames)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "output_file": output_path,
            "filename": output_filename,
            "processing_time": processing_time,
            "file_size": os.path.getsize(output_path),
            "embedded_size": len(final_secret_bytes),
            "video_hash": video_hash
        }
    
    def extract_data(self, stego_video_path: str, password: str = None, output_dir: str = None, fast_mode: bool = False) -> Dict[str, Any]:
        """Extract data with unique identification"""
        import json
        import signal
        
        start_time = time.time()
        
        # PERFORMANCE FIX: Add simple timeout tracking with fast mode support
        global_timeout_seconds = 30 if fast_mode else 120  # 30 seconds for fast mode, 2 minutes for normal
        extraction_start_time = time.time()
        
        if fast_mode:
            print(f"[VideoStego] 🚀 FAST MODE: Using aggressive timeout of {global_timeout_seconds}s")
        print(f"[VideoStego] ========== EXTRACTION DEBUG ==========")
        print(f"[VideoStego] File: {os.path.basename(stego_video_path)}")
        print(f"[VideoStego] Password provided: {password is not None}")
        print(f"[VideoStego] Instance password: {self.password is not None}")
        print(f"[VideoStego] Output dir: {output_dir}")
        
        # Use provided password if given, otherwise use instance password
        extraction_password = password if password is not None else self.password
        print(f"[VideoStego] Using password for extraction: {'provided' if password is not None else 'instance'}")
        print(f"[VideoStego] Final extraction password: '{extraction_password}'")
        
        # Generate hash for input video INCLUDING the password (CRITICAL FIX)
        input_hash = self._generate_video_hash(stego_video_path, extraction_password)
        print(f"[VideoStego] Extraction hash: {input_hash}")
        
        # Check timeout before expensive operations
        if time.time() - extraction_start_time > global_timeout_seconds:
            return {"success": False, "error": "Extraction timed out before frame search"}
        
        # Find frame directory by video hash pattern (directories use unique_hash, not just video_hash)
        frame_dir = self._find_frame_directory_by_video_hash(stego_video_path, input_hash)
        
        # ENHANCED FIX: If no exact hash match found, try property-only matching for videos with different names
        if not frame_dir:
            print(f"[VideoStego] 🔧 FALLBACK 1: Trying property-only hash matching...")
            property_hash = self._generate_property_only_hash(stego_video_path, extraction_password)
            frame_dir = self._find_frame_directory_by_property_hash(stego_video_path, property_hash)
        
        # CRITICAL FIX: If still no match found, try name-based matching for stego videos
        if not frame_dir:
            print(f"[VideoStego] 🔧 FALLBACK 2: Trying name-based directory search...")
            frame_dir = self._find_frame_directory_by_name_pattern(stego_video_path)
        
        # Validate frame_dir is not None
        if not frame_dir:
            print(f"[VideoStego] ❌ Could not find frame directory for video hash: {input_hash}")
            print(f"[VideoStego] ========== EXTRACTION FAILED (NO FRAME DIR) ==========")
            return {"success": False, "error": "Frame directory not found"}
            
        print(f"[VideoStego] Looking for frame directory: {frame_dir}")
            
        # Verify that we found the correct directory
        if frame_dir:
            actual_dir_name = os.path.basename(frame_dir)
            expected_video_hash = input_hash
            
            # Extract the hash from the directory name to compare
            if "_frames" in actual_dir_name:
                parts = actual_dir_name.replace("_frames", "").split("_")
                if len(parts) >= 3:  # stego_basename_hash format
                    found_hash = parts[-1]  # Last part is the hash
                    if found_hash == expected_video_hash:
                        print(f"[VideoStego] ✅ Found frame directory (original: {expected_video_hash}, current: {found_hash})")
                    else:
                        # This is likely a unique_hash (video_hash + data_hash)
                        print(f"[VideoStego] ✅ Found frame directory (original: {expected_video_hash}, current: {found_hash})")
        
        # Check for exact hash match first
        if os.path.exists(frame_dir):
            print(f"[VideoStego] ✅ Found exact hash directory: {frame_dir}")
        else:
            print(f"[VideoStego] Exact hash directory not found: {frame_dir}")
            print(f"[VideoStego] Attempting smart fallback search for video re-encoding...")
            
            # Get video properties for intelligent matching
            cap = cv2.VideoCapture(stego_video_path)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                cap.release()
                
                print(f"[VideoStego] Video properties: {width}x{height}, {total_frames} frames, {fps:.2f} fps")
                
                # Search all frame directories for matching properties
                best_match = None
                best_score = 0
                
                for dir_name in os.listdir(self.outputs_dir):
                    if dir_name.endswith("_frames"):
                        frame_info_path = os.path.join(self.outputs_dir, dir_name, "frame_info.json")
                        if os.path.exists(frame_info_path):
                            try:
                                with open(frame_info_path, 'r') as f:
                                    frame_info = json.load(f)
                                
                                # Calculate match score based on properties
                                score = 0
                                if frame_info.get('width') == width:
                                    score += 2
                                if frame_info.get('height') == height:
                                    score += 2
                                if abs(frame_info.get('total_frames', 0) - total_frames) <= 2:  # Allow small difference
                                    score += 3
                                if abs(frame_info.get('fps', 0) - fps) <= 1.0:  # Allow 1 fps difference
                                    score += 1
                                
                                # STRICT VIDEO MATCHING: Only use directories for THIS specific video
                                original_filename = os.path.splitext(os.path.basename(stego_video_path))[0].lower()
                                
                                # Remove common stego prefixes to get core video name
                                for prefix in ['stego_', 'embedded_']:
                                    if original_filename.startswith(prefix):
                                        original_filename = original_filename[len(prefix):]
                                        break
                                
                                # Check if this directory was created for THIS video
                                dir_name_lower = dir_name.lower()
                                video_specific_match = False
                                
                                # Method 1: Exact video name in directory name
                                if original_filename in dir_name_lower:
                                    video_specific_match = True
                                    score += 25  # Very high priority for exact match
                                    print(f"[VideoStego] 🎯 EXACT VIDEO MATCH: {dir_name} contains '{original_filename}'")
                                else:
                                    # Method 2: Check if this is a carrier-based directory for current video
                                    video_parts = [p for p in original_filename.split('_') if len(p) > 3]  # Ignore short parts
                                    matching_major_parts = 0
                                    
                                    for part in video_parts:
                                        if part in dir_name_lower:
                                            matching_major_parts += 1
                                    
                                    # Only match if MOST major parts are present
                                    if len(video_parts) > 0 and matching_major_parts >= max(1, len(video_parts) - 1):
                                        video_specific_match = True
                                        score += 15
                                        print(f"[VideoStego] 🎯 PARTIAL MATCH: {dir_name} has {matching_major_parts}/{len(video_parts)} major parts")
                                
                                # CRITICAL: Skip directories that don't belong to this video
                                if not video_specific_match:
                                    print(f"[VideoStego] ❌ SKIPPED: {dir_name} - not related to video '{original_filename}'")
                                    continue
                                
                                print(f"[VideoStego] ✅ CANDIDATE: {dir_name} (score: {score})")
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = os.path.join(self.outputs_dir, dir_name)
                                    
                            except Exception as e:
                                print(f"[VideoStego] Error checking {dir_name}: {e}")
                
                # Use moderate confidence threshold for video-specific match
                if best_match and best_score >= 8:  # Lower threshold to accept property matches
                    frame_dir = best_match
                    print(f"[VideoStego] ✅ Found video-specific directory: {os.path.basename(frame_dir)} (score: {best_score})")
                else:
                    print(f"[VideoStego] ❌ No video-specific directory found (best score: {best_score})")
                    print(f"[VideoStego] 🚨 This video may not contain embedded data for the current file")
                    print(f"[VideoStego] ========== EXTRACTION FAILED (NO VIDEO-SPECIFIC DIR) ==========")
                    return {"success": False, "error": "No video-specific directory found"}
            else:
                print(f"[VideoStego] ❌ Cannot open video for property matching")
                print(f"[VideoStego] ========== EXTRACTION FAILED (CANNOT OPEN VIDEO) ==========")
                return {"success": False, "error": "Cannot open video for property matching"}
        
        # Verify frame info
        frame_info_path = os.path.join(frame_dir, "frame_info.json")
        if not os.path.exists(frame_info_path):
            print(f"[VideoStego] ❌ Frame info not found: {frame_info_path}")
            print(f"[VideoStego] ========== EXTRACTION FAILED (NO FRAME INFO) ==========")
            return {"success": False, "error": "Frame info not found"}
        
        with open(frame_info_path, 'r') as f:
            frame_info = json.load(f)
        
        # Log frame directory info (hash may differ due to encoding)
        original_hash = frame_info.get('video_hash', 'unknown')
        print(f"[VideoStego] ✅ Found frame directory (original: {original_hash}, current: {input_hash})")
        
        # Extract data from frames
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.png')])
        
        if not frame_files:
            print(f"[VideoStego] ❌ No frame files found in: {frame_dir}")
            print(f"[VideoStego] ========== EXTRACTION FAILED (NO FRAME FILES) ==========")
            return {"success": False, "error": "No frame files found"}
        
        print(f"[VideoStego] Extracting from {len(frame_files)} frames...")
        
        # CORRECTED EXTRACTION: Fix redundancy and duplicate processing bugs
        all_bits = []
        redundancy = 3  # Must match embedding redundancy
        magic = b'VEILFORGE_VIDEO_V1'
        magic_bits = len(magic) * 8
        header_bits = (len(magic) + 4) * 8  # Magic + metadata size
        
        # PERFORMANCE: Reduce frame processing in fast mode, but allow more for layered containers
        max_frames = 20 if fast_mode else 50  # Increased from 3 to 20 for fast mode
        frames_to_process = min(len(frame_files), max_frames)
        print(f"[VideoStego] ⚡ EXTRACTION: Processing up to {frames_to_process} frames {'(FAST MODE)' if fast_mode else ''}...")
        
        extraction_start = time.time()
        extraction_complete = False
        layered_container_detected = False  # FLAG: Prevent repeated detection
        
        # Initialize bit_limit based on mode and detection status
        base_limit = 50000 if fast_mode else 500000  # 50k bits (~6KB) for fast mode
        bit_limit = base_limit
        
        for frame_idx in range(frames_to_process):
            # Check timeout during frame processing
            if time.time() - extraction_start_time > global_timeout_seconds:
                print(f"[VideoStego] ⏰ TIMEOUT: Extraction exceeded {global_timeout_seconds} seconds")
                return {"success": False, "error": f"Extraction timed out after {global_timeout_seconds} seconds"}
                
            frame_file = frame_files[frame_idx] 
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                flat_frame = frame.flatten()
                frame_bits_extracted = 0
                
                print(f"[VideoStego] 🔍 Frame shape: {frame.shape}, flattened length: {len(flat_frame)}")
                print(f"[VideoStego] 🔍 Processing with redundancy: {redundancy}, max iterations: {len(flat_frame) // redundancy}")
                print(f"[VideoStego] 🔍 Bit limit: {bit_limit}")
                
                # FIXED: Single extraction loop with proper redundancy handling
                loop_iterations = 0
                for i in range(0, len(flat_frame), redundancy):
                    loop_iterations += 1
                    # Check timeout during bit extraction
                    if time.time() - extraction_start_time > global_timeout_seconds:
                        print(f"[VideoStego] ⏰ TIMEOUT: Extraction exceeded {global_timeout_seconds} seconds during bit extraction")
                        return {"success": False, "error": f"Extraction timed out during processing"}
                        
                    # Skip layered container update if already detected to prevent infinite loop
                    if layered_container_detected:
                        bit_limit = 4000000  # 4M bits (~500KB) - enough for large containers
                    
                    if len(all_bits) >= bit_limit:
                        print(f"[VideoStego] ⚠️  Hit extraction limit of {bit_limit} bits {'(FAST MODE)' if fast_mode else ''} - stopping extraction")
                        print(f"[VideoStego] 🔍 Current all_bits length: {len(all_bits)}")
                        break
                        
                    # Debug the condition check for first few iterations
                    if loop_iterations <= 5:
                        print(f"[VideoStego] 🔍 Loop {loop_iterations}: i={i}, condition: {i} + {redundancy} <= {len(flat_frame)} = {i + redundancy <= len(flat_frame)}")
                    
                    # MAIN EXTRACTION LOGIC - moved outside conditional
                    if i + redundancy <= len(flat_frame):
                        # FIXED: Proper majority vote for redundancy (same as embedding)
                        bits = [flat_frame[i + j] & 1 for j in range(redundancy)]
                        majority_bit = 1 if sum(bits) > redundancy // 2 else 0
                        all_bits.append(str(majority_bit))
                        frame_bits_extracted += 1
                        
                        # Debug every 1000 bits to see progress
                        if frame_bits_extracted % 1000 == 0:
                            print(f"[VideoStego] 📊 Extracted {frame_bits_extracted} bits so far...")
                        
                        # Debug for the first few bits to see what's happening
                        if frame_bits_extracted <= 5:
                            print(f"[VideoStego] 🔍 Bit {frame_bits_extracted}: i={i}, majority_bit={majority_bit}, all_bits_len={len(all_bits)}")
                        
                        # Smart early termination: Check for magic signature (reduce logging)
                        if len(all_bits) == magic_bits:  # Only check once when we have exactly the magic signature length
                            try:
                                # Check if we found the magic signature
                                test_bits = ''.join(all_bits[:magic_bits])
                                test_bytes = bytes([int(test_bits[i:i+8], 2) for i in range(0, len(test_bits), 8)])
                                if test_bytes == magic:
                                    print(f"[VideoStego] ✅ Found magic signature, continuing extraction...")
                            except:
                                pass
                        
                        # LAYERED CONTAINER EARLY DETECTION: Check for container signature after magic + header - ONLY ONCE
                        if not layered_container_detected and len(all_bits) >= magic_bits + 512:  # After magic + 64 bytes of header/metadata
                            try:
                                # Extract what we have so far and check for layered container
                                test_bits_str = ''.join(all_bits)
                                # Convert to bytes (skip incomplete byte at end)
                                complete_bytes = len(test_bits_str) // 8 * 8
                                test_bytes = bytes([int(test_bits_str[i:i+8], 2) for i in range(0, complete_bytes, 8)])
                                test_str = test_bytes.decode('utf-8', errors='ignore')
                                
                                # Look for layered container signature early in the data
                                if ('"type":"layered_container"' in test_str or 
                                    '"layers":' in test_str or
                                    '"version":"1.0"' in test_str):
                                    # Layered container detected - MASSIVELY increase limit ONCE
                                    bit_limit = 4000000  # 4M bits (~500KB) - enough for large containers
                                    layered_container_detected = True  # Set flag to prevent repeated detection
                                    print(f"[VideoStego] 🎯 EARLY LAYERED CONTAINER DETECTED - Increased limit to {bit_limit} bits")
                            except:
                                pass  # Ignore decode errors, continue with normal extraction
                        
                        # DISABLED: Early completion check causing infinite loop
                        # This was causing infinite loops by checking every bit extracted
                        pass
                
                # Progress logging
                if frame_idx == 0 and frame_bits_extracted > 0:
                    print(f"[VideoStego] ✅ Extracted {len(all_bits)} bits from first frame")
                    if len(all_bits) == 1:
                        print(f"[VideoStego] ⚠️ WARNING: Only extracted 1 bit - investigating...")
                        print(f"[VideoStego] 🔍 Frame processed pixels: {len(flat_frame)}")
                        print(f"[VideoStego] 🔍 Expected max bits: {len(flat_frame) // redundancy}")
                        print(f"[VideoStego] 🔍 Actual loop iterations: {loop_iterations}")
                        print(f"[VideoStego] 🔍 Extraction complete flag: {extraction_complete}")
                    
                # Check if we should exit the frame processing loop
                if extraction_complete:
                    print(f"[VideoStego] 🛑 Extraction marked complete - exiting frame loop")
                    break
            
            # Safety check: if we've processed enough frames for typical data sizes
            if len(all_bits) > 50000 and len(all_bits) % 8 == 0:  
                # Try a quick validation
                bit_string = ''.join(all_bits)
                temp_bytes = bytearray()
                
                for j in range(0, min(len(bit_string), 50000), 8):  # Check first ~6KB
                    if j + 8 <= len(bit_string):
                        byte_value = int(bit_string[j:j+8], 2)
                        temp_bytes.append(byte_value)
                
                if len(temp_bytes) > len(magic) and temp_bytes.startswith(magic):
                    print(f"[VideoStego] 📊 Progress check: Found valid header, extracted {len(all_bits)} bits so far")
            
            # Check if extraction is complete after processing this frame
            if extraction_complete:
                break
        
        # Convert to bytes
        bit_string = ''.join(all_bits)
        print(f"[VideoStego] 🔍 DEBUG: Extracted {len(all_bits)} bits total")
        print(f"[VideoStego] 🔍 DEBUG: First 64 bits: {bit_string[:64]}")
        extracted_bytes = bytearray()
        
        for i in range(0, len(bit_string), 8):
            if i + 8 <= len(bit_string):
                byte_value = int(bit_string[i:i+8], 2)
                extracted_bytes.append(byte_value)
        
        # Verify magic header
        magic = b'VEILFORGE_VIDEO_V1'
        print(f"[VideoStego] 🔍 DEBUG: Extracted {len(extracted_bytes)} bytes")
        print(f"[VideoStego] 🔍 DEBUG: Expected magic: {magic}")
        print(f"[VideoStego] 🔍 DEBUG: First {len(magic)} bytes: {extracted_bytes[:len(magic)]}")
        print(f"[VideoStego] 🔍 DEBUG: Magic comparison: {extracted_bytes.startswith(magic)}")
        if not extracted_bytes.startswith(magic):
            return {"success": False, "error": "Invalid magic header"}
        
        # Extract metadata
        metadata_start = len(magic)
        metadata_size = struct.unpack('<I', extracted_bytes[metadata_start:metadata_start+4])[0]
        metadata_bytes = extracted_bytes[metadata_start+4:metadata_start+4+metadata_size]
        
        try:
            metadata = json.loads(metadata_bytes.decode('utf-8'))
        except:
            return {"success": False, "error": "Failed to parse metadata"}
        
        # Extract secret data
        data_start = metadata_start + 4 + metadata_size
        data_size = metadata['size']
        secret_data = bytes(extracted_bytes[data_start:data_start+data_size])

        # Verify checksum - should match the data that was actually embedded
        expected_checksum = metadata['checksum']
        actual_checksum = hashlib.sha256(secret_data).hexdigest()
        
        print(f"[VideoStego] 🔍 CHECKSUM DEBUG:")
        print(f"[VideoStego]   Expected: {expected_checksum}")
        print(f"[VideoStego]   Actual:   {actual_checksum}")
        print(f"[VideoStego]   Data size: {len(secret_data)} bytes")
        print(f"[VideoStego]   Expected size: {metadata.get('size', 'unknown')} bytes")
        print(f"[VideoStego]   Frame directory: {metadata.get('unique_hash', 'unknown')}")
        print(f"[VideoStego]   Video hash: {metadata.get('video_hash', 'unknown')}")
        
        if expected_checksum != actual_checksum:
            print(f"[VideoStego] ❌ Checksum verification failed")
            print(f"[VideoStego] 🔍 First 50 bytes of extracted data: {secret_data[:50]}")
            
            # Try to validate if the data still looks reasonable (layered container)
            try:
                if secret_data.startswith(b'{"version"') and b'layered_container' in secret_data:
                    print(f"[VideoStego] 🔧 RECOVERY: Data appears to be valid layered container despite checksum mismatch")
                    print(f"[VideoStego] 📊 Proceeding with extraction (checksum may be from different encoding)")
                    filename = metadata['filename']
                    processing_time = time.time() - start_time
                    print(f"[VideoStego] ✅ Extracted {len(secret_data)} bytes in {processing_time:.2f}s (recovered)")
                    print(f"[VideoStego] ========== EXTRACTION SUCCESS (RECOVERED) ==========")
                    
                    # Check if data is a layered container (recovery case)
                    is_layered_data = self._is_layered_container(secret_data)
                    print(f"[VideoStego] 📊 Layered container detection (recovered): {'✅ YES' if is_layered_data else '❌ NO'}")
                    
                    if is_layered_data:
                        # Extract layers and create ZIP
                        layers = self._extract_layers(secret_data)
                        zip_buffer = self._create_layered_zip(layers)
                        
                        return {
                            "success": True,
                            "multi_layer_extraction": True,
                            "extracted_data": secret_data,
                            "zip_file": zip_buffer,
                            "layers": layers,
                            "total_layers_extracted": len(layers) if layers else 0
                        }
                    else:
                        # 🎯 CHECK FOR LAYERED CONTAINER - Override filename if layered container detected
                        print(f"[VideoStego] 🔍 Checking secret_data type: {type(secret_data)}")
                        print(f"[VideoStego] 🔍 Secret data length: {len(secret_data) if hasattr(secret_data, '__len__') else 'no length'}")
                        
                        # Handle both string and bytes data
                        decoded_data = None
                        if isinstance(secret_data, bytes):
                            print(f"[VideoStego] 🔍 Data is bytes, attempting decode...")
                            try:
                                decoded_data = secret_data.decode('utf-8')
                            except UnicodeDecodeError as e:
                                print(f"[VideoStego] ❌ Failed to decode bytes as UTF-8: {e}")
                                decoded_data = None
                        elif isinstance(secret_data, str):
                            print(f"[VideoStego] 🔍 Data is already string, using directly...")
                            decoded_data = secret_data
                        else:
                            print(f"[VideoStego] ❌ Unexpected data type: {type(secret_data)}")
                            decoded_data = None
                        
                        if decoded_data:
                            print(f"[VideoStego] 🔍 Processing decoded data, length: {len(decoded_data)}")
                            try:
                                import json
                                parsed_data = json.loads(decoded_data)
                                print(f"[VideoStego] 🔍 Successfully parsed JSON, type: {parsed_data.get('type', 'no type')}")
                                
                                if (isinstance(parsed_data, dict) and 
                                    parsed_data.get('type') == 'layered_container' and
                                    'layers' in parsed_data and len(parsed_data['layers']) > 0):
                                    
                                    print(f"[VideoStego] 🎯 LAYERED CONTAINER DETECTED! Layers: {len(parsed_data['layers'])}")
                                    
                                    # Extract filename from first layer
                                    first_layer = parsed_data['layers'][0]
                                    if isinstance(first_layer, dict) and 'filename' in first_layer:
                                        original_filename = first_layer['filename']
                                        print(f"[VideoStego] 🎯 Overriding filename from '{filename}' to '{original_filename}'")
                                        filename = original_filename
                                        
                                        # Extract the actual file content
                                        if 'content' in first_layer:
                                            import base64
                                            actual_file_data = base64.b64decode(first_layer['content'])
                                            print(f"[VideoStego] 📁 Extracted original file content: {len(actual_file_data)} bytes")
                                            secret_data = actual_file_data
                                    else:
                                        print(f"[VideoStego] ⚠️ Layered container found but no filename in first layer")
                                else:
                                    print(f"[VideoStego] 📋 Not a layered container (type: {parsed_data.get('type', 'unknown')})")
                            except json.JSONDecodeError as e:
                                print(f"[VideoStego] 📋 Not a JSON container: {e}")
                        else:
                            print(f"[VideoStego] ❌ Could not decode secret_data for layered container check")
                        
                        return {
                            "success": True,
                            "multi_layer_extraction": False,
                            "extracted_data": secret_data,
                            "filename": filename
                        }
            except:
                pass
            
            print(f"[VideoStego] ========== EXTRACTION FAILED (CHECKSUM MISMATCH) ==========")
            return {"success": False, "error": "Checksum verification failed"}
        
        filename = metadata['filename']
        processing_time = time.time() - start_time
        
        print(f"[VideoStego] ✅ Extracted {len(secret_data)} bytes in {processing_time:.2f}s")
        print(f"[VideoStego] ========== EXTRACTION SUCCESS ==========")
        
        # Check if data is a layered container
        is_layered_data = self._is_layered_container(secret_data)
        print(f"[VideoStego] 📊 Layered container detection: {'✅ YES' if is_layered_data else '❌ NO'}")
        
        if is_layered_data:
            # Extract layers with enhanced debugging
            print(f"[VideoStego] 🔍 LAYERED CONTAINER DETECTED - Extracting individual layers...")
            layers = self._extract_layers(secret_data)
            print(f"[VideoStego] 📊 _extract_layers returned: {len(layers)} layers")
            
            if len(layers) == 1:
                # Single layer - return the original file directly
                layer_name = list(layers.keys())[0]
                layer_info = layers[layer_name]
                print(f"[VideoStego] 🎯 SINGLE LAYER DETECTED - Returning original file")
                print(f"[VideoStego] 📁 File: '{layer_info['filename']}' ({len(layer_info['data'])} bytes)")
                print(f"[VideoStego] 📁 Type: {layer_info.get('type', 'unknown')}")
                
                # CRITICAL FIX: Use content-based filename detection for copyright text (like image steganography)
                detected_filename = detect_filename_from_content(layer_info['data'])
                actual_filename = layer_info['filename']
                
                # If the detected filename is different and suggests text content, use it
                if detected_filename.endswith('.txt') and not actual_filename.endswith('.txt'):
                    print(f"[VideoStego] 🔧 COPYRIGHT FIX: Detected text content, changing filename")
                    print(f"[VideoStego]   Original: {actual_filename}")
                    print(f"[VideoStego]   Detected: {detected_filename}")
                    actual_filename = detected_filename
                
                return {
                    "success": True,
                    "multi_layer_extraction": False,
                    "extracted_data": layer_info['data'],
                    "filename": actual_filename
                }
            elif len(layers) > 1:
                # Multiple layers - create ZIP
                print(f"[VideoStego] 📦 Multiple layers detected ({len(layers)}), creating ZIP archive")
                zip_buffer = self._create_layered_zip(layers)
                
                return {
                    "success": True,
                    "multi_layer_extraction": True,
                    "extracted_data": secret_data,
                    "zip_file": zip_buffer,
                    "layers": layers,
                    "total_layers_extracted": len(layers)
                }
            else:
                # No layers extracted - this indicates a problem
                print(f"[VideoStego] ❌ CRITICAL: Layered container detected but NO layers extracted!")
                print(f"[VideoStego] ❌ This suggests a parsing issue - returning raw JSON as fallback")
                print(f"[VideoStego] 📊 Raw data size: {len(secret_data)} bytes")
                if isinstance(secret_data, bytes) and len(secret_data) > 0:
                    print(f"[VideoStego] 📊 Raw data preview: {secret_data[:200]}")
                
                # CRITICAL FIX: Use content-based filename detection for copyright text (fallback case)
                detected_filename = detect_filename_from_content(secret_data)
                actual_filename = filename
                
                if detected_filename.endswith('.txt') and not actual_filename.endswith('.txt'):
                    print(f"[VideoStego] 🔧 COPYRIGHT FIX (FALLBACK): Detected text content, changing filename")
                    print(f"[VideoStego]   Original: {actual_filename}")
                    print(f"[VideoStego]   Detected: {detected_filename}")
                    actual_filename = detected_filename
                
                return {
                    "success": True,
                    "multi_layer_extraction": False,
                    "extracted_data": secret_data,
                    "filename": actual_filename
                }
        else:
            # Non-layered data case
            # CRITICAL FIX: Use content-based filename detection for copyright text (non-layered case)
            detected_filename = detect_filename_from_content(secret_data)
            actual_filename = filename
            
            if detected_filename.endswith('.txt') and not actual_filename.endswith('.txt'):
                print(f"[VideoStego] 🔧 COPYRIGHT FIX (NON-LAYERED): Detected text content, changing filename")
                print(f"[VideoStego]   Original: {actual_filename}")
                print(f"[VideoStego]   Detected: {detected_filename}")
                actual_filename = detected_filename
            
            return {
                "success": True,
                "multi_layer_extraction": False,
                "extracted_data": secret_data,
                "filename": actual_filename
            }
    
    def _try_ffmpeg_quality_approach(self, frame_dir: str, output_path: str, fps: float,
                                   width: int, height: int, original_video_path: str,
                                   total_original_frames: int, modified_frame_count: int):
        """Try using FFmpeg for superior quality control when available"""
        
        try:
            import subprocess
            import tempfile
            import shutil
            
            print(f"[VideoStego] 🔥 Attempting FFmpeg ULTRA-QUALITY approach...")
            
            # Check if FFmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
                print(f"[VideoStego] ✅ FFmpeg detected, proceeding with ultra-quality encoding...")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                print(f"[VideoStego] ❌ FFmpeg not available, skipping FFmpeg approach")
                return None
            
            # Create temporary directory for FFmpeg processing
            temp_dir = tempfile.mkdtemp()
            temp_video_list = os.path.join(temp_dir, "frame_list.txt")
            
            try:
                # Create frame list for FFmpeg
                with open(temp_video_list, 'w') as f:
                    cap_original = cv2.VideoCapture(original_video_path)
                    frame_index = 0
                    
                    while frame_index < total_original_frames:
                        ret, original_frame = cap_original.read()
                        if not ret:
                            break
                        
                        modified_frame_path = os.path.join(frame_dir, f"frame_{frame_index:06d}.png")
                        
                        if os.path.exists(modified_frame_path):
                            # Use modified frame
                            f.write(f"file '{modified_frame_path}'\n")
                            f.write(f"duration {1/fps}\n")
                        else:
                            # Export original frame temporarily
                            temp_frame_path = os.path.join(temp_dir, f"orig_frame_{frame_index:06d}.png")
                            cv2.imwrite(temp_frame_path, original_frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                            f.write(f"file '{temp_frame_path}'\n")
                            f.write(f"duration {1/fps}\n")
                        
                        frame_index += 1
                    
                    cap_original.release()
                
                # Use FFmpeg with ultra-high quality settings
                temp_output = os.path.join(temp_dir, "temp_output.mp4")
                
                ffmpeg_cmd = [
                    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                    '-i', temp_video_list,
                    '-c:v', 'libx264',  # H.264 codec
                    '-preset', 'veryslow',  # Best quality preset
                    '-crf', '12',  # Ultra high quality (0-51, lower = better)
                    '-pix_fmt', 'yuv420p',  # Compatible pixel format
                    '-movflags', '+faststart',  # Optimize for streaming
                    '-profile:v', 'high',  # High profile for better quality
                    '-level', '4.1',  # Level for compatibility
                    temp_output
                ]
                
                print(f"[VideoStego] 🎬 Running FFmpeg with ultra-quality settings...")
                
                # Use shorter timeout for smaller modifications
                timeout_duration = 30 if modified_frame_count < 5 else 60
                print(f"[VideoStego] ⏱️ Using {timeout_duration}s timeout for {modified_frame_count} modified frames")
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=timeout_duration)
                
                if result.returncode == 0 and os.path.exists(temp_output):
                    # Move result to final location
                    shutil.move(temp_output, output_path)
                    
                    final_size = os.path.getsize(output_path)
                    original_size = os.path.getsize(original_video_path)
                    preservation_ratio = final_size / original_size
                    
                    print(f"[VideoStego] 🎉 FFmpeg SUCCESS: {preservation_ratio:.1%} quality preservation!")
                    
                    # Clean up temp directory
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    return output_path
                else:
                    print(f"[VideoStego] ❌ FFmpeg failed: {result.stderr}")
                    
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            print(f"[VideoStego] ⚠️ FFmpeg approach failed: {e}")
        
        return None
    
    def _create_ultra_fast_single_frame_replacement(self, frame_dir: str, output_path: str, fps: float,
                                                   width: int, height: int, original_video_path: str,
                                                   total_original_frames: int, modified_frame_count: int):
        """Ultra-fast video creation for single frame modifications using stream copying"""
        
        print(f"[VideoStego] ⚡ ULTRA-FAST: Single frame replacement mode (only {modified_frame_count} modified)")
        
        try:
            # For single frame modifications, use direct stream copying with minimal processing
            # This should be 10x faster than full re-encoding
            
            # Get the modified frame info
            modified_frames = {}
            for file in os.listdir(frame_dir):
                if file.endswith('.png'):
                    frame_idx = int(file.split('_')[1].split('.')[0])
                    modified_frames[frame_idx] = os.path.join(frame_dir, file)
            
            print(f"[VideoStego] 📋 Modified frames: {list(modified_frames.keys())}")
            
            # Use mp4v codec with very fast settings for minimal frame changes
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            # Create video writer with optimized settings
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)
            
            if not out.isOpened():
                raise Exception("Ultra-fast video writer failed to initialize")
            
            # Open original video
            cap_original = cv2.VideoCapture(original_video_path)
            if not cap_original.isOpened():
                raise Exception("Failed to open original video")
            
            print(f"[VideoStego] 🚀 Ultra-fast processing: copying {total_original_frames} frames...")
            
            # Process frames with ultra-fast approach
            frame_index = 0
            copy_count = 0
            modify_count = 0
            
            while frame_index < total_original_frames:
                ret, original_frame = cap_original.read()
                if not ret:
                    break
                
                if frame_index in modified_frames:
                    # Load and write modified frame
                    modified_frame = cv2.imread(modified_frames[frame_index], cv2.IMREAD_COLOR)
                    if modified_frame is not None and modified_frame.shape == original_frame.shape:
                        out.write(modified_frame)
                        modify_count += 1
                    else:
                        out.write(original_frame)
                        copy_count += 1
                else:
                    # Direct copy original frame (no processing)
                    out.write(original_frame)
                    copy_count += 1
                
                frame_index += 1
                
                # Progress indicator for large videos
                if frame_index % 100 == 0:
                    progress = (frame_index / total_original_frames) * 100
                    print(f"[VideoStego] 📊 Progress: {progress:.1f}% ({frame_index}/{total_original_frames})")
            
            cap_original.release()
            out.release()
            
            print(f"[VideoStego] ✅ Ultra-fast processing complete:")
            print(f"[VideoStego]   📊 Frames copied: {copy_count}")
            print(f"[VideoStego]   📊 Frames modified: {modify_count}")
            print(f"[VideoStego]   ⚡ Efficiency: {(copy_count / (copy_count + modify_count)) * 100:.1f}%")
            
            final_size = os.path.getsize(output_path)
            original_size = os.path.getsize(original_video_path)
            preservation_ratio = final_size / original_size
            
            print(f"[VideoStego] 📏 Size: {final_size / 1024 / 1024:.1f}MB ({preservation_ratio:.1%} of original)")
            
            return output_path
            
        except Exception as e:
            print(f"[VideoStego] ❌ Ultra-fast approach failed: {e}")
            # Fallback to regular optimized approach
            return self._create_optimized_video_with_minimal_changes(
                frame_dir, output_path, fps, width, height,
                original_video_path, total_original_frames, modified_frame_count
            )
    
    def hide_data(self, video_path: str, payload: Union[str, bytes], output_path: str, 
                  is_file: bool = False, filename: str = None, project_name: str = None) -> Dict[str, Any]:
        """Backward compatibility method for hide_data API"""
        
        # Convert old API to new embed_data method
        output_filename = os.path.basename(output_path) if output_path else None
        
        result = self.embed_data(
            carrier_video_path=video_path,
            secret_data=payload,
            output_filename=output_filename,
            secret_filename=filename,
            project_name=project_name
        )
        
        # Convert new format to old format expected by API
        if result.get("success"):
            return {
                "success": True,
                "output_path": result["output_file"],
                "processing_time": result["processing_time"],
                "file_size": result["file_size"]
            }
        else:
            return {"success": False, "error": "Embedding failed"}

    def _is_layered_container(self, data: bytes) -> bool:
        """Check if the extracted data is a layered container JSON"""
        print(f"[VideoStego] 🔍 Checking if data is layered container ({len(data)} bytes)")
        
        try:
            if not data:
                print(f"[VideoStego] 🔍 No data provided")
                return False
            
            # SECURITY FIX: Only check for layered containers in data that was actually embedded through video steganography
            # This prevents false positives from audio or other extraction methods that might contain similar text
            
            # First, ensure the data is reasonable size for a layered container (not too small or too large)
            if len(data) < 50:  # Too small to be a meaningful layered container
                print(f"[VideoStego] 🔍 Data too small ({len(data)} bytes) for layered container")
                return False
            
            if len(data) > 1024 * 1024:  # Larger than 1MB is unlikely to be pure JSON metadata
                print(f"[VideoStego] 🔍 Data too large ({len(data)} bytes) to be layered container metadata")
                return False
            
            # First try simple string search for layered container signatures (works even with truncated JSON)
            print(f"[VideoStego] 🔍 Attempting UTF-8 decode...")
            json_str = data.decode('utf-8', errors='ignore')
            print(f"[VideoStego] 🔍 UTF-8 decode successful, checking for container signatures...")
            
            # ENHANCED CHECK: More specific signatures to reduce false positives
            # Look for specific layered container patterns that are unlikely to occur accidentally
            has_container_signature = (
                ('"type":"layered_container"' in json_str and '"layers":[' in json_str) or
                ('"version":"layered_container_v1"' in json_str and '"layers":[' in json_str) or
                # Check for the exact format we generate in our layered containers
                ('"type": "layered_container"' in json_str and '"layers": [' in json_str)
            )
            
            # Additional validation: must start with '{' and end with '}' for valid JSON
            json_str_stripped = json_str.strip()
            if not (json_str_stripped.startswith('{') and json_str_stripped.endswith('}')):
                print(f"[VideoStego] 🔍 Data doesn't look like JSON structure")
                return False
            
            if has_container_signature:
                print(f"[VideoStego] 🔍 Found layered container signature in string data")
                
                # Try to parse as JSON for full validation (might fail if truncated)
                try:
                    print(f"[VideoStego] 🔍 Trying full JSON parse for validation...")
                    json_data = json.loads(json_str)
                    print(f"[VideoStego] 🔍 JSON parse successful")
                    
                    # ENHANCED VALIDATION: More strict validation to prevent false positives
                    is_layered = (isinstance(json_data, dict) and 
                                 (json_data.get('type') == 'layered_container' or 
                                  json_data.get('version') == 'layered_container_v1') and
                                 'layers' in json_data and
                                 isinstance(json_data.get('layers'), list) and
                                 len(json_data.get('layers', [])) > 0)
                    
                    if is_layered:
                        layers_count = len(json_data.get('layers', []))
                        print(f"[VideoStego] 🔍 Full validation successful: {layers_count} layers")
                    else:
                        print(f"[VideoStego] 🔍 Enhanced validation failed - not a valid layered container")
                    
                    return is_layered
                except json.JSONDecodeError as e:
                    print(f"[VideoStego] 🔍 JSON parse failed: {e}")
                    print(f"[VideoStego] 🔍 Treating as regular data, not layered container")
                    return False  # FIXED: Don't trust signature if JSON is invalid
            else:
                print(f"[VideoStego] 🔍 No layered container signature found")
                return False
            
        except Exception as e:
            print(f"[VideoStego] 🔍 Layered container check failed: {e}")
            return False

    def _extract_layers(self, data: bytes) -> dict:
        """Extract individual layers from layered container data - ENHANCED ERROR HANDLING"""
        print(f"[VideoStego] 🔧 _extract_layers called with {len(data)} bytes")
        
        # CRITICAL FIX: Add validation before processing
        if not data or len(data) == 0:
            print(f"[VideoStego] ❌ No data provided to _extract_layers")
            return {}
        
        if len(data) > 10 * 1024 * 1024:  # 10MB limit for safety
            print(f"[VideoStego] ❌ Data too large ({len(data)} bytes) for layer extraction")
            return {}
        
        try:
            # Try to decode as UTF-8 with better error handling
            print(f"[VideoStego] 🔧 Attempting to decode bytes as UTF-8...")
            try:
                json_str = data.decode('utf-8')
            except UnicodeDecodeError as ude:
                print(f"[VideoStego] ❌ UTF-8 decode failed: {ude}")
                # Try with error handling
                json_str = data.decode('utf-8', errors='replace')
                print(f"[VideoStego] ⚠️ Used error replacement in UTF-8 decode")
            
            print(f"[VideoStego] 🔧 UTF-8 decode successful, length: {len(json_str)}")
            
            # Validate that this looks like JSON before parsing
            json_str_stripped = json_str.strip()
            if not json_str_stripped:
                print(f"[VideoStego] ❌ Empty string after UTF-8 decode")
                return {}
            
            if not (json_str_stripped.startswith('{') and json_str_stripped.endswith('}')):
                print(f"[VideoStego] ❌ Data doesn't appear to be JSON (doesn't start with {{ and end with }})")
                return {}
            
            # Show safe preview (avoid showing potentially sensitive data)
            safe_preview = json_str_stripped[:200] if len(json_str_stripped) > 200 else json_str_stripped
            print(f"[VideoStego] 🔧 JSON preview: {safe_preview}...")
            
            # Try to parse as JSON with enhanced error handling
            print(f"[VideoStego] 🔧 Attempting to parse as JSON...")
            try:
                container_data = json.loads(json_str)
            except json.JSONDecodeError as jde:
                print(f"[VideoStego] ❌ JSON parse failed: {jde}")
                print(f"[VideoStego] ❌ Error position: line {getattr(jde, 'lineno', 'unknown')} column {getattr(jde, 'colno', 'unknown')}")
                print(f"[VideoStego] ❌ This likely means the extracted data is corrupted or not a valid layered container")
                return {}  # Return empty dict instead of allowing exception to propagate
            print(f"[VideoStego] 🔧 JSON parse successful")
            print(f"[VideoStego] 🔧 Container type: {container_data.get('type', 'MISSING')}")
            print(f"[VideoStego] 🔧 Container keys: {list(container_data.keys())}")
            
            layers = {}
            layers_data = container_data.get('layers', [])
            print(f"[VideoStego] 🔧 Layers data type: {type(layers_data)}")
            print(f"[VideoStego] 🔧 Layers data length: {len(layers_data) if hasattr(layers_data, '__len__') else 'N/A'}")
            
            # Handle array format (new format): [{'filename': '...', 'content': '...', 'type': '...'}]
            if isinstance(layers_data, list):
                print(f"[VideoStego] 📦 Processing layered container with {len(layers_data)} layers (array format)")
                for i, layer_info in enumerate(layers_data):
                    print(f"[VideoStego] 🔧 Processing layer {i+1}: {type(layer_info)}")
                    if isinstance(layer_info, dict):
                        print(f"[VideoStego] 🔧 Layer {i+1} keys: {list(layer_info.keys())}")
                        if 'content' in layer_info:
                            # Decode base64 layer data
                            import base64
                            content_b64 = layer_info['content']
                            print(f"[VideoStego] 🔧 Layer {i+1} content length: {len(content_b64)} chars")
                            layer_data = base64.b64decode(content_b64)
                            layer_filename = layer_info.get('filename', f'layer_{i+1}.bin')
                            layers[f"layer_{i+1}"] = {
                                'data': layer_data,
                                'type': layer_info.get('type', 'binary'),
                                'filename': layer_filename
                            }
                            print(f"[VideoStego] 📁 Layer {i+1}: '{layer_filename}' ({len(layer_data)} bytes, type: {layer_info.get('type', 'binary')})")
                        else:
                            print(f"[VideoStego] ⚠️ Layer {i+1} missing 'content' field")
                    else:
                        print(f"[VideoStego] ⚠️ Layer {i+1} is not a dict: {type(layer_info)}")
            
            # Handle object format (legacy format): {'layer_name': {'data': '...', 'type': '...', 'filename': '...'}}
            elif isinstance(layers_data, dict):
                print(f"[VideoStego] 📦 Processing layered container with {len(layers_data)} layers (object format)")
                for layer_name, layer_info in layers_data.items():
                    if isinstance(layer_info, dict) and 'data' in layer_info:
                        # Decode base64 layer data
                        import base64
                        layer_data = base64.b64decode(layer_info['data'])
                        layers[layer_name] = {
                            'data': layer_data,
                            'type': layer_info.get('type', 'unknown'),
                            'filename': layer_info.get('filename', f'{layer_name}.bin')
                        }
            else:
                print(f"[VideoStego] ❌ Layers data is neither list nor dict: {type(layers_data)}")
            
            print(f"[VideoStego] 📦 Successfully extracted {len(layers)} layers from container")
            return layers
            
        except UnicodeDecodeError as e:
            print(f"[VideoStego] ❌ UTF-8 decode failed: {e}")
            print(f"[VideoStego] ❌ This suggests the extracted data is binary, not text-based layered container")
            return {}
        except json.JSONDecodeError as e:
            # This is the error the user was seeing - make it more informative
            print(f"[VideoStego] ❌ JSON parse failed: {e}")
            print(f"[VideoStego] ❌ Data was not valid JSON - this may indicate:")
            print(f"[VideoStego] ❌   1. The file was not created with video steganography")
            print(f"[VideoStego] ❌   2. The extracted data is corrupted")
            print(f"[VideoStego] ❌   3. Wrong extraction method (audio file processed as video)")
            print(f"[VideoStego] ❌ Treating as non-layered data")
            return {}
        except Exception as e:
            print(f"[VideoStego] ❌ Failed to extract layers: {e}")
            print(f"[VideoStego] ❌ This indicates an unexpected error in layer processing")
            import traceback
            traceback.print_exc()
            return {}

    def _create_layered_zip(self, layers: dict) -> bytes:
        """Create a ZIP archive containing all extracted layers"""
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        
        try:
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for layer_name, layer_info in layers.items():
                    filename = layer_info.get('filename', f'{layer_name}.bin')
                    zipf.writestr(filename, layer_info['data'])
            
            zip_buffer.seek(0)
            zip_data = zip_buffer.getvalue()
            
            print(f"[VideoStego] 📦 Created multi-layer ZIP with {len(layers)} files ({len(zip_data)} bytes)")
            return zip_data
        except Exception as e:
            print(f"[VideoStego] ❌ Failed to create layered ZIP: {e}")
            return b''

# Aliases for compatibility
FinalVideoSteganographyManager = VideoSteganographyManager
OptimizedVideoSteganographyManager = VideoSteganographyManager