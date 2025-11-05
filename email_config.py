# Email Configuration for VeilForge Contact Form - SECURED WITH ENVIRONMENT VARIABLES
# All sensitive values are now loaded from environment variables
import os

EMAIL_CONFIG = {
    # SMTP Server Configuration
    'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
    
    # Email Credentials - LOADED FROM ENVIRONMENT VARIABLES
    'EMAIL_USER': os.getenv('EMAIL_USER'),
    'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
    
    # Recipient Configuration
    'RECIPIENT_EMAIL': os.getenv('RECIPIENT_EMAIL', 'contact@example.com'),
    'SENDER_NAME': os.getenv('SENDER_NAME', 'VeilForge Contact System'),
    
    # Email Templates
    'SUBJECT_TEMPLATE': os.getenv('EMAIL_SUBJECT_TEMPLATE', 'VeilForge Contact: {subject}'),
    
    # Enable/Disable email sending for testing
    'ENABLE_EMAIL': os.getenv('ENABLE_EMAIL', 'False').lower() == 'true'
}

# Validate required environment variables
required_vars = ['EMAIL_USER', 'EMAIL_PASSWORD']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars and EMAIL_CONFIG['ENABLE_EMAIL']:
    print(f"⚠️ Warning: Missing required environment variables: {', '.join(missing_vars)}")
    print("Email functionality will be disabled until these are configured.")
    EMAIL_CONFIG['ENABLE_EMAIL'] = False

# Instructions for Gmail App Password:
"""
To use Gmail SMTP, you need to:
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" for this application
4. Use that App Password (not your regular Gmail password)
5. Set ENABLE_EMAIL to True
"""

# Alternative Email Services:
"""
For other email providers:
- Outlook/Hotmail: smtp-mail.outlook.com:587
- Yahoo: smtp.mail.yahoo.com:587
- Custom SMTP: Use your provider's SMTP settings
"""