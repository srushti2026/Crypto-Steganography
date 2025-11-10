-- PixelVault Database Migration
-- Run this in your Supabase SQL Editor

-- Step 1: Check current constraint (using modern PostgreSQL syntax)
SELECT 
    c.conname AS constraint_name,
    pg_get_constraintdef(c.oid) AS constraint_definition
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'projects' 
AND c.conname LIKE '%project_type%';

-- Step 2: Drop existing constraint (if it exists)
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;

-- Step 3: Add new constraint with pixelvault support  
ALTER TABLE projects ADD CONSTRAINT projects_project_type_check 
CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));

-- Step 4: Verify the new constraint was added (using modern PostgreSQL syntax)
SELECT 
    c.conname AS constraint_name,
    pg_get_constraintdef(c.oid) AS constraint_definition
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname = 'projects' 
AND c.conname = 'projects_project_type_check';

-- Step 5: Test creating a pixelvault project (optional)
-- This will fail if the constraint is not working properly
INSERT INTO projects (name, description, project_type) 
VALUES ('Test PixelVault', 'Test project', 'pixelvault') 
RETURNING id;

-- Step 6: Clean up test project (run after confirming the above works)
-- DELETE FROM projects WHERE name = 'Test PixelVault';