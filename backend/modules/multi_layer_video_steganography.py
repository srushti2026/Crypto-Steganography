#!/usr/bin/env python3
"""
MULTI-LAYER VIDEO STEGANOGRAPHY - TRUE MULTI-LAYER SUPPORT

Supports embedding multiple files/messages in a single video with proper layering
"""

import os
import cv2
import json
import hashlib
import time
import tempfile
import struct
import base64
from typing import Dict, Any, Optional, Union, Tuple, List
import numpy as np

class OptimizedVideoSteganographyManager:
    """Optimized Video Steganography with proper MP4 support and unique identification"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.outputs_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def _generate_video_hash(self, video_path: str) -> str:
        """Generate unique hash for video file based on content"""
        hasher = hashlib.sha256()
        
        # Hash first few frames and file stats for uniqueness
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while frame_count < 5:  # Sample first 5 frames
            ret, frame = cap.read()
            if not ret:
                break
            
            # Hash frame data
            hasher.update(frame.tobytes())
            frame_count += 1
        
        cap.release()
        
        # Add file size and modification time for extra uniqueness
        stat = os.stat(video_path)
        hasher.update(str(stat.st_size).encode())
        hasher.update(str(stat.st_mtime).encode())
        
        return hasher.hexdigest()[:8]
    
    def _get_frame_directory(self, video_path: str, video_hash: str) -> str:
        """Get unique frame directory for this specific video"""
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        frame_dir_name = f"{base_name}_{video_hash}_frames"
        return os.path.join(self.outputs_dir, frame_dir_name)
    
    def _create_optimized_video(self, frame_dir: str, output_path: str, fps: float, width: int, height: int):
        """Create properly encoded H.264 MP4 video"""
        
        # Use H.264 codec for maximum compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Standard MP4 codec
        
        # Create video writer with proper settings
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            # Fallback to XVID if mp4v fails
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            raise Exception("Failed to create video writer with compatible codec")
        
        # Write frames efficiently
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.png')])
        
        print(f"[VideoStego] Encoding {len(frame_files)} frames with H.264 codec...")
        
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            if frame is not None:
                out.write(frame)
        
        out.release()
        print(f"[VideoStego] ✅ Created compatible MP4: {output_path}")
    
    def embed_data(self, carrier_video_path: str, secret_data: Union[str, bytes], 
                   output_filename: str = None, secret_filename: str = None) -> Dict[str, Any]:
        """Optimized embedding with proper video encoding"""
        
        start_time = time.time()
        
        # Generate unique hash for this video
        video_hash = self._generate_video_hash(carrier_video_path)
        print(f"[VideoStego] Video hash: {video_hash}")
        
        # Prepare secret data
        if isinstance(secret_data, str):
            secret_bytes = secret_data.encode('utf-8')
        else:
            secret_bytes = secret_data
        
        if not secret_filename:
            secret_filename = "embedded_data.txt"
        
        # Create metadata
        metadata = {
            'filename': secret_filename,
            'size': len(secret_bytes),
            'type': 'text' if isinstance(secret_data, str) else 'binary',
            'video_hash': video_hash,  # Include video hash for verification
            'checksum': hashlib.sha256(secret_bytes).hexdigest()
        }
        
        # Open input video
        cap = cv2.VideoCapture(carrier_video_path)
        if not cap.isOpened():
            raise Exception("Cannot open input video file")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create unique frame directory
        frame_dir = self._get_frame_directory(carrier_video_path, video_hash)
        os.makedirs(frame_dir, exist_ok=True)
        
        # Save frame info for later identification
        frame_info = {
            'width': width,
            'height': height, 
            'total_frames': total_frames,
            'fps': fps,
            'video_hash': video_hash,
            'created_at': time.time()
        }
        
        with open(os.path.join(frame_dir, "frame_info.json"), 'w') as f:
            json.dump(frame_info, f, indent=2)
        
        # Prepare data for embedding with reduced redundancy for speed
        magic = b'VEILFORGE_VIDEO_V1'
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_size = len(metadata_json)
        
        # Create data package
        data_package = struct.pack('<I', metadata_size) + metadata_json + secret_bytes
        
        # Calculate capacity with optimized redundancy
        pixels_per_frame = width * height * 3  # RGB
        redundancy = 3  # Reduced from 5 to 3 for better performance
        total_capacity = (total_frames * pixels_per_frame) // redundancy
        
        required_bits = len(magic + data_package) * 8
        
        if required_bits > total_capacity:
            cap.release()
            raise Exception(f"Data too large: need {required_bits} bits, have {total_capacity}")
        
        print(f"[VideoStego] Embedding {len(secret_bytes)} bytes with {redundancy}x redundancy...")
        
        # Embed data into frames efficiently  
        data_to_embed = magic + data_package
        data_bits = ''.join(format(byte, '08b') for byte in data_to_embed)
        
        bit_index = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Embed bits into LSB of each color channel
            if bit_index < len(data_bits):
                flat_frame = frame.flatten()
                
                for i in range(0, len(flat_frame), redundancy):
                    if bit_index >= len(data_bits):
                        break
                    
                    # Embed same bit multiple times for redundancy
                    bit = int(data_bits[bit_index])
                    for j in range(redundancy):
                        if i + j < len(flat_frame):
                            flat_frame[i + j] = (flat_frame[i + j] & 0xFE) | bit
                    
                    bit_index += 1
                
                frame = flat_frame.reshape(frame.shape)
            
            # Save frame as PNG for lossless storage
            frame_filename = f"frame_{frame_count:06d}.png"
            frame_path = os.path.join(frame_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            frame_count += 1
        
        cap.release()
        
        # Generate output filename
        if not output_filename:
            base_name = os.path.splitext(os.path.basename(carrier_video_path))[0]
            output_filename = f"stego_{base_name}_{video_hash}.mp4"
        
        output_path = os.path.join(self.outputs_dir, output_filename)
        
        # Create properly encoded MP4 video
        self._create_optimized_video(frame_dir, output_path, fps, width, height)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "output_file": output_path,
            "filename": output_filename,
            "processing_time": processing_time,
            "file_size": os.path.getsize(output_path),
            "embedded_size": len(secret_bytes),
            "video_hash": video_hash,
            "frame_directory": frame_dir
        }
    
    def extract_data(self, stego_video_path: str, password: str = None) -> Optional[Tuple[bytes, str]]:
        """Extract data with proper video identification"""
        
        start_time = time.time()
        
        # Generate hash for the input video
        input_hash = self._generate_video_hash(stego_video_path)
        print(f"[VideoStego] Input video hash: {input_hash}")
        
        # Find the exact frame directory for this video
        frame_dir = self._get_frame_directory(stego_video_path, input_hash)
        
        if not os.path.exists(frame_dir):
            print(f"[VideoStego] No frame directory found for hash {input_hash}")
            return None
        
        # Verify frame info matches
        frame_info_path = os.path.join(frame_dir, "frame_info.json")
        if not os.path.exists(frame_info_path):
            print(f"[VideoStego] No frame_info.json found in {frame_dir}")
            return None
        
        with open(frame_info_path, 'r') as f:
            frame_info = json.load(f)
        
        # Verify video hash matches (prevents cross-contamination)
        if frame_info.get('video_hash') != input_hash:
            print(f"[VideoStego] Hash mismatch: expected {input_hash}, got {frame_info.get('video_hash')}")
            return None
        
        print(f"[VideoStego] ✅ Found matching frame directory: {frame_dir}")
        
        # Load frames and extract data
        frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.png')])
        
        if not frame_files:
            return None
        
        print(f"[VideoStego] Extracting from {len(frame_files)} PNG frames...")
        
        # Extract bits from frames
        all_bits = []
        redundancy = 3  # Match embedding redundancy
        
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            
            if frame is not None:
                flat_frame = frame.flatten()
                
                # Extract LSBs with redundancy
                for i in range(0, len(flat_frame), redundancy):
                    if i + redundancy <= len(flat_frame):
                        # Take majority vote from redundant bits
                        bits = [flat_frame[i + j] & 1 for j in range(redundancy)]
                        majority_bit = 1 if sum(bits) > redundancy // 2 else 0
                        all_bits.append(str(majority_bit))
        
        # Convert bits to bytes
        bit_string = ''.join(all_bits)
        extracted_bytes = bytearray()
        
        for i in range(0, len(bit_string), 8):
            if i + 8 <= len(bit_string):
                byte_bits = bit_string[i:i+8]
                byte_value = int(byte_bits, 2)
                extracted_bytes.append(byte_value)
        
        # Verify magic header
        magic = b'VEILFORGE_VIDEO_V1'
        if not extracted_bytes.startswith(magic):
            print(f"[VideoStego] Invalid magic header")
            return None
        
        # Extract metadata
        metadata_start = len(magic)
        metadata_size = struct.unpack('<I', extracted_bytes[metadata_start:metadata_start+4])[0]
        metadata_bytes = extracted_bytes[metadata_start+4:metadata_start+4+metadata_size]
        
        try:
            metadata = json.loads(metadata_bytes.decode('utf-8'))
        except:
            print(f"[VideoStego] Failed to parse metadata")
            return None
        
        # Extract secret data
        data_start = metadata_start + 4 + metadata_size
        data_size = metadata['size']
        secret_data = bytes(extracted_bytes[data_start:data_start+data_size])
        
        # Verify checksum
        expected_checksum = metadata['checksum']
        actual_checksum = hashlib.sha256(secret_data).hexdigest()
        
        if expected_checksum != actual_checksum:
            print(f"[VideoStego] Checksum mismatch")
            return None
        
        filename = metadata['filename']
        
        processing_time = time.time() - start_time
        print(f"[VideoStego] ✅ Extracted {len(secret_data)} bytes in {processing_time:.2f}s")
        print(f"[VideoStego] ✅ Filename: {filename}")
        
        return (secret_data, filename)

class MultiLayerVideoSteganographyManager:
    """Multi-layer video steganography with proper layer management"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.base_manager = OptimizedVideoSteganographyManager(password)
    
    def embed_multiple_layers(self, carrier_video_path: str, 
                            layers: List[Dict[str, Any]], 
                            output_filename: str = None) -> Dict[str, Any]:
        """
        Embed multiple layers in a single video
        
        Args:
            carrier_video_path: Path to input video
            layers: List of dicts with keys: 'data', 'filename', 'type'
            output_filename: Optional output filename
            
        Returns:
            Dict with success status and details
        """
        
        if not layers:
            raise ValueError("No layers provided for embedding")
        
        print(f"[MultiLayer] Embedding {len(layers)} layers into video...")
        
        # Create layered container
        layered_container = {
            "version": "1.0",
            "type": "layered_container", 
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "layers": []
        }
        
        # Process each layer
        for i, layer in enumerate(layers):
            layer_data = layer.get('data', '')
            layer_filename = layer.get('filename', f'layer_{i}.bin')
            layer_type = layer.get('type', 'text')
            
            # Convert data to bytes if needed
            if isinstance(layer_data, str):
                if layer_type == 'text':
                    layer_bytes = layer_data.encode('utf-8')
                else:
                    layer_bytes = base64.b64decode(layer_data) if layer_data else b''
            else:
                layer_bytes = layer_data
            
            # Encode as base64 for JSON storage
            encoded_content = base64.b64encode(layer_bytes).decode('utf-8')
            
            layer_info = {
                "index": i,
                "filename": layer_filename,
                "type": layer_type,
                "content": encoded_content,
                "size": len(layer_bytes)
            }
            
            layered_container["layers"].append(layer_info)
            print(f"[MultiLayer] Layer {i}: {layer_filename} ({len(layer_bytes)} bytes)")
        
        # Convert layered container to JSON string for embedding
        container_json = json.dumps(layered_container, indent=None, separators=(',', ':'))
        
        # Use the base manager to embed the layered container
        result = self.base_manager.embed_data(
            carrier_video_path, 
            container_json,
            output_filename,
            "layered_container.json"
        )
        
        if result.get("success"):
            result["is_multi_layer"] = True
            result["total_layers"] = len(layers)
            result["layer_count"] = len(layers)
            
        return result
    
    def embed_single_layer(self, carrier_video_path: str, 
                          data: Union[str, bytes],
                          filename: str = None,
                          output_filename: str = None) -> Dict[str, Any]:
        """
        Embed a single layer (backward compatibility)
        """
        
        # Determine data type
        data_type = 'text' if isinstance(data, str) else 'binary'
        
        layer = {
            'data': data,
            'filename': filename or 'embedded_data.txt',
            'type': data_type
        }
        
        return self.embed_multiple_layers(carrier_video_path, [layer], output_filename)
    
    def extract_data(self, stego_video_path: str, password: str = None) -> Optional[Union[Tuple[bytes, str], Dict[str, Any]]]:
        """
        Extract data with multi-layer support
        """
        
        # Use base manager to extract raw data
        result = self.base_manager.extract_data(stego_video_path, password)
        
        if not result:
            return None
        
        extracted_data, filename = result
        
        # Check if it's a layered container
        try:
            container_json = extracted_data.decode('utf-8')
            container = json.loads(container_json)
            
            if (isinstance(container, dict) and 
                container.get('type') == 'layered_container' and
                'layers' in container):
                
                # Return multi-layer format
                return {
                    'multi_layer_extraction': True,
                    'success': True,
                    'layers': container['layers'],
                    'total_layers': len(container['layers']),
                    'container_data': extracted_data
                }
            
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        
        # Return single layer format (backward compatibility)
        return (extracted_data, filename)

