#!/usr/bin/env python3
"""
SAFE UNIVERSAL FILE STEGANOGRAPHY - PRODUCTION READY
Replaces the corrupting LSB system with safe append methods
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

class UniversalFileSteganography:
    """Safe universal steganography that never corrupts any file type"""
    
    def __init__(self):
        self.magic_header = b"VEILFORGE_UNIVERSAL_SAFE_V2"
        self.end_marker = b"VEILFORGE_UNIVERSAL_END_V2"
    
    def hide_data(self, carrier_file_path: str, content_to_hide: Union[str, bytes], 
                  output_path: str, password: Optional[str] = None, 
                  is_file: bool = False, original_filename: str = None, **kwargs) -> Dict[str, Any]:
        """Safe hiding method that preserves ALL file types"""
        
        print(f"[SAFE UNIVERSAL] Processing {os.path.basename(carrier_file_path)}")
        
        # Read carrier file without any modification
        with open(carrier_file_path, 'rb') as f:
            original_file_data = f.read()
        
        # Determine file type for validation
        file_ext = os.path.splitext(carrier_file_path)[1].lower()
        
        # Prepare secret data with robust type checking
        if is_file and isinstance(content_to_hide, str) and os.path.exists(content_to_hide):
            with open(content_to_hide, 'rb') as f:
                original_payload = f.read()
            filename = original_filename or os.path.basename(content_to_hide)
        else:
            # Handle various input types safely
            if isinstance(content_to_hide, str):
                original_payload = content_to_hide.encode('utf-8')
            elif isinstance(content_to_hide, bytes):
                original_payload = content_to_hide
            elif isinstance(content_to_hide, bool):
                # Handle boolean inputs (convert to string first)
                original_payload = str(content_to_hide).encode('utf-8')
                print(f"[SAFE UNIVERSAL] Warning: Boolean input converted to string: {content_to_hide}")
            else:
                # Handle other types by converting to string
                try:
                    original_payload = str(content_to_hide).encode('utf-8')
                    print(f"[SAFE UNIVERSAL] Warning: {type(content_to_hide)} input converted to string")
                except Exception as e:
                    raise ValueError(f"Cannot process content_to_hide of type {type(content_to_hide)}: {e}")
            filename = original_filename or 'hidden_data.txt'
        
        return self._safe_embed_universal(original_file_data, original_payload, output_path, password, filename, file_ext)
    
    def hide_file_in_file(self, container_path: str, secret_file_path: str, 
                         output_path: str) -> Dict[str, Any]:
        """Safe file-in-file hiding"""
        
        with open(secret_file_path, 'rb') as f:
            secret_data = f.read()
        filename = os.path.basename(secret_file_path)
        
        with open(container_path, 'rb') as f:
            carrier_data = f.read()
        
        file_ext = os.path.splitext(container_path)[1].lower()
        
        return self._safe_embed_universal(carrier_data, secret_data, output_path, None, filename, file_ext)
    
    def _safe_embed_universal(self, carrier_data: bytes, secret_data: bytes, 
                             output_path: str, password: Optional[str], 
                             filename: str, file_ext: str) -> Dict[str, Any]:
        """Universal safe embedding for ALL file types"""
        
        # Create metadata with original data checksum
        metadata = {
            'filename': filename,
            'original_size': len(secret_data),
            'encrypted': bool(password),
            'checksum': hashlib.sha256(secret_data).hexdigest(),
            'carrier_size': len(carrier_data),
            'carrier_ext': file_ext
        }
        
        # Encrypt if password provided
        if password:
            payload_data = self._encrypt_data(secret_data, password)
        else:
            payload_data = secret_data
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # Safe format: [ORIGINAL_FILE][MAGIC][META_SIZE][METADATA][DATA_SIZE][DATA][END]
        safe_file = (
            carrier_data +  # Original file completely preserved
            self.magic_header +
            len(metadata_json).to_bytes(4, 'little') +
            metadata_json +
            len(payload_data).to_bytes(4, 'little') +
            payload_data +
            self.end_marker
        )
        
        # Write safe file
        with open(output_path, 'wb') as f:
            f.write(safe_file)
        
        overhead = len(safe_file) - len(carrier_data)
        
        print(f"[SAFE UNIVERSAL] ✅ {file_ext.upper()} preserved completely")
        print(f"[SAFE UNIVERSAL] ✅ Added {overhead} bytes safely")
        print(f"[SAFE UNIVERSAL] ✅ No file structure modification")
        
        return {
            'success': True,
            'method': 'safe_universal_append',
            'original_size': len(carrier_data),
            'final_size': len(safe_file),
            'overhead_bytes': overhead,
            'file_type_preserved': True
        }
    
    def extract_data(self, stego_file_path: str, password: Optional[str] = None, 
                     output_dir: str = None) -> Optional[Union[Tuple[bytes, str], Dict[str, Any]]]:
        """Safe extraction method"""
        
        with open(stego_file_path, 'rb') as f:
            file_data = f.read()
        
        # Find magic header
        magic_pos = file_data.find(self.magic_header)
        if magic_pos == -1:
            print("[SAFE UNIVERSAL] No hidden data found")
            return None
        
        try:
            # Parse metadata
            metadata_size_pos = magic_pos + len(self.magic_header)
            metadata_size = int.from_bytes(file_data[metadata_size_pos:metadata_size_pos+4], 'little')
            
            metadata_pos = metadata_size_pos + 4
            metadata_json = file_data[metadata_pos:metadata_pos+metadata_size]
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Parse data
            data_size_pos = metadata_pos + metadata_size
            data_size = int.from_bytes(file_data[data_size_pos:data_size_pos+4], 'little')
            
            payload_pos = data_size_pos + 4
            payload_data = file_data[payload_pos:payload_pos+data_size]
            
            # Decrypt if needed
            if metadata['encrypted'] and password:
                try:
                    secret_data = self._decrypt_data(payload_data, password)
                except Exception as e:
                    print(f"[SAFE UNIVERSAL] Decryption error: {e}")
                    return None
            else:
                secret_data = payload_data
            
            # Verify integrity
            actual_checksum = hashlib.sha256(secret_data).hexdigest()
            if actual_checksum != metadata['checksum']:
                print(f"[SAFE UNIVERSAL] ⚠️  Checksum mismatch but continuing")
            
            print(f"[SAFE UNIVERSAL] ✅ Extracted {len(secret_data)} bytes")
            
            # Handle API response format
            if output_dir:
                output_path = os.path.join(output_dir, f"extracted_{metadata['filename']}")
                with open(output_path, 'wb') as f:
                    f.write(secret_data)
                
                # Try to decode as text for API response
                try:
                    text_data = secret_data.decode('utf-8')
                except:
                    text_data = base64.b64encode(secret_data).decode('ascii')
                
                return {
                    'success': True,
                    'extracted_data': text_data,
                    'filename': metadata['filename'],
                    'saved_to': output_path
                }
            
            return (secret_data, metadata['filename'])
        
        except Exception as e:
            print(f"[SAFE UNIVERSAL] Extraction error: {e}")
            return None
    
    def extract_file_from_file(self, stego_file_path: str, output_dir: str) -> Optional[str]:
        """Extract file and save to directory"""
        
        result = self.extract_data(stego_file_path, None, output_dir)
        if result and isinstance(result, dict) and result.get('success'):
            return result['saved_to']
        return None
    
    def _encrypt_data(self, data: bytes, password: str) -> bytes:
        """Encrypt data using AES-GCM"""
        salt = os.urandom(16)
        nonce = os.urandom(12)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes, password: str) -> bytes:
        """Decrypt data using AES-GCM"""
        salt = encrypted_data[:16]
        nonce = encrypted_data[16:28]
        ciphertext = encrypted_data[28:]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)