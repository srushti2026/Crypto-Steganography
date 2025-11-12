
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

  return <header className={cn("fixed top-0 left-0 right-0 z-50 transition-all duration-300", scrolled ? "bg-background/95 dark:bg-card/95 backdrop-blur-lg py-1 shadow-lg shadow-primary/10 border-b border-border/20" : "bg-background/80 dark:bg-card/80 backdrop-blur-md py-1.5 shadow-sm")}>
      <nav className="container flex justify-between items-center">
        <div className="flex items-center space-x-4 lg:space-x-8">
          <Link to="/" className="flex items-center">
            <img src={logo} alt="VeilForge Logo" className="h-10 sm:h-12 lg:h-14 w-auto object-contain max-w-[120px] sm:max-w-[140px] lg:max-w-none" />
          </Link>
          
          {/* Left Navigation Links */}
          <ul className="hidden md:flex space-x-4 lg:space-x-8">
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

        {/* Right Navigation Links */}
        <div className="hidden md:flex items-center space-x-2">
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

        {/* Mobile Navigation */}
        <div className="md:hidden flex items-center space-x-2">
          <ThemeToggle />
          <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="rounded-full">
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <div className={cn("fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden transition-opacity duration-300", mobileMenuOpen ? "opacity-100" : "opacity-0 pointer-events-none")}>
        <div className={cn("fixed inset-y-0 right-0 w-4/5 max-w-xs bg-card shadow-xl p-4 sm:p-6 transition-transform duration-300 ease-in-out overflow-y-auto", mobileMenuOpen ? "translate-x-0" : "translate-x-full")}>
          <div className="flex flex-col h-full justify-between min-h-screen">
            <div>
              <div className="flex justify-end mb-6 sm:mb-8">
                <Button variant="ghost" size="icon" onClick={() => setMobileMenuOpen(false)} className="rounded-full">
                  <X className="h-6 w-6" />
                </Button>
              </div>
              <ul className="space-y-4 sm:space-y-6">
                {leftLinks.map(link => {
                  const isActive = location.pathname === link.path;
                  return (
                    <li key={link.name}>
                      <Link 
                        to={link.path} 
                        className={cn(
                          "text-base sm:text-lg font-medium transition-colors hover:text-primary block px-3 py-2 rounded-lg",
                          isActive ? "text-primary bg-accent/30" : ""
                        )} 
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        {link.name}
                      </Link>
                    </li>
                  );
                })}
                {rightLinks.map(link => {
                  const isActive = location.pathname === link.path;
                  return (
                    <li key={link.name}>
                      <Link 
                        to={link.path} 
                        className={cn(
                          "text-base sm:text-lg font-medium transition-colors hover:text-primary flex items-center gap-2 px-3 py-2 rounded-lg",
                          isActive ? "text-primary bg-accent/30" : ""
                        )} 
                        onClick={() => setMobileMenuOpen(false)}
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
                          "text-base sm:text-lg font-medium transition-colors hover:text-primary flex items-center gap-2 px-3 py-2 rounded-lg",
                          isActive ? "text-primary bg-accent/30" : ""
                        )} 
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        {link.icon}
                        {link.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
            
            <div className="space-y-3">
              {user ? (
                <Button onClick={() => { handleLogoutClick(); setMobileMenuOpen(false); }} variant="outline" className="w-full">
                  <LogOut className="mr-2 h-4 w-4" />
                  Logout
                </Button>
              ) : (
                <Button asChild variant="outline" className="w-full">
                  <Link to="/auth" onClick={() => setMobileMenuOpen(false)}>
                    Login
                  </Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

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
    </header>;
}
