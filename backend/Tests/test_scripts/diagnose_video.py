"""
Simple diagnostic test for video properties
"""
import cv2
import os

# Find test video
test_videos = []
for root, dirs, files in os.walk("../"):
    for file in files:
        if file.lower().endswith(('.mp4', '.avi', '.mov')):
            test_videos.append(os.path.join(root, file))
            if len(test_videos) >= 1:  # Just need one
                break
    if test_videos:
        break

if test_videos:
    test_video = test_videos[0]
    print(f"Testing video: {test_video}")
    
    cap = cv2.VideoCapture(test_video)
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"FPS: {fps}")
        print(f"Width: {width}")
        print(f"Height: {height}")
        print(f"Total frames: {total_frames}")
        
        pixels_per_frame = width * height * 3
        redundancy = 3
        total_capacity = (total_frames * pixels_per_frame) // redundancy
        
        print(f"Pixels per frame: {pixels_per_frame}")
        print(f"Total capacity (bits): {total_capacity}")
        
        # Try to read first frame
        ret, frame = cap.read()
        if ret:
            print(f"First frame shape: {frame.shape}")
            print("✅ Video can be read successfully")
        else:
            print("❌ Cannot read first frame")
        
        cap.release()
    else:
        print("❌ Cannot open video")
else:
    print("❌ No test video found")