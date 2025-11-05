import { supabase } from "@/integrations/supabase/client";

/**
 * Session management utility for proper authentication handling
 */
export class SessionManager {
  private static readonly REMEMBER_ME_KEY = 'rememberMe';
  private static readonly SESSION_CHECK_KEY = 'sessionActive';

  /**
   * Initialize session management
   */
  static initialize() {
    // Set session active flag when page loads
    sessionStorage.setItem(this.SESSION_CHECK_KEY, 'true');
    
    // Listen for page unload to detect browser close
    window.addEventListener('beforeunload', this.handlePageUnload.bind(this));
    
    // Listen for storage changes to sync across tabs
    window.addEventListener('storage', this.handleStorageChange.bind(this));
  }

  /**
   * Handle page unload (browser close or refresh)
   */
  private static handlePageUnload() {
    const rememberMe = localStorage.getItem(this.REMEMBER_ME_KEY);
    
    if (rememberMe !== 'true') {
      // If remember me is not enabled, clear session on browser close
      // We use a timeout to distinguish between refresh and close
      setTimeout(() => {
        const sessionStillActive = sessionStorage.getItem(this.SESSION_CHECK_KEY);
        if (!sessionStillActive) {
          // Browser was actually closed, not just refreshed
          this.clearSession();
        }
      }, 1000);
    }
  }

  /**
   * Handle storage changes across tabs
   */
  private static handleStorageChange(event: StorageEvent) {
    if (event.key === this.REMEMBER_ME_KEY && event.newValue === 'false') {
      // Remember me was disabled, check if we should sign out
      this.checkSessionValidity();
    }
  }

  /**
   * Check if current session should remain valid
   */
  static async checkSessionValidity() {
    const rememberMe = localStorage.getItem(this.REMEMBER_ME_KEY);
    const { data: { session } } = await supabase.auth.getSession();
    
    if (session && rememberMe === 'false') {
      // Session exists but remember me is disabled
      // Only keep session if it's a fresh login (within last hour)
      const loginTime = session.user?.last_sign_in_at;
      if (loginTime) {
        const timeDiff = Date.now() - new Date(loginTime).getTime();
        const oneHour = 60 * 60 * 1000;
        
        if (timeDiff > oneHour) {
          await this.clearSession();
          return false;
        }
      }
    }
    
    return !!session;
  }

  /**
   * Clear user session
   */
  static async clearSession() {
    await supabase.auth.signOut();
    localStorage.removeItem(this.REMEMBER_ME_KEY);
    sessionStorage.removeItem(this.SESSION_CHECK_KEY);
  }

  /**
   * Set remember me preference
   */
  static setRememberMe(remember: boolean) {
    localStorage.setItem(this.REMEMBER_ME_KEY, remember.toString());
  }

  /**
   * Get remember me preference
   */
  static getRememberMe(): boolean {
    return localStorage.getItem(this.REMEMBER_ME_KEY) === 'true';
  }

  /**
   * Handle successful login
   */
  static async handleLogin(rememberMe: boolean) {
    this.setRememberMe(rememberMe);
    sessionStorage.setItem(this.SESSION_CHECK_KEY, 'true');
  }

  /**
   * Handle logout
   */
  static async handleLogout() {
    await this.clearSession();
    window.location.href = '/auth';
  }
}

// Initialize session management when module loads
if (typeof window !== 'undefined') {
  SessionManager.initialize();
}