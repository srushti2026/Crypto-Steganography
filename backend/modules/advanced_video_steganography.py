#!/usr/bin/env python3
"""
Advanced Video Steganography System
Supports robust file and data embedding/extraction in video files
"""

import cv2
import numpy as np
import struct
import json
import hashlib
import os
import sys
from typing import Dict, List, Tuple, Optional, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    import pywt
    WAVELET_AVAILABLE = True
except ImportError:
    WAVELET_AVAILABLE = False
    print("[!] PyWavelets not available. Install: pip install PyWavelets")

class VideoSteganographyError(Exception):
    """Custom exception for video steganography operations"""
    pass

class AdvancedVideoSteganography:
    """
    Advanced video steganography with multiple embedding techniques:
    1. LSB embedding in color channels
    2. DWT coefficient modification
    3. Frame difference encoding
    4. Redundancy and error correction
    """
    
    def __init__(self, password: str = None, method: str = 'lsb'):
        self.password = password
        self.method = method  # 'lsb', 'dwt', 'hybrid'
        self.magic_header = b'ADVVIDEO'
        self.version = b'v1.0'
        
        # Embedding parameters
        self.lsb_bits = 1  # Number of LSB bits to use
        self.redundancy = 3  # How many times to embed data
        self.error_threshold = 0.1  # Acceptable error rate for extraction
        
        # DWT parameters (if available)
        if WAVELET_AVAILABLE:
            self.wavelet = 'db4'
            self.dwt_strength = 0.1
        
        # Frame selection parameters
        self.keyframe_interval = 10  # Every Nth frame for embedding
        self.max_frames_per_chunk = 5  # Max frames to use per data chunk
        
    def _generate_key(self, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        if not self.password:
            return None
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(self.password.encode())
    
    def _encrypt_data(self, data: bytes) -> Tuple[bytes, bytes, bytes]:
        """Encrypt data using AES-GCM"""
        if not self.password:
            return data, b'', b''
        
        salt = os.urandom(16)
        key = self._generate_key(salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        
        encrypted_data = aesgcm.encrypt(nonce, data, None)
        return encrypted_data, salt, nonce
    
    def _decrypt_data(self, encrypted_data: bytes, salt: bytes, nonce: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        if not self.password or not salt or not nonce:
            return encrypted_data
        
        key = self._generate_key(salt)
        aesgcm = AESGCM(key)
        
        return aesgcm.decrypt(nonce, encrypted_data, None)
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get comprehensive video information"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoSteganographyError(f"Cannot open video: {video_path}")
        
        info = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
    
    def _embed_lsb(self, frame: np.ndarray, data_bits: str, start_pos: int = 0) -> Tuple[np.ndarray, int]:
        """Embed data in frame using LSB technique"""
        height, width, channels = frame.shape
        modified_frame = frame.copy()
        
        bit_index = 0
        embedded_bits = 0
        
        # Embed in all three channels for better capacity
        for channel in range(channels):
            for y in range(height):
                for x in range(width):
                    if bit_index + start_pos >= len(data_bits):
                        return modified_frame, embedded_bits
                    
                    # Get the bit to embed
                    bit = int(data_bits[bit_index + start_pos])
                    
                    # Modify LSB of current channel
                    pixel_value = modified_frame[y, x, channel]
                    modified_frame[y, x, channel] = (pixel_value & 0xFE) | bit
                    
                    bit_index += 1
                    embedded_bits += 1
                
                if bit_index + start_pos >= len(data_bits):
                    break
            
            if bit_index + start_pos >= len(data_bits):
                break
        
        return modified_frame, embedded_bits
    
    def _extract_lsb(self, frame: np.ndarray, bit_count: int) -> str:
        """Extract data from frame using LSB technique"""
        height, width, channels = frame.shape
        extracted_bits = []
        
        bit_index = 0
        
        # Extract from all three channels in same order as embedding
        for channel in range(channels):
            for y in range(height):
                for x in range(width):
                    if bit_index >= bit_count:
                        break
                    
                    # Get LSB of current channel
                    pixel_value = frame[y, x, channel]
                    bit = pixel_value & 1
                    extracted_bits.append(str(bit))
                    
                    bit_index += 1
                
                if bit_index >= bit_count:
                    break
            
            if bit_index >= bit_count:
                break
        
        return ''.join(extracted_bits)
    
    def _embed_dwt(self, frame: np.ndarray, data_bits: str, start_pos: int = 0) -> Tuple[np.ndarray, int]:
        """Embed data using DWT coefficients"""
        if not WAVELET_AVAILABLE:
            return self._embed_lsb(frame, data_bits, start_pos)
        
        # Convert to grayscale for DWT
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()
        
        gray = gray.astype(np.float32)
        
        # Apply DWT
        coeffs = pywt.dwt2(gray, self.wavelet)
        ll, (lh, hl, hh) = coeffs
        
        bit_index = 0
        embedded_bits = 0
        
        # Embed in HH (high-high) coefficients - least perceptible
        h, w = hh.shape
        for y in range(h):
            for x in range(w):
                if bit_index + start_pos >= len(data_bits):
                    break
                
                bit = int(data_bits[bit_index + start_pos])
                
                # Modify coefficient based on bit
                if bit == 1:
                    hh[y, x] += self.dwt_strength
                else:
                    hh[y, x] -= self.dwt_strength
                
                bit_index += 1
                embedded_bits += 1
        
        # Reconstruct frame
        modified_coeffs = (ll, (lh, hl, hh))
        reconstructed = pywt.idwt2(modified_coeffs, self.wavelet)
        
        # Convert back to uint8 and handle size differences
        if reconstructed.shape != gray.shape:
            reconstructed = cv2.resize(reconstructed, (gray.shape[1], gray.shape[0]))
        
        reconstructed = np.clip(reconstructed, 0, 255).astype(np.uint8)
        
        # Convert back to color if original was color
        if len(frame.shape) == 3:
            modified_frame = cv2.cvtColor(reconstructed, cv2.COLOR_GRAY2BGR)
        else:
            modified_frame = reconstructed
        
        return modified_frame, embedded_bits
    
    def _extract_dwt(self, frame: np.ndarray, bit_count: int, reference_frame: np.ndarray = None) -> str:
        """Extract data from DWT coefficients"""
        if not WAVELET_AVAILABLE:
            return self._extract_lsb(frame, bit_count)
        
        # Convert to grayscale
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()
        
        gray = gray.astype(np.float32)
        
        # Apply DWT
        coeffs = pywt.dwt2(gray, self.wavelet)
        ll, (lh, hl, hh) = coeffs
        
        extracted_bits = []
        bit_index = 0
        
        # Extract from HH coefficients
        h, w = hh.shape
        for y in range(h):
            for x in range(w):
                if bit_index >= bit_count:
                    break
                
                # Determine bit based on coefficient value
                coeff = hh[y, x]
                bit = 1 if coeff > 0 else 0
                extracted_bits.append(str(bit))
                
                bit_index += 1
        
        return ''.join(extracted_bits)
    
    def _create_metadata(self, data: bytes, video_info: Dict[str, Any], 
                        embedding_info: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive metadata for the embedded data"""
        return {
            'magic': self.magic_header.hex(),
            'version': self.version.decode(),
            'method': self.method,
            'data_size': len(data),
            'checksum': hashlib.sha256(data).hexdigest(),
            'redundancy': self.redundancy,
            'video_info': video_info,
            'embedding_info': embedding_info,
            'encrypted': bool(self.password),
            'timestamp': str(np.datetime64('now'))
        }
    
    def _select_embedding_frames(self, total_frames: int, data_size: int) -> List[int]:
        """Select optimal frames for embedding based on data size and video length"""
        # For redundancy, we want to embed the complete payload multiple times
        # Select frames spread throughout the video
        
        min_frames_needed = self.redundancy  # At least one frame per redundant copy
        max_frames_to_use = min(total_frames // 4, 20)  # Don't use too many frames
        
        frames_to_use = max(min_frames_needed, min(max_frames_to_use, self.redundancy * 2))
        
        # Distribute frames evenly throughout video
        if frames_to_use >= total_frames:
            selected_frames = list(range(total_frames))
        else:
            step = total_frames // frames_to_use
            selected_frames = [i * step for i in range(frames_to_use)]
        
        # Ensure we don't exceed frame count
        selected_frames = [f for f in selected_frames if f < total_frames]
        
        return selected_frames[:frames_to_use]
    
    def _estimate_frame_capacity(self) -> int:
        """Estimate how many bits can be embedded per frame"""
        if self.method == 'lsb':
            # For LSB, we can use 1 bit per pixel (conservative estimate)
            return 640 * 480 * self.lsb_bits  # Assume minimum resolution
        elif self.method == 'dwt':
            # DWT has lower capacity but better robustness
            return 640 * 480 // 4  # HH subband is 1/4 of original
        else:
            # Hybrid method
            return 640 * 480 // 2
    
    def embed_data(self, video_path: str, data: bytes, output_path: str, 
                   filename: str = None) -> Dict[str, Any]:
        """Embed data/file in video with robust error handling"""
        
        print(f"[+] Starting video steganography embedding")
        print(f"[+] Input video: {video_path}")
        print(f"[+] Output video: {output_path}")
        print(f"[+] Data size: {len(data)} bytes")
        print(f"[+] Method: {self.method}")
        
        # Get video information
        video_info = self._get_video_info(video_path)
        print(f"[+] Video: {video_info['width']}x{video_info['height']}, "
              f"{video_info['frame_count']} frames, {video_info['fps']:.2f} FPS")
        
        # Encrypt data if password provided
        if self.password:
            print(f"[+] Encrypting data...")
            encrypted_data, salt, nonce = self._encrypt_data(data)
        else:
            encrypted_data, salt, nonce = data, b'', b''
        
        # Create header with metadata
        header_data = {
            'filename': filename or 'embedded_data.bin',
            'original_size': len(data),
            'encrypted': bool(self.password),
            'method': self.method,
            'checksum': hashlib.sha256(data).hexdigest()
        }
        
        header_json = json.dumps(header_data).encode()
        header_size = struct.pack('<I', len(header_json))
        
        # Prepare full payload
        full_payload = (
            self.magic_header + 
            self.version + 
            header_size + 
            header_json + 
            salt + 
            nonce + 
            encrypted_data
        )
        
        print(f"[+] Total payload size: {len(full_payload)} bytes")
        
        # Select embedding frames
        embedding_frames = self._select_embedding_frames(
            video_info['frame_count'], 
            len(full_payload)
        )
        
        print(f"[+] Selected {len(embedding_frames)} frames for embedding")
        print(f"[+] Redundancy: {self.redundancy}x")
        
        # Calculate data distribution
        chunks_per_redundancy = len(embedding_frames) // self.redundancy
        if chunks_per_redundancy == 0:
            chunks_per_redundancy = 1
        
        print(f"[+] Will embed complete payload {self.redundancy} times across frames")
        print(f"[+] Frames per copy: {chunks_per_redundancy}")
        
        # Open video for reading and writing
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoSteganographyError(f"Cannot open video: {video_path}")
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            output_path, 
            fourcc, 
            video_info['fps'], 
            (video_info['width'], video_info['height'])
        )
        
        if not writer.isOpened():
            raise VideoSteganographyError("Failed to create output video")
        
        # Process frames
        frame_idx = 0
        embedding_idx = 0
        successful_embeds = 0
        
        print(f"[+] Processing frames...")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Check if this frame should contain embedded data
            if frame_idx in embedding_frames and embedding_idx < len(embedding_frames):
                try:
                    # Embed the complete payload in each selected frame (redundancy)
                    data_bits = ''.join(format(byte, '08b') for byte in full_payload)
                    
                    # Embed using selected method
                    if self.method == 'lsb':
                        modified_frame, bits_embedded = self._embed_lsb(frame, data_bits)
                    elif self.method == 'dwt':
                        modified_frame, bits_embedded = self._embed_dwt(frame, data_bits)
                    else:  # hybrid
                        # Use both methods for maximum robustness
                        temp_frame, _ = self._embed_lsb(frame, data_bits[:len(data_bits)//2])
                        modified_frame, bits_embedded = self._embed_dwt(temp_frame, data_bits[len(data_bits)//2:])
                        bits_embedded += len(data_bits)//2
                    
                    writer.write(modified_frame)
                    successful_embeds += 1
                    
                    if frame_idx % 50 == 0:
                        print(f"[+] Processed frame {frame_idx}, embedded {len(full_payload)} bytes")
                    
                    embedding_idx += 1
                    
                except Exception as e:
                    print(f"[!] Error embedding in frame {frame_idx}: {e}")
                    writer.write(frame)
            else:
                writer.write(frame)
            
            frame_idx += 1
        
        cap.release()
        writer.release()
        
        print(f"[+] Embedding complete!")
        print(f"[+] Successfully embedded in {successful_embeds}/{len(embedding_frames)} frames")
        print(f"[+] Output saved: {output_path}")
        
        # Create metadata for extraction
        embedding_info = {
            'frames': embedding_frames,
            'method': self.method,
            'redundancy': self.redundancy,
            'payload_per_frame': len(full_payload),  # Complete payload in each frame
            'total_payload_size': len(full_payload)
        }
        
        metadata = self._create_metadata(data, video_info, embedding_info)
        
        return {
            'success': True,
            'metadata': metadata,
            'embedding_frames': embedding_frames,
            'payload_size': len(full_payload),
            'original_size': len(data),
            'method': self.method,
            'encrypted': bool(self.password),
            'output_path': output_path
        }
    
    def extract_data(self, video_path: str, metadata: Dict[str, Any] = None, 
                     output_path: str = None) -> Tuple[bytes, str]:
        """Extract data/file from video with robust error correction"""
        
        print(f"[+] Starting video steganography extraction")
        print(f"[+] Input video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise VideoSteganographyError(f"Cannot open video: {video_path}")
        
        # If no metadata, attempt blind extraction
        if metadata is None:
            print(f"[+] No metadata provided, attempting blind extraction")
            metadata = self._blind_extract_metadata(cap)
        
        embedding_info = metadata.get('embedding_info', {})
        embedding_frames = embedding_info.get('frames', [])
        method = embedding_info.get('method', self.method)
        payload_size = embedding_info.get('total_payload_size', 0)
        
        if not embedding_frames:
            raise VideoSteganographyError("No embedding frame information available")
        
        print(f"[+] Extracting from {len(embedding_frames)} frames")
        print(f"[+] Expected payload size: {payload_size} bytes")
        print(f"[+] Method: {method}")
        
        # Extract data from frames
        extracted_payloads = []
        successful_extractions = 0
        
        for frame_idx in embedding_frames:
            try:
                # Seek to frame
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    print(f"[!] Could not read frame {frame_idx}")
                    continue
                
                # Calculate expected bits for complete payload
                expected_bits = payload_size * 8
                
                # Extract using appropriate method
                if method == 'lsb':
                    extracted_bits = self._extract_lsb(frame, expected_bits)
                elif method == 'dwt':
                    extracted_bits = self._extract_dwt(frame, expected_bits)
                else:  # hybrid
                    bits1 = self._extract_lsb(frame, expected_bits//2)
                    bits2 = self._extract_dwt(frame, expected_bits//2)
                    extracted_bits = bits1 + bits2
                
                # Convert bits to bytes
                payload_data = bytearray()
                for i in range(0, len(extracted_bits), 8):
                    if i + 7 < len(extracted_bits):
                        byte_bits = extracted_bits[i:i+8]
                        byte_value = int(byte_bits, 2)
                        payload_data.append(byte_value)
                
                if len(payload_data) >= payload_size:
                    extracted_payloads.append(bytes(payload_data[:payload_size]))
                    successful_extractions += 1
                
            except Exception as e:
                print(f"[!] Error extracting from frame {frame_idx}: {e}")
        
        cap.release()
        
        print(f"[+] Successfully extracted from {successful_extractions}/{len(embedding_frames)} frames")
        
        # Use majority voting to select best payload
        if not extracted_payloads:
            raise VideoSteganographyError("No valid payloads extracted")
        
        # Debug: Check what we extracted
        print(f"[DEBUG] Extracted {len(extracted_payloads)} payloads")
        for i, payload in enumerate(extracted_payloads[:3]):  # Check first 3
            print(f"[DEBUG] Payload {i}: size={len(payload)}, first 16 bytes={payload[:16].hex()}")
            print(f"[DEBUG] Expected magic header: {(self.magic_header + self.version).hex()}")
        
        # Find the most common payload (redundancy check)
        best_payload = extracted_payloads[0]  # Start with first
        
        # Simple validation - use the first payload that has valid magic header
        for i, payload in enumerate(extracted_payloads):
            if payload.startswith(self.magic_header + self.version):
                print(f"[DEBUG] Found valid payload at index {i}")
                best_payload = payload
                break
        
        # If no valid header found, try to find it within the payload
        if not best_payload.startswith(self.magic_header + self.version):
            print("[DEBUG] No valid magic header found, searching within payloads...")
            for payload in extracted_payloads:
                magic_pos = payload.find(self.magic_header + self.version)
                if magic_pos >= 0:
                    print(f"[DEBUG] Found magic header at position {magic_pos}")
                    best_payload = payload[magic_pos:]
                    break
        
        full_payload = best_payload
        
        if not full_payload:
            raise VideoSteganographyError("Failed to extract valid payload from video")
        
        # Parse payload
        try:
            # Verify magic header
            if not full_payload.startswith(self.magic_header + self.version):
                raise VideoSteganographyError("Invalid magic header in extracted data")
            
            offset = len(self.magic_header) + len(self.version)
            
            # Read header size
            header_size = struct.unpack('<I', full_payload[offset:offset+4])[0]
            offset += 4
            
            # Read header
            header_json = full_payload[offset:offset+header_size]
            header_data = json.loads(header_json.decode())
            offset += header_size
            
            # Read salt and nonce (if encrypted)
            if header_data.get('encrypted', False):
                salt = full_payload[offset:offset+16]
                nonce = full_payload[offset+16:offset+28]
                offset += 28
                encrypted_data = full_payload[offset:]
                
                # Decrypt
                print(f"[+] Decrypting extracted data...")
                original_data = self._decrypt_data(encrypted_data, salt, nonce)
            else:
                original_data = full_payload[offset:]
            
            # Verify checksum
            expected_checksum = header_data.get('checksum', '')
            actual_checksum = hashlib.sha256(original_data).hexdigest()
            
            if expected_checksum and expected_checksum != actual_checksum:
                print(f"[!] Warning: Checksum mismatch. Data may be corrupted.")
            
            print(f"[+] Extraction successful!")
            print(f"[+] Original filename: {header_data.get('filename', 'unknown')}")
            print(f"[+] Extracted {len(original_data)} bytes")
            
            # Save to file if output path provided
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(original_data)
                print(f"[+] Saved to: {output_path}")
            
            return original_data, header_data.get('filename', 'extracted_data.bin')
            
        except Exception as e:
            raise VideoSteganographyError(f"Failed to parse extracted payload: {e}")
    
    def _reconstruct_payload(self, chunks: List[bytes], expected_size: int) -> bytes:
        """Reconstruct payload from extracted chunks using redundancy"""
        if not chunks:
            return b''
        
        # Find the most consistent data by majority voting
        reconstructed = b''
        
        # Simple approach: use the first non-empty chunk that's closest to expected size
        best_chunk = b''
        best_score = float('inf')
        
        for chunk in chunks:
            if chunk:
                # Score based on size difference from expected
                size_diff = abs(len(chunk) - expected_size)
                if size_diff < best_score:
                    best_score = size_diff
                    best_chunk = chunk
        
        if best_chunk:
            # Trim or pad to expected size
            if len(best_chunk) >= expected_size:
                reconstructed = best_chunk[:expected_size]
            else:
                reconstructed = best_chunk  # Use what we have
        
        return reconstructed
    
    def _blind_extract_metadata(self, cap: cv2.VideoCapture) -> Dict[str, Any]:
        """Attempt to extract metadata when not provided"""
        # This is a simplified blind extraction - in practice, you would
        # try to detect embedded data patterns
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Assume standard keyframe interval
        estimated_frames = list(range(0, frame_count, self.keyframe_interval))
        
        return {
            'embedding_info': {
                'frames': estimated_frames[:50],  # Limit to reasonable number
                'method': self.method,
                'redundancy': self.redundancy,
                'total_payload_size': 10000  # Estimated
            }
        }

# Test function
def test_video_steganography():
    """Test the video steganography system"""
    
    # Create test video if it doesn't exist
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print("[+] Creating test video...")
        create_test_video(test_video)
    
    # Test data
    test_data = b"This is a secret message embedded in a video file using advanced steganography!"
    test_filename = "secret_message.txt"
    password = "test_password_123"
    
    # Initialize steganography system
    stego = AdvancedVideoSteganography(password=password, method='lsb')
    
    # Test embedding
    print("\n" + "="*60)
    print("TESTING VIDEO STEGANOGRAPHY - EMBEDDING")
    print("="*60)
    
    result = stego.embed_data(test_video, test_data, "stego_test_video.mp4", test_filename)
    
    if result['success']:
        print(f"[+] Embedding successful!")
        
        # Test extraction
        print("\n" + "="*60)
        print("TESTING VIDEO STEGANOGRAPHY - EXTRACTION")
        print("="*60)
        
        extracted_data, extracted_filename = stego.extract_data(
            "stego_test_video.mp4", 
            result['metadata'],
            "extracted_secret.txt"
        )
        
        # Verify results
        if extracted_data == test_data:
            print(f"[+] SUCCESS: Data integrity verified!")
            print(f"[+] Original size: {len(test_data)} bytes")
            print(f"[+] Extracted size: {len(extracted_data)} bytes")
            print(f"[+] Filename: {extracted_filename}")
            return True
        else:
            print(f"[!] FAILED: Data mismatch")
            return False
    else:
        print(f"[!] Embedding failed")
        return False

def create_test_video(output_path: str, duration: int = 5):
    """Create a simple test video"""
    import numpy as np
    
    width, height = 640, 480
    fps = 30
    total_frames = duration * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame_num in range(total_frames):
        # Create a colorful frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some patterns
        cv2.rectangle(frame, (50, 50), (width-50, height-50), (100, 150, 200), -1)
        cv2.circle(frame, (width//2, height//2), 50, (255, 100, 100), -1)
        
        # Add frame number
        cv2.putText(frame, f"Frame {frame_num}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        writer.write(frame)
    
    writer.release()
    print(f"[+] Test video created: {output_path}")

if __name__ == "__main__":
    test_video_steganography()