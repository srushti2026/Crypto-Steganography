/**
 * Utility functions for file downloads with proper "Save As" functionality
 */

export interface FileType {
  description: string;
  accept: Record<string, string[]>;
}

// File type mappings for proper save dialogs
export const FILE_TYPE_MAP: Record<string, FileType> = {
  // Video formats
  'mp4': { description: 'MP4 Video', accept: { 'video/mp4': ['.mp4'] } },
  'avi': { description: 'AVI Video', accept: { 'video/avi': ['.avi'] } },
  'mov': { description: 'MOV Video', accept: { 'video/quicktime': ['.mov'] } },
  'mkv': { description: 'MKV Video', accept: { 'video/x-matroska': ['.mkv'] } },
  'webm': { description: 'WebM Video', accept: { 'video/webm': ['.webm'] } },
  // Audio formats
  'wav': { description: 'WAV Audio', accept: { 'audio/wav': ['.wav'] } },
  'mp3': { description: 'MP3 Audio', accept: { 'audio/mp3': ['.mp3'] } },
  'flac': { description: 'FLAC Audio', accept: { 'audio/flac': ['.flac'] } },
  'ogg': { description: 'OGG Audio', accept: { 'audio/ogg': ['.ogg'] } },
  'aac': { description: 'AAC Audio', accept: { 'audio/aac': ['.aac'] } },
  'm4a': { description: 'M4A Audio', accept: { 'audio/mp4': ['.m4a'] } },
  // Image formats
  'jpg': { description: 'JPEG Image', accept: { 'image/jpeg': ['.jpg', '.jpeg'] } },
  'jpeg': { description: 'JPEG Image', accept: { 'image/jpeg': ['.jpg', '.jpeg'] } },
  'png': { description: 'PNG Image', accept: { 'image/png': ['.png'] } },
  'bmp': { description: 'BMP Image', accept: { 'image/bmp': ['.bmp'] } },
  'gif': { description: 'GIF Image', accept: { 'image/gif': ['.gif'] } },
  'webp': { description: 'WebP Image', accept: { 'image/webp': ['.webp'] } },
  // Document formats
  'pdf': { description: 'PDF Document', accept: { 'application/pdf': ['.pdf'] } },
  'doc': { description: 'Word Document', accept: { 'application/msword': ['.doc'] } },
  'docx': { description: 'Word Document', accept: { 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] } },
  'txt': { description: 'Text File', accept: { 'text/plain': ['.txt'] } },
  'rtf': { description: 'RTF Document', accept: { 'application/rtf': ['.rtf'] } },
  // Archive formats
  'zip': { description: 'ZIP Archive', accept: { 'application/zip': ['.zip'] } },
  'json': { description: 'JSON File', accept: { 'application/json': ['.json'] } },
  // Binary fallback
  'bin': { description: 'Binary File', accept: { 'application/octet-stream': ['.bin'] } }
};

/**
 * Get file extension from filename
 */
export function getFileExtension(filename: string): string {
  const lastDotIndex = filename.lastIndexOf('.');
  if (lastDotIndex > 0 && lastDotIndex < filename.length - 1) {
    return filename.substring(lastDotIndex + 1).toLowerCase();
  }
  return '';
}

/**
 * Clean filename for better user experience
 */
export function cleanFilename(filename: string): string {
  if (filename.includes('extracted_tmp') || filename.includes('temp_')) {
    const extension = getFileExtension(filename);
    return `extracted_file_${Date.now()}.${extension || 'txt'}`;
  }
  return filename;
}

/**
 * Get appropriate file type for save dialog
 */
export function getFileType(filename: string): FileType {
  const extension = getFileExtension(filename);
  const fileType = FILE_TYPE_MAP[extension];
  
  if (fileType) {
    return fileType;
  }
  
  // Create type for unknown extensions
  if (extension) {
    return {
      description: `${extension.toUpperCase()} File`,
      accept: { [`application/${extension}`]: [`.${extension}`] }
    };
  }
  
  // Default to all files
  return {
    description: 'All Files',
    accept: { '*/*': [] }
  };
}

// Download deduplication to prevent double downloads
const activeDownloads = new Set<string>();

/**
 * Download file with proper "Save As" functionality
 * Uses File System Access API when available, falls back to traditional download
 */
