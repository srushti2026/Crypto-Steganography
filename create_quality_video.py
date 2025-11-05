#!/usr/bin/env python3
"""
Create a higher quality test video with lossless codec
"""

import cv2
import numpy as np

def create_quality_test_video():
    # Create a larger, higher quality video
    width, height = 640, 480
    fps = 30
    frame_count = 50
    
    # Use lossless codec
    fourcc = cv2.VideoWriter_fourcc(*'FFV1')
    out = cv2.VideoWriter('quality_test_video.avi', fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("Failed to create video with FFV1, trying HFYU...")
        fourcc = cv2.VideoWriter_fourcc(*'HFYU')
        out = cv2.VideoWriter('quality_test_video.avi', fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("Failed to create lossless video, using MJPG...")
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('quality_test_video.avi', fourcc, fps, (width, height))
    
    if not out.isOpened():
        print("Failed to create video!")
        return False
    
    print(f"Creating {width}x{height} video with {frame_count} frames...")
    
    for i in range(frame_count):
        # Create a varied frame with different colors/patterns
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create different patterns in each frame
        pattern = i % 4
        if pattern == 0:
            # Gradient
            for y in range(height):
                for x in range(width):
                    frame[y, x] = [x % 256, y % 256, (x + y) % 256]
        elif pattern == 1:
            # Checkerboard
            for y in range(height):
                for x in range(width):
                    if (x // 20 + y // 20) % 2:
                        frame[y, x] = [200, 100, 50]
                    else:
                        frame[y, x] = [50, 150, 200]
        elif pattern == 2:
            # Circles
            center_x, center_y = width // 2, height // 2
            for y in range(height):
                for x in range(width):
                    dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    frame[y, x] = [int(dist) % 256, (int(dist) * 2) % 256, (int(dist) * 3) % 256]
        else:
            # Random-ish pattern
            for y in range(height):
                for x in range(width):
                    frame[y, x] = [(x * y + i) % 256, (x + y * i) % 256, (x * i + y) % 256]
        
        out.write(frame)
        if (i + 1) % 10 == 0:
            print(f"  Frame {i + 1}/{frame_count}")
    
    out.release()
    print("✅ Video created successfully!")
    return True

if __name__ == "__main__":
    create_quality_test_video()