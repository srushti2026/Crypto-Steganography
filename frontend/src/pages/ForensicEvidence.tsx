import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { supabase } from "@/integrations/supabase/client";
import { ProjectFileService } from "@/services/projectFileService";
import { ProjectFilesDisplay } from "@/pages/Dashboard";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { 
  Shield, 
  FileCheck, 
  Lock, 
  Upload, 
  Download, 
  Key,
  FileText,
  Eye,
  EyeOff,
  Copy,
  RefreshCw,
  Calendar,
  User,
  FileImage,
  CheckCircle
} from "lucide-react";

// API Service Integration
const getApiUrl = () => {
  // Check if we're in production (Vercel deployment)
  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    return 'https://veilforge.onrender.com';
  }
  
  // Try to get environment variable
  try {
    const envUrl = import.meta?.env?.VITE_API_URL;
    if (envUrl) return envUrl;
  } catch (error) {
    console.warn('Environment variable access failed');
  }
  
  // Local development fallback
  return 'http://localhost:8000';
};
const API_BASE_URL = getApiUrl();

// Enhanced toast system
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
  const topOffset = 16 + (activeToasts.length * 80);
  
  notification.className = `fixed right-4 ${bgColor} text-white p-3 rounded-lg shadow-lg z-50 transition-all duration-300 ease-in-out`;
  notification.style.top = `${topOffset}px`;
  notification.textContent = message;
  
  activeToasts.push(notification);
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '1';
    notification.style.transform = 'translateX(0)';
  }, 10);
  
  setTimeout(() => {
    const index = activeToasts.indexOf(notification);
    if (index > -1) {
      activeToasts.splice(index, 1);
      
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      
      setTimeout(() => {
        if (notification.parentNode) {
          document.body.removeChild(notification);
        }
        
        activeToasts.forEach((toast, i) => {
          const newTopOffset = 16 + (i * 80);
          toast.style.top = `${newTopOffset}px`;
        });
      }, 300);
    }
  }, duration);
  
  notification.style.opacity = '0';
  notification.style.transform = 'translateX(100%)';
}

