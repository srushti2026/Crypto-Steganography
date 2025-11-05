#!/usr/bin/env python3
"""
SAFE Document Steganography - Metadata-Based Approach

This implementation uses PDF metadata fields and comments to hide data
without touching the document structure, content streams, or cross-references.
"""

import os
import json
import struct
import hashlib
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets

class SafeDocumentSteganography:
    """Safe document steganography using metadata and comments"""
    
    def __init__(self, password: str = None):
        self.password = password
        self.magic_header = b'SAFE'
    
    def hide_file_in_document(self, document_path: str, secret_file_path: str, output_path: str) -> Dict[str, Any]:
        """Hide a file in a document using safe metadata embedding"""
        
        print(f"[SAFE] Hiding '{secret_file_path}' in document '{document_path}'")
        
        with open(document_path, 'rb') as f:
            document_data = f.read()
        
        with open(secret_file_path, 'rb') as f:
            secret_data = f.read()
        
        # Encrypt if password provided
        if self.password:
            encrypted_data = self._encrypt_data(secret_data)
            payload = encrypted_data
        else:
            payload = secret_data
        
        # Create metadata
        filename = os.path.basename(secret_file_path)
        metadata = {
            'filename': filename,
            'size': len(secret_data),
            'encrypted': bool(self.password),
            'checksum': hashlib.sha256(secret_data).hexdigest()[:16]
        }
        
        # Choose embedding method based on document type
        if document_data.startswith(b'%PDF'):
            modified_data = self._embed_in_pdf_metadata(document_data, payload, metadata)
        elif document_data.startswith(b'{\\rtf'):
            modified_data = self._embed_in_rtf_metadata(document_data, payload, metadata)
        elif document_data.startswith(b'PK'):  # DOCX, etc.
            modified_data = self._embed_in_zip_comment(document_data, payload, metadata)
        else:
            # Fallback: append to end with marker
            modified_data = self._embed_in_end_marker(document_data, payload, metadata)
        
        # Save result
        with open(output_path, 'wb') as f:
            f.write(modified_data)
        
        print(f"[SAFE] Successfully hidden data in '{output_path}'")
        print(f"[SAFE] Original size: {len(document_data)} bytes")
        print(f"[SAFE] Modified size: {len(modified_data)} bytes")
        print(f"[SAFE] Overhead: {len(modified_data) - len(document_data)} bytes")
        
        return {
            'success': True,
            'method': 'metadata_safe',
            'original_size': len(document_data),
            'output_size': len(modified_data),
            'overhead': len(modified_data) - len(document_data),
            'encrypted': bool(self.password)
        }
    
    def _embed_in_pdf_metadata(self, pdf_data: bytes, payload: bytes, metadata: dict) -> bytes:
        """Embed data in PDF using end marker (SAFE - doesn't modify existing structure)"""
        
        # For now, use the most reliable method - end marker
        # This is 100% safe as it doesn't modify any PDF structure
        print(f"[PDF] Using safe end-marker approach to preserve PDF integrity")
        return self._embed_in_end_marker(pdf_data, payload, metadata)
    
    def _embed_in_rtf_metadata(self, rtf_data: bytes, payload: bytes, metadata: dict) -> bytes:
        """Embed data in RTF using info group (SAFE)"""
        
        rtf_text = rtf_data.decode('latin-1', errors='ignore')
        
        # Find insertion point (after header, before content)
        insert_pos = rtf_text.find('\\f0') 
        if insert_pos == -1:
            insert_pos = len(rtf_text) - 10  # Before closing }
        else:
            insert_pos = rtf_text.find(' ', insert_pos) + 1
        
        # Encode data safely
        encoded_payload = base64.b64encode(payload).decode('ascii')
        encoded_metadata = base64.b64encode(json.dumps(metadata).encode()).decode('ascii')
        
        # Create RTF info group (invisible metadata)
        info_group = f'{{\\info{{\\comment SAFE_META:{encoded_metadata}}}{{\\keywords SAFE_DATA:{encoded_payload}}}}} '
        
        # Insert metadata
        modified_rtf = rtf_text[:insert_pos] + info_group + rtf_text[insert_pos:]
        
        print(f"[RTF] Added info group at position {insert_pos}")
        return modified_rtf.encode('latin-1')
    
    def _embed_in_zip_comment(self, zip_data: bytes, payload: bytes, metadata: dict) -> bytes:
        """Embed data in ZIP comment field (SAFE for DOCX, etc.)"""
        
        # ZIP files have a comment field at the end - completely safe to use
        encoded_data = base64.b64encode(payload).decode('ascii')
        encoded_metadata = base64.b64encode(json.dumps(metadata).encode()).decode('ascii')
        
        comment = f"SAFE_META:{encoded_metadata}|SAFE_DATA:{encoded_data}"
        comment_bytes = comment.encode('utf-8')
        
        if len(comment_bytes) > 65535:
            raise ValueError("Payload too large for ZIP comment field")
        
        # Modify ZIP end record to include comment
        # Find end of central directory record
        eocd_pos = zip_data.rfind(b'PK\x05\x06')
        if eocd_pos == -1:
            return self._embed_in_end_marker(zip_data, payload, metadata)
        
        # Replace comment length and add comment
        modified_zip = bytearray(zip_data)
        
        # Set comment length (bytes 20-21 of EOCD record)
        comment_len = len(comment_bytes)
        modified_zip[eocd_pos + 20] = comment_len & 0xFF
        modified_zip[eocd_pos + 21] = (comment_len >> 8) & 0xFF
        
        # Append comment
        modified_zip.extend(comment_bytes)
        
        print(f"[ZIP] Added {len(comment_bytes)} byte comment")
        return bytes(modified_zip)
    
    def _embed_in_end_marker(self, data: bytes, payload: bytes, metadata: dict) -> bytes:
        """Fallback: append data to end with clear marker (SAFE)"""
        
        # Create end marker structure
        marker = b'SAFE_STEGO_DATA'
        
        # Encode safely
        encoded_payload = base64.b64encode(payload)
        encoded_metadata = base64.b64encode(json.dumps(metadata).encode())
        
        # Structure: original_data + marker + metadata_len + metadata + payload_len + payload + marker
        metadata_len = struct.pack('<I', len(encoded_metadata))
        payload_len = struct.pack('<I', len(encoded_payload))
        
        modified_data = (data + marker + metadata_len + encoded_metadata + 
                        payload_len + encoded_payload + marker)
        
        print(f"[END] Appended {len(modified_data) - len(data)} bytes safely")
        return modified_data
    
    def _get_next_pdf_object_number(self, pdf_data: bytes) -> int:
        """Find the next available PDF object number"""
        
        # Simple heuristic: find highest existing object number
        import re
        pdf_text = pdf_data.decode('latin-1', errors='ignore')
        
        # Find all object definitions
        obj_matches = re.findall(r'(\d+) 0 obj', pdf_text)
        if obj_matches:
            max_obj = max(int(num) for num in obj_matches)
            return max_obj + 1
        else:
            return 1000  # Safe fallback
    
    def extract_file_from_document(self, stego_document_path: str, output_dir: str = None) -> str:
        """Extract hidden file from document"""
        
        print(f"[SAFE] Extracting from '{stego_document_path}'")
        
        with open(stego_document_path, 'rb') as f:
            document_data = f.read()
        
        # Try different extraction methods
        if document_data.startswith(b'%PDF'):
            payload, metadata = self._extract_from_pdf_metadata(document_data)
        elif document_data.startswith(b'{\\rtf'):
            payload, metadata = self._extract_from_rtf_metadata(document_data)
        elif document_data.startswith(b'PK'):
            payload, metadata = self._extract_from_zip_comment(document_data)
        else:
            payload, metadata = self._extract_from_end_marker(document_data)
        
        if not payload or not metadata:
            raise ValueError("No hidden data found")
        
        # Decrypt if needed
        if metadata.get('encrypted', False):
            if not self.password:
                raise ValueError("Password required for encrypted file")
            payload = self._decrypt_data(payload)
        
        # Verify integrity
        actual_checksum = hashlib.sha256(payload).hexdigest()[:16]
        expected_checksum = metadata['checksum']
        
        if actual_checksum != expected_checksum:
            print(f"⚠️ Warning: Checksum mismatch")
        
        # Save extracted file
        output_dir = output_dir or os.getcwd()
        output_filename = f"extracted_{metadata['filename']}"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'wb') as f:
            f.write(payload)
        
        print(f"[SAFE] Extracted '{metadata['filename']}' ({len(payload)} bytes)")
        print(f"[SAFE] Saved as: {output_path}")
        
        return output_path
    
    def _extract_from_pdf_metadata(self, pdf_data: bytes) -> tuple:
        """Extract from PDF using end marker"""
        
        # Use the reliable end marker extraction
        print(f"[PDF] Using safe end-marker extraction")
        return self._extract_from_end_marker(pdf_data)
    
    def _extract_from_rtf_metadata(self, rtf_data: bytes) -> tuple:
        """Extract from RTF info group"""
        
        rtf_text = rtf_data.decode('latin-1', errors='ignore')
        
        # Look for our markers
        meta_match = rtf_text.find('SAFE_META:')
        data_match = rtf_text.find('SAFE_DATA:')
        
        if meta_match == -1 or data_match == -1:
            return None, None
        
        # Extract metadata
        meta_start = meta_match + len('SAFE_META:')
        meta_end = rtf_text.find('}', meta_start)
        if meta_end == -1:
            meta_end = rtf_text.find('|', meta_start)
        
        encoded_metadata = rtf_text[meta_start:meta_end]
        
        # Extract data
        data_start = data_match + len('SAFE_DATA:')
        data_end = rtf_text.find('}', data_start)
        
        encoded_payload = rtf_text[data_start:data_end]
        
        try:
            metadata = json.loads(base64.b64decode(encoded_metadata).decode())
            payload = base64.b64decode(encoded_payload)
            return payload, metadata
        except Exception as e:
            print(f"[RTF] Extraction error: {e}")
            return None, None
    
    def _extract_from_zip_comment(self, zip_data: bytes) -> tuple:
        """Extract from ZIP comment"""
        
        # Find end of central directory record
        eocd_pos = zip_data.rfind(b'PK\x05\x06')
        if eocd_pos == -1:
            return None, None
        
        # Read comment length
        comment_len = struct.unpack('<H', zip_data[eocd_pos + 20:eocd_pos + 22])[0]
        
        if comment_len == 0:
            return None, None
        
        # Extract comment
        comment_start = eocd_pos + 22
        comment = zip_data[comment_start:comment_start + comment_len].decode('utf-8')
        
        if not comment.startswith('SAFE_META:'):
            return None, None
        
        # Parse comment
        parts = comment.split('|SAFE_DATA:')
        if len(parts) != 2:
            return None, None
        
        encoded_metadata = parts[0][len('SAFE_META:'):]
        encoded_payload = parts[1]
        
        try:
            metadata = json.loads(base64.b64decode(encoded_metadata).decode())
            payload = base64.b64decode(encoded_payload)
            return payload, metadata
        except Exception as e:
            print(f"[ZIP] Extraction error: {e}")
            return None, None
    
    def _extract_from_end_marker(self, data: bytes) -> tuple:
        """Extract from end marker"""
        
        marker = b'SAFE_STEGO_DATA'
        
        # Find last occurrence of marker
        last_marker_pos = data.rfind(marker)
        if last_marker_pos == -1:
            return None, None
        
        # Find first occurrence of marker
        first_marker_pos = data.find(marker)
        if first_marker_pos == -1 or first_marker_pos == last_marker_pos:
            return None, None
        
        # Extract structure
        pos = first_marker_pos + len(marker)
        
        # Read metadata
        metadata_len = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
        
        encoded_metadata = data[pos:pos+metadata_len]
        pos += metadata_len
        
        # Read payload
        payload_len = struct.unpack('<I', data[pos:pos+4])[0]
        pos += 4
        
        encoded_payload = data[pos:pos+payload_len]
        
        try:
            metadata = json.loads(base64.b64decode(encoded_metadata).decode())
            payload = base64.b64decode(encoded_payload)
            return payload, metadata
        except Exception as e:
            print(f"[END] Extraction error: {e}")
            return None, None
    
    def _encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-GCM"""
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(self.password.encode())
        
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        return salt + nonce + ciphertext
    
    def _decrypt_data(self, encrypted_data: bytes) -> bytes:
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
        key = kdf.derive(self.password.encode())
        
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)