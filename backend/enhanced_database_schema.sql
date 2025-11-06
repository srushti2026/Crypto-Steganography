-- Enhanced Database Schema for Production-Ready VeilForge
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enhanced Users table with profile information
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE NOT NULL,
    username text UNIQUE NOT NULL,
    full_name text,
    profile_photo_url text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    last_login timestamp with time zone,
    login_count integer DEFAULT 0
);

-- Projects table - each user can have multiple projects
CREATE TABLE IF NOT EXISTS projects (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    name text NOT NULL,
    description text,
    password_hash text, -- Optional project-level password
    settings jsonb DEFAULT '{}', -- Store project settings as JSON
    files_protected integer DEFAULT 0,
    total_operations integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    UNIQUE(user_id, name) -- Prevent duplicate project names per user
);

-- Enhanced Steganography operations table with project association
CREATE TABLE IF NOT EXISTS steganography_operations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    project_id uuid REFERENCES projects(id) ON DELETE SET NULL, -- Optional project association
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

-- File storage table - stores both uploaded and processed files
CREATE TABLE IF NOT EXISTS project_files (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id uuid REFERENCES projects(id) ON DELETE CASCADE,
    operation_id uuid REFERENCES steganography_operations(id) ON DELETE SET NULL,
    file_name text NOT NULL,
    file_type text NOT NULL, -- 'uploaded' or 'processed'
    file_path text, -- Path in storage system
    file_url text, -- Public URL for downloads
    mime_type text,
    file_size bigint,
    file_hash text, -- For integrity checking
    metadata jsonb DEFAULT '{}', -- Store additional file metadata
    created_at timestamp with time zone DEFAULT now()
);

-- User feedback table
CREATE TABLE IF NOT EXISTS user_feedback (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    name text,
    email text,
    subject text,
    message text NOT NULL,
    rating integer CHECK (rating >= 1 AND rating <= 5),
    status text DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'resolved', 'closed')),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- User sessions table for remember me functionality
CREATE TABLE IF NOT EXISTS user_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    session_token text UNIQUE NOT NULL,
    device_info text,
    ip_address text,
    remember_me boolean DEFAULT false,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    last_accessed timestamp with time zone DEFAULT now()
);

-- File metadata table (keeping for backward compatibility)
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

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_operations_user_id ON steganography_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_operations_project_id ON steganography_operations(project_id);
CREATE INDEX IF NOT EXISTS idx_operations_created_at ON steganography_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_operations_media_type ON steganography_operations(media_type);
CREATE INDEX IF NOT EXISTS idx_project_files_project_id ON project_files(project_id);
CREATE INDEX IF NOT EXISTS idx_project_files_operation_id ON project_files(operation_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_status ON user_feedback(status);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_metadata_operation_id ON file_metadata(operation_id);

-- Functions to update counters
CREATE OR REPLACE FUNCTION update_project_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.success = true THEN
        UPDATE projects 
        SET 
            files_protected = files_protected + 1,
            total_operations = total_operations + 1,
            updated_at = now()
        WHERE id = NEW.project_id;
    ELSIF TG_OP = 'INSERT' THEN
        UPDATE projects 
        SET 
            total_operations = total_operations + 1,
            updated_at = now()
        WHERE id = NEW.project_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update project statistics
DROP TRIGGER IF EXISTS trigger_update_project_stats ON steganography_operations;
CREATE TRIGGER trigger_update_project_stats
    AFTER INSERT ON steganography_operations
    FOR EACH ROW
    WHEN (NEW.project_id IS NOT NULL)
    EXECUTE FUNCTION update_project_stats();

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM user_sessions WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;

-- Create RLS (Row Level Security) policies for better security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE steganography_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only see/modify their own data
CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON users FOR UPDATE USING (auth.uid() = id);

-- Projects - users can only access their own projects
CREATE POLICY "Users can view own projects" ON projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create projects" ON projects FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own projects" ON projects FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own projects" ON projects FOR DELETE USING (auth.uid() = user_id);

-- Operations - users can only access their own operations
CREATE POLICY "Users can view own operations" ON steganography_operations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create operations" ON steganography_operations FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Project files - users can only access files from their projects
CREATE POLICY "Users can view own project files" ON project_files FOR SELECT 
USING (project_id IN (SELECT id FROM projects WHERE user_id = auth.uid()));
CREATE POLICY "Users can create project files" ON project_files FOR INSERT 
WITH CHECK (project_id IN (SELECT id FROM projects WHERE user_id = auth.uid()));

-- Feedback - users can view their own feedback
CREATE POLICY "Users can view own feedback" ON user_feedback FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create feedback" ON user_feedback FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL);

-- Sessions - users can only access their own sessions
CREATE POLICY "Users can view own sessions" ON user_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create sessions" ON user_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own sessions" ON user_sessions FOR DELETE USING (auth.uid() = user_id);