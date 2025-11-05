/**
 * API Service for Steganography Operations
 * Handles all communication with the FastAPI backend
 */

// Dynamic API base URL that adapts to the current hostname
const getApiBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    // Use the same hostname as the frontend but port 8000 for the API
    return `${window.location.protocol}//${window.location.hostname}:8000/api`;
  }
  // Fallback for server-side rendering
  return 'http://localhost:8000/api';
};

const API_BASE_URL = getApiBaseUrl();

export interface User {
  email: string;
  username: string;
}

export interface EmbedRequest {
  carrier_type: string;
  content_type: string;
  text_content?: string;
  password: string;
  encryption_type?: string;
  project_name?: string;
  project_description?: string;
}

export interface ExtractRequest {
  password: string;
  output_format?: string;
}

export interface OperationResponse {
  success: boolean;
  operation_id: string;
  message: string;
  data?: any;
  download_url?: string;
}

export interface StatusResponse {
  status: string;
  progress?: number;
  message?: string;
  error?: string;
  result?: any;
}

export interface SupportedFormats {
  image: {
    carrier_formats: string[];
    content_formats: string[];
    max_size_mb: number;
  };
  video: {
    carrier_formats: string[];
    content_formats: string[];
    max_size_mb: number;
  };
  audio: {
    carrier_formats: string[];
    content_formats: string[];
    max_size_mb: number;
  };
  document: {
    carrier_formats: string[];
    content_formats: string[];
    max_size_mb: number;
  };
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Utility function to clean up backend error messages
  private cleanErrorMessage(message: string): string {
    // Filter out technical backend errors that confuse users
    if (message.includes("NoneType") || 
        message.includes("subscriptable") ||
        message.includes("steganography_operations") ||
        message.includes("PGRST205") ||
        message.includes("schema cache")) {
      return "Operation may have completed successfully but database logging failed. Please check your outputs folder for the result file.";
    }
    
    // Handle common HTTP errors more gracefully
    if (message.includes("HTTP 500")) {
      return "Server error occurred. Please try again or contact support.";
    } else if (message.includes("HTTP 422")) {
      return "Invalid request data. Please check your input.";
    } else if (message.includes("HTTP 404")) {
      return "Service not available. Please ensure the backend is running.";
    } else if (message.includes("HTTP 401")) {
      return "Authentication required.";
    } else if (message.includes("HTTP 403")) {
      return "Access denied.";
    }
    
    return message;
  }

