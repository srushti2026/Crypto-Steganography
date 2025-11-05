import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { supabase } from "@/integrations/supabase/client";
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
  Zap,
  Music,
  Video
} from "lucide-react";

// Simple toast replacement for now
const toast = {
  success: (message: string) => {
    console.log('✅ SUCCESS:', message);
    alert(message);
  },
  error: (message: string) => {
    console.error('❌ ERROR:', message);
    alert('Error: ' + message);
  }
};

export default function General() {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState("embed");
  const [carrierFile, setCarrierFile] = useState<File | null>(null);
  const [extractFile, setExtractFile] = useState<File | null>(null);
  const [contentType, setContentType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [fileContent, setFileContent] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [operationResult, setOperationResult] = useState<any>(null);

  useEffect(() => {
    window.scrollTo(0, 0);
    
    const checkAuth = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) {
          navigate("/auth");
        }
      } catch (error) {
        console.error("Auth check error:", error);
      }
    };

    checkAuth();
  }, [navigate]);

  const handleCarrierFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCarrierFile(e.target.files[0]);
    }
  };

  const handleExtractFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setExtractFile(e.target.files[0]);
    }
  };

  const handleContentFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFileContent(e.target.files[0]);
    }
  };

  const generatePassword = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let result = '';
    for (let i = 0; i < 16; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setPassword(result);
    toast.success('Strong password generated!');
  };

  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleEmbed = async () => {
    if (!carrierFile) {
      toast.error("Please select a carrier file");
      return;
    }

    if (contentType === "text" && !textContent.trim()) {
      toast.error("Please enter text content to hide");
      return;
    }

    if (contentType === "file" && !fileContent) {
      toast.error("Please select a file to hide");
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }

    setIsProcessing(true);
    simulateProgress();
    
    // Simulate API call - replace with actual API integration
    setTimeout(() => {
      setIsProcessing(false);
      setOperationResult({
        filename: "embedded_" + carrierFile.name,
        file_size: carrierFile.size + 1000,
        processing_time: 2.5
      });
      toast.success("Embedding completed successfully!");
    }, 2500);
  };

  const handleExtract = async () => {
    if (!extractFile) {
      toast.error("Please select a file to extract from");
      return;
    }

    if (!password.trim()) {
      toast.error("Please enter the password");
      return;
    }

    setIsProcessing(true);
    simulateProgress();
    
    // Simulate API call - replace with actual API integration
    setTimeout(() => {
      setIsProcessing(false);
      setOperationResult({
        filename: "extracted_data.txt",
        preview: "This is the extracted secret message...",
        processing_time: 1.8
      });
      toast.success("Extraction completed successfully!");
    }, 2500);
  };

  const downloadResult = () => {
    if (!operationResult) {
      toast.error("No result to download");
      return;
    }
    toast.success("Download would start here - integrate with actual backend");
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
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="embed">Embed Data</TabsTrigger>
                <TabsTrigger value="extract">Extract Data</TabsTrigger>
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
                      {/* Carrier File Upload */}
                      <div className="space-y-2">
                        <Label htmlFor="carrier-file">Carrier File</Label>
                        <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                          <input
                            id="carrier-file"
                            type="file"
                            accept="image/*,video/*,audio/*,.pdf,.docx,.txt"
                            onChange={handleCarrierFileChange}
                            className="hidden"
                          />
                          <label htmlFor="carrier-file" className="cursor-pointer">
                            <FileImage className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                            <p className="text-sm text-muted-foreground">
                              {carrierFile ? carrierFile.name : "Click to upload carrier file"}
                            </p>
                          </label>
                        </div>
                      </div>

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
                                File
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

                      {contentType === "file" && (
                        <div className="space-y-2">
                          <Label htmlFor="content-file">File to Hide</Label>
                          <div className="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-primary/50 transition-colors">
                            <input
                              id="content-file"
                              type="file"
                              onChange={handleContentFileChange}
                              className="hidden"
                            />
                            <label htmlFor="content-file" className="cursor-pointer">
                              {getContentIcon()}
                              <p className="text-sm text-muted-foreground mt-2">
                                {fileContent ? fileContent.name : "Click to upload file"}
                              </p>
                            </label>
                          </div>
                        </div>
                      )}

                      {/* Password */}
                      <div className="space-y-2">
                        <Label htmlFor="password">Encryption Password</Label>
                        <div className="flex gap-2">
                          <Input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter strong password"
                            className="flex-1"
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={generatePassword}
                            className="shrink-0"
                          >
                            <Key className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>

                      <Button 
                        onClick={handleEmbed} 
                        className="w-full"
                        disabled={!carrierFile || (!textContent && !fileContent) || isProcessing}
                      >
                        {isProcessing ? "Processing..." : "Embed Data"}
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
                      {carrierFile && (
                        <div className="space-y-2">
                          <Label>Carrier File Preview</Label>
                          <div className="aspect-video rounded-lg overflow-hidden bg-muted flex items-center justify-center">
                            <FileImage className="h-16 w-16 text-muted-foreground" />
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {carrierFile.name} ({(carrierFile.size / 1024).toFixed(1)} KB)
                          </p>
                        </div>
                      )}

                      {isProcessing && (
                        <div className="space-y-2">
                          <Label>Processing Progress</Label>
                          <Progress value={progress} className="w-full" />
                          <p className="text-sm text-muted-foreground">
                            Embedding data... {progress}%
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
                                ` Processed in ${operationResult.processing_time} seconds.`
                              }
                            </AlertDescription>
                          </Alert>
                          
                          {operationResult.preview && (
                            <div className="space-y-2">
                              <Label>Content Preview</Label>
                              <div className="p-3 bg-muted rounded-lg">
                                <p className="text-sm font-mono">
                                  {operationResult.preview}
                                </p>
                              </div>
                            </div>
                          )}
                          
                          <Button onClick={downloadResult} className="w-full">
                            <Download className="h-4 w-4 mr-2" />
                            Download Result
                          </Button>
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
                            accept="image/*,video/*,audio/*,.pdf,.docx,.txt"
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
                      <div className="space-y-2">
                        <Label htmlFor="extract-password">Decryption Password</Label>
                        <Input
                          id="extract-password"
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter password to decrypt"
                        />
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
                        View extracted content and download results
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {isProcessing && (
                        <div className="space-y-2">
                          <Label>Extraction Progress</Label>
                          <Progress value={progress} className="w-full" />
                          <p className="text-sm text-muted-foreground">
                            Extracting hidden data... {progress}%
                          </p>
                        </div>
                      )}

                      {operationResult && !isProcessing && (
                        <div className="space-y-4">
                          <Alert>
                            <CheckCircle className="h-4 w-4" />
                            <AlertDescription>
                              Extraction completed successfully!
                            </AlertDescription>
                          </Alert>
                          
                          {operationResult.preview && (
                            <div className="space-y-2">
                              <Label>Extracted Content Preview</Label>
                              <div className="p-3 bg-muted rounded-lg">
                                <p className="text-sm font-mono">
                                  {operationResult.preview}
                                </p>
                              </div>
                            </div>
                          )}
                          
                          <Button onClick={downloadResult} className="w-full">
                            <Download className="h-4 w-4 mr-2" />
                            Download Extracted Data
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}