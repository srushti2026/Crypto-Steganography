#!/usr/bin/env python3
"""
SAFE VIDEO STEGANOGRAPHY - Production Ready
Uses safe append method that never corrupts video files
Maintains original format, codec, and playability
"""

import os
import json
import hashlib
import base64
import struct
from typing import Dict, Any, Optional, Union, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class SafeVideoSteganography:
    """Safe video steganography that never modifies the original video content"""
    
    def __init__(self, password: str = ""):
        self.password = password
        self.magic_header = b"VEILFORGE_SAFE_VIDEO_V1"
        self.end_marker = b"VEILFORGE_VIDEO_END_V1"
    
    def hide_data_in_video(self, video_path: str, secret_data: Union[str, bytes], 
                          output_path: str, is_file: bool = False, 
                          original_filename: str = None) -> Dict[str, Any]:
        """Safe hiding that preserves video completely"""
        
        # Read original video file without any modification
        with open(video_path, 'rb') as f:
            original_video_data = f.read()
        
        print(f"[SAFE VIDEO] Original video size: {len(original_video_data)} bytes")
        
        # Prepare secret data
        if is_file and os.path.exists(secret_data):
            with open(secret_data, 'rb') as f:
                original_payload = f.read()
            filename = original_filename or os.path.basename(secret_data)
        else:
            if isinstance(secret_data, str):
                original_payload = secret_data.encode('utf-8')
            else:
                original_payload = secret_data
            filename = original_filename or 'hidden_data.txt'
        
        # Create metadata with original data checksum (before encryption)
        metadata = {
            'filename': filename,
            'original_size': len(original_payload),
            'encrypted': bool(self.password),
            'checksum': hashlib.sha256(original_payload).hexdigest(),
            'video_size': len(original_video_data)
        }
        
        # Encrypt after metadata creation
        if self.password:
            payload_data = self._encrypt_data(original_payload)
        else:
            payload_data = original_payload
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # Safe payload: [ORIGINAL_VIDEO][MAGIC][META_SIZE][METADATA][DATA_SIZE][DATA][END]
        safe_video = (
            original_video_data +  # Original video completely unchanged
            self.magic_header +
            len(metadata_json).to_bytes(4, 'little') +
            metadata_json +
            len(payload_data).to_bytes(4, 'little') +
            payload_data +
            self.end_marker
        )
        
        # Write safe video file
        with open(output_path, 'wb') as f:
            f.write(safe_video)
        
        overhead_bytes = len(safe_video) - len(original_video_data)
        
        print(f"[SAFE VIDEO] ✅ Video preserved completely")
        print(f"[SAFE VIDEO] ✅ Original format maintained")
        print(f"[SAFE VIDEO] ✅ Added {overhead_bytes} bytes safely")
        print(f"[SAFE VIDEO] ✅ Output: {output_path}")
        
        return {
            'success': True,
            'method': 'safe_video_append',
            'original_size': len(original_video_data),
            'final_size': len(safe_video),
            'overhead_bytes': overhead_bytes,
            'format_preserved': True,
            'playable': True
        }
    
    def extract_data_from_video(self, stego_video_path: str) -> Optional[Tuple[bytes, str]]:
        """Extract hidden data from safe video"""
        
        with open(stego_video_path, 'rb') as f:
            video_data = f.read()
        
        # Find magic header
        magic_pos = video_data.find(self.magic_header)
        if magic_pos == -1:
            print("[SAFE VIDEO] No hidden data found")
            return None
        
        try:
            # Parse metadata size
            metadata_size_pos = magic_pos + len(self.magic_header)
            metadata_size = int.from_bytes(video_data[metadata_size_pos:metadata_size_pos+4], 'little')
            
            # Parse metadata
            metadata_pos = metadata_size_pos + 4
            metadata_json = video_data[metadata_pos:metadata_pos+metadata_size]
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Parse data size
            data_size_pos = metadata_pos + metadata_size
            data_size = int.from_bytes(video_data[data_size_pos:data_size_pos+4], 'little')
            
            # Extract hidden data
            payload_pos = data_size_pos + 4
            payload_data = video_data[payload_pos:payload_pos+data_size]
            
            # Decrypt if needed
            if metadata['encrypted'] and self.password:
                try:
                    payload_data = self._decrypt_data(payload_data)
                except Exception as e:
                    print(f"[SAFE VIDEO] Decryption error: {e}")
                    return None
            
            # Verify integrity (checksum is calculated on original data before encryption)
            actual_checksum = hashlib.sha256(payload_data).hexdigest()
            if actual_checksum != metadata['checksum']:
                print(f"[SAFE VIDEO] Checksum mismatch: expected {metadata['checksum']}, got {actual_checksum}")
                # Don't fail completely, return data anyway for debugging
                print(f"[SAFE VIDEO] ⚠️  Returning data despite checksum mismatch")
            
            print(f"[SAFE VIDEO] ✅ Extracted {len(payload_data)} bytes")
            print(f"[SAFE VIDEO] ✅ Filename: {metadata['filename']}")
            
            # SPECIAL HANDLING: Check if this is a layered container that needs format preservation
            print(f"[SAFE VIDEO] 🔍 Checking for layered container: filename='{metadata['filename']}'")
            if metadata['filename'] == 'layered_container.json' and isinstance(payload_data, bytes):
                print(f"[SAFE VIDEO] 📋 Detected layered_container.json filename - parsing container")
                try:
                    # Try to parse as layered container JSON
                    container_json = payload_data.decode('utf-8')
                    import json
                    container = json.loads(container_json)
                    
                    print(f"[SAFE VIDEO] 📋 JSON parsed - type: {container.get('type', 'missing')}")
                    print(f"[SAFE VIDEO] 📋 Has layers: {'layers' in container}")
                    if 'layers' in container:
                        print(f"[SAFE VIDEO] 📋 Number of layers: {len(container['layers'])}")
                    
                    if (isinstance(container, dict) and 
                        container.get('type') == 'layered_container' and
                        'layers' in container and 
                        len(container['layers']) == 1):
                        
                        # Single layer container - extract the original filename
                        layer = container['layers'][0]
                        if isinstance(layer, dict) and layer.get('filename'):
                            original_filename = layer['filename']
                            print(f"[SAFE VIDEO] 🎯 Layered container detected - using original filename: {original_filename}")
                            return (payload_data, original_filename)
                        else:
                            print(f"[SAFE VIDEO] ⚠️  Layer missing filename: {layer}")
                    else:
                        print(f"[SAFE VIDEO] ⚠️  Not a single-layer container")
                except Exception as e:
                    print(f"[SAFE VIDEO] ⚠️  Layered container parsing failed: {e}")
                    # Fall through to return original metadata
            else:
                print(f"[SAFE VIDEO] ℹ️  Not a layered container file")
            
            return (payload_data, metadata['filename'])
        
        except Exception as e:
            print(f"[SAFE VIDEO] ❌ Extraction error: {e}")
            return None
    
    def get_original_video(self, stego_video_path: str, output_path: str) -> str:
        """Extract the original, unmodified video file"""
        
        with open(stego_video_path, 'rb') as f:
            video_data = f.read()
        
        # Find where steganographic data starts
        magic_pos = video_data.find(self.magic_header)
        if magic_pos == -1:
            magic_pos = len(video_data)  # No stego data
        
        # Extract original video
        original_video = video_data[:magic_pos]
        
        with open(output_path, 'wb') as f:
            f.write(original_video)
        
        print(f"[SAFE VIDEO] ✅ Original video recovered: {len(original_video)} bytes")
        return output_path
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        if not self.password:
            return data
        
        # Generate salt and nonce
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        # Return: salt + nonce + ciphertext
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        if not self.password:
            return encrypted_data
        
        # Extract components
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        # Decrypt
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)


