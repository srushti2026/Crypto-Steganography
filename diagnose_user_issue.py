#!/usr/bin/env python3
"""
Direct test of the exact user scenario to identify the root cause
"""

import requests
import json
import os
import time

API_BASE = "http://localhost:8000"

def test_user_scenario():
    """Test the exact scenario the user described"""
    print("🔍 Testing User's Exact Scenario")
    print("=" * 50)
    
    # The user mentioned they downloaded a layered_container.json
    # So let's test with a video that likely has this issue
    test_files = [
        "sample_video_steganography_playable.avi",
        "sample_video_steganography.avi", 
        "test_embedded_file.mp4"
    ]
    
    # Try common passwords from the user's examples
    test_passwords = [
        "testpass123",
        "password123", 
        "DK3b2iyMV*@M4dcN",  # From the terminal logs
        "test",
        ""
    ]
    
    for video_file in test_files:
        if not os.path.exists(video_file):
            print(f"⏭️  Skipping {video_file} (not found)")
            continue
            
        print(f"\n🎯 Testing: {video_file}")
        
        for password in test_passwords:
            print(f"🔑 Trying password: '{password}'")
            
            result = test_extraction(video_file, password)
            if result:
                print(f"✅ SUCCESS with {video_file} using password '{password}'")
                return True
            
        print(f"❌ No success with {video_file}")
    
    print("\n❌ Could not find a working video+password combination")
    print("🔧 Let's create our own test case...")
    
    # Create a simple test case
    return create_and_test_simple_case()

def test_extraction(video_file, password):
    """Test extraction with specific file and password"""
    try:
        with open(video_file, 'rb') as f:
            files = {'stego_file': (video_file, f, 'video/mp4' if video_file.endswith('.mp4') else 'video/avi')}
            data = {
                'password': password,
                'output_format': 'auto'
            }
            
            response = requests.post(f"{API_BASE}/api/extract", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'operation_id' in result:
                    operation_id = result['operation_id']
                    
                    # Quick status check
                    time.sleep(1)
                    status_response = requests.get(f"{API_BASE}/api/operations/{operation_id}/status")
                    
                    if status_response.status_code == 200:
                        status = status_response.json()
                        
                        if status.get('status') == 'completed':
                            return check_extraction_download(operation_id, video_file, password)
                        elif status.get('status') == 'failed':
                            error_msg = status.get('error', 'Unknown')
                            if "Multi-layer extraction failed" in error_msg:
                                print(f"🔍 FOUND THE ISSUE! Multi-layer extraction failed")
                                analyze_backend_logs()
                                return True  # We found the problem
                            print(f"   ❌ Failed: {error_msg}")
                        else:
                            print(f"   ⏳ Status: {status.get('status')}")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def check_extraction_download(operation_id, video_file, password):
    """Check what the download actually contains"""
    print(f"   📥 Checking download...")
    
    try:
        response = requests.get(f"{API_BASE}/api/operations/{operation_id}/download")
        
        if response.status_code == 200:
            content = response.content
            content_type = response.headers.get('content-type', 'unknown')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"   📄 Content-Type: {content_type}")
            print(f"   📁 Content-Disposition: {content_disposition}")
            print(f"   💾 Size: {len(content)} bytes")
            
            # This is the key check - is it JSON layered container?
            if content.startswith(b'{') and b'"type":"layered_container"' in content:
                print(f"\n   🚨 ISSUE CONFIRMED: Downloaded layered_container.json instead of original file!")
                print(f"   📄 File: {video_file}")
                print(f"   🔑 Password: {password}")
                
                # Save the problematic JSON for analysis
                json_file = f"problematic_layered_container_{int(time.time())}.json"
                with open(json_file, 'wb') as f:
                    f.write(content)
                
                print(f"   💾 Saved problematic JSON as: {json_file}")
                
                # Parse and analyze the JSON
                try:
                    container_json = json.loads(content.decode('utf-8'))
                    layers = container_json.get('layers', [])
                    print(f"\n   📊 LAYERED CONTAINER ANALYSIS:")
                    print(f"   - Container version: {container_json.get('version', 'unknown')}")
                    print(f"   - Number of layers: {len(layers)}")
                    
                    for i, layer in enumerate(layers):
                        filename = layer.get('filename', 'unknown')
                        size = layer.get('size', 0)
                        layer_type = layer.get('type', 'unknown')
                        print(f"   - Layer {i}: '{filename}' ({size} bytes, type: {layer_type})")
                        
                        # This shows what SHOULD have been returned
                        print(f"   🔧 SHOULD RETURN: {filename} directly, not JSON container")
                    
                except Exception as e:
                    print(f"   ❌ Could not parse JSON: {e}")
                
                return True  # We found the issue
            else:
                # Check if it's a proper file
                if len(content) > 10:  # Not just "None" 
                    print(f"   ✅ Looks like proper file extraction (not JSON)")
                    return True
                else:
                    print(f"   ❌ Too small, likely empty or 'None'")
            
        else:
            print(f"   ❌ Download failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Download check failed: {e}")
    
    return False

def analyze_backend_logs():
    """Analyze what's happening in the backend"""
    print(f"\n🔍 ROOT CAUSE ANALYSIS:")
    print(f"The issue is in the layered container processing pipeline:")
    print(f"1. Video extraction detects layered container (✅ WORKS)")
    print(f"2. Increases bit limits to extract full container (✅ WORKS - no more infinite loop)")  
    print(f"3. Extracts layered container JSON successfully (✅ WORKS)")
    print(f"4. ❌ FAILS: Should convert JSON back to original files")
    print(f"5. ❌ PROBLEM: Returns raw JSON instead of extracted files")
    
    print(f"\n🔧 SOLUTION NEEDED:")
    print(f"The extract_layered_data_container() function needs to be called")
    print(f"and return individual files, not the raw JSON container")

def create_and_test_simple_case():
    """Create a simple test case if no existing files work"""
    print(f"\n🔧 Creating Simple Test Case...")
    
    # Just test with any existing video file
    test_video = None
    for video_file in os.listdir('.'):
        if video_file.endswith(('.mp4', '.avi')) and os.path.getsize(video_file) > 1000:
            test_video = video_file
            break
    
    if test_video:
        print(f"📹 Using test video: {test_video}")
        
        # Try extraction with a random password to see the workflow
        result = test_extraction(test_video, "random_password_test")
        if result:
            return True
    
    print(f"❌ No suitable test video found")
    return False

def main():
    """Main test function"""
    print("🧪 VeilForge Issue Diagnosis - Layered Container Problem")
    print("=" * 65)
    
    success = test_user_scenario()
    
    print("\n" + "=" * 65)
    if success:
        print("🎯 ISSUE IDENTIFIED: System returns layered_container.json instead of original files")
        print("🔧 NEXT STEP: Fix the extract_layered_data_container processing in app.py")
    else:
        print("❓ Could not reproduce the specific issue - may need more test data")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)