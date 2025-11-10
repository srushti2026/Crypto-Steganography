import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
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
import { Lock, Key, Eye, Shield, Binary, Upload, FileText, Image as ImageIcon, File, Music, Video, Download, CheckCircle, Settings } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export default function PixelVault() {
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState("embed");
  const [inputText, setInputText] = useState("");
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [contentType, setContentType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [fileContent, setFileContent] = useState<File | null>(null);
  const [password, setPassword] = useState("");
  const [encryptionEnabled, setEncryptionEnabled] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [extractFile, setExtractFile] = useState<File | null>(null);

  useEffect(() => {
    window.scrollTo(0, 0);
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) navigate("/auth");
    });
  }, [navigate]);

  const handleGenerate = () => {
    setIsProcessing(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsProcessing(false);
          setGeneratedImage("https://images.unsplash.com/photo-1620641788421-7a1c342ea42e?w=800&h=800&fit=crop");
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

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

  const handleEmbed = () => {
    setIsProcessing(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsProcessing(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleExtract = () => {
    setIsProcessing(true);
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsProcessing(false);
          alert("Extraction complete!");
          return 100;
        }
        return prev + 10;
      });
    }, 200);
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
        <div className="container max-w-6xl mx-auto px-4">
          {/* Hero Section */}
          <div className="text-center mb-16 space-y-6">
            <div className="inline-block mb-4">
              <div className="flex items-center gap-4 bg-[#1E88E5]/20 dark:bg-[#1E88E5]/20 light:bg-cyan-100/80 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 px-8 py-4 pixel-corners shadow-[0_0_20px_rgba(0,184,217,0.5)]">
                <Lock className="w-8 h-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600" />
                <h1 className="text-4xl md:text-5xl font-bold tracking-wider pixel-text text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                  PIXELVAULT
                </h1>
                <Shield className="w-8 h-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600" />
              </div>
            </div>
            
            <p className="text-xl md:text-2xl text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", lineHeight: '2' }}>
              HIDDEN. ENCRYPTED. SECURED.
            </p>
          </div>

          {/* Main Content with Tabs */}
          <Tabs value={selectedTab} onValueChange={setSelectedTab} className="space-y-6">
            <TabsList className="grid w-full grid-cols-3 bg-[#1E88E5]/20 dark:bg-[#1E88E5]/20 light:bg-cyan-100/80">
              <TabsTrigger value="embed" className="pixel-text text-xs" style={{ fontFamily: "'Press Start 2P', cursive" }}>EMBED</TabsTrigger>
              <TabsTrigger value="extract" className="pixel-text text-xs" style={{ fontFamily: "'Press Start 2P', cursive" }}>EXTRACT</TabsTrigger>
              <TabsTrigger value="settings" className="pixel-text text-xs" style={{ fontFamily: "'Press Start 2P', cursive" }}>SETTINGS</TabsTrigger>
            </TabsList>

            {/* EMBED TAB */}
            <TabsContent value="embed" className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left: Text to Image Generator */}
                <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
                  <CardHeader>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
                      <CardTitle className="text-2xl font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                        TEXT-TO-IMAGE
                      </CardTitle>
                      <div className="w-3 h-3 bg-[#00B8D9] dark:bg-[#00B8D9] light:bg-cyan-500 animate-pulse" />
                    </div>
                    <div className="h-1 bg-[#00B8D9]/30 dark:bg-[#00B8D9]/30 light:bg-cyan-300/50" />
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="relative">
                      <Textarea
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="ENTER YOUR SECRET MESSAGE..."
                        className="min-h-[200px] bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900 placeholder:text-[#00B8D9]/50 dark:placeholder:text-[#00B8D9]/50 light:placeholder:text-cyan-600/50 font-mono resize-none focus:border-[#00B8D9] focus:shadow-[0_0_20px_rgba(0,184,217,0.5)] transition-all pixel-corners"
                        style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px', lineHeight: '1.8' }}
                      />
                      <div className="absolute top-2 right-2">
                        <Lock className="w-4 h-4 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 animate-pulse" />
                      </div>
                    </div>

                    <Button
                      onClick={handleGenerate}
                      className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500 hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_20px_rgba(30,136,229,0.5)] hover:shadow-[0_0_30px_rgba(0,184,217,0.8)] transition-all py-6 pixel-text"
                      style={{ fontFamily: "'Press Start 2P', cursive" }}
                      disabled={!inputText || isProcessing}
                    >
                      <Shield className="w-5 h-5 mr-3" />
                      GENERATE
                      <Key className="w-5 h-5 ml-3" />
                    </Button>

                    {isProcessing && (
                      <div className="space-y-2">
                        <Progress value={progress} className="w-full" />
                        <p className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 font-mono">
                          GENERATING... {progress}%
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Right: Preview & Embed Options */}
                <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)]">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '16px' }}>
                      <Eye className="h-5 w-5" />
                      PREVIEW & EMBED
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {generatedImage && (
                      <div className="space-y-2">
                        <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Generated Image</Label>
                        <div className="aspect-square rounded-lg overflow-hidden bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400">
                          <img
                            src={generatedImage}
                            alt="Generated preview"
                            className="w-full h-full object-cover"
                          />
                        </div>
                      </div>
                    )}

                    {generatedImage && (
                      <>
                        <div className="space-y-2">
                          <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Content Type to Hide</Label>
                          <Select value={contentType} onValueChange={setContentType}>
                            <SelectTrigger className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900">
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
                          <div className="space-y-2">
                            <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Secret Message</Label>
                            <Textarea
                              value={textContent}
                              onChange={(e) => setTextContent(e.target.value)}
                              placeholder="Enter secret message..."
                              className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900"
                              rows={4}
                            />
                          </div>
                        )}

                        {(contentType === "image" || contentType === "audio" || contentType === "video" || contentType === "file") && (
                          <div className="space-y-2">
                            <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">File to Hide</Label>
                            <div className="border-2 border-dashed border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 rounded-lg p-4 text-center hover:border-[#00B8D9] transition-colors bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50 light:bg-cyan-50/50">
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
                                <p className="text-sm text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 mt-2">
                                  {fileContent ? fileContent.name : `Click to upload ${contentType}`}
                                </p>
                              </label>
                            </div>
                          </div>
                        )}

                        <div className="space-y-4 p-4 bg-[#0D1B2A]/30 dark:bg-[#0D1B2A]/30 light:bg-cyan-100/50 rounded-lg border-2 border-[#1E88E5]/30 dark:border-[#1E88E5]/30 light:border-cyan-300">
                          <div className="flex items-center justify-between">
                            <Label className="flex items-center gap-2 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">
                              <Lock className="h-4 w-4" />
                              Enable Encryption
                            </Label>
                            <Switch
                              checked={encryptionEnabled}
                              onCheckedChange={setEncryptionEnabled}
                            />
                          </div>

                          {encryptionEnabled && (
                            <div className="space-y-2">
                              <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Encryption Password</Label>
                              <Input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter password"
                                className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900"
                              />
                            </div>
                          )}
                        </div>

                        <Button 
                          onClick={handleEmbed}
                          className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500 hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text"
                          style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}
                          disabled={(!textContent && !fileContent) || isProcessing}
                        >
                          <Shield className="w-4 h-4 mr-2" />
                          EMBED DATA
                        </Button>

                        {progress === 100 && !isProcessing && (
                          <Button className="w-full border-2 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text" variant="outline" style={{ fontFamily: "'Press Start 2P', cursive", fontSize: '12px' }}>
                            <Download className="mr-2 h-4 w-4" />
                            DOWNLOAD
                          </Button>
                        )}
                      </>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* EXTRACT TAB */}
            <TabsContent value="extract" className="space-y-6">
              <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)] max-w-2xl mx-auto">
                <CardHeader>
                  <CardTitle className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                    EXTRACT DATA
                  </CardTitle>
                  <CardDescription className="text-[#E0E6ED]/70 dark:text-[#E0E6ED]/70 light:text-gray-600">
                    Extract hidden data from steganographic images
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Upload Stego Image</Label>
                    <div className="border-2 border-dashed border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 rounded-lg p-6 text-center hover:border-[#00B8D9] transition-colors bg-[#0D1B2A]/50 dark:bg-[#0D1B2A]/50 light:bg-cyan-50/50">
                      <input
                        id="extract-file"
                        type="file"
                        accept="image/*"
                        onChange={handleExtractFileChange}
                        className="hidden"
                      />
                      <label htmlFor="extract-file" className="cursor-pointer">
                        <Upload className="h-8 w-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 mx-auto mb-2" />
                        <p className="text-sm text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">
                          {extractFile ? extractFile.name : "Click to upload image"}
                        </p>
                      </label>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Decryption Password (if encrypted)</Label>
                    <Input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter password"
                      className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900"
                    />
                  </div>

                  <Button 
                    onClick={handleExtract}
                    className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500 hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text py-6"
                    style={{ fontFamily: "'Press Start 2P', cursive" }}
                    disabled={!extractFile || isProcessing}
                  >
                    <Key className="w-5 h-5 mr-3" />
                    EXTRACT
                    <Eye className="w-5 h-5 ml-3" />
                  </Button>

                  {isProcessing && (
                    <div className="space-y-2">
                      <Progress value={progress} className="w-full" />
                      <p className="text-xs text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 font-mono">
                        EXTRACTING... {progress}%
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* SETTINGS TAB */}
            <TabsContent value="settings" className="space-y-6">
              <Card className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/90 border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners shadow-[0_0_30px_rgba(0,184,217,0.3)] max-w-2xl mx-auto">
                <CardHeader>
                  <CardTitle className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                    PROJECT SETTINGS
                  </CardTitle>
                  <CardDescription className="text-[#E0E6ED]/70 dark:text-[#E0E6ED]/70 light:text-gray-600">
                    Configure your PixelVault project
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Project Name</Label>
                    <Input
                      placeholder="My PixelVault Project"
                      className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700">Description</Label>
                    <Textarea
                      placeholder="Project description..."
                      className="bg-[#0D1B2A] dark:bg-[#0D1B2A] light:bg-cyan-50 border-2 border-[#1E88E5] dark:border-[#1E88E5] light:border-cyan-400 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-gray-900"
                      rows={4}
                    />
                  </div>
                  <Button className="w-full bg-[#1E88E5] dark:bg-[#1E88E5] light:bg-cyan-500 hover:bg-[#00B8D9] dark:hover:bg-[#00B8D9] light:hover:bg-cyan-600 text-[#E0E6ED] dark:text-[#E0E6ED] light:text-white border-4 border-[#00B8D9] dark:border-[#00B8D9] light:border-cyan-400 pixel-corners pixel-text py-6" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                    <Settings className="w-5 h-5 mr-3" />
                    SAVE SETTINGS
                  </Button>
                </CardContent>
              </Card>

              {/* Info Cards */}
              <div className="grid md:grid-cols-3 gap-4 mt-8">
                {[
                  { icon: Lock, title: "ENCRYPT", desc: "Military-grade encryption" },
                  { icon: Eye, title: "STEALTH", desc: "Hidden in plain sight" },
                  { icon: Shield, title: "PROTECT", desc: "Copyright secured" }
                ].map((item, i) => (
                  <div
                    key={i}
                    className="bg-[#1E88E5]/10 dark:bg-[#1E88E5]/10 light:bg-white/80 border-2 border-[#00B8D9]/50 dark:border-[#00B8D9]/50 light:border-cyan-400/50 pixel-corners p-4 hover:border-[#00B8D9] dark:hover:border-[#00B8D9] light:hover:border-cyan-500 hover:shadow-[0_0_15px_rgba(0,184,217,0.3)] transition-all group"
                  >
                    <item.icon className="w-8 h-8 text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-600 mb-3 group-hover:animate-pulse" />
                    <h3 className="text-sm font-bold text-[#00B8D9] dark:text-[#00B8D9] light:text-cyan-700 mb-2 pixel-text" style={{ fontFamily: "'Press Start 2P', cursive" }}>
                      {item.title}
                    </h3>
                    <p className="text-xs text-[#E0E6ED]/70 dark:text-[#E0E6ED]/70 light:text-gray-600 font-mono">{item.desc}</p>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>

      <Footer />

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); }
          25% { transform: translateY(-20px) translateX(10px); }
          50% { transform: translateY(-40px) translateX(-10px); }
          75% { transform: translateY(-20px) translateX(5px); }
        }
        
        .animate-float {
          animation: float 15s ease-in-out infinite;
        }
        
        .pixel-corners {
          position: relative;
          clip-path: polygon(
            0 8px, 8px 8px, 8px 0,
            calc(100% - 8px) 0, calc(100% - 8px) 8px, 100% 8px,
            100% calc(100% - 8px), calc(100% - 8px) calc(100% - 8px), calc(100% - 8px) 100%,
            8px 100%, 8px calc(100% - 8px), 0 calc(100% - 8px)
          );
        }
        
        .pixel-text {
          text-shadow: 2px 2px 0 rgba(0, 184, 217, 0.5);
        }
      `}</style>
    </div>
  );
}