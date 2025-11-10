-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE NOT NULL,
    username text UNIQUE NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Steganography operations table
CREATE TABLE IF NOT EXISTS steganography_operations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    operation_type text NOT NULL CHECK (operation_type IN ('hide', 'extract')),
    media_type text NOT NULL CHECK (media_type IN ('video', 'audio', 'image', 'document')),
    original_filename text NOT NULL,
    output_filename text,
    file_size bigint,
    message_preview text,
    password_hash text NOT NULL,
    encryption_method text DEFAULT 'xor_md5',
    success boolean DEFAULT false,
    error_message text,
    processing_time real,
    created_at timestamp with time zone DEFAULT now()
);

-- File metadata table
CREATE TABLE IF NOT EXISTS file_metadata (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id uuid REFERENCES steganography_operations(id) ON DELETE CASCADE,
    file_type text NOT NULL,
    mime_type text,
    file_path text,
    file_hash text,
    file_size bigint,
    dimensions text,
    duration real,
    created_at timestamp with time zone DEFAULT now()
);

-- Projects table (for dashboard functionality)
CREATE TABLE IF NOT EXISTS projects (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    name text NOT NULL,
    description text,
    project_type text DEFAULT 'general' CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault')),
    settings jsonb DEFAULT '{}',
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Files table (for project file management)
CREATE TABLE IF NOT EXISTS files (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
    filename text NOT NULL,
    file_type text NOT NULL CHECK (file_type IN ('input', 'output')),
    file_size bigint,
    mime_type text,
    created_at timestamp with time zone DEFAULT now()
);

-- Activities table (for tracking operations)
CREATE TABLE IF NOT EXISTS activities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    activity_type text NOT NULL,
    description text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);

-- Profiles table (for user profile management)
CREATE TABLE IF NOT EXISTS profiles (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    updated_at timestamp with time zone DEFAULT now(),
    last_sign_in_at timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);

-- Complaints table (for contact/feedback functionality)
CREATE TABLE IF NOT EXISTS complaints (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    email text NOT NULL,
    subject text NOT NULL,
    message text NOT NULL,
    status text DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'resolved', 'closed')),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_operations_user_id ON steganography_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_operations_created_at ON steganography_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_operations_media_type ON steganography_operations(media_type);
CREATE INDEX IF NOT EXISTS idx_metadata_operation_id ON file_metadata(operation_id);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_files_project_id ON files(project_id);
CREATE INDEX IF NOT EXISTS idx_activities_project_id ON activities(project_id);
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);

-- Row Level Security (RLS) Policies
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE complaints ENABLE ROW LEVEL SECURITY;

-- Projects policies
CREATE POLICY "Users can view their own projects" ON projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own projects" ON projects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own projects" ON projects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own projects" ON projects FOR DELETE USING (auth.uid() = user_id);

-- Files policies
CREATE POLICY "Users can view files from their projects" ON files FOR SELECT USING (
  EXISTS (SELECT 1 FROM projects WHERE projects.id = files.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can insert files to their projects" ON files FOR INSERT WITH CHECK (
  EXISTS (SELECT 1 FROM projects WHERE projects.id = files.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can update files from their projects" ON files FOR UPDATE USING (
  EXISTS (SELECT 1 FROM projects WHERE projects.id = files.project_id AND projects.user_id = auth.uid())
);
CREATE POLICY "Users can delete files from their projects" ON files FOR DELETE USING (
  EXISTS (SELECT 1 FROM projects WHERE projects.id = files.project_id AND projects.user_id = auth.uid())
);

-- Activities policies  
CREATE POLICY "Users can view activities from their projects" ON activities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own activities" ON activities FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Profiles policies
CREATE POLICY "Users can view their own profile" ON profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own profile" ON profiles FOR UPDATE USING (auth.uid() = user_id);

-- Complaints policies (allow unauthenticated users to submit)
CREATE POLICY "Anyone can insert complaints" ON complaints FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can view their own complaints" ON complaints FOR SELECT USING (auth.uid() = user_id OR user_id IS NULL);