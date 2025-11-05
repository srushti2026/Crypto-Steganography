import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HeroSection from "@/components/HeroSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Shield, Eye, FileImage, Lock, Zap, Users } from "lucide-react";

export default function Index() {
  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
  }, []);
  
  // VeilForge features
  const features = [
    {
      icon: <Shield className="h-8 w-8 text-primary" />,
      title: "Strong Security",
      description: "Secure encryption with advanced algorithms ensure your hidden data stays protected."
    },
    {
      icon: <Eye className="h-8 w-8 text-primary" />,
      title: "Invisible Watermarking", 
      description: "Advanced algorithms make your hidden content completely undetectable to the human eye."
    },
    {
      icon: <FileImage className="h-8 w-8 text-primary" />,
      title: "Multi-Format Support",
      description: "Hide text, images, and files in PNG/JPEG carriers. Special DOCX embedding support."
    },
    {
      icon: <Lock className="h-8 w-8 text-primary" />,
      title: "Privacy First",
      description: "Your processed files are only accessible to you. We never store sensitive content."
    },
    {
      icon: <Zap className="h-8 w-8 text-primary" />,
      title: "Lightning Fast",
      description: "Process files under 5 seconds for files ≤10MB with our optimized algorithms."
    },
    {
      icon: <Users className="h-8 w-8 text-primary" />,
      title: "Scalable Platform",
      description: "Robust infrastructure supports multiple concurrent users and batch processing."
    }
  ];

  // Sectors served
  const sectors = [
    {
      title: "Personal Privacy & Security",
      description: "Protect personal documents, communications, and sensitive information",
      applications: ["Personal Documents", "Private Communications", "Identity Protection"]
    },
    {
      title: "Corporate Security", 
      description: "Intellectual property protection and confidential data embedding",
      applications: ["IP Protection", "Trade Secrets", "Internal Communications"]
    },
    {
      title: "Forensics",
      description: "Secure evidence storage and legal document authentication", 
      applications: ["Evidence Integrity", "Legal Authentication", "Secure Evidence"]
    },
    {
      title: "Media & Entertainment",
      description: "Copyright protection and content authentication for creative works",
      applications: ["Copyright Protection", "Content Authentication", "Anti-Piracy"]
    }
  ];
  
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1">
        {/* Hero Section */}
        <HeroSection />
        
        {/* About VeilForge Section */}
        <section id="about" className="section">
          <div className="container">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div className="animate-fade-in [animation-delay:100ms]">
                <span className="text-sm text-primary font-medium uppercase tracking-wider">
                  Advanced Steganography
                </span>
                <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-6">
                  The Future of Invisible Data Protection
                </h2>
                <p className="text-muted-foreground mb-6">
                  VeilForge revolutionizes data security through cutting-edge steganography. Our platform uses advanced algorithms to seamlessly embed encrypted content within images, making your sensitive data completely invisible to unauthorized eyes.
                </p>
                <p className="text-muted-foreground mb-8">
                  Whether you're protecting intellectual property, securing classified communications, or maintaining evidence chains, VeilForge provides strong security with uncompromised usability.
                </p>
                <Button asChild className="btn-primary">
                  <Link to="/home">
                    Explore Platform <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              </div>
              
              <div className="relative animate-fade-in [animation-delay:300ms]">
                <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-gradient-to-br from-primary/20 to-sea-light/30 flex items-center justify-center">
                  <div className="text-center p-8">
                    <FileImage className="h-24 w-24 text-primary mx-auto mb-4" />
                    <h3 className="text-xl font-semibold mb-2">Secure Embedding</h3>
                    <p className="text-muted-foreground">Your data, hidden in plain sight</p>
                  </div>
                </div>
                <div className="absolute -bottom-6 -left-6 w-2/3 rounded-2xl overflow-hidden shadow-xl bg-gradient-to-br from-sea-dark/80 to-primary/60 flex items-center justify-center">
                  <div className="text-center p-6 text-white">
                    <Lock className="h-16 w-16 mx-auto mb-3" />
                    <h4 className="font-semibold">Securely Encrypted</h4>
                  </div>
                </div>
                <div className="absolute -top-6 -right-6 w-1/2 rounded-2xl overflow-hidden shadow-xl bg-gradient-to-br from-primary to-sea-light flex items-center justify-center">
                  <div className="text-center p-6 text-white">
                    <Eye className="h-12 w-12 mx-auto mb-2" />
                    <h4 className="text-sm font-semibold">Invisible</h4>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* Features Section */}
        <section className="section bg-card">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-12 animate-fade-in">
              <span className="text-sm text-primary font-medium uppercase tracking-wider">
                Platform Features
              </span>
              <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-4">
                Why Choose VeilForge?
              </h2>
              <p className="text-muted-foreground">
                Advanced steganography technology meets enterprise-grade security and user-friendly design
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div 
                  key={index} 
                  className="glass-card p-6 rounded-xl animate-fade-in flex flex-col items-center text-center"
                  style={{ animationDelay: `${(index + 1) * 100}ms` }}
                >
                  <div className="mb-4 p-3 rounded-full bg-primary/10">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Sectors Served */}
        <section className="section">
          <div className="container">
            <div className="text-center max-w-3xl mx-auto mb-12 animate-fade-in">
              <span className="text-sm text-primary font-medium uppercase tracking-wider">
                Sectors Served
              </span>
              <h2 className="text-3xl md:text-4xl font-bold mt-2 mb-4">
                Trusted by Industry Leaders
              </h2>
              <p className="text-muted-foreground">
                From government agencies to creative studios, VeilForge secures sensitive data across critical industries
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {sectors.map((sector, index) => (
                <div 
                  key={index} 
                  className="glass-card p-8 rounded-xl animate-fade-in"
                  style={{ animationDelay: `${(index + 1) * 150}ms` }}
                >
                  <h3 className="text-2xl font-bold mb-3">{sector.title}</h3>
                  <p className="text-muted-foreground mb-4">{sector.description}</p>
                  <div className="flex flex-wrap gap-2">
                    {sector.applications.map((app, appIndex) => (
                      <span 
                        key={appIndex} 
                        className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-medium"
                      >
                        {app}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
        
        {/* Testimonials Section */}
        <TestimonialsSection />
        
        {/* CTA Section */}
        <section className="relative py-24 bg-primary/5">
          <div className="container">
            <div className="max-w-3xl mx-auto text-center animate-fade-in">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Ready to Secure Your Data?
              </h2>
              <p className="text-muted-foreground mb-8">
                Join thousands of professionals who trust VeilForge for invisible data protection. Start your secure journey today.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="btn-primary">
                  <Link to="/home">Get Started Free</Link>
                </Button>
                <Button asChild size="lg" variant="outline">
                  <Link to="/contact">Contact Sales</Link>
                </Button>
              </div>
            </div>
          </div>
          
          {/* Decorative waves */}
          <div className="absolute bottom-0 left-0 right-0 h-24 overflow-hidden">
            <svg 
              className="absolute bottom-0 w-full h-24 fill-background"
              preserveAspectRatio="none"
              viewBox="0 0 1440 74"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path 
                d="M0,37.1L40,34.5C80,32,160,27,240,29.6C320,32,400,42,480,42.9C560,44,640,35,720,32.1C800,30,880,34,960,40.8C1040,47,1120,56,1200,56.6C1280,57,1360,48,1400,43.3L1440,39.1L1440,74L1400,74C1360,74,1280,74,1200,74C1120,74,1040,74,960,74C880,74,800,74,720,74C640,74,560,74,480,74C400,74,320,74,240,74C160,74,80,74,40,74L0,74Z"
                className="animate-wave opacity-50"
              />
              <path 
                d="M0,37.1L40,34.5C80,32,160,27,240,29.6C320,32,400,42,480,42.9C560,44,640,35,720,32.1C800,30,880,34,960,40.8C1040,47,1120,56,1200,56.6C1280,57,1360,48,1400,43.3L1440,39.1L1440,74L1400,74C1360,74,1280,74,1200,74C1120,74,1040,74,960,74C880,74,800,74,720,74C640,74,560,74,480,74C400,74,320,74,240,74C160,74,80,74,40,74L0,74Z"
                className="animate-wave opacity-100 [animation-delay:-4s]"
              />
            </svg>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
}
