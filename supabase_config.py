"""
Supabase Configuration for Video Steganography Project
"""
import os
from supabase import create_client, Client

# Supabase configuration - SECURED WITH ENVIRONMENT VARIABLES
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Validate that required environment variables are set
if not SUPABASE_URL:
    print("❌ CRITICAL: SUPABASE_URL environment variable is required")
    print("💡 Please check your .env file or environment configuration")
    print("   Expected format: SUPABASE_URL=https://your-project-ref.supabase.co")
    raise ValueError("SUPABASE_URL environment variable is required")

if not SUPABASE_KEY:
    print("❌ CRITICAL: SUPABASE_KEY environment variable is required") 
    print("💡 Please check your .env file or environment configuration")
    print("   Expected format: SUPABASE_KEY=your-supabase-anon-key")
    raise ValueError("SUPABASE_KEY environment variable is required")

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Database tables schema (for reference)
TABLES_SCHEMA = {
    "users": {
        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
        "email": "text UNIQUE NOT NULL",
        "username": "text UNIQUE NOT NULL",
        "created_at": "timestamp with time zone DEFAULT now()",
        "updated_at": "timestamp with time zone DEFAULT now()"
    },
    "steganography_operations": {
        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
        "user_id": "uuid REFERENCES users(id) ON DELETE CASCADE",
        "operation_type": "text NOT NULL", # 'hide' or 'extract'
        "media_type": "text NOT NULL", # 'video', 'audio', 'image', 'document'
        "original_filename": "text NOT NULL",
        "output_filename": "text",
        "file_size": "bigint",
        "message_preview": "text", # First 100 chars of hidden message
        "password_hash": "text NOT NULL",
        "encryption_method": "text DEFAULT 'xor_md5'",
        "success": "boolean DEFAULT false",
        "error_message": "text",
        "processing_time": "real",
        "created_at": "timestamp with time zone DEFAULT now()"
    },
    "file_metadata": {
        "id": "uuid PRIMARY KEY DEFAULT gen_random_uuid()",
        "operation_id": "uuid REFERENCES steganography_operations(id) ON DELETE CASCADE",
        "file_type": "text NOT NULL",
        "mime_type": "text",
        "file_path": "text",
        "file_hash": "text",
        "file_size": "bigint",
        "dimensions": "text", # For images/videos: "width,height"
        "duration": "real", # For audio/video files
        "created_at": "timestamp with time zone DEFAULT now()"
    }
}

def create_tables_sql():
    """
    Generate SQL statements to create all required tables
    """
    sql_statements = []
    
    # Enable UUID extension
    sql_statements.append("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
    
    # Users table
    sql_statements.append("""
        CREATE TABLE IF NOT EXISTS users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text UNIQUE NOT NULL,
            username text UNIQUE NOT NULL,
            created_at timestamp with time zone DEFAULT now(),
            updated_at timestamp with time zone DEFAULT now()
        );
    """)
    
    # Steganography operations table
    sql_statements.append("""
        CREATE TABLE IF NOT EXISTS steganography_operations (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES users(id) ON DELETE CASCADE,
            operation_type text NOT NULL CHECK (operation_type IN ('hide', 'extract')),
            media_type text NOT NULL CHECK (media_type IN ('video', 'audio', 'image', 'document')),
            original_filename text NOT NULL,
            output_filename text,
            file_size bigint,
            message_preview text,
            password_hash text NOT NULL,
            encryption_method text DEFAULT 'xor_md5',
            success boolean DEFAULT false,
            error_message text,
            processing_time real,
            created_at timestamp with time zone DEFAULT now()
        );
    """)
    
    # File metadata table
    sql_statements.append("""
        CREATE TABLE IF NOT EXISTS file_metadata (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            operation_id uuid REFERENCES steganography_operations(id) ON DELETE CASCADE,
            file_type text NOT NULL,
            mime_type text,
            file_path text,
            file_hash text,
            file_size bigint,
            dimensions text,
            duration real,
            created_at timestamp with time zone DEFAULT now()
        );
    """)
    
    # Indexes for better performance
    sql_statements.append("CREATE INDEX IF NOT EXISTS idx_operations_user_id ON steganography_operations(user_id);")
    sql_statements.append("CREATE INDEX IF NOT EXISTS idx_operations_created_at ON steganography_operations(created_at);")
    sql_statements.append("CREATE INDEX IF NOT EXISTS idx_operations_media_type ON steganography_operations(media_type);")
    sql_statements.append("CREATE INDEX IF NOT EXISTS idx_metadata_operation_id ON file_metadata(operation_id);")
    
    return sql_statements

if __name__ == "__main__":
    print("Supabase Configuration")
    print("======================")
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}..." if SUPABASE_KEY != "your-anon-key" else "Key: Not configured")
    print("\nTo use this configuration:")
    print("1. Create a new project at https://supabase.com/dashboard")
    print("2. Get your project URL and anon key")
    print("3. Set environment variables:")
    print("   set SUPABASE_URL=https://your-project-ref.supabase.co")
    print("   set SUPABASE_KEY=your-anon-key")
    print("4. Run the database setup script")