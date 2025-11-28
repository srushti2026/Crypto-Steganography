#!/usr/bin/env python3
"""
Compare pixel values between PNG frames and reconstructed AVI
"""

import sys
import os
import cv2
import numpy as np

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.video_steganography import VideoSteganography

def compare_png_vs_avi():
    """Compare pixel values between PNG frame and AVI video"""
    
    # Read first PNG frame
    png_frame_path = "backend/temp/frame_000000.png"
    png_frame = cv2.imread(png_frame_path)
    
    # Read first frame from AVI
    avi_path = "backend/test_output.avi"
    cap = cv2.VideoCapture(avi_path)
    ret, avi_frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Could not read AVI frame")
        return
    
    print("Comparing first frame pixel values (first 10 pixels):")
    print("Format: PNG vs AVI (channel R/G/B)")
    
    # Compare first 10 pixels
    for i in range(10):
        row = i // 10
        col = i % 10
        png_pixel = png_frame[row, col]
        avi_pixel = avi_frame[row, col]
        
        print(f"Pixel[{row}][{col}]: PNG{tuple(png_pixel)} vs AVI{tuple(avi_pixel)}")
        
        # Check if any channel differs
        if not np.array_equal(png_pixel, avi_pixel):
            print(f"  ❌ DIFFERENCE detected!")
            for ch in range(3):
                if png_pixel[ch] != avi_pixel[ch]:
                    print(f"    Channel {ch}: {png_pixel[ch]} -> {avi_pixel[ch]} (LSB: {png_pixel[ch]&1} -> {avi_pixel[ch]&1})")
        else:
            print(f"  ✅ Identical")
    
    # Check frame dimensions
    print(f"\nFrame dimensions:")
    print(f"PNG: {png_frame.shape}")
    print(f"AVI: {avi_frame.shape}")
    
    # Now test extraction from PNG directly
    print("\n" + "="*50)
    print("Testing extraction from PNG frame directly...")
    
    stego = VideoSteganography()
    
    # Temporarily modify extraction to work with single PNG
    # We'll read the PNG as if it were a video with one frame
    temp_video_path = "backend/temp/png_as_video.avi"
    
    # Create a single-frame video from the PNG
    fourcc = 0  # Uncompressed
    height, width = png_frame.shape[:2]
    out = cv2.VideoWriter(temp_video_path, fourcc, 1.0, (width, height))
    out.write(png_frame)
    out.release()
    
    # Try extraction from this single-frame video
    print(f"Extracting from single PNG frame (as video)...")
    extracted_data, data_type = stego.extract_data(temp_video_path)
    
    if extracted_data and data_type == "text":
        extracted_message = extracted_data.decode('utf-8')
        print(f"✅ Extracted from PNG: {extracted_message}")
    else:
        print("❌ No data extracted from PNG frame")
    
    # Clean up
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

if __name__ == "__main__":
    compare_png_vs_avi()