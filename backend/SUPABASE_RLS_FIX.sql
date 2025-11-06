-- ============================================================================
-- SUPABASE RLS POLICY FIX FOR STEGANOGRAPHY APPLICATION
-- ============================================================================
-- 
-- INSTRUCTIONS:
-- 1. Go to your Supabase project dashboard: https://app.supabase.com
-- 2. Navigate to SQL Editor
-- 3. Click "New Query"
-- 4. Copy and paste this file
-- 5. Click "RUN" to execute
-- 
-- This will fix the RLS policies to allow anonymous access
-- ============================================================================

-- Drop existing restrictive policies
DROP POLICY IF EXISTS "Users can view own data" ON public.users;
DROP POLICY IF EXISTS "Users can view own operations" ON public.steganography_operations;
DROP POLICY IF EXISTS "Users can view own file metadata" ON public.file_metadata;

-- Create permissive policies for anonymous access
-- Since this is a demo application, we allow anonymous access to all records

-- Users table: Allow all operations for anonymous users
CREATE POLICY "Allow anonymous access to users" ON public.users
    FOR ALL USING (true);

-- Operations table: Allow all operations for anonymous users  
CREATE POLICY "Allow anonymous access to operations" ON public.steganography_operations
    FOR ALL USING (true);

-- File metadata table: Allow all operations for anonymous users
CREATE POLICY "Allow anonymous access to file metadata" ON public.file_metadata
    FOR ALL USING (true);

-- ============================================================================
-- VERIFICATION
-- ============================================================================
SELECT 
    '✅ RLS policies updated for anonymous access!' as message,
    'Database logging should now work properly' as status;

-- Test query to verify access works
SELECT COUNT(*) as user_count FROM public.users;