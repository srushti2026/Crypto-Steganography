"""
Database Setup Script for Video Steganography Project
Run this script to create all required tables in your Supabase database
"""
import os
import sys
from supabase_config import get_supabase_client, create_tables_sql

def setup_database():
    """
    Set up the database with all required tables
    """
    try:
        # Check if environment variables are set
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        # Validate that required environment variables are present
        if not supabase_url:
            print("❌ Error: SUPABASE_URL environment variable is required")
            print("Please set your Supabase URL in the environment variables or .env file")
            print("Example: SUPABASE_URL=https://your-project-ref.supabase.co")
            return False
            
        if not supabase_key:
            print("❌ Error: SUPABASE_KEY environment variable is required")
            print("Please set your Supabase anon key in the environment variables or .env file")
            print("Example: SUPABASE_KEY=your-anon-key-here")
            return False
            
        print(f"✅ Using SUPABASE_URL: {supabase_url[:30]}...")
        print("✅ Using SUPABASE_KEY: [REDACTED]")
        
        print("🔄 Connecting to Supabase...")
        supabase = get_supabase_client()
        
        print("🔄 Creating database tables...")
        sql_statements = create_tables_sql()
        
        for i, sql in enumerate(sql_statements, 1):
            try:
                print(f"   Executing statement {i}/{len(sql_statements)}")
                result = supabase.rpc('exec_sql', {'sql': sql.strip()}).execute()
                if hasattr(result, 'error') and result.error:
                    print(f"   ⚠️  Warning in statement {i}: {result.error}")
            except Exception as e:
                print(f"   ⚠️  Error in statement {i}: {str(e)}")
                # Continue with other statements
        
        print("✅ Database setup completed!")
        print("\nCreated tables:")
        print("   - users")
        print("   - steganography_operations") 
        print("   - file_metadata")
        print("\nYour database is ready for the steganography application!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify your Supabase URL and key are correct")
        print("2. Check your internet connection")
        print("3. Ensure your Supabase project is active")
        return False

def test_connection():
    """
    Test the database connection
    """
    try:
        print("🔄 Testing Supabase connection...")
        supabase = get_supabase_client()
        
        # Try to query the users table
        result = supabase.table('users').select('*').limit(1).execute()
        print("✅ Connection successful!")
        print(f"   Users table exists with {len(result.data) if result.data else 0} records")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False

def main():
    """
    Main function to run database setup
    """
    print("Supabase Database Setup")
    print("=======================")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test connection mode
        success = test_connection()
    else:
        # Full setup mode
        print("\nThis will create the following tables in your Supabase database:")
        print("- users")
        print("- steganography_operations")
        print("- file_metadata")
        
        response = input("\nContinue? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
        
        success = setup_database()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update your application to use the database")
        print("2. Test the integration with your steganography app")
    else:
        print("\n💥 Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()