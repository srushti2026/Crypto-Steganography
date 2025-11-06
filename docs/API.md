# VeilForge API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend.onrender.com`

## Authentication
Currently, authentication is optional. All endpoints can be accessed without authentication for basic functionality.

## Common Response Format

### Success Response
```json
{
  "success": true,
  "operation_id": "uuid-string",
  "message": "Operation completed successfully",
  "data": {},
  "download_url": "/api/operations/{id}/download"
}
```

### Error Response
```json
{
  "detail": "Error message description"
}
```

## Core Endpoints

### Health Check
**GET** `/api/health`

Check if the backend service is running.

**Response:**
```json
{
  "status": "Backend is working!",
  "timestamp": "2024-01-01T12:00:00"
}
```

### Supported Formats
**GET** `/api/supported-formats`

Get supported file formats for each steganography type.

**Response:**
```json
{
  "image": {
    "carrier_formats": ["png", "jpg", "jpeg", "bmp", "tiff"],
    "content_formats": ["text", "file"],
    "max_size_mb": 0
  },
  "video": {
    "carrier_formats": ["mp4", "avi", "mov", "mkv"],
    "content_formats": ["text", "file"],
    "max_size_mb": 0
  }
}
```

## Steganography Operations

### Embed Data
**POST** `/api/embed`

Embed data into a carrier file.

**Parameters:**
- `carrier_file` (file): The file to hide data in
- `content_file` (file, optional): File to hide (if not using text)
- `carrier_type` (string, optional): Type of carrier (auto-detected if not provided)
- `content_type` (string): "text" or "file"
- `text_content` (string, optional): Text to hide (if content_type is "text")
- `password` (string): Encryption password
- `encryption_type` (string, default: "aes-256-gcm"): Encryption algorithm
- `user_id` (string, optional): User identifier

**Example:**
```bash
curl -X POST "http://localhost:8000/api/embed" \
  -F "carrier_file=@image.png" \
  -F "content_type=text" \
  -F "text_content=Secret message" \
  -F "password=mypassword123"
```

### Extract Data  
**POST** `/api/extract`

Extract hidden data from a file.

**Parameters:**
- `carrier_file` (file): File containing hidden data
- `password` (string): Decryption password
- `output_format` (string, default: "auto"): Output format preference

### Forensic Embed
**POST** `/api/forensic-embed`

Advanced embedding with forensic metadata.

**Parameters:**
- `carrier_file` (file): Carrier file
- `content_file` (file): Content to hide
- `password` (string): Encryption password
- `forensic_metadata` (string): JSON metadata to embed

### Forensic Extract
**POST** `/api/forensic-extract`

Extract data with forensic analysis.

**Parameters:**
- `carrier_file` (file): File to analyze
- `password` (string): Decryption password

## Operation Management

### Check Operation Status
**GET** `/api/operations/{operation_id}/status`

Check the status of a running operation.

**Response:**
```json
{
  "status": "completed",
  "progress": 100,
  "message": "Operation finished successfully",
  "result": {}
}
```

### Download Results
**GET** `/api/operations/{operation_id}/download`

Download the result of a completed operation.

**Response:** File download

### Delete Operation
**DELETE** `/api/operations/{operation_id}`

Clean up operation data and files.

## Utilities

### Generate Password
**GET** `/api/generate-password?length=16&include_symbols=true`

Generate a secure random password.

**Response:**
```json
{
  "password": "Kx9#mP2$vQ8@nR5!",
  "length": 16,
  "strength": "strong"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid parameters |
| 404  | Not Found - Operation or file not found |
| 413  | Payload Too Large - File size exceeds limits |
| 422  | Unprocessable Entity - Validation error |
| 500  | Internal Server Error |

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended for production use.

## File Size Limits

- **Images**: Up to 100MB
- **Videos**: Up to 500MB  
- **Audio**: Up to 100MB
- **Documents**: Up to 50MB

## Security Notes

- All file uploads are temporary and cleaned up automatically
- Passwords are never stored, only used for encryption/decryption
- Use HTTPS in production
- Validate all file inputs on your client side as well