  // Helper method for making requests
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const rawError = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      const cleanedError = this.cleanErrorMessage(rawError);
      throw new Error(cleanedError);
    }

    return response.json();
  }

  // User Management
  async registerUser(user: User): Promise<any> {
    return this.makeRequest('/users/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(user),
    });
  }

  async getUserOperations(userId: string, limit: number = 50): Promise<any> {
    return this.makeRequest(`/users/${userId}/operations?limit=${limit}`);
  }

  async getUserStats(userId: string): Promise<any> {
    return this.makeRequest(`/users/${userId}/stats`);
  }

  // Project Management
  async createProject(project: {
    name: string;
    description?: string;
    project_type?: string;
  }): Promise<any> {
    return this.makeRequest('/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project),
    });
  }

  // Steganography Operations
  async getSupportedFormats(): Promise<SupportedFormats> {
    return this.makeRequest('/supported-formats');
  }

  async generatePassword(length: number = 16, includeSymbols: boolean = true): Promise<{
    password: string;
    length: number;
    strength: string;
  }> {
    return this.makeRequest(`/generate-password?length=${length}&include_symbols=${includeSymbols}`);
  }

  async embedData(
    carrierFile: File,
    request: EmbedRequest,
    contentFile?: File,
    userId?: string,
    onProgress?: (progress: number) => void
  ): Promise<OperationResponse> {
    const formData = new FormData();
    formData.append('carrier_file', carrierFile);
    formData.append('carrier_type', request.carrier_type);
    formData.append('content_type', request.content_type);
    formData.append('password', request.password);
    
    if (request.text_content) {
      formData.append('text_content', request.text_content);
    }
    
    if (contentFile) {
      formData.append('content_file', contentFile);
    }
    
    if (request.encryption_type) {
      formData.append('encryption_type', request.encryption_type);
    }
    
    if (request.project_name) {
      formData.append('project_name', request.project_name);
    }
    
    if (userId) {
      formData.append('user_id', userId);
    }

    const response = await fetch(`${this.baseUrl}/embed`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const rawError = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      const cleanedError = this.cleanErrorMessage(rawError);
      throw new Error(cleanedError);
    }

    const result = await response.json();
    
    // Start polling for progress if callback provided
    if (onProgress && result.operation_id) {
      this.pollOperationStatus(result.operation_id, onProgress);
    }
    
    return result;
  }

  async extractData(
    stegoFile: File,
    request: ExtractRequest,
    userId?: string,
    onProgress?: (progress: number) => void
  ): Promise<OperationResponse> {
    const formData = new FormData();
    formData.append('stego_file', stegoFile);
    formData.append('password', request.password);
    formData.append('output_format', request.output_format || 'auto');
    
    if (userId) {
      formData.append('user_id', userId);
    }

    const response = await fetch(`${this.baseUrl}/extract`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const rawError = errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
      const cleanedError = this.cleanErrorMessage(rawError);
      throw new Error(cleanedError);
    }

    const result = await response.json();
    
    // Start polling for progress if callback provided
    if (onProgress && result.operation_id) {
      this.pollOperationStatus(result.operation_id, onProgress);
    }
    
    return result;
  }

  // Operation Status and Management
  async getOperationStatus(operationId: string): Promise<StatusResponse> {
    return this.makeRequest(`/operations/${operationId}/status`);
  }

  async downloadResult(operationId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/operations/${operationId}/download`);
    
    if (!response.ok) {
      const errorMessage = `Failed to download result: ${response.statusText}`;
      const cleanedError = this.cleanErrorMessage(errorMessage);
      throw new Error(cleanedError);
    }
    
    return response.blob();
  }

  async deleteOperation(operationId: string): Promise<any> {
    return this.makeRequest(`/operations/${operationId}`, {
      method: 'DELETE',
    });
  }

  async listOperations(limit: number = 100): Promise<any> {
    return this.makeRequest(`/operations?limit=${limit}`);
  }

  // Progress Polling
  private async pollOperationStatus(
    operationId: string,
    onProgress: (progress: number) => void,
    interval: number = 1000
  ): Promise<void> {
    const poll = async () => {
      try {
        const status = await this.getOperationStatus(operationId);
        
        if (status.progress !== undefined) {
          onProgress(status.progress);
        }
        
        if (status.status === 'completed' || status.status === 'failed') {
          return; // Stop polling
        }
        
        // Continue polling
        setTimeout(poll, interval);
      } catch (error) {
        console.error('Error polling operation status:', error);
      }
    };
    
    poll();
  }

  // Health Check
  async healthCheck(): Promise<any> {
    return this.makeRequest('/health');
  }

  // Utility Methods
  getDownloadUrl(operationId: string): string {
    return `${this.baseUrl}/operations/${operationId}/download`;
  }

  validateFile(file: File, carrierType: string, supportedFormats: SupportedFormats): {
    valid: boolean;
    error?: string;
  } {
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    if (!fileExtension) {
      return { valid: false, error: 'File has no extension' };
    }

    const formats = supportedFormats[carrierType as keyof SupportedFormats];
    if (!formats) {
      return { valid: false, error: 'Unsupported carrier type' };
    }

    if (!formats.carrier_formats.includes(fileExtension)) {
      return {
        valid: false,
        error: `Unsupported format. Supported: ${formats.carrier_formats.join(', ')}`
      };
    }

    // Check file size limit (0 means no limit)
    if (formats.max_size_mb > 0) {
      const maxSizeBytes = formats.max_size_mb * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        return {
          valid: false,
          error: `File too large. Maximum size: ${formats.max_size_mb}MB`
        };
      }
    }

    return { valid: true };
  }

  formatFileSize(bytes: number): string {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export class for custom instances
export default ApiService;