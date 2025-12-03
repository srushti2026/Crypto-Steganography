#!/usr/bin/env python3
"""
Fixed Advanced Video Steganography Implementation
Supports hiding text, images, and documents in video files
"""

import cv2
import numpy as np
import os
import json
import hashlib
import struct
import time
import shutil
from typing import Union, Tuple, Optional, Dict, Any
import base64
from pathlib import Path


class VideoSteganography:
    """            try:
                playable_fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                playable_out = cv2.VideoWriter(playable_video_path, playable_fourcc, fps, (width, height))
                
                if not playable_out.isOpened():
                    print(f"[VideoStego] Warning: Cannot create playable video file")
                    playable_out = None
                else:
                    print(f"[VideoStego] Playable video writer opened successfully")
            except Exception as e:
                print(f"[VideoStego] Warning: Playable video creation failed: {e}")
                playable_out = Noneideo steganography using LSB embedding in video frames"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.magic_header = b"VEILFORGE_VIDEO_V1"
        self.redundancy = 3  # Triple redundancy for reliability
        
    def _generate_key(self, seed: str) -> int:
        """Generate a consistent key from password and seed"""
        combined = f"{self.password}{seed}".encode('utf-8')
        return int(hashlib.sha256(combined).hexdigest()[:8], 16)
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA-256 checksum of data"""
        return hashlib.sha256(data).hexdigest()
    
    def _embed_bit_in_pixel(self, pixel_value: int, bit: int) -> int:
        """Embed a single bit in the LSB of a pixel value"""
        return (pixel_value & 0xFE) | bit
    
    def _extract_bit_from_pixel(self, pixel_value: int) -> int:
        """Extract LSB bit from a pixel value"""
        return pixel_value & 1
    
    def _prepare_payload(self, data: Union[str, bytes], filename: str = None) -> bytes:
        """Prepare payload with metadata"""
        print(f"[VideoStego] _prepare_payload called with filename: {repr(filename)}")
        print(f"[VideoStego] Data type: {type(data)}, Data size: {len(data) if hasattr(data, '__len__') else 'unknown'}")
        
        # Convert text to bytes if needed
        if isinstance(data, str):
            if os.path.isfile(data):
                # It's a file path
                with open(data, 'rb') as f:
                    file_data = f.read()
                filename = filename or os.path.basename(data)
                data_bytes = file_data
                data_type = 'file'
                print(f"[VideoStego] File path detected, using filename: {filename}")
            else:
                # It's text content
                data_bytes = data.encode('utf-8')
                # For text content, only use provided filename if it looks like a text filename
                if filename and (filename.endswith('.txt') or filename.endswith('.md') or '.' not in filename):
                    print(f"[VideoStego] Text content, keeping provided filename: {filename}")
                    pass  # Use provided filename
                else:
                    old_filename = filename
                    filename = 'embedded_text.txt'  # Default for text content
                    print(f"[VideoStego] Text content, changed filename from {old_filename} to {filename}")
                data_type = 'text'
        else:
            # It's already bytes
            data_bytes = data
            # For binary content, only use provided filename if it's not a video filename
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
            is_video_filename = filename and any(filename.lower().endswith(ext) for ext in video_extensions)
            
            print(f"[VideoStego] Binary content, filename: {filename}")
            print(f"[VideoStego] Is video filename: {is_video_filename}")
            
            if filename and not is_video_filename:
                print(f"[VideoStego] Binary content, keeping provided filename: {filename}")
                pass  # Use provided filename
            else:
                old_filename = filename
                filename = 'embedded_data.bin'  # Default for binary content
                print(f"[VideoStego] Binary content, changed filename from {old_filename} to {filename}")
            data_type = 'binary'
        
        print(f"[VideoStego] Final filename for metadata: {filename}")
        print(f"[VideoStego] Data type: {data_type}")
        
        # Create metadata
        metadata = {
            'filename': filename,
            'size': len(data_bytes),
            'type': data_type,
            'checksum': self._calculate_checksum(data_bytes)
        }
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_size = len(metadata_json)
        
        # Pack: magic_header + metadata_size + metadata + data
        payload = (
            self.magic_header +
            struct.pack('<I', metadata_size) +  # 4 bytes for metadata size
            metadata_json +
            data_bytes
        )
        
        print(f"[VideoStego] Prepared payload:")
        print(f"  Magic header: {len(self.magic_header)} bytes")
        print(f"  Metadata size: {metadata_size} bytes")
        print(f"  Data size: {len(data_bytes)} bytes")
        print(f"  Total payload: {len(payload)} bytes")
        
        return payload
    
    def _get_embeddable_pixels(self, frame: np.ndarray) -> int:
        """Calculate number of pixels available for embedding"""
        height, width = frame.shape[:2]
        channels = 3 if len(frame.shape) == 3 else 1
        return height * width * channels
    
    def _embed_payload_in_frame(self, frame: np.ndarray, payload_bits: list, 
                               start_index: int) -> Tuple[np.ndarray, int]:
        """Embed payload bits into a single frame"""
        modified_frame = frame.copy()
        height, width = frame.shape[:2]
        
        # Flatten frame for easier access
        if len(frame.shape) == 3:
            flat_frame = modified_frame.reshape(-1, 3)
        else:
            flat_frame = modified_frame.reshape(-1, 1)
        
        channels = flat_frame.shape[1]
        bits_embedded = 0
        pixel_count = 0
        
        for pixel_idx in range(flat_frame.shape[0]):
            if start_index + bits_embedded >= len(payload_bits):
                break
                
            for channel in range(channels):
                if start_index + bits_embedded >= len(payload_bits):
                    break
                
                # Get the bit to embed
                bit_to_embed = payload_bits[start_index + bits_embedded]
                
                # Embed bit using LSB
                original_value = int(flat_frame[pixel_idx, channel])
                new_value = (original_value & 0xFE) | bit_to_embed
                flat_frame[pixel_idx, channel] = new_value
                
                pixel_count += 1
                
                # Move to next bit after redundancy copies
                if pixel_count % self.redundancy == 0:
                    bits_embedded += 1
        
        # Reshape back to original frame shape
        if len(frame.shape) == 3:
            modified_frame = flat_frame.reshape(height, width, 3)
        else:
            modified_frame = flat_frame.reshape(height, width)
        
        return modified_frame, start_index + bits_embedded

    def _embed_payload_in_frame_fast(self, frame: np.ndarray, payload_bits: list, 
                                    start_index: int, redundancy: int) -> Tuple[np.ndarray, int]:
        """OPTIMIZED: Fast embedding with reduced redundancy for performance"""
        modified_frame = frame.copy()
        height, width = frame.shape[:2]
        
        # Flatten for vectorized operations
        if len(frame.shape) == 3:
            flat_frame = modified_frame.reshape(-1, 3)
        else:
            flat_frame = modified_frame.reshape(-1, 1)
        
        channels = flat_frame.shape[1]
        bits_embedded = 0
        pixel_count = 0
        
        # OPTIMIZATION: Process in larger chunks and limit redundancy
        for pixel_idx in range(flat_frame.shape[0]):
            if start_index + bits_embedded >= len(payload_bits):
                break
                
            for channel in range(channels):
                if start_index + bits_embedded >= len(payload_bits):
                    break
                
                # Get the bit to embed
                bit_to_embed = payload_bits[start_index + bits_embedded]
                
                # Fast LSB embedding
                flat_frame[pixel_idx, channel] = (int(flat_frame[pixel_idx, channel]) & 0xFE) | bit_to_embed
                
                pixel_count += 1
                
                # Use provided redundancy parameter (lower for speed)
                if pixel_count % redundancy == 0:
                    bits_embedded += 1
        
        # Reshape back
        if len(frame.shape) == 3:
            modified_frame = flat_frame.reshape(height, width, 3)
        else:
            modified_frame = flat_frame.reshape(height, width)
        
        return modified_frame, start_index + bits_embedded
    
    def _find_matching_frame_directory(self, video_path: str) -> Optional[str]:
        """Find frame directory that matches the uploaded video file"""
        try:
            import os
            import cv2
            
            # Get video properties to match against frame directories
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
                
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            
            # Search in the same directory and outputs directory
            search_dirs = [
                os.path.dirname(video_path),
                os.path.join(os.path.dirname(video_path), 'outputs'),
                os.path.join(os.path.dirname(os.path.dirname(video_path)), 'outputs')  # For uploads->outputs
            ]
            
            print(f"[VideoStego] Searching for frame directory matching {width}x{height}, {total_frames} frames")
            
            # Collect all matching directories and their timestamps
            matching_dirs = []
            
            for search_dir in search_dirs:
                if not os.path.exists(search_dir):
                    continue
                    
                # Look for directories ending with _frames
                for item in os.listdir(search_dir):
                    if item.endswith('_frames'):
                        frame_dir_path = os.path.join(search_dir, item)
                        if os.path.isdir(frame_dir_path):
                            # Check if this frame directory matches our video
                            marker_file = os.path.join(frame_dir_path, "frame_info.json")
                            if os.path.exists(marker_file):
                                try:
                                    import json
                                    with open(marker_file, 'r') as f:
                                        frame_info = json.load(f)
                                    
                                    # Match dimensions and frame count
                                    if (frame_info.get('width') == width and 
                                        frame_info.get('height') == height and
                                        frame_info.get('total_frames') == total_frames):
                                        
                                        # Get directory creation time for priority
                                        dir_stat = os.stat(frame_dir_path)
                                        creation_time = dir_stat.st_ctime
                                        
                                        matching_dirs.append((frame_dir_path, creation_time, item))
                                        print(f"[VideoStego] Found candidate: {item}")
                                        
                                except:
                                    continue
            
            if matching_dirs:
                # Sort by creation time (most recent first) to prefer newer embeddings
                matching_dirs.sort(key=lambda x: x[1], reverse=True)
                
                print(f"[VideoStego] Found {len(matching_dirs)} matching directories, using most recent")
                for frame_dir_path, _, dir_name in matching_dirs:
                    print(f"[VideoStego] Trying: {dir_name}")
                    
                    # Try extraction to verify this is the right directory
                    try:
                        test_result = self._extract_from_frames(frame_dir_path)
                        if test_result and test_result[0] is not None:
                            print(f"[VideoStego] ✅ Successfully validated frame directory: {frame_dir_path}")
                            return frame_dir_path
                        else:
                            print(f"[VideoStego] ❌ Frame directory failed validation (no data): {frame_dir_path}")
                    except Exception as e:
                        print(f"[VideoStego] ❌ Frame directory failed validation (error): {frame_dir_path} - {e}")
                        continue
            
            print(f"[VideoStego] ❌ No matching frame directory found")
            return None
            
        except Exception as e:
            print(f"[VideoStego] Error searching for frame directory: {e}")
            return None
        
    def _extract_from_frames(self, frame_dir: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract data directly from PNG frames for perfect LSB preservation"""
        try:
            # Read frame info
            marker_file = os.path.join(frame_dir, "frame_info.json")
            with open(marker_file, 'r') as f:
                frame_info = json.load(f)
            
            total_frames = frame_info['total_frames']
            width = frame_info['width']
            height = frame_info['height']
            redundancy = frame_info['redundancy']
            
            print(f"[VideoStego] Perfect extraction from {total_frames} PNG frames")
            print(f"[VideoStego] Frame info: {width}x{height}, {redundancy}x redundancy")
            
            # Extract all bits using the known redundancy
            all_extracted_bits = []
            current_bit_votes = []
            
            for frame_num in range(total_frames):
                frame_path = os.path.join(frame_dir, f"frame_{frame_num:06d}.png")
                if not os.path.exists(frame_path):
                    continue
                    
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue
                
                # Flatten frame for processing
                if len(frame.shape) == 3:
                    flat_frame = frame.reshape(-1, 3)
                    channels = 3
                else:
                    flat_frame = frame.reshape(-1, 1)
                    channels = 1
                
                # Extract LSBs in the same order as embedding
                for pixel_idx in range(flat_frame.shape[0]):
                    for channel in range(channels):
                        bit_value = int(flat_frame[pixel_idx, channel]) & 1
                        current_bit_votes.append(bit_value)
                        
                        # Use known redundancy to group bits
                        if len(current_bit_votes) == redundancy:
                            # Majority vote for error correction
                            final_bit = 1 if sum(current_bit_votes) > len(current_bit_votes) // 2 else 0
                            all_extracted_bits.append(final_bit)
                            current_bit_votes = []
            
            print(f"[VideoStego] Extracted {len(all_extracted_bits)} bits from PNG frames")
            
            # Process the extracted bits to get the payload
            return self._process_extracted_bits(all_extracted_bits)
            
        except Exception as e:
            print(f"[VideoStego] Frame extraction failed: {e}")
            return None, None
    
    def _process_extracted_bits(self, all_extracted_bits: list) -> Tuple[Optional[bytes], Optional[str]]:
        """Process extracted bits to recover the original payload and filename"""
        try:
            if len(all_extracted_bits) < len(self.magic_header) * 8:
                print(f"[VideoStego] ❌ Not enough bits for magic header")
                return None, None

            # Check magic header
            magic_header_bits_needed = len(self.magic_header) * 8
            magic_bits = all_extracted_bits[:magic_header_bits_needed]
            
            # Convert bits to bytes for magic header
            magic_bytes = []
            for i in range(0, magic_header_bits_needed, 8):
                byte_bits = magic_bits[i:i+8]
                byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                magic_bytes.append(byte_value)
            
            extracted_magic = bytes(magic_bytes)
            print(f"[VideoStego] Expected magic: {self.magic_header}")
            print(f"[VideoStego] Extracted magic: {extracted_magic}")
            if extracted_magic != self.magic_header:
                print(f"[VideoStego] ❌ Magic header mismatch")
                return None, None
            
            # Extract metadata size (4 bytes)
            metadata_size_start = magic_header_bits_needed
            metadata_size_end = metadata_size_start + 32  # 4 bytes * 8 bits
            
            if len(all_extracted_bits) < metadata_size_end:
                print(f"[VideoStego] ❌ Not enough bits for metadata size")
                return None, None
            
            metadata_size_bits = all_extracted_bits[metadata_size_start:metadata_size_end]
            metadata_size_bytes = []
            for i in range(0, 32, 8):
                byte_bits = metadata_size_bits[i:i+8]
                byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                metadata_size_bytes.append(byte_value)
            
            metadata_size = struct.unpack('<I', bytes(metadata_size_bytes))[0]
            print(f"[VideoStego] Metadata size: {metadata_size}")
            
            # Extract metadata
            metadata_start = metadata_size_end
            metadata_end = metadata_start + metadata_size * 8
            
            if len(all_extracted_bits) < metadata_end:
                print(f"[VideoStego] ❌ Not enough bits for metadata")
                return None, None
            
            metadata_bits = all_extracted_bits[metadata_start:metadata_end]
            metadata_bytes = []
            for i in range(0, len(metadata_bits), 8):
                if i + 8 <= len(metadata_bits):
                    byte_bits = metadata_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    metadata_bytes.append(byte_value)
            
            metadata_json = bytes(metadata_bytes).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            print(f"[VideoStego] Metadata: {metadata}")
            data_size = metadata['size']
            extracted_filename = metadata.get('filename', 'extracted_data.bin')
            
            # Extract data
            data_start = metadata_end
            data_end = data_start + data_size * 8
            
            if len(all_extracted_bits) < data_end:
                print(f"[VideoStego] ❌ Not enough bits for data")
                return None, None
            
            data_bits = all_extracted_bits[data_start:data_end]
            data_bytes = []
            for i in range(0, len(data_bits), 8):
                if i + 8 <= len(data_bits):
                    byte_bits = data_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    data_bytes.append(byte_value)
            
            extracted_data = bytes(data_bytes)
            print(f"[VideoStego] ✅ Successfully extracted {len(extracted_data)} bytes")
            print(f"[VideoStego] ✅ Filename: {extracted_filename}")
            
            return extracted_data, extracted_filename
            
        except Exception as e:
            print(f"[VideoStego] Payload processing failed: {e}")
            return None, None

    def embed_data(self, video_path: str, data: Union[str, bytes], 
                   output_path: str, filename: str = None) -> Dict[str, Any]:
        """Embed data into video file - OPTIMIZED for performance"""
        try:
            print(f"[VideoStego] Starting FAST embedding process...")
            start_time = time.time()
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Prepare payload with the provided filename for content identification
            payload = self._prepare_payload(data, filename)
            
            # Convert payload to bits
            payload_bits = []
            for byte in payload:
                for i in range(8):
                    payload_bits.append((byte >> i) & 1)
            
            # OPTIMIZATION 1: Use high redundancy for error correction
            bits_needed = len(payload_bits)
            if bits_needed < 5000:  # Small payloads (adjust threshold for performance)
                redundancy = 5  # Increased redundancy for better error correction
            else:
                redundancy = 5  # High redundancy to handle video codec LSB alterations
            
            total_bits_needed = bits_needed * redundancy
            
            # OPTIMIZATION 2: Calculate minimum frames needed
            pixels_per_frame = width * height * 3  # RGB channels
            frames_needed = max(1, (total_bits_needed + pixels_per_frame - 1) // pixels_per_frame)
            frames_to_process = min(frames_needed + 10, total_frames)  # Add buffer but limit processing
            
            print(f"[VideoStego] OPTIMIZED STATS:")
            print(f"  Video: {width}x{height}, {fps} FPS, {total_frames} frames")
            print(f"  Payload: {len(payload)} bytes -> {bits_needed} bits")
            print(f"  Redundancy: {redundancy}x -> {total_bits_needed} total bits")
            print(f"  Frames needed: {frames_needed}, will process: {frames_to_process}")
            
            # CRITICAL: Try different approach - use image sequence instead of video codec
            # This completely bypasses video compression issues
            base_name = os.path.splitext(output_path)[0]
            output_dir = f"{base_name}_frames"
            os.makedirs(output_dir, exist_ok=True)
            
            print(f"[VideoStego] Using frame-by-frame approach to bypass codec issues")
            print(f"[VideoStego] Frames will be stored in: {output_dir}")
            
            # We'll store frames as PNG (lossless) and reconstruct later
            used_codec = "Frame-by-frame (PNG)"
            frame_paths = []
            
            # OPTIMIZATION 3: Process only required frames
            current_bit_index = 0
            frames_processed = 0
            embedding_complete = False
            
            print(f"[VideoStego] Fast embedding in progress...")
            print(f"[VideoStego] First few payload bits: {payload_bits[:20]}")
            
            for frame_num in range(total_frames):
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_num < frames_to_process and not embedding_complete:
                    if current_bit_index < total_bits_needed:
                        # Debug: Show what we're embedding in the first frame
                        if frame_num == 0:
                            original_frame = frame.copy()
                        
                        # Embed data in this frame
                        modified_frame, new_bit_index = self._embed_payload_in_frame_fast(
                            frame, payload_bits, current_bit_index, redundancy
                        )
                        
                        # Debug: Check first frame modifications
                        if frame_num == 0:
                            print(f"[VideoStego] First frame embedding debug:")
                            flat_orig = original_frame.reshape(-1, 3)
                            flat_mod = modified_frame.reshape(-1, 3)
                            for debug_i in range(min(10, flat_orig.shape[0])):
                                for debug_ch in range(3):
                                    orig_val = int(flat_orig[debug_i, debug_ch])
                                    mod_val = int(flat_mod[debug_i, debug_ch])
                                    if orig_val != mod_val:
                                        print(f"  Pixel[{debug_i}][{debug_ch}]: {orig_val} -> {mod_val} (LSB: {mod_val & 1})")
                        
                        current_bit_index = new_bit_index
                        
                        # Save frame as PNG (lossless)
                        frame_path = os.path.join(output_dir, f"frame_{frame_num:06d}.png")
                        cv2.imwrite(frame_path, modified_frame)
                        frame_paths.append(frame_path)
                        
                        if current_bit_index >= total_bits_needed:
                            embedding_complete = True
                            print(f"[VideoStego] ✅ Embedding complete at frame {frame_num + 1}")
                    else:
                        # Save unmodified frame
                        frame_path = os.path.join(output_dir, f"frame_{frame_num:06d}.png")
                        cv2.imwrite(frame_path, frame)
                        frame_paths.append(frame_path)
                else:
                    # Save unmodified frame
                    frame_path = os.path.join(output_dir, f"frame_{frame_num:06d}.png")
                    cv2.imwrite(frame_path, frame)
                    frame_paths.append(frame_path)
                
                frames_processed += 1
                
                # Progress update every 50 frames or when complete
                if frames_processed % 50 == 0 or embedding_complete:
                    elapsed = time.time() - start_time
                    progress = (current_bit_index / total_bits_needed) * 100 if total_bits_needed > 0 else 100
                    print(f"  Frame {frames_processed}/{total_frames}, {progress:.1f}% embedded, {elapsed:.1f}s")
            
            # Cleanup
            cap.release()
            
            # DUAL OUTPUT: Create both steganography and playable versions
            print(f"[VideoStego] Creating dual output from {frames_processed} frames...")
            
            # 1. STEGANOGRAPHY FILE (FFV1 - preserves LSB data for extraction)
            # Always use the provided output_path for the steganography file
            stego_video_path = output_path
            # Create playable version path by modifying the base name
            base_name = os.path.splitext(stego_video_path)[0]
            playable_video_path = f"{base_name}_playable.avi"
            
            if filename:
                print(f"[VideoStego] Using provided filename for metadata: {filename}")
            
            print(f"[VideoStego] Creating steganography file: {os.path.basename(stego_video_path)}")
            
            # Ensure output directory exists
            video_output_dir = os.path.dirname(stego_video_path)
            if video_output_dir:  # Only create if there's actually a directory path
                os.makedirs(video_output_dir, exist_ok=True)
            
            # Use FFV1 codec for steganography preservation
            try:
                # Try completely uncompressed first
                fourcc = cv2.VideoWriter_fourcc(*'DIB ')  # Uncompressed RGB
                stego_out = cv2.VideoWriter(stego_video_path, fourcc, fps, (width, height))
                used_codec = "DIB (Uncompressed)"
                
                if not stego_out.isOpened():
                    print(f"[VideoStego] DIB codec failed, trying FFV1...")
                    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
                    stego_out = cv2.VideoWriter(stego_video_path, fourcc, fps, (width, height))
                    used_codec = "FFV1 (Lossless)"
                    
                    if not stego_out.isOpened():
                        print(f"[VideoStego] FFV1 codec failed, trying HuffYUV...")
                        # Fallback to HuffYUV
                        fourcc = cv2.VideoWriter_fourcc(*'HFYU')
                        stego_out = cv2.VideoWriter(stego_video_path, fourcc, fps, (width, height))
                        used_codec = "HuffYUV (Lossless)"
                        
                        if not stego_out.isOpened():
                            print(f"[VideoStego] HuffYUV codec failed, trying MJPG...")
                            # Last fallback to MJPG (might lose some LSB data but better than nothing)
                            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                            stego_out = cv2.VideoWriter(stego_video_path, fourcc, fps, (width, height))
                            used_codec = "MJPG (Lossy)"
                            
                            if not stego_out.isOpened():
                                raise ValueError(f"Cannot create steganography video: {stego_video_path}")
                
                print(f"[VideoStego] Steganography video writer opened successfully with {used_codec}")
            except Exception as e:
                raise ValueError(f"Cannot create steganography video: {stego_video_path}. Error: {str(e)}")
            
            # 2. PLAYABLE FILE (MJPG - compatible but loses LSB data)
            print(f"[VideoStego] Creating playable file: {os.path.basename(playable_video_path)}")
            
            try:
                playable_fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                playable_out = cv2.VideoWriter(playable_video_path, playable_fourcc, fps, (width, height))
                
                if not playable_out.isOpened():
                    print(f"[VideoStego] Warning: Cannot create playable version")
                    playable_out = None
            except Exception as e:
                print(f"[VideoStego] Warning: Playable version failed: {e}")
                playable_out = None
            
            print(f"[VideoStego] Using {used_codec} for steganography preservation")
            
            # Write frames to both outputs
            frames_written = 0
            for frame_num in range(frames_processed):
                frame_path = os.path.join(output_dir, f"frame_{frame_num:06d}.png")
                if os.path.exists(frame_path):
                    frame = cv2.imread(frame_path)
                    if frame is not None:
                        # Write to steganography file
                        stego_out.write(frame)
                        # Write to playable file if available
                        if playable_out is not None:
                            playable_out.write(frame)
                        frames_written += 1
                    else:
                        print(f"[VideoStego] Warning: Could not read frame {frame_num}")
                else:
                    print(f"[VideoStego] Warning: Frame file not found: {frame_path}")
            
            print(f"[VideoStego] Wrote {frames_written}/{frames_processed} frames to video files")
            
            stego_out.release()
            if playable_out is not None:
                playable_out.release()
                
            # Set the main output to the steganography file
            final_video_path = stego_video_path
            
            # Keep frame directory for perfect extraction and create a marker file
            try:
                marker_file = os.path.join(output_dir, "frame_info.json")
                frame_info = {
                    'total_frames': frames_processed,
                    'width': width,
                    'height': height,
                    'redundancy': redundancy,
                    'steganography_file': stego_video_path,
                    'created_at': time.time()
                }
                with open(marker_file, 'w') as f:
                    json.dump(frame_info, f)
                print(f"[VideoStego] Frame directory preserved for perfect extraction: {output_dir}")
            except Exception as e:
                print(f"[VideoStego] Warning: Could not create frame info: {e}")
            
            # Return the final video file path
            output_path = final_video_path
            
            total_time = time.time() - start_time
            print(f"[VideoStego] ✅ FAST embedding completed in {total_time:.2f} seconds!")
            print(f"  Steganography file: {os.path.basename(stego_video_path)}")
            if playable_out is not None:
                print(f"  Playable file: {os.path.basename(playable_video_path)}")
            print(f"  Embedded {bits_needed} bits into {frames_processed} frames")
            
            # Check file sizes
            stego_size = os.path.getsize(stego_video_path)
            playable_size = os.path.getsize(playable_video_path) if os.path.exists(playable_video_path) else 0
            
            return {
                'success': True,
                'output_path': output_path,  # Main output (steganography file)
                'steganography_file': stego_video_path,  # For extraction
                'playable_file': playable_video_path if playable_out is not None else None,  # For viewing
                'frames_processed': frames_processed,
                'bits_embedded': bits_needed,
                'payload_size': len(payload),
                'processing_time': total_time,
                'redundancy_used': redundancy,
                'codec_used': used_codec,
                'file_sizes': {
                    'steganography': stego_size,
                    'playable': playable_size
                },
                'video_properties': {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'total_frames': total_frames
                }
            }
            
        except Exception as e:
            print(f"[VideoStego] ❌ Fast embedding failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_data(self, video_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract hidden data from video file - OPTIMIZED for performance"""
        try:
            print(f"[VideoStego] Starting FAST extraction from: {video_path}")
            start_time = time.time()
            
            # FIRST: Check if there's a frame-based storage directory for this video
            base_name = os.path.splitext(video_path)[0]
            frame_dir = f"{base_name}_frames"
            
            if os.path.isdir(frame_dir):
                marker_file = os.path.join(frame_dir, "frame_info.json")
                if os.path.exists(marker_file):
                    print(f"[VideoStego] Found frame-based storage, using perfect PNG extraction")
                    return self._extract_from_frames(frame_dir)
            
            # SMART SEARCH: If direct lookup failed, search for matching frame directories
            # This handles cases where uploaded file has different name than original
            frame_dir_found = self._find_matching_frame_directory(video_path)
            if frame_dir_found:
                print(f"[VideoStego] Found matching frame directory: {frame_dir_found}")
                return self._extract_from_frames(frame_dir_found)
            
            # FALLBACK: Check if it's frame-based storage or regular video
            if os.path.isdir(video_path):
                # Frame-based storage
                marker_file = os.path.join(video_path, "frame_info.json")
                if os.path.exists(marker_file):
                    with open(marker_file, 'r') as f:
                        frame_info = json.load(f)
                    
                    total_frames = frame_info['total_frames']
                    width = frame_info['width'] 
                    height = frame_info['height']
                    
                    print(f"[VideoStego] Frame-based storage: {width}x{height}, {total_frames} frames")
                    
                    # Read frames from PNG files
                    def read_frame(frame_num):
                        frame_path = os.path.join(video_path, f"frame_{frame_num:06d}.png")
                        if os.path.exists(frame_path):
                            return True, cv2.imread(frame_path)
                        return False, None
                        
                else:
                    raise ValueError(f"Invalid frame-based storage: {video_path}")
                    
            else:
                # Regular video file
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    raise ValueError(f"Cannot open video: {video_path}")
                
                # Get video properties
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                print(f"[VideoStego] Video: {width}x{height}, {total_frames} frames")
                
                def read_frame(frame_num):
                    return cap.read()
            
            # OPTIMIZATION 1: Estimate redundancy and frames needed
            # First, try to extract magic header to determine redundancy
            magic_needed_bits = len(self.magic_header) * 8
            # Match embedding logic: 2x redundancy for small payloads < 5000 bits
            estimated_redundancy = 2  # For small payloads
            
            # OPTIMIZATION 2: Try both redundancy levels to find the right one
            pixels_per_frame = width * height * 3  # RGB channels
            
            print(f"[VideoStego] FAST EXTRACTION - trying adaptive redundancy detection")
            
            # Try different redundancy levels to find the correct one
            for try_redundancy in [2, 3, 5]:
                print(f"[VideoStego] Trying {try_redundancy}x redundancy...")
                
                # Reset for this attempt
                all_extracted_bits = []
                frame_count = 0
                frames_to_check = min(10, total_frames)  # Only need a few frames to test
                
                success = False
            
                while frame_count < frames_to_check:
                    ret, frame = read_frame(frame_count)
                    if not ret:
                        break
                    
                    # Extract bits with current redundancy attempt
                    height, width = frame.shape[:2]
                    
                    if len(frame.shape) == 3:
                        flat_frame = frame.reshape(-1, 3)
                    else:
                        flat_frame = frame.reshape(-1, 1)
                    
                    channels = flat_frame.shape[1]
                    pixel_count = 0
                    current_bit_votes = []
                    
                    # DEBUG: Print first few pixel values only for first redundancy attempt
                    if try_redundancy == 3 and frame_count == 0:
                        print(f"[VideoStego] First frame extraction debug for 3x:")
                        position = 0
                        for debug_i in range(min(10, flat_frame.shape[0])):
                            for debug_ch in range(channels):
                                pixel_val = int(flat_frame[debug_i, debug_ch])
                                lsb = pixel_val & 1
                                print(f"  Position {position}: Pixel[{debug_i}][{debug_ch}]: {pixel_val} (LSB: {lsb})")
                                position += 1
                                if position >= 30:  # Show first 30 positions
                                    break
                            if position >= 30:
                                break
                    
                    for pixel_idx in range(flat_frame.shape[0]):
                        for channel in range(channels):
                            # Quick LSB extraction
                            bit_value = int(flat_frame[pixel_idx, channel]) & 1
                            current_bit_votes.append(bit_value)
                            
                            # Use current redundancy attempt - collect exactly try_redundancy votes
                            if len(current_bit_votes) == try_redundancy:
                                # Quick majority vote
                                final_bit = 1 if sum(current_bit_votes) > len(current_bit_votes) // 2 else 0
                                all_extracted_bits.append(final_bit)
                                current_bit_votes = []
                    
                    frame_count += 1
                    
                    # Check if we have enough bits for magic header
                    if len(all_extracted_bits) >= magic_needed_bits:
                        break
                
                # Test if this redundancy gives us the correct magic header
                if len(all_extracted_bits) >= magic_needed_bits:
                    magic_bits = all_extracted_bits[:magic_needed_bits]
                    magic_bytes = []
                    for i in range(0, magic_needed_bits, 8):
                        if i + 8 <= len(magic_bits):
                            byte_bits = magic_bits[i:i+8]
                            byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                            magic_bytes.append(byte_value)
                    
                    # Debug first byte reconstruction for 3x redundancy  
                    if try_redundancy == 3:
                        print(f"  First 8 extracted bits: {magic_bits[:8]}")
                        print(f"  First byte reconstruction: {magic_bytes[0] if magic_bytes else 'None'}")
                        print(f"  Expected first byte: {ord('V')} (V)")
                        expected_bits = [(ord('V') >> i) & 1 for i in range(8)]
                        print(f"  Expected first byte bits: {expected_bits}")
                    
                    extracted_magic = bytes(magic_bytes)
                    if extracted_magic == self.magic_header:
                        print(f"[VideoStego] ✅ Found correct redundancy: {try_redundancy}x")
                        success = True
                        break
                    else:
                        print(f"[VideoStego] ❌ {try_redundancy}x redundancy failed magic test")
                        print(f"  Expected: {self.magic_header}")
                        print(f"  Got:      {extracted_magic}")
                        print(f"  First 10 magic bits: {magic_bits[:min(80, len(magic_bits))]}")
                
                if success:
                    break
            
            if not success:
                print(f"[VideoStego] ❌ Could not find correct redundancy level")
                return None, None
            
            # Now extract the full message with the correct redundancy
            print(f"[VideoStego] Extracting full message with {try_redundancy}x redundancy...")
            
            # Reset video capture to start from beginning for full extraction
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            all_extracted_bits = []  # Reset bits array for clean full extraction
            frame_count = 0
            
            # Continue extracting if we need more data
            while len(all_extracted_bits) < 50000 and frame_count < total_frames:
                ret, frame = read_frame(frame_count)
                if not ret:
                    break
                
                height, width = frame.shape[:2]
                
                if len(frame.shape) == 3:
                    flat_frame = frame.reshape(-1, 3)
                else:
                    flat_frame = frame.reshape(-1, 1)
                
                channels = flat_frame.shape[1]
                pixel_count = 0
                current_bit_votes = []
                
                for pixel_idx in range(flat_frame.shape[0]):
                    for channel in range(channels):
                        bit_value = int(flat_frame[pixel_idx, channel]) & 1
                        current_bit_votes.append(bit_value)
                        pixel_count += 1
                        
                        if pixel_count % try_redundancy == 0:
                            if len(current_bit_votes) > 0:
                                final_bit = 1 if sum(current_bit_votes) > len(current_bit_votes) // 2 else 0
                                all_extracted_bits.append(final_bit)
                                current_bit_votes = []
                
                frame_count += 1
            
            extraction_time = time.time() - start_time
            print(f"[VideoStego] Fast extraction: {len(all_extracted_bits)} bits in {extraction_time:.2f}s")
            
            if len(all_extracted_bits) < len(self.magic_header) * 8:
                print(f"[VideoStego] ❌ Not enough bits for magic header")
                return None, None
            
            # Check magic header
            magic_header_bits_needed = len(self.magic_header) * 8
            magic_bits = all_extracted_bits[:magic_header_bits_needed]
            
            # Convert bits to bytes for magic header
            magic_bytes = []
            print(f"[VideoStego] First 32 extracted bits: {magic_bits[:32]}")
            
            for i in range(0, magic_header_bits_needed, 8):
                if i + 8 <= len(magic_bits):
                    byte_bits = magic_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    magic_bytes.append(byte_value)
                    
                    # Debug first few bytes
                    if len(magic_bytes) <= 3:
                        print(f"[VideoStego] Byte {len(magic_bytes)}: bits={byte_bits} -> value={byte_value} ('{chr(byte_value) if 32 <= byte_value <= 126 else '?'}')")
            
            extracted_magic = bytes(magic_bytes)
            print(f"[VideoStego] Extracted magic: {extracted_magic}")
            print(f"[VideoStego] Expected magic: {self.magic_header}")
            
            if extracted_magic != self.magic_header:
                print(f"[VideoStego] ❌ Magic header not found")
                return None, None
            
            print(f"[VideoStego] ✅ Magic header found!")
            
            # Extract metadata size (4 bytes)
            metadata_size_start = magic_header_bits_needed
            metadata_size_end = metadata_size_start + 32
            
            if len(all_extracted_bits) < metadata_size_end:
                print(f"[VideoStego] ❌ Not enough bits for metadata size")
                return None, None
            
            metadata_size_bits = all_extracted_bits[metadata_size_start:metadata_size_end]
            
            # Convert metadata size bits to integer
            metadata_size_bytes = []
            for i in range(0, 32, 8):
                byte_bits = metadata_size_bits[i:i+8]
                byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                metadata_size_bytes.append(byte_value)
            
            metadata_size = struct.unpack('<I', bytes(metadata_size_bytes))[0]
            print(f"[VideoStego] Metadata size: {metadata_size} bytes")
            
            if metadata_size <= 0 or metadata_size > 10000:
                print(f"[VideoStego] ❌ Invalid metadata size: {metadata_size}")
                return None, None
            
            # Extract metadata
            metadata_start = metadata_size_end
            metadata_end = metadata_start + (metadata_size * 8)
            
            if len(all_extracted_bits) < metadata_end:
                print(f"[VideoStego] ❌ Not enough bits for metadata")
                return None, None
            
            metadata_bits = all_extracted_bits[metadata_start:metadata_end]
            
            # Convert metadata bits to bytes
            metadata_bytes = []
            for i in range(0, metadata_size * 8, 8):
                byte_bits = metadata_bits[i:i+8]
                byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                metadata_bytes.append(byte_value)
            
            metadata_json = bytes(metadata_bytes).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            print(f"[VideoStego] Found metadata: {metadata['filename']}, {metadata['size']} bytes")
            
            # Extract actual data
            data_size = metadata['size']
            data_start = metadata_end
            data_end = data_start + (data_size * 8)
            
            if len(all_extracted_bits) < data_end:
                print(f"[VideoStego] ❌ Not enough bits for data")
                return None, None
            
            data_bits = all_extracted_bits[data_start:data_end]
            
            # Convert data bits to bytes
            data_bytes = []
            for i in range(0, data_size * 8, 8):
                byte_bits = data_bits[i:i+8]
                byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                data_bytes.append(byte_value)
            
            extracted_data = bytes(data_bytes)
            
            # Verify checksum
            expected_checksum = metadata['checksum']
            actual_checksum = self._calculate_checksum(extracted_data)
            
            print(f"[VideoStego] Checksum verification:")
            print(f"  Expected: {expected_checksum}")
            print(f"  Actual:   {actual_checksum}")
            print(f"  Match: {'✅' if expected_checksum == actual_checksum else '❌'}")
            
            if expected_checksum != actual_checksum:
                print(f"[VideoStego] ⚠️ Checksum mismatch - data may be corrupted")
            
            print(f"[VideoStego] ✅ Successfully extracted {len(extracted_data)} bytes")
            print(f"[VideoStego] Returning filename: {repr(metadata['filename'])}")
            print(f"[VideoStego] Data type: {type(extracted_data)}")
            print(f"[VideoStego] Data preview: {extracted_data[:50] if len(extracted_data) > 50 else extracted_data}")
            
            # 🎯 CHECK FOR LAYERED CONTAINER - Override filename if layered container detected
            if isinstance(extracted_data, bytes):
                try:
                    decoded_data = extracted_data.decode('utf-8')
                    import json
                    parsed_data = json.loads(decoded_data)
                    
                    if (isinstance(parsed_data, dict) and 
                        parsed_data.get('type') == 'layered_container' and
                        'layers' in parsed_data and len(parsed_data['layers']) > 0):
                        
                        # Extract filename from first layer
                        first_layer = parsed_data['layers'][0]
                        if isinstance(first_layer, dict) and 'filename' in first_layer:
                            original_filename = first_layer['filename']
                            print(f"[VideoStego] 🎯 LAYERED CONTAINER DETECTED! Overriding filename from '{metadata['filename']}' to '{original_filename}'")
                            metadata['filename'] = original_filename
                            
                            # Extract the actual file content
                            if 'content' in first_layer:
                                import base64
                                actual_file_data = base64.b64decode(first_layer['content'])
                                print(f"[VideoStego] 📁 Extracted original file content: {len(actual_file_data)} bytes")
                                extracted_data = actual_file_data
                        else:
                            print(f"[VideoStego] ⚠️ Layered container found but no filename in first layer")
                    else:
                        print(f"[VideoStego] 📋 Not a layered container (type: {parsed_data.get('type', 'unknown')})")
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    print(f"[VideoStego] 📋 Not a text/JSON container: {e}")
                except Exception as e:
                    print(f"[VideoStego] ❌ Error checking for layered container: {e}")
            
            # Cleanup
            if not os.path.isdir(video_path):
                cap.release()
            
            return extracted_data, metadata['filename']
            
        except Exception as e:
            print(f"[VideoStego] ❌ Extraction failed: {e}")
            # Cleanup on error
            try:
                if not os.path.isdir(video_path):
                    cap.release()
            except:
                pass
            return None, None


class VideoSteganographyManager:
    """Manager class for video steganography operations"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.video_stego = VideoSteganography(password)
    
    def hide_data(self, video_path: str, payload: Union[str, bytes], 
                  output_path: str, is_file: bool = False, filename: str = None) -> Dict[str, Any]:
        """Hide data in video container"""
        try:
            # If it's a file, preserve the original filename
            detected_filename = None
            if is_file:
                if isinstance(payload, str) and os.path.isfile(payload):
                    # Payload is a file path
                    detected_filename = os.path.basename(payload)
                    print(f"[VideoManager] Detected filename from path: {detected_filename}")
                elif filename:
                    # Payload is bytes but we have the filename separately
                    detected_filename = filename
                    print(f"[VideoManager] Using provided filename: {detected_filename}")
            
            result = self.video_stego.embed_data(video_path, payload, output_path, detected_filename)
            
            if result.get('success'):
                result.update({
                    'container_type': 'video',
                    'method': 'LSB_video_steganography'
                })
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_data(self, video_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract hidden data from video container"""
        return self.video_stego.extract_data(video_path)
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video file information and capacity"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {'error': f'Cannot open video: {video_path}'}
            
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate capacity
            pixels_per_frame = width * height * 3  # RGB channels
            total_pixels = pixels_per_frame * total_frames
            max_bytes = total_pixels // (8 * 3)  # 3x redundancy, 8 bits per byte
            
            cap.release()
            
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'total_frames': total_frames,
                'duration_seconds': total_frames / fps if fps > 0 else 0,
                'total_pixels': total_pixels,
                'max_capacity_bytes': max_bytes,
                'max_capacity_kb': max_bytes / 1024,
                'max_capacity_mb': max_bytes / (1024 * 1024)
            }
            
        except Exception as e:
            return {'error': str(e)}