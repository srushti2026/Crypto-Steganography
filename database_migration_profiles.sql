-- Database Migration: Add Profile Fields to Supabase
-- This script adds all the missing columns that the Profile page expects

-- Add the missing columns to the profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS username VARCHAR(255),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(255), 
ADD COLUMN IF NOT EXISTS nickname VARCHAR(255),
ADD COLUMN IF NOT EXISTS phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS website TEXT,
ADD COLUMN IF NOT EXISTS telegram VARCHAR(255),
ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(255),
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'subscriber',
ADD COLUMN IF NOT EXISTS display_name_publicly VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_sign_in_at TIMESTAMPTZ;

-- Add indexes for commonly queried fields
CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);

-- Add constraints
ALTER TABLE profiles 
ADD CONSTRAINT IF NOT EXISTS check_role CHECK (role IN ('subscriber', 'premium', 'admin'));

-- Update existing records to have default role if null
UPDATE profiles SET role = 'subscriber' WHERE role IS NULL;

-- Create or update Row Level Security policies
-- Allow users to read their own profile
CREATE POLICY IF NOT EXISTS "Users can view their own profile" ON profiles
FOR SELECT USING (auth.uid() = user_id);

-- Allow users to update their own profile  
CREATE POLICY IF NOT EXISTS "Users can update their own profile" ON profiles
FOR UPDATE USING (auth.uid() = user_id);

-- Allow users to insert their own profile
CREATE POLICY IF NOT EXISTS "Users can insert their own profile" ON profiles
FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Enable RLS on the profiles table
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;