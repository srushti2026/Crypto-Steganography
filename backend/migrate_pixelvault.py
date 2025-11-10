"""
Migration script to add 'pixelvault' project type to the database
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def test_pixelvault_creation():
    """Test if we can create a pixelvault project"""
    try:
        print("🧪 Testing pixelvault project creation...")
        
        # Try to create a test pixelvault project
        test_project = {
            "name": "Test PixelVault Project",
            "description": "Test project to verify pixelvault type works",
            "project_type": "pixelvault",
            "settings": {}
        }
        
        result = supabase.table("projects").insert(test_project).execute()
        
        if result.data:
            print("✅ PixelVault project creation test PASSED!")
            print(f"   Created test project with ID: {result.data[0]['id']}")
            
            # Clean up test project
            supabase.table("projects").delete().eq("id", result.data[0]['id']).execute()
            print("   Test project cleaned up.")
            return True
        else:
            print("❌ PixelVault project creation test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ PixelVault project creation test FAILED: {e}")
        return False

def run_migration():
    """Run the pixelvault project type migration"""
    try:
        print("🔄 Checking current database constraint...")
        
        # First, test if pixelvault type already works
        if test_pixelvault_creation():
            print("✅ PixelVault project type is already supported!")
            return
        
        print("❌ PixelVault project type not supported. Manual SQL execution required.")
        print("\n" + "="*70)
        print("📋 MANUAL STEPS REQUIRED:")
        print("="*70)
        print("1. Open your Supabase Dashboard")
        print("2. Go to SQL Editor")
        print("3. Run the following SQL commands:")
        print("\n-- Step 1: Drop existing constraint")
        print("ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;")
        print("\n-- Step 2: Add new constraint with pixelvault")
        print("ALTER TABLE projects ADD CONSTRAINT projects_project_type_check")
        print("CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));")
        print("\n-- Step 3: Verify constraint was added")
        print("SELECT conname, consrc FROM pg_constraint WHERE conname = 'projects_project_type_check';")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        print("\n" + "="*70)
        print("📋 MANUAL SQL EXECUTION REQUIRED:")
        print("="*70)
        print("Please run these commands in your Supabase SQL Editor:")
        print("1. ALTER TABLE projects DROP CONSTRAINT IF EXISTS projects_project_type_check;")
        print("2. ALTER TABLE projects ADD CONSTRAINT projects_project_type_check CHECK (project_type IN ('general', 'copyright', 'forensic', 'pixelvault'));")
        print("="*70)

if __name__ == "__main__":
    run_migration()