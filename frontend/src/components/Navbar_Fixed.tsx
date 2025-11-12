import { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Menu, X, LogOut, Mail, Code, UserCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import ThemeToggle from "./ThemeToggle";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { supabase } from "@/integrations/supabase/client";
import { SessionManager } from "@/utils/sessionManager";
import logo from "@/assets/logo.png";

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [logoutConfirmOpen, setLogoutConfirmOpen] = useState(false);

  useEffect(() => {
    // Check current auth state
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);
  
  const leftLinks = user ? [
    { name: "Home", path: "/home" },
    { name: "Dashboard", path: "/dashboard" },
    { name: "General", path: "/general" },
    { name: "PixelVault", path: "/pixelvault" },
    { name: "Copyright", path: "/copyright" },
    { name: "Forensic", path: "/forensic" },
  ] : [];

  const rightLinks = [
    { name: "Contact", path: "/contact", icon: <Mail className="h-4 w-4" /> },
    { name: "Developers", path: "/developers", icon: <Code className="h-4 w-4" /> },
  ];

  const userLinks = user ? [
    { name: "Profile", path: "/profile", icon: <UserCircle className="h-4 w-4" /> },
  ] : [];

  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 20;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [scrolled]);
  
  const handleLogoutClick = () => {
    setLogoutConfirmOpen(true);
  };

  const confirmLogout = async () => {
    setLogoutConfirmOpen(false);
    await SessionManager.handleLogout();
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header className={cn("fixed top-0 left-0 right-0 z-50 transition-all duration-300", scrolled ? "bg-background/95 dark:bg-card/95 backdrop-blur-lg py-2 shadow-lg shadow-primary/10 border-b border-border/20" : "bg-background/80 dark:bg-card/80 backdrop-blur-md py-3 shadow-sm")}>
      <nav className="mx-auto max-w-7xl px-3 sm:px-4 md:px-6 lg:px-8 flex justify-between items-center w-full min-h-[60px]">
        <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-8">
          <Link to="/" className="flex items-center flex-shrink-0">
            <img src={logo} alt="VeilForge Logo" className="h-8 sm:h-10 md:h-12 lg:h-14 w-auto object-contain max-w-[100px] sm:max-w-[120px] md:max-w-[140px] lg:max-w-none" />
          </Link>
          
          {/* Left Navigation Links - Hidden on mobile and small tablets */}
          <ul className="hidden lg:flex space-x-4 xl:space-x-8">
            {leftLinks.map(link => {
              const isActive = location.pathname === link.path;
              return (
                <li key={link.name} className="relative">
                  <Link 
                    to={link.path} 
                    className={cn(
                      "font-medium transition-all duration-200 hover:text-primary hover:bg-accent/50 rounded-lg px-3 py-2 after:absolute after:bottom-0 after:left-3 after:right-3 after:h-0.5 after:bg-primary after:transition-all",
                      isActive 
                        ? "text-primary bg-accent/30 after:w-[calc(100%-1.5rem)]" 
                        : "after:w-0 hover:after:w-[calc(100%-1.5rem)]"
                    )}
                  >
                    {link.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Right Navigation Links - Hidden on mobile and small tablets */}
        <div className="hidden lg:flex items-center space-x-2">
          <ThemeToggle />
          {rightLinks.map(link => (
            <Button key={link.name} asChild variant="ghost" size="icon">
              <Link to={link.path}>
                {link.icon}
              </Link>
            </Button>
          ))}
          {userLinks.map(link => (
            <Button key={link.name} asChild variant="ghost" size="icon">
              <Link to={link.path}>
                {link.icon}
              </Link>
            </Button>
          ))}
          {user ? (
            <Button onClick={handleLogoutClick} variant="ghost" size="icon">
              <LogOut className="h-4 w-4" />
            </Button>
          ) : (
            <Button asChild variant="outline">
              <Link to="/auth">Login</Link>
            </Button>
          )}
        </div>

        {/* Mobile Navigation - Show on mobile and tablet */}
        <div className="lg:hidden flex items-center space-x-2">
          <div className="hidden sm:block">
            <ThemeToggle />
          </div>
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)} 
            className="rounded-full p-2 min-w-[44px] min-h-[44px] hover:bg-accent/50 transition-colors"
            aria-label="Toggle mobile menu"
          >
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </nav>

      {/* Mobile Menu Overlay - Only shown when menu is open */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-[100] lg:hidden">
          {/* Backdrop - Click to close */}
          <div 
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={closeMobileMenu}
          />
          
          {/* Menu Panel */}
          <div className="absolute inset-y-0 right-0 w-[85%] max-w-sm bg-background border-l border-border shadow-2xl overflow-y-auto">
            <div className="flex flex-col h-full min-h-screen">
              {/* Header */}
              <div className="flex justify-between items-center p-4 border-b border-border">
                <div className="text-lg font-semibold text-foreground">Navigation</div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={closeMobileMenu} 
                  className="rounded-full hover:bg-accent"
                >
                  <X className="h-6 w-6" />
                </Button>
              </div>
              
              {/* Menu Content */}
              <div className="flex-1 p-4">
                {/* Theme Toggle for mobile */}
                <div className="sm:hidden mb-6">
                  <ThemeToggle />
                </div>
                
                {/* Navigation Links */}
                <ul className="space-y-2">
                  {leftLinks.map(link => {
                    const isActive = location.pathname === link.path;
                    return (
                      <li key={link.name}>
                        <Link 
                          to={link.path} 
                          className={cn(
                            "block px-4 py-3 text-base font-medium transition-colors rounded-lg border border-transparent",
                            isActive 
                              ? "text-primary bg-accent border-primary/20 shadow-sm" 
                              : "text-foreground hover:text-primary hover:bg-accent/50"
                          )} 
                          onClick={closeMobileMenu}
                        >
                          {link.name}
                        </Link>
                      </li>
                    );
                  })}
                  
                  {/* Divider */}
                  {(rightLinks.length > 0 || userLinks.length > 0) && (
                    <li className="py-2">
                      <div className="border-t border-border"></div>
                    </li>
                  )}
                  
                  {rightLinks.map(link => {
                    const isActive = location.pathname === link.path;
                    return (
                      <li key={link.name}>
                        <Link 
                          to={link.path} 
                          className={cn(
                            "flex items-center gap-3 px-4 py-3 text-base font-medium transition-colors rounded-lg border border-transparent",
                            isActive 
                              ? "text-primary bg-accent border-primary/20 shadow-sm" 
                              : "text-foreground hover:text-primary hover:bg-accent/50"
                          )} 
                          onClick={closeMobileMenu}
                        >
                          {link.icon}
                          {link.name}
                        </Link>
                      </li>
                    );
                  })}
                  
                  {userLinks.map(link => {
                    const isActive = location.pathname === link.path;
                    return (
                      <li key={link.name}>
                        <Link 
                          to={link.path} 
                          className={cn(
                            "flex items-center gap-3 px-4 py-3 text-base font-medium transition-colors rounded-lg border border-transparent",
                            isActive 
                              ? "text-primary bg-accent border-primary/20 shadow-sm" 
                              : "text-foreground hover:text-primary hover:bg-accent/50"
                          )} 
                          onClick={closeMobileMenu}
                        >
                          {link.icon}
                          {link.name}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </div>
              
              {/* Bottom Actions */}
              <div className="border-t border-border p-4 space-y-3">
                {user ? (
                  <Button 
                    onClick={() => { 
                      handleLogoutClick(); 
                      closeMobileMenu(); 
                    }} 
                    variant="outline" 
                    className="w-full h-12 text-base"
                  >
                    <LogOut className="mr-2 h-5 w-5" />
                    Logout
                  </Button>
                ) : (
                  <Button asChild variant="default" className="w-full h-12 text-base">
                    <Link to="/auth" onClick={closeMobileMenu}>
                      Login
                    </Link>
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Logout Confirmation Dialog */}
      <Dialog open={logoutConfirmOpen} onOpenChange={setLogoutConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Logout</DialogTitle>
            <DialogDescription>
              Are you sure you want to logout? You will be redirected to the login page.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setLogoutConfirmOpen(false)}>
              Cancel
            </Button>
            <Button onClick={confirmLogout}>
              Logout
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </header>
  );
}