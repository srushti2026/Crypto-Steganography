import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { supabase } from "@/integrations/supabase/client";
import { ProjectFileService } from "@/services/projectFileService";
import { ProjectFilesDisplay } from "@/pages/Dashboard";
import { toast } from "sonner";
import {
  Shield,
  Upload,
  Download,
  FileImage,
  FileVideo,
  FileAudio,
  FileText,
  Lock,
  Eye,
  CheckCircle,
  AlertTriangle,
  Info,
  X,
  Plus,
  Calendar,
  Settings,
  RefreshCw,
  EyeOff,
  Copy,
  Key
} from "lucide-react";

// API Configuration - Dynamic URL that adapts to current hostname
const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000/api`;

// Helper function to format timestamp in user-friendly way
const formatTimestampForHumans = (date: Date): string => {
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  };
  return date.toLocaleDateString('en-US', options);
};

// Helper function to display timestamp (handles both old ISO and new user-friendly formats)
const displayTimestamp = (timestampStr: string): string => {
  // Handle null, undefined, or empty strings
  if (!timestampStr || timestampStr.trim() === '') {
    return 'N/A';
  }

  // Clean the timestamp string
  const cleanTimestamp = timestampStr.trim();

  // Check if it's already in ISO format (contains 'T' and ends with 'Z' or has timezone)
  if (cleanTimestamp.includes('T') && (cleanTimestamp.endsWith('Z') || cleanTimestamp.includes('+') || cleanTimestamp.match(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/))) {
    // It's an ISO timestamp, convert to user-friendly format
    try {
      const date = new Date(cleanTimestamp);
      // Check if the date is valid
      if (isNaN(date.getTime())) {
        return cleanTimestamp; // Return original string if date is invalid
      }
      return formatTimestampForHumans(date);
    } catch {
      // If parsing fails, return as-is
      return cleanTimestamp;
    }
  } else {
    // Check if it looks like it might be a partial ISO string or malformed date
    if (cleanTimestamp.includes('-') && cleanTimestamp.length > 10) {
      try {
        const date = new Date(cleanTimestamp);
        if (!isNaN(date.getTime())) {
          return formatTimestampForHumans(date);
        }
      } catch {
        // If it fails, fall through to return as-is
      }
    }
    
    // It's already in user-friendly format or unrecognized format, return as-is
    return cleanTimestamp;
  }
};

// Types
interface FormatData {
  carrier_formats: string[];
  content_formats: string[];
  max_size_mb: number;
}

interface SupportedFormats {
  image: FormatData;
  audio: FormatData;
  video: FormatData;
  document?: FormatData;
}

interface OperationResult {
  success: boolean;
  message: string;
  filename?: string;
  output_filename?: string;
  processing_time?: number;
  extracted_filename?: string;
  content_type?: string;
  file_size?: number;
  text_content?: string;
  preview?: string;
  capacity_info?: {
    estimated_capacity: number;
    content_size: number;
    utilization_percentage: number;
  };
  batch_results?: Array<{
    carrier_file: string;
    output_file: string;
    success: boolean;
    message?: string;
    processing_time?: number;
  }>;
}

export default function CopyrightProtection() {
  const navigate = useNavigate();
  const location = useLocation();

  // State management
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [carrierFiles, setCarrierFiles] = useState<File[]>([]); // Multiple carrier files
  const [batchMode, setBatchMode] = useState(false); // Toggle between single and batch mode
  const [extractFile, setExtractFile] = useState<File | null>(null);

  // Copyright fields state
  const [authorName, setAuthorName] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [copyrightAlias, setCopyrightAlias] = useState("");

  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [savePasswordWithProject, setSavePasswordWithProject] = useState(false);
  const [savedPassword, setSavedPassword] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressCompleted, setProgressCompleted] = useState(false);
  const [progressInterval, setProgressInterval] = useState<NodeJS.Timeout | null>(null);
  const [operationResult, setOperationResult] = useState<OperationResult | null>(null);
  const [currentOperationId, setCurrentOperationId] = useState<string | null>(null);
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormats | null>(null);
  const [carrierType, setCarrierType] = useState("image");
  const [encryptionType] = useState("aes-256-gcm"); // Hidden from user, always use AES-256-GCM
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [savedProjects, setSavedProjects] = useState<any[]>([]);

  // File refresh trigger
  const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);

  // Project information fields
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
    
    // Check authentication and get user
    supabase.auth.getUser().then(async ({ data: { user } }) => {
      if (!user) {
        navigate("/auth");
      } else {
        setCurrentUser(user);
        
        // Handle newly created project from dashboard
        if (location.state?.newProject && location.state?.projectJustCreated) {
          console.log('📦 New copyright project received from dashboard:', location.state.newProject);
          setSelectedProject(location.state.newProject);
          setProjectName(location.state.newProject.name);
          setProjectDescription(location.state.newProject.description || "");
          toast.success(`Welcome to your new ${location.state.newProject.project_type} project!`);
        }
        
        // Handle existing project being opened from dashboard
        if (location.state?.existingProject && location.state?.projectToOpen) {
          console.log('🔓 Opening existing copyright project:', location.state.existingProject);
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
            console.log('📋 Restoring copyright project metadata:', metadata);
            const meta = metadata as any;
            
            // Copyright-specific fields
            if (meta.authorName) setAuthorName(meta.authorName);
            if (meta.timestamp) setTimestamp(meta.timestamp);
            if (meta.copyrightAlias) setCopyrightAlias(meta.copyrightAlias);
            
            // Operation settings
            if (meta.carrierType) setCarrierType(meta.carrierType);
            // encryptionType is hardcoded to 'aes-256-gcm' in copyright page
            
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
          
          toast.success(`Opened project: ${project.name} with saved copyright settings`);
        }
        
        // Load user projects
        await loadUserProjects(user.id);
      }
    });

    // Fetch supported formats
    fetchSupportedFormats();
  }, [navigate]);

  const loadUserProjects = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;

      setSavedProjects(data || []);
      
      // Auto-select the first project if available, or create one if none exists
      // But don't override if a project was just created or opened from dashboard
      if (data && data.length > 0 && !selectedProject && !location.state?.projectJustCreated && !location.state?.projectToOpen) {
        setSelectedProject(data[0]);
        setProjectName(data[0].name);
        setProjectDescription(data[0].description || "");
      } else if ((!data || data.length === 0) && !selectedProject) {
        // Auto-create a default project if none exists
        await createDefaultProject(userId);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    }
  };

  const createDefaultProject = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: userId,
            name: 'Copyright Protection Project',
            description: 'Automatically created project for copyright protection operations',
            project_type: 'copyright'
          }
        ])
        .select()
        .single();

      if (error) throw error;

      setSavedProjects([data]);
      setSelectedProject(data);
      toast.success('Project created successfully!');
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project');
    }
  };

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

  const fetchSupportedFormats = async () => {
    try {
      console.log("📡 Fetching supported formats from:", `${API_BASE_URL}/supported-formats`);
      const response = await fetch(`${API_BASE_URL}/supported-formats`);
      console.log(`📡 Formats response status: ${response.status}`);
      console.log(`📡 Response headers:`, response.headers);
      
      if (response.ok) {
        const formats = await response.json();
        console.log("📋 Raw API response:", formats);
        console.log("📋 Setting supported formats state...");
        setSupportedFormats(formats);
        console.log("✅ Supported formats state updated");
        
        // Verify the state was set correctly
        setTimeout(() => {
          console.log("🔍 Verifying formats state after update...");
        }, 100);
      } else {
        console.log("❌ Failed to fetch formats:", response.status);
        console.log("❌ Response text:", await response.text());
      }
    } catch (error) {
      console.error("❌ Error fetching supported formats:", error);
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
      toast.error("Please enter a project name");
      return;
    }

    try {
      // Create comprehensive metadata object for copyright protection project
      const projectMetadata = {
        // Copyright-specific fields
        authorName: authorName,
        timestamp: timestamp,
        copyrightAlias: copyrightAlias,
        
        // Operation settings
        carrierType: carrierType,
        encryptionType: encryptionType,
        
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

      toast.success("Project settings saved successfully!");
      console.log('✅ Copyright project settings updated with metadata:', data);
    } catch (error) {
      console.error('❌ Error saving copyright project settings:', error);
      toast.error(`Failed to save project settings: ${error.message}`);
    }
  };

  const copyPasswordToClipboard = async () => {
    if (password) {
      try {
        await navigator.clipboard.writeText(password);
        toast.success("Password copied to clipboard!");
      } catch (error) {
        console.error("Failed to copy password:", error);
        toast.error("Failed to copy password to clipboard");
      }
    }
  };

  // Polling function for operation status
  const pollOperationStatus = async (operationId: string) => {
    const maxAttempts = 120; // 2 minutes with 1-second intervals
    let attempts = 0;

    const poll = async () => {
      try {
        attempts++;
        const response = await fetch(`${API_BASE_URL}/operations/${operationId}/status`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const status = await response.json();
        if (status.progress !== undefined) {
          // Never allow progress to go backwards
          setSafeProgress(status.progress);
        }

        if (status.status === 'completed') {
          stopProgressSimulation();
          setSafeProgress(100); // Ensure it shows 100% on completion
          
          // Store processed result if user is authenticated and project is selected
          if (currentUser && selectedProject && status.result) {
            try {
              // Create a processed file record
              const processedFileName = status.result.output_file || "copyright_processed_file";
              const processedFileUrl = status.result.download_url || "";
              
              await ProjectFileService.storeProcessedFile(
                selectedProject.id,
                processedFileName,
                "processed_copyright_result",
                processedFileUrl,
                status.result.file_size || 0,
                currentUser.id,
                operationId,
                encryptionType
              );
            } catch (error) {
              console.error('Error storing copyright processed file:', error);
              // Don't fail the operation if file storage fails
            }
          }
          
          setTimeout(() => {
            setIsProcessing(false);
            // Set success to true since status is 'completed'
            setOperationResult({
              ...status.result,
              success: true
            });
            // Trigger file list refresh
            setFileRefreshTrigger(prev => prev + 1);
            toast.success("Operation completed successfully!");
          }, 500); // Small delay to show 100% before showing results
        } else if (status.status === 'failed') {
          stopProgressSimulation();
          setIsProcessing(false);
          // Set success to false since status is 'failed'
          setOperationResult({
            success: false,
            message: status.error || "Operation failed"
          });
          toast.error(status.error || "Operation failed");
        } else if (attempts < maxAttempts) {
          setTimeout(poll, 1000);
        } else {
          stopProgressSimulation();
          setIsProcessing(false);
          toast.error("Operation timed out");
        }
      } catch (error) {
        stopProgressSimulation();
        console.error("Polling error:", error);
        if (attempts < maxAttempts) {
          setTimeout(poll, 1000);
        } else {
          setIsProcessing(false);
          toast.error("Failed to check operation status");
        }
      }
    };

    poll();
  };

  // File validation
  const validateFile = (file: File, type: string): boolean => {
    console.log(`🔍 Validating file: ${file.name} for type: ${type}`);
    console.log("📋 Supported formats available:", supportedFormats);
    
    if (!supportedFormats) {
      console.log("❌ No supported formats loaded yet");
      toast.error("Supported formats not loaded. Please wait a moment and try again.");
      return false;
    }

    const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
    console.log(`📄 File extension detected: ${fileExtension}`);
    
    const formatData = supportedFormats[type as keyof SupportedFormats];
    console.log(`📋 Format data for ${type}:`, formatData);
    
    // Handle the new format structure from API
    const formats = formatData?.carrier_formats || [];
    console.log(`✅ Available formats for ${type}:`, formats);
    
    if (!formats.includes(fileExtension)) {
      console.log(`❌ File extension ${fileExtension} not supported`);
      toast.error(`Unsupported ${type} format. Supported: ${formats.join(', ')}`);
      return false;
    }

    console.log("✅ File validation passed");
    return true;
  };

  // Handle embedding operation
  const handleEmbed = async () => {
    console.log("🔄 Embed button clicked - starting validation...");
    
    // Validation
    if (batchMode) {
      if (!carrierFiles || carrierFiles.length === 0) {
        console.log("❌ Validation failed: No carrier files selected for batch mode");
        toast.error("Please select at least one carrier file for batch processing");
        return;
      }
      console.log(`✅ Batch mode: ${carrierFiles.length} files selected`);
    } else {
      if (!carrierFile) {
        console.log("❌ Validation failed: No carrier file selected");
        toast.error("Please select a carrier file");
        return;
      }
      console.log(`✅ Single mode: File selected - ${carrierFile.name}`);
    }

    // Copyright validation
    if (!authorName.trim()) {
      console.log("❌ Validation failed: No author name");
      toast.error("Please enter the author name");
      return;
    }
    console.log(`✅ Author name: ${authorName}`);
    
    if (!copyrightAlias.trim()) {
      console.log("❌ Validation failed: No copyright alias");
      toast.error("Please enter the copyright alias");
      return;
    }
    console.log(`✅ Copyright alias: ${copyrightAlias}`);
    // Timestamp is optional - will be auto-generated if empty

    if (!password.trim()) {
      console.log("❌ Validation failed: No password");
      toast.error("Please enter a password");
      return;
    }
    console.log("✅ Password provided");

    // Validate file format(s)
    console.log(`🔍 Validating file formats for carrier type: ${carrierType}`);
    if (batchMode) {
      for (let i = 0; i < carrierFiles.length; i++) {
        if (!validateFile(carrierFiles[i], carrierType)) {
          console.log(`❌ File validation failed for: ${carrierFiles[i].name}`);
          toast.error(`Validation failed for file ${i + 1}: ${carrierFiles[i].name}`);
          return;
        }
      }
      console.log("✅ All batch files validated successfully");
    } else {
      if (!validateFile(carrierFile, carrierType)) {
        console.log(`❌ File validation failed for: ${carrierFile.name}`);
        return;
      }
      console.log("✅ Carrier file validated successfully");
    }

    console.log("🚀 Starting embed process...");
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
      
      formData.append('content_type', 'text'); // Always text for copyright
      formData.append('password', password);
      formData.append('encryption_type', encryptionType);

      // Add project information if provided
      if (projectName.trim()) {
        formData.append('project_name', projectName.trim());
      }
      if (projectDescription.trim()) {
        formData.append('project_description', projectDescription.trim());
      }

      // Create copyright JSON object with user-friendly timestamp
      const currentDate = new Date();
      const userFriendlyTimestamp = timestamp.trim() || formatTimestampForHumans(currentDate);
      
      const copyrightData = {
        author_name: authorName.trim(),
        copyright_alias: copyrightAlias.trim(),
        timestamp: userFriendlyTimestamp
      };
      formData.append('text_content', JSON.stringify(copyrightData));

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call
      const endpoint = batchMode ? `${API_BASE_URL}/embed-batch` : `${API_BASE_URL}/embed`;
      console.log(`📡 Making API call to: ${endpoint}`);
      console.log("📦 FormData contents:");
      for (let [key, value] of formData.entries()) {
        if (value instanceof File) {
          console.log(`  ${key}: File(${value.name}, ${value.size} bytes)`);
        } else {
          console.log(`  ${key}: ${value}`);
        }
      }
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData
      });

      console.log(`📡 API Response: ${response.status}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        console.log("❌ API Error:", errorData);
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      console.log("✅ API Success:", result);
      setCurrentOperationId(result.operation_id);
      
      // Store uploaded files in project if user is authenticated and project is selected
      if (currentUser && selectedProject) {
        try {
          console.log('💾 Storing files for copyright project:', selectedProject.id);
          
          if (batchMode) {
            // Store all carrier files for batch processing
            for (const file of carrierFiles) {
              const storedFile = await ProjectFileService.storeUploadedFile(
                selectedProject.id,
                file,
                currentUser.id
              );
              console.log('✅ Stored copyright carrier file:', storedFile);
            }
          } else {
            // Store single carrier file
            const storedFile = await ProjectFileService.storeUploadedFile(
              selectedProject.id,
              carrierFile!,
              currentUser.id
            );
            console.log('✅ Stored copyright carrier file:', storedFile);
          }
          
          // Create operation record
          const operation = await ProjectFileService.createOperation(
            selectedProject.id,
            currentUser.id,
            batchMode ? "batch_copyright_embed" : "copyright_embed",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            "copyright_text",
            true, // copyright always uses encryption
            true, // assume success initially
            undefined
          );
          console.log('✅ Created copyright operation:', operation);
          
        } catch (error) {
          console.error('💥 Error storing copyright files:', error);
          // Don't fail the operation if file storage fails
        }
      } else {
        console.warn('⚠️ Cannot store files - missing user or project:', {
          currentUser: !!currentUser,
          selectedProject: !!selectedProject
        });
      }
      
      toast.success("Copyright embedding started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      // Clean up backend error messages for better UX
      let errorMessage = error.message || "Copyright embedding failed";
      
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
      const formData = new FormData();
      formData.append('stego_file', extractFile);  // Backend expects 'stego_file', not 'carrier_file'
      formData.append('password', password);
      formData.append('output_format', 'auto');

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

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
            "copyright_extract",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            "copyright_text", // extracting copyright data
            false, // extraction doesn't typically involve encryption
            true, // assume success initially
            undefined
          );
        } catch (error) {
          console.error('Error storing copyright extraction files:', error);
          // Don't fail the operation if file storage fails
        }
      }
      
      toast.success("Copyright extraction started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      
      let errorMessage = error.message || "Copyright extraction failed";
      
      if (errorMessage.includes("NoneType") || 
          errorMessage.includes("subscriptable") ||
          errorMessage.includes("steganography_operations") ||
          errorMessage.includes("PGRST205") ||
          errorMessage.includes("schema cache")) {
        errorMessage = "Operation may have completed but database logging failed. Please check your outputs folder for the result file.";
      }
      
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file format or password incorrect.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Service not available. Please ensure the backend is running.";
      }
      
      toast.error(errorMessage);
      console.error("Extract error:", error);
    }
  };

  // Enhanced download with proper save as functionality
  const saveAsResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      const downloadEndpoint = `${API_BASE_URL}/operations/${currentOperationId}/download`;
      
      // Determine default filename based on operation type
      let defaultFilename;
      if (selectedTab === 'embed') {
        defaultFilename = operationResult?.output_filename || operationResult?.filename || 'copyright_embedded_file';
        // Ensure extension matches carrier file if available
        if (!defaultFilename.includes('.') && carrierFile) {
          const originalExt = carrierFile.name.split('.').pop();
          defaultFilename += `.${originalExt}`;
        }
      } else if (selectedTab === 'extract') {
        defaultFilename = operationResult?.extracted_filename || 'copyright_extracted_content.txt';
      } else {
        defaultFilename = 'copyright_result.bin';
      }
      
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

      // Removed orphaned debug code
      


  // Utility function to format file sizes
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Helper function to parse and validate copyright data
  const parseCopyrightData = (textContent: string) => {
    try {
      const data = JSON.parse(textContent);
      if (data.author_name && data.copyright_alias && data.timestamp) {
        return data;
      }
    } catch (e) {
      // Not valid JSON or missing required fields
    }
    return null;
  };

  // Generate secure password
  const generatePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setPassword(password);
    toast.success("Password generated successfully!");
  };

  // Save copyright information as JSON file with proper save as functionality
  const saveAsCopyrightInfo = async (copyrightData: any) => {
    try {
      const dataStr = JSON.stringify(copyrightData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const defaultFilename = `copyright-info-${copyrightData.author_name?.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
      
      // Use the utility function for proper save as functionality
      const { downloadFileWithSaveAs } = await import('@/utils/fileDownload');
      await downloadFileWithSaveAs(
        dataBlob,
        defaultFilename,
        `Copyright information saved as "{filename}"!`
      );
    } catch (error: any) {
      console.error("Save copyright info error:", error);
      toast.error(`Failed to save copyright information: ${error.message}`);
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
                <div className="flex items-center gap-3">
                  <Shield className="h-8 w-8 text-primary" />
                  <div>
                    <h1 className="text-3xl font-bold">Copyright Protection</h1>
                    <p className="text-muted-foreground">Secure your intellectual property with invisible copyright steganography</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Main Content */}
        <section className="py-8">
          <div className="container">
            <div className="max-w-4xl mx-auto">
              <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="embed" className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    Embed Copyright
                  </TabsTrigger>
                  <TabsTrigger value="extract" className="flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    Extract Copyright
                  </TabsTrigger>
                  <TabsTrigger value="settings" className="flex items-center gap-2">
                    <Settings className="h-4 w-4" />
                    Project Settings
                  </TabsTrigger>
                </TabsList>

                {/* Embed Tab */}
                <TabsContent value="embed" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Shield className="h-5 w-5" />
                        Embed Copyright Information
                      </CardTitle>
                      <CardDescription>
                        Hide your copyright details invisibly within media files to protect your intellectual property.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Batch Mode Toggle */}
                      <div className="flex items-center space-x-2">
                        <Switch
                          id="batch-mode"
                          checked={batchMode}
                          onCheckedChange={setBatchMode}
                        />
                        <Label htmlFor="batch-mode">
                          Batch Processing (Process multiple files at once)
                        </Label>
                      </div>

                      {/* Carrier File Selection */}
                      <div className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="carrier-type">Carrier File Type</Label>
                          <Select value={carrierType} onValueChange={setCarrierType}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="image">
                                <div className="flex items-center gap-2">
                                  <FileImage className="h-4 w-4" />
                                  Image File
                                </div>
                              </SelectItem>
                              <SelectItem value="audio">
                                <div className="flex items-center gap-2">
                                  <FileAudio className="h-4 w-4" />
                                  Audio File
                                </div>
                              </SelectItem>
                              <SelectItem value="video">
                                <div className="flex items-center gap-2">
                                  <FileVideo className="h-4 w-4" />
                                  Video File
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
                          {supportedFormats && (
                            <p className="text-xs text-muted-foreground">
                              Supported formats: {supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.join(", ") || "Loading..."}
                            </p>
                          )}
                        </div>

                        {!batchMode ? (
                          <div className="space-y-2">
                            <Label htmlFor="carrier-file">Carrier File</Label>
                            <div className="flex items-center gap-2">
                              <Input
                                id="carrier-file"
                                type="file"
                                onChange={(e) => setCarrierFile(e.target.files?.[0] || null)}
                                accept={supportedFormats ? supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.map(ext => `.${ext}`).join(',') || '' : ''}
                              />
                            </div>
                            {carrierFile && (
                              <p className="text-sm text-muted-foreground">
                                Selected: {carrierFile.name} ({formatFileSize(carrierFile.size)})
                              </p>
                            )}
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Label htmlFor="carrier-files">Carrier Files (Multiple)</Label>
                            <div className="flex items-center gap-2">
                              <Input
                                id="carrier-files"
                                type="file"
                                multiple
                                onChange={(e) => setCarrierFiles(Array.from(e.target.files || []))}
                                accept={supportedFormats ? supportedFormats[carrierType as keyof SupportedFormats]?.carrier_formats?.map(ext => `.${ext}`).join(',') || '' : ''}
                              />
                            </div>
                            {carrierFiles.length > 0 && (
                              <div className="text-sm text-muted-foreground space-y-1">
                                <p>Selected {carrierFiles.length} files:</p>
                                {carrierFiles.slice(0, 3).map((file, index) => (
                                  <p key={index} className="ml-2">• {file.name} ({formatFileSize(file.size)})</p>
                                ))}
                                {carrierFiles.length > 3 && (
                                  <p className="ml-2">• ... and {carrierFiles.length - 3} more files</p>
                                )}
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Copyright Information Section */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Shield className="h-5 w-5 text-blue-600" />
                          <Label className="text-lg font-medium">Copyright Information</Label>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label htmlFor="author-name">Author Name *</Label>
                            <Input
                              id="author-name"
                              value={authorName}
                              onChange={(e) => setAuthorName(e.target.value)}
                              placeholder="Enter author's full name..."
                            />
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor="copyright-alias">Copyright Alias *</Label>
                            <Input
                              id="copyright-alias"
                              value={copyrightAlias}
                              onChange={(e) => setCopyrightAlias(e.target.value)}
                              placeholder="Enter copyright alias or company..."
                            />
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="timestamp">Timestamp</Label>
                          <div className="flex gap-2">
                            <Input
                              id="timestamp"
                              value={timestamp}
                              onChange={(e) => setTimestamp(e.target.value)}
                              placeholder="Enter custom timestamp or leave for auto-generated..."
                              className="flex-1"
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => setTimestamp(formatTimestampForHumans(new Date()))}
                              className="shrink-0"
                            >
                              <Calendar className="h-4 w-4 mr-2" />
                              Use Current Time
                            </Button>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Current time will be used if left empty. Format: ISO 8601 (e.g., {new Date().toISOString()})
                          </p>
                        </div>
                      </div>

                      <Separator />

                      {/* Password Settings */}
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          <Lock className="h-5 w-5 text-primary" />
                          <Label className="text-lg font-medium">Password Security</Label>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="password">Password *</Label>
                          <div className="flex gap-2">
                            <Input
                              id="password"
                              type={showPassword ? "text" : "password"}
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Enter a strong password..."
                              className="flex-1"
                            />
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => setShowPassword(!showPassword)}
                              className="shrink-0"
                            >
                              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </Button>
                            <Button
                              type="button"
                              variant="outline"
                              onClick={generatePassword}
                              className="shrink-0"
                            >
                              <RefreshCw className="h-4 w-4 mr-2" />
                              Generate
                            </Button>
                            {password && (
                              <Button
                                type="button"
                                variant="outline"
                                onClick={copyPasswordToClipboard}
                                className="shrink-0"
                                title="Copy password to clipboard"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                          
                          {/* Password Management Options */}
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                id="save-password-with-project-copyright"
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
                              <Label htmlFor="save-password-with-project-copyright" className="text-sm">
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
                      </div>

                      <Button 
                        onClick={() => {
                          console.log("🎯 Embed button clicked!");
                          handleEmbed();
                        }} 
                        disabled={isProcessing} 
                        className="w-full"
                        size="lg"
                      >
                        {isProcessing ? (
                          <>Processing... ({progress}%)</>
                        ) : (
                          <>
                            <Shield className="h-4 w-4 mr-2" />
                            Embed Copyright Information
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Extract Tab */}
                <TabsContent value="extract" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="h-5 w-5" />
                        Extract Copyright Information
                      </CardTitle>
                      <CardDescription>
                        Extract and verify copyright information from protected media files.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="space-y-2">
                        <Label htmlFor="extract-file">File to Extract From</Label>
                        <Input
                          id="extract-file"
                          type="file"
                          onChange={(e) => setExtractFile(e.target.files?.[0] || null)}
                        />
                        {extractFile && (
                          <p className="text-sm text-muted-foreground">
                            Selected: {extractFile.name} ({formatFileSize(extractFile.size)})
                          </p>
                        )}
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="extract-password">Password *</Label>
                        <div className="flex gap-2">
                          <Input
                            id="extract-password"
                            type={showPassword ? "text" : "password"}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter the password..."
                            className="flex-1"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => setShowPassword(!showPassword)}
                            className="shrink-0"
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                          {password.trim() && (
                            <Button
                              type="button"
                              variant="outline"
                              onClick={copyPasswordToClipboard}
                              className="shrink-0"
                              title="Copy password to clipboard"
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Uses AES-256-GCM decryption
                        </p>
                        
                        {/* Password Management Options */}
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              id="save-password-with-project-extract"
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
                            <Label htmlFor="save-password-with-project-extract" className="text-sm">
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
                        onClick={handleExtract} 
                        disabled={isProcessing} 
                        className="w-full"
                        size="lg"
                      >
                        {isProcessing ? (
                          <>Processing... ({progress}%)</>
                        ) : (
                          <>
                            <Eye className="h-4 w-4 mr-2" />
                            Extract Copyright Information
                          </>
                        )}
                      </Button>
                    </CardContent>
                  </Card>
                </TabsContent>

                {/* Project Settings Tab */}
                <TabsContent value="settings" className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Settings className="h-5 w-5" />
                        Project Settings
                      </CardTitle>
                      <CardDescription>
                        Configure project information and metadata for your copyright operations.
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="settings-project-name">Project Name</Label>
                          <Input
                            id="settings-project-name"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="Enter project name..."
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="settings-project-description">Project Description</Label>
                          <Textarea
                            id="settings-project-description"
                            value={projectDescription}
                            onChange={(e) => setProjectDescription(e.target.value)}
                            placeholder="Brief description of the project..."
                            rows={4}
                          />
                        </div>
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
                                  onClick={() => setShowPassword(!showPassword)}
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
                                if (e.target.checked && password.trim()) {
                                  setSavedPassword(password);
                                  toast.success("Password saved with project settings!");
                                } else if (!e.target.checked) {
                                  setSavedPassword("");
                                  toast.success("Password removed from project settings!");
                                }
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
                      
                      {/* Project Actions */}
                      <div className="space-y-3 pt-4 border-t">
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
                              if (selectedProject) {
                                window.open('/dashboard', '_blank');
                                toast.success("Opening dashboard in new tab");
                              } else {
                                toast.error("No project selected to save to dashboard");
                              }
                            }}
                          >
                            Save Project to Dashboard
                          </Button>
                        </div>
                        
                        {/* Project Files Display */}
                        {selectedProject && (
                          <div className="space-y-3 pt-4 border-t">
                            <h4 className="text-sm font-semibold flex items-center gap-2">
                              <FileText className="h-4 w-4" />
                              Project Files
                            </h4>
                            <ProjectFilesDisplay project={selectedProject} refreshTrigger={fileRefreshTrigger} />
                          </div>
                        )}
                      </div>
                      
                      <Alert>
                        <Info className="h-4 w-4" />
                        <AlertDescription>
                          Project settings are optional and will be included in the operation metadata for better organization and tracking.
                        </AlertDescription>
                      </Alert>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>

              {/* Progress and Results */}
              {isProcessing && (
                <Card className="mt-6">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <Label className="text-sm font-medium">Processing Copyright Protection...</Label>
                        <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
                      </div>
                      <Progress value={progress} className="w-full h-3" />
                      <p className="text-xs text-muted-foreground text-center">
                        Embedding copyright data... Securing your intellectual property.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Operation Result */}
              {operationResult && !isProcessing && (
                <Card className="mt-6">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <Alert className={operationResult.success ? "border-green-200 bg-green-50 dark:bg-green-950/30" : "border-blue-200 bg-blue-50 dark:bg-blue-950/30"}>
                        <div className="flex items-center gap-2">
                          {operationResult.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <AlertTriangle className="h-4 w-4 text-blue-600" />
                          )}
                          <span className="font-medium">
                            {operationResult.success ? "Success" : "Failed"}
                          </span>
                        </div>
                        <AlertDescription className="mt-2">
                          {operationResult.message}
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
                          {(operationResult.text_content || operationResult.preview) && (() => {
                            const textData = operationResult.text_content || operationResult.preview;
                            const copyrightData = parseCopyrightData(textData);
                            
                            if (copyrightData) {
                              // Display copyright information prominently
                              return (
                                <div className="space-y-4">
                                  <div className="p-4 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg">
                                    <div className="flex items-center justify-between mb-3">
                                      <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 flex items-center gap-2">
                                        <Shield className="h-5 w-5" />
                                        Copyright Information Verified
                                      </h3>
                                      <Button
                                        variant="outline"
                                        size="sm"
                                        onClick={() => saveAsCopyrightInfo(copyrightData)}
                                        className="text-green-700 border-green-300 hover:bg-green-100"
                                      >
                                        <Download className="h-4 w-4 mr-2" />
                                        Save As JSON...
                                      </Button>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Author Name:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {copyrightData.author_name}
                                        </p>
                                      </div>
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Copyright Alias:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {copyrightData.copyright_alias}
                                        </p>
                                      </div>
                                      <div className="space-y-1">
                                        <p className="font-medium text-green-700 dark:text-green-300">Timestamp:</p>
                                        <p className="text-green-800 dark:text-green-200 font-mono bg-white dark:bg-green-900/20 p-2 rounded">
                                          {displayTimestamp(copyrightData.timestamp)}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              );
                            } else {
                              // Display regular text content
                              return (
                                <div className="space-y-1">
                                  <p className="text-sm font-medium">Text Content:</p>
                                  <div className="p-2 bg-background rounded border max-h-32 overflow-y-auto">
                                    <pre className="text-xs font-mono whitespace-pre-wrap">{textData}</pre>
                                  </div>
                                </div>
                              );
                            }
                          })()}
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Button 
                          onClick={saveAsResult} 
                          className="w-full bg-primary hover:bg-primary/90"
                          disabled={!currentOperationId}
                          title="Save your file with custom location and filename"
                        >
                          <Download className="h-4 w-4 mr-2" />
                          💾 Save As... (Choose Where & What Name)
                        </Button>
                        

                      </div>
                      

                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
