-- Simple PixelVault Migration - Run in Supabase SQL Editor
-- This is the minimal version - just run these 3 commands:

-- 1. Drop existing constraint
ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;

-- 2. Add new constraint with pixelvault
ALTER TABLE projects ADD CONSTRAINT projects_project_type_check 
CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));

-- 3. Test it works (this should succeed)
SELECT 'Migration completed successfully!' AS status;