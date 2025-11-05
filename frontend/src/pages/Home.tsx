import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Play, FileImage, Shield, Lock, Eye, Zap } from "lucide-react";
import DemoVideo from "@/assets/DemoExp.mp4";

export default function Home() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const checkAuth = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        navigate("/auth");
      } else {
        setIsLoading(false);
      }
    };

    checkAuth();

    // Handle navigation and scrolling
    if (window.location.hash === '#demo') {
      // Scroll to demo section after page loads
      setTimeout(() => {
        const demoElement = document.getElementById('demo');
        if (demoElement) {
          demoElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      // Scroll to top when component mounts
      window.scrollTo(0, 0);
    }
  }, [navigate]);

  if (isLoading) {
    return null;
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-20 bg-gradient-to-br from-primary/10 to-sea-light/20 dark:from-primary/5 dark:to-sea-dark/20 overflow-hidden">
          <div className="container relative z-10 pt-20">
            <div className="text-center max-w-4xl mx-auto">
              <span className="text-sm text-primary font-medium uppercase tracking-wider">
                Welcome to VeilForge
              </span>
              <h1 className="text-4xl md:text-6xl font-bold mt-4 mb-6">
                Master the Art of <span className="text-primary">Invisible</span> Data Protection
              </h1>
              <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                Experience the future of steganography with encryption, invisible watermarking, and enterprise-level security. Your sensitive data, hidden in plain sight.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="btn-primary">
                  <Link to="/dashboard">Start Protecting Data</Link>
                </Button>
                <Button 
                  size="lg" 
                  variant="outline"
                  onClick={() => {
                    const demoSection = document.getElementById('demo');
                    if (demoSection) {
                      demoSection.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start'
                      });
                    }
                  }}
                >
                  <Play className="mr-2 h-4 w-4" />
                  Watch Demo
                </Button>
              </div>
            </div>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-1/3 h-full opacity-10">
            <div className="absolute top-10 right-10 w-64 h-64 rounded-full bg-primary/50 blur-3xl animate-pulse-slow" />
            <div className="absolute bottom-10 right-40 w-48 h-48 rounded-full bg-sea-light blur-3xl animate-pulse-slow [animation-delay:1s]" />
          </div>
        </section>

        {/* How-to Section */}
        <section className="section">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-in">
              <span className="text-sm text-primary font-medium uppercase tracking-wider">
                How It Works
              </span>
              <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-4">
                Three Simple Steps to Invisible Security
              </h2>
              <p className="text-muted-foreground">
                VeilForge makes advanced steganography accessible to everyone with our intuitive workflow
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center animate-fade-in [animation-delay:100ms]">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FileImage className="h-8 w-8 text-primary" />
                </div>
                <div className="bg-primary/5 rounded-full px-4 py-1 inline-block mb-4">
                  <span className="text-sm font-semibold text-primary">Step 1</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Upload & Prepare</h3>
                <p className="text-muted-foreground">
                  Upload your carrier image and choose the data you want to hide - text, files, or images. Set encryption preferences for maximum security.
                </p>
              </div>
              
              <div className="text-center animate-fade-in [animation-delay:200ms]">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-8 w-8 text-primary" />
                </div>
                <div className="bg-primary/5 rounded-full px-4 py-1 inline-block mb-4">
                  <span className="text-sm font-semibold text-primary">Step 2</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Encrypt & Embed</h3>
                <p className="text-muted-foreground">
                  Our advanced algorithms encrypt your data with secure encryption and seamlessly embed it within the image pixels, making it completely invisible.
                </p>
              </div>
              
              <div className="text-center animate-fade-in [animation-delay:300ms]">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Eye className="h-8 w-8 text-primary" />
                </div>
                <div className="bg-primary/5 rounded-full px-4 py-1 inline-block mb-4">
                  <span className="text-sm font-semibold text-primary">Step 3</span>
                </div>
                <h3 className="text-xl font-semibold mb-3">Share & Extract</h3>
                <p className="text-muted-foreground">
                  Download your processed image and share it safely. Only authorized users with the correct password can extract the hidden data.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Demo Video Section */}
        <section id="demo" className="section bg-card">
          <div className="container">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div className="animate-fade-in">
                <span className="text-sm text-primary font-medium uppercase tracking-wider">
                  See It In Action
                </span>
                <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-6">
                  Watch VeilForge Transform Your Data Security
                </h2>
                <p className="text-muted-foreground mb-6">
                  Watch our comprehensive demo showing VeilForge's powerful steganography capabilities in action. Learn how to securely hide and protect your sensitive data.
                </p>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center">
                    <div className="h-5 w-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3">
                      <Zap className="h-3 w-3" />
                    </div>
                    Live steganography process demonstration
                  </li>
                  <li className="flex items-center">
                    <div className="h-5 w-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3">
                      <Lock className="h-3 w-3" />
                    </div>
                    Advanced encryption and security features
                  </li>
                  <li className="flex items-center">
                    <div className="h-5 w-5 rounded-full bg-primary/10 text-primary flex items-center justify-center mr-3">
                      <Shield className="h-3 w-3" />
                    </div>
                    Real-world use cases and applications
                  </li>
                </ul>
              </div>
              
              <div className="relative animate-fade-in [animation-delay:200ms]">
                <div className="aspect-video rounded-xl overflow-hidden shadow-2xl bg-black">
                  <video 
                    className="w-full h-full object-cover"
                    controls
                    preload="metadata"
                    poster=""
                  >
                    <source src={DemoVideo} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                </div>
                
                {/* Floating elements */}
                <div className="absolute -top-4 -right-4 bg-primary text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg">
                  Demo Video
                </div>
                <div className="absolute -bottom-4 -left-4 bg-white dark:bg-card rounded-lg p-4 shadow-xl">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">Live Processing</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Main Sections */}
        <section className="section">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-16 animate-fade-in">
              <span className="text-sm text-primary font-medium uppercase tracking-wider">
                Specialized Solutions
              </span>
              <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-4">
                Choose Your Security Domain
              </h2>
              <p className="text-muted-foreground">
                VeilForge offers specialized tools for different security needs and compliance requirements
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* General Section */}
              <div className="glass-card p-8 rounded-xl animate-fade-in [animation-delay:100ms] hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-primary/20">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <FileImage className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4">General Protection</h3>
                  <p className="text-muted-foreground mb-6">
                    Standard steganography for everyday data protection needs. Perfect for personal documents and confidential communications.
                  </p>
                  <ul className="text-sm space-y-2 mb-8 text-left">
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Text & file embedding</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Secure Encryption</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Batch processing</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Project management</li>
                  </ul>
                  <Button asChild className="w-full btn-primary">
                    <Link to="/general">Access General Tools</Link>
                  </Button>
                </div>
              </div>
              
              {/* Copyright Protection */}
              <div className="glass-card p-8 rounded-xl animate-fade-in [animation-delay:200ms] hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-primary/20">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Shield className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4">Copyright Protection</h3>
                  <p className="text-muted-foreground mb-6">
                    Specialized tools for intellectual property protection and digital rights management in creative industries.
                  </p>
                  <ul className="text-sm space-y-2 mb-8 text-left">
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />IP watermarking</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Content protection</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Ownership proof</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Digital signatures</li>
                  </ul>
                  <Button asChild className="w-full btn-primary">
                    <Link to="/copyright">Protect IP Rights</Link>
                  </Button>
                </div>
              </div>
              
              {/* Forensic Evidence */}
              <div className="glass-card p-8 rounded-xl animate-fade-in [animation-delay:300ms] hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-primary/20">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Lock className="h-8 w-8 text-primary" />
                  </div>
                  <h3 className="text-2xl font-bold mb-4">Forensic Evidence</h3>
                  <p className="text-muted-foreground mb-6">
                    Evidence protection for legal proceedings and forensic investigations with secure embedding.
                  </p>
                  <ul className="text-sm space-y-2 mb-8 text-left">
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Evidence integrity</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Integrity verification</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Secure embedding</li>
                    <li className="flex items-center"><ArrowRight className="h-3 w-3 mr-2 text-primary" />Audit trails</li>
                  </ul>
                  <Button asChild className="w-full btn-primary">
                    <Link to="/forensic">Secure Evidence</Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}