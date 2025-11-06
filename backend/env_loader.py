"""
Environment Variable Loader for VeilForge
Safely loads environment variables from .env file for local development
and validates that required variables are present.
"""

import os
from pathlib import Path

def load_env_file():
    """
    Load environment variables from .env file if it exists
    This is only used for local development - production uses Vercel environment variables
    """
    env_path = Path(__file__).parent / '.env'
    
    if env_path.exists():
        print(f"📁 Loading environment variables from {env_path}")
        
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        loaded_vars = []
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Parse KEY=VALUE format
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Only set if not already in environment
                if key and not os.getenv(key):
                    os.environ[key] = value
                    loaded_vars.append(key)
        
        print(f"✅ Loaded {len(loaded_vars)} environment variables")
        return True
    else:
        print("ℹ️ No .env file found - using system environment variables")
        return False

def validate_required_env_vars():
    """
    Validate that all required environment variables are present
    """
    required_vars = {
        'SUPABASE_URL': 'Your Supabase project URL',
        'SUPABASE_KEY': 'Your Supabase anon key',
    }
    
    optional_vars = {
        'VITE_EMAILJS_PUBLIC_KEY': 'EmailJS public key (for frontend)',
        'VITE_EMAILJS_SERVICE_ID': 'EmailJS service ID (for frontend)',
        'VITE_EMAILJS_TEMPLATE_ID': 'EmailJS template ID (for frontend)',
        'EMAIL_USER': 'SMTP email user (for backend email)',
        'EMAIL_PASSWORD': 'SMTP email password (for backend email)',
        'RECIPIENT_EMAIL': 'Default recipient email address',
    }
    
    missing_required = []
    missing_optional = []
    
    # Check required variables
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"  {var} - {description}")
    
    # Check optional variables  
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"  {var} - {description}")
    
    if missing_required:
        print("\n❌ CRITICAL: Missing required environment variables:")
        for var in missing_required:
            print(var)
        print("\n💡 Please add these to your .env file or Vercel environment variables")
        return False
    
    if missing_optional:
        print("\n⚠️  Optional environment variables not set:")
        for var in missing_optional:
            print(var)
        print("\n💡 Some features may not work without these variables")
    
    print("\n✅ All required environment variables are configured")
    return True

def get_env_status():
    """
    Get a summary of environment variable status for debugging
    """
    status = {
        'supabase': {
            'url': bool(os.getenv('SUPABASE_URL')),
            'key': bool(os.getenv('SUPABASE_KEY'))
        },
        'emailjs': {
            'public_key': bool(os.getenv('VITE_EMAILJS_PUBLIC_KEY')),
            'service_id': bool(os.getenv('VITE_EMAILJS_SERVICE_ID')),
            'template_id': bool(os.getenv('VITE_EMAILJS_TEMPLATE_ID'))
        },
        'email': {
            'user': bool(os.getenv('EMAIL_USER')),
            'password': bool(os.getenv('EMAIL_PASSWORD')),
            'recipient': bool(os.getenv('RECIPIENT_EMAIL'))
        }
    }
    
    return status

# Auto-load when imported (for convenience)
if __name__ == "__main__":
    load_env_file()
    validate_required_env_vars()
    
    print("\n📊 Environment Status:")
    status = get_env_status()
    for category, vars in status.items():
        print(f"\n{category.upper()}:")
        for var, is_set in vars.items():
            icon = "✅" if is_set else "❌"
            print(f"  {icon} {var}")
else:
    # Auto-load for imports
    load_env_file()