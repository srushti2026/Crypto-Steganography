#!/usr/bin/env python3
"""
Create a simple sample video for testing
"""

import cv2
import numpy as np
import os

def create_sample_video():
    """Create a simple sample video"""
    
    output_path = "backend/temp/sample_video.mp4"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Video properties
    width, height = 640, 480
    fps = 30
    duration = 3  # seconds
    total_frames = fps * duration
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Creating sample video: {output_path}")
    print(f"Properties: {width}x{height}, {fps} FPS, {duration}s ({total_frames} frames)")
    
    # Generate frames
    for frame_num in range(total_frames):
        # Create a colorful frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some pattern
        color = int((frame_num / total_frames) * 255)
        
        # Gradient background
        for y in range(height):
            for x in range(width):
                frame[y, x] = [
                    (color + x // 3) % 256,
                    (color + y // 3) % 256,
                    (color + (x + y) // 6) % 256
                ]
        
        # Add text overlay
        text = f"Frame {frame_num + 1}/{total_frames}"
        cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add a moving circle
        center_x = int(width/2 + 150 * np.sin(2 * np.pi * frame_num / 60))
        center_y = int(height/2 + 100 * np.cos(2 * np.pi * frame_num / 60))
        cv2.circle(frame, (center_x, center_y), 30, (255, 255, 255), -1)
        
        writer.write(frame)
        
        if frame_num % 30 == 0:
            print(f"  Generated {frame_num + 1}/{total_frames} frames...")
    
    writer.release()
    
    # Verify the video
    cap = cv2.VideoCapture(output_path)
    if cap.isOpened():
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Video created successfully!")
        print(f"  Path: {output_path}")
        print(f"  Size: {os.path.getsize(output_path):,} bytes")
        print(f"  Properties: {actual_width}x{actual_height}, {actual_fps} FPS, {frame_count} frames")
        
        cap.release()
        return True
    else:
        print(f"❌ Failed to create video")
        return False

if __name__ == "__main__":
    create_sample_video()