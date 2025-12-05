import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Plus, Settings, FileText, Clock, Lock, Edit, RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Helper function to parse project description (copied from Dashboard.tsx)
const parseProjectDescription = (description: string | null) => {
  if (!description) return { description: "", metadata: {} };
  
  // First, check if it's a JSON string
  if (description.trim().startsWith('{')) {
    try {
      const parsed = JSON.parse(description);
      
      if (parsed.description !== undefined) {
        // Standard project format with metadata - extract the inner description
        return {
          description: parsed.description || "",
          metadata: parsed.metadata || {}
        };
      } else {
        // JSON object without description field - show as plain text
        return { description: description, metadata: {} };
      }
    } catch (e) {
      console.warn('Failed to parse project description JSON:', e);
      // If JSON parsing fails, return as plain text
      return { description: description, metadata: {} };
    }
  } else {
    // Plain text description
    return { description: description, metadata: {} };
  }
};

interface Project {
  id: string;
  name: string;
  description: string;
  project_type: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface ProjectManagerProps {
  onProjectSelect?: (project: Project) => void;
  currentProject?: Project | null;
  projects?: Project[];
  onRefreshProjects?: () => void;
}

export default function ProjectManager({ onProjectSelect, currentProject, projects: externalProjects, onRefreshProjects }: ProjectManagerProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [editForm, setEditForm] = useState({ name: '', description: '' });
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (externalProjects) {
      setProjects(externalProjects);
      setLoading(false);
    } else {
      loadProjects();
    }
  }, [externalProjects]);

  const loadProjects = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('projects')
        .select('*')
        .eq('user_id', user.id)
        .order('updated_at', { ascending: false });

      if (error) {
        console.error('Error loading projects:', error);
      } else {
        setProjects(data || []);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEditProject = (project: Project, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    setEditingProject(project);
    
    // Parse the description to get the clean text for editing
    const { description } = parseProjectDescription(project.description);
    setEditForm({ name: project.name, description: description || '' });
    setIsEditModalOpen(true);
  };

  const saveProjectChanges = async () => {
    if (!editingProject) return;

    try {
      // Parse existing description to preserve metadata
      const { metadata } = parseProjectDescription(editingProject.description);
      
      // Save description in consistent JSON format
      const descriptionToSave = JSON.stringify({
        description: editForm.description.trim() || null,
        metadata: metadata
      });

      const { data, error } = await supabase
        .from('projects')
        .update({
          name: editForm.name,
          description: descriptionToSave,
          updated_at: new Date().toISOString()
        })
        .eq('id', editingProject.id)
        .select()
        .single();

      if (error) throw error;

      // Update local state
      const updatedProjects = projects.map(p => 
        p.id === editingProject.id ? data : p
      );
      setProjects(updatedProjects);

      // Refresh projects in parent if callback exists
      if (onRefreshProjects) {
        onRefreshProjects();
      }

      toast({
        title: "Project Updated",
        description: "Project changes have been saved successfully.",
      });

      setIsEditModalOpen(false);
      setEditingProject(null);
    } catch (error) {
      console.error('Error updating project:', error);
      toast({
        title: "Error",
        description: "Failed to update project.",
        variant: "destructive",
      });
    }
  };



  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Loading Projects...</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Project Management</CardTitle>
              <CardDescription>
                Manage your steganography projects and settings
              </CardDescription>
            </div>
            
            <Button 
              variant="outline" 
              size="sm"
              onClick={onRefreshProjects}
              disabled={!onRefreshProjects}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {projects.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No Projects Yet</h3>
              <p className="text-gray-600 mb-4">
                Create your first project to start organizing your steganography operations.
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Projects will appear here once you create them from the steganography operations.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project) => {
                // Parse description to show clean text
                const { description } = parseProjectDescription(project.description);
                
                return (
                <Card 
                  key={project.id} 
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    currentProject?.id === project.id ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => onProjectSelect && onProjectSelect(project)}
                >
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base truncate">{project.name}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{project.project_type}</Badge>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => handleEditProject(project, e)}
                          className="h-7 w-7 p-0"
                        >
                          <Edit className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                    {description && (
                      <CardDescription className="text-sm line-clamp-2">
                        {description}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {formatDate(project.created_at)}
                      </div>
                    </div>
                  </CardContent>
                </Card>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Project Dialog */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
            <DialogDescription>
              Update your project name and description.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="project-name">Project Name</Label>
              <Input
                id="project-name"
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                placeholder="Enter project name"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="project-description">Description</Label>
              <Textarea
                id="project-description"
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                placeholder="Enter project description (optional)"
                rows={3}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveProjectChanges}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}