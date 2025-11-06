#!/usr/bin/env python3
"""
Audio Steganography Capacity Management Fix
Prevents file corruption by checking data capacity before embedding
"""

import os
import math
import numpy as np
import soundfile as sf
from typing import Tuple, Optional

class AudioCapacityManager:
    """Manages audio file capacity for steganography"""
    
    @staticmethod
    def calculate_audio_capacity(audio_path: str) -> Tuple[int, dict]:
        """Calculate maximum data capacity for an audio file"""
        try:
            # Read audio file to get its properties
            audio_data, sample_rate = sf.read(audio_path, dtype='int16')
            
            # If stereo, use only one channel for capacity calculation
            if len(audio_data.shape) > 1:
                num_samples = audio_data.shape[0]
                channels = audio_data.shape[1]
            else:
                num_samples = len(audio_data)
                channels = 1
            
            # LSB steganography uses 1 bit per sample
            # Account for header, footer, and encryption overhead
            header_bits = 96  # "AUDIO_STEGO:" header
            footer_bits = 112  # "END_AUDIO_STEGO" footer  
            overhead_bits = header_bits + footer_bits + 64  # Extra safety margin
            
            # Usable bits for data
            total_usable_bits = num_samples - overhead_bits
            
            # Account for encryption overhead (approximately 33% increase)
            encryption_overhead = 1.35
            
            # Account for base64 encoding overhead (33% increase)
            base64_overhead = 1.33
            
            # Account for JSON wrapper overhead
            json_overhead = 200  # bytes for JSON structure
            
            # Calculate maximum payload size in bytes
            max_encrypted_bits = total_usable_bits
            max_plain_text_chars = int(max_encrypted_bits / 8 / encryption_overhead)
            max_base64_bytes = int(max_plain_text_chars / base64_overhead)
            max_payload_bytes = max_base64_bytes - json_overhead
            
            # Safety factor
            safe_payload_bytes = int(max_payload_bytes * 0.8)  # Use only 80% of capacity
            
            audio_info = {
                'duration_seconds': num_samples / sample_rate,
                'sample_rate': sample_rate,
                'channels': channels,
                'total_samples': num_samples,
                'total_bits': num_samples,
                'overhead_bits': overhead_bits,
                'usable_bits': total_usable_bits,
                'max_payload_bytes': max_payload_bytes,
                'safe_payload_bytes': safe_payload_bytes
            }
            
            return safe_payload_bytes, audio_info
            
        except Exception as e:
            print(f"❌ Error calculating audio capacity: {e}")
            return 0, {}
    
    @staticmethod
    def check_payload_size(payload_size: int, audio_capacity: int, audio_info: dict) -> dict:
        """Check if payload fits in audio file"""
        capacity_used = (payload_size / audio_capacity) * 100 if audio_capacity > 0 else 100
        
        result = {
            'fits': payload_size <= audio_capacity,
            'payload_size': payload_size,
            'audio_capacity': audio_capacity,
            'capacity_used_percent': capacity_used,
            'audio_info': audio_info
        }
        
        if payload_size > audio_capacity:
            recommended_duration = (payload_size / audio_capacity) * audio_info.get('duration_seconds', 0)
            result['recommendation'] = f"Need audio file of at least {recommended_duration:.1f} seconds duration"
        
        return result
    
    @staticmethod
    def suggest_carrier_requirements(payload_size: int, sample_rate: int = 44100) -> dict:
        """Suggest minimum audio carrier requirements for a given payload"""
        # Reverse calculation to find required audio duration
        
        # Account for all overheads
        encryption_overhead = 1.35
        base64_overhead = 1.33
        json_overhead = 200
        safety_factor = 1.25  # 25% safety margin
        
        # Calculate required data size including overheads
        required_base64_size = (payload_size + json_overhead) * base64_overhead
        required_encrypted_size = required_base64_size * encryption_overhead
        required_bits = required_encrypted_size * 8
        
        # Add header/footer overhead
        overhead_bits = 96 + 112 + 64
        total_required_bits = (required_bits + overhead_bits) * safety_factor
        
        # Calculate required audio samples
        required_samples = int(total_required_bits)
        required_duration = required_samples / sample_rate
        
        return {
            'payload_size': payload_size,
            'required_duration_seconds': required_duration,
            'required_samples': required_samples,
            'sample_rate': sample_rate,
            'recommendation': f"Use audio file of at least {required_duration:.1f} seconds at {sample_rate} Hz"
        }


def test_capacity_manager():
    """Test the capacity management system"""
    print("🔍 Testing Audio Capacity Management")
    print("=" * 50)
    
    # Test with existing audio files
    test_files = [
        'ff-16b-2c-44100hz.wav',
        'demo_audio.wav',
        'debug_test_audio.wav'
    ]
    
    existing_files = [f for f in test_files if os.path.exists(f)]
    
    if not existing_files:
        print("No test audio files found, creating one...")
        # Create a test audio file
        test_audio = 'capacity_test.wav'
        sample_rate = 44100
        duration = 5.0  # 5 seconds
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440.0
        audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
        sf.write(test_audio, audio_data, sample_rate)
        existing_files = [test_audio]
    
    for audio_file in existing_files[:1]:  # Test with first file only
        print(f"\n📊 Analyzing: {audio_file}")
        
        capacity, info = AudioCapacityManager.calculate_audio_capacity(audio_file)
        
        print(f"  Duration: {info.get('duration_seconds', 0):.2f} seconds")
        print(f"  Sample Rate: {info.get('sample_rate', 0)} Hz")
        print(f"  Channels: {info.get('channels', 0)}")
        print(f"  Total Samples: {info.get('total_samples', 0):,}")
        print(f"  Safe Capacity: {capacity:,} bytes ({capacity/1024:.1f} KB)")
        
        # Test with different payload sizes
        test_payloads = [
            ("Small text", 100),
            ("Medium text", 1000),
            ("Small image", 10 * 1024),    # 10 KB
            ("Medium image", 50 * 1024),   # 50 KB
            ("Large image", 100 * 1024),   # 100 KB
            ("Small video", 500 * 1024),   # 500 KB
            ("Medium video", 1024 * 1024), # 1 MB
        ]
        
        print(f"\n  Capacity Analysis:")
        for name, size in test_payloads:
            check = AudioCapacityManager.check_payload_size(size, capacity, info)
            status = "✅ FITS" if check['fits'] else "❌ TOO BIG"
            print(f"    {name:15} ({size:>8,} bytes): {status} ({check['capacity_used_percent']:.1f}%)")
            
            if not check['fits'] and 'recommendation' in check:
                print(f"      💡 {check['recommendation']}")
        
        # Test existing video files
        print(f"\n  Real File Analysis:")
        video_files = ['api_test_video.mp4', 'comprehensive_test_video.mp4', 'debug_test_video.mp4']
        
        for video_file in video_files:
            if os.path.exists(video_file):
                size = os.path.getsize(video_file)
                check = AudioCapacityManager.check_payload_size(size, capacity, info)
                status = "✅ FITS" if check['fits'] else "❌ TOO BIG"
                print(f"    {video_file:25} ({size:>8,} bytes): {status} ({check['capacity_used_percent']:.1f}%)")
                
                if not check['fits']:
                    req = AudioCapacityManager.suggest_carrier_requirements(size)
                    print(f"      💡 {req['recommendation']}")
        
        break  # Only test with first audio file
    
    print(f"\n🎉 Capacity analysis complete!")

if __name__ == "__main__":
    test_capacity_manager()