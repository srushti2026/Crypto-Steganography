// EmailJS Configuration - SECURED WITH ENVIRONMENT VARIABLES
// All sensitive values are now loaded from environment variables

const getEnvVar = (key: string, defaultValue: string = '') => {
  try {
    return import.meta?.env?.[key] || defaultValue;
  } catch {
    return defaultValue;
  }
};

export const EMAILJS_CONFIG = {
  // Your EmailJS public key (loaded from VITE_EMAILJS_PUBLIC_KEY)
  PUBLIC_KEY: getEnvVar('VITE_EMAILJS_PUBLIC_KEY', ''),
  
  // Your EmailJS service ID (loaded from VITE_EMAILJS_SERVICE_ID)
  SERVICE_ID: getEnvVar('VITE_EMAILJS_SERVICE_ID', ''),
  
  // Your EmailJS template ID (loaded from VITE_EMAILJS_TEMPLATE_ID)
  TEMPLATE_ID: getEnvVar('VITE_EMAILJS_TEMPLATE_ID', ''),
  
  // The recipient email address (loaded from VITE_RECIPIENT_EMAIL)
  TO_EMAIL: getEnvVar('VITE_RECIPIENT_EMAIL', 'contact@example.com')
};

// Validate configuration at runtime
if (!EMAILJS_CONFIG.PUBLIC_KEY) {
  console.error('❌ VITE_EMAILJS_PUBLIC_KEY environment variable is required');
}
if (!EMAILJS_CONFIG.SERVICE_ID) {
  console.error('❌ VITE_EMAILJS_SERVICE_ID environment variable is required');
}
if (!EMAILJS_CONFIG.TEMPLATE_ID) {
  console.error('❌ VITE_EMAILJS_TEMPLATE_ID environment variable is required');
}

// Template variables that will be sent to your email template:
// {{to_email}} - Recipient email ()
// {{from_name}} - Sender's name
// {{from_email}} - Sender's email
// {{phone}} - Sender's phone number
// {{subject}} - Message subject
// {{message}} - Message content
// {{reply_to}} - Reply-to email (sender's email)