-- Migration to update activities table structure
-- This adds the missing columns that the frontend expects

-- Add the missing columns to the activities table
ALTER TABLE activities ADD COLUMN IF NOT EXISTS carrier_file_id uuid;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS processed_file_id uuid;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS payload_type text;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS encryption_enabled boolean DEFAULT false;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS success boolean DEFAULT true;
ALTER TABLE activities ADD COLUMN IF NOT EXISTS error_message text;

-- Add foreign key constraints for the file references
ALTER TABLE activities ADD CONSTRAINT IF NOT EXISTS activities_carrier_file_id_fkey 
    FOREIGN KEY (carrier_file_id) REFERENCES files(id) ON DELETE SET NULL;
    
ALTER TABLE activities ADD CONSTRAINT IF NOT EXISTS activities_processed_file_id_fkey 
    FOREIGN KEY (processed_file_id) REFERENCES files(id) ON DELETE SET NULL;

-- Make description optional since the TypeScript types don't require it
ALTER TABLE activities ALTER COLUMN description DROP NOT NULL;

-- Verify the update
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'activities' 
ORDER BY ordinal_position;