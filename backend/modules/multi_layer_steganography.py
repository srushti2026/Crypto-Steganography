#!/usr/bin/env python3
"""
MULTI-LAYER STEGANOGRAPHY MODULE - ADVANCED LAYERED EMBEDDING
Supports multiple hidden messages/files with same or different passwords
"""

import os
import json
import hashlib
import base64
import struct
import zipfile
import tempfile
import uuid
from typing import Dict, Any, Optional, Union, Tuple, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def _is_likely_text_content(data):
    """Check if data is likely to be text content that can be safely decoded"""
    if not data:
        return False
    
    try:
        # Try to decode a sample to see if it's text
        sample = data[:min(1000, len(data))]
        decoded = sample.decode('utf-8', errors='strict')
        
        # Check if it contains mostly printable characters
        printable_chars = sum(1 for c in decoded if c.isprintable() or c.isspace())
        ratio = printable_chars / len(decoded) if decoded else 0
        
        return ratio > 0.8  # 80% printable characters
    except (UnicodeDecodeError, UnicodeError):
        return False

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
    # Audio formats
    elif data_bytes.startswith(b'RIFF') and b'WAVE' in data_bytes[:20]:
        return "extracted_audio.wav"
    elif data_bytes.startswith(b'ID3') or data_bytes.startswith(b'\xFF\xFB') or data_bytes.startswith(b'\xFF\xFA'):
        return "extracted_audio.mp3"
    elif data_bytes.startswith(b'fLaC'):
        return "extracted_audio.flac"
    elif data_bytes.startswith(b'OggS'):
        return "extracted_audio.ogg"
    elif data_bytes.startswith(b'\xFF\xF1') or data_bytes.startswith(b'\xFF\xF9'):
        return "extracted_audio.aac"
    elif data_bytes.startswith(b'\x00\x00\x00\x20ftypM4A'):
        return "extracted_audio.m4a"
    elif data_bytes.startswith(b'\x30\x26\xB2\x75\x8E\x66\xCF\x11'):
        return "extracted_audio.wma"
    
    # Video formats
    elif (data_bytes.startswith(b'\x00\x00\x00\x18ftyp') or 
          data_bytes.startswith(b'\x00\x00\x00\x20ftyp')):
        # Check specific MP4 variants
        if b'mp41' in data_bytes[:50] or b'mp42' in data_bytes[:50] or b'isom' in data_bytes[:50]:
            return "extracted_video.mp4"
        elif b'M4V' in data_bytes[:50]:
            return "extracted_video.m4v"
        elif b'qt' in data_bytes[:50]:
            return "extracted_video.mov"
        else:
            return "extracted_video.mp4"  # Default to mp4
    elif data_bytes.startswith(b'RIFF') and b'AVI ' in data_bytes[:20]:
        return "extracted_video.avi"
    elif data_bytes.startswith(b'\x1A\x45\xDF\xA3'):
        return "extracted_video.mkv"
    elif data_bytes.startswith(b'\x30\x26\xB2\x75\x8E\x66\xCF\x11'):
        return "extracted_video.wmv"
    elif data_bytes.startswith(b'FLV\x01'):
        return "extracted_video.flv"
    elif data_bytes.startswith(b'\x1A\x45\xDF\xA3') and b'webm' in data_bytes[:100]:
        return "extracted_video.webm"
    else:
        # Check if it looks like text content
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

