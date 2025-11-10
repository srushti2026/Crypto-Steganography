import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
import { ProjectFileService } from "@/services/projectFileService";
import { ProjectFilesDisplay } from "@/pages/Dashboard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  FileImage, 
  Download, 
  Key,
  FileText,
  Image as ImageIcon,
  File,
  CheckCircle,
  Shield,
  Eye,
  EyeOff,
  Copy,
  Save,
  Zap,
  Music,
  Video,
  RefreshCw
} from "lucide-react";

// API Service Integration
const getApiUrl = () => {
  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    return 'https://veilforge.onrender.com';
  }
  try {
    return import.meta?.env?.VITE_API_URL || 'https://veilforge.onrender.com';
  } catch {
    return 'https://veilforge.onrender.com';
  }
};
const API_BASE_URL = getApiUrl();

interface SupportedFormats {
  image: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  video: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  audio: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
  document: { carrier_formats: string[]; content_formats: string[]; max_size_mb: number; };
}

// Enhanced toast with better UX - fixed stacking issue
let toastCount = 0;
const activeToasts: HTMLElement[] = [];

const toast = {
  success: (message: string) => {
    console.log('✅ SUCCESS:', message);
    createToast(message, 'bg-green-500', 3000);
  },
  error: (message: string) => {
    console.error('❌ ERROR:', message);
    createToast(message, 'bg-blue-500', 5000);
  }
};

function createToast(message: string, bgColor: string, duration: number) {
  const notification = document.createElement('div');
  const topOffset = 16 + (activeToasts.length * 80); // 16px base + 80px per existing toast
  
  notification.className = `fixed right-4 ${bgColor} text-white p-3 rounded-lg shadow-lg z-50 transition-all duration-300 ease-in-out`;
  notification.style.top = `${topOffset}px`;
  notification.textContent = message;
  
  // Add to active toasts
  activeToasts.push(notification);
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.style.opacity = '1';
    notification.style.transform = 'translateX(0)';
  }, 10);
  
  // Remove after duration
  setTimeout(() => {
    const index = activeToasts.indexOf(notification);
    if (index > -1) {
      activeToasts.splice(index, 1);
      
      // Animate out
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
        
        // Reposition remaining toasts
        activeToasts.forEach((toast, i) => {
          const newTopOffset = 16 + (i * 80);
          toast.style.top = `${newTopOffset}px`;
        });
      }, 300);
    }
  }, duration);
  
  // Initial state for animation
  notification.style.opacity = '0';
  notification.style.transform = 'translateX(100%)';
}

