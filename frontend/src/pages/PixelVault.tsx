import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Lock, Key, Eye, EyeOff, Shield, Binary, Upload, FileText, Image as ImageIcon, File, Music, Video, Download, CheckCircle, Settings, Sparkles, Palette, Wand2, Lightbulb, Copy, Save, RefreshCw } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

// API Service Integration
// Use environment variable for production deployment
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

// Helper function to clean filenames for display
const cleanFilenameForDisplay = (filename: string): string => {
 if (!filename) return 'embedded_file';
 
 // Extract extension
 const extension = filename.split('.').pop()?.toLowerCase() || '';
 const nameWithoutExt = filename.replace(/\.[^.]*$/, '');
 
 // Clean the name
 let baseName = nameWithoutExt;
 
 // Remove prefixes
 baseName = baseName.replace(/^(stego_|carrier_|content_)/, '');
 
 // Remove timestamp_uuid patterns
 baseName = baseName.replace(/_\d{10}_[a-f0-9]{8}/g, '');
 
 // Remove extra underscores
 baseName = baseName.replace(/_+/g, '_').replace(/^_|_$/g, '');
 
 // Ensure we have a name
 if (!baseName || baseName.length < 2) {
 baseName = 'embedded_file';
 }
 
 return extension ? `${baseName}.${extension}` : baseName;
};