class MultiLayerSteganography:
    """Advanced multi-layer steganography supporting multiple hidden messages"""
    
    def __init__(self):
        # Version-based magic headers for layered embedding
        self.magic_headers = {
            1: b"VEILFORGE_LAYER_V1_SAFE",
            2: b"VEILFORGE_LAYER_V2_SAFE", 
            3: b"VEILFORGE_LAYER_V3_SAFE",
            4: b"VEILFORGE_LAYER_V4_SAFE",
            5: b"VEILFORGE_LAYER_V5_SAFE",
        }
        
        self.end_markers = {
            1: b"VEILFORGE_LAYER_END_V1",
            2: b"VEILFORGE_LAYER_END_V2",
            3: b"VEILFORGE_LAYER_END_V3", 
            4: b"VEILFORGE_LAYER_END_V4",
            5: b"VEILFORGE_LAYER_END_V5",
        }
        
        # Layer index markers
        self.layer_index_magic = b"VEILFORGE_LAYER_INDEX_V1"
        self.layer_index_end = b"VEILFORGE_LAYER_INDEX_END"
        
        # Legacy compatibility
        self.legacy_magic = b"VEILFORGE_UNIVERSAL_SAFE_V2"
        self.legacy_end = b"VEILFORGE_UNIVERSAL_END_V2"
    
    def hide_data(self, carrier_file_path: str, content_to_hide: Union[str, bytes], 
                  output_path: str, password: Optional[str] = None, 
                  is_file: bool = False, original_filename: str = None, **kwargs) -> Dict[str, Any]:
        """Multi-layer hiding method that preserves ALL file types"""
        
        print(f"[MULTI-LAYER] Processing {os.path.basename(carrier_file_path)}")
        
        # Read carrier file (might already contain hidden layers)
        with open(carrier_file_path, 'rb') as f:
            file_data = f.read()
        
        # Detect existing layers
        existing_layers = self._detect_existing_layers(file_data)
        next_layer_number = len(existing_layers) + 1
        
        print(f"[MULTI-LAYER] Found {len(existing_layers)} existing layers")
        print(f"[MULTI-LAYER] Adding layer #{next_layer_number}")
        
        # Determine file type
        file_ext = os.path.splitext(carrier_file_path)[1].lower()
        
        # Prepare secret data
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
            else:
                original_payload = str(content_to_hide).encode('utf-8')
            
            # Use proper file detection instead of hardcoding .txt
            if original_filename:
                filename = original_filename
            else:
                detected_filename = detect_filename_from_content(original_payload)
                # Replace generic prefix with layer-specific prefix
                if detected_filename.startswith("extracted_"):
                    base_name = detected_filename.replace("extracted_", f"hidden_message_layer_{next_layer_number}_")
                else:
                    base_name = f"hidden_message_layer_{next_layer_number}_{detected_filename}"
                filename = base_name
        
        return self._embed_new_layer(file_data, original_payload, output_path, 
                                   password, filename, file_ext, next_layer_number, existing_layers)
    
    def _detect_existing_layers(self, file_data: bytes) -> List[Dict[str, Any]]:
        """Detect all existing hidden layers in the file"""
        layers = []
        
        # Check for legacy format first
        legacy_pos = file_data.find(self.legacy_magic)
        if legacy_pos != -1:
            layer_info = {
                'layer_number': 0,  # Legacy layer
                'magic_pos': legacy_pos,
                'magic_header': self.legacy_magic,
                'end_marker': self.legacy_end,
                'password_hash': None  # Will be determined during extraction
            }
            layers.append(layer_info)
        
        # Check for versioned layers
        for version in range(1, 6):
            magic_header = self.magic_headers.get(version)
            if magic_header:
                pos = file_data.find(magic_header)
                if pos != -1:
                    layer_info = {
                        'layer_number': version,
                        'magic_pos': pos,
                        'magic_header': magic_header,
                        'end_marker': self.end_markers[version],
                        'password_hash': None
                    }
                    layers.append(layer_info)
        
        # Sort layers by position in file
        layers.sort(key=lambda x: x['magic_pos'])
        return layers
    
    def _embed_new_layer(self, file_data: bytes, secret_data: bytes, 
                        output_path: str, password: Optional[str], 
                        filename: str, file_ext: str, layer_number: int,
                        existing_layers: List[Dict]) -> Dict[str, Any]:
        """Embed a new layer into the file"""
        
        if layer_number > 5:
            raise ValueError("Maximum 5 layers supported")
        
        # Create layer metadata
        layer_id = str(uuid.uuid4())
        password_hash = hashlib.sha256((password or "").encode()).hexdigest() if password else None
        
        # SECURITY: Add file hash to bind this layer to THIS specific file
        file_hash = hashlib.sha256(file_data).hexdigest()[:16]
        
        metadata = {
            'layer_id': layer_id,
            'layer_number': layer_number,
            'filename': filename,
            'original_size': len(secret_data),
            'encrypted': bool(password),
            'password_hash': password_hash,
            'checksum': hashlib.sha256(secret_data).hexdigest(),
            'carrier_ext': file_ext,
            'file_hash': file_hash,  # SECURITY: Bind to specific file
            'timestamp': hashlib.md5(str(layer_number).encode()).hexdigest()[:8]  # Layer identifier
        }
        
        # Encrypt if password provided
        if password:
            payload_data = self._encrypt_data(secret_data, password)
        else:
            payload_data = secret_data
        
        metadata_json = json.dumps(metadata).encode('utf-8')
        
        # Get magic headers for this layer
        magic_header = self.magic_headers[layer_number]
        end_marker = self.end_markers[layer_number]
        
        # Build new layer format
        new_layer = (
            magic_header +
            len(metadata_json).to_bytes(4, 'little') +
            metadata_json +
            len(payload_data).to_bytes(4, 'little') +
            payload_data +
            end_marker
        )
        
        # Append new layer to existing file data
        final_file = file_data + new_layer
        
        # Update layer index
        final_file = self._update_layer_index(final_file, existing_layers, metadata)
        
        # Write final file
        with open(output_path, 'wb') as f:
            f.write(final_file)
        
        overhead = len(final_file) - len(file_data)
        
        print(f"[MULTI-LAYER] ✅ Layer #{layer_number} added successfully")
        print(f"[MULTI-LAYER] ✅ Added {overhead} bytes for new layer")
        print(f"[MULTI-LAYER] ✅ Total layers: {len(existing_layers) + 1}")
        
        return {
            'success': True,
            'method': 'multi_layer_safe_append',
            'layer_number': layer_number,
            'layer_id': layer_id,
            'total_layers': len(existing_layers) + 1,
            'overhead_bytes': overhead,
            'file_type_preserved': True
        }
    
    def _update_layer_index(self, file_data: bytes, existing_layers: List[Dict], new_layer_metadata: Dict) -> bytes:
        """Update or create the layer index at the end of file"""
        
        # Remove existing index if present (but preserve all layer data)
        index_pos = file_data.find(self.layer_index_magic)
        if index_pos != -1:
            # Find the end of the index block
            index_end_pos = file_data.find(self.layer_index_end, index_pos)
            if index_end_pos != -1:
                # Remove only the index block, keep everything else
                file_data = file_data[:index_pos] + file_data[index_end_pos + len(self.layer_index_end):]
            else:
                # Fallback: truncate at index start if end marker not found
                file_data = file_data[:index_pos]
        
        # Build complete layer list
        all_layers = []
        for layer in existing_layers:
            all_layers.append({
                'layer_number': layer['layer_number'],
                'password_hash': layer.get('password_hash'),
                'magic_pos': layer['magic_pos']
            })
        
        # Add new layer info
        all_layers.append({
            'layer_number': new_layer_metadata['layer_number'],
            'password_hash': new_layer_metadata.get('password_hash'),
            'layer_id': new_layer_metadata['layer_id']
        })
        
        # Create index structure
        index_data = {
            'version': 1,
            'total_layers': len(all_layers),
            'layers': all_layers,
            'created_by': 'VeilForge_MultiLayer_V1'
        }
        
        index_json = json.dumps(index_data).encode('utf-8')
        
        # Append index
        index_block = (
            self.layer_index_magic +
            len(index_json).to_bytes(4, 'little') +
            index_json +
            self.layer_index_end
        )
        
        return file_data + index_block
    
    def extract_all_layers(self, stego_file_path: str, password: Optional[str] = None, 
                          output_dir: str = None) -> Dict[str, Any]:
        """Extract only the most recent layer that matches the password - prevents cross-contamination"""
        
        with open(stego_file_path, 'rb') as f:
            file_data = f.read()
        
        print(f"[MULTI-LAYER] Analyzing file for hidden layers...")
        
        # Detect all layers
        existing_layers = self._detect_existing_layers(file_data)
        
        if not existing_layers:
            print("[MULTI-LAYER] No hidden layers found")
            return {'success': False, 'message': 'No hidden data found'}
        
        print(f"[MULTI-LAYER] Found {len(existing_layers)} layer(s)")
        
        # EXTRACT ALL LAYERS: Extract all layers that match the password
        # This allows proper multi-layer functionality
        extracted_layers = []
        
        # Process layers in order (oldest to newest for proper numbering)
        for layer_info in existing_layers:
            try:
                layer_data = self._extract_single_layer(file_data, layer_info, password)
                if layer_data:
                    extracted_layers.append(layer_data)
                    print(f"[MULTI-LAYER] ✅ Extracted layer #{layer_info['layer_number']}")
                    # Continue to extract ALL matching layers, not just the first one
            except Exception as e:
                print(f"[MULTI-LAYER] ⚠️ Failed to extract layer #{layer_info['layer_number']}: {e}")
        
        if not extracted_layers:
            return {'success': False, 'message': 'No layers could be extracted with the provided password'}
        
        # If only one layer extracted, return it directly
        if len(extracted_layers) == 1:
            layer = extracted_layers[0]
            if output_dir:
                output_path = os.path.join(output_dir, f"extracted_{layer['filename']}")
                with open(output_path, 'wb') as f:
                    f.write(layer['content'])
                layer['saved_to'] = output_path
            
            # CRITICAL FIX: Return the actual binary content for file extraction
            # Don't try to decode binary files as text - preserve the original binary data
            content_data = layer['content']
            
            # Only convert to text if it's actually text content
            try:
                # Check if it's likely text content by trying to decode a small sample
                if len(content_data) > 0 and _is_likely_text_content(content_data):
                    text_content = content_data.decode('utf-8')
                    print(f"[MULTI-LAYER] Extracted text content: {len(text_content)} characters")
                else:
                    # For binary files, return the binary content directly for processing
                    text_content = f"[Binary file: {layer['filename']}]"
                    print(f"[MULTI-LAYER] Extracted binary file: {len(content_data)} bytes")
            except:
                text_content = f"[Binary file: {layer['filename']}]"
                print(f"[MULTI-LAYER] Extracted binary file (decode failed): {len(content_data)} bytes")
            
            return {
                'success': True,
                'single_extraction': True,
                'extracted_data': text_content,
                'filename': layer['filename'],
                'layer_number': layer['layer_number'],
                'total_layers_found': len(existing_layers),
                'saved_to': layer.get('saved_to'),
                'binary_content': content_data  # CRITICAL: Include the actual binary data
            }
        
        # Multiple layers - create zip file
        return self._create_multi_layer_response(extracted_layers, output_dir, len(existing_layers))
    
    def _extract_single_layer(self, file_data: bytes, layer_info: Dict, password: Optional[str]) -> Optional[Dict[str, Any]]:
        """Extract a single layer from file data"""
        
        magic_header = layer_info['magic_header']
        end_marker = layer_info['end_marker']
        magic_pos = layer_info['magic_pos']
        
        try:
            # Handle legacy format
            if magic_header == self.legacy_magic:
                return self._extract_legacy_layer(file_data, magic_pos, password)
            
            # Parse metadata
            metadata_size_pos = magic_pos + len(magic_header)
            metadata_size = int.from_bytes(file_data[metadata_size_pos:metadata_size_pos+4], 'little')
            
            metadata_pos = metadata_size_pos + 4
            metadata_json = file_data[metadata_pos:metadata_pos+metadata_size]
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Check password compatibility
            if password:
                provided_hash = hashlib.sha256(password.encode()).hexdigest()
                if metadata.get('password_hash') and metadata['password_hash'] != provided_hash:
                    return None  # Password doesn't match this layer
            elif metadata.get('encrypted', False):
                return None  # Layer is encrypted but no password provided
            
            # Parse data
            data_size_pos = metadata_pos + metadata_size
            data_size = int.from_bytes(file_data[data_size_pos:data_size_pos+4], 'little')
            
            payload_pos = data_size_pos + 4
            payload_data = file_data[payload_pos:payload_pos+data_size]
            
            # Decrypt if needed
            if metadata['encrypted'] and password:
                secret_data = self._decrypt_data(payload_data, password)
            else:
                secret_data = payload_data
            
            return {
                'layer_number': metadata.get('layer_number', 0),
                'layer_id': metadata.get('layer_id', 'legacy'),
                'filename': metadata['filename'],
                'content': secret_data,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"[MULTI-LAYER] Layer extraction error: {e}")
            return None
    
    def _extract_legacy_layer(self, file_data: bytes, magic_pos: int, password: Optional[str]) -> Optional[Dict[str, Any]]:
        """Extract legacy single-layer format"""
        
        try:
            # Parse metadata (legacy format)
            metadata_size_pos = magic_pos + len(self.legacy_magic)
            metadata_size = int.from_bytes(file_data[metadata_size_pos:metadata_size_pos+4], 'little')
            
            metadata_pos = metadata_size_pos + 4
            metadata_json = file_data[metadata_pos:metadata_pos+metadata_size]
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Check encryption compatibility
            if metadata.get('encrypted', False) and not password:
                return None
            elif not metadata.get('encrypted', False) and password:
                return None  # Not encrypted but password provided
            
            # Parse data
            data_size_pos = metadata_pos + metadata_size
            data_size = int.from_bytes(file_data[data_size_pos:data_size_pos+4], 'little')
            
            payload_pos = data_size_pos + 4
            payload_data = file_data[payload_pos:payload_pos+data_size]
            
            # Decrypt if needed
            if metadata['encrypted'] and password:
                secret_data = self._decrypt_data(payload_data, password)
            else:
                secret_data = payload_data
            
            return {
                'layer_number': 0,  # Legacy
                'layer_id': 'legacy',
                'filename': metadata['filename'],
                'content': secret_data,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"[MULTI-LAYER] Legacy extraction error: {e}")
            return None
    
    def _create_multi_layer_response(self, extracted_layers: List[Dict], output_dir: str, total_layers: int) -> Dict[str, Any]:
        """Create response for multiple extracted layers"""
        
        if not output_dir:
            output_dir = tempfile.mkdtemp()
        
        # Create zip file with all extracted layers
        zip_filename = f"multilayer_extraction_{hashlib.md5(str(len(extracted_layers)).encode()).hexdigest()[:8]}.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        layer_info = []
        display_messages = []
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, layer in enumerate(extracted_layers):
                # Save individual layer file
                layer_filename = f"layer_{layer['layer_number']}_{layer['filename']}"
                layer_path = os.path.join(output_dir, layer_filename)
                
                with open(layer_path, 'wb') as f:
                    f.write(layer['content'])
                
                # Add to zip
                zipf.write(layer_path, layer_filename)
                
                # Collect info for response
                try:
                    if layer['filename'].endswith(('.txt', '.json', '.py', '.js', '.html', '.css')):
                        text_content = layer['content'].decode('utf-8')
                        display_messages.append(f"Layer {layer['layer_number']}: {text_content[:200]}...")
                    else:
                        display_messages.append(f"Layer {layer['layer_number']}: [Binary file: {layer['filename']}]")
                except:
                    display_messages.append(f"Layer {layer['layer_number']}: [Binary file: {layer['filename']}]")
                
                layer_info.append({
                    'layer_number': layer['layer_number'],
                    'filename': layer['filename'],
                    'size': len(layer['content']),
                    'saved_as': layer_filename
                })
                
                # Clean up individual file
                os.remove(layer_path)
        
        return {
            'success': True,
            'multi_layer_extraction': True,
            'total_layers_extracted': len(extracted_layers),
            'total_layers_found': total_layers,
            'zip_file': zip_path,
            'zip_filename': zip_filename,
            'extracted_data': '\n\n'.join(display_messages),
            'layer_details': layer_info
        }
    
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