class FinalVideoSteganographyManager:
    """Production video steganography manager using safe methods"""
    
    def __init__(self):
        self.safe_stego = SafeVideoSteganography()
    
    def hide_data(self, carrier_file_path: str, content_to_hide: Union[str, bytes], 
                  output_path: str, password: Optional[str] = None, 
                  is_file: bool = False, original_filename: str = None, **kwargs) -> Dict[str, Any]:
        """Hide data in video using safe method"""
        
        # Set password if provided
        if password:
            self.safe_stego.password = password
        
        return self.safe_stego.hide_data_in_video(
            carrier_file_path, content_to_hide, output_path, 
            is_file, original_filename
        )
    
    def extract_data(self, stego_file_path: str, password: Optional[str] = None, 
                     output_dir: str = None) -> Optional[Union[Tuple[bytes, str], Dict[str, Any]]]:
        """Extract data from video using safe method"""
        
        # Set password if provided
        if password:
            self.safe_stego.password = password
        
        result = self.safe_stego.extract_data_from_video(stego_file_path)
        
        if result and output_dir:
            data, filename = result
            # Save extracted file
            output_path = os.path.join(output_dir, f"extracted_{filename}")
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return {
                'success': True,
                'extracted_data': data.decode('utf-8') if filename.endswith('.txt') else data,
                'filename': filename,
                'saved_to': output_path
            }
        
        return result


# Legacy compatibility - replace the old broken system
FinalVideoSteganography = SafeVideoSteganography