"""
Supabase Service Module for Video Steganography Project
Handles all database operations for steganography operations
"""
import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, List, Any

# Handle different import contexts
try:
    from supabase_config import get_supabase_client
except ImportError:
    try:
        from .supabase_config import get_supabase_client
    except ImportError:
        from backend.supabase_config import get_supabase_client

class SteganographyDatabase:
    """
    Database service for steganography operations
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    # User Management
    def create_user(self, email: str, username: str) -> Optional[str]:
        """
        Create a new user and return their ID
        """
        try:
            result = self.supabase.table('users').insert({
                'email': email,
                'username': username
            }).execute()
            
            if result.data:
                return result.data[0]['id']
            return None
            
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Get user by email address
        """
        try:
            result = self.supabase.table('users').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get user by username
        """
        try:
            result = self.supabase.table('users').select('*').eq('username', username).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    # Steganography Operations
    def log_operation_start(self, user_id: str, operation_type: str, media_type: str, 
                           original_filename: str, password: str) -> Optional[str]:
        """
        Log the start of a steganography operation
        Returns operation ID if successful
        """
        try:
            # Hash the password for logging (security)
            password_hash = hashlib.md5(password.encode()).hexdigest()
            
            result = self.supabase.table('steganography_operations').insert({
                'user_id': user_id,
                'operation_type': operation_type,
                'media_type': media_type,
                'original_filename': original_filename,
                'password_hash': password_hash,
                'success': False  # Will be updated when operation completes
            }).execute()
            
            if result.data:
                return result.data[0]['id']
            return None
            
        except Exception as e:
            error_msg = str(e)
            # Check if it's a missing table error (common in development)
            if 'PGRST205' in error_msg or 'table' in error_msg.lower() and 'schema cache' in error_msg.lower():
                # Silently continue without database logging - this is optional functionality
                return None  # Don't log anything, just continue
            elif '23503' in error_msg and 'user_id_fkey' in error_msg:
                # Foreign key constraint violation - user doesn't exist, just continue silently
                print(f"[INFO] User not in database, continuing without logging")
                return None
            else:
                print(f"Error logging operation start: {error_msg}")
                return None
    
    def log_operation_complete(self, operation_id: str, success: bool, 
                             output_filename: Optional[str] = None,
                             file_size: Optional[int] = None,
                             message_preview: Optional[str] = None,
                             error_message: Optional[str] = None,
                             processing_time: Optional[float] = None) -> bool:
        """
        Log the completion of a steganography operation
        """
        try:
            update_data = {
                'success': success,
                'updated_at': datetime.now().isoformat()
            }
            
            if output_filename:
                update_data['output_filename'] = output_filename
            if file_size:
                update_data['file_size'] = file_size
            if message_preview:
                # Store only first 100 characters for preview
                update_data['message_preview'] = message_preview[:100]
            if error_message:
                update_data['error_message'] = error_message
            if processing_time:
                update_data['processing_time'] = processing_time
            
            result = self.supabase.table('steganography_operations').update(
                update_data
            ).eq('id', operation_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            error_msg = str(e)
            # Check if it's a missing table error (common in development)
            if 'PGRST205' in error_msg or 'table' in error_msg.lower() and 'schema cache' in error_msg.lower():
                # Silently continue without database logging - this is optional functionality
                return True  # Don't log anything, just continue
            else:
                print(f"Error logging operation completion: {error_msg}")
                return False
    
    def get_user_operations(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent operations for a user
        """
        try:
            result = self.supabase.table('steganography_operations').select(
                '*'
            ).eq('user_id', user_id).order(
                'created_at', desc=True
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            print(f"Error getting user operations: {str(e)}")
            return []
    
    def get_operation_stats(self, user_id: Optional[str] = None) -> Dict:
        """
        Get operation statistics
        """
        try:
            # Base query
            query = self.supabase.table('steganography_operations').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            
            result = query.execute()
            operations = result.data if result.data else []
            
            # Calculate stats
            total_operations = len(operations)
            successful_operations = len([op for op in operations if op['success']])
            failed_operations = total_operations - successful_operations
            
            # Media type breakdown
            media_stats = {}
            for op in operations:
                media_type = op['media_type']
                if media_type not in media_stats:
                    media_stats[media_type] = {'total': 0, 'successful': 0}
                media_stats[media_type]['total'] += 1
                if op['success']:
                    media_stats[media_type]['successful'] += 1
            
            return {
                'total_operations': total_operations,
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'success_rate': (successful_operations / total_operations * 100) if total_operations > 0 else 0,
                'media_stats': media_stats
            }
            
        except Exception as e:
            print(f"Error getting operation stats: {str(e)}")
            return {}
    
    # File Metadata
    def log_file_metadata(self, operation_id: str, file_type: str, 
                         file_path: Optional[str] = None,
                         mime_type: Optional[str] = None,
                         file_hash: Optional[str] = None,
                         file_size: Optional[int] = None,
                         dimensions: Optional[str] = None,
                         duration: Optional[float] = None) -> bool:
        """
        Log metadata for processed files
        """
        try:
            result = self.supabase.table('file_metadata').insert({
                'operation_id': operation_id,
                'file_type': file_type,
                'file_path': file_path,
                'mime_type': mime_type,
                'file_hash': file_hash,
                'file_size': file_size,
                'dimensions': dimensions,
                'duration': duration
            }).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            print(f"Error logging file metadata: {str(e)}")
            return False
    
    # Database Health
    def health_check(self) -> Dict[str, Any]:
        """
        Check database health and connectivity
        """
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = self.supabase.table('users').select('id').limit(1).execute()
            
            connection_time = time.time() - start_time
            
            # Get table counts
            users_result = self.supabase.table('users').select('id').execute()
            operations_result = self.supabase.table('steganography_operations').select('id').execute()
            metadata_result = self.supabase.table('file_metadata').select('id').execute()
            
            return {
                'status': 'healthy',
                'connection_time_ms': round(connection_time * 1000, 2),
                'table_counts': {
                    'users': len(users_result.data) if users_result.data else 0,
                    'operations': len(operations_result.data) if operations_result.data else 0,
                    'file_metadata': len(metadata_result.data) if metadata_result.data else 0
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Convenience function to get database instance
def get_database() -> SteganographyDatabase:
    """
    Get a database service instance
    """
    return SteganographyDatabase()

if __name__ == "__main__":
    # Test the database service
    print("Testing Supabase Database Service")
    print("=================================")
    
    db = get_database()
    
    # Health check
    health = db.health_check()
    print(f"Database Health: {health['status']}")
    
    if health['status'] == 'healthy':
        print(f"Connection Time: {health['connection_time_ms']}ms")
        print(f"Table Counts: {health['table_counts']}")
    else:
        print(f"Error: {health.get('error', 'Unknown error')}")