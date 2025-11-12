import React from 'react';

export const EnvDebug: React.FC = () => {
  const envVars = {
    VITE_EMAILJS_PUBLIC_KEY: import.meta.env.VITE_EMAILJS_PUBLIC_KEY,
    VITE_EMAILJS_SERVICE_ID: import.meta.env.VITE_EMAILJS_SERVICE_ID,
    VITE_EMAILJS_TEMPLATE_ID: import.meta.env.VITE_EMAILJS_TEMPLATE_ID,
    VITE_RECIPIENT_EMAIL: import.meta.env.VITE_RECIPIENT_EMAIL,
    VITE_API_URL: import.meta.env.VITE_API_URL,
    NODE_ENV: import.meta.env.NODE_ENV,
    MODE: import.meta.env.MODE,
    DEV: import.meta.env.DEV,
    PROD: import.meta.env.PROD,
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 10, 
      left: 10, 
      background: 'black', 
      color: 'white', 
      padding: 10, 
      fontSize: '12px',
      zIndex: 9999,
      maxWidth: '300px',
      overflow: 'auto',
      border: '1px solid white'
    }}>
      <h3>Environment Variables Debug</h3>
      {Object.entries(envVars).map(([key, value]) => (
        <div key={key}>
          <strong>{key}:</strong> {value ? '✅ SET' : '❌ MISSING'}
          {value && <span> ({String(value).substring(0, 10)}...)</span>}
        </div>
      ))}
    </div>
  );
};