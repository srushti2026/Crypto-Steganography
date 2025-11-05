-- ============================================================================
-- SUPABASE DATABASE SETUP FOR STEGANOGRAPHY APPLICATION
-- ============================================================================
-- 
-- INSTRUCTIONS:
-- 1. Go to your Supabase project dashboard: https://app.supabase.com
-- 2. Navigate to SQL Editor
-- 3. Click "New Query"
-- 4. Copy and paste this entire file
-- 5. Click "RUN" to execute
-- 
-- This will create all required tables for the steganography application
-- ============================================================================

-- Enable UUID extension (required for ID generation)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: users
-- Stores user accounts for the steganography application
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text UNIQUE NOT NULL,
    username text UNIQUE NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- ============================================================================
-- TABLE: steganography_operations 
-- Tracks all embedding and extraction operations
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.steganography_operations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES public.users(id) ON DELETE CASCADE,
    operation_type text NOT NULL CHECK (operation_type IN ('hide', 'extract')),
    media_type text NOT NULL CHECK (media_type IN ('video', 'audio', 'image', 'document')),
    original_filename text NOT NULL,
    output_filename text,
    file_size bigint,
    message_preview text,
    password_hash text NOT NULL,
    encryption_method text DEFAULT 'aes-256-gcm',
    success boolean DEFAULT false,
    error_message text,
    processing_time real,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);

-- ============================================================================
-- TABLE: file_metadata
-- Stores detailed metadata about processed files
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.file_metadata (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id uuid REFERENCES public.steganography_operations(id) ON DELETE CASCADE,
    file_type text NOT NULL,
    mime_type text,
    file_path text,
    file_hash text,
    file_size bigint,
    dimensions text,
    duration real,
    created_at timestamp with time zone DEFAULT now()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_operations_user_id ON public.steganography_operations(user_id);
CREATE INDEX IF NOT EXISTS idx_operations_created_at ON public.steganography_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_operations_media_type ON public.steganography_operations(media_type);
CREATE INDEX IF NOT EXISTS idx_operations_type ON public.steganography_operations(operation_type);
CREATE INDEX IF NOT EXISTS idx_metadata_operation_id ON public.file_metadata(operation_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Enable security policies for multi-user access
-- ============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.steganography_operations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_metadata ENABLE ROW LEVEL SECURITY;

-- Allow users to read their own records
CREATE POLICY "Users can view own data" ON public.users
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can view own operations" ON public.steganography_operations
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own file metadata" ON public.file_metadata
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.steganography_operations so 
            WHERE so.id = operation_id AND so.user_id = auth.uid()
        )
    );

-- ============================================================================
-- VERIFICATION QUERIES
-- Run these to verify the setup worked correctly
-- ============================================================================

-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'steganography_operations', 'file_metadata')
ORDER BY table_name;

-- Check table structures
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'steganography_operations', 'file_metadata')
ORDER BY table_name, ordinal_position;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================
SELECT 
    '🎉 Database setup completed successfully!' as message,
    'Tables created: users, steganography_operations, file_metadata' as details,
    'Your steganography application is now ready to use database logging!' as status;