export async function downloadFileWithSaveAs(
  blob: Blob, 
  suggestedName: string,
  successMessage?: string
): Promise<void> {
  console.log('🚀 downloadFileWithSaveAs called with:', {
    blobSize: blob?.size || 'undefined',
    blobType: blob?.type || 'undefined',
    suggestedName,
    successMessage
  });
  
  if (!blob) {
    throw new Error('No blob provided for download');
  }

  // Create a unique key for this download to prevent duplicates
  const downloadKey = `${suggestedName}-${blob.size}-${Date.now()}`;
  
  if (activeDownloads.has(downloadKey)) {
    console.log('🔄 Download already in progress, skipping duplicate:', suggestedName);
    return;
  }
  
  activeDownloads.add(downloadKey);
  
  try {
  
  const cleanName = cleanFilename(suggestedName);
  const fileType = getFileType(cleanName);
  
  console.log('🔽 Starting download with Save As:', cleanName);
  console.log('📁 File type detected:', fileType);
  console.log('🌐 File System Access API available:', 'showSaveFilePicker' in window);
  console.log('🔒 Secure context:', window.isSecureContext);
  console.log('🌍 Current origin:', window.location.origin);
  

  
  // Check if it's a document file - use special handling to force Save As dialog
  const extension = getFileExtension(cleanName);
  const isDocumentFile = ['pdf', 'doc', 'docx', 'txt', 'rtf'].includes(extension);
  
  // For document files, use a method that forces the Save As dialog
  if (isDocumentFile) {
    console.log('📄 Document file detected, forcing Save As dialog');
    
    try {
      // Create a new blob with a generic MIME type to force Save As dialog
      const forcedBlob = new Blob([blob], { type: 'application/octet-stream' });
      
      // Method 1: Try to use the File System Access API if available and secure
      if ('showSaveFilePicker' in window && window.isSecureContext) {
        try {
          console.log('🎯 Trying File System Access API for document...');
          
          const fileHandle = await (window as any).showSaveFilePicker({
            suggestedName: cleanName,
            types: [fileType],
            excludeAcceptAllOption: false,
            startIn: 'downloads'
          });
          
          console.log('✅ User selected save location:', fileHandle.name);
          
          const writableStream = await fileHandle.createWritable();
          await writableStream.write(blob);
          await writableStream.close();
          
          console.log('💾 Document saved successfully via File System API');
          return;
        } catch (apiError: any) {
          if (apiError.name === 'AbortError') {
            console.log('🚫 User cancelled save operation');
            return;
          }
          console.log('⚠️ File System API failed for document, trying alternative method:', apiError.message);
        }
      }
      
      // Method 2: Use multiple approaches to force Save As dialog
      console.log('🔄 Using alternative methods to force Save As dialog');
      
      // Try method 2a: Simulate user interaction and right-click context
      try {
        const url = window.URL.createObjectURL(forcedBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = cleanName;
        
        // Make the link visible temporarily and simulate user interaction
        link.style.position = 'fixed';
        link.style.top = '-1000px';
        link.textContent = 'Download';
        
        document.body.appendChild(link);
        
        // Focus and trigger with user event simulation
        link.focus();
        
        // Create a proper user event
        const event = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window,
          button: 0,
          buttons: 1,
          clientX: 0,
          clientY: 0
        });
        
        link.dispatchEvent(event);
        
        // Clean up
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 500);
        
        console.log(`✅ Document download with enhanced user event: ${cleanName}`);
        return;
        
      } catch (methodError) {
        console.log('⚠️ Enhanced method failed, trying basic method:', methodError);
        
        // Method 2b: Basic approach with modified blob
        const url = window.URL.createObjectURL(forcedBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = cleanName;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        
        setTimeout(() => {
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        }, 100);
        
        console.log(`✅ Document download with basic method: ${cleanName}`);
        return;
      }
      
    } catch (error) {
      console.error('❌ Error in document download:', error);
      // Fall through to regular method if all else fails
    }
  }
  
  // Try File System Access API for non-document files (Chrome, Edge) - FORCE USER TO CHOOSE LOCATION
  // Skip this API for document files due to security restrictions, only works in secure contexts
  if ('showSaveFilePicker' in window && window.isSecureContext && !isDocumentFile) {
    try {
      console.log('🎯 Attempting to show save picker for non-document file...');
      
      const fileHandle = await (window as any).showSaveFilePicker({
        suggestedName: cleanName,
        types: [fileType],
        excludeAcceptAllOption: false,
        startIn: 'downloads'
      });
      
      console.log('✅ User selected save location:', fileHandle.name);
      
      const writableStream = await fileHandle.createWritable();
      await writableStream.write(blob);
      await writableStream.close();
      
      console.log('💾 File saved successfully');
      
      console.log(`✅ File ${fileHandle.name} saved successfully to chosen location`);
      return;
    } catch (error: any) {
      console.log('❌ Save picker error:', error.name, error.message);
      
      if (error.name === 'AbortError') {
        console.log('🚫 User cancelled save operation');
        return;
      }
      
      // Log error and fall through to traditional download
      console.warn('⚠️ File System Access API failed, using traditional download:', error);
    }
  }
  
  // Final fallback: Traditional download with original filename
  console.log('⬇️ Using traditional download as final fallback');
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = cleanName;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  
  // Cleanup
  setTimeout(() => {
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }, 100);
  
  console.log(`✅ File ${cleanName} downloaded to Downloads folder`);
  } finally {
    // Clean up the download key
    activeDownloads.delete(downloadKey);
  }
}

/**
 * Download file from URL with proper "Save As" functionality
 */
export async function downloadFromUrl(
  url: string, 
  suggestedName: string,
  successMessage?: string
): Promise<void> {
  try {
    console.log('🌐 Downloading from URL:', url);
    console.log('📁 Requested filename:', suggestedName);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    console.log('📦 Blob created, size:', blob.size, 'bytes, type:', blob.type);
    
    await downloadFileWithSaveAs(blob, suggestedName, successMessage);
  } catch (error: any) {
    console.error('❌ Download error:', error);
    
    let errorMessage = 'Unknown download error';
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    }
    
    console.error(`Download failed: ${errorMessage}`);
    throw error; // Re-throw to allow calling code to handle if needed
  }
}