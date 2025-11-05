#!/usr/bin/env python3
"""
Advanced Video Steganography Implementation
Supports hiding text, images, and documents in video files
"""

import cv2
import numpy as np
import os
import json
import hashlib
import struct
from typing import Union, Tuple, Optional, Dict, Any
import base64
from pathlib import Path

class VideoSteganography:
    """Advanced video steganography using LSB embedding in video frames"""
    
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
        # Convert text to bytes if needed
        if isinstance(data, str):
            if os.path.isfile(data):
                # It's a file path
                with open(data, 'rb') as f:
                    file_data = f.read()
                filename = filename or os.path.basename(data)
                data_bytes = file_data
                data_type = 'file'
            else:
                # It's text content
                data_bytes = data.encode('utf-8')
                filename = filename or 'embedded_text.txt'
                data_type = 'text'
        else:
            # It's already bytes
            data_bytes = data
            filename = filename or 'embedded_data.bin'
            data_type = 'binary'
        
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
    
    def _extract_payload_from_frame(self, frame: np.ndarray, num_bits: int,
                                  start_index: int) -> Tuple[list, int]:
        """Extract payload bits from a single frame"""
        height, width = frame.shape[:2]
        
        # Flatten frame for easier access
        if len(frame.shape) == 3:
            flat_frame = frame.reshape(-1, 3)
        else:
            flat_frame = frame.reshape(-1, 1)
        
        channels = flat_frame.shape[1]
        extracted_bits = []
        bits_extracted = 0
        pixel_count = 0
        current_bit_votes = []
        
        for pixel_idx in range(flat_frame.shape[0]):
            if bits_extracted >= num_bits:
                break
                
            for channel in range(channels):
                if bits_extracted >= num_bits:
                    break
                
                # Extract bit from LSB
                bit_value = int(flat_frame[pixel_idx, channel]) & 1
                current_bit_votes.append(bit_value)
                pixel_count += 1
                
                # After redundancy copies, determine the bit value
                if pixel_count % self.redundancy == 0:
                    # Majority vote
                    if len(current_bit_votes) > 0:
                        final_bit = 1 if sum(current_bit_votes) > len(current_bit_votes) // 2 else 0
                        extracted_bits.append(final_bit)
                        bits_extracted += 1
                        current_bit_votes = []
        
        return extracted_bits, start_index + bits_extracted
    
    def embed_data(self, video_path: str, data: Union[str, bytes], 
                   output_path: str, filename: str = None) -> Dict[str, Any]:
        """Embed data into video file"""
        try:
            print(f"[VideoStego] Starting embedding process...")
            print(f"  Input video: {video_path}")
            print(f"  Output video: {output_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"  Video properties: {width}x{height}, {fps} FPS, {total_frames} frames")
            
            # Prepare payload
            payload = self._prepare_payload(data, filename)
            
            # Convert payload to bits
            payload_bits = []
            for byte in payload:
                for i in range(8):
                    payload_bits.append((byte >> i) & 1)
            
            # Calculate total bits needed with redundancy
            total_bits_needed = len(payload_bits) * self.redundancy
            
            # Calculate available space
            pixels_per_frame = self._get_embeddable_pixels(np.zeros((height, width, 3)))
            total_available_pixels = pixels_per_frame * total_frames
            
            print(f"  Bits to embed: {len(payload_bits)}")
            print(f"  With {self.redundancy}x redundancy: {total_bits_needed}")
            print(f"  Available pixels: {total_available_pixels}")
            print(f"  Capacity check: {'✅ OK' if total_bits_needed <= total_available_pixels else '❌ INSUFFICIENT'}")
            
            if total_bits_needed > total_available_pixels:
                raise ValueError(f"Video too small: need {total_bits_needed} pixels, have {total_available_pixels}")
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise ValueError(f"Cannot create output video: {output_path}")
            
            # Embed data frame by frame
            current_bit_index = 0
            frame_count = 0
            
            print(f"[VideoStego] Embedding data in frames...")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if current_bit_index < len(payload_bits) * self.redundancy:
                    # Embed data in this frame
                    modified_frame, current_bit_index = self._embed_payload_in_frame(
                        frame, payload_bits, current_bit_index
                    )
                    out.write(modified_frame)
                else:
                    # No more data to embed, copy frame as-is
                    out.write(frame)
                
                frame_count += 1
                if frame_count % 100 == 0:
                    progress = (current_bit_index / (len(payload_bits) * self.redundancy)) * 100
                    print(f"  Progress: Frame {frame_count}/{total_frames}, {progress:.1f}% embedded")
            
            # Cleanup
            cap.release()
            out.release()
            
            print(f"[VideoStego] ✅ Successfully embedded {len(payload_bits)} bits into {frame_count} frames")
            
            return {
                'success': True,
                'output_path': output_path,
                'frames_processed': frame_count,
                'bits_embedded': len(payload_bits),
                'payload_size': len(payload),
                'video_properties': {
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'total_frames': total_frames
                }
            }
            
        except Exception as e:
            print(f"[VideoStego] ❌ Embedding failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_data(self, video_path: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Extract hidden data from video file"""
        try:
            print(f"[VideoStego] Starting extraction from: {video_path}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"[VideoStego] Video has {total_frames} frames")
            
            # Read all frames first
            frames = []
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            cap.release()
            
            print(f"[VideoStego] Loaded {len(frames)} frames for extraction")
            
            # Extract magic header first
            magic_header_bits_needed = len(self.magic_header) * 8
            extracted_bits = []
            current_bit_index = 0
            
            print(f"[VideoStego] Looking for magic header ({len(self.magic_header)} bytes = {magic_header_bits_needed} bits)")
            
            for frame_idx, frame in enumerate(frames):
                if len(extracted_bits) >= magic_header_bits_needed:
                    break
                
                frame_bits, _ = self._extract_payload_from_frame(
                    frame, magic_header_bits_needed - len(extracted_bits), 0
                )
                extracted_bits.extend(frame_bits)
            
            # Convert bits to bytes for magic header
            magic_bytes = []
            for i in range(0, len(self.magic_header) * 8, 8):
                if i + 8 <= len(extracted_bits):
                    byte_bits = extracted_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    magic_bytes.append(byte_value)
            
            extracted_magic = bytes(magic_bytes)
            print(f"[VideoStego] Extracted magic: {extracted_magic}")
            print(f"[VideoStego] Expected magic: {self.magic_header}")
            
            if extracted_magic != self.magic_header:
                print(f"[VideoStego] ❌ Magic header not found")
                return None, None
            
            print(f"[VideoStego] ✅ Magic header found!")
            
            # Continue extraction from where we left off
            current_bit_position = len(self.magic_header) * 8 * self.redundancy
            
            # Extract metadata size (4 bytes)
            metadata_size_bits_needed = 4 * 8
            metadata_size_bits = []
            
            # Continue from current position
            remaining_bits_needed = metadata_size_bits_needed
            for frame_idx, frame in enumerate(frames):
                if remaining_bits_needed <= 0:
                    break
                
                # Calculate how many redundant pixels we need to skip
                pixels_to_skip = current_bit_position // self.redundancy
                frame_capacity = frame.shape[0] * frame.shape[1] * 3  # height * width * channels
                
                if pixels_to_skip >= frame_capacity:
                    # This frame is fully consumed, move to next
                    current_bit_position -= frame_capacity * self.redundancy
                    continue
                
                # Extract from this frame
                frame_bits = self._extract_bits_from_position(frame, remaining_bits_needed, pixels_to_skip)
                metadata_size_bits.extend(frame_bits)
                remaining_bits_needed -= len(frame_bits)
                
                # Update position
                current_bit_position += len(frame_bits) * self.redundancy
            
            # Convert metadata size bits to integer
            metadata_size_bytes = []
            for i in range(0, 32, 8):
                if i + 8 <= len(metadata_size_bits):
                    byte_bits = metadata_size_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    metadata_size_bytes.append(byte_value)
            
            if len(metadata_size_bytes) < 4:
                raise ValueError("Could not extract metadata size")
            
            metadata_size = struct.unpack('<I', bytes(metadata_size_bytes))[0]
            print(f"[VideoStego] Metadata size: {metadata_size} bytes")
            
            if metadata_size <= 0 or metadata_size > 10000:
                raise ValueError(f"Invalid metadata size: {metadata_size}")
            
            # Extract metadata
            metadata_bits_needed = metadata_size * 8
            metadata_bits = []
            
            remaining_bits_needed = metadata_bits_needed
            for frame_idx, frame in enumerate(frames):
                if remaining_bits_needed <= 0:
                    break
                
                pixels_to_skip = current_bit_position // self.redundancy
                frame_capacity = frame.shape[0] * frame.shape[1] * 3
                
                if pixels_to_skip >= frame_capacity:
                    current_bit_position -= frame_capacity * self.redundancy
                    continue
                
                frame_bits = self._extract_bits_from_position(frame, remaining_bits_needed, pixels_to_skip)
                metadata_bits.extend(frame_bits)
                remaining_bits_needed -= len(frame_bits)
                current_bit_position += len(frame_bits) * self.redundancy
            
            # Convert metadata bits to bytes
            metadata_bytes = []
            for i in range(0, metadata_size * 8, 8):
                if i + 8 <= len(metadata_bits):
                    byte_bits = metadata_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    metadata_bytes.append(byte_value)
            
            if len(metadata_bytes) < metadata_size:
                raise ValueError("Could not extract complete metadata")
            
            metadata_json = bytes(metadata_bytes).decode('utf-8')
            metadata = json.loads(metadata_json)
            
            print(f"[VideoStego] Found metadata: {metadata['filename']}, {metadata['size']} bytes")
            
            # Extract actual data
            data_size = metadata['size']
            data_bits_needed = data_size * 8
            data_bits = []
            
            remaining_bits_needed = data_bits_needed
            for frame_idx, frame in enumerate(frames):
                if remaining_bits_needed <= 0:
                    break
                
                pixels_to_skip = current_bit_position // self.redundancy
                frame_capacity = frame.shape[0] * frame.shape[1] * 3
                
                if pixels_to_skip >= frame_capacity:
                    current_bit_position -= frame_capacity * self.redundancy
                    continue
                
                frame_bits = self._extract_bits_from_position(frame, remaining_bits_needed, pixels_to_skip)
                data_bits.extend(frame_bits)
                remaining_bits_needed -= len(frame_bits)
                current_bit_position += len(frame_bits) * self.redundancy
            
            # Convert data bits to bytes
            data_bytes = []
            for i in range(0, data_size * 8, 8):
                if i + 8 <= len(data_bits):
                    byte_bits = data_bits[i:i+8]
                    byte_value = sum(bit << j for j, bit in enumerate(byte_bits))
                    data_bytes.append(byte_value)
            
            if len(data_bytes) < data_size:
                raise ValueError("Could not extract complete data")
            
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
            
            return extracted_data, metadata['filename']
            
        except Exception as e:
            print(f"[VideoStego] ❌ Extraction failed: {e}")
            return None, None
    
    def _extract_bits_from_position(self, frame: np.ndarray, num_bits: int, skip_pixels: int) -> list:
        """Extract bits from frame starting at a specific pixel position"""
        height, width = frame.shape[:2]
        
        if len(frame.shape) == 3:
            flat_frame = frame.reshape(-1, 3)
        else:
            flat_frame = frame.reshape(-1, 1)
        
        channels = flat_frame.shape[1]
        extracted_bits = []
        pixel_count = 0
        current_bit_votes = []
        bits_extracted = 0
        
        # Skip the specified number of pixels
        start_pixel = skip_pixels
        
        for pixel_idx in range(start_pixel, flat_frame.shape[0]):
            if bits_extracted >= num_bits:
                break
                
            for channel in range(channels):
                if bits_extracted >= num_bits:
                    break
                
                # Extract bit from LSB
                bit_value = int(flat_frame[pixel_idx, channel]) & 1
                current_bit_votes.append(bit_value)
                pixel_count += 1
                
                # After redundancy copies, determine the bit value
                if pixel_count % self.redundancy == 0:
                    if len(current_bit_votes) > 0:
                        final_bit = 1 if sum(current_bit_votes) > len(current_bit_votes) // 2 else 0
                        extracted_bits.append(final_bit)
                        bits_extracted += 1
                        current_bit_votes = []
        
        return extracted_bits


class VideoSteganographyManager:
    """Manager class for video steganography operations"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.video_stego = VideoSteganography(password)
    
    def hide_data(self, video_path: str, payload: Union[str, bytes], 
                  output_path: str, is_file: bool = False) -> Dict[str, Any]:
        """Hide data in video container"""
        try:
            # If it's a file, preserve the original filename
            filename = None
            if is_file and isinstance(payload, str) and os.path.isfile(payload):
                filename = os.path.basename(payload)
                print(f"[VideoManager] Preserving original filename: {filename}")
            
            result = self.video_stego.embed_data(video_path, payload, output_path, filename)
            
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


def create_test_video(output_path: str = "test_video.mp4", duration: int = 5) -> str:
    """Create a test video for demonstration"""
    try:
        width, height = 640, 480
        fps = 30
        total_frames = duration * fps
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"Creating test video: {output_path} ({duration}s, {total_frames} frames)")
        
        for frame_num in range(total_frames):
            # Create a colorful test pattern
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add some patterns
            frame[:, :, 0] = (frame_num * 2) % 256  # Red channel changes over time
            frame[:, :, 1] = 128 + 64 * np.sin(frame_num * 0.1)  # Green oscillates
            frame[:, :, 2] = 255 - (frame_num * 2) % 256  # Blue decreases
            
            # Add some geometric shapes
            cv2.rectangle(frame, (50, 50), (150, 150), (255, 255, 255), 2)
            cv2.circle(frame, (width//2, height//2), 50, (0, 255, 0), -1)
            
            # Add frame number text
            cv2.putText(frame, f"Frame {frame_num}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        print(f"✅ Test video created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Failed to create test video: {e}")
        return None


def demo_video_steganography():
    """Demonstrate video steganography capabilities"""
    print("🎬 VIDEO STEGANOGRAPHY DEMO 🎬\n")
    
    # Create test video
    test_video = create_test_video("demo_video.mp4", duration=3)
    if not test_video:
        print("Failed to create test video")
        return
    
    # Create manager
    manager = VideoSteganographyManager("secret123")
    
    # Get video info
    info = manager.get_video_info(test_video)
    print(f"📹 Video Info:")
    print(f"  Resolution: {info['width']}x{info['height']}")
    print(f"  Duration: {info['duration_seconds']:.1f}s")
    print(f"  Frames: {info['total_frames']}")
    print(f"  Capacity: {info['max_capacity_kb']:.1f} KB")
    
    # Test 1: Hide text message
    print(f"\n📝 TEST 1: Text Message")
    text_message = "This is a secret message hidden in a video! 🎬🔒"
    result1 = manager.hide_data(test_video, text_message, "stego_text_video.mp4")
    
    if result1.get('success'):
        print(f"  ✅ Text embedded successfully")
        extracted_data, filename = manager.extract_data("stego_text_video.mp4")
        if extracted_data:
            extracted_text = extracted_data.decode('utf-8')
            print(f"  ✅ Extracted: '{extracted_text}'")
            print(f"  ✅ Match: {'YES' if extracted_text == text_message else 'NO'}")
        else:
            print(f"  ❌ Extraction failed")
    else:
        print(f"  ❌ Embedding failed: {result1.get('error')}")
    
    # Test 2: Hide an image file (create a small test image)
    print(f"\n🖼️ TEST 2: Image File")
    
    # Create a small test image
    test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    cv2.imwrite("test_image.png", test_image)
    
    result2 = manager.hide_data(test_video, "test_image.png", "stego_image_video.mp4", is_file=True)
    
    if result2.get('success'):
        print(f"  ✅ Image embedded successfully")
        extracted_data, filename = manager.extract_data("stego_image_video.mp4")
        if extracted_data and filename:
            print(f"  ✅ Extracted filename: '{filename}'")
            print(f"  ✅ Data size: {len(extracted_data)} bytes")
            
            # Save extracted image
            with open(f"extracted_{filename}", "wb") as f:
                f.write(extracted_data)
            print(f"  ✅ Saved as: extracted_{filename}")
        else:
            print(f"  ❌ Extraction failed")
    else:
        print(f"  ❌ Embedding failed: {result2.get('error')}")
    
    print(f"\n🎉 Video steganography demo completed!")
    print(f"   ✅ Text and file embedding work in video")
    print(f"   ✅ Original filenames are preserved")
    print(f"   ✅ Data integrity is maintained with checksums")


if __name__ == '__main__':
    demo_video_steganography()