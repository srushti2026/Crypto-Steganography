# Test file upload script
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

# File path
$filePath = "C:\Users\Administrator\Documents\Git\VeilForge\task_31\backend\uploads\stego_stego_168KB_3a0e98_1764404737_f121ff79.mp4"
$fileName = [System.IO.Path]::GetFileName($filePath)

# Read file content
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$fileEnc = [System.Text.Encoding]::GetEncoding('iso-8859-1').GetString($fileBytes)

# Build form data
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
    "Content-Type: video/mp4",
    "",
    $fileEnc,
    "--$boundary",
    "Content-Disposition: form-data; name=`"extraction_type`"",
    "",
    "video",
    "--$boundary",
    "Content-Disposition: form-data; name=`"password`"",
    "",
    "",
    "--$boundary",
    "Content-Disposition: form-data; name=`"compression_level`"",
    "",
    "medium",
    "--$boundary--"
)

$body = $bodyLines -join $LF

# Send request
$headers = @{
    'Content-Type' = "multipart/form-data; boundary=$boundary"
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/extract" -Method Post -Body $body -Headers $headers
    Write-Host "Success: $($response.message)"
    Write-Host "Operation ID: $($response.operation_id)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}