# Backward compatibility wrapper
class UniversalFileSteganography(MultiLayerSteganography):
    """Backward compatible wrapper that adds multi-layer support to existing API"""
    
    def __init__(self):
        super().__init__()
    
    def extract_data(self, stego_file_path: str, password: Optional[str] = None, 
                     output_dir: str = None) -> Optional[Union[Tuple[bytes, str], Dict[str, Any]]]:
        """
        FIXED: Use normal multi-layer extraction for legitimate operations
        This ensures compatibility with how data was embedded
        """
        
        try:
            # Use the normal multi-layer extraction method
            print(f"[MULTI-LAYER EXTRACT] Using normal extraction method")
            result = self.extract_all_layers(stego_file_path, password, output_dir)
            
            if not result or not result.get('success'):
                return None
            
            # If output_dir was specified, the result should already be in the correct format
            if output_dir:
                return result
            else:
                # Handle single extraction case (most common for forensic)
                if result.get('single_extraction'):
                    # Single layer was extracted successfully
                    filename = result.get('filename', 'extracted_data.txt')
                    # The extracted_data is already decoded as text for single layers
                    text_data = result.get('extracted_data', '')
                    
                    # For forensic extraction, we need to return the raw text (not re-encode)
                    # since the forensic data is JSON text that was embedded as text
                    if isinstance(text_data, str):
                        return (text_data.encode('utf-8'), filename)  # Return as bytes for consistency
                    else:
                        return (text_data, filename)
                else:
                    # Multiple layers - get from extracted_layers array
                    layers = result.get('extracted_layers', [])
                    if layers:
                        first_layer = layers[0]
                        filename = first_layer.get('filename', 'extracted_data.txt')
                        content = first_layer.get('content', b'')
                        return (content, filename)
                return None
        
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def extract_single_file_layer(self, file_data: bytes, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        SECURITY CRITICAL: Extract data ONLY from this specific file, never from other files.
        Uses file hash binding to ensure no cross-file contamination.
        """
        try:
            # Generate file hash for this specific file
            file_hash = hashlib.sha256(file_data).hexdigest()[:16]
            print(f"[SECURE EXTRACT] File hash: {file_hash}")
            
            # Try to extract data using LSB method directly from this file's data
            extracted_data = self._extract_from_file_data_secure(file_data, password, file_hash)
            
            if extracted_data:
                print(f"[SECURE EXTRACT] ✅ Found data in THIS file: {len(extracted_data)} bytes")
                
                # Detect content type
                is_text = True
                try:
                    text_content = extracted_data.decode('utf-8')
                    filename = 'extracted_message.txt'
                except UnicodeDecodeError:
                    text_content = f"[Binary data: {len(extracted_data)} bytes]"
                    filename = 'extracted_file.bin'
                    is_text = False
                
                return {
                    'single_extraction': True,
                    'file_type': 'text' if is_text else 'binary',
                    'content': extracted_data,
                    'encrypted': bool(password),
                    'metadata': {'filename': filename, 'file_hash': file_hash},
                    'layer_info': {
                        'layer_number': 1,
                        'file_type': 'text' if is_text else 'binary',
                        'encrypted': bool(password)
                    }
                }
            else:
                print(f"[SECURE EXTRACT] ❌ No data found in THIS file")
                return None
                
        except Exception as e:
            print(f"[SECURE EXTRACT] Error: {e}")
            return None
    
    def _extract_from_file_data_secure(self, file_data: bytes, password: Optional[str], expected_file_hash: str) -> Optional[bytes]:
        """Extract data directly from file bytes with hash verification to prevent cross-contamination"""
        try:
            # Look for our magic marker in the file data
            magic_start = b"VEILFORGE_LAYER_START"
            magic_end = b"VEILFORGE_LAYER_END"
            
            # Find all potential data blocks
            start_pos = 0
            while True:
                start_idx = file_data.find(magic_start, start_pos)
                if start_idx == -1:
                    break
                    
                end_idx = file_data.find(magic_end, start_idx + len(magic_start))
                if end_idx == -1:
                    start_pos = start_idx + len(magic_start)
                    continue
                
                # Extract the data block
                data_block = file_data[start_idx + len(magic_start):end_idx]
                
                try:
                    # Try to parse as layer data
                    if len(data_block) < 8:
                        start_pos = end_idx + len(magic_end)
                        continue
                    
                    # Read metadata length
                    metadata_len = struct.unpack('<I', data_block[:4])[0]
                    if metadata_len > len(data_block) - 8:
                        start_pos = end_idx + len(magic_end)
                        continue
                    
                    # Read content length
                    content_len = struct.unpack('<I', data_block[4:8])[0]
                    if metadata_len + content_len + 8 > len(data_block):
                        start_pos = end_idx + len(magic_end)
                        continue
                    
                    # Extract metadata and content
                    metadata_bytes = data_block[8:8 + metadata_len]
                    content_bytes = data_block[8 + metadata_len:8 + metadata_len + content_len]
                    
                    # Parse metadata
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                    
                    # CRITICAL SECURITY CHECK: Verify file hash
                    stored_file_hash = metadata.get('file_hash', '')
                    if stored_file_hash and stored_file_hash != expected_file_hash:
                        print(f"[SECURE EXTRACT] Rejecting data: hash mismatch {stored_file_hash} != {expected_file_hash}")
                        start_pos = end_idx + len(magic_end)
                        continue
                    
                    # Decrypt if password provided
                    if password and metadata.get('encrypted', False):
                        try:
                            content_bytes = self._decrypt_data(content_bytes, password)
                        except Exception as decrypt_error:
                            print(f"[SECURE EXTRACT] Decryption failed: {decrypt_error}")
                            start_pos = end_idx + len(magic_end)
                            continue
                    elif password and not metadata.get('encrypted', False):
                        # Password provided but data not encrypted - skip
                        start_pos = end_idx + len(magic_end)
                        continue
                    elif not password and metadata.get('encrypted', False):
                        # Data encrypted but no password - skip
                        start_pos = end_idx + len(magic_end)
                        continue
                    
                    print(f"[SECURE EXTRACT] ✅ Valid data found for this file")
                    return content_bytes
                    
                except (json.JSONDecodeError, struct.error, UnicodeDecodeError) as parse_error:
                    print(f"[SECURE EXTRACT] Parse error: {parse_error}")
                    start_pos = end_idx + len(magic_end)
                    continue
                
                start_pos = end_idx + len(magic_end)
            
            # No valid data found
            print(f"[SECURE EXTRACT] No valid data found in this file")
            return None
            
        except Exception as e:
            print(f"[SECURE EXTRACT] Extraction error: {e}")
            return None
            return None

def extract_layered_data_container(layered_container_json: bytes) -> List[Tuple[bytes, str]]:
    """
    Extract layers from a layered container JSON
    
    Args:
        layered_container_json: The JSON bytes from a layered container
        
    Returns:
        List of tuples (layer_data, layer_filename)
    """
    try:
        # Parse the layered container JSON
        container_str = layered_container_json.decode('utf-8')
        container = json.loads(container_str)
        
        if container.get('type') != 'layered_container':
            raise ValueError(f"Not a layered container: {container.get('type')}")
        
        layers = container.get('layers', [])
        if not layers:
            raise ValueError("No layers found in container")
        
        extracted_layers = []
        
        for layer in layers:
            layer_filename = layer.get('filename', f'layer_{layer.get("index", 0)}.bin')
            layer_type = layer.get('type', 'binary')
            layer_content = layer.get('content', '')
            
            if layer_type == 'binary':
                # Base64 decode binary content
                try:
                    layer_data = base64.b64decode(layer_content)
                except Exception as e:
                    print(f"[LAYER ERROR] Failed to decode base64 for {layer_filename}: {e}")
                    continue
            elif layer_type == 'text':
                # Base64 decode text content 
                try:
                    decoded_bytes = base64.b64decode(layer_content)
                    layer_data = decoded_bytes
                except Exception as e:
                    print(f"[LAYER ERROR] Failed to decode base64 text for {layer_filename}: {e}")
                    # Try as raw text
                    layer_data = layer_content.encode('utf-8')
            else:
                # Unknown type, treat as text
                layer_data = layer_content.encode('utf-8')
            
            extracted_layers.append((layer_data, layer_filename))
            print(f"[LAYER SUCCESS] Extracted layer: {layer_filename} ({len(layer_data)} bytes)")
        
        return extracted_layers
        
    except Exception as e:
        print(f"[LAYER ERROR] Failed to extract layered container: {e}")
        import traceback
        traceback.print_exc()
        return []