export default function PixelVault() {
 const navigate = useNavigate();
 const location = useLocation();
 const { toast } = useToast();
 
 // State management
 const [user, setUser] = useState<any>(null);
 const [processedImage, setProcessedImage] = useState<string | null>(null);
 const [processedImageFile, setProcessedImageFile] = useState<string | null>(null);
 const [selectedTab, setSelectedTab] = useState("embed");
 
 // Text-to-image generation state
 const [inputPrompt, setInputPrompt] = useState("");
 const [generatedImage, setGeneratedImage] = useState<string | null>(null);
 const [generatedImageFile, setGeneratedImageFile] = useState<string | null>(null);
 const [generatedImages, setGeneratedImages] = useState<string[]>([]);
 const [imageSize, setImageSize] = useState<{width: number, height: number, fileSize: number} | null>(null);
 
 // Embed/Extract common state
 const [contentType, setContentType] = useState("text");
 const [textContent, setTextContent] = useState("");
 const [fileContent, setFileContent] = useState<File | null>(null);
 const [password, setPassword] = useState("");
 const [encryptionEnabled, setEncryptionEnabled] = useState(false); // Made optional as requested
 const [isProcessing, setIsProcessing] = useState(false);
 const [progress, setProgress] = useState(0);
 
 // Batch processing state
 const [batchMode, setBatchMode] = useState(false);
 

 const [batchCount, setBatchCount] = useState(3);
 const [generatedCarrierFiles, setGeneratedCarrierFiles] = useState<File[]>([]);
 
 // Advanced password management
 const [showPassword, setShowPassword] = useState(false);
 const [savePasswordWithProject, setSavePasswordWithProject] = useState(false);
 const [savedPassword, setSavedPassword] = useState("");
 
 // Extract state
 const [extractFile, setExtractFile] = useState<File | null>(null);
 const [extractedContent, setExtractedContent] = useState<any>(null);
 const [extractionFailed, setExtractionFailed] = useState(false);
 const [extractionError, setExtractionError] = useState<string>("");
 
 // Project state
 const [projectName, setProjectName] = useState("");
 const [projectDescription, setProjectDescription] = useState("");
 const [projectTags, setProjectTags] = useState("");
 const [selectedProject, setSelectedProject] = useState<any>(null);
 const [projects, setProjects] = useState<any[]>([]);
 
 // File management state
 const [embeddedResult, setEmbeddedResult] = useState<any>(null);
 const [downloadableFiles, setDownloadableFiles] = useState<any[]>([]);
 const [saveProject, setSaveProject] = useState(false);

 useEffect(() => {
 window.scrollTo(0, 0);
 
 const initializeComponent = async () => {
 try {
 // Check authentication
 const { data: { user } } = await supabase.auth.getUser();
 if (!user) {
 navigate("/auth");
 return;
 }
 setUser(user);

 // Handle newly created project from dashboard
 if (location.state?.newProject && location.state?.projectJustCreated) {
 console.log('📦 New PixelVault project received from dashboard:', location.state.newProject);
 setSelectedProject(location.state.newProject);
 setProjectName(location.state.newProject.name);
 setProjectDescription(location.state.newProject.description || "");
 setProjects([location.state.newProject]);
 toast({
 title: "Welcome!",
 description: `Welcome to your new ${location.state.newProject.project_type} project!`,
 });
 }
 
 // Handle existing project being opened from dashboard
 if (location.state?.existingProject && location.state?.projectToOpen) {
 console.log('🔓 Opening existing PixelVault project:', location.state.existingProject);
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
 console.log('📋 Restoring PixelVault project metadata:', metadata);
 const meta = metadata as any;
 
 // PixelVault project settings
 if (meta.tags) setProjectTags(meta.tags);
 
 // Image generation settings
 if (meta.inputPrompt) setInputPrompt(meta.inputPrompt);
 if (meta.generatedImages) {
   // Convert relative URLs to full URLs for display
   const fullUrls = meta.generatedImages.map((url: string) => 
     url.startsWith('/api/') ? `${API_BASE_URL}${url}` : url
   );
   setGeneratedImages(fullUrls);
 }
 if (meta.generatedImage) {
   // Convert relative URL to full URL for display
   const fullUrl = meta.generatedImage.startsWith('/api/') 
     ? `${API_BASE_URL}${meta.generatedImage}` 
     : meta.generatedImage;
   setGeneratedImage(fullUrl);
 }
 if (meta.generatedImageFile) setGeneratedImageFile(meta.generatedImageFile);
 if (meta.processedImage) {
   // Convert relative URL to full URL for display
   const fullUrl = meta.processedImage.startsWith('/api/') 
     ? `${API_BASE_URL}${meta.processedImage}` 
     : meta.processedImage;
   setProcessedImage(fullUrl);
 }
 if (meta.processedImageFile) setProcessedImageFile(meta.processedImageFile);
 
 // Embedding settings
 if (meta.contentType) setContentType(meta.contentType);
 if (meta.textContent) setTextContent(meta.textContent);
 
 // Security settings
 if (meta.password && meta.savePasswordWithProject) {
 setPassword(meta.password);
 setSavePasswordWithProject(meta.savePasswordWithProject);
 }
 if (meta.encryptionEnabled !== undefined) setEncryptionEnabled(meta.encryptionEnabled);
 
 // UI preferences
 if (meta.showPassword !== undefined) setShowPassword(meta.showPassword);
 if (meta.batchMode !== undefined) setBatchMode(meta.batchMode);
 if (meta.batchCount) setBatchCount(meta.batchCount);
 
 // Last operation results
 if (meta.embeddedResult) setEmbeddedResult(meta.embeddedResult);
 if (meta.extractedContent) setExtractedContent(meta.extractedContent);
 }
 
 toast({
 title: "Project Loaded",
 description: `Opened project: ${project.name}`,
 });
 }

 } catch (error) {
 console.error('❌ Error initializing PixelVault component:', error);
 toast({
 title: "Error",
 description: "Failed to initialize PixelVault",
 variant: "destructive",
 });
 }
 };

 initializeComponent();
 }, [navigate, location.state]);

 // Password management functions
 const generatePassword = () => {
 const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
 let result = '';
 for (let i = 0; i < 12; i++) {
 result += chars.charAt(Math.floor(Math.random() * chars.length));
 }
 setPassword(result);
 toast({
 title: "Password Generated",
 description: "Secure password created and copied to clipboard!",
 });
 navigator.clipboard.writeText(result);
 };

 const togglePasswordVisibility = () => setShowPassword(!showPassword);

 const copyPasswordToClipboard = () => {
 if (password) {
 navigator.clipboard.writeText(password);
 toast({
 title: "Copied",
 description: "Password copied to clipboard!",
 });
 }
 };

 const loadSavedPassword = () => {
 if (savedPassword) {
 setPassword(savedPassword);
 toast({
 title: "Password Loaded",
 description: "Saved password has been loaded!",
 });
 }
 };

 // Text-to-image generation
 const handleGenerate = async () => {
 if (!inputPrompt.trim()) {
 toast({
 title: "Error",
 description: "Please enter a prompt for image generation",
 variant: "destructive",
 });
 return;
 }

 setIsProcessing(true);
 setProgress(0);
 
 try {
 // Simulate progress
 const progressInterval = setInterval(() => {
 setProgress(prev => {
 if (prev >= 90) {
 clearInterval(progressInterval);
 return 90;
 }
 return prev + 10;
 });
 }, 200);

 if (batchMode) {
 // Generate multiple images for batch processing
 const imagePromises = [];
 for (let i = 0; i < batchCount; i++) {
 const promise = fetch(`${API_BASE_URL}/api/generate-image`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({
 prompt: inputPrompt + ` (variant ${i + 1})`,
 project_name: projectName || undefined,
 project_description: projectDescription || undefined,
 }),
 });
 imagePromises.push(promise);
 }

 const responses = await Promise.all(imagePromises);
 const images = [];
 const files = [];

 for (const response of responses) {
 const data = await response.json();
 if (data.success && data.image_url) {
 // Create full URL for the image
 const fullImageUrl = data.image_url.startsWith('http') 
   ? data.image_url 
   : `${API_BASE_URL}${data.image_url}`;
 images.push(fullImageUrl);
 // Convert image URL to Blob for batch embedding
 const imageResponse = await fetch(fullImageUrl);
 const blob = await imageResponse.blob();
 // Create a File-like object with required properties
 const file = Object.assign(blob, {
 name: `generated_${Date.now()}_${Math.random()}.png`,
 lastModified: Date.now(),
 webkitRelativePath: ''
 }) as File;
 files.push(file);
 }
 }

 setGeneratedImages(images);
 setGeneratedCarrierFiles(files);
 setGeneratedImage(images[0] || null);
 
 // Auto-save to project if one is selected after batch generation
 if (selectedProject && projectName.trim()) {
 console.log('🔄 Auto-saving project after batch image generation...');
 setTimeout(() => {
 saveProjectSettings().catch(error => {
 console.error('Auto-save after batch generation failed:', error);
 });
 }, 100);
 }

 clearInterval(progressInterval);
 setProgress(100);

 toast({
 title: "Success",
 description: `Generated ${images.length} images for batch processing!`,
 });
 } else {
 // Single image generation
 const response = await fetch(`${API_BASE_URL}/api/generate-image`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({
 prompt: inputPrompt,
 project_name: projectName || undefined,
 project_description: projectDescription || undefined,
 }),
 });

 const data = await response.json();
 
 clearInterval(progressInterval);
 setProgress(100);

 if (data.success) {
 // Create full URL for the image
 const fullImageUrl = data.image_url.startsWith('http') 
   ? data.image_url 
   : `${API_BASE_URL}${data.image_url}`;
 setGeneratedImage(fullImageUrl);
 setGeneratedImageFile(data.image_filename);
 
 // Get image info for capacity display
 getImageInfo(fullImageUrl);
 
 // Add the generated image to the images array for project saving
 setGeneratedImages(prev => {
 const updated = [...prev];
 if (!updated.includes(fullImageUrl)) {
 updated.push(fullImageUrl);
 }
 return updated;
 });
 
 // Auto-save to project if one is selected after single image generation
 if (selectedProject && projectName.trim()) {
 console.log('🔄 Auto-saving project after single image generation...');
 setTimeout(() => {
 saveProjectSettings().catch(error => {
 console.error('Auto-save after single image generation failed:', error);
 });
 }, 100);
 }
 
 toast({
 title: "Success",
 description: "Image generated successfully!",
 });
 } else {
 throw new Error(data.detail || 'Generation failed');
 }
 }
 } catch (error: any) {
 toast({
 title: "Error",
 description: error.message || "Failed to generate image",
 variant: "destructive",
 });
 } finally {
 setIsProcessing(false);
 }
 };

 // Get image information for capacity estimation
 const getImageInfo = async (imageUrl: string) => {
 try {
 const response = await fetch(imageUrl);
 const blob = await response.blob();
 
 return new Promise<{width: number, height: number, fileSize: number}>((resolve) => {
 const img = new Image();
 img.onload = () => {
 const info = {
 width: img.width,
 height: img.height,
 fileSize: blob.size
 };
 setImageSize(info);
 resolve(info);
 };
 img.src = imageUrl;
 });
 } catch (error) {
 console.error('Failed to get image info:', error);
 return null;
 }
 };

 // File upload handlers
 const handleContentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
 if (e.target.files && e.target.files[0]) {
 setFileContent(e.target.files[0]);
 }
 };

 const handleExtractFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
 if (e.target.files && e.target.files[0]) {
 setExtractFile(e.target.files[0]);
 }
 };

 // Embed functionality
 const handleEmbed = async () => {
 // Validation for batch vs single mode
 if (batchMode) {
 if (!generatedCarrierFiles || generatedCarrierFiles.length === 0) {
 toast({
 title: "Error",
 description: "Please generate images for batch processing first",
 variant: "destructive",
 });
 return;
 }
 } else {
 if (!generatedImage) {
 toast({
 title: "Error",
 description: "Please generate an image first",
 variant: "destructive",
 });
 return;
 }
 }

 if (contentType === "text" && !textContent.trim()) {
 toast({
 title: "Error",
 description: "Please enter text content to hide",
 variant: "destructive",
 });
 return;
 }

 if (contentType !== "text" && !fileContent) {
 toast({
 title: "Error",
 description: "Please select a file to hide",
 variant: "destructive",
 });
 return;
 }

 if (encryptionEnabled && !password.trim()) {
 toast({
 title: "Error",
 description: "Please enter a password for encryption",
 variant: "destructive",
 });
 return;
 }

 setIsProcessing(true);
 setProgress(0);

 try {
 const formData = new FormData();
 
 if (batchMode) {
 // Add all generated carrier files for batch processing
 generatedCarrierFiles.forEach((file, index) => {
 formData.append('carrier_files', file);
 });
 } else {
 // Single file processing - Get the generated image as a file
 const imageResponse = await fetch(generatedImage);
 const imageBlob = await imageResponse.blob();
 // Create a File-like object with required properties
 const imageFile = Object.assign(imageBlob, {
 name: generatedImageFile || 'generated_image.png',
 lastModified: Date.now(),
 webkitRelativePath: ''
 }) as File;
 
 formData.append('carrier_file', imageFile);
 formData.append('carrier_type', 'image');
 }
 
 formData.append('content_type', contentType);
 
 if (contentType === "text") {
 formData.append('text_content', textContent);
 } else {
 formData.append('content_file', fileContent as File);
 }
 
 formData.append('password', encryptionEnabled ? password : '');
 formData.append('encryption_type', 'aes-256-gcm');

 // Add project information if provided
 if (projectName.trim()) {
 formData.append('project_name', projectName.trim());
 }
 if (projectDescription.trim()) {
 formData.append('project_description', projectDescription.trim());
 }

 // Simulate progress
 const progressInterval = setInterval(() => {
 setProgress(prev => {
 if (prev >= 90) {
 clearInterval(progressInterval);
 return 90;
 }
 return prev + 15;
 });
 }, 300);

 // Choose endpoint based on mode
 const endpoint = batchMode ? `${API_BASE_URL}/api/embed-batch` : `${API_BASE_URL}/api/embed`;
 const response = await fetch(endpoint, {
 method: 'POST',
 body: formData,
 });

 const data = await response.json();
 
 clearInterval(progressInterval);
 setProgress(100);

 if (data.success) {
 // Store the embedding result
 setEmbeddedResult(data);
 
 // Auto-save to project if one is selected
 if (selectedProject && projectName.trim()) {
 console.log('🔄 Auto-saving project after successful embedding...');
 // Delay slightly to ensure state is updated
 setTimeout(() => {
 saveProjectSettings().catch(error => {
 console.error('Auto-save failed:', error);
 });
 }, 100);
 }
 
 toast({
 title: "Success",
 description: batchMode 
 ? `Data embedded in ${generatedCarrierFiles.length} images successfully!`
 : "Data embedded successfully!",
 });

 // Store processed/stego image URL separately (do not overwrite original generated image)
 if (!batchMode && data.output_filename) {
 setProcessedImage(`${API_BASE_URL}/api/download/${data.output_filename}`);
 setProcessedImageFile(data.output_filename);
 }

 // Save password with project if enabled
 if (savePasswordWithProject && password.trim()) {
 setSavedPassword(password);
 }
 } else {
 throw new Error(data.message || 'Embedding failed');
 }
 } catch (error: any) {
 toast({
 title: "Error",
 description: error.message || "Failed to embed data",
 variant: "destructive",
 });
 } finally {
 setIsProcessing(false);
 }
 };

 // Extract functionality
 const handleExtract = async () => {
 if (!extractFile) {
 toast({
 title: "Error",
 description: "Please select an image to extract from",
 variant: "destructive",
 });
 return;
 }

 setIsProcessing(true);
 setProgress(0);
 setExtractedContent(null); // Clear previous results
 setExtractionFailed(false); // Clear previous failure state
 setExtractionError(""); // Clear previous error message

 try {
 const formData = new FormData();
 formData.append('stego_file', extractFile);
 formData.append('password', password || '');

 // Start extraction operation
 const response = await fetch(`${API_BASE_URL}/api/extract`, {
 method: 'POST',
 body: formData,
 });

 const data = await response.json();
 
 if (data.success && data.operation_id) {
 console.log(`[EXTRACTION] Started operation: ${data.operation_id}`);
 
 // First check immediately in case extraction completed very quickly
 try {
 if (!data.operation_id || data.operation_id === 'undefined') {
 console.error('Invalid operation ID for extraction status check');
 return;
 }
 
 const immediateStatusResponse = await fetch(`${API_BASE_URL}/api/operations/${data.operation_id}/status`);
 if (immediateStatusResponse.ok) {
 const immediateStatusData = await immediateStatusResponse.json();
 console.log('[EXTRACTION] Immediate status check:', immediateStatusData);
 
 if (immediateStatusData.status === 'completed') {
 setProgress(100);
 setIsProcessing(false);
 
 if (immediateStatusData.result) {
 setExtractedContent({
 success: true,
 ...immediateStatusData.result
 });
 toast({
 title: "Success", 
 description: "Data extracted successfully!",
 });
 return; // Exit early, no need to poll
 }
 } else if (immediateStatusData.status === 'failed') {
 setIsProcessing(false);
 setExtractionFailed(true);
 setExtractionError(immediateStatusData.error || 'Extraction failed');
 throw new Error(immediateStatusData.error || 'Extraction failed');
 }
 }
 } catch (immediateError) {
 console.log('[EXTRACTION] Immediate check failed, starting polling:', immediateError);
 }
 
 // If not completed immediately, start polling with shorter intervals
 let pollCount = 0;
 const maxPolls = 10; // Maximum 10 polls (5 seconds total)
 
 const pollInterval = setInterval(async () => {
 try {
 if (!data.operation_id || data.operation_id === 'undefined') {
 console.error('Invalid operation ID for polling, stopping interval');
 clearInterval(pollInterval);
 return;
 }
 
 pollCount++;
 console.log(`[EXTRACTION POLL] Attempt ${pollCount}/${maxPolls} - Checking operation: ${data.operation_id}`);
 
 const statusResponse = await fetch(`${API_BASE_URL}/api/operations/${data.operation_id}/status`);
 
 if (!statusResponse.ok) {
 throw new Error(`Status check failed: ${statusResponse.status}`);
 }
 
 const statusData = await statusResponse.json();
 console.log(`[EXTRACTION POLL] Status:`, statusData.status, 'Progress:', statusData.progress);
 
 if (statusData.progress !== undefined) {
 setProgress(statusData.progress);
 }
 
 if (statusData.status === 'completed') {
 clearInterval(pollInterval);
 setProgress(100);
 setIsProcessing(false);
 
 console.log('[EXTRACTION POLL] Completed! Result:', statusData.result);
 
 if (statusData.result) {
 setExtractedContent({
 success: true,
 ...statusData.result
 });
 toast({
 title: "Success",
 description: "Data extracted successfully!",
 });
 } else {
 throw new Error('No extraction results found');
 }
 } else if (statusData.status === 'failed') {
 clearInterval(pollInterval);
 setIsProcessing(false);
 setExtractionFailed(true);
 setExtractionError(statusData.error || 'Extraction failed');
 throw new Error(statusData.error || 'Extraction failed');
 } else if (pollCount >= maxPolls) {
 // Timeout after max polls - try one final check
 clearInterval(pollInterval);
 console.log('[EXTRACTION POLL] Max polls reached, final status check...');
 
 try {
 if (!data.operation_id || data.operation_id === 'undefined') {
 console.error('Invalid operation ID for final status check');
 return;
 }
 
 const finalStatusResponse = await fetch(`${API_BASE_URL}/api/operations/${data.operation_id}/status`);
 if (finalStatusResponse.ok) {
 const finalStatusData = await finalStatusResponse.json();
 if (finalStatusData.status === 'completed' && finalStatusData.result) {
 setProgress(100);
 setIsProcessing(false);
 setExtractedContent({
 success: true,
 ...finalStatusData.result
 });
 toast({
 title: "Success",
 description: "Data extracted successfully!",
 });
 return;
 }
 }
 } catch (finalError) {
 console.error('[EXTRACTION POLL] Final check failed:', finalError);
 }
 
 setIsProcessing(false);
 setExtractionFailed(true);
 setExtractionError('Extraction timeout - please try again with a shorter message or smaller file');
 throw new Error('Extraction timeout - please try again with a shorter message or smaller file');
 }
 } catch (pollError: any) {
 console.error('[EXTRACTION POLL] Error:', pollError);
 clearInterval(pollInterval);
 setIsProcessing(false);
 throw pollError;
 }
 }, 500); // Poll every 500ms for faster response
 
 } else {
 throw new Error(data.message || 'Failed to start extraction');
 }
 } catch (error: any) {
 setExtractionFailed(true);
 setExtractionError(error.message || "Failed to extract data");
 
 // Enhanced error message for password issues
 let errorTitle = "EXTRACTION FAILED";
 let errorDescription = error.message || "Failed to extract data";
 
 if (error.message && error.message.toLowerCase().includes("password")) {
 errorTitle = "WRONG PASSWORD";
 errorDescription = "PASSWORD INCORRECT OR NO HIDDEN DATA FOUND";
 } else if (error.message && error.message.toLowerCase().includes("no hidden")) {
 errorTitle = "NO HIDDEN MESSAGE";
 errorDescription = "FILE CONTAINS NO HIDDEN DATA OR WRONG PASSWORD";
 }
 
 toast({
 title: errorTitle,
 description: errorDescription,
 variant: "destructive",
 });
 setIsProcessing(false);
 }
 };

 // Save project settings
 const saveProjectSettings = async () => {
 if (!selectedProject || !projectName.trim()) {
 toast({
 title: "Error",
 description: "Please select a project and enter a project name",
 variant: "destructive",
 });
 return;
 }

 try {
 // Create comprehensive metadata object for PixelVault project
 const projectMetadata = {
 // PixelVault specific settings
 tags: projectTags,
 
 // Image generation settings
 inputPrompt: inputPrompt,
 generatedImages: generatedImages,
 generatedImage: generatedImage, // Save current generated image
 generatedImageFile: generatedImageFile, // Save generated image filename
 processedImage: processedImage,
 processedImageFile: processedImageFile,
 
 // Embedding settings
 contentType: contentType,
 textContent: contentType === 'text' ? textContent : '',
 
 // Security settings
 password: savePasswordWithProject ? password : '',
 savePasswordWithProject: savePasswordWithProject,
 encryptionEnabled: encryptionEnabled,
 
 // UI preferences
 showPassword: showPassword,
 batchMode: batchMode,
 batchCount: batchCount,
 
 // Last operation results
 embeddedResult: embeddedResult,
 extractedContent: extractedContent,
 
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
 setProjects(prevProjects => 
 prevProjects.map(p => p.id === selectedProject.id ? data : p)
 );

 toast({
 title: "Success",
 description: "Project settings saved successfully!",
 });
 console.log('✅ PixelVault project settings updated:', data);
 } catch (error: any) {
 console.error('❌ Error saving PixelVault project settings:', error);
 toast({
 title: "Error",
 description: `Failed to save project settings: ${error.message}`,
 variant: "destructive",
 });
 }
 };
 const handleSaveSettings = async () => {
 // If project exists, save to existing project
 if (selectedProject) {
 await saveProjectSettings();
 return;
 }
 
 // Create new project
 if (!projectName.trim()) {
 toast({
 title: "Error",
 description: "Please enter a project name",
 variant: "destructive",
 });
 return;
 }

 try {
 const response = await fetch(`${API_BASE_URL}/api/projects`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({
 name: projectName,
 description: projectDescription,
 project_type: 'pixelvault',
 }),
 });

 const data = await response.json();

 if (data.success) {
 toast({
 title: "Success",
 description: "Project created successfully!",
 });
 // Set the newly created project as selected
 if (data.project) {
 setSelectedProject(data.project);
 setProjects(prev => [...prev, data.project]);
 }
 } else {
 throw new Error(data.message || 'Failed to create project');
 }
 } catch (error: any) {
 toast({
 title: "Error",
 description: error.message || "Failed to create project",
 variant: "destructive",
 });
 }
 };

 // Download embedded file
 const downloadEmbeddedFile = async (result: any) => {
 try {
 let downloadUrl = '';
 
 if (result.output_filename) {
 // Use absolute URL for proper backend access
 downloadUrl = `${API_BASE_URL}/api/download/${result.output_filename}`;
 } else if (result.download_url) {
 if (result.download_url.startsWith('http')) {
 downloadUrl = result.download_url;
 } else if (result.download_url.startsWith('/api/')) {
 downloadUrl = `${API_BASE_URL}${result.download_url}`;
 } else {
 downloadUrl = `${API_BASE_URL}/api${result.download_url}`;
 }
 } else {
 toast({
 title: "Error",
 description: "No download URL available",
 variant: "destructive",
 });
 return;
 }

 // Fetch the file properly to ensure correct format
 console.log('🔄 Fetching file from:', downloadUrl);
 const response = await fetch(downloadUrl);
 
 if (!response.ok) {
 throw new Error(`Download failed: ${response.status} ${response.statusText}`);
 }
 
 // Log response headers for debugging
 console.log('📋 Response headers:');
 response.headers.forEach((value, key) => {
 console.log(` ${key}: ${value}`);
 });
 
 // Get the blob data
 const blob = await response.blob();
 console.log('📦 Blob info:', {
 type: blob.type,
 size: blob.size
 });
 
 // Try to extract filename from Content-Disposition header or use fallback
 let filename = 'embedded_file';
 
 const contentDisposition = response.headers.get('Content-Disposition');
 if (contentDisposition) {
 console.log('📄 Content-Disposition:', contentDisposition);
 const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
 if (filenameMatch) {
 filename = filenameMatch[1].replace(/['"]/g, '');
 }
 } else if (result.output_filename) {
 filename = result.output_filename;
 } else if (result.filename) {
 filename = result.filename;
 }
 
 console.log('📝 Raw filename:', filename);
 
 // Clean up filename - remove excessive timestamps and UUIDs while preserving extension
 let cleanedFilename = filename;
 
 // Extract extension first
 const extension = filename.split('.').pop()?.toLowerCase() || '';
 const nameWithoutExt = filename.replace(/\.[^.]*$/, '');
 
 // Remove excessive prefixes and clean up the name
 let baseName = nameWithoutExt;
 
 // Remove stego_ prefix if present
 baseName = baseName.replace(/^stego_/, '');
 
 // Remove carrier_ prefix if present 
 baseName = baseName.replace(/^carrier_/, '');
 
 // If the name has multiple timestamp_uuid patterns, keep only the original name
 const timestampPattern = /_\d{10}_[a-f0-9]{8}/g;
 const matches = baseName.match(timestampPattern);
 if (matches && matches.length > 1) {
 // Remove all but keep the base name before first timestamp
 baseName = baseName.split('_')[0];
 }
 
 // Ensure we have a reasonable filename
 if (!baseName || baseName.length < 2) {
 baseName = 'embedded_image';
 }
 
 // Reconstruct with proper extension
 const imageExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp'];
 let finalExtension = extension;
 
 if (!finalExtension || !imageExtensions.includes(finalExtension)) {
 // If no proper image extension, try to detect from blob type
 if (blob.type.startsWith('image/')) {
 const mimeToExt = {
 'image/png': 'png',
 'image/jpeg': 'jpg',
 'image/jpg': 'jpg',
 'image/bmp': 'bmp',
 'image/gif': 'gif',
 'image/webp': 'webp'
 };
 finalExtension = mimeToExt[blob.type] || 'png';
 } else {
 finalExtension = 'png'; // Default to PNG for images
 }
 }
 
 // Create final clean filename
 cleanedFilename = `${baseName}.${finalExtension}`;
 
 console.log('🔧 Cleaned filename:', cleanedFilename);
 
 // Use the enhanced download utility with Save As functionality
 console.log('🔄 Using Save As utility for:', cleanedFilename);
 const { downloadFileWithSaveAs } = await import('@/utils/fileDownload');
 await downloadFileWithSaveAs(
 blob, 
 cleanedFilename,
 `Embedded image saved successfully as "{filename}"!`
 );
 
 toast({
 title: "Download Completed",
 description: `Downloaded ${cleanedFilename} successfully!`,
 });
 
 } catch (error: any) {
 console.error('❌ Download error:', error);
 toast({
 title: "Error",
 description: `Failed to download file: ${error.message}`,
 variant: "destructive",
 });
 }
 };

 // Download generated image with Save As functionality
 const downloadGeneratedImage = async () => {
 try {
 if (!generatedImage) {
 toast({
 title: "Error", 
 description: "No generated image available for download",
 variant: "destructive",
 });
 return;
 }

 // Extract filename from the generated image URL
 const urlParts = generatedImage.split('/');
 const filename = urlParts[urlParts.length - 1] || 'generated_image.png';
 
 // Clean up the filename
 const cleanedName = filename.replace(/^generated_/, '') || 'ai_generated_image.png';
 
 console.log('🔄 Downloading generated image:', generatedImage);
 console.log('📁 Suggested filename:', cleanedName);
 
 // Use the utility function for proper save as functionality
 const { downloadFromUrl } = await import('@/utils/fileDownload');
 await downloadFromUrl(
 generatedImage,
 cleanedName,
 `Generated image saved successfully as "{filename}"!`
 );
 
 toast({
 title: "Download Completed",
 description: `Generated image downloaded successfully!`,
 });
 
 } catch (error: any) {
 console.error('❌ Generated image download error:', error);
 toast({
 title: "Error",
 description: `Failed to download generated image: ${error.message}`,
 variant: "destructive",
 });
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
 <div className="min-h-screen bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-gradient-to-br light:from-cyan-50 light:via-blue-50 light:to-purple-50 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900 relative overflow-hidden">
 <Navbar />
 
 {/* Animated Background Elements */}
 <div className="fixed inset-0 pointer-events-none">
 {/* Grid Pattern */}
 <div className="absolute inset-0 opacity-10 dark:opacity-10 light:opacity-5" style={{
 backgroundImage: `linear-gradient(#00B8D9 1px, transparent 1px), linear-gradient(90deg, #00B8D9 1px, transparent 1px)`,
 backgroundSize: '50px 50px'
 }} />
 
 {/* Floating Binary */}
 <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-20 dark:opacity-20 light:opacity-10">
 {[...Array(20)].map((_, i) => (
 <div
 key={i}
 className="absolute text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 font-mono text-xs animate-float"
 style={{
 left: `${Math.random() * 100}%`,
 top: `${Math.random() * 100}%`,
 animationDelay: `${Math.random() * 5}s`,
 animationDuration: `${10 + Math.random() * 10}s`,
 }}
 >
 {Math.random() > 0.5 ? "01010101" : "10101010"}
 </div>
 ))}
 </div>

 {/* Glowing Circuit Lines */}
 <div className="absolute inset-0">
 <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-[#00B8D9] to-transparent animate-pulse" />
 <div className="absolute top-2/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-[#1E88E5] to-transparent animate-pulse" style={{ animationDelay: '1s' }} />
 <div className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-[#00B8D9] to-transparent animate-pulse" style={{ animationDelay: '2s' }} />
 </div>
 </div>

 <main className="relative z-10 pt-32 pb-20">
 <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
 {/* Hero Section */}
 <div className="text-center mb-8 sm:mb-12 lg:mb-16 space-y-4 sm:space-y-6">
 <div className="inline-block mb-4">
 <div className="flex items-center gap-2 sm:gap-4 bg-[#1E88E5]/20 dark:bg-[#1E88E5]/20 light:bg-cyan-100/80 border-2 sm:border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 px-4 sm:px-6 lg:px-8 py-3 sm:py-4 pixel-corners shadow-[0_0_20px_rgba(0,184,217,0.5)]">
 <Lock className="w-6 h-6 sm:w-8 sm:h-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600" />
 <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold tracking-wider pixel-text text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700" style={{ fontFamily: "'Press Start 2P', cursive" }}>
 PIXELVAULT
 </h1>
 <Shield className="w-6 h-6 sm:w-8 sm:h-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600" />
 </div>
 </div>
 
 <p className="text-sm sm:text-lg md:text-xl lg:text-2xl text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text px-4" style={{ fontFamily: "'Press Start 2P', cursive", lineHeight: '2' }}>
 HIDDEN. ENCRYPTED. SECURED.
 </p>
 </div>

 {/* Main Content with Tabs */}
 <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-8">
 <TabsList className="grid w-full grid-cols-3 bg-[#0D1B2A]/80 dark:bg-[#0D1B2A]/80 light:bg-cyan-900/90 border-2 sm:border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.5)] h-12 sm:h-16">
 <TabsTrigger 
 value="embed" 
 className="pixel-text text-xs sm:text-sm lg:text-lg font-bold h-full data-[state=active]:bg-[#1E88E5] data-[state=active]:text-[#E0E6ED] data-[state=active]:shadow-[0_0_20px_rgba(30,136,229,0.8)] data-[state=active]:border-2 data-[state=active]:border-[#00B8D9] text-[#00B8D9] hover:bg-[#1E88E5]/30 transition-all duration-300 pixel-corners" 
 style={{ fontFamily: "'Press Start 2P', cursive", textShadow: "2px 2px 0 rgba(0, 184, 217, 0.5)" }}
 >
 EMBED
 </TabsTrigger>
 <TabsTrigger 
 value="extract" 
 className="pixel-text text-xs sm:text-sm lg:text-lg font-bold h-full data-[state=active]:bg-[#1E88E5] data-[state=active]:text-[#E0E6ED] data-[state=active]:shadow-[0_0_20px_rgba(30,136,229,0.8)] data-[state=active]:border-2 data-[state=active]:border-[#00B8D9] text-[#00B8D9] hover:bg-[#1E88E5]/30 transition-all duration-300 pixel-corners" 
 style={{ fontFamily: "'Press Start 2P', cursive", textShadow: "2px 2px 0 rgba(0, 184, 217, 0.5)" }}
 >
 EXTRACT
 </TabsTrigger>
 <TabsTrigger 
 value="settings" 
 className="pixel-text text-xs sm:text-sm lg:text-lg font-bold h-full data-[state=active]:bg-[#1E88E5] data-[state=active]:text-[#E0E6ED] data-[state=active]:shadow-[0_0_20px_rgba(30,136,229,0.8)] data-[state=active]:border-2 data-[state=active]:border-[#00B8D9] text-[#00B8D9] hover:bg-[#1E88E5]/30 transition-all duration-300 pixel-corners" 
 style={{ fontFamily: "'Press Start 2P', cursive", textShadow: "2px 2px 0 rgba(0, 184, 217, 0.5)" }}
 >
 SETTINGS
 </TabsTrigger>
 </TabsList>

 {/* EMBED TAB */}
 <TabsContent value="embed" className="space-y-4 sm:space-y-6">
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
 {/* Left: Text to Image Generator */}
 <div className="space-y-4 sm:space-y-6">
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-2 sm:border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
 <CardHeader className="p-4 sm:p-6">
 <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
 <div className="w-2 h-2 sm:w-3 sm:h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 <CardTitle className="text-lg sm:text-xl lg:text-2xl font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
 TEXT-TO-IMAGE
 </CardTitle>
 <div className="w-2 h-2 sm:w-3 sm:h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 </div>
 <div className="h-1 bg-[#00B8D9]/30 dark:bg-[#00B8D9]/30" />
 </CardHeader>
 <CardContent className="space-y-4 sm:space-y-6 p-4 sm:p-6 pt-0">
 <div className="relative">
 <Textarea
 value={inputPrompt}
 onChange={(e) => setInputPrompt(e.target.value)}
 placeholder="ENTER YOUR SECRET MESSAGE..."
 className="min-h-[200px] bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white placeholder:text-[#00B8D9]/50 dark:placeholder:text-[#00B8D9]/50 font-mono resize-none focus:border-[#00B8D9] focus:shadow-[0_0_20px_rgba(0,184,217,0.5)] transition-all pixel-corners"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px', lineHeight: '1.8' }}
 />
 <div className="absolute top-2 right-2">
 <Lock className="w-4 h-4 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600animate-pulse" />
 </div>
 </div>

 {/* Batch Mode Toggle */}
 <div className="space-y-4 p-4 bg-[#0D1B2A]/30 dark:bg-[#0D1B2A]/30 rounded-lg border-2 border-[#1E88E5]/30 dark:border-[#1E88E5]/30">
 <div className="flex items-center justify-between">
 <Label className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <RefreshCw className="h-4 w-4" />
 BATCH MODE
 </Label>
 <Switch
 checked={batchMode}
 onCheckedChange={setBatchMode}
 />
 </div>

 {batchMode && (
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 NUMBER OF IMAGES
 </Label>
 <Select value={batchCount.toString()} onValueChange={(v) => setBatchCount(parseInt(v))}>
 <SelectTrigger className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white">
 <SelectValue />
 </SelectTrigger>
 <SelectContent>
 <SelectItem value="2">2 Images</SelectItem>
 <SelectItem value="3">3 Images</SelectItem>
 <SelectItem value="5">5 Images</SelectItem>
 <SelectItem value="10">10 Images</SelectItem>
 </SelectContent>
 </Select>
 </div>
 )}
 </div>

 <Button
 onClick={handleGenerate}
 className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600text-[#E0E6ED] dark:text-[#E0E6ED] light:text-whiteborder-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_20px_rgba(30,136,229,0.5)] hover:shadow-[0_0_30px_rgba(0,184,217,0.8)] transition-all py-6 pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive" }}
 disabled={!inputPrompt || isProcessing}
 >
 <Shield className="w-5 h-5 mr-3" />
 {batchMode ? `GENERATE ${batchCount}` : 'GENERATE'}
 <Key className="w-5 h-5 ml-3" />
 </Button>

 {isProcessing && (
 <div className="space-y-2">
 <Progress value={progress} className="w-full" />
 <p className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600font-mono">
 GENERATING... {progress}%
 </p>
 </div>
 )}
 </CardContent>
 </Card>

 {/* Message Input & Password Section */}
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
 <CardHeader>
 <div className="flex items-center gap-3 mb-4">
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 <CardTitle className="text-xl font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
 CONTENT & SECURITY
 </CardTitle>
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 </div>
 <div className="h-1 bg-[#00B8D9]/30 dark:bg-[#00B8D9]/30" />
 </CardHeader>
 <CardContent className="space-y-6">
 {generatedImage && (
 <>
 {/* Image Size Information */}
 {imageSize && (
 <div className="p-3 bg-[#0D1B2A]/30 border-2 border-[#1E88E5]/30 rounded-lg space-y-2">
 <Label className="text-[#00B8D9] pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 CARRIER IMAGE INFO
 </Label>
 <div className="grid grid-cols-2 gap-4 text-xs">
 <div className="space-y-1">
 <p className="text-[#00B8D9]/70 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '7px' }}>
 DIMENSIONS:
 </p>
 <p className="text-[#E0E6ED] font-mono">
 {imageSize.width} × {imageSize.height}
 </p>
 </div>
 <div className="space-y-1">
 <p className="text-[#00B8D9]/70 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '7px' }}>
 FILE SIZE:
 </p>
 <p className="text-[#E0E6ED] font-mono">
 {(imageSize.fileSize / 1024).toFixed(1)} KB
 </p>
 </div>
 </div>
 <div className="mt-2 p-2 bg-green-400/10 border border-green-400/30 rounded">
 <p className="text-green-300 text-xs pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '7px' }}>
 MAX HIDDEN CAPACITY: ~{Math.floor(imageSize.fileSize / 8).toLocaleString()} BYTES
 </p>
 </div>
 </div>
 )}
 <div className="space-y-3">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>CONTENT TYPE TO HIDE</Label>
 <Select value={contentType} onValueChange={setContentType}>
 <SelectTrigger className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white pixel-corners">
 <SelectValue />
 </SelectTrigger>
 <SelectContent>
 <SelectItem value="text">
 <div className="flex items-center gap-2">
 <FileText className="h-4 w-4" />
 Text Message
 </div>
 </SelectItem>
 <SelectItem value="image">
 <div className="flex items-center gap-2">
 <ImageIcon className="h-4 w-4" />
 Image File
 </div>
 </SelectItem>
 <SelectItem value="audio">
 <div className="flex items-center gap-2">
 <Music className="h-4 w-4" />
 Audio File
 </div>
 </SelectItem>
 <SelectItem value="video">
 <div className="flex items-center gap-2">
 <Video className="h-4 w-4" />
 Video File
 </div>
 </SelectItem>
 <SelectItem value="file">
 <div className="flex items-center gap-2">
 <File className="h-4 w-4" />
 Document/File
 </div>
 </SelectItem>
 </SelectContent>
 </Select>
 </div>

 {contentType === "text" && (
 <div className="space-y-3">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>SECRET MESSAGE</Label>
 <Textarea
 value={textContent}
 onChange={(e) => setTextContent(e.target.value)}
 placeholder="Enter your secret message..."
 className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white pixel-corners font-mono"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px', lineHeight: '1.6' }}
 rows={4}
 />
 </div>
 )}

 {(contentType === "image" || contentType === "audio" || contentType === "video" || contentType === "file") && (
 <div className="space-y-3">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>FILE TO HIDE</Label>
 <div className="border-2 border-dashed border-[#1E88E5] dark:border-[#1E88E5] rounded-lg p-6 text-center hover:border-[#00B8D9] transition-colors bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50pixel-corners">
 <input
 id="content-file"
 type="file"
 accept={
 contentType === "image" ? "image/*" : 
 contentType === "audio" ? "audio/*" : 
 contentType === "video" ? "video/*" : 
 "*/*"
 }
 onChange={handleContentFileChange}
 className="hidden"
 />
 <label htmlFor="content-file" className="cursor-pointer">
 {getContentIcon()}
 <p className="text-sm text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600mt-2 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 {fileContent ? fileContent.name : `CLICK TO UPLOAD ${contentType.toUpperCase()}`}
 </p>
 </label>
 </div>
 </div>
 )}

 {/* Security Options */}
 <div className="space-y-4 p-4 bg-[#0D1B2A]/30 dark:bg-[#0D1B2A]/30 rounded-lg border-2 border-[#1E88E5]/30 dark:border-[#1E88E5]/30pixel-corners">
 <div className="flex items-center justify-between">
 <Label className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <Shield className="h-4 w-4" />
 ENABLE ENCRYPTION
 </Label>
 <Switch
 checked={encryptionEnabled}
 onCheckedChange={setEncryptionEnabled}
 />
 </div>

 {encryptionEnabled && (
 <div className="space-y-3">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 ENCRYPTION PASSWORD
 </Label>
 
 {/* Password Input Row */}
 <div className="flex gap-2">
 <div className="relative flex-1">
 <Input
 type={showPassword ? "text" : "password"}
 value={password}
 onChange={(e) => setPassword(e.target.value)}
 placeholder="Enter strong password"
 className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white pr-10 pixel-corners"
 />
 <Button
 type="button"
 variant="ghost"
 size="sm"
 onClick={togglePasswordVisibility}
 className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-[#1E88E5]/20"
 >
 {showPassword ? <EyeOff className="h-4 w-4 text-[#00B8D9]" /> : <Eye className="h-4 w-4 text-[#00B8D9]" />}
 </Button>
 </div>
 <Button
 type="button"
 variant="outline"
 onClick={generatePassword}
 className="shrink-0 bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20 pixel-corners"
 title="Generate Password"
 >
 <Key className="h-4 w-4" />
 </Button>
 <Button
 type="button"
 variant="outline"
 onClick={copyPasswordToClipboard}
 className="shrink-0 bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20 pixel-corners"
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
 onChange={(e) => setSavePasswordWithProject(e.target.checked)}
 className="rounded border-2 border-[#1E88E5]"
 />
 <Label 
 htmlFor="save-password-with-project" 
 className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}
 >
 SAVE PASSWORD WITH PROJECT
 </Label>
 </div>
 </div>
 </div>
 )}
 </div>

 {/* Embed Button */}
 <Button 
 onClick={handleEmbed}
 className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600text-[#E0E6ED] dark:text-[#E0E6ED] light:text-whiteborder-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}
 disabled={
 (batchMode ? (generatedCarrierFiles.length === 0) : !generatedImage) || 
 (contentType === "text" && !textContent.trim()) ||
 (contentType !== "text" && !fileContent) ||
 isProcessing
 }
 >
 <Shield className="w-4 h-4 mr-2" />
 {isProcessing 
 ? (batchMode ? `PROCESSING ${generatedCarrierFiles.length} FILES...` : "PROCESSING...")
 : (batchMode ? `EMBED IN ${generatedCarrierFiles.length} FILES` : "EMBED DATA")
 }
 </Button>


 </>
 )}
 </CardContent>
 </Card>
 </div>

 {/* Right Column: Preview & Embed Actions */}
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
 <CardHeader>
 <CardTitle className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '16px' }}>
 <Eye className="h-5 w-5" />
 PREVIEW & EMBED
 </CardTitle>
 </CardHeader>
 <CardContent className="space-y-6">
 {/* Batch mode preview */}
 {batchMode && generatedImages.length > 0 && (
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 BATCH PREVIEW ({generatedImages.length} IMAGES)
 </Label>
 <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto p-2 border-2 border-[#1E88E5]/30 rounded-lg bg-[#0D1B2A]/20">
 {generatedImages.slice(0, 4).map((imageUrl, index) => (
 <div 
 key={index}
 className="aspect-square rounded-md overflow-hidden bg-[#0D1B2A] border-2 border-[#1E88E5]/50 hover:border-[#00B8D9] transition-colors"
 >
 <img 
 src={imageUrl} 
 alt={`Batch preview ${index + 1}`}
 className="w-full h-full object-cover"
 />
 </div>
 ))}
 {generatedImages.length > 4 && (
 <div className="aspect-square rounded-md bg-[#0D1B2A] border-2 border-[#1E88E5]/50 flex items-center justify-center">
 <span className="text-sm font-medium text-[#00B8D9] pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>+{generatedImages.length - 4}</span>
 </div>
 )}
 </div>
 <div className="text-xs text-[#00B8D9]/70 bg-[#1E88E5]/10 p-2 rounded pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 TOTAL IMAGES: {generatedImages.length}
 </div>
 </div>
 )}

 {/* Single image preview */}
 {!batchMode && generatedImage && (
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>GENERATED IMAGE</Label>
 <div className="aspect-square rounded-lg overflow-hidden bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5]">
 <img
 src={generatedImage}
 alt="Generated preview"
 className="w-full h-full object-cover"
 />
 </div>
 </div>
 )}

 {/* Generated Image Download - Always downloads the original AI-generated image */}
 {progress === 100 && !isProcessing && generatedImage && (
 <Button 
 className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white border-0 shadow-lg hover:shadow-xl transition-all py-6 text-lg font-semibold pixel-corners"
 onClick={() => downloadGeneratedImage()}
 >
 <Download className="mr-3 h-5 w-5" />
 DOWNLOAD GENERATED IMAGE
 <CheckCircle className="ml-3 h-5 w-5" />
 </Button>
 )}

 {/* Embedded File Download - Moved to Right Column */}
 {progress === 100 && !isProcessing && embeddedResult && (
 <Button 
 className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white border-0 shadow-lg hover:shadow-xl transition-all py-6 text-lg font-semibold pixel-corners"
 onClick={() => downloadEmbeddedFile(embeddedResult)}
 >
 <Download className="mr-3 h-5 w-5" />
 DOWNLOAD EMBEDDED IMAGE
 <CheckCircle className="ml-3 h-5 w-5" />
 </Button>
 )}
 </CardContent>
 </Card>
 </div>
 </TabsContent>

 {/* EXTRACT TAB */}
 <TabsContent value="extract" className="space-y-6">
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
 {/* Extract Configuration */}
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
 <CardHeader>
 <div className="flex items-center gap-3 mb-4">
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 <CardTitle className="text-2xl font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive" }}>
 EXTRACT CONFIG
 </CardTitle>
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 </div>
 <div className="h-1 bg-[#00B8D9]/30 dark:bg-[#00B8D9]/30" />
 </CardHeader>
 <CardContent className="space-y-6">
 {/* File Upload */}
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}>
 STEGANOGRAPHIC FILE
 </Label>
 <div className="border-2 border-dashed border-[#1E88E5] dark:border-[#1E88E5] rounded-lg p-6 text-center hover:border-[#00B8D9] transition-colors bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50">
 <input
 id="extract-file"
 type="file"
 accept="image/*,video/*,audio/*,.wav,.mp3,.flac,.ogg,.aac,.m4a,.pdf,.docx,.txt,.rtf"
 onChange={handleExtractFileChange}
 className="hidden"
 />
 <label htmlFor="extract-file" className="cursor-pointer">
 <div className="flex flex-col items-center gap-3">
 <Upload className="h-8 w-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600" />
 <p className="text-sm text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 {extractFile ? extractFile.name : "CLICK TO UPLOAD STEGO FILE"}
 </p>
 <p className="text-xs text-[#00B8D9]/70 dark:text-[#00B8D9]/70 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 SUPPORTS: IMG, VID, AUDIO, DOCS
 </p>
 </div>
 </label>
 </div>
 </div>

 {/* Password Management */}
 <div className="space-y-3">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}>
 DECRYPTION PASSWORD
 </Label>
 
 {/* Password Input Row */}
 <div className="flex gap-2">
 <div className="relative flex-1">
 <Input
 type={showPassword ? "text" : "password"}
 value={password}
 onChange={(e) => setPassword(e.target.value)}
 placeholder="Enter password to decrypt"
 className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white pr-10"
 />
 <Button
 type="button"
 variant="ghost"
 size="sm"
 onClick={togglePasswordVisibility}
 className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-[#1E88E5]/20"
 >
 {showPassword ? <EyeOff className="h-4 w-4 text-[#00B8D9]" /> : <Eye className="h-4 w-4 text-[#00B8D9]" />}
 </Button>
 </div>
 <Button
 type="button"
 variant="outline"
 onClick={copyPasswordToClipboard}
 className="shrink-0 bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20"
 disabled={!password.trim()}
 title="Copy Password"
 >
 <Copy className="h-4 w-4" />
 </Button>
 </div>
 
 {/* Load Saved Password Option */}
 {savedPassword && (
 <div className="flex items-center gap-2 p-2 bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50rounded-lg border border-[#1E88E5]/30">
 <Shield className="h-4 w-4 text-green-400" />
 <span className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>USE SAVED PASSWORD</span>
 <Button
 type="button"
 variant="ghost"
 size="sm"
 onClick={loadSavedPassword}
 className="ml-auto h-6 px-2 text-xs bg-[#1E88E5]/20 hover:bg-[#1E88E5]/30 text-[#00B8D9] pixel-text-extract"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}
 >
 LOAD
 </Button>
 </div>
 )}
 </div>

 <Button 
 onClick={handleExtract}
 className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600text-[#E0E6ED] dark:text-[#E0E6ED] light:text-whiteborder-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}
 disabled={!extractFile || isProcessing}
 >
 <Key className="w-4 h-4 mr-2" />
 {isProcessing ? "EXTRACTING..." : "EXTRACT DATA"}
 <Eye className="w-4 h-4 ml-2" />
 </Button>
 </CardContent>
 </Card>

 {/* Extract Results */}
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
 <CardHeader>
 <CardTitle className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '16px' }}>
 <Eye className="h-5 w-5" />
 EXTRACTION RESULTS
 </CardTitle>
 </CardHeader>
 <CardContent className="space-y-6">
 {isProcessing && (
 <div className="space-y-3">
 <div className="flex items-center justify-between">
 <Label className="text-sm font-medium text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 EXTRACTION PROGRESS
 </Label>
 <span className="text-sm font-semibold text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 {Math.round(progress)}%
 </span>
 </div>
 <Progress value={progress} className="w-full h-3" />
 <p className="text-xs text-[#00B8D9]/70 text-center pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 EXTRACTING HIDDEN DATA... RECOVERING SECURE CONTENT.
 </p>
 </div>
 )}

 {extractedContent && !isProcessing && (
 <div className="space-y-4">
 <Alert className="bg-green-400/10 border-2 border-green-400/50 pixel-corners">
 <CheckCircle className="h-4 w-4 text-green-400" />
 <AlertDescription className="text-green-300 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 EXTRACTION COMPLETED SUCCESSFULLY!
 {extractedContent.processing_time && 
 ` PROCESSED IN ${extractedContent.processing_time.toFixed(2)} SECONDS.`
 }
 </AlertDescription>
 </Alert>
 
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}>
 EXTRACTED CONTENT
 </Label>
 <div className="p-3 bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50rounded-lg space-y-2 border-2 border-[#1E88E5]/30">
 {extractedContent.extracted_filename && (
 <p className="text-sm text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <strong>FILE:</strong> {extractedContent.extracted_filename}
 </p>
 )}
 {extractedContent.content_type && (
 <p className="text-sm text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <strong>TYPE:</strong> {extractedContent.content_type}
 </p>
 )}
 {extractedContent.file_size && (
 <p className="text-sm text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <strong>SIZE:</strong> {(extractedContent.file_size / 1024).toFixed(1)} KB
 </p>
 )}
 
 {/* Multi-layer extraction details */}
 {extractedContent.is_multi_layer && (
 <div className="space-y-2 p-2 bg-[#0D1B2A]/30 border border-[#1E88E5]/30 rounded">
 <p className="text-sm text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 <strong>MULTI-LAYER:</strong> {extractedContent.total_layers_extracted} LAYERS FOUND
 </p>
 {extractedContent.layer_details && extractedContent.layer_details.length > 0 && (
 <div className="space-y-1">
 <p className="text-sm font-medium text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 LAYER DETAILS:
 </p>
 <div className="space-y-1">
 {extractedContent.layer_details.map((layer: any, index: number) => (
 <div key={index} className="text-xs bg-[#0D1B2A] rounded p-2 border border-[#1E88E5]/20 pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 <strong>LAYER {layer.layer_number}:</strong> {layer.filename} 
 ({(layer.size / 1024).toFixed(1)} KB)
 </div>
 ))}
 </div>
 </div>
 )}
 </div>
 )}
 
 {/* Text content display */}
 {(extractedContent.text_content || extractedContent.preview) && (
 <div className="space-y-1">
 <p className="text-sm font-medium text-[#00B8D9] pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 CONTENT PREVIEW:
 </p>
 <div className="p-2 bg-[#0D1B2A] border border-[#1E88E5]/30 rounded font-mono text-xs text-[#E0E6ED] max-h-32 overflow-y-auto">
 {extractedContent.text_content || extractedContent.preview}
 </div>
 </div>
 )}
 </div>
 </div>

 {/* Download Section */}
 {extractedContent.download_url && (
 <Button 
 className="w-full bg-gradient-to-r from-green-400 to-emerald-400 hover:from-green-500 hover:to-emerald-500 text-[#0D1B2A] border-4 border-green-400 pixel-corners pixel-text shadow-[0_0_20px_rgba(34,197,94,0.5)]"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}
 onClick={() => downloadEmbeddedFile(extractedContent)}
 >
 <Download className="mr-3 h-5 w-5" />
 DOWNLOAD EXTRACTED FILE
 <CheckCircle className="ml-3 h-5 w-5" />
 </Button>
 )}
 </div>
 )}

 {/* Placeholder when no extraction yet or extraction failed */}
 {!extractedContent && !isProcessing && (
 <div className="p-8 text-center border-2 border-dashed rounded-lg pixel-corners">
 {extractionFailed ? (
 // Show when extraction failed or no hidden message found
 <div className="text-red-400 border-red-400/50 bg-red-500/10 p-6 rounded-lg border-2">
 <Key className="h-12 w-12 mx-auto mb-4 text-red-400" />
 <div className="space-y-3">
 {extractionError.toLowerCase().includes("password") ? (
 <>
 <p className="pixel-text-extract font-bold text-red-400" style={{ 
 fontFamily: "'Press Start 2P', cursive", 
 fontSize: '16px',
 textShadow: '0 0 15px rgba(248, 113, 113, 0.9), 0 0 30px rgba(248, 113, 113, 0.5)',
 fontWeight: 'bold'
 }}>
 WRONG PASSWORD
 </p>
 <p className="pixel-text-extract text-orange-300" style={{ 
 fontFamily: "'Press Start 2P', cursive", 
 fontSize: '11px',
 textShadow: '0 0 10px rgba(253, 186, 116, 0.8)',
 fontWeight: 'bold'
 }}>
 PASSWORD INCORRECT OR DECRYPTION FAILED
 </p>
 </>
 ) : (
 <>
 <p className="pixel-text-extract font-bold text-red-400" style={{ 
 fontFamily: "'Press Start 2P', cursive", 
 fontSize: '16px',
 textShadow: '0 0 15px rgba(248, 113, 113, 0.9), 0 0 30px rgba(248, 113, 113, 0.5)',
 fontWeight: 'bold'
 }}>
 NO HIDDEN MESSAGE DETECTED
 </p>
 <p className="pixel-text-extract text-orange-300" style={{ 
 fontFamily: "'Press Start 2P', cursive", 
 fontSize: '11px',
 textShadow: '0 0 10px rgba(253, 186, 116, 0.8)',
 fontWeight: 'bold'
 }}>
 CHECK PASSWORD OR TRY DIFFERENT FILE
 </p>
 </>
 )}
 {extractionError && (
 <div className="mt-4 p-3 bg-red-900/30 border border-red-500/30 rounded-md">
 <p className="pixel-text-extract text-red-200 text-center" style={{ 
 fontFamily: "'Press Start 2P', cursive", 
 fontSize: '8px',
 lineHeight: '1.6'
 }}>
 ERROR: {extractionError}
 </p>
 </div>
 )}
 </div>
 </div>
 ) : (
 // Show when no extraction attempted yet
 <div className="text-[#00B8D9]/50 border-[#1E88E5]/30">
 <Key className="h-8 w-8 mx-auto mb-2 opacity-50" />
 <p className="text-xs pixel-text-extract" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 UPLOAD STEGO FILE TO SEE EXTRACTED CONTENT
 </p>
 </div>
 )}
 </div>
 )}
 </CardContent>
 </Card>
 </div>
 </TabsContent>

 {/* PROJECT SETTINGS TAB */}
 <TabsContent value="settings" className="space-y-6">
 <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)] max-w-4xl mx-auto">
 <CardHeader>
 <div className="flex items-center gap-3 mb-4">
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 <CardTitle className="text-2xl font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
 PROJECT SETTINGS
 </CardTitle>
 <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
 </div>
 <div className="h-1 bg-[#00B8D9]/30 dark:bg-[#00B8D9]/30" />
 </CardHeader>
 <CardContent className="space-y-6">
 <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
 {/* Project Information */}
 <div className="space-y-6">
 <h3 className="text-lg font-semibold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '14px' }}>
 PROJECT INFO
 </h3>
 
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 PROJECT NAME
 </Label>
                <Input
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="e.g., Secret Mission Files"
                  className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white"
                />
              </div> <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 PROJECT DESCRIPTION
 </Label>
                <Textarea
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Brief description of this steganography project..."
                  className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white"
                  rows={3}
                />
              </div> <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}>
 TAGS (COMMA-SEPARATED)
 </Label>
                <Input
                  value={projectTags}
                  onChange={(e) => setProjectTags(e.target.value)}
                  placeholder="secret, mission, confidential"
                  className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white"
                />
              </div> {/* Password Management Section */}
 <div className="space-y-4 p-4 bg-[#0D1B2A]/30 dark:bg-[#0D1B2A]/30 rounded-lg border-2 border-[#1E88E5]/30 dark:border-[#1E88E5]/30">
 <h4 className="text-sm font-semibold flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 <Shield className="h-4 w-4" />
 PASSWORD MANAGEMENT
 </h4>
 
 <div className="space-y-3">
 <div className="space-y-2">
 <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 PROJECT PASSWORD
 </Label>
 <div className="flex gap-2">
 <div className="relative flex-1">
 <Input
 type={showPassword ? "text" : "password"}
 value={password}
 onChange={(e) => setPassword(e.target.value)}
 placeholder="Enter or generate password"
 className="bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white pr-10"
 />
 <Button
 type="button"
 variant="ghost"
 size="sm"
 onClick={togglePasswordVisibility}
 className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-[#1E88E5]/20"
 >
 {showPassword ? <EyeOff className="h-4 w-4 text-[#00B8D9]" /> : <Eye className="h-4 w-4 text-[#00B8D9]" />}
 </Button>
 </div>
 <Button
 type="button"
 variant="outline"
 onClick={generatePassword}
 className="shrink-0 bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20"
 title="Generate Password"
 >
 <Key className="h-4 w-4" />
 </Button>
 <Button
 type="button"
 variant="outline"
 onClick={copyPasswordToClipboard}
 className="shrink-0 bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20"
 disabled={!password.trim()}
 title="Copy Password"
 >
 <Copy className="h-4 w-4" />
 </Button>
 </div>
 </div>
 
 {savedPassword && (
 <div className="p-2 bg-green-400/10 border border-green-400/30 rounded-lg pixel-corners">
 <div className="flex items-center gap-2">
 <CheckCircle className="h-4 w-4 text-green-400" />
 <span className="text-sm text-green-300 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px' }}>
 PASSWORD SAVED WITH PROJECT ({savedPassword.length} CHARS)
 </span>
 </div>
 </div>
 )}
 </div>
 </div>
 </div>
 
 {/* Project Preview */}
 <div className="space-y-6">
 <h3 className="text-lg font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '16px', textShadow: '2px 2px 4px rgba(0,0,0,0.8)', letterSpacing: '1px' }}>
 PROJECT PREVIEW
 </h3>
 
 {projectName ? (
 <div className="p-4 bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50rounded-lg space-y-3 border-2 border-[#1E88E5]/30 pixel-corners">
 <div className="flex items-center gap-2">
 <File className="h-4 w-4 text-[#00B8D9]" />
 <span className="font-bold text-[#00B8D9] pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 {projectName}
 </span>
 </div>
 
 {projectDescription && (
 <p className="text-sm text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text leading-relaxed" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px', lineHeight: '1.6', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 {projectDescription}
 </p>
 )}
 
 {projectTags && (
 <div className="flex flex-wrap gap-2">
 {projectTags.split(',').map((tag, index) => (
 <Badge key={index} variant="secondary" className="text-xs bg-[#1E88E5]/30 border-2 border-[#00B8D9]/70 text-[#00B8D9] pixel-text px-2 py-1" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)', fontWeight: 'bold' }}>
 {tag.trim()}
 </Badge>
 ))}
 </div>
 )}
 
 {/* Generated Images Preview */}
 {(generatedImage || generatedImages.length > 0) && (
 <div className="space-y-2">
 <div className="flex items-center gap-2">
 <ImageIcon className="h-4 w-4 text-[#00B8D9]" />
 <span className="text-sm text-[#00B8D9] pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 GENERATED IMAGES ({generatedImages.length + (generatedImage && !generatedImages.includes(generatedImage) ? 1 : 0)})
 </span>
 </div>
 <div className="grid grid-cols-2 gap-2">
 {generatedImage && (
 <div className="relative group">
 <img 
 src={generatedImage} 
 alt="Generated" 
 className="w-full h-20 object-cover rounded border-2 border-[#00B8D9]/30 hover:border-[#00B8D9] transition-colors"
 />
 <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
 <span className="text-xs text-white pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '2px 2px 4px rgba(0,0,0,0.9)' }}>
 CURRENT
 </span>
 </div>
 </div>
 )}
 {generatedImages.slice(0, 3).map((img, idx) => (
 <div key={idx} className="relative group">
 <img 
 src={img} 
 alt={`Generated ${idx + 1}`} 
 className="w-full h-20 object-cover rounded border-2 border-[#00B8D9]/30 hover:border-[#00B8D9] transition-colors"
 />
 <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
 <span className="text-xs text-white pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '2px 2px 4px rgba(0,0,0,0.9)' }}>
 #{idx + 1}
 </span>
 </div>
 </div>
 ))}
 </div>
 {generatedImages.length > 3 && (
 <div className="text-center">
 <span className="text-xs text-[#00B8D9] pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 +{generatedImages.length - 3} MORE
 </span>
 </div>
 )}
 </div>
 )}

 {/* Embedded Result Preview */}
 {embeddedResult && (
 <div className="space-y-2">
 <div className="flex items-center gap-2">
 <Lock className="h-4 w-4 text-green-400" />
 <span className="text-sm text-green-400 pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 EMBEDDED FILE READY
 </span>
 </div>
 <div className="p-2 bg-green-400/10 border border-green-400/30 rounded pixel-corners">
 <div className="flex justify-between items-center">
 <span className="text-xs text-green-300 pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 {cleanFilenameForDisplay(embeddedResult.output_filename || 'EMBEDDED_FILE')}
 </span>
 <Button
 size="sm"
 variant="ghost"
 onClick={() => downloadEmbeddedFile(embeddedResult)}
 className="h-6 px-2 bg-green-400/20 hover:bg-green-400/30 text-green-300 pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)', fontWeight: 'bold' }}
 >
 DOWNLOAD
 </Button>
 </div>
 </div>
 </div>
 )}

 {/* Password Status */}
 {savedPassword && (
 <div className="flex items-center gap-2 p-2 bg-green-400/10 border border-green-400/30 rounded pixel-corners">
 <Shield className="h-4 w-4 text-green-400" />
 <span className="text-xs text-green-300 pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '9px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 PASSWORD SAVED ({savedPassword.length} CHARS)
 </span>
 <Button
 type="button"
 variant="ghost"
 size="sm"
 onClick={copyPasswordToClipboard}
 className="ml-auto h-6 w-6 p-0 bg-[#1E88E5]/20 hover:bg-[#1E88E5]/30 text-[#00B8D9]"
 title="Copy Password"
 >
 <Copy className="h-3 w-3" />
 </Button>
 </div>
 )}
 
 <div className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '8px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 CREATED: {new Date().toLocaleDateString()}
 </div>
 </div>
 ) : (
 <div className="p-8 text-center text-[#00B8D9]/50 dark:text-[#00B8D9]/50border-2 border-dashed border-[#1E88E5]/30 rounded-lg pixel-corners">
 <File className="h-8 w-8 mx-auto mb-2 opacity-50" />
 <p className="pixel-text font-bold" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
 ENTER PROJECT INFO TO SEE PREVIEW
 </p>
 </div>
 )}
 
 {/* Project Actions */}
 <div className="space-y-2">
 <Button 
 className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600text-[#E0E6ED] dark:text-[#E0E6ED] light:text-whiteborder-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}
 disabled={!projectName.trim()}
 onClick={handleSaveSettings}
 >
 <Save className="w-4 h-4 mr-2" />
 SAVE PROJECT SETTINGS
 </Button>
 
 <Button 
 variant="outline"
 className="w-full bg-[#0D1B2A] dark:bg-[#0D1B2A] border-2 border-[#1E88E5] dark:border-[#1E88E5] text-[#00B8D9] hover:bg-[#1E88E5]/20 pixel-text"
 style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '10px' }}
 onClick={() => {
 setProjectName("");
 setProjectDescription("");
 setProjectTags("");
 setSavePasswordWithProject(false);
 setSavedPassword("");
 setPassword("");
 toast({
 title: "Success",
 description: "Project settings and password cleared!",
 });
 }}
 >
 <RefreshCw className="w-4 h-4 mr-2" />
 CLEAR SETTINGS
 </Button>
 </div>
 </div>
 </div>
 </CardContent>
 </Card>

 {/* Feature Highlights */}
 <div className="grid md:grid-cols-3 gap-6 mt-8">
 {[
 { icon: Wand2, title: "AI GENERATION", desc: "Create unique images with AI", gradient: "from-cyan-500 to-blue-500" },
 { icon: Shield, title: "INVISIBLE HIDING", desc: "Embed data seamlessly", gradient: "from-yellow-600 to-yellow-800" },
 { icon: Lock, title: "SECURE PROTECTION", desc: "Optional password encryption", gradient: "from-emerald-500 to-teal-500" }
 ].map((item, i) => (
 <div
 key={i}
 className="bg-slate-800/40 border border-slate-600 rounded-xl p-6 hover:border-cyan-500 hover:shadow-xl transition-all group backdrop-blur-sm"
 >
 <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${item.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
 <item.icon className="w-6 h-6 text-white" />
 </div>
 <h3 className="text-lg font-bold text-cyan-400 mb-2">
 {item.title}
 </h3>
 <p className="text-sm text-slate-300">{item.desc}</p>
 </div>
            ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </main>      <Footer />
    </div>
  );
}