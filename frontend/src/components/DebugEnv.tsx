// Debug component to check environment variables in production
export const DebugEnv = () => {
  const envVars = {
    NODE_ENV: process.env.NODE_ENV,
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'unknown',
    href: typeof window !== 'undefined' ? window.location.href : 'unknown'
  };

  let apiUrl = 'unknown';
  try {
    apiUrl = import.meta?.env?.VITE_API_URL || 'not-found';
  } catch (error) {
    apiUrl = 'error-accessing-import-meta';
  }

  return (
    <div style={{ 
      position: 'fixed', 
      bottom: '10px', 
      right: '10px', 
      background: 'rgba(0,0,0,0.8)', 
      color: 'white', 
      padding: '10px', 
      fontSize: '12px',
      borderRadius: '5px',
      zIndex: 9999
    }}>
      <div>🔧 Debug Info:</div>
      <div>API URL: {apiUrl}</div>
      <div>Hostname: {envVars.hostname}</div>
      <div>ENV: {envVars.NODE_ENV}</div>
    </div>
  );
};