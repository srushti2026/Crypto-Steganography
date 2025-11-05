import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { ProjectFileService } from "@/services/projectFileService";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { Plus, Settings, FileText, Clock, Lock, Download, File, FolderOpen } from "lucide-react";

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
}

export default function ProjectManager({ onProjectSelect, currentProject }: ProjectManagerProps) {
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [projectFiles, setProjectFiles] = useState<any[]>([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  
  // Form states
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [projectPassword, setProjectPassword] = useState("");
  const [projectSettings, setProjectSettings] = useState({
    defaultEncryption: "xor_md5",
    autoBackup: false,
    compressionLevel: "medium"
  });

  useEffect(() => {
    loadProjects();
  }, []);

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
        toast({
          title: "Error",
          description: "Failed to load projects",
          variant: "destructive"
        });
      } else {
        setProjects(data || []);
      }
    } catch (error) {
      console.error('Error loading projects:', error);
      toast({
        title: "Error",
        description: "Failed to load projects",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!projectName.trim()) {
      toast({
        title: "Error",
        description: "Project name is required",
        variant: "destructive"
      });
      return;
    }

    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: user.id,
            name: projectName.trim(),
            description: projectDescription.trim(),
            project_type: 'steganography'
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('Error creating project:', error);
        toast.error("Failed to create project");
      } else {
        toast.success("Project created successfully!");
        setProjects([data, ...projects]);
        setCreateDialogOpen(false);
        clearForm();
        
        // Auto-select the new project
        if (onProjectSelect) {
          onProjectSelect(data);
        }
      }
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error("Failed to create project");
    }
  };

  const updateProjectSettings = async () => {
    if (!selectedProject) return;

    try {
      const { error } = await supabase
        .from('projects')
        .update({
          name: projectName.trim(),
          description: projectDescription.trim(),
          password_hash: projectPassword ? btoa(projectPassword) : null,
          settings: projectSettings,
          updated_at: new Date().toISOString()
        })
        .eq('id', selectedProject.id);

      if (error) {
        console.error('Error updating project:', error);
        toast.error("Failed to update project settings");
      } else {
        toast.success("Project settings updated successfully!");
        setSettingsDialogOpen(false);
        loadProjects(); // Reload to get updated data
      }
    } catch (error) {
      console.error('Error updating project:', error);
      toast.error("Failed to update project settings");
    }
  };

  const clearForm = () => {
    setProjectName("");
    setProjectDescription("");
    setProjectPassword("");
    setProjectSettings({
      defaultEncryption: "xor_md5",
      autoBackup: false,
      compressionLevel: "medium"
    });
  };

  const loadProjectFiles = async (projectId: string) => {
    setLoadingFiles(true);
    try {
      const files = await ProjectFileService.getProjectFiles(projectId);
      setProjectFiles(files);
    } catch (error) {
      console.error('Error loading project files:', error);
      toast.error("Failed to load project files");
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleDownloadFile = async (fileId: string, fileName: string) => {
    try {
      await ProjectFileService.downloadProjectFile(fileId, fileName);
      toast.success("File download started");
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error("Failed to download file");
    }
  };

  const openSettingsDialog = (project: Project) => {
    setSelectedProject(project);
    setProjectName(project.name);
    setProjectDescription(project.description || "");
    setProjectPassword(""); // Don't show existing password
    setProjectSettings(project.settings || {
      defaultEncryption: "xor_md5",
      autoBackup: false,
      compressionLevel: "medium"
    });
    setSettingsDialogOpen(true);
    
    // Load project files
    loadProjectFiles(project.id);
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
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">My Projects</h2>
          <p className="text-muted-foreground">
            Manage your steganography projects and settings
          </p>
        </div>
        
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
              <DialogDescription>
                Create a new project to organize your steganography operations.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <Label htmlFor="project-name">Project Name</Label>
                <Input
                  id="project-name"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  placeholder="Enter project name"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="project-description">Description</Label>
                <Textarea
                  id="project-description"
                  value={projectDescription}
                  onChange={(e) => setProjectDescription(e.target.value)}
                  placeholder="Optional project description"
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="project-password">Project Password (Optional)</Label>
                <Input
                  id="project-password"
                  type="password"
                  value={projectPassword}
                  onChange={(e) => setProjectPassword(e.target.value)}
                  placeholder="Optional password for project protection"
                />
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={createProject}>Create Project</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Current Project */}
      {currentProject && (
        <Card className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <div className="w-2 h-2 bg-primary rounded-full"></div>
                Current Project: {currentProject.name}
              </CardTitle>
              <Button 
                variant="ghost" 
                size="sm"
                onClick={() => openSettingsDialog(currentProject)}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Files Protected</span>
                <p className="font-semibold">{currentProject.files_protected}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Total Operations</span>
                <p className="font-semibold">{currentProject.total_operations}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Last Updated</span>
                <p className="font-semibold">{formatDate(currentProject.updated_at)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <Card className="p-8 text-center">
          <div className="mx-auto w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
            <FileText className="h-8 w-8 text-primary" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
          <p className="text-muted-foreground mb-4">
            Create your first project to start organizing your steganography operations.
          </p>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create First Project
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <Card 
              key={project.id} 
              className={`cursor-pointer transition-all hover:shadow-lg ${
                currentProject?.id === project.id ? 'border-primary bg-primary/5' : ''
              }`}
              onClick={() => onProjectSelect && onProjectSelect(project)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-base line-clamp-1">
                      {project.name}
                    </CardTitle>
                    {project.description && (
                      <CardDescription className="line-clamp-2 mt-1">
                        {project.description}
                      </CardDescription>
                    )}
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      openSettingsDialog(project);
                    }}
                  >
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Files Protected</span>
                    <Badge variant="secondary">{project.files_protected}</Badge>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Operations</span>
                    <Badge variant="outline">{project.total_operations}</Badge>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatDate(project.updated_at)}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Project Settings Dialog */}
      <Dialog open={settingsDialogOpen} onOpenChange={setSettingsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Project Settings</DialogTitle>
            <DialogDescription>
              Manage settings for {selectedProject?.name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="settings-name">Project Name</Label>
              <Input
                id="settings-name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="settings-description">Description</Label>
              <Textarea
                id="settings-description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder="Project description"
                rows={3}
              />
            </div>
            
            <div>
              <Label htmlFor="settings-password">Project Password</Label>
              <Input
                id="settings-password"
                type="password"
                value={projectPassword}
                onChange={(e) => setProjectPassword(e.target.value)}
                placeholder="Leave empty to keep current password"
              />
            </div>

            <div>
              <Label htmlFor="encryption-method">Default Encryption Method</Label>
              <select
                id="encryption-method"
                className="w-full p-2 border rounded-md"
                value={projectSettings.defaultEncryption}
                onChange={(e) => setProjectSettings({
                  ...projectSettings,
                  defaultEncryption: e.target.value
                })}
              >
                <option value="xor_md5">XOR with MD5</option>
                <option value="aes">AES Encryption</option>
                <option value="base64">Base64 Encoding</option>
              </select>
            </div>
            
            {/* File Management Section */}
            <div className="border-t pt-4 mt-6">
              <div className="flex items-center gap-2 mb-3">
                <FolderOpen className="w-4 h-4" />
                <Label className="text-base font-semibold">Project Files</Label>
              </div>
              
              {loadingFiles ? (
                <p className="text-sm text-gray-500">Loading files...</p>
              ) : projectFiles.length === 0 ? (
                <p className="text-sm text-gray-500">No files uploaded yet. Upload files through the steganography operations to see them here.</p>
              ) : (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {projectFiles.map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2 flex-1">
                        <File className="w-4 h-4 text-gray-600" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{file.file_name}</p>
                          <p className="text-xs text-gray-500">
                            {file.is_carrier ? 'Carrier File' : file.is_processed ? 'Processed File' : 'Unknown'} •{' '}
                            {file.file_size ? `${(file.file_size / 1024 / 1024).toFixed(2)} MB` : 'Unknown size'} •{' '}
                            {new Date(file.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      {file.file_url && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDownloadFile(file.id, file.file_name)}
                          className="shrink-0"
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <p className="text-xs text-blue-800">
                  <strong>File Tracking:</strong> Files are automatically tracked when you upload and process them through steganography operations. 
                  This helps you manage and download your files later.
                </p>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setSettingsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={updateProjectSettings}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}