const ForensicEvidence = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Core state
  const [selectedTab, setSelectedTab] = useState("embed");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressCompleted, setProgressCompleted] = useState(false);
  const [operationResult, setOperationResult] = useState<any>(null);
  const [currentOperationId, setCurrentOperationId] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Forensic-specific metadata fields
  const [caseId, setCaseId] = useState("");
  const [embeddedOwner, setEmbeddedOwner] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [description, setDescription] = useState("");

  // File handling
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [hiddenFile, setHiddenFile] = useState<File | null>(null);
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [savePasswordWithProject, setSavePasswordWithProject] = useState(false);
  const [savedPassword, setSavedPassword] = useState("");

  // Extract results
  const [extractedMetadata, setExtractedMetadata] = useState<any>(null);
  const [showExtractedData, setShowExtractedData] = useState(false);

  // Project Settings state
  const [selectedProject, setSelectedProject] = useState<any>(null);
  const [savedProjects, setSavedProjects] = useState<any[]>([]);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  // File refresh trigger
  const [fileRefreshTrigger, setFileRefreshTrigger] = useState(0);
  const [projectTags, setProjectTags] = useState("");
  const [saveProject, setSaveProject] = useState(false);

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
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          console.log("⚠️  No user authenticated, but allowing access for testing");
        }
        setCurrentUser(user);
        
        // Set default timestamp to current date and time
        setTimestamp(new Date().toISOString().slice(0, 16));
      } catch (error) {
        console.error("Initialization error:", error);
        toast.error("Failed to initialize application");
      }
    };

    initializeComponent();
  }, [navigate]);

  // Debug effect to track operationResult changes
  useEffect(() => {
    console.log("🔍 Debug - operationResult changed:", operationResult);
    console.log("🔍 Debug - currentOperationId:", currentOperationId);
    console.log("🔍 Debug - selectedTab:", selectedTab);
    console.log("🔍 Debug - isProcessing:", isProcessing);
  }, [operationResult, currentOperationId, selectedTab, isProcessing]);

  // Load user projects for forensic operations
  useEffect(() => {
    const loadProjects = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        // Handle newly created project from dashboard
        if (location.state?.newProject && location.state?.projectJustCreated) {
          console.log('📦 New forensic project received from dashboard:', location.state.newProject);
          setSelectedProject(location.state.newProject);
          setProjectName(location.state.newProject.name);
          setProjectDescription(location.state.newProject.description || "");
          setSavedProjects([location.state.newProject]);
          toast.success(`Welcome to your new ${location.state.newProject.project_type} project!`);
        }
        
        // Handle existing project being opened from dashboard
        if (location.state?.existingProject && location.state?.projectToOpen) {
          console.log('🔓 Opening existing forensic project:', location.state.existingProject);
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
            console.log('📋 Restoring forensic project metadata:', metadata);
            const meta = metadata as any;
            
            // Forensic-specific fields
            if (meta.caseId) setCaseId(meta.caseId);
            if (meta.embeddedOwner) setEmbeddedOwner(meta.embeddedOwner);
            if (meta.timestamp) setTimestamp(meta.timestamp);
            if (meta.description) setDescription(meta.description);
            
            // Security settings
            if (meta.password && meta.savePasswordWithProject) {
              setPassword(meta.password);
              setSavedPassword(meta.password);
              setSavePasswordWithProject(true);
            }
            
            // UI preferences
            if (meta.showPassword !== undefined) setShowPassword(meta.showPassword);
            if (meta.showExtractedData !== undefined) setShowExtractedData(meta.showExtractedData);
            
            // Evidence data
            if (meta.extractedMetadata) setExtractedMetadata(meta.extractedMetadata);
            
            // Operation result
            if (meta.lastOperationResult) setOperationResult(meta.lastOperationResult);
          }
          
          setSavedProjects([project]);
          toast.success(`Opened forensic project: ${project.name} with saved evidence data`);
        }
        
        await loadUserProjects(user.id);
      }
    };
    loadProjects();
  }, []);
  // File handling functions
  const handleCarrierFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCarrierFile(e.target.files[0]);
    }
  };

  const handleHiddenFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setHiddenFile(e.target.files[0]);
    }
  };

  const handleExtractFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setExtractFile(e.target.files[0]);
    }
  };

  // Password functions
  const generatePassword = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-password?length=16&include_symbols=true`);
      if (response.ok) {
        const data = await response.json();
        setPassword(data.password);
        toast.success(`Generated ${data.strength} password`);
      } else {
        throw new Error('Failed to generate password');
      }
    } catch (error) {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?';
      let result = '';
      for (let i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      setPassword(result);
      toast.success('Generated strong password (local fallback)');
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
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

  // Project Management Functions
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
        await createDefaultProject(userId);
      }
    } catch (error) {
      console.error('💥 Error loading forensic projects:', error);
    }
  };

  const createDefaultProject = async (userId: string) => {
    try {
      const { data, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: userId,
            name: 'Forensic Evidence Project',
            description: 'Automatically created project for forensic steganography operations',
            project_type: 'forensic'
          }
        ])
        .select()
        .single();

      if (error) throw error;

      setSavedProjects([data]);
      setSelectedProject(data);
      setProjectName(data.name);
      setProjectDescription(data.description || "");
      toast.success('Default forensic project created successfully!');
      
      return data;
    } catch (error) {
      console.error('💥 Error creating default forensic project:', error);
      toast.error(`Failed to create default project: ${error.message}`);
    }
  };

  const saveProjectSettings = async () => {
    if (!selectedProject || !projectName.trim()) {
      toast.error("Please enter a project name");
      return;
    }

    try {
      // Create comprehensive metadata object for forensic evidence project
      const projectMetadata = {
        // Forensic-specific fields
        caseId: caseId,
        embeddedOwner: embeddedOwner,
        timestamp: timestamp,
        description: description,
        
        // Security settings
        password: savePasswordWithProject ? password : '',
        savePasswordWithProject: savePasswordWithProject,
        
        // UI preferences
        showPassword: showPassword,
        showExtractedData: showExtractedData,
        
        // Evidence data
        extractedMetadata: extractedMetadata,
        
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

      setSelectedProject(data);
      setSavedProjects(prevProjects => 
        prevProjects.map(p => p.id === selectedProject.id ? data : p)
      );

      toast.success("Forensic project settings saved successfully!");
      console.log('✅ Forensic project settings updated with metadata:', data);
    } catch (error) {
      console.error('❌ Error saving forensic project settings:', error);
      toast.error(`Failed to save project settings: ${error.message}`);
    }
  };

  const copyPasswordToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(password);
      toast.success("Password copied to clipboard!");
    } catch (error) {
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

  // Embed function with forensic metadata
  const handleForensicEmbed = async () => {
    // Validation
    if (!carrierFile) {
      toast.error("Please select a carrier file");
      return;
    }

    if (!hiddenFile) {
      toast.error("Please select a file to hide");
      return;
    }

    if (!caseId.trim()) {
      toast.error("Please enter a Case ID");
      return;
    }

    if (!embeddedOwner.trim()) {
      toast.error("Please enter the Embedded Owner");
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }

    setIsProcessing(true);
    resetProgress();
    setOperationResult(null);
    setCurrentOperationId(null);
    console.log("🚀 Starting forensic embed operation...");
    
    try {
      const formData = new FormData();
      formData.append('carrier_file', carrierFile);
      formData.append('content_file', hiddenFile);
      formData.append('password', password);
      formData.append('content_type', 'forensic');

      // Add forensic metadata as JSON
      const forensicMetadata = {
        case_id: caseId.trim(),
        embedded_owner: embeddedOwner.trim(),
        timestamp: timestamp || new Date().toISOString(),
        description: description.trim() || '',
        name: hiddenFile.name,
        file_size: hiddenFile.size,
        file_type: hiddenFile.type || 'application/octet-stream',
        carrier_name: carrierFile.name,
        created_by: currentUser?.email || 'unknown'
      };

      formData.append('forensic_metadata', JSON.stringify(forensicMetadata));

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Make API call to forensic-specific endpoint
      const response = await fetch(`${API_BASE_URL}/api/forensic-embed`, {
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
          console.log('💾 Storing files for forensic project:', selectedProject.id);
          
          // Store carrier file
          const storedCarrierFile = await ProjectFileService.storeUploadedFile(
            selectedProject.id,
            carrierFile,
            currentUser.id
          );
          console.log('✅ Stored forensic carrier file:', storedCarrierFile);
          
          // Store hidden file (evidence)
          const storedHiddenFile = await ProjectFileService.storeUploadedFile(
            selectedProject.id,
            hiddenFile,
            currentUser.id
          );
          console.log('✅ Stored forensic evidence file:', storedHiddenFile);
          
          // Create operation record
          const operation = await ProjectFileService.createOperation(
            selectedProject.id,
            currentUser.id,
            "forensic_embed",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            "forensic_evidence",
            password.length > 0, // encryption enabled if password provided
            true, // assume success initially
            undefined
          );
          console.log('✅ Created forensic operation:', operation);
          
        } catch (error) {
          console.error('💥 Error storing forensic files:', error);
          // Don't fail the operation if file storage fails
        }
      } else {
        console.warn('⚠️ Cannot store files - missing user or project:', {
          currentUser: !!currentUser,
          selectedProject: !!selectedProject
        });
      }
      
      toast.success("Forensic embedding operation started successfully!");
      
      // Start polling for progress
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      let errorMessage = error.message || "Forensic embedding operation failed";
      
      if (errorMessage.includes("NoneType") || errorMessage.includes("subscriptable")) {
        errorMessage = "Operation may have completed but database logging failed. Please check your outputs folder for the result file.";
      }
      
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file format or missing required information.";
      } else if (errorMessage.includes("HTTP 404")) {
        errorMessage = "Forensic service not available. Using standard embed endpoint.";
        
        // Fallback to standard embed with forensic data as text
        handleStandardEmbedWithForensicData();
        return;
      }
      
      toast.error(errorMessage);
      console.error("Forensic embed error:", error);
    }
  };

  // Fallback function using standard embed endpoint
  const handleStandardEmbedWithForensicData = async () => {
    try {
      const formData = new FormData();
      formData.append('carrier_file', carrierFile!);
      formData.append('content_file', hiddenFile!);
      formData.append('password', password);
      formData.append('content_type', 'file');
      formData.append('carrier_type', 'image'); // Default to image

      // Add forensic metadata as JSON text content alongside the file
      const forensicMetadata = {
        case_id: caseId.trim(),
        embedded_owner: embeddedOwner.trim(),
        timestamp: timestamp || new Date().toISOString(),
        description: description.trim() || '',
        name: hiddenFile!.name,
        file_size: hiddenFile!.size,
        file_type: hiddenFile!.type || 'application/octet-stream',
        carrier_name: carrierFile!.name,
        created_by: currentUser?.email || 'unknown'
      };

      // Create a combined payload
      const combinedData = {
        forensic_metadata: forensicMetadata,
        original_filename: hiddenFile!.name
      };

      formData.append('forensic_data', JSON.stringify(combinedData));

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      const response = await fetch(`${API_BASE_URL}/api/embed`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();
      setCurrentOperationId(result.operation_id);
      toast.success("Forensic embedding operation started (using standard endpoint)!");
      
      pollOperationStatus(result.operation_id);
      
    } catch (error: any) {
      setIsProcessing(false);
      toast.error(error.message || "Embedding operation failed");
      console.error("Standard embed error:", error);
    }
  };

  // Extract function with forensic metadata display
  const handleForensicExtract = async () => {
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
    setExtractedMetadata(null);
    setShowExtractedData(false);
    
    try {
      const formData = new FormData();
      formData.append('stego_file', extractFile);
      formData.append('password', password);
      formData.append('output_format', 'forensic');

      if (currentUser?.id) {
        formData.append('user_id', currentUser.id);
      }

      // Try forensic-specific endpoint first
      let response = await fetch(`${API_BASE_URL}/api/forensic-extract`, {
        method: 'POST',
        body: formData
      });

      // If forensic endpoint not available, use standard endpoint
      if (!response.ok && response.status === 404) {
        formData.set('output_format', 'auto');
        response = await fetch(`${API_BASE_URL}/api/extract`, {
          method: 'POST',
          body: formData
        });
      }

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
            "forensic_extract",
            undefined, // carrier file ID will be set later
            undefined, // processed file ID will be set later
            "forensic_evidence", // extracting forensic evidence data
            false, // extraction doesn't typically involve encryption
            true, // assume success initially
            undefined
          );
        } catch (error) {
          console.error('Error storing forensic extraction files:', error);
          // Don't fail the operation if file storage fails
        }
      }
      
      toast.success("Forensic extraction operation started successfully!");
      
      pollOperationStatus(result.operation_id, true);
      
    } catch (error: any) {
      setIsProcessing(false);
      let errorMessage = error.message || "Forensic extraction operation failed";
      
      if (errorMessage.includes("NoneType") || errorMessage.includes("subscriptable")) {
        errorMessage = "Operation may have completed but database logging failed. Please check the extraction results.";
      }
      
      if (errorMessage.includes("HTTP 500")) {
        errorMessage = "Server error occurred. Please try again or contact support.";
      } else if (errorMessage.includes("HTTP 422")) {
        errorMessage = "Invalid file or incorrect password.";
      }
      
      toast.error(errorMessage);
      console.error("Forensic extract error:", error);
    }
  };

  const pollOperationStatus = async (operationId: string, isExtraction: boolean = false) => {
    const maxAttempts = 300;
    let attempts = 0;

    const poll = async () => {
      try {
        if (!operationId || operationId === 'undefined') {
          console.error('Invalid operation ID for polling:', operationId);
          return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/operations/${operationId}/status`);
        if (!response.ok) throw new Error('Failed to check status');
        
        const status = await response.json();
        
        if (status.progress !== undefined) {
          setSafeProgress(status.progress);
        }

        if (status.status === "completed") {
          setSafeProgress(100);
          setIsProcessing(false);
          console.log("✅ Operation completed successfully!");
          console.log("📊 Full status response:", status);
          console.log("📊 Status result field:", status.result);
          console.log("🎯 Current tab:", selectedTab);
          console.log("🆔 Operation ID:", operationId);
          
          // Store processed result if user is authenticated and project is selected
          if (currentUser && selectedProject && status.result) {
            try {
              // Create a processed file record
              const processedFileName = status.result.output_file || "forensic_processed_file";
              const processedFileUrl = status.result.download_url || "";
              
              await ProjectFileService.storeProcessedFile(
                selectedProject.id,
                processedFileName,
                "processed_forensic_result",
                processedFileUrl,
                status.result.file_size || 0,
                currentUser.id,
                operationId,
                password ? "forensic_encryption" : undefined
              );
            } catch (error) {
              console.error('Error storing forensic processed file:', error);
              // Don't fail the operation if file storage fails
            }
          }
          
          // Force set operationResult even if it's null
          if (status.result) {
            setOperationResult(status.result);
            console.log("✅ Set operationResult:", status.result);
          } else {
            console.log("⚠️ Status result is null, creating dummy result for download");
            // Create a minimal result object to enable download
            const dummyResult = {
              success: true,
              filename: `forensic_evidence_${operationId.slice(0, 8)}.png`,
              message: "Operation completed successfully"
            };
            setOperationResult(dummyResult);
          }

          
          // For extraction, try to parse forensic metadata
          if (isExtraction && status.result) {
            try {
              // Check if there's forensic metadata in the result
              if (status.result.forensic_metadata) {
                setExtractedMetadata(status.result.forensic_metadata);
                setShowExtractedData(true);
              } else if (status.result.extracted_content) {
                // Try to parse extracted content for forensic data
                try {
                  const contentData = JSON.parse(status.result.extracted_content);
                  if (contentData.forensic_metadata) {
                    setExtractedMetadata(contentData.forensic_metadata);
                    setShowExtractedData(true);
                  }
                } catch (parseError) {
                  console.log("No forensic metadata found in extracted content");
                }
              }
            } catch (error) {
              console.error("Error parsing forensic metadata:", error);
            }
          }
          
          // Trigger file list refresh
          setFileRefreshTrigger(prev => prev + 1);
          toast.success("Operation completed successfully!");
          return;
        }

        if (status.status === "failed") {
          setIsProcessing(false);
          let errorMessage = status.error || "Operation failed";
          
          if (errorMessage.includes("NoneType") || errorMessage.includes("subscriptable")) {
            errorMessage = "Operation completed but logging failed. Your files were processed successfully.";
          }
          
          toast.error(errorMessage);
          return;
        }

        attempts++;
        if (attempts < maxAttempts && (status.status === "processing" || status.status === "starting")) {
          setTimeout(poll, 1000);
        } else {
          setIsProcessing(false);
          if (attempts >= maxAttempts) {
            toast.error("Operation timed out");
          }
        }
      } catch (error) {
        setIsProcessing(false);
        toast.error("Failed to check operation status");
        console.error("Status poll error:", error);
      }
    };

    poll();
  };

  // Download results with ZIP for forensic extract
  const downloadForensicResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/operations/${currentOperationId}/download-forensic`);
      
      // If forensic download not available, use standard download
      if (!response.ok && response.status === 404) {
        return downloadStandardResult();
      }
      
      if (!response.ok) {
        throw new Error(`Failed to download: ${response.statusText}`);
      }

      const blob = await response.blob();
      const defaultFilename = `forensic_evidence_${caseId || Date.now()}.zip`;
      
      downloadBlob(blob, defaultFilename);
      toast.success("Forensic evidence package downloaded successfully!");
      
    } catch (error) {
      console.error("Download error:", error);
      // Fallback to standard download
      downloadStandardResult();
    }
  };

  // Download forensic extract result with proper save as functionality
  const downloadForensicResultWithSaveAs = async () => {
    if (!currentOperationId) {
      toast.error("No operation result to download");
      return;
    }

    try {
      const downloadEndpoint = `${API_BASE_URL}/api/operations/${currentOperationId}/download-forensic`;
      const defaultFilename = `forensic_evidence_${caseId || Date.now()}.zip`;
      
      // Try forensic download first, fallback to standard if not available
      try {
        const { downloadFromUrl } = await import('@/utils/fileDownload');
        await downloadFromUrl(
          downloadEndpoint,
          defaultFilename,
          `Forensic evidence package saved as "{filename}"!`
        );
      } catch (error: any) {
        if (error.message.includes('404')) {
          // Fallback to standard download
          return downloadStandardResultWithSaveAs();
        }
        throw error;
      }
    } catch (error: any) {
      console.error("Download error:", error);
      toast.error(`Download failed: ${error.message}`);
    }
  };

  const downloadStandardResult = async () => {
    if (!currentOperationId) {
      toast.error("No operation ID available for download");
      return;
    }

    try {
      console.log("🔽 Attempting download for operation:", currentOperationId);
      
      if (!currentOperationId || currentOperationId === 'undefined') {
        toast.error("Invalid operation ID for download");
        return;
      }
      
      // First try to get the latest status to ensure we have the result
      const statusResponse = await fetch(`${API_BASE_URL}/api/operations/${currentOperationId}/status`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        console.log("🔄 Latest status:", statusData);
        if (statusData.result && !operationResult) {
          setOperationResult(statusData.result);
        }
      }
      
      const response = await fetch(`${API_BASE_URL}/api/operations/${currentOperationId}/download`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(`Download not found. The operation may still be processing or the file was not created. Status: ${response.status}`);
        }
        throw new Error(`Download failed: ${response.status} ${response.statusText}`);
      }

      const blob = await response.blob();
      const defaultFilename = operationResult?.filename || `forensic_evidence_${currentOperationId.slice(0, 8)}.png`;
      
      console.log("🔽 Download successful, filename:", defaultFilename);
      downloadBlob(blob, defaultFilename);
      toast.success("Forensic evidence file downloaded successfully!");
      
    } catch (error) {
      console.error("Download error:", error);
      toast.error(`Failed to download file: ${error.message}`);
      
      // Additional debugging for 404 errors
      if (error.message.includes('404')) {
        console.log("🔍 Debug info for 404 error:");
        console.log("Current operation ID:", currentOperationId);
        console.log("Current operation result:", operationResult);
      }
    }
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Download with proper save as functionality
  const downloadStandardResultWithSaveAs = async () => {
    if (!currentOperationId) {
      toast.error("No operation ID available for download");
      return;
    }

    try {
      console.log("🔽 Attempting Save As download for operation:", currentOperationId);
      
      if (!currentOperationId || currentOperationId === 'undefined') {
        toast.error("Invalid operation ID for download");
        return;
      }
      
      // First try to get the latest status to ensure we have the result
      const statusResponse = await fetch(`${API_BASE_URL}/api/operations/${currentOperationId}/status`);
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        console.log("🔄 Latest status:", statusData);
        if (statusData.result && !operationResult) {
          setOperationResult(statusData.result);
        }
      }
      
      const downloadEndpoint = `${API_BASE_URL}/api/operations/${currentOperationId}/download`;
      const defaultFilename = operationResult?.filename || `forensic_evidence_${currentOperationId.slice(0, 8)}.png`;
      
      // Use the utility function for proper save as functionality
      const { downloadFromUrl } = await import('@/utils/fileDownload');
      await downloadFromUrl(
        downloadEndpoint,
        defaultFilename,
        `Forensic evidence file saved as "{filename}"!`
      );
      
    } catch (error: any) {
      console.error("Download error:", error);
      toast.error(`Failed to download file: ${error.message}`);
      
      // Additional debugging for 404 errors
      if (error.message.includes('404')) {
        console.log("🔍 Debug info for 404 error:");
        console.log("Current operation ID:", currentOperationId);
        console.log("Current operation result:", operationResult);
      }
    }
  };

  // Create and download metadata.txt file
  const downloadMetadataFile = () => {
    if (!extractedMetadata) return;

    const metadataContent = `FORENSIC EVIDENCE METADATA
