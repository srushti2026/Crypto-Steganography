import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Github, Linkedin, Mail, Code, Database, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import profileImage from "@/assets/profile.JPG";

const Developers = () => {
  const developers = [
    {
      name: "SRUSHTI",
      role: "1KS22CG051",
      avatar: profileImage,
      bio: "Student of 4th year Computer Science and Design, KSIT",
      github: "https://github.com/SrushtiKumar",
      linkedin: "https://www.linkedin.com/in/srushti-kumar-4019652a2/",
      email: "srushti0404@gmail.com"
    },
    {
      name: "TRIYA HIREMATH",
      role: "1KS22CG053",
      avatar: profileImage,
      bio: "Student of 4th year Computer Science and Design, KSIT",
      github: "https://github.com/triyaa-h",
      linkedin: "https://www.linkedin.com/in/triya-hiremath-40696b269/",
      email: "triyahiremath@gmail.com"
    },
    {
      name: "AMITA S",
      role: "1KS22CG003",
      avatar: profileImage,
      bio: "Student of 4th year Computer Science and Design, KSIT",
      github: "https://github.com/aamita1306",
      linkedin: "https://www.linkedin.com/in/amita-s-441444287/",
      email: "amitasudarshan1@gmail.com"
    }
  ];

  const techStack = [
    { name: "React & TypeScript", icon: Code },
    { name: "Supabase", icon: Database },
    { name: "Advanced Encryption", icon: Shield }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-24">
        {/* Project Overview */}
        <section className="max-w-4xl mx-auto mb-16 animate-fade-in">
          <h1 className="text-5xl font-bold mb-6 text-center bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            About VeilForge
          </h1>
          <p className="text-xl text-muted-foreground text-center mb-8">
            VeilForge is a cutting-edge steganography platform designed to protect digital content 
            through advanced embedding techniques, copyright protection, and forensic evidence chain management.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {techStack.map((tech, index) => (
              <Card key={index} className="hover-scale transition-all">
                <CardContent className="flex flex-col items-center justify-center p-6">
                  <tech.icon className="w-12 h-12 text-primary mb-3" />
                  <h3 className="font-semibold text-center">{tech.name}</h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Applications */}
        <section className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold mb-8 text-center">Applications</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Copyright Protection</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Embed invisible watermarks in digital content to prove ownership and track unauthorized distribution
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Secure Communication</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Hide sensitive messages within ordinary files for covert communication channels
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Forensic Evidence</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Maintain integrity of digital evidence with secure embedding techniques
                </p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Data Privacy</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Protect sensitive information by hiding it in plain sight within carrier files
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Development Team */}
        <section className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold mb-12 text-center">Meet the Team</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {developers.map((dev, index) => (
              <Card key={index} className="hover-scale transition-all">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center text-center">
                    <img 
                      src={dev.avatar} 
                      alt={dev.name}
                      className="w-32 h-32 rounded-full mb-4 border-4 border-primary/20"
                    />
                    <h3 className="text-xl font-bold mb-1">{dev.name}</h3>
                    <p className="text-primary font-medium mb-3">{dev.role}</p>
                    <p className="text-muted-foreground mb-4">{dev.bio}</p>
                    
                    <div className="flex gap-4">
                      <a href={dev.github} className="text-muted-foreground hover:text-primary transition-colors">
                        <Github className="w-5 h-5" />
                      </a>
                      <a href={dev.linkedin} className="text-muted-foreground hover:text-primary transition-colors">
                        <Linkedin className="w-5 h-5" />
                      </a>
                      <a href={`mailto:${dev.email}`} className="text-muted-foreground hover:text-primary transition-colors">
                        <Mail className="w-5 h-5" />
                      </a>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default Developers;
