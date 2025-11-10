-- Fix PixelVault project type constraint
-- Run this SQL in your Supabase SQL Editor

-- Drop the existing constraint if it exists
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;

-- Add the updated constraint with 'pixelvault' included
ALTER TABLE projects ADD CONSTRAINT projects_project_type_check 
CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));

-- Verify the constraint was added successfully
SELECT conname, consrc 
FROM pg_constraint 
WHERE conname = 'projects_project_type_check';