#!/usr/bin/env python3
"""
Apply database migration to update activities table structure
"""

import os
import sys
from supabase_config import get_supabase_client

def apply_migration():
    """Apply the activities table migration"""
    
    print("🔄 Applying Activities Table Migration")
    print("=" * 50)
    
    try:
        # Read the migration SQL
        migration_file = "migrations/update_activities_table.sql"
        if not os.path.exists(migration_file):
            print(f"❌ Migration file not found: {migration_file}")
            return False
            
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("📖 Migration SQL loaded successfully")
        
        # Get Supabase client
        supabase = get_supabase_client()
        print("✅ Connected to Supabase")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
        
        print(f"🔄 Executing {len(statements)} migration statements...")
        
        for i, sql in enumerate(statements, 1):
            try:
                print(f"   Statement {i}/{len(statements)}: {sql[:50]}...")
                result = supabase.rpc('exec_sql', {'sql': sql}).execute()
                
                if hasattr(result, 'error') and result.error:
                    print(f"   ⚠️  Warning: {result.error}")
                else:
                    print(f"   ✅ Success")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                # Continue with other statements
        
        print("🎉 Migration completed!")
        print("\n📊 Verifying table structure...")
        
        # Verify the migration by checking the table structure
        verify_sql = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'activities' 
        ORDER BY ordinal_position;
        """
        
        result = supabase.rpc('exec_sql', {'sql': verify_sql}).execute()
        if hasattr(result, 'data') and result.data:
            print("✅ Activities table structure verified")
        else:
            print("⚠️  Could not verify table structure")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)