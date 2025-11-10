-- Migration to add 'pixelvault' project type
-- This script updates the existing check constraint to include the new project type

-- Drop the existing check constraint
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;

-- Add the new constraint with pixelvault included
ALTER TABLE projects ADD CONSTRAINT projects_project_type_check 
    CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));

-- Verify the update
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'projects' AND column_name = 'project_type';