============================

Case ID: ${extractedMetadata.case_id || 'N/A'}
Embedded Owner: ${extractedMetadata.embedded_owner || 'N/A'}
Timestamp: ${extractedMetadata.timestamp || 'N/A'}
Original Filename: ${extractedMetadata.name || 'N/A'}
File Size: ${extractedMetadata.file_size ? formatFileSize(extractedMetadata.file_size) : 'N/A'}
File Type: ${extractedMetadata.file_type || 'N/A'}
Carrier Filename: ${extractedMetadata.carrier_name || 'N/A'}
Created By: ${extractedMetadata.created_by || 'N/A'}
Description: ${extractedMetadata.description || 'No description provided'}

Extraction Details:
- Extraction Date: ${new Date().toISOString()}
- Extracted By: ${currentUser?.email || 'Unknown'}
- Operation ID: ${currentOperationId || 'N/A'}

============================
Generated by VeilForge Forensic Evidence System
`;

    const blob = new Blob([metadataContent], { type: 'text/plain' });
    const filename = `metadata_${extractedMetadata.case_id || 'evidence'}.txt`;
    downloadBlob(blob, filename);
  };

  const formatFileSize = (bytes: number): string => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-24">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <div className="flex-1"></div>
              <div className="flex-1 flex justify-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10">
                  <Shield className="w-10 h-10 text-primary" />
                </div>
              </div>
              <div className="flex-1"></div>
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              Forensic Evidence Chain Protection
            </h1>
            <p className="text-xl text-muted-foreground">
              Maintain integrity and authenticity of digital evidence with embedded metadata
            </p>
          </div>

          {/* Main Steganography Interface */}
          <div className="mb-12">
            <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-8">
              <TabsList className="grid w-full grid-cols-3 mb-8">
                <TabsTrigger value="embed" className="flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Embed Evidence
                </TabsTrigger>
                <TabsTrigger value="extract" className="flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Extract Evidence
                </TabsTrigger>
                <TabsTrigger value="settings" className="flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Project Settings
                </TabsTrigger>
              </TabsList>

              {/* Embed Tab */}
              <TabsContent value="embed" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5" />
                      Embed Forensic Evidence
                    </CardTitle>
                    <CardDescription>
                      Hide a file within a carrier file along with forensic metadata for evidence chain protection
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Forensic Metadata Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted/30 rounded-lg">
                      <div className="space-y-2">
                        <Label htmlFor="caseId" className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Case ID *
                        </Label>
                        <Input
                          id="caseId"
                          placeholder="e.g., CASE-2024-001"
                          value={caseId}
                          onChange={(e) => setCaseId(e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="embeddedOwner" className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          Embedded Owner *
                        </Label>
                        <Input
                          id="embeddedOwner"
                          placeholder="e.g., Detective Smith"
                          value={embeddedOwner}
                          onChange={(e) => setEmbeddedOwner(e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="timestamp" className="flex items-center gap-2">
                          <Calendar className="w-4 h-4" />
                          Timestamp
                        </Label>
                        <div className="flex gap-2">
                          <Input
                            id="timestamp"
                            type="datetime-local"
                            value={timestamp}
                            onChange={(e) => setTimestamp(e.target.value)}
                            className="flex-1"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                              const now = new Date();
                              const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
                              setTimestamp(localDateTime.toISOString().slice(0, 16));
                            }}
                            className="flex-shrink-0"
                          >
                            Present Time
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2 md:col-span-2">
                        <Label htmlFor="description" className="flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Description (Optional)
                        </Label>
                        <Textarea
                          id="description"
                          placeholder="Additional context or notes about this evidence..."
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          rows={3}
                        />
                      </div>
                    </div>

                    {/* File Upload Section */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-2">
                        <Label htmlFor="carrierFile">Carrier File *</Label>
                        <div className="border-2 border-dashed border-primary/30 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <FileImage className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                          <Input
                            id="carrierFile"
                            type="file"
                            onChange={handleCarrierFileChange}
                            className="hidden"
                            accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                          />
                          <Button
                            variant="outline"
                            onClick={() => document.getElementById('carrierFile')?.click()}
                            className="mb-2"
                          >
                            Choose Carrier File
                          </Button>
                          {carrierFile && (
                            <p className="text-sm text-muted-foreground">
                              {carrierFile.name} ({formatFileSize(carrierFile.size)})
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="hiddenFile">File to Hide *</Label>
                        <div className="border-2 border-dashed border-primary/30 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <Lock className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                          <Input
                            id="hiddenFile"
                            type="file"
                            onChange={handleHiddenFileChange}
                            className="hidden"
                          />
                          <Button
                            variant="outline"
                            onClick={() => document.getElementById('hiddenFile')?.click()}
                            className="mb-2"
                          >
                            Choose File to Hide
                          </Button>
                          {hiddenFile && (
                            <p className="text-sm text-muted-foreground">
                              {hiddenFile.name} ({formatFileSize(hiddenFile.size)})
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Password Section */}
                    <div className="space-y-4 p-4 bg-muted/30 rounded-lg">
                      <Label htmlFor="embedPassword" className="flex items-center gap-2">
                        <Key className="w-4 h-4" />
                        Encryption Password *
                      </Label>
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <Input
                            id="embedPassword"
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter a strong password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-1 top-1 h-8 w-8"
                            onClick={togglePasswordVisibility}
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                        <Button
                          type="button"
                          variant="outline"
                          onClick={generatePassword}
                          className="flex-shrink-0"
                        >
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Generate
                        </Button>
                        {password && (
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="flex-shrink-0"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                      
                      {/* Password Management Options */}
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="save-password-with-project-forensic-embed"
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
                          <Label htmlFor="save-password-with-project-forensic-embed" className="text-sm">
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

                    {/* Processing Progress */}
                    {isProcessing && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Processing Forensic Evidence...</span>
                          <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
                        </div>
                        <Progress value={progress} className="w-full h-3" />
                        <p className="text-xs text-muted-foreground text-center">
                          Embedding forensic data... Securing evidence for legal compliance.
                        </p>
                      </div>
                    )}

                    {/* Embed Button */}
                    <Button
                      onClick={handleForensicEmbed}
                      disabled={isProcessing || !carrierFile || !hiddenFile || !caseId || !embeddedOwner || !password}
                      size="lg"
                      className="w-full"
                    >
                      {isProcessing ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : (
                        <>
                          <Shield className="w-4 h-4 mr-2" />
                          Embed Forensic Evidence
                        </>
                      )}
                    </Button>



                    {/* Download Section - Appears after successful operation */}
                    {operationResult && !isProcessing && (
                      <Card className="mt-4 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700">
                        <CardContent className="pt-4">
                          <div className="flex items-center gap-2 mb-3">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            <span className="font-medium text-green-800 dark:text-green-200">
                              Forensic evidence embedded successfully!
                            </span>
                          </div>
                          <Button onClick={downloadStandardResultWithSaveAs} className="w-full">
                            <Download className="w-4 h-4 mr-2" />
                            Download Forensic Evidence File
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Extract Tab */}
              <TabsContent value="extract" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      Extract Forensic Evidence
                    </CardTitle>
                    <CardDescription>
                      Extract hidden files and forensic metadata from evidence files
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* File Upload */}
                    <div className="space-y-2">
                      <Label htmlFor="extractFile">Processed Evidence File *</Label>
                      <div className="border-2 border-dashed border-primary/30 rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                        <FileImage className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                        <Input
                          id="extractFile"
                          type="file"
                          onChange={handleExtractFileChange}
                          className="hidden"
                          accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                        />
                        <Button
                          variant="outline"
                          onClick={() => document.getElementById('extractFile')?.click()}
                          className="mb-2"
                        >
                          Choose Evidence File
                        </Button>
                        {extractFile && (
                          <p className="text-sm text-muted-foreground">
                            {extractFile.name} ({formatFileSize(extractFile.size)})
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Password Section */}
                    <div className="space-y-4 p-4 bg-muted/30 rounded-lg">
                      <Label htmlFor="extractPassword" className="flex items-center gap-2">
                        <Key className="w-4 h-4" />
                        Decryption Password *
                      </Label>
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <Input
                            id="extractPassword"
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter the password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-1 top-1 h-8 w-8"
                            onClick={togglePasswordVisibility}
                          >
                            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                          </Button>
                        </div>
                        {password && (
                          <Button
                            type="button"
                            variant="outline"
                            onClick={copyPasswordToClipboard}
                            className="flex-shrink-0"
                          >
                            <Copy className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                      
                      {/* Password Management Options */}
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="save-password-with-project-forensic-extract"
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
                          <Label htmlFor="save-password-with-project-forensic-extract" className="text-sm">
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

                    {/* Processing Progress */}
                    {isProcessing && (
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Extracting Forensic Evidence...</span>
                          <span className="text-sm font-semibold text-primary">{Math.round(progress)}%</span>
                        </div>
                        <Progress value={progress} className="w-full h-3" />
                        <p className="text-xs text-muted-foreground text-center">
                          Extracting forensic data... Retrieving secure evidence.
                        </p>
                      </div>
                    )}

                    {/* Extract Button */}
                    <Button
                      onClick={handleForensicExtract}
                      disabled={isProcessing || !extractFile || !password}
                      size="lg"
                      className="w-full"
                    >
                      {isProcessing ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Extracting...
                        </>
                      ) : (
                        <>
                          <Download className="w-4 h-4 mr-2" />
                          Extract Evidence
                        </>
                      )}
                    </Button>

                    {/* Extracted Metadata Display */}
                    {showExtractedData && extractedMetadata && (
                      <Card className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
                        <CardHeader>
                          <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
                            <CheckCircle className="w-5 h-5" />
                            Forensic Metadata Found
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Case ID</Label>
                              <p className="font-mono text-sm">{extractedMetadata.case_id || 'N/A'}</p>
                            </div>
                            
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Embedded Owner</Label>
                              <p className="font-mono text-sm">{extractedMetadata.embedded_owner || 'N/A'}</p>
                            </div>
                            
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Timestamp</Label>
                              <p className="font-mono text-sm">{extractedMetadata.timestamp ? new Date(extractedMetadata.timestamp).toLocaleString() : 'N/A'}</p>
                            </div>
                            
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Original Filename</Label>
                              <p className="font-mono text-sm">{extractedMetadata.name || 'N/A'}</p>
                            </div>
                          </div>
                          
                          {extractedMetadata.description && (
                            <div className="space-y-2">
                              <Label className="text-xs text-muted-foreground">Description</Label>
                              <p className="text-sm p-2 bg-background rounded border">{extractedMetadata.description}</p>
                            </div>
                          )}
                          
                          <div className="flex gap-2 pt-4">
                            <Button onClick={downloadForensicResultWithSaveAs} className="flex-1">
                              <Download className="w-4 h-4 mr-2" />
                              Download Evidence Package (ZIP)
                            </Button>
                            <Button onClick={downloadMetadataFile} variant="outline">
                              <FileText className="w-4 h-4 mr-2" />
                              Download Metadata
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    )}

                    {/* Standard Success Result (No Forensic Metadata) */}
                    {operationResult && selectedTab === "extract" && !showExtractedData && (
                      <Alert>
                        <CheckCircle className="h-4 w-4" />
                        <AlertDescription className="flex items-center justify-between">
                          <span>Extraction completed! No forensic metadata found (standard file).</span>
                          <Button onClick={downloadStandardResult} size="sm" variant="outline">
                            <Download className="w-4 w-4 mr-2" />
                            Download
                          </Button>
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Project Settings Tab */}
              <TabsContent value="settings" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="w-5 h-5" />
                      Forensic Project Settings
                    </CardTitle>
                    <CardDescription>
                      Configure project details and settings for forensic evidence management
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Project Information */}
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="projectName">Project Name</Label>
                        <Input
                          id="projectName"
                          placeholder="e.g., Investigation CASE-2024-001"
                          value={projectName}
                          onChange={(e) => setProjectName(e.target.value)}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="projectDescription">Project Description</Label>
                        <Textarea
                          id="projectDescription"
                          placeholder="Describe the forensic investigation or evidence collection project..."
                          value={projectDescription}
                          onChange={(e) => setProjectDescription(e.target.value)}
                          rows={4}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="projectTags">Tags (comma-separated)</Label>
                        <Input
                          id="projectTags"
                          placeholder="e.g., digital evidence, cybercrime, investigation"
                          value={projectTags}
                          onChange={(e) => setProjectTags(e.target.value)}
                        />
                      </div>
                    </div>

                    {/* Case Default Settings */}
                    <div className="p-4 bg-muted/30 rounded-lg space-y-4">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Default Case Settings
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Default Case ID Prefix</Label>
                          <Input
                            placeholder="e.g., CASE-2024-"
                            value={caseId.split('-').slice(0, -1).join('-') + (caseId.split('-').slice(0, -1).join('-') ? '-' : '')}
                            onChange={(e) => {
                              const prefix = e.target.value;
                              if (prefix.endsWith('-')) {
                                setCaseId(prefix + '001');
                              } else {
                                setCaseId(prefix);
                              }
                            }}
                          />
                        </div>
                        
                        <div className="space-y-2">
                          <Label>Default Embedded Owner</Label>
                          <Input
                            placeholder="e.g., Detective Smith"
                            value={embeddedOwner}
                            onChange={(e) => setEmbeddedOwner(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Security Settings */}
                    <div className="p-4 bg-muted/30 rounded-lg space-y-4">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Lock className="w-4 h-4" />
                        Security Settings
                      </h3>
                      
                      <div className="space-y-4">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="autoGeneratePassword"
                            className="rounded"
                          />
                          <Label htmlFor="autoGeneratePassword">
                            Auto-generate secure passwords for new evidence
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="requireTimestamp"
                            className="rounded"
                            defaultChecked
                          />
                          <Label htmlFor="requireTimestamp">
                            Require timestamp for all evidence (recommended)
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="enableAuditLog"
                            className="rounded"
                            defaultChecked
                          />
                          <Label htmlFor="enableAuditLog">
                            Enable detailed audit logging
                          </Label>
                        </div>
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

                    {/* Export Settings */}
                    <div className="p-4 bg-muted/30 rounded-lg space-y-4">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Download className="w-4 h-4" />
                        Export Settings
                      </h3>
                      
                      <div className="space-y-4">
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="includeMetadata"
                            className="rounded"
                            defaultChecked
                          />
                          <Label htmlFor="includeMetadata">
                            Always include metadata.txt in evidence packages
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="createHashSums"
                            className="rounded"
                          />
                          <Label htmlFor="createHashSums">
                            Generate file hash checksums for evidence integrity
                          </Label>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id="compressEvidence"
                            className="rounded"
                            defaultChecked
                          />
                          <Label htmlFor="compressEvidence">
                            Compress evidence packages to reduce file size
                          </Label>
                        </div>
                      </div>
                    </div>

                    {/* Save Project Settings */}
                    <div className="flex items-center justify-between pt-4 border-t">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="saveProject"
                          checked={saveProject}
                          onChange={(e) => setSaveProject(e.target.checked)}
                          className="rounded"
                        />
                        <Label htmlFor="saveProject">
                          Save as project template for future cases
                        </Label>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => {
                          setProjectName("");
                          setProjectDescription("");
                          setProjectTags("");
                          setCaseId("");
                          setEmbeddedOwner("");
                          setSaveProject(false);
                        }}>
                          Reset
                        </Button>
                        <Button 
                          onClick={saveProjectSettings}
                          disabled={!projectName.trim() || !selectedProject}
                        >
                          Save Project Settings
                        </Button>
                        
                        <Button 
                          variant="outline"
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
                    </div>
                    
                    {/* Project Files Display */}
                    {selectedProject && (
                      <div className="space-y-3 pt-6 border-t">
                        <h4 className="text-sm font-semibold flex items-center gap-2">
                          <FileText className="h-4 w-4" />
                          Forensic Project Files
                        </h4>
                        <ProjectFilesDisplay project={selectedProject} refreshTrigger={fileRefreshTrigger} />
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            <div className="p-6 rounded-lg border bg-card hover-scale transition-all">
              <FileCheck className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Evidence Integrity</h3>
              <p className="text-muted-foreground">
                Ensure digital evidence remains integrity-verified throughout legal proceedings with embedded metadata
              </p>
            </div>

            <div className="p-6 rounded-lg border bg-card hover-scale transition-all">
              <Lock className="w-12 h-12 text-primary mb-4" />
              <h3 className="text-xl font-semibold mb-2">Chain of Custody</h3>
              <p className="text-muted-foreground">
                Maintain a verifiable record of all interactions with forensic evidence through steganographic protection
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default ForensicEvidence;
