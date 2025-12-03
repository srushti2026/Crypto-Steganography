import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Link } from "react-router-dom";
import { 
  Plus, 
  FileImage, 
  Shield, 
  Lock, 
  Calendar, 
  Download, 
  Eye, 
  Trash2, 
  Settings,
  FolderOpen,
  Activity,
  Clock,
  BarChart3,
  FileText,
  Check,
  Sparkles
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import ProjectManager from "@/components/ProjectManager";

// Helper function to format layered container descriptions for display
const formatLayeredContainerDescription = (data: any): string => {
  try {
    // Check if we have a layered container
    if (data.type === 'layered_container' && data.layers && Array.isArray(data.layers)) {
      const layerCount = data.layers.length;
      
      if (layerCount === 1) {
        // Single layer - show the filename
        const layer = data.layers[0];
        const filename = layer.filename || 'extracted_file';
        // Clean filename for display
        const cleanName = filename.replace(/^(stego_|carrier_|content_)/, '')
                                  .replace(/_\d{10}_[a-f0-9]{8}/g, '')
                                  .replace(/_+/g, '_')
                                  .replace(/^_|_$/g, '');
        return `Extracted file: ${cleanName || 'file'}`;
      } else {
        // Multiple layers - show count and filenames
        const fileNames = data.layers
          .map((layer: any) => {
            const filename = layer.filename || 'file';
            return filename.replace(/^(stego_|carrier_|content_)/, '')
                          .replace(/_\d{10}_[a-f0-9]{8}/g, '')
                          .replace(/_+/g, '_')
                          .replace(/^_|_$/g, '') || 'file';
          })
          .join(', ');
        return `Extracted ${layerCount} files: ${fileNames}`;
      }
    }
  } catch (e) {
    // Not a layered container
  }
  
  // Return original data as string if not a layered container
  return typeof data === 'string' ? data : JSON.stringify(data);
};

// Helper function to parse project description
const parseProjectDescription = (description: string | null) => {
  if (!description) return { description: "", metadata: {} };
  
  // First, check if it's a JSON string
  if (description.trim().startsWith('{')) {
    try {
      const parsed = JSON.parse(description);
      
      if (parsed.description !== undefined) {
        // Standard project format with metadata - extract the inner description
        let displayDescription = parsed.description || "";
        
        // Check if we have extraction results with layered containers in metadata
        if (parsed.metadata && parsed.metadata.extractedContent) {
          const extractedContent = parsed.metadata.extractedContent;
          
          // Check if extractedContent has layered container in text_content
          if (extractedContent.text_content) {
            try {
              const layeredData = JSON.parse(extractedContent.text_content);
              if (layeredData.type === 'layered_container') {
                const formattedDesc = formatLayeredContainerDescription(layeredData);
                displayDescription = formattedDesc;
              }
            } catch (e) {
              // Not a layered container in text_content
              if (extractedContent.extracted_filename) {
                displayDescription = `Extracted file: ${extractedContent.extracted_filename}`;
              }
            }
          } else if (extractedContent.extracted_filename) {
            displayDescription = `Extracted file: ${extractedContent.extracted_filename}`;
          }
        }
        
        return {
          description: displayDescription,
          metadata: parsed.metadata || {}
        };
      } else if (parsed.type === 'layered_container') {
        // Direct layered container format
        return {
          description: formatLayeredContainerDescription(parsed),
          metadata: {}
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

interface ProjectFile {
  id: string;
  file_name: string;
  file_type: string;
  file_url?: string;
  file_size?: number;
  is_carrier?: boolean;
  is_processed?: boolean;
  encryption_method?: string;
  created_at: string;
}

interface ProjectFilesDisplayProps {
  project: any;
}

interface AllProjectFilesDisplayProps {
  user: any;
  projects: any[];
}

function AllProjectFilesDisplay({ user, projects }: AllProjectFilesDisplayProps) {
  const [allFiles, setAllFiles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    if (user) {
      loadAllProjectFiles();
    }
  }, [user, projects]);

  const loadAllProjectFiles = async () => {
    try {
      const { data, error } = await supabase
        .from("files")
        .select(`
          *,
          projects(name, project_type)
        `)
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (error) throw error;

      setAllFiles(data || []);
    } catch (error) {
      console.error('❌ Error loading all project files:', error);
      toast({
        title: "Error",
        description: "Failed to load project files.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2">Loading files...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          All Project Files
        </CardTitle>
        <CardDescription>
          Files from all your steganography projects ({allFiles.length} total)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {allFiles.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No Files Yet</h3>
            <p>Start uploading and processing files to see them here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {allFiles.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="flex-shrink-0">
                    {file.is_processed ? (
                      <Badge variant="default">Processed</Badge>
                    ) : (
                      <Badge variant="secondary">Uploaded</Badge>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate" title={file.file_name}>
                      {file.file_name}
                    </p>
                    <p className="text-sm text-gray-500 truncate">
                      Project: {file.projects?.name || 'Unknown Project'} ({file.projects?.project_type})
                      {file.file_size && ` • ${(file.file_size / 1024 / 1024).toFixed(2)} MB`}
                      {file.encryption_method && ` • ${file.encryption_method} encryption`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  <Button size="sm" variant="outline" asChild>
                    <a 
                      href={file.file_url || `/api/files/download/${file.id}`} 
                      download={file.file_name}
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </a>
                  </Button>
                  <span className="text-xs text-gray-400">
                    {new Date(file.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface ProjectFilesDisplayProps {
  project: any;
  refreshTrigger?: number; // Optional prop to trigger refresh
}

export function ProjectFilesDisplay({ project, refreshTrigger }: ProjectFilesDisplayProps) {
  const [files, setFiles] = useState<ProjectFile[]>([]);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    loadProjectFiles();
  }, [project.id, refreshTrigger]);

  const loadProjectFiles = async () => {
    try {
      setLoading(true);
      console.log('📁 Loading files for project:', project.id);
      
      const { data, error } = await supabase
        .from('files')
        .select('*')
        .eq('project_id', project.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      
      console.log('📁 Found files:', data);
      setFiles(data || []);
    } catch (error) {
      console.error('❌ Error loading project files:', error);
      toast({
        title: "Error",
        description: "Failed to load project files.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-2">Loading files...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Files in {project.name}</CardTitle>
        <CardDescription>
          {files.length} files found
        </CardDescription>
      </CardHeader>
      <CardContent>
        {files.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold mb-2">No Files Yet</h3>
            <p className="text-gray-600">
              Files will appear here when you upload and process them in steganography operations.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="flex-shrink-0">
                    {file.is_processed ? (
                      <Badge variant="default">Processed</Badge>
                    ) : (
                      <Badge variant="secondary">Uploaded</Badge>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate" title={file.file_name}>
                      {file.file_name}
                    </p>
                    <p className="text-sm text-gray-500 truncate">
                      {file.file_size && `${(file.file_size / 1024 / 1024).toFixed(2)} MB`}
                      {file.encryption_method && ` • ${file.encryption_method} encryption`}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2 flex-shrink-0">
                  <Button size="sm" variant="outline" asChild>
                    <a 
                      href={file.file_url || `/api/files/download/${file.id}`} 
                      download={file.file_name}
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </a>
                  </Button>
                  <span className="text-xs text-gray-400">
                    {new Date(file.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [selectedTab, setSelectedTab] = useState("overview");
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [currentProject, setCurrentProject] = useState<any>(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [projectToDelete, setProjectToDelete] = useState<any>(null);
  const [dashboardStats, setDashboardStats] = useState({
    totalProjects: 0,
    filesProtected: 0,
    totalOperations: 0
  });

  const handleOpenProject = (project: any) => {
    console.log('🔓 Opening existing project:', project);
    setCurrentProject(project);
    navigate(`/${project.project_type}`, { 
      state: { 
        existingProject: project,
        projectToOpen: true
      } 
    });
  };

  const handleProjectTypeSelect = async (type: string) => {
    if (!user) {
      toast({
        title: "Authentication Required",
        description: "Please log in to create a project.",
        variant: "destructive",
      });
      return;
    }

    try {
      // Create a new project of the selected type
      const projectNames = {
        general: 'General Steganography Project',
        pixelvault: 'PixelVault AI Project',
        copyright: 'Copyright Protection Project',
        forensic: 'Forensic Evidence Project'
      };

      const projectDescriptions = {
        general: 'General purpose steganography operations for hiding data in various media files',
        pixelvault: 'AI-powered image generation with seamless data embedding and security',
        copyright: 'Copyright protection and digital watermarking project',
        forensic: 'Forensic steganography for evidence collection and analysis'
      };

      const { data: newProject, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: user.id,
            name: projectNames[type as keyof typeof projectNames],
            description: projectDescriptions[type as keyof typeof projectDescriptions],
            project_type: type
          }
        ])
        .select()
        .single();

      if (error) throw error;

      // Refresh projects list to include the new project
      await fetchProjects(user.id);

      toast({
        title: "Project Created",
        description: `New ${type} project created successfully!`,
      });

      console.log('✅ New project created:', newProject);

      setIsProjectModalOpen(false);
      
      // Navigate to the appropriate page with the new project
      navigate(`/${type}`, { 
        state: { 
          newProject: newProject,
          projectJustCreated: true
        } 
      });
    } catch (error) {
      console.error('❌ Error creating project:', error);
      toast({
        title: "Error",
        description: `Failed to create ${type} project: ${error.message}`,
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    checkAuthAndLoadData();
    
    // Refresh data when page becomes visible (user returns from other pages)
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('📊 Dashboard: Page became visible, refreshing data...');
        checkAuthAndLoadData();
      }
    };
    
    const handleFocus = () => {
      console.log('📊 Dashboard: Window focused, refreshing data...');
      checkAuthAndLoadData();
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  const checkAuthAndLoadData = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      navigate("/auth");
      return;
    }

    setUser(user);
    await Promise.all([
      fetchProjects(user.id),
      fetchDashboardStats(user.id)
    ]);
  };

  const fetchProjects = async (userId: string) => {
    try {
      console.log('📊 Dashboard: Fetching projects for user:', userId);
      
      const { data, error } = await supabase
        .from("projects")
        .select("*")
        .eq("user_id", userId)
        .order("updated_at", { ascending: false });

      console.log('📊 Dashboard: Projects query result:', { data, error });

      if (error) throw error;
      
      // Fetch statistics for each project
      const projectsWithStats = await Promise.all((data || []).map(async (project) => {
        const [filesCount, operationsCount] = await Promise.all([
          // Count files for this project
          supabase
            .from("files")
            .select("id", { count: 'exact' })
            .eq("project_id", project.id),
          // Count activities/operations for this project
          supabase
            .from("activities")
            .select("id", { count: 'exact' })
            .eq("project_id", project.id)
        ]);

        return {
          ...project,
          files_protected: filesCount.count || 0,
          total_operations: operationsCount.count || 0
        };
      }));
      
      setProjects(projectsWithStats);
      console.log('📊 Dashboard: Set projects with stats:', projectsWithStats);
      
      // Set first project as current if none selected
      if (projectsWithStats && projectsWithStats.length > 0 && !currentProject) {
        setCurrentProject(projectsWithStats[0]);
        console.log('📊 Dashboard: Set current project:', projectsWithStats[0]);
      }
    } catch (error) {
      console.error("❌ Dashboard: Error fetching projects:", error);
      toast({
        title: "Error",
        description: "Failed to load projects.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDashboardStats = async (userId: string) => {
    try {
      // Get project statistics
      const { data: projectData, error: projectError } = await supabase
        .from("projects")
        .select("id, name")
        .eq("user_id", userId);

      if (projectError) throw projectError;

      // Get files count for the user
      const { data: filesData, error: filesError } = await supabase
        .from("files")
        .select("id")
        .eq("user_id", userId);

      if (filesError) throw filesError;

      // Get recent operations count (last 7 days)
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
      
      const { data: recentOps, error: opsError } = await supabase
        .from("activities")
        .select("id")
        .eq("user_id", userId)
        .gte("created_at", sevenDaysAgo.toISOString());

      if (opsError) throw opsError;

      // Get total operations count
      const { data: allOps, error: allOpsError } = await supabase
        .from("activities")
        .select("id")
        .eq("user_id", userId);

      if (allOpsError) throw allOpsError;

      // Calculate totals
      const totalProjects = projectData?.length || 0;
      const filesProtected = filesData?.length || 0;
      const totalOperations = allOps?.length || 0;

      setDashboardStats({
        totalProjects,
        filesProtected,
        totalOperations
      });

    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const createQuickProject = async () => {
    try {
      if (!user) return;

      const projectName = `Project ${new Date().toLocaleDateString()}`;
      
      const { data, error } = await supabase
        .from('projects')
        .insert([
          {
            user_id: user.id,
            name: projectName,
            description: 'Auto-created project',
            project_type: 'general'
          }
        ])
        .select()
        .single();

      if (error) {
        console.error('Error creating project:', error);
        throw error;
      }

      // Refresh projects list
      await fetchProjects(user.id);
      setCurrentProject(data);
      
      toast({
        title: "Project Created",
        description: `${projectName} has been created successfully.`,
      });

      return data;
    } catch (error) {
      console.error("Error creating project:", error);
      toast({
        title: "Error",
        description: "Failed to create project.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      // First delete associated files
      const { error: filesError } = await supabase
        .from("files")
        .delete()
        .eq("project_id", projectId);

      if (filesError) {
        console.warn("Error deleting project files:", filesError);
        // Continue with project deletion even if files deletion fails
      }

      // Delete associated activities
      const { error: activitiesError } = await supabase
        .from("activities")
        .delete()
        .eq("project_id", projectId);

      if (activitiesError) {
        console.warn("Error deleting project activities:", activitiesError);
        // Continue with project deletion even if activities deletion fails
      }

      // Finally delete the project itself
      const { error } = await supabase
        .from("projects")
        .delete()
        .eq("id", projectId);

      if (error) throw error;

      setProjects(projects.filter(p => p.id !== projectId));
      toast({
        title: "Project Deleted",
        description: "Project and all associated data have been deleted successfully.",
      });
    } catch (error) {
      console.error("Error deleting project:", error);
      toast({
        title: "Error",
        description: "Failed to delete project.",
        variant: "destructive",
      });
    }
  };

  const handleDeleteClick = (project: any) => {
    setProjectToDelete(project);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (projectToDelete) {
      await handleDeleteProject(projectToDelete.id);
      setDeleteConfirmOpen(false);
      setProjectToDelete(null);
    }
  };

  const cancelDelete = () => {
    setDeleteConfirmOpen(false);
    setProjectToDelete(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "general":
        return <FileImage className="h-4 w-4" />;
      case "copyright":
        return <Shield className="h-4 w-4" />;
      case "forensic":
        return <Lock className="h-4 w-4" />;
      default:
        return <FileImage className="h-4 w-4" />;
    }
  };

  const getTypeBadgeColor = (type: string) => {
    switch (type) {
      case "general":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "copyright":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "forensic":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";
    }
  };

  const stats = {
    totalProjects: dashboardStats.totalProjects,
    activeProjects: dashboardStats.totalProjects,
    processedFiles: dashboardStats.filesProtected
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20">
        {/* Header Section */}
        <section className="py-8 bg-gradient-to-r from-primary/5 to-sea-light/10 dark:from-primary/10 dark:to-background">
          <div className="container">
            <div className="flex items-center justify-between">
              <div className="animate-fade-in">
                <h1 className="text-3xl md:text-4xl font-bold mb-2">Welcome back!</h1>
                <p className="text-muted-foreground">
                  Manage your steganography projects and protected data from your secure dashboard
                </p>
              </div>
              
              <div className="animate-fade-in [animation-delay:200ms] flex gap-3">
                <Button asChild size="lg" variant="outline">
                  <Link to="/home#demo">
                    <Eye className="mr-2 h-4 w-4" />
                    Watch Demo
                  </Link>
                </Button>
                <Dialog open={isProjectModalOpen} onOpenChange={setIsProjectModalOpen}>
                  <DialogTrigger asChild>
                    <Button size="lg" className="btn-primary">
                      <Plus className="mr-2 h-4 w-4" />
                      New Project
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-md max-h-[85vh] overflow-y-auto">
                    <DialogHeader className="pb-4 space-y-2">
                      <DialogTitle className="text-xl font-bold text-center">Create New Project</DialogTitle>
                      <DialogDescription className="text-center text-sm text-muted-foreground">
                        Choose the type of steganography project you'd like to create
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-3">
                      <Button
                        onClick={() => handleProjectTypeSelect('general')}
                        variant="outline"
                        className="group w-full flex items-center h-auto p-4 text-left hover:bg-primary/10 hover:border-primary/50 transition-all duration-300"
                      >
                        <div className="mr-4 p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors flex-shrink-0">
                          <FileImage className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-base mb-1 group-hover:text-primary transition-colors">General Steganography</div>
                          <div className="text-xs text-muted-foreground leading-tight">
                            Hide any type of data in images, audio, or video files
                          </div>
                        </div>
                      </Button>
                      
                      <Button
                        onClick={() => handleProjectTypeSelect('copyright')}
                        variant="outline"
                        className="group w-full flex items-center h-auto p-4 text-left hover:bg-primary/10 hover:border-primary/50 transition-all duration-300"
                      >
                        <div className="mr-4 p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors flex-shrink-0">
                          <Shield className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-base mb-1 group-hover:text-primary transition-colors">Copyright Protection</div>
                          <div className="text-xs text-muted-foreground leading-tight">
                            Embed copyright information to protect your property
                          </div>
                        </div>
                      </Button>
                      
                      <Button
                        onClick={() => handleProjectTypeSelect('pixelvault')}
                        variant="outline"
                        className="group w-full flex items-center h-auto p-4 text-left hover:bg-gradient-to-r hover:from-cyan-50 hover:to-purple-50 hover:border-cyan-500/50 transition-all duration-300"
                      >
                        <div className="mr-4 p-2 rounded-lg bg-gradient-to-r from-cyan-100 to-purple-100 group-hover:from-cyan-200 group-hover:to-purple-200 transition-colors flex-shrink-0">
                          <Sparkles className="h-5 w-5 text-cyan-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-base mb-1 group-hover:text-cyan-700 transition-colors">PixelVault</div>
                          <div className="text-xs text-muted-foreground leading-tight">
                            Generate AI images and embed secret data seamlessly
                          </div>
                        </div>
                      </Button>
                      
                      <Button
                        onClick={() => handleProjectTypeSelect('forensic')}
                        variant="outline"
                        className="group w-full flex items-center h-auto p-4 text-left hover:bg-primary/10 hover:border-primary/50 transition-all duration-300"
                      >
                        <div className="mr-4 p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors flex-shrink-0">
                          <Lock className="h-5 w-5 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-base mb-1 group-hover:text-primary transition-colors">Forensic Evidence</div>
                          <div className="text-xs text-muted-foreground leading-tight">
                            Securely embed forensic data and evidence in files
                          </div>
                        </div>
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Cards */}
        <section className="py-8">
          <div className="container">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="animate-fade-in">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Total Projects</p>
                      <p className="text-2xl font-bold">{stats.totalProjects}</p>
                    </div>
                    <FolderOpen className="h-8 w-8 text-primary" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="animate-fade-in [animation-delay:100ms]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Active Projects</p>
                      <p className="text-2xl font-bold text-green-600">{stats.activeProjects}</p>
                    </div>
                    <Activity className="h-8 w-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="animate-fade-in [animation-delay:200ms]">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Files Processed</p>
                      <p className="text-2xl font-bold text-blue-600">{stats.processedFiles}</p>
                    </div>
                    <BarChart3 className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Projects Management */}
        <section className="py-8">
          <div className="container">
            <ProjectManager 
              onProjectSelect={setCurrentProject}
              currentProject={currentProject}
              projects={projects}
              onRefreshProjects={() => user && fetchProjects(user.id)}
            />
          </div>
        </section>

        {/* Tabs for Additional Features */}
        <section className="py-8">
          <div className="container">
            <Tabs value={selectedTab} onValueChange={setSelectedTab} className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="files">Project Files</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="space-y-6">
                <div className="grid gap-6">
                  {projects.length > 0 && projects.map((project, index) => {
                    const { description } = parseProjectDescription(project.description);
                    return (
                      <Card key={project.id} className="animate-fade-in hover:shadow-lg transition-all duration-300">
                        <CardHeader>
                          <CardTitle>{project.name}</CardTitle>
                          <CardDescription>{description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="flex justify-between items-center">
                            <div className="text-sm text-muted-foreground">
                              Files Protected: {project.files_protected} | Operations: {project.total_operations}
                            </div>
                            <div className="flex items-center space-x-2">
                              <Button 
                                variant="outline" 
                                size="sm" 
                                onClick={() => handleOpenProject(project)}
                              >
                                <FolderOpen className="h-4 w-4 mr-1" />
                                Open Project
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleDeleteClick(project)}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 border-blue-200"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </TabsContent>
              
              
              <TabsContent value="files" className="space-y-4">
                <AllProjectFilesDisplay user={user} projects={projects} />
              </TabsContent>
            </Tabs>
          </div>
        </section>
      </main>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <Trash2 className="h-5 w-5 text-blue-600" />
              <span>Delete Project</span>
            </DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the project "{projectToDelete?.name}"? 
              <br />
              <span className="text-blue-600 font-medium">
                This action cannot be undone and will permanently remove all project data, files, and settings.
              </span>
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 mt-4">
            <Button 
              variant="outline" 
              onClick={cancelDelete}
            >
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={confirmDelete}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Delete Project
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      
      <Footer />
    </div>
  );
}

