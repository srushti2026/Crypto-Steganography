#!/usr/bin/env python3
"""
Comprehensive File-in-Audio Steganography
Hide any type of file (.txt, .pdf, .docx, .exe, etc.) inside audio files
Uses optimized multi-band DWT embedding with file type detection
"""

import numpy as np
import pywt
import librosa
import soundfile as sf
import os
import json
import mimetypes
import struct
from pathlib import Path

# Cryptography imports for password support
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets

# Optional dependency for better MIME type detection
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

class UniversalFileAudio:
    """Universal file hiding in audio using optimized multi-band embedding"""
    
    def __init__(self, password: str = None):
        self.password = password
        self.redundancy = 2  # Balanced redundancy vs capacity
        self.wavelet = 'db4'
        self.level = 5
        self.detail_bands = [1, 2, 3, 4]  # Use 4 bands for maximum capacity
        
    def _get_file_info(self, file_path):
        """Get comprehensive file information"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Try using python-magic for better detection if available
            if HAS_MAGIC:
                try:
                    mime_type = magic.from_file(file_path, mime=True)
                except:
                    mime_type = 'application/octet-stream'
            else:
                mime_type = 'application/octet-stream'
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        filename = os.path.basename(file_path)
        
        return {
            'filename': filename,
            'extension': file_ext,
            'mime_type': mime_type,
            'size': file_size,
            'readable_size': self._format_size(file_size)
        }
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/(1024**2):.1f} MB"
        else:
            return f"{size_bytes/(1024**3):.1f} GB"
    
    def _get_audio_capacity(self, audio_path):
        """Calculate total embedding capacity for any file type"""
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use 95% of audio for maximum capacity
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        # CRITICAL FIX: Use more realistic capacity calculation
        target_band = 2 if 2 < len(coeffs) else len(coeffs) - 1
        band_coeffs = len(coeffs[target_band])
        
        # Adaptive capacity: use tighter spacing for small files
        offset = 8  # Skip first few coefficients  
        available_coeffs = band_coeffs - offset
        
        # Use spacing of 2 instead of 4 for better capacity
        max_bits = available_coeffs // 2  # More aggressive spacing
        max_bytes = max_bits // 8
        
        # Ensure minimum capacity for very small files
        if max_bytes < 100:
            # For very small audio, use even tighter packing
            max_bits = available_coeffs  # 1:1 coefficient to bit ratio
            max_bytes = max_bits // 8
        
        return max_bytes, band_coeffs, len(y), sr
    
    def embed_file(self, audio_path, file_path, output_path, compression_level=6):
        """
        Embed any file type into audio
        
        Args:
            audio_path: Input audio file
            file_path: File to hide (any type: .txt, .pdf, .docx, etc.)
            output_path: Output audio file with hidden data
            compression_level: Compression level 0-9 (higher = smaller file)
        """
        print(f"📁 Embedding file '{file_path}' into '{audio_path}'")
        
        # Get file information
        file_info = self._get_file_info(file_path)
        print(f"📄 File: {file_info['filename']} ({file_info['readable_size']})")
        print(f"🔍 Type: {file_info['mime_type']} ({file_info['extension']})")
        
        # Check audio capacity
        max_bytes, total_coeffs, audio_samples, sr = self._get_audio_capacity(audio_path)
        print(f"📊 Audio: {audio_samples} samples, {sr} Hz, {audio_samples/sr:.1f}s")
        print(f"💾 Capacity: {self._format_size(max_bytes)} available")
        
        # Read file data
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"📦 Original file: {len(file_data)} bytes")
        
        # Apply compression if needed
        compressed_data = file_data
        if compression_level > 0:
            import zlib
            compressed_data = zlib.compress(file_data, level=compression_level)
            compression_ratio = len(compressed_data) / len(file_data)
            print(f"🗜️ Compressed: {len(compressed_data)} bytes ({compression_ratio:.1%} of original)")
        
        # Create comprehensive header
        header = {
            'magic': 'UNIVERSAL_FILE_AUDIO',
            'version': '1.0',
            'filename': file_info['filename'],
            'extension': file_info['extension'],
            'mime_type': file_info['mime_type'],
            'original_size': len(file_data),
            'compressed_size': len(compressed_data),
            'compression_level': compression_level,
            'checksum': hex(hash(file_data) & 0xFFFFFFFF)  # Simple checksum
        }
        
        header_json = json.dumps(header, separators=(',', ':')).encode('utf-8')
        
        # Package: header_length + header + compressed_data
        total_package = len(header_json).to_bytes(4, 'little') + header_json + compressed_data
        
        print(f"📋 Header: {len(header_json)} bytes")
        print(f"📦 Total package: {len(total_package)} bytes ({self._format_size(len(total_package))})")
        
        # Check if it fits
        if len(total_package) > max_bytes:
            if compression_level < 9:
                # Increase compression but ensure it doesn't exceed 9
                new_compression = min(9, compression_level + 2)
                if new_compression > compression_level:
                    print(f"⚠️ File too large, trying higher compression (level {new_compression})...")
                    return self.embed_file(audio_path, file_path, output_path, new_compression)
                else:
                    raise ValueError(f"File too large! Need {self._format_size(len(total_package))}, have {self._format_size(max_bytes)}")
            else:
                raise ValueError(f"File too large! Need {self._format_size(len(total_package))}, have {self._format_size(max_bytes)}")
        
        usage_percent = (len(total_package) / max_bytes) * 100
        print(f"📊 Capacity usage: {usage_percent:.1f}%")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use maximum segment
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        # Convert to bits
        data_bits = ''.join(format(byte, '08b') for byte in total_package)
        print(f"🔢 Embedding {len(total_package)} bytes ({len(data_bits)} bits)")
        
        # Distribute across bands with robust embedding
        bits_per_band = len(data_bits) // len(self.detail_bands)
        remaining_bits = len(data_bits) % len(self.detail_bands)
        
        bit_index = 0
        
        for band_idx, band in enumerate(self.detail_bands):
            if band >= len(coeffs):
                continue
                
            detail_band = coeffs[band].copy()
            
            # Calculate bits for this band based on coefficient spacing
            max_bits_this_band = len(detail_band) // 4  # Every 4th coefficient
            band_bits = min(bits_per_band, max_bits_this_band)
            if band_idx < remaining_bits and band_bits < max_bits_this_band:
                band_bits += 1
            
            if bit_index + band_bits > len(data_bits):
                band_bits = len(data_bits) - bit_index
            
            band_data = data_bits[bit_index:bit_index + band_bits]
            bit_index += band_bits
            
            print(f"🔊 Band {band}: {len(detail_band)} coeffs, embedding {len(band_data)} bits")
            
            # Embed in this band using robust approach
            for bit_idx, bit_char in enumerate(band_data):
                bit_val = int(bit_char)
                
                # Use spacing of 4 for robustness
                coeff_idx = bit_idx * 4
                if coeff_idx < len(detail_band):
                    # Use fixed large magnitudes for maximum robustness
                    if bit_val == 1:
                        detail_band[coeff_idx] = 1.0   # Strong positive for bit 1
                    else:
                        detail_band[coeff_idx] = -1.0  # Strong negative for bit 0
            
            # Update coefficients
            coeffs[band] = detail_band
            
            if bit_index >= len(data_bits):
                break
        
        # Reconstruct audio
        y_modified = pywt.waverec(coeffs, self.wavelet)
        
        # Ensure same length
        if len(y_modified) != len(segment):
            if len(y_modified) > len(segment):
                y_modified = y_modified[:len(segment)]
            else:
                padding = np.zeros(len(segment) - len(y_modified))
                y_modified = np.concatenate([y_modified, padding])
        
        # Update audio
        y[0, :len(y_modified)] = y_modified
        
        # Save
        audio_out = y[0] if y.shape[0] == 1 else y.T
        sf.write(output_path, audio_out, sr)
        
        print(f"✅ File embedded successfully in '{output_path}'")
        
        return {
            'original_file_size': len(file_data),
            'compressed_size': len(compressed_data),
            'total_package_size': len(total_package),
            'compression_ratio': f"{len(compressed_data)/len(file_data):.1%}",
            'capacity_used': f"{usage_percent:.1f}%",
            'file_type': file_info['mime_type'],
            'bands_used': len([b for b in self.detail_bands if b < len(coeffs)])
        }
    
    def extract_file(self, audio_path, output_dir=None):
        """
        Extract any file type from audio
        
        Args:
            audio_path: Steganographic audio file
            output_dir: Directory to save extracted file (optional)
            
        Returns:
            Path to extracted file
        """
        print(f"🔍 Extracting file from '{audio_path}'")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Use same segment
        segment = y[0, :int(y.shape[1] * 0.95)]
        coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
        
        # Extract bits from all bands in the same order as embedding
        all_bits = []
        
        for band in self.detail_bands:
            if band >= len(coeffs):
                continue
                
            detail_band = coeffs[band]
            print(f"🔊 Extracting from band {band}: {len(detail_band)} coefficients")
            
            # Extract using robust approach with simple threshold  
            max_bits_this_band = len(detail_band) // 4  # Match the spacing used in embedding
            
            for bit_idx in range(max_bits_this_band):
                coeff_idx = bit_idx * 4  # Every 4th coefficient to match embedding
                if coeff_idx < len(detail_band):
                    coeff = detail_band[coeff_idx]
                    # Robust positive/negative threshold extraction with precision handling
                    threshold = 1e-12
                    if abs(coeff) < threshold:
                        # If coefficient is too close to zero, default to 0
                        bit_value = 0
                    else:
                        bit_value = 1 if coeff > 0 else 0
                    all_bits.append(str(bit_value))
        
        print(f"📊 Total extracted bits: {len(all_bits)}")
        
        # Debug: Show first few bits
        if len(all_bits) > 64:
            print(f"[DEBUG] First 64 bits: {''.join(all_bits[:64])}")
        
        # Convert to bytes
        extracted_bytes = []
        for i in range(0, len(all_bits), 8):
            if i + 7 < len(all_bits):
                byte_bits = ''.join(all_bits[i:i+8])
                byte_val = int(byte_bits, 2)
                extracted_bytes.append(byte_val)
        
        print(f"[DEBUG] First 10 extracted bytes: {extracted_bytes[:10]}")
        
        if len(extracted_bytes) < 4:
            raise ValueError("Not enough data extracted")
        
        # Check for magic header first
        magic_header = b"UNIVERSAL_FILE_AUDIO"
        magic_found = False
        start_offset = 0
        
        # Look for magic header in first few bytes
        for offset in range(min(100, len(extracted_bytes) - len(magic_header))):
            test_magic = bytes(extracted_bytes[offset:offset + len(magic_header)])
            if test_magic == magic_header:
                print(f"✅ Magic header found at offset {offset}")
                start_offset = offset
                magic_found = True
                break
        
        if not magic_found:
            raise ValueError("Magic header not found")
        
        # Parse header length from correct position
        header_length_offset = start_offset + len(magic_header)
        header_length = int.from_bytes(bytes(extracted_bytes[header_length_offset:header_length_offset+4]), 'little')
        print(f"📋 Header length: {header_length}")
        
        if header_length <= 0 or header_length > 1000:
            raise ValueError(f"Invalid header length: {header_length}")
        
        # Extract header
        header_start = header_length_offset + 4
        header_end = header_start + header_length
        
        if len(extracted_bytes) < header_end:
            raise ValueError("Not enough bytes for header")
        
        header_bytes = bytes(extracted_bytes[header_start:header_end])
        
        try:
            header_str = header_bytes.decode('utf-8')
            header = json.loads(header_str)
            print(f"📋 Header parsed successfully")
        except Exception as e:
            print(f"[ERROR] Header parsing failed: {e}")
            raise ValueError(f"Cannot decode header: {e}")
        
        print(f"📋 Header: {header}")
        
        if header.get('magic') != 'UNIVERSAL_FILE_AUDIO':
            raise ValueError("Not a valid universal file-audio file")
        
        # Extract compressed data from corrected position
        compressed_size = header['compressed_size']
        data_start = header_end
        data_end = data_start + compressed_size
        
        if len(extracted_bytes) < data_end:
            raise ValueError(f"Not enough bytes for file data: need {data_end}, have {len(extracted_bytes)}")
        
        compressed_data = bytes(extracted_bytes[data_start:data_end])
        
        # Decompress if needed
        if header['compression_level'] > 0:
            import zlib
            file_data = zlib.decompress(compressed_data)
            print(f"🗜️ Decompressed: {len(compressed_data)} → {len(file_data)} bytes")
        else:
            file_data = compressed_data
        
        # Verify size
        if len(file_data) != header['original_size']:
            print(f"⚠️ Size mismatch: expected {header['original_size']}, got {len(file_data)}")
        
        # Verify checksum
        calculated_checksum = hex(hash(file_data) & 0xFFFFFFFF)
        if calculated_checksum != header['checksum']:
            print(f"⚠️ Checksum mismatch: expected {header['checksum']}, got {calculated_checksum}")
        
        # Determine output path
        filename = header['filename']
        if output_dir:
            if os.path.isdir(output_dir):
                output_path = os.path.join(output_dir, filename)
            else:
                output_path = output_dir
        else:
            output_path = f"extracted_{filename}"
        
        # Save file
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        print(f"📁 File extracted: {filename}")
        print(f"📄 Type: {header['mime_type']} ({header['extension']})")
        print(f"📊 Size: {self._format_size(len(file_data))}")
        print(f"💾 Saved to: {output_path}")
        
        return output_path
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        
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
        
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-GCM"""
        if len(encrypted_data) < 28:
            raise ValueError(f"Encrypted data too short: {len(encrypted_data)} bytes, need at least 28")
        
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
    
    def hide_data(self, carrier_file_path: str, content_to_hide, output_path: str, is_file: bool = False, original_filename: str = None, **kwargs):
        """Simplified hide data method using robust single-band DWT approach"""
        try:
            print(f"[SIMPLE AUDIO] Hiding data in {carrier_file_path}")
            
            # Prepare content
            if is_file:
                if isinstance(content_to_hide, str):
                    raw_data = content_to_hide.encode('utf-8')
                else:
                    raw_data = content_to_hide
            else:
                text_data = str(content_to_hide)
                raw_data = text_data.encode('utf-8')
            
            print(f"[SIMPLE AUDIO] Raw data: {len(raw_data)} bytes")
            
            # Check capacity
            max_bytes, _, _, _ = self._get_audio_capacity(carrier_file_path)
            
            # Create metadata with original filename
            metadata = {
                'filename': original_filename or 'hidden_data.txt',
                'data_size': len(raw_data),
                'encrypted': bool(self.password)
            }
            
            import json
            metadata_json = json.dumps(metadata).encode('utf-8')
            
            # Create header: magic(6) + metadata_length(4) + metadata + data_length(4) + encrypted_data
            magic = b'SAUDIO'
            
            # Encrypt if password provided
            if self.password:
                encrypted_data = self._encrypt_data(raw_data)
                final_data = encrypted_data
                print(f"[SIMPLE AUDIO] Encrypted data: {len(final_data)} bytes")
            else:
                final_data = raw_data
                print(f"[SIMPLE AUDIO] Unencrypted data: {len(final_data)} bytes")
            
            # Create payload: magic + metadata_length + metadata + data_length + data
            metadata_length = struct.pack('<I', len(metadata_json))
            data_length = struct.pack('<I', len(final_data))
            payload = magic + metadata_length + metadata_json + data_length + final_data
            
            print(f"[SIMPLE AUDIO] Total payload: {len(payload)} bytes")
            print(f"[SIMPLE AUDIO] Available capacity: {max_bytes} bytes")
            
            if len(payload) > max_bytes:
                return {
                    'success': False,
                    'error': f'Data too large: need {len(payload)} bytes, have {max_bytes} bytes'
                }
            
            # Load and process audio
            y, sr = librosa.load(carrier_file_path, sr=None)
            if len(y.shape) == 1:
                y = y.reshape(1, -1)
            
            # CRITICAL FIX: Skip the beginning of audio to prevent audible noise
            # Use middle portion of audio for embedding to preserve music quality
            audio_length = y.shape[1]
            start_skip = int(audio_length * 0.1)  # Skip first 10%
            end_skip = int(audio_length * 0.1)    # Skip last 10%
            
            # Work with middle 80% of audio
            segment_start = start_skip
            segment_end = audio_length - end_skip
            segment = y[0, segment_start:segment_end]
            
            # Apply DWT to the middle segment only
            coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
            
            target_band = 2 if 2 < len(coeffs) else len(coeffs) - 1
            detail_band = coeffs[target_band].copy()
            
            # Convert payload to bits
            data_bits = ''.join(format(byte, '08b') for byte in payload)
            print(f"[SIMPLE AUDIO] Embedding {len(data_bits)} bits in band {target_band} (middle segment)")
            
            # CRITICAL FIX: Use adaptive spacing based on available space
            offset = 8   # Skip first few coefficients
            available_coeffs = len(detail_band) - offset
            
            # Calculate required spacing - use minimum possible
            min_spacing = max(1, available_coeffs // len(data_bits))
            spacing = min(4, min_spacing)  # Prefer 4 but use less if needed
            
            print(f"📊 Adaptive spacing: {spacing} (available: {available_coeffs}, needed: {len(data_bits)})")
            
            # Check if we have enough space
            required_coeffs = len(data_bits) * spacing + offset
            if required_coeffs > len(detail_band):
                raise ValueError(f"Insufficient capacity: need {required_coeffs} coefficients, have {len(detail_band)}")
            
            for bit_idx, bit_char in enumerate(data_bits):
                bit_val = int(bit_char)
                coeff_idx = offset + (bit_idx * spacing)
                
                if coeff_idx < len(detail_band):
                    # RELIABLE FIX: Use consistent magnitude-based embedding for reliable extraction
                    current_coeff = detail_band[coeff_idx]
                    
                    # Set a consistent magnitude that's detectable and robust
                    base_magnitude = max(0.1, abs(current_coeff) * 0.5)
                    
                    # Clear embedding: positive for 1, negative for 0
                    if bit_val == 1:
                        detail_band[coeff_idx] = base_magnitude
                    else:
                        detail_band[coeff_idx] = -base_magnitude
            
            # Update coefficients and reconstruct the segment
            coeffs[target_band] = detail_band
            y_modified_segment = pywt.waverec(coeffs, self.wavelet)
            
            # Ensure same length as original segment
            if len(y_modified_segment) != len(segment):
                if len(y_modified_segment) > len(segment):
                    y_modified_segment = y_modified_segment[:len(segment)]
                else:
                    padding = np.zeros(len(segment) - len(y_modified_segment))
                    y_modified_segment = np.concatenate([y_modified_segment, padding])
            
            # CRITICAL: Replace only the middle segment, preserve beginning and end
            y_out = y.copy()
            y_out[0, segment_start:segment_start + len(y_modified_segment)] = y_modified_segment
            
            # Save output
            audio_out = y_out[0] if y_out.shape[0] == 1 else y_out.T
            sf.write(output_path, audio_out, sr)
            
            print(f"[SIMPLE AUDIO] Successfully embedded data in {output_path}")
            
            return {
                'success': True,
                'output_path': output_path,
                'details': {
                    'data_size': len(raw_data),
                    'payload_size': len(payload),
                    'capacity_used': f"{len(payload)/max_bytes*100:.1f}%"
                }
            }
            
        except Exception as e:
            print(f"[SIMPLE AUDIO] Error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_data(self, stego_file_path: str, output_dir: str = None):
        """Simplified extract data method using robust single-band DWT approach"""
        try:
            print(f"[SIMPLE AUDIO] Extracting from {stego_file_path}")
            
            # Load audio - match embedding segment selection
            y, sr = librosa.load(stego_file_path, sr=None)
            if len(y.shape) == 1:
                y = y.reshape(1, -1)
            
            # Use same middle segment as embedding
            audio_length = y.shape[1]
            start_skip = int(audio_length * 0.1)  # Skip first 10%
            end_skip = int(audio_length * 0.1)    # Skip last 10%
            
            segment_start = start_skip
            segment_end = audio_length - end_skip
            segment = y[0, segment_start:segment_end]
            
            coeffs = pywt.wavedec(segment, self.wavelet, level=self.level)
            
            target_band = 2 if 2 < len(coeffs) else len(coeffs) - 1
            detail_band = coeffs[target_band]
            
            print(f"[SIMPLE AUDIO] Extracting from band {target_band} (middle segment)")
            
            # Extract bits - match embedding strategy
            extracted_bits = []
            offset = 8  # Same offset used in embedding
            
            # Calculate spacing (same as embedding)
            usable_coeffs = len(detail_band) - 16
            
            # CRITICAL FIX: Try multiple spacing values to find the right one
            magic_found = False
            
            for spacing in [4, 3, 2, 1]:  # Try all possible spacing values (most common first)
                extracted_bits = []
                
                print(f"[SIMPLE AUDIO] Trying spacing {spacing} for extraction")
                
                # Extract bits using simple coefficient sign method
                max_bits = (len(detail_band) - offset) // spacing
                for bit_idx in range(max_bits):
                    coeff_idx = offset + (bit_idx * spacing)
                    if coeff_idx < len(detail_band):
                        coeff = detail_band[coeff_idx]
                        # More robust extraction with threshold to handle precision issues
                        # Use a small threshold to avoid noise-related errors
                        threshold = 1e-6
                        if abs(coeff) < threshold:
                            # If coefficient is too close to zero, treat as 0
                            bit_value = 0
                        else:
                            # Clear distinction: positive = 1, negative = 0
                            bit_value = 1 if coeff > 0 else 0
                        extracted_bits.append(str(bit_value))
                
                # Test if this produces valid magic header
                if len(extracted_bits) >= 48:  # Need at least 6 bytes for magic
                    test_bytes = []
                    for i in range(0, 48, 8):
                        if i + 7 < len(extracted_bits):
                            byte_bits = ''.join(extracted_bits[i:i+8])
                            test_bytes.append(int(byte_bits, 2))
                    
                    if len(test_bytes) >= 6 and bytes(test_bytes[:6]) == b'SAUDIO':
                        print(f"[SIMPLE AUDIO] Found valid magic with spacing {spacing}")
                        magic_found = True
                        break
            
            if not magic_found:
                print(f"[SIMPLE AUDIO] No valid magic header found with any spacing")
            
            # Convert to bytes
            extracted_bytes = []
            for i in range(0, len(extracted_bits), 8):
                if i + 7 < len(extracted_bits):
                    byte_bits = ''.join(extracted_bits[i:i+8])
                    byte_val = int(byte_bits, 2)
                    extracted_bytes.append(byte_val)
            
            if len(extracted_bytes) < 10:  # Need at least magic + length
                print(f"[SIMPLE AUDIO] Not enough data extracted: {len(extracted_bytes)} bytes")
                return None
            
            # Check magic header
            magic = bytes(extracted_bytes[:6])
            if magic != b'SAUDIO':
                print(f"[SIMPLE AUDIO] Invalid magic header: {magic}")
                return None
            
            # Try new format with metadata first, fall back to old format
            try:
                # New format: magic + metadata_length + metadata + data_length + data
                metadata_length = struct.unpack('<I', bytes(extracted_bytes[6:10]))[0]
                
                # Validate metadata length is reasonable
                if metadata_length > 1000 or metadata_length < 10:
                    raise ValueError("Invalid metadata length, trying old format")
                    
                print(f"[SIMPLE AUDIO] Metadata length: {metadata_length} bytes")
                
                # Extract metadata
                metadata_start = 10
                metadata_end = metadata_start + metadata_length
                
                if len(extracted_bytes) < metadata_end + 4:
                    raise ValueError("Not enough data for new format")
                    
                metadata_bytes = bytes(extracted_bytes[metadata_start:metadata_end])
                
                import json
                metadata = json.loads(metadata_bytes.decode('utf-8'))
                original_filename = metadata.get('filename', 'extracted_data.bin')
                print(f"[SIMPLE AUDIO] Original filename: {original_filename}")
                
                # Get data length
                data_length = struct.unpack('<I', bytes(extracted_bytes[metadata_end:metadata_end+4]))[0]
                print(f"[SIMPLE AUDIO] Data length: {data_length} bytes")
                
                data_start = metadata_end + 4
                if len(extracted_bytes) < data_start + data_length:
                    raise ValueError(f"Not enough data: need {data_start + data_length}, have {len(extracted_bytes)}")
                
                # Extract the actual data
                data_bytes = bytes(extracted_bytes[data_start:data_start+data_length])
                
            except (ValueError, json.JSONDecodeError, struct.error) as e:
                # Fall back to old format: magic + data_length + data
                print(f"[SIMPLE AUDIO] New format failed ({e}), trying old format")
                
                if len(extracted_bytes) < 10:
                    print(f"[SIMPLE AUDIO] Not enough data for old format")
                    return None
                    
                # Get data length (old format)
                data_length = struct.unpack('<I', bytes(extracted_bytes[6:10]))[0]
                print(f"[SIMPLE AUDIO] Data length (old format): {data_length} bytes")
                
                if len(extracted_bytes) < 10 + data_length:
                    print(f"[SIMPLE AUDIO] Not enough data: need {10 + data_length}, have {len(extracted_bytes)}")
                    return None
                
                # Extract the actual data
                data_bytes = bytes(extracted_bytes[10:10+data_length])
                original_filename = None  # Will use format detection for old format
            
            # Decrypt if password was used
            if self.password:
                try:
                    print(f"[SIMPLE AUDIO] Attempting decryption with password: {repr(self.password)}")
                    print(f"[SIMPLE AUDIO] Encrypted data length: {len(data_bytes)} bytes")
                    print(f"[SIMPLE AUDIO] Encrypted data first 20 bytes: {data_bytes[:20]}")
                    final_data = self._decrypt_data(data_bytes)
                    print(f"[SIMPLE AUDIO] Decrypted successfully, result length: {len(final_data)} bytes")
                except Exception as e:
                    print(f"[SIMPLE AUDIO] Decryption failed: {e}")
                    print(f"[SIMPLE AUDIO] Error type: {type(e)}")
                    import traceback
                    traceback.print_exc()
                    return None
            else:
                print(f"[SIMPLE AUDIO] No password set, using raw data")
                final_data = data_bytes
            
            # Use original filename if available, otherwise detect format
            if original_filename:
                filename = original_filename
            else:
                # Old format - detect from content
                filename = self._detect_file_format(final_data)
                
            return (final_data, filename)
                
        except Exception as e:
            print(f"[SIMPLE AUDIO] Extraction error: {e}")
            return None
    
    def _detect_file_format(self, data: bytes) -> str:
        """Detect file format from binary signature and return appropriate filename"""
        
        if not data:
            return 'extracted_data.bin'
        
        # Check for common file signatures
        if data.startswith(b'ID3') or data.startswith(b'\xff\xfb') or data.startswith(b'\xff\xf3') or data.startswith(b'\xff\xf2'):
            return 'extracted_audio.mp3'
        elif data.startswith(b'RIFF') and b'WAVE' in data[:20]:
            return 'extracted_audio.wav'
        elif data.startswith(b'fLaC'):
            return 'extracted_audio.flac'
        elif data.startswith(b'OggS'):
            return 'extracted_audio.ogg'
        # Image formats
        elif data.startswith(b'\xff\xd8\xff'):
            return 'extracted_image.jpg'
        elif data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'extracted_image.png'
        elif data.startswith(b'GIF8'):
            return 'extracted_image.gif'
        # Video formats
        elif data.startswith(b'\x00\x00\x00\x14ftyp') or data.startswith(b'\x00\x00\x00\x18ftyp') or data.startswith(b'\x00\x00\x00\x1cftyp') or data.startswith(b'\x00\x00\x00\x20ftyp'):
            return 'extracted_video.mp4'
        elif data.startswith(b'RIFF') and b'AVI ' in data[:20]:
            return 'extracted_video.avi'
        # Document formats  
        elif data.startswith(b'%PDF'):
            return 'extracted_document.pdf'
        elif data.startswith(b'PK\x03\x04') and b'word/' in data[:1000]:
            return 'extracted_document.docx'
        elif data.startswith(b'PK\x03\x04') and b'xl/' in data[:1000]:
            return 'extracted_document.xlsx'
        elif data.startswith(b'PK'):
            return 'extracted_archive.zip'
        # Text formats - check if it's valid UTF-8 text
        else:
            try:
                text_content = data.decode('utf-8')
                # Check if it looks like reasonable text (printable characters)
                if len(text_content) > 0 and all(c.isprintable() or c.isspace() for c in text_content[:100]):
                    return 'extracted_text.txt'
            except UnicodeDecodeError:
                pass
        
        # Default fallback
        return 'extracted_data.bin'

def test_universal_file_steganography():
    """Test hiding various file types in audio"""
    print("=== UNIVERSAL FILE-IN-AUDIO STEGANOGRAPHY TEST ===")
    
    # Create high-capacity audio (60 seconds)
    sr = 44100
    duration = 60
    t = np.linspace(0, duration, sr * duration)
    # Rich frequency content for better capacity
    audio = 0.15 * (
        np.sin(2 * np.pi * 440 * t) +
        0.8 * np.sin(2 * np.pi * 880 * t) +
        0.6 * np.sin(2 * np.pi * 1320 * t) +
        0.4 * np.sin(2 * np.pi * 220 * t) +
        0.3 * np.random.normal(0, 0.1, len(t))
    )
    sf.write('universal_test_audio.wav', audio, sr)
    
    stego = UniversalFileAudio()
    
    # Check capacity
    max_bytes, total_coeffs, samples, sr_check = stego._get_audio_capacity('universal_test_audio.wav')
    print(f"📊 Audio capacity: {stego._format_size(max_bytes)} in {duration}s audio")
    print(f"🔊 Total coefficients: {total_coeffs}")
    
    # Create test files of various types
    test_files = []
    
    # 1. Text file
    text_content = """This is a secret text document!
    
It contains multiple lines of text with various characters:
- Special symbols: !@#$%^&*()
- Numbers: 1234567890
- Unicode: 🔒🎵📁✅
- Formatted text with spaces and tabs

This document demonstrates that any text file can be hidden
inside audio files using our steganography system.

The system preserves all formatting, special characters,
and maintains perfect file integrity during extraction.

End of secret document.
""" * 5  # Make it larger
    
    with open('secret_document.txt', 'w', encoding='utf-8') as f:
        f.write(text_content)
    test_files.append(('secret_document.txt', 'Text Document'))
    
    # 2. JSON file (structured data)
    json_data = {
        "secret_data": {
            "mission": "steganography_test",
            "agents": ["Alice", "Bob", "Charlie"],
            "coordinates": [{"lat": 40.7128, "lng": -74.0060}, {"lat": 51.5074, "lng": -0.1278}],
            "encrypted_payload": "VGhpcyBpcyBhIHNlY3JldCBtZXNzYWdl",
            "status": "active",
            "priority": 9,
            "metadata": {
                "created": "2025-10-03",
                "expires": "2025-12-31",
                "classification": "TOP SECRET"
            }
        }
    }
    
    with open('secret_data.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    test_files.append(('secret_data.json', 'JSON Data'))
    
    # 3. CSV file
    csv_content = """Name,Age,Department,Salary,Secret_Code
John Doe,30,Engineering,75000,X7Y9Z2
Jane Smith,28,Marketing,65000,A5B8C1
Bob Johnson,35,Finance,80000,M3N6P9
Alice Brown,32,HR,70000,Q2W5E8
Charlie Wilson,29,IT,72000,R4T7Y1"""
    
    with open('employee_data.csv', 'w', encoding='utf-8') as f:
        f.write(csv_content)
    test_files.append(('employee_data.csv', 'CSV Spreadsheet'))
    
    # 4. Python script
    python_code = '''#!/usr/bin/env python3
"""
Secret Python Script Hidden in Audio
This demonstrates that executable code can be hidden and extracted.
"""

import os
import sys
import base64

def secret_function():
    """A secret function that does secret operations"""
    secret_key = "VGhpcyBpcyBhIHNlY3JldCBrZXk="
    decoded = base64.b64decode(secret_key).decode('utf-8')
    print(f"Secret revealed: {decoded}")
    
    # Perform some calculations
    result = sum(i**2 for i in range(100))
    print(f"Secret calculation result: {result}")
    
    return result

def main():
    """Main function of the secret script"""
    print("🔒 Secret Python Script Executed!")
    print("This script was hidden inside an audio file.")
    
    result = secret_function()
    
    # Generate secret report
    report = {
        'status': 'success',
        'calculation': result,
        'message': 'Script executed from steganographic extraction'
    }
    
    print(f"📊 Report: {report}")
    return report

if __name__ == "__main__":
    main()
'''
    
    with open('secret_script.py', 'w', encoding='utf-8') as f:
        f.write(python_code)
    test_files.append(('secret_script.py', 'Python Script'))
    
    # 5. HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secret Web Page</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 20px;
        }
        .secret-content {
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .code { 
            background: #333; 
            padding: 10px; 
            border-radius: 5px; 
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h1>🔒 Secret Web Page</h1>
    <div class="secret-content">
        <h2>Hidden in Audio Steganography</h2>
        <p>This HTML page was secretly embedded inside an audio file!</p>
        
        <h3>Secret Information:</h3>
        <ul>
            <li>Project: Audio Steganography</li>
            <li>Status: Operational</li>
            <li>Encryption: AES-256</li>
            <li>Capacity: Multi-file support</li>
        </ul>
        
        <div class="code">
            console.log("Secret page loaded from steganographic extraction!");
        </div>
    </div>
    
    <script>
        alert("🎉 Secret HTML file successfully extracted from audio!");
        console.log("This webpage was hidden in audio coefficients!");
    </script>
</body>
</html>'''
    
    with open('secret_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    test_files.append(('secret_page.html', 'HTML Webpage'))
    
    # Test each file type
    successful_tests = 0
    
    for filename, description in test_files:
        print(f"\n{'='*60}")
        print(f"📁 Testing: {description} ({filename})")
        print('='*60)
        
        try:
            # Get file info
            file_size = os.path.getsize(filename)
            print(f"📊 Original file: {stego._format_size(file_size)}")
            
            # Embed
            result = stego.embed_file('universal_test_audio.wav', filename, f'stego_{filename}.wav')
            print(f"✅ Embedding successful!")
            print(f"📋 Result: {result}")
            
            # Extract
            extracted_path = stego.extract_file(f'stego_{filename}.wav', output_dir='.')
            print(f"✅ Extraction successful!")
            
            # Verify file integrity
            with open(filename, 'rb') as f1, open(extracted_path, 'rb') as f2:
                original_data = f1.read()
                extracted_data = f2.read()
                
                if original_data == extracted_data:
                    print(f"✅ PERFECT FILE INTEGRITY - 100% match!")
                    successful_tests += 1
                else:
                    print(f"❌ File integrity failed!")
            
            # Clean up
            for f in [f'stego_{filename}.wav']:
                if os.path.exists(f):
                    os.remove(f)
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 UNIVERSAL FILE STEGANOGRAPHY TEST COMPLETE!")
    print(f"📊 Results: {successful_tests}/{len(test_files)} file types successful")
    print('='*60)
    
    if successful_tests == len(test_files):
        print("✅ ALL FILE TYPES WORKING PERFECTLY!")
        print("🔒 Text files, JSON, CSV, Python scripts, HTML - all supported!")
    
    # Clean up test files
    cleanup_files = [
        'universal_test_audio.wav', 'secret_document.txt', 'secret_data.json',
        'employee_data.csv', 'secret_script.py', 'secret_page.html',
        'extracted_secret_document.txt', 'extracted_secret_data.json',
        'extracted_employee_data.csv', 'extracted_secret_script.py', 'extracted_secret_page.html'
    ]
    
    for f in cleanup_files:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    test_universal_file_steganography()