# Tests Directory

This directory contains all test files, generated samples, and stego created files to keep the main application directory clean and organized.

## Directory Structure

### `/test_scripts/`
Contains all test Python scripts and debugging tools:
- `test_*.py` - Various test scripts for different functionality
- `debug_*.py` - Debugging and diagnostic scripts  
- `comprehensive_test.py` - Comprehensive testing scripts
- `create_test_video.py` - Video creation utilities for testing

### `/generated_files/`
Contains test videos and files generated during development:
- Test video files (`.mp4`, `.avi`)
- Debug logs and output files
- Sample embedded videos used for testing

### `/outputs/`
Contains all steganographic output files created by the application:
- Stego videos with embedded content
- Frame directories used for steganographic processing
- Extracted content files and forensic packages
- All generated steganographic artifacts

### `/uploads/`
Contains uploaded files used during testing:
- Carrier media files
- Test content files
- Sample files for embedding tests

### `/temp/`
Contains temporary files created during testing:
- Temporary processing files
- Sample videos and media for quick tests

## Important Notes

- **DO NOT** add core application files to this directory
- The main `backend/` directory should only contain:
  - `app.py` (main application)
  - `modules/` (core steganography modules)
  - `api/` (API endpoints)
  - Configuration files
  - Database files
  - Empty `outputs/`, `temp/`, `uploads/` directories for application use

## Running Tests

To run tests from the main backend directory, use:
```bash
python Tests/test_scripts/test_name.py
```

Or navigate to the test_scripts directory:
```bash
cd Tests/test_scripts
python test_name.py
```