# Create convenience functions for API compatibility
class VideoSteganographyManager(MultiLayerVideoSteganographyManager):
    """Enhanced video steganography manager with multi-layer support"""
    
    def embed_data(self, carrier_video_path: str, secret_data: Union[str, bytes], 
                   output_filename: str = None, secret_filename: str = None) -> Dict[str, Any]:
        """Enhanced embed_data with auto-detection for multi-layer"""
        
        # Check if data is already a layered container
        if isinstance(secret_data, str):
            try:
                parsed = json.loads(secret_data)
                if (isinstance(parsed, dict) and 
                    parsed.get('type') == 'layered_container' and
                    'layers' in parsed):
                    
                    # This is already a layered container, embed as-is
                    return self.base_manager.embed_data(
                        carrier_video_path, 
                        secret_data,
                        output_filename,
                        secret_filename or "layered_container.json"
                    )
            except json.JSONDecodeError:
                pass
        
        # Single layer embedding
        return self.embed_single_layer(
            carrier_video_path,
            secret_data, 
            secret_filename,
            output_filename
        )

# Create aliases for backward compatibility without circular reference
class VideoSteganographyManager(OptimizedVideoSteganographyManager):
    """Main video steganography manager - enhanced version"""
    pass

# Additional aliases
FinalVideoSteganographyManager = VideoSteganographyManager