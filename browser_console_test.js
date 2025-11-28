// BROWSER CONSOLE TEST
// Paste this in your browser's developer console (F12 -> Console tab)
// when you're on http://localhost:8080

console.log('🔍 Testing API from browser console...');

// Test 1: Check API health
fetch('http://localhost:8000/api/health')
  .then(response => {
    console.log('✅ Health check response:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('✅ Health data:', data);
  })
  .catch(error => {
    console.error('❌ Health check failed:', error);
  });

// Test 2: Quick extraction test (you'll need to create a stego file first)
// This is just to show you how to test - you'll need actual stego file data

const testExtraction = (stegoFileBlob, password) => {
  const formData = new FormData();
  formData.append('stego_file', stegoFileBlob, 'test.png');
  formData.append('password', password);

  console.log('🔍 Testing extraction from browser...');
  
  fetch('http://localhost:8000/api/extract', {
    method: 'POST',
    body: formData,
  })
  .then(response => {
    console.log('📥 Extract response status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('📥 Extract response data:', data);
    
    if (data.operation_id) {
      // Check status
      const checkStatus = () => {
        fetch(`http://localhost:8000/api/operations/${data.operation_id}/status`)
          .then(response => response.json())
          .then(statusData => {
            console.log('📊 Status:', statusData);
            
            if (statusData.status === 'completed') {
              console.log('🎉 Extraction completed!');
              console.log('📄 Result:', statusData.result);
            } else if (statusData.status === 'failed') {
              console.log('❌ Extraction failed:', statusData.error);
            } else {
              setTimeout(checkStatus, 1000); // Check again in 1 second
            }
          });
      };
      
      checkStatus();
    }
  })
  .catch(error => {
    console.error('❌ Extraction failed:', error);
  });
};

// Usage example (you need to provide actual stego file):
// testExtraction(yourStegoFileBlob, 'your_password');

console.log('🔧 Browser API test loaded. Use testExtraction(fileBlob, password) to test extraction.');