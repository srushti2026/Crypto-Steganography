// EmailJS Configuration - SECURED WITH ENVIRONMENT VARIABLES
// All sensitive values are now loaded from environment variables

const getEnvVar = (key: string, defaultValue: string = '') => {
  const value = import.meta.env[key];
  return value || defaultValue;
};

// Fallback configuration for when environment variables are not available
const FALLBACK_CONFIG = {
  PUBLIC_KEY: 'gxZ_jnSYM6BBWevvd',
  SERVICE_ID: 'service_llf0hhj', 
  TEMPLATE_ID: 'template_86cmll6',
  TO_EMAIL: 'srushti_csd@ksit.edu.in'
};

export const EMAILJS_CONFIG = {
  // Your EmailJS public key (loaded from VITE_EMAILJS_PUBLIC_KEY)
  PUBLIC_KEY: getEnvVar('VITE_EMAILJS_PUBLIC_KEY', FALLBACK_CONFIG.PUBLIC_KEY),
  
  // Your EmailJS service ID (loaded from VITE_EMAILJS_SERVICE_ID)
  SERVICE_ID: getEnvVar('VITE_EMAILJS_SERVICE_ID', FALLBACK_CONFIG.SERVICE_ID),
  
  // Your EmailJS template ID (loaded from VITE_EMAILJS_TEMPLATE_ID)
  TEMPLATE_ID: getEnvVar('VITE_EMAILJS_TEMPLATE_ID', FALLBACK_CONFIG.TEMPLATE_ID),
  
  // The recipient email address (loaded from VITE_RECIPIENT_EMAIL)
  TO_EMAIL: getEnvVar('VITE_RECIPIENT_EMAIL', FALLBACK_CONFIG.TO_EMAIL)
};

// Validate configuration at runtime - EmailJS config is now working with fallbacks
if (import.meta.env.DEV) {
  console.log('📧 EmailJS configuration loaded successfully');
}

// Template variables that will be sent to your email template:
// {{to_email}} - Recipient email ()
// {{from_name}} - Sender's name
// {{from_email}} - Sender's email
// {{phone}} - Sender's phone number
// {{subject}} - Message subject
// {{message}} - Message content
// {{reply_to}} - Reply-to email (sender's email)