export default function General() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [carrierFiles, setCarrierFiles] = useState<File[]>([]); // Multiple carrier files
  const [batchMode, setBatchMode] = useState(false); // Toggle between single and batch mode
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [contentType, setContentType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [fileContent, setFileContent] = useState<File | null>(null);
  


  
  const [password, setPassword] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressCompleted, setProgressCompleted] = useState(false);
  const [operationResult, setOperationResult] = useState<any>(null);
  const [progressInterval, setProgressInterval] = useState<NodeJS.Timeout | null>(null);
  const [currentOperationId, setCurrentOperationId] = useState<string | null>(null);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null);
  const [carrierType, setCarrierType] = useState("image");
  const [encryptionType, setEncryptionType] = useState("aes-256-gcm");
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [apiHealth, setApiHealth] = useState<any>(null);
  
  // Project Settings State
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [saveProject, setSaveProject] = useState(false);
  const [projectTags, setProjectTags] = useState("");
  const [savedProjects, setSavedProjects] = useState<any[]>([]);
  
  // Password Management State
  const [showPassword, setShowPassword] = useState(false);
  const [savePasswordWithProject, setSavePasswordWithProject] = useState(false);
  const [savedPassword, setSavedPassword] = useState("");
  
  // Size Estimate State
  const [estimateFile, setEstimateFile] = useState<File | null>(null);
  const [estimateType, setEstimateType] = useState<"carrier" | "content">("carrier");
  const [estimateResult, setEstimateResult] = useState<any>(null);
  const [estimateLoading, setEstimateLoading] = useState(false);

  // File refresh trigger
  const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);

  // Safe progress setter that prevents backwards movement after completion
  const setSafeProgress = (value: number | ((prev: number) => number)) => {
    if (progressCompleted) return; // Don't update progress if already completed
    
    if (typeof value === 'function') {
      setProgress(prev => {
        const newValue = value(prev);
        if (newValue >= 100) {
          setProgressCompleted(true);
        }
        return Math.max(prev, newValue); // Never go backwards
      });
    } else {
      if (value >= 100) {
        setProgressCompleted(true);
      }
      setProgress(prev => Math.max(prev, value)); // Never go backwards
    }
  };

  // Reset progress state for new operations
  const resetProgress = () => {
    setProgress(0);
    setProgressCompleted(false);
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    
    const initializeComponent = async () => {
      try {
        // Check authentication
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          console.log("⚠️  No user authenticated, but allowing access for testing");
          // Temporarily allow access without authentication for testing
          // navigate("/auth");
          // return;
        }
        setCurrentUser(user);

        // Load API health and supported formats
        await loadApiData();
        
        // Handle newly created project from dashboard
        if (location.state?.newProject && location.state?.projectJustCreated) {
          console.log('📦 New project received from dashboard:', location.state.newProject);
          setSelectedProject(location.state.newProject);
          setProjectName(location.state.newProject.name);
          setProjectDescription(location.state.newProject.description || "");
          setSavedProjects([location.state.newProject]);
          toast.success(`Welcome to your new ${location.state.newProject.project_type} project!`);
        }
        
        // Handle existing project being opened from dashboard
        if (location.state?.existingProject && location.state?.projectToOpen) {
          console.log('🔓 Opening existing project:', location.state.existingProject);
          const project = location.state.existingProject;
          
          setSelectedProject(project);
          setProjectName(project.name);
          
          // Parse description to extract metadata
          let description = "";
          let metadata = {};
          
          try {
            if (project.description) {
              const parsed = JSON.parse(project.description);
              if (parsed.description !== undefined) {
                description = parsed.description || "";
                metadata = parsed.metadata || {};
              } else {
                // Legacy format - just a string
                description = project.description;
              }
            }
          } catch (e) {
            // Legacy format - just a string
            description = project.description || "";
          }
          
          setProjectDescription(description);
          
          // Restore all project metadata if available
          if (metadata && typeof metadata === 'object') {
            console.log('📋 Restoring project metadata:', metadata);
            const meta = metadata as any;
            
            // General project settings
            if (meta.tags) setProjectTags(meta.tags);
            
            // Operation settings
            if (meta.carrierType) setCarrierType(meta.carrierType);
            if (meta.encryptionType) setEncryptionType(meta.encryptionType);
            if (meta.contentType) setContentType(meta.contentType);
            if (meta.textContent) setTextContent(meta.textContent);
            
            // Security settings
            if (meta.password && meta.savePasswordWithProject) {
              setPassword(meta.password);
              setSavedPassword(meta.password);
              setSavePasswordWithProject(true);
            }
            
            // UI preferences
            if (meta.showPassword !== undefined) setShowPassword(meta.showPassword);
            if (meta.batchMode !== undefined) setBatchMode(meta.batchMode);
            
            // Operation result
            if (meta.lastOperationResult) setOperationResult(meta.lastOperationResult);
          }
          
          toast.success(`Opened project: ${project.name} with saved settings`);
        }
        
        // Load user projects
        if (user) {
          await loadUserProjects(user.id);
        }
      } catch (error) {
        console.error("Initialization error:", error);
        toast.error("Failed to initialize application");
      }
    };

    initializeComponent();
  }, [navigate]);

  const loadApiData = async () => {
    try {
      console.log('🔍 Loading API data from:', API_BASE_URL);
      
      // Check API health
      console.log('📡 Testing API health...');
      const healthResponse = await fetch(`${API_BASE_URL}/health`);
      console.log('Health response status:', healthResponse.status);
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setApiHealth(healthData);
        console.log('✅ API Health loaded:', healthData);
      } else {
        console.log('❌ Health check failed with status:', healthResponse.status);
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }

      // Load supported formats
      console.log('📡 Loading supported formats...');
      const formatsResponse = await fetch(`${API_BASE_URL}/supported-formats`);
      console.log('Formats response status:', formatsResponse.status);
      
      if (formatsResponse.ok) {
        const formatsData = await formatsResponse.json();
        setSupportedFormats(formatsData);
        console.log('✅ Supported Formats loaded:', formatsData);
      } else {
        console.log('⚠️ Formats loading failed with status:', formatsResponse.status);
        // Don't throw error for formats - it's not critical
      }

      console.log('🎉 API data loading completed successfully');
      
    } catch (error) {
      console.error("❌ Failed to load API data:", error);
      console.error("Error details:", {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      toast.error("Backend API not available. Some features may not work.");
    }
  };

  const loadUserProjects = async (userId: string) => {
    try {
      console.log('🔍 Loading projects for user:', userId);
      
      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) {
        console.error('❌ Supabase projects query error:', error);
        throw error;
      }

      console.log('📊 Projects loaded:', data);
      setSavedProjects(data || []);
      
      // Auto-select the first project if available, or create one if none exists
      // But don't override if a project was just created or opened from dashboard
      if (data && data.length > 0 && !selectedProject && !location.state?.projectJustCreated && !location.state?.projectToOpen) {
        console.log('✅ Selected existing project:', data[0]);
        setSelectedProject(data[0]);
        setProjectName(data[0].name);
        setProjectDescription(data[0].description || "");
      } else if ((!data || data.length === 0) && !selectedProject) {
        console.log('🆕 No projects found, creating default project...');
        // Auto-create a default project if none exists
        await createDefaultProject(userId);
      }
    } catch (error) {
      console.error('💥 Error loading projects:', error);
    }
  };

  const createDefaultProject = async (userId: string) => {
    try {
      console.log('🚀 Creating default project for user:', userId);
      
      const { data, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: userId,
            name: 'Default Project',
            description: 'Automatically created project for steganography operations',
            project_type: 'general'
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('❌ Supabase project creation error:', error);
        throw error;
      }

      console.log('✅ Project created successfully:', data);
      setSavedProjects([data]);
      setSelectedProject(data);
      toast.success('Default project created successfully!');
      
      return data;
    } catch (error) {
      console.error('💥 Error creating default project:', error);
      toast.error(`Failed to create default project: ${error.message}`);
    }
  };

  const handleCarrierFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setCarrierFile(file);
      
      // Auto-detect carrier type based on file extension
      const extension = file.name.split('.').pop()?.toLowerCase();
      let detectedType = carrierType; // default to current type
      
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          detectedType = "image";
          setCarrierType("image");
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(extension)) {
          detectedType = "video";
          setCarrierType("video");
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(extension)) {
          detectedType = "audio";
          setCarrierType("audio");
        } else if (['pdf', 'docx', 'txt', 'rtf'].includes(extension)) {
          detectedType = "document";
          setCarrierType("document");
        }
      }
      
      // Validate file with detected type after a short delay to allow state update
      setTimeout(() => {
        if (supportedFormats) {
          validateFile(file, detectedType);
        }
      }, 100);
    }
  };

  const handleCarrierFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      setCarrierFiles(files);
      
      // Auto-detect carrier type from first file
      const firstFile = files[0];
      const extension = firstFile.name.split('.').pop()?.toLowerCase();
      let detectedType = carrierType;
      
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          detectedType = "image";
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv'].includes(extension)) {
          detectedType = "video";
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac'].includes(extension)) {
          detectedType = "audio";
        } else if (['pdf', 'doc', 'docx', 'txt'].includes(extension)) {
          detectedType = "document";
        }
        
        if (detectedType !== carrierType) {
          setCarrierType(detectedType);
        }
      }
      
      // Validate all files
      setTimeout(() => {
        if (supportedFormats) {
          files.forEach((file, index) => {
            try {
              validateFile(file, detectedType);
            } catch (error) {
              toast.error(`File ${index + 1} (${file.name}): ${error}`);
            }
          });
        }
      }, 100);
    }
  };

  const removeCarrierFile = (index: number) => {
    const newFiles = carrierFiles.filter((_, i) => i !== index);
    setCarrierFiles(newFiles);
  };

  const handleExtractFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setExtractFile(file);
      
      // Auto-detect file type for extraction
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (extension) {
        if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(extension)) {
          setCarrierType("image");
        } else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(extension)) {
          setCarrierType("video");
        } else if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(extension)) {
          setCarrierType("audio");
        } else if (['pdf', 'docx', 'txt', 'rtf'].includes(extension)) {
          setCarrierType("document");
        }
      }
    }
  };

  const handleContentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileContent(e.target.files[0]);
    }
  };

  const generatePassword = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-password?length=16&include_symbols=true`);
      if (response.ok) {
        const data = await response.json();
        setPassword(data.password);
        toast.success(`Generated ${data.strength} password (${data.length} characters)`);
      } else {
        throw new Error('Failed to generate password');
      }
    } catch (error) {
      console.error('Password generation error:', error);
      // Fallback to local generation
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
      let result = '';
      for (let i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      setPassword(result);
      toast.success('Generated strong password (local fallback)');
    }
  };

  const simulateProgress = () => {
    resetProgress();
    let currentProgress = 0;
    
    const interval = setInterval(() => {
      currentProgress += Math.random() * 15 + 5; // Progress by 5-20% each step
      if (currentProgress >= 95) {
        currentProgress = 95; // Cap at 95% until real completion
        clearInterval(interval);
      }
      setSafeProgress(Math.min(currentProgress, 95));
    }, 500); // Update every 500ms for smooth animation
    
    setProgressInterval(interval);
  };

  const stopProgressSimulation = () => {
    if (progressInterval) {
      clearInterval(progressInterval);
      setProgressInterval(null);
    }
  };

  // Password Management Functions
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const copyPasswordToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(password);
      toast.success("Password copied to clipboard!");
    } catch (error) {
      console.error("Failed to copy password:", error);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = password;
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      try {
        document.execCommand('copy');
        toast.success("Password copied to clipboard!");
      } catch (fallbackError) {
        toast.error("Failed to copy password");
      }
      document.body.removeChild(textArea);
    }
  };

  const savePasswordWithProjectSettings = () => {
    if (savePasswordWithProject && password.trim()) {
      setSavedPassword(password);
      toast.success("Password saved with project settings!");
    } else if (!savePasswordWithProject) {
      setSavedPassword("");
      toast.success("Password removed from project settings!");
    }
  };

  const loadSavedPassword = () => {
    if (savedPassword) {
      setPassword(savedPassword);
      toast.success("Loaded saved password from project!");
    } else {
      toast.error("No saved password found in project settings");
    }
  };

  const saveProjectSettings = async () => {
    if (!selectedProject || !projectName.trim()) {
      toast.error("Please select a project and enter a project name");
      return;
    }

    try {
      // Create comprehensive metadata object for general steganography project
      const projectMetadata = {
        // General project settings
        tags: projectTags,
        
        // Operation settings
        carrierType: carrierType,
        encryptionType: encryptionType,
        contentType: contentType,
        textContent: contentType === 'text' ? textContent : '',
        
        // Security settings
        password: savePasswordWithProject ? password : '',
        savePasswordWithProject: savePasswordWithProject,
        
        // UI preferences
        showPassword: showPassword,
        batchMode: batchMode,
        
        // Last operation details
        lastOperationResult: operationResult,
        
        // Timestamp
        lastSaved: new Date().toISOString()
      };

      const { data, error } = await supabase
        .from('projects')
        .update({
          name: projectName.trim(),
          description: JSON.stringify({
            description: projectDescription.trim() || null,
            metadata: projectMetadata
          }),
          updated_at: new Date().toISOString()
        })
        .eq('id', selectedProject.id)
        .select()
        .single();

      if (error) throw error;

      // Update the selected project state
      setSelectedProject(data);
      
      // Update the projects list
      setSavedProjects(prevProjects => 
        prevProjects.map(p => p.id === selectedProject.id ? data : p)
      );

      toast.success("Project settings saved successfully!");
      console.log('✅ Project settings updated with metadata:', data);
    } catch (error) {
      console.error('❌ Error saving project settings:', error);
      toast.error(`Failed to save project settings: ${error.message}`);
    }
  };

  const validateFile = (file: File, type: string) => {
    if (!supportedFormats) return true;

    const extension = file.name.split('.').pop()?.toLowerCase();
    const formats = supportedFormats[type as keyof SupportedFormats];
    
    if (!formats) {
      toast.error(`Unsupported file type: ${type}`);
      return false;
    }

    if (!formats.carrier_formats.includes(extension || '')) {
      toast.error(`Unsupported format. Supported: ${formats.carrier_formats.join(', ')}`);
      return false;
    }

    // Check file size limit (0 means no limit)
    if (formats.max_size_mb > 0) {
      const maxSizeBytes = formats.max_size_mb * 1024 * 1024;
      if (file.size > maxSizeBytes) {
        toast.error(`File too large. Maximum size: ${formats.max_size_mb}MB`);
        return false;
      }
    }

    return true;
  };

  const formatFileSize = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleEmbed = async () => {
    // Validation for batch vs single mode
    if (batchMode) {
      if (!carrierFiles || carrierFiles.length === 0) {
        toast.error("Please select at least one carrier file for batch processing");
        return;
      }
    } else {
      if (!carrierFile) {
        toast.error("Please select a carrier file");
        return;
      }
    }

    if (contentType === "text" && !textContent.trim()) {
      toast.error("Please enter text content to hide");
      return;
    }



    if ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) {
      toast.error(`Please select a ${contentType} to hide`);
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }

    // Validate file format(s)
    if (batchMode) {
      for (let i = 0; i < carrierFiles.length; i++) {
        if (!validateFile(carrierFiles[i], carrierType)) {
          toast.error(`Validation failed for file ${i + 1}: ${carrierFiles[i].name}`);
          return;
        }
      }
    } else {
      if (!validateFile(carrierFile, carrierType)) {
        return;
      }
    }

    setIsProcessing(true);
    resetProgress();
    setOperationResult(null);
    setCurrentOperationId(null);
    
    // Start progress simulation for smooth animation
    simulateProgress();
    
    try {
      const formData = new FormData();
      
      if (batchMode) {
        // Add all carrier files for batch processing
        carrierFiles.forEach((file, index) => {
          formData.append('carrier_files', file);
        });
      } else {
        // Single file processing
        formData.append('carrier_file', carrierFile);
        formData.append('carrier_type', carrierType);
      }
      
      formData.append('content_type', contentType);
      formData.append('password', password);
      formData.append('encryption_type', encryptionType);

      // Add project information if provided
      if (projectName.trim()) {
        formData.append('project_name', projectName.trim());
      }
      if (projectDescription.trim()) {
        formData.append('project_description', projectDescription.trim());
      }

      if (contentType === "text") {
        formData.append('text_content', textContent);
      } else if (contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") {
        formData.append('content_file', fileContent);
        // Set content_type to "file" for all file types for backend compatibility
        formData.set('content_type', 'file');
      }

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const endpoint = batchMode ? `${API_BASE_URL}/embed-batch` : `${API_BASE_URL}/embed`;
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setCurrentOperationId(result.operation_id);
      
      // Store uploaded files in project if user is authenticated and project is selected
      if (currentUser && selectedProject) {
        try {
          console.log('💾 Storing files for project:', selectedProject.id);
          
          if (batchMode) {
            // Store all carrier files for batch processing
            for (const file of carrierFiles) {
              const storedFile = await ProjectFileService.storeUploadedFile(
                selectedProject.id,
                file,
                currentUser.id
              );
              console.log('✅ Stored carrier file:', storedFile);
            }
          } else {
            // Store single carrier file
            const storedFile = await ProjectFileService.storeUploadedFile(
              selectedProject.id,
              carrierFile!,
              currentUser.id
            );
            console.log('✅ Stored carrier file:', storedFile);
          }
          
          // Store content file if it exists
          if (fileContent) {
            const storedContentFile = await ProjectFileService.storeUploadedFile(
              selectedProject.id,
              fileContent,
              currentUser.id
            );
            console.log('✅ Stored content file:', storedContentFile);
          }
          
          // Create operation record
          const operation = await ProjectFileService.createOperation(
            selectedProject.id,
            currentUser.id,
            batchMode ? "batch_embed" : "embed",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            contentType,
            encryptionType !== "none",
            true, // assume success initially
            undefined
          );
          console.log('✅ Created operation:', operation);
          
        } catch (error) {
          console.error('💥 Error storing files:', error);
          // Don't fail the operation if file storage fails
        }
      } else {
        console.warn('⚠️ Cannot store files - missing user or project:', {
          currentUser: !!currentUser,
          selectedProject: !!selectedProject
        });
      }
      
      toast.success("Embedding operation started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Embedding operation failed";
      
      // Filter out technical backend errors that confuse users
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check your outputs folder for the result file.";
      }
      
      // Handle HTTP errors more gracefully
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file format or missing required information.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
      console.error("Embed error:", error);
    }
  };

  const handleExtract = async () => {
    // Validation
    if (!extractFile) {
      toast.error("Please select a file to extract from");
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter the password");
      return;
    }

    setIsProcessing(true);
    resetProgress();
    setOperationResult(null);
    setCurrentOperationId(null);
    
    // Start progress simulation for smooth animation
    simulateProgress();
    
    try {
      // Prepare form data
      const formData = new FormData();
      formData.append('stego_file', extractFile);
      formData.append('password', password);
      formData.append('output_format', 'auto');

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const response = await fetch(`${API_BASE_URL}/extract`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setCurrentOperationId(result.operation_id);
      
      // Store uploaded file in project if user is authenticated and project is selected
      if (currentUser && selectedProject) {
        try {
          // Store the stego file being extracted from
          await ProjectFileService.storeUploadedFile(
            selectedProject.id,
            extractFile,
            currentUser.id
          );
          
          // Create operation record
          await ProjectFileService.createOperation(
            selectedProject.id,
            currentUser.id,
            "extract",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            "unknown", // payload type is unknown until extraction
            false, // extraction doesn't typically involve encryption
            true, // assume success initially
            undefined
          );
        } catch (error) {
          console.error('Error storing extraction files:', error);
          // Don't fail the operation if file storage fails
        }
      }
      
      toast.success("Extraction operation started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Extraction operation failed";
      
      // Filter out technical backend errors that confuse users
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check the extraction results.";
      }
      
      // Handle HTTP errors more gracefully
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file or incorrect password.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
      console.error("Extract error:", error);
    }
  };

  const pollOperationStatus = async (operationId: string) => {
    const maxAttempts = 300; // 5 minutes at 1-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/operations/${operationId}/status`);
        if (!response.ok) throw new Error('Failed to check status');
        
        const status = await response.json();
        
        if (status.progress !== undefined) {
          // Stop simulation and use real progress, but never go backwards
          stopProgressSimulation();
          setSafeProgress(status.progress);
        }

        if (status.status === "completed") {
          // Stop simulation and ensure 100% progress before completing
          stopProgressSimulation();
          setSafeProgress(100);
          
          // Store processed result if user is authenticated and project is selected
          if (currentUser && selectedProject && status.result) {
            try {
              // Create a processed file record
              const processedFileName = status.result.output_file || "processed_file";
              const processedFileUrl = status.result.download_url || "";
              
              await ProjectFileService.storeProcessedFile(
                selectedProject.id,
                processedFileName,
                "processed_steganography_result",
                processedFileUrl,
                status.result.file_size || 0,
                currentUser.id,
                operationId,
                encryptionType
              );
            } catch (error) {
              console.error('Error storing processed file:', error);
              // Don't fail the operation if file storage fails
            }
          }
          
          // Wait a moment for the progress bar to reach 100%
          setTimeout(() => {
            setIsProcessing(false);
            setOperationResult(status.result);
            // Trigger file list refresh
            setFileRefreshTrigger(prev => prev + 1);
            toast.success("Operation completed successfully!");
          }, 500);
          return;
        }

        if (status.status === "failed") {
          stopProgressSimulation();
          setIsProcessing(false);
          // Clean up backend error messages for better UX
          let errorMessage = status.error || "Operation failed";
          
          // Filter out technical backend errors that confuse users
          if (errorMessage.includes("NoneType") || 
              errorMessage.includes("subscriptable") ||
              errorMessage.includes("steganography_operations") ||
              errorMessage.includes("PGRST205")) {
            errorMessage = "Operation completed but logging failed. Your files were processed successfully.";
          }
          
          toast.error(errorMessage);
          return;
        }

        attempts++;
        if (attempts < maxAttempts && (status.status === "processing" || status.status === "starting")) {
          setTimeout(poll, 1000);
        } else {
          stopProgressSimulation();
          setIsProcessing(false);
          if (attempts >= maxAttempts) {
            toast.error("Operation timed out");
          }
        }
      } catch (error) {
        stopProgressSimulation();
        setIsProcessing(false);
        toast.error("Failed to check operation status");
        console.error("Status poll error:", error);
      }
    };

    poll();
  };

  // Enhanced download with proper save as functionality
  const downloadResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      // Check if this is a batch operation
      const isBatchOperation = operationResult?.batch_operation || false;
      const downloadEndpoint = isBatchOperation 
        ? `${API_BASE_URL}/operations/${currentOperationId}/download-batch`
        : `${API_BASE_URL}/operations/${currentOperationId}/download`;
      
      // For batch operations, suggest a ZIP filename
      const defaultFilename = isBatchOperation 
        ? `batch_results_${Date.now()}.zip`
        : (operationResult?.filename || `result_${Date.now()}.bin`);
      
      // Use the utility function for proper save as functionality
      const { downloadFromUrl } = await import('@/utils/fileDownload');
      await downloadFromUrl(
        downloadEndpoint, 
        defaultFilename,
        `File saved successfully as "{filename}"!`
      );
    } catch (error: any) {
      console.error("Download error:", error);
      toast.error(`Download failed: ${error.message}`);
    }
  };

  // Size Estimation Functions
  const handleEstimateFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setEstimateFile(file);
      setEstimateResult(null);
    }
  };

  const calculateSizeEstimate = async () => {
    if (!estimateFile) {
      toast.error("Please select a file first");
      return;
    }

    setEstimateLoading(true);
    setEstimateResult(null);

    try {
      const fileSizeBytes = estimateFile.size;
      const fileSizeKB = fileSizeBytes / 1024;
      const fileSizeMB = fileSizeKB / 1024;

      if (estimateType === "carrier") {
        // Calculate how much data can be embedded in this carrier file
        const fileExt = estimateFile.name.split('.').pop()?.toLowerCase() || '';
        let capacityBytes = 0;
        let estimatedCapacity = "";

        // Audio capacity calculation (based on our audio capacity manager)
        if (['wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a'].includes(fileExt)) {
          // Approximate: 1 bit per sample for LSB steganography
          // For audio files, estimate based on duration and sample rate
          const estimatedSamples = fileSizeBytes * 0.5; // Rough estimate
          capacityBytes = Math.floor(estimatedSamples * 0.8 / 8); // 80% safety factor
          estimatedCapacity = "audio steganography";
        }
        // Image capacity calculation
        else if (['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'].includes(fileExt)) {
          // Rough estimate: 1 bit per pixel for LSB
          const estimatedPixels = fileSizeBytes * 0.1; // Very rough estimate
          capacityBytes = Math.floor(estimatedPixels / 8);
          estimatedCapacity = "image steganography";
        }
        // Video capacity calculation
        else if (['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'].includes(fileExt)) {
          // Video has higher capacity
          capacityBytes = Math.floor(fileSizeBytes * 0.01); // 1% of video size
          estimatedCapacity = "video steganography";
        }
        // Document capacity calculation
        else if (['pdf', 'docx', 'txt', 'rtf'].includes(fileExt)) {
          // Document steganography has variable capacity
          capacityBytes = Math.floor(fileSizeBytes * 0.1); // 10% of document size
          estimatedCapacity = "document steganography";
        }

        setEstimateResult({
          type: "carrier",
          fileSize: fileSizeBytes,
          fileSizeFormatted: fileSizeBytes > 1024 * 1024 ? `${fileSizeMB.toFixed(2)} MB` : `${fileSizeKB.toFixed(2)} KB`,
          capacity: capacityBytes,
          capacityFormatted: capacityBytes > 1024 ? `${(capacityBytes / 1024).toFixed(2)} KB` : `${capacityBytes} bytes`,
          method: estimatedCapacity,
          recommendations: [
            `This ${fileExt.toUpperCase()} file can hide approximately ${capacityBytes > 1024 ? `${(capacityBytes / 1024).toFixed(2)} KB` : `${capacityBytes} bytes`} of data`,
            capacityBytes > 10000 ? "✅ Good capacity for most files" : capacityBytes > 1000 ? "⚠️ Moderate capacity - suitable for small files" : "❌ Limited capacity - only text messages recommended"
          ]
        });
      } else {
        // Calculate what size carrier file is needed for this content
        const overhead = fileSizeBytes * 1.5; // Account for encryption and encoding overhead
        const recommendedCarrierSize = overhead * 10; // 10x for safety margin

        const audioCarrierDuration = Math.ceil(overhead / 3000); // ~3KB per second for audio
        const imageCarrierPixels = overhead * 8; // 8 bits per pixel
        const videoCarrierSize = overhead * 100; // Video can hide more efficiently

        setEstimateResult({
          type: "content",
          fileSize: fileSizeBytes,
          fileSizeFormatted: fileSizeBytes > 1024 * 1024 ? `${fileSizeMB.toFixed(2)} MB` : `${fileSizeKB.toFixed(2)} KB`,
          recommendations: [
            `For audio carriers: Use ${audioCarrierDuration}+ second audio files`,
            `For image carriers: Use images with ${Math.ceil(Math.sqrt(imageCarrierPixels))}x${Math.ceil(Math.sqrt(imageCarrierPixels))}+ pixels`,
            `For video carriers: Use ${((videoCarrierSize / 1024 / 1024)).toFixed(1)}+ MB video files`,
            fileSizeBytes > 100000 ? "💡 Large file - consider using video carriers for best results" : "💡 Small file - any carrier type should work"
          ]
        });
      }
    } catch (error) {
      console.error("Size estimation error:", error);
      toast.error("Failed to calculate size estimate");
    } finally {
      setEstimateLoading(false);
    }
  };

  const getContentIcon = () => {
    switch (contentType) {
      case "text": return <FileText className="h-4 w-4" />;

      case "image": return <ImageIcon className="h-4 w-4" />;
      case "audio": return <Music className="h-4 w-4" />;
      case "video": return <Video className="h-4 w-4" />;
      case "file": return <File className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };



  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20">
        {/* Header Section */}
        <section className="py-8 bg-gradient-to-r from-primary/5 to-secondary/10">
          <div className="container">
            <div className="animate-fade-in">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mr-4">
                    <FileImage className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h1 className="text-3xl md:text-4xl font-bold">General Protection</h1>
                    <p className="text-muted-foreground">
                      Advanced steganography for everyday data protection needs
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-4">
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Shield className="h-3 w-3" />
                  Secure Encryption
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Eye className="h-3 w-3" />
                  Invisible Embedding
                </Badge>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <Zap className="h-3 w-3" />
                  Fast Processing
                </Badge>
              </div>
            </div>
          </div>
        </section>

        <section className="py-8">
          <div className="container">
            <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="embed">Embed Data</TabsTrigger>
                <TabsTrigger value="extract">Extract Data</TabsTrigger>
                <TabsTrigger value="project-settings">Project Settings</TabsTrigger>
                <TabsTrigger value="size-estimate">Size Estimate</TabsTrigger>
              </TabsList>
              
              <TabsContent value="embed" className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Input Section */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Upload className="h-5 w-5" />
                        Embed Configuration
                      </CardTitle>
                      <CardDescription>
                        Configure your carrier file and hidden content for secure embedding
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Batch Mode Toggle */}
                      <div className="space-y-2">
                        <Label>Processing Mode</Label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="batch-mode"
                            checked={batchMode}
                            onChange={(e) => setBatchMode(e.target.checked)}
                            className="rounded"
                          />
                          <label htmlFor="batch-mode" className="text-sm font-medium cursor-pointer">
                            Batch Mode (Multiple Carrier Files)
                          </label>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {batchMode 
                            ? "Hide the same content in multiple carrier files"
                            : "Hide content in a single carrier file"
                          }
                        </p>
                      </div>
                      {/* Carrier File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="carrier-file">
                          {batchMode ? "Carrier Files (Multiple)" : "Carrier File"}
                        </Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          {!batchMode ? (
                            // Single file upload
                            <>
                              <input
                                id="carrier-file"
                                type="file"
                                accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                                onChange={handleCarrierFileChange}
                                className="hidden"
                              />
                              <label htmlFor="carrier-file" className="cursor-pointer">
                                <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">
                                  {carrierFile ? carrierFile.name : "Click to upload carrier file"}
                                </p>
                              </label>
                            </>
                          ) : (
                            // Multiple files upload
                            <>
                              <input
                                id="carrier-files"
                                type="file"
                                accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                                multiple
                                onChange={handleCarrierFilesChange}
                                className="hidden"
                              />
                              <label htmlFor="carrier-files" className="cursor-pointer">
                                <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                                <p className="text-sm text-muted-foreground">
                                  {carrierFiles.length > 0 
                                    ? `${carrierFiles.length} files selected` 
                                    : "Click to upload multiple carrier files"}
                                </p>
                              </label>
                            </>
                          )}
                        </div>
                        
                        {/* Display selected files for batch mode */}
                        {batchMode && carrierFiles.length > 0 && (
                          <div className="space-y-2 max-h-40 overflow-y-auto animate-fade-in">
                            <Label className="text-xs flex items-center gap-2">
                              Selected Files:
                              <Badge variant="secondary" className="text-xs">
                                {carrierFiles.length} files
                              </Badge>
                            </Label>
                            {carrierFiles.map((file, index) => (
                              <div 
                                key={index} 
                                className="flex items-center justify-between bg-gradient-to-r from-muted to-muted/50 p-3 rounded-lg border border-primary/10 hover:border-primary/20 transition-colors animate-slide-up"
                                style={{ animationDelay: `${index * 0.1}s` }}
                              >
                                <div className="flex items-center gap-3 flex-1">
                                  {/* File type icon */}
                                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                    {file.type.startsWith('image/') ? (
                                      <ImageIcon className="h-4 w-4 text-primary" />
                                    ) : file.type.startsWith('video/') ? (
                                      <Video className="h-4 w-4 text-blue-600" />
                                    ) : file.type.startsWith('audio/') ? (
                                      <Music className="h-4 w-4 text-green-600" />
                                    ) : (
                                      <FileText className="h-4 w-4 text-gray-600" />
                                    )}
                                  </div>
                                  
                                  <div className="flex-1 min-w-0">
                                    <span className="text-sm font-medium truncate block">{file.name}</span>
                                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                      <span>{(file.size / 1024).toFixed(1)} KB</span>
                                      <span>•</span>
                                      <span className="capitalize">{file.type.split('/')[0]}</span>
                                    </div>
                                  </div>
                                </div>
                                
                                <button
                                  onClick={() => removeCarrierFile(index)}
                                  className="ml-2 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 w-6 h-6 rounded-full flex items-center justify-center transition-colors"
                                  title="Remove file"
                                >
                                  ×
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Auto-detected Carrier Type Display */}
                      {carrierFile && (
                        <div className="space-y-2">
                          <Label>Detected Carrier Type</Label>
                          <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
                            {carrierType === "image" && <ImageIcon className="h-4 w-4" />}
                            {carrierType === "video" && <Video className="h-4 w-4" />}
                            {carrierType === "audio" && <Music className="h-4 w-4" />}
                            {carrierType === "document" && <FileText className="h-4 w-4" />}
                            <span className="capitalize font-medium">{carrierType}</span>
                            <span className="text-sm text-muted-foreground ml-auto">
                              Auto-detected from file extension
                            </span>
                          </div>
                        </div>
                      )}
                      {/* Content Type Selection */}
                      <div className="space-y-2">
                        <Label>Content Type to Hide</Label>
                        <Select value={contentType} onValueChange={setContentType}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Text Message
                              </div>
                            </SelectItem>
                            <SelectItem value="file">
                              <div className="flex items-center gap-2">
                                <File className="h-4 w-4" />
                                Any File
                              </div>
                            </SelectItem>
                            <SelectItem value="image">
                              <div className="flex items-center gap-2">
                                <ImageIcon className="h-4 w-4" />
                                Image File
                              </div>
                            </SelectItem>
                            <SelectItem value="video">
                              <div className="flex items-center gap-2">
                                <Video className="h-4 w-4" />
                                Video File
                              </div>
                            </SelectItem>
                            <SelectItem value="audio">
                              <div className="flex items-center gap-2">
                                <Music className="h-4 w-4" />
                                Audio File
                              </div>
                            </SelectItem>
                            <SelectItem value="document">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                Document File
                              </div>
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      {/* Content Input */}
                      {contentType === "text" && (
                        <div className="space-y-2">
                          <Label htmlFor="text-content">Secret Message</Label>
                          <Textarea
                            id="text-content"
                            value={textContent}
                            onChange={(e) => setTextContent(e.target.value)}
                            placeholder="Enter your secret message here..."
                            rows={4}
                          />
                        </div>
                      )}



                      {(contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && (
                        <div className="space-y-2">
                          <Label htmlFor="content-file">
                            {contentType === "file" ? "File to Hide" :
                             contentType === "image" ? "Image to Hide" :
                             contentType === "video" ? "Video to Hide" :
                             contentType === "audio" ? "Audio to Hide" :
                             "Document to Hide"}
                          </Label>
                          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-primary/50 transition-colors">
                            <input
                              id="content-file"
                              type="file"
                              accept={
                                contentType === "image" ? "image/*" :
                                contentType === "video" ? "video/*" :
                                contentType === "audio" ? "audio/*" :
                                contentType === "document" ? ".pdf,.docx,.txt,.doc" :
                                "*/*"
                              }
                              onChange={handleContentFileChange}
                              className="hidden"
                            />
                            <label htmlFor="content-file" className="cursor-pointer">
                              {getContentIcon()}
                              <p className="text-sm text-muted-foreground mt-2">
                                {fileContent ? fileContent.name : `Click to upload ${contentType}`}
                              </p>
                            </label>
                          </div>
                        </div>
                      )}

                      {/* Password */}
                      <div className="space-y-3">
                        <Label htmlFor="password">Encryption Password</Label>
                        
                        {/* Password Input Row */}
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Input
                              id="password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter strong password"
                              className="pr-10"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={togglePasswordVisibility}
                              className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={generatePassword}
                            className="shrink-0"
                            title="Generate Password"
                          >
                            <Key className="h-4 w-4" />
                          </Button>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="shrink-0"
                            disabled={!password.trim()}
                            title="Copy Password"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        
                        {/* Password Management Options */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="save-password-with-project"
                              checked={savePasswordWithProject}
                              onChange={(e) => {
                                setSavePasswordWithProject(e.target.checked);
                                if (e.target.checked && password.trim()) {
                                  setSavedPassword(password);
                                  toast.success("Password will be saved with project!");
                                } else if (!e.target.checked) {
                                  setSavedPassword("");
                                }
                              }}
                              className="rounded"
                            />
                            <Label htmlFor="save-password-with-project" className="text-sm">
                              Save password with project settings
                            </Label>
                          </div>
                          
                          {savedPassword && (
                            <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
                              <Shield className="h-4 w-4 text-green-600" />
                              <span className="text-sm text-muted-foreground">Password saved with project</span>
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={loadSavedPassword}
                                className="ml-auto h-6 px-2 text-xs"
                              >
                                Load
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>

                      <Button 
                        onClick={handleEmbed} 
                        className="w-full"
                        disabled={(batchMode ? (carrierFiles.length === 0) : !carrierFile) || 
                          (contentType === "text" && !textContent.trim()) ||
                          ((contentType === "file" || contentType === "image" || contentType === "video" || contentType === "audio" || contentType === "document") && !fileContent) ||
                          isProcessing}
                      >
                        {isProcessing 
                          ? (batchMode ? `Processing ${carrierFiles.length} files...` : "Processing...")
                          : (batchMode ? `Embed in ${carrierFiles.length} Files` : "Embed Data")
                        }
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Preview/Progress Section */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Preview & Progress
                      </CardTitle>
                      <CardDescription>
                        Monitor your embedding process and preview results
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Batch mode preview */}
                      {batchMode && carrierFiles.length > 0 && (
                        <div className="space-y-2 animate-fade-in">
                          <Label>Batch Preview ({carrierFiles.length} files)</Label>
                          <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto p-2 border rounded-lg bg-muted/30">
                            {carrierFiles.slice(0, 4).map((file, index) => (
                              <div 
                                key={index}
                                className="aspect-square rounded-md overflow-hidden bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center border border-primary/20 animate-fade-in"
                                style={{ animationDelay: `${index * 0.1}s` }}
                              >
                                {file.type.startsWith('image/') ? (
                                  <img 
                                    src={URL.createObjectURL(file)} 
                                    alt={`Preview ${index + 1}`}
                                    className="w-full h-full object-cover"
                                    onLoad={(e) => {
                                      if (e.currentTarget && e.currentTarget.src) {
                                        setTimeout(() => URL.revokeObjectURL(e.currentTarget.src), 1000);
                                      }
                                    }}
                                  />
                                ) : file.type.startsWith('video/') ? (
                                  <Video className="h-8 w-8 text-blue-600" />
                                ) : file.type.startsWith('audio/') ? (
                                  <Music className="h-8 w-8 text-green-600" />
                                ) : (
                                  <FileText className="h-8 w-8 text-gray-600" />
                                )}
                              </div>
                            ))}
                            {carrierFiles.length > 4 && (
                              <div className="aspect-square rounded-md bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 flex items-center justify-center border border-gray-300 dark:border-gray-600">
                                <span className="text-sm font-medium">+{carrierFiles.length - 4}</span>
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-muted-foreground bg-primary/5 p-2 rounded">
                            Total size: {(carrierFiles.reduce((sum, file) => sum + file.size, 0) / 1024).toFixed(1)} KB
                          </div>
                        </div>
                      )}

                      {/* Single file preview area - Always visible */}
                      {!batchMode && (
                        <div className="space-y-2 animate-fade-in">
                          <Label>Carrier File Preview</Label>
                          <div className="aspect-video rounded-lg overflow-hidden bg-muted border-2 border-dashed border-primary/20 relative group min-h-[200px]">
                            {/* Animated background gradient */}
                            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 animate-pulse"></div>
                            
                            {/* Preview content based on file type - Enhanced for all formats */}
                            {carrierFile ? (
                              carrierFile.type.startsWith('image/') ? (
                              <div className="w-full h-full relative">
                                <img 
                                  src={URL.createObjectURL(carrierFile)} 
                                  alt="Carrier preview"
                                  className="w-full h-full object-cover animate-fade-in transition-transform duration-300 group-hover:scale-105"
                                  onLoad={(e) => {
                                    // Clean up object URL after loading with null safety
                                    if (e.currentTarget && e.currentTarget.src) {
                                      setTimeout(() => URL.revokeObjectURL(e.currentTarget.src), 1000);
                                    }
                                  }}
                                />
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300 flex items-center justify-center">
                                  <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-white/90 dark:bg-black/90 rounded-full p-3">
                                    <FileImage className="h-6 w-6 text-primary" />
                                  </div>
                                </div>
                              </div>
                            ) : carrierFile.type.startsWith('video/') ? (
                              <div className="w-full h-full relative flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20">
                                <div className="text-center animate-bounce">
                                  <Video className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                                  <p className="text-sm font-medium text-blue-700 dark:text-blue-300">Video File</p>
                                </div>
                                <div className="absolute top-2 right-2 bg-blue-600 text-white text-xs px-2 py-1 rounded animate-fade-in">
                                  MP4
                                </div>
                              </div>
                            ) : carrierFile.type.startsWith('audio/') ? (
                              <div className="w-full h-full relative flex items-center justify-center bg-gradient-to-br from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20">
                                <div className="text-center">
                                  <Music className="h-12 w-12 text-green-600 mx-auto mb-2 animate-pulse" />
                                  <p className="text-sm font-medium text-green-700 dark:text-green-300">Audio File</p>
                                  {/* Animated audio waves */}
                                  <div className="flex items-center justify-center mt-3 gap-1">
                                    {[1, 2, 3, 4, 5].map((i) => (
                                      <div 
                                        key={i}
                                        className={`bg-green-500 animate-bounce w-1 rounded-full ${
                                          i === 1 ? 'h-2' : i === 2 ? 'h-4' : i === 3 ? 'h-6' : i === 4 ? 'h-4' : 'h-2'
                                        }`}
                                        style={{ animationDelay: `${i * 0.1}s` }}
                                      ></div>
                                    ))}
                                  </div>
                                </div>
                                <div className="absolute top-2 right-2 bg-green-600 text-white text-xs px-2 py-1 rounded animate-fade-in">
                                  {carrierFile.name.split('.').pop()?.toUpperCase()}
                                </div>
                              </div>
                            ) : (
                              // Document or other file types
                              <div className="w-full h-full relative flex items-center justify-center bg-gradient-to-br from-gray-50 to-slate-50 dark:from-gray-900/20 dark:to-slate-900/20">
                                <div className="text-center animate-fade-in">
                                  {carrierFile.name.toLowerCase().endsWith('.pdf') ? (
                                    <div>
                                      <FileText className="h-12 w-12 text-red-600 mx-auto mb-2" />
                                      <p className="text-sm font-medium text-red-700 dark:text-red-300">PDF Document</p>
                                    </div>
                                  ) : carrierFile.name.toLowerCase().match(/\.(doc|docx)$/) ? (
                                    <div>
                                      <FileText className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                                      <p className="text-sm font-medium text-blue-700 dark:text-blue-300">Word Document</p>
                                    </div>
                                  ) : carrierFile.name.toLowerCase().endsWith('.txt') ? (
                                    <div>
                                      <FileText className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Text File</p>
                                    </div>
                                  ) : (
                                    <div>
                                      <FileText className="h-12 w-12 text-gray-600 mx-auto mb-2" />
                                      <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                        {carrierFile.type.includes('/') ? 
                                          carrierFile.type.split('/')[1].toUpperCase() + ' File' : 
                                          'Document File'
                                        }
                                      </p>
                                    </div>
                                  )}
                                </div>
                                <div className="absolute top-2 right-2 bg-gray-600 text-white text-xs px-2 py-1 rounded animate-fade-in">
                                  {carrierFile.name.split('.').pop()?.toUpperCase()}
                                </div>
                              </div>
                              )
                            ) : (
                              // No file selected - show placeholder
                              <div className="w-full h-full relative flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900/20 dark:to-gray-800/20">
                                <div className="text-center animate-fade-in opacity-60">
                                  <FileImage className="h-16 w-16 text-gray-400 mx-auto mb-3" />
                                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">No File Selected</p>
                                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">Upload a carrier file to see preview</p>
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {/* File info with animation - Only show when file is selected */}
                          {carrierFile && (
                            <div className="animate-slide-up bg-gradient-to-r from-primary/5 to-secondary/5 p-3 rounded-lg border border-primary/10">
                              <div className="flex items-center justify-between">
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate" title={carrierFile.name}>
                                    {carrierFile.name}
                                  </p>
                                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <span>{(carrierFile.size / 1024).toFixed(1)} KB</span>
                                    <span>•</span>
                                    <span className="capitalize">{carrierFile.type.split('/')[0]}</span>
                                  </div>
                                </div>
                                <div className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-green-600 font-medium">Ready</span>
                                </div>
                              </div>
                              
                              {/* Capacity indicator */}
                              <div className="mt-2 pt-2 border-t border-primary/10">
                                <div className="flex items-center justify-between text-xs">
                                  <span className="text-muted-foreground">Estimated Capacity:</span>
                                  <span className="font-medium text-primary">
                                    {carrierFile.type.startsWith('image/') ? 
                                      `~${Math.floor(carrierFile.size * 0.1 / 1024)} KB` :
                                      carrierFile.type.startsWith('audio/') ?
                                      `~${Math.floor(carrierFile.size * 0.05 / 1024)} KB` :
                                      carrierFile.type.startsWith('video/') ?
                                      `~${Math.floor(carrierFile.size * 0.01 / 1024)} KB` :
                                      'Variable'
                                    }
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {isProcessing && (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Label className="text-sm font-medium">Processing Progress</Label>
                            <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
                          </div>
                          <Progress value={progress} className="w-full h-3" />
                          <p className="text-xs text-muted-foreground text-center">
                            Embedding data... Please wait while we securely hide your content.
                          </p>
                        </div>
                      )}

                      {operationResult && !isProcessing && (
                        <div className="space-y-4">
                          <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                              Operation completed successfully! 
                              {operationResult.processing_time && 
                                ` Processed in ${operationResult.processing_time.toFixed(2)} seconds.`
                              }
                            </AlertDescription>
                          </Alert>
                          
                          <div className="space-y-2">
                            <Label>Operation Results</Label>
                            <div className="p-3 bg-muted rounded-lg space-y-2">
                              {operationResult.filename && (
                                <p className="text-sm"><strong>Output File:</strong> {operationResult.filename}</p>
                              )}
                              {operationResult.file_size && (
                                <p className="text-sm"><strong>File Size:</strong> {formatFileSize(operationResult.file_size)}</p>
                              )}
                              {operationResult.content_type && (
                                <p className="text-sm"><strong>Content Type:</strong> {operationResult.content_type}</p>
                              )}
                            </div>
                          </div>
                          
                          <Button 
                            onClick={downloadResult} 
                            className="w-full"
                            disabled={!currentOperationId}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Save Result As...
                          </Button>
                          <p className="text-xs text-muted-foreground text-center mt-2">
                            Choose your preferred filename and save location
                          </p>
                        </div>
                      )}

                      {/* Project History */}
                      {projectName && (
                        <div className="space-y-2 pt-4 border-t">
                          <Label>Current Project</Label>
                          <div className="p-3 bg-muted rounded-lg space-y-1">
                            <p className="text-sm font-medium">{projectName}</p>
                            {projectDescription && (
                              <p className="text-xs text-muted-foreground">{projectDescription}</p>
                            )}
                            {projectTags && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {projectTags.split(',').map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {tag.trim()}
                                  </Badge>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="extract" className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Extract Configuration */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Download className="h-5 w-5" />
                        Extract Configuration
                      </CardTitle>
                      <CardDescription>
                        Upload steganographic file and extract hidden content
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="extract-file">Steganographic File</Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <input
                            id="extract-file"
                            type="file"
                            accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                            onChange={handleExtractFileChange}
                            className="hidden"
                          />
                          <label htmlFor="extract-file" className="cursor-pointer">
                            <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground">
                              {extractFile ? extractFile.name : "Click to upload file with hidden data"}
                            </p>
                          </label>
                        </div>
                      </div>

                      {/* Password */}
                      <div className="space-y-3">
                        <Label htmlFor="extract-password">Decryption Password</Label>
                        
                        {/* Password Input Row */}
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Input
                              id="extract-password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter password to decrypt"
                              className="pr-10"
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={togglePasswordVisibility}
                              className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                          </div>
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="shrink-0"
                            disabled={!password.trim()}
                            title="Copy Password"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                        </div>
                        
                        {/* Load Saved Password Option */}
                        {savedPassword && (
                          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
                            <Shield className="h-4 w-4 text-green-600" />
                            <span className="text-sm text-muted-foreground">Use saved project password</span>
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              onClick={loadSavedPassword}
                              className="ml-auto h-6 px-2 text-xs"
                            >
                              Load
                            </Button>
                          </div>
                        )}
                      </div>

                      <Button 
                        onClick={handleExtract} 
                        className="w-full"
                        disabled={!extractFile || !password || isProcessing}
                      >
                        {isProcessing ? "Processing..." : "Extract Data"}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Extract Results */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Extraction Results
                      </CardTitle>
                      <CardDescription>
                        View extracted content and save to your chosen location
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {isProcessing && (
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <Label className="text-sm font-medium">Extraction Progress</Label>
                            <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
                          </div>
                          <Progress value={progress} className="w-full h-3" />
                          <p className="text-xs text-muted-foreground text-center">
                            Extracting hidden data... Recovering your secure content.
                          </p>
                        </div>
                      )}

                      {operationResult && !isProcessing && (
                        <div className="space-y-4">
                          <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                              Extraction completed successfully!
                              {operationResult.processing_time && 
                                ` Processed in ${operationResult.processing_time.toFixed(2)} seconds.`
                              }
                            </AlertDescription>
                          </Alert>
                          
                          <div className="space-y-2">
                            <Label>Extracted Content</Label>
                            <div className="p-3 bg-muted rounded-lg space-y-2">
                              {operationResult.extracted_filename && (
                                <p className="text-sm"><strong>Extracted File:</strong> {operationResult.extracted_filename}</p>
                              )}
                              {operationResult.content_type && (
                                <p className="text-sm"><strong>Content Type:</strong> {operationResult.content_type}</p>
                              )}
                              {operationResult.file_size && (
                                <p className="text-sm"><strong>File Size:</strong> {formatFileSize(operationResult.file_size)}</p>
                              )}
                              
                              {/* Multi-layer extraction details */}
                              {operationResult.is_multi_layer && (
                                <div className="space-y-2">
                                  <p className="text-sm"><strong>Multi-Layer Extraction:</strong> {operationResult.total_layers_extracted} layers found</p>
                                  {operationResult.layer_details && operationResult.layer_details.length > 0 && (
                                    <div className="space-y-1">
                                      <p className="text-sm font-medium">Layer Details:</p>
                                      <div className="space-y-1">
                                        {operationResult.layer_details.map((layer: any, index: number) => (
                                          <div key={index} className="text-xs bg-background rounded p-2">
                                            <strong>Layer {layer.layer_number}:</strong> {layer.filename} 
                                            ({formatFileSize(layer.size)})
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Text content display */}
                              {(operationResult.text_content || operationResult.preview) && (
                                <div className="space-y-1">
                                  <p className="text-sm font-medium">
                                    {operationResult.is_multi_layer ? "Combined Layer Content:" : "Text Content:"}
                                  </p>
                                  <div className="p-2 bg-background rounded border max-h-32 overflow-y-auto">
                                    <pre className="text-xs font-mono whitespace-pre-wrap">
                                      {operationResult.text_content || operationResult.preview}
                                    </pre>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <Button 
                            onClick={downloadResult} 
                            className="w-full"
                            disabled={!currentOperationId}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            {operationResult.is_multi_layer 
                              ? `Download ZIP (${operationResult.total_layers_extracted} layers)`
                              : "Save Extracted Data As..."
                            }
                          </Button>
                          <p className="text-xs text-muted-foreground text-center mt-2">
                            {operationResult.is_multi_layer
                              ? "ZIP file contains all extracted layers as separate files"
                              : "Choose your preferred filename and save location"
                            }
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              {/* Project Settings Tab */}
              <TabsContent value="project-settings" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <File className="h-5 w-5" />
                      Project Settings
                    </CardTitle>
                    <CardDescription>
                      Configure project information and manage your steganography projects
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {/* Project Information */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Project Information</h3>
                        
                        {/* Current Project Display */}
                        {selectedProject && (
                          <div className="space-y-2">
                            <Label>Current Project</Label>
                            <div className="p-3 border rounded-lg bg-muted/50">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium">{selectedProject.name}</p>
                                  <p className="text-sm text-muted-foreground">
                                    Type: {selectedProject.project_type} • ID: {selectedProject.id}
                                  </p>
                                </div>
                                <Badge variant="secondary">{selectedProject.project_type}</Badge>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-name-tab">Project Name</Label>
                          <Input
                            id="project-name-tab"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="e.g., Secret Mission Files"
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-description-tab">Project Description</Label>
                          <Textarea
                            id="project-description-tab"
                            value={projectDescription}
                            onChange={(e) => setProjectDescription(e.target.value)}
                            placeholder="Brief description of this steganography project..."
                            rows={3}
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="project-tags-tab">Tags (comma-separated)</Label>
                          <Input
                            id="project-tags-tab"
                            value={projectTags}
                            onChange={(e) => setProjectTags(e.target.value)}
                            placeholder="secret, mission, confidential"
                          />
                        </div>
                        
                        {/* Password Management Section */}
                        <div className="space-y-4 p-4 border rounded-lg bg-muted/30">
                          <h4 className="text-sm font-semibold flex items-center gap-2">
                            <Shield className="h-4 w-4" />
                            Password Management
                          </h4>
                          
                          <div className="space-y-3">
                            <div className="space-y-2">
                              <Label htmlFor="project-password">Project Password</Label>
                              <div className="flex gap-2">
                                <div className="relative flex-1">
                                  <Input
                                    id="project-password"
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="Enter or generate password"
                                    className="pr-10"
                                  />
                                  <Button
                                    type="button"
                                    variant="ghost"
                                    size="sm"
                                    onClick={togglePasswordVisibility}
                                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-muted"
                                  >
                                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                                  </Button>
                                </div>
                                <Button
                                  type="button"
                                  variant="outline"
                                  onClick={generatePassword}
                                  className="shrink-0"
                                  title="Generate Password"
                                >
                                  <Key className="h-4 w-4" />
                                </Button>
                                <Button
                                  type="button"
                                  variant="outline"
                                  onClick={copyPasswordToClipboard}
                                  className="shrink-0"
                                  disabled={!password.trim()}
                                  title="Copy Password"
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                id="save-password-project-tab"
                                checked={savePasswordWithProject}
                                onChange={(e) => {
                                  setSavePasswordWithProject(e.target.checked);
                                  savePasswordWithProjectSettings();
                                }}
                                className="rounded"
                              />
                              <Label htmlFor="save-password-project-tab" className="text-sm">
                                Save password with this project
                              </Label>
                            </div>
                            
                            {savedPassword && (
                              <div className="p-2 bg-green-50 border border-green-200 rounded-lg">
                                <div className="flex items-center gap-2">
                                  <CheckCircle className="h-4 w-4 text-green-600" />
                                  <span className="text-sm text-green-700">
                                    Password saved with project ({savedPassword.length} characters)
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="save-project"
                            checked={saveProject}
                            onChange={(e) => setSaveProject(e.target.checked)}
                            className="rounded"
                          />
                          <Label htmlFor="save-project">Save project for future use</Label>
                        </div>
                      </div>
                      
                      {/* Project Preview */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Project Preview</h3>
                        
                        {projectName ? (
                          <div className="p-4 bg-muted rounded-lg space-y-3">
                            <div className="flex items-center gap-2">
                              <File className="h-4 w-4" />
                              <span className="font-medium">{projectName}</span>
                            </div>
                            
                            {projectDescription && (
                              <p className="text-sm text-muted-foreground">
                                {projectDescription}
                              </p>
                            )}
                            
                            {projectTags && (
                              <div className="flex flex-wrap gap-1">
                                {projectTags.split(',').map((tag, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {tag.trim()}
                                  </Badge>
                                ))}
                              </div>
                            )}
                            
                            {/* Password Status */}
                            {savedPassword && (
                              <div className="flex items-center gap-2 p-2 bg-green-50 border border-green-200 rounded">
                                <Shield className="h-4 w-4 text-green-600" />
                                <span className="text-xs text-green-700">
                                  Password saved ({savedPassword.length} chars)
                                </span>
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="sm"
                                  onClick={copyPasswordToClipboard}
                                  className="ml-auto h-6 w-6 p-0"
                                  title="Copy Password"
                                >
                                  <Copy className="h-3 w-3" />
                                </Button>
                              </div>
                            )}
                            
                            <div className="text-xs text-muted-foreground">
                              Created: {new Date().toLocaleDateString()}
                            </div>
                          </div>
                        ) : (
                          <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                            <File className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p>Enter project information to see preview</p>
                          </div>
                        )}
                        
                        {/* Project Files */}
                        {selectedProject && (
                          <div className="space-y-3">
                            <h4 className="text-sm font-semibold flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Project Files
                            </h4>
                            <ProjectFilesDisplay project={selectedProject} refreshTrigger={fileRefreshTrigger} />
                          </div>
                        )}
                        
                        {/* Project Actions */}
                        <div className="space-y-2">
                          <Button 
                            className="w-full" 
                            disabled={!projectName.trim() || !selectedProject}
                            onClick={saveProjectSettings}
                          >
                            Save Project Settings
                          </Button>
                          
                          <Button 
                            variant="outline" 
                            className="w-full"
                            onClick={() => {
                              setProjectName("");
                              setProjectDescription("");
                              setProjectTags("");
                              setSaveProject(false);
                              setSavePasswordWithProject(false);
                              setSavedPassword("");
                              setPassword("");
                              toast.success("Project settings and password cleared!");
                            }}
                          >
                            Clear Settings
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              {/* Size Estimate Tab */}
              <TabsContent value="size-estimate" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <RefreshCw className="h-5 w-5" />
                      Size Estimate Calculator
                    </CardTitle>
                    <CardDescription>
                      Calculate file capacity requirements and size recommendations
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      {/* Input Section */}
                      <div className="space-y-6">
                        <div className="space-y-4">
                          <Label>Estimation Type</Label>
                          <Select value={estimateType} onValueChange={(value: "carrier" | "content") => setEstimateType(value)}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="carrier">
                                <div className="flex items-center gap-2">
                                  <FileImage className="h-4 w-4" />
                                  Carrier File Capacity
                                </div>
                              </SelectItem>
                              <SelectItem value="content">
                                <div className="flex items-center gap-2">
                                  <File className="h-4 w-4" />
                                  Content File Requirements
                                </div>
                              </SelectItem>
                            </SelectContent>
                          </Select>
                          <p className="text-sm text-muted-foreground">
                            {estimateType === "carrier" 
                              ? "Upload a carrier file to see how much data it can hide"
                              : "Upload a content file to see what carrier size is needed"
                            }
                          </p>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="estimate-file">
                            {estimateType === "carrier" ? "Carrier File" : "Content File"}
                          </Label>
                          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-primary/50 transition-colors">
                            <input
                              id="estimate-file"
                              type="file"
                              onChange={handleEstimateFileChange}
                              className="hidden"
                              accept={estimateType === "carrier" 
                                ? "image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
                                : "*/*"
                              }
                            />
                            <label htmlFor="estimate-file" className="cursor-pointer">
                              {estimateType === "carrier" ? <FileImage className="h-6 w-6 text-muted-foreground mx-auto mb-2" /> : <File className="h-6 w-6 text-muted-foreground mx-auto mb-2" />}
                              <p className="text-sm text-muted-foreground">
                                {estimateFile ? estimateFile.name : `Click to upload ${estimateType} file`}
                              </p>
                              {estimateFile && (
                                <p className="text-xs text-muted-foreground mt-1">
                                  Size: {formatFileSize(estimateFile.size)}
                                </p>
                              )}
                            </label>
                          </div>
                        </div>
                        
                        <Button 
                          onClick={calculateSizeEstimate}
                          className="w-full"
                          disabled={!estimateFile || estimateLoading}
                        >
                          {estimateLoading ? (
                            <>
                              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                              Calculating...
                            </>
                          ) : (
                            <>
                              <Zap className="h-4 w-4 mr-2" />
                              Calculate Size Estimate
                            </>
                          )}
                        </Button>
                      </div>
                      
                      {/* Results Section */}
                      <div className="space-y-6">
                        <h3 className="text-lg font-semibold">Size Analysis Results</h3>
                        
                        {estimateResult ? (
                          <div className="space-y-4">
                            <div className="p-4 bg-muted rounded-lg space-y-3">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">File Size:</span>
                                <span className="text-sm">{estimateResult.fileSizeFormatted}</span>
                              </div>
                              
                              {estimateResult.type === "carrier" && (
                                <>
                                  <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Estimated Capacity:</span>
                                    <span className="text-sm">{estimateResult.capacityFormatted}</span>
                                  </div>
                                  <div className="flex items-center justify-between">
                                    <span className="text-sm font-medium">Method:</span>
                                    <span className="text-sm capitalize">{estimateResult.method}</span>
                                  </div>
                                </>
                              )}
                            </div>
                            
                            <div className="space-y-2">
                              <Label>Recommendations:</Label>
                              <div className="space-y-2">
                                {estimateResult.recommendations.map((rec: string, index: number) => (
                                  <Alert key={index}>
                                    <AlertDescription className="text-sm">
                                      {rec}
                                    </AlertDescription>
                                  </Alert>
                                ))}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-8 text-center text-muted-foreground border-2 border-dashed rounded-lg">
                            <RefreshCw className="h-8 w-8 mx-auto mb-2 opacity-50" />
                            <p>Upload a file and click calculate to see size analysis</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}