import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { FileImage, Shield, Lock } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

interface ProjectCreationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function ProjectCreationDialog({ open, onOpenChange }: ProjectCreationDialogProps) {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isCreating, setIsCreating] = useState(false);

  const projectTypes = [
    {
      type: "general",
      title: "General Project",
      description: "Standard steganography for everyday data protection needs",
      icon: <FileImage className="h-8 w-8 text-primary" />,
      path: "/general",
    },
    {
      type: "copyright",
      title: "Copyright Protection Project",
      description: "Specialized tools for intellectual property protection",
      icon: <Shield className="h-8 w-8 text-primary" />,
      path: "/copyright",
    },
    {
      type: "forensic",
      title: "Forensic Embedding Project",
      description: "Evidence protection for legal proceedings",
      icon: <Lock className="h-8 w-8 text-primary" />,
      path: "/forensic",
    },
  ];

  const handleProjectTypeSelect = async (projectType: string, path: string) => {
    setIsCreating(true);
    
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        toast({
          title: "Authentication Required",
          description: "Please log in to create a project.",
          variant: "destructive",
        });
        navigate("/auth");
        return;
      }

      const { error } = await supabase.from("projects").insert({
        user_id: user.id,
        name: `New ${projectType.charAt(0).toUpperCase() + projectType.slice(1)} Project`,
        project_type: projectType,
        description: `Created ${new Date().toLocaleDateString()}`,
      });

      if (error) throw error;

      toast({
        title: "Project Created",
        description: "Your new project has been created successfully.",
      });

      onOpenChange(false);
      navigate(path);
    } catch (error) {
      console.error("Error creating project:", error);
      toast({
        title: "Error",
        description: "Failed to create project. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[800px]">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Choose your security domain to start protecting your sensitive data
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-4">
          {projectTypes.map((project) => (
            <Card
              key={project.type}
              className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 border-transparent hover:border-primary/20"
              onClick={() => !isCreating && handleProjectTypeSelect(project.type, project.path)}
            >
              <CardContent className="p-6 text-center">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  {project.icon}
                </div>
                <CardTitle className="text-lg mb-2">{project.title}</CardTitle>
                <CardDescription className="text-sm">
                  {project.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
