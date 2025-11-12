import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { 
  User, 
  Mail, 
  UserCircle, 
  Upload, 
  Lock, 
  Phone, 
  Globe, 
  MessageCircle, 
  Camera, 
  Settings, 
  Shield, 
  Calendar, 
  MapPin, 
  Briefcase,
  Edit3,
  Save,
  X,
  Check,
  Info
} from "lucide-react";

export default function Profile() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [userId, setUserId] = useState<string>("");
  const [profile, setProfile] = useState({
    username: "",
    first_name: "",
    last_name: "",
    nickname: "",
    email: "",
    phone: "",
    website: "",
    telegram: "",
    whatsapp: "",
    bio: "",
    role: "subscriber",
    display_name_publicly: "",
    avatar_url: ""
  });
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string>("");
  const [passwords, setPasswords] = useState({
    current: "",
    new: "",
    confirm: ""
  });
  const [activeTab, setActiveTab] = useState("account");
  const [isEditing, setIsEditing] = useState(false);
  const [stats, setStats] = useState({
    totalProjects: 0,
    filesProtected: 0,
    totalOperations: 0,
    accountAge: 0
  });

  useEffect(() => {
    // Check authentication and load profile
    supabase.auth.getUser().then(({ data: { user } }) => {
      if (!user) {
        navigate("/auth");
      } else {
        setUserId(user.id);
        loadProfile(user.id);
        loadUserStats(user.id);
      }
    });
  }, [navigate]);

  const loadProfile = async (uid: string) => {
    try {
      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("user_id", uid)
        .single();

      if (error) throw error;

      if (data) {
        setProfile({
          username: data.username || "",
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          nickname: data.nickname || "",
          email: data.email || "",
          phone: data.phone || "",
          website: data.website || "",
          telegram: data.telegram || "",
          whatsapp: data.whatsapp || "",
          bio: data.bio || "",
          role: data.role || "subscriber",
          display_name_publicly: data.display_name_publicly || "",
          avatar_url: data.avatar_url || ""
        });
        setAvatarPreview(data.avatar_url || "");
      }
    } catch (error: any) {
      console.error("Error loading profile:", error);
    }
  };

  const loadUserStats = async (uid: string) => {
    try {
      // Load user projects count
      const { count: projectCount } = await supabase
        .from("projects")
        .select("*", { count: 'exact', head: true })
        .eq("user_id", uid);

      // Load user files count
      const { count: filesCount } = await supabase
        .from("files")
        .select("*", { count: 'exact', head: true })
        .eq("user_id", uid);

      // Load user operations count
      const { count: operationsCount } = await supabase
        .from("activities")
        .select("*", { count: 'exact', head: true })
        .eq("user_id", uid);

      setStats({
        totalProjects: projectCount || 0,
        filesProtected: filesCount || 0,
        totalOperations: operationsCount || 0,
        accountAge: new Date().getFullYear()
      });
    } catch (error: any) {
      console.error("Error loading user stats:", error);
      // Set default stats if there's an error
      setStats({
        totalProjects: 0,
        filesProtected: 0,
        totalOperations: 0,
        accountAge: new Date().getFullYear()
      });
    }
  };

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      let avatarUrl = profile.avatar_url;

      // Upload avatar if a new file was selected
      if (avatarFile) {
        const fileExt = avatarFile.name.split('.').pop();
        const fileName = `${userId}-avatar-${Date.now()}.${fileExt}`;
        
        // Note: Avatars bucket should be created by admin in Supabase dashboard
        // Skipping bucket creation to avoid permission errors in production

        const { error: uploadError } = await supabase.storage
          .from('avatars')
          .upload(fileName, avatarFile, {
            cacheControl: '3600',
            upsert: true
          });

        if (uploadError) throw uploadError;

        const { data: { publicUrl } } = supabase.storage
          .from('avatars')
          .getPublicUrl(fileName);

        avatarUrl = publicUrl;
      }

      // Update both profiles and users tables
      const { error: profileError } = await supabase
        .from("profiles")
        .update({
          username: profile.username,
          first_name: profile.first_name,
          last_name: profile.last_name,
          nickname: profile.nickname,
          email: profile.email,
          phone: profile.phone,
          website: profile.website,
          telegram: profile.telegram,
          whatsapp: profile.whatsapp,
          bio: profile.bio,
          role: profile.role,
          display_name_publicly: profile.display_name_publicly,
          avatar_url: avatarUrl,
          updated_at: new Date().toISOString()
        })
        .eq("user_id", userId);

      const error = profileError;

      if (error) throw error;

      toast({
        title: "Profile updated",
        description: "Your profile has been updated successfully.",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwords.new !== passwords.confirm) {
      toast({
        title: "Error",
        description: "New passwords don't match",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({
        password: passwords.new
      });

      if (error) throw error;

      toast({
        title: "Password updated",
        description: "Your password has been changed successfully.",
      });
      
      setPasswords({ current: "", new: "", confirm: "" });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-1 pt-20 pb-12">
        <div className="container max-w-6xl">
          <div className="animate-fade-in">
            {/* Header Section */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold mb-2">Profile Settings</h1>
              <p className="text-muted-foreground">
                Manage your account settings and preferences
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Sidebar - Account Management */}
              <Card className="lg:col-span-1 h-fit animate-profile-card hover-lift">
                <CardHeader className="text-center">
                  <div className="relative mx-auto w-24 h-24 mb-4">
                    <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center overflow-hidden border-2 border-primary/20 animate-avatar-pulse">
                      {avatarPreview || profile.avatar_url ? (
                        <img 
                          src={avatarPreview || profile.avatar_url} 
                          alt="Profile Picture" 
                          className="w-full h-full object-cover rounded-full"
                        />
                      ) : (
                        <UserCircle className="h-12 w-12 text-primary" />
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      className="absolute -bottom-1 -right-1 rounded-full w-8 h-8 p-0"
                      onClick={() => document.getElementById('avatar-upload')?.click()}
                    >
                      <Camera className="h-4 w-4" />
                    </Button>
                    <input
                      id="avatar-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                  </div>
                  <CardTitle className="text-lg">
                    {profile.display_name_publicly || profile.first_name || "User"}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => document.getElementById('avatar-upload')?.click()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Photo
                  </Button>
                  <Separator />
                  <div className="space-y-2">
                    <div className="space-y-2">
                      <Label>Old Password</Label>
                      <Input
                        type="password"
                        placeholder="Enter current password"
                        value={passwords.current}
                        onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>New Password</Label>
                      <Input
                        type="password"
                        placeholder="Enter new password"
                        value={passwords.new}
                        onChange={(e) => setPasswords({ ...passwords, new: e.target.value })}
                      />
                    </div>
                    <Button
                      onClick={handleChangePassword}
                      disabled={loading || !passwords.current || !passwords.new}
                      className="w-full"
                      size="sm"
                    >
                      Change Password
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Main Content */}
              <div className="lg:col-span-3 space-y-6">
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="account">Account</TabsTrigger>
                    <TabsTrigger value="profile">Profile</TabsTrigger>
                    <TabsTrigger value="contact">Contact</TabsTrigger>
                    <TabsTrigger value="about">About</TabsTrigger>
                  </TabsList>

                  {/* Account Management Tab */}
                  <TabsContent value="account" className="space-y-4">
                    <Card className="animate-profile-card hover-lift">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          Account Management
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setIsEditing(!isEditing)}
                          >
                            {isEditing ? <X className="h-4 w-4" /> : <Edit3 className="h-4 w-4" />}
                            {isEditing ? "Cancel" : "Edit"}
                          </Button>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <form onSubmit={handleUpdateProfile} className="space-y-6">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="username">Username</Label>
                              <Input
                                id="username"
                                value={profile.username}
                                onChange={(e) => setProfile({ ...profile, username: e.target.value })}
                                disabled={!isEditing}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="first_name">First Name</Label>
                              <Input
                                id="first_name"
                                value={profile.first_name}
                                onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
                                disabled={!isEditing}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="nickname">Nickname</Label>
                              <Input
                                id="nickname"
                                value={profile.nickname}
                                onChange={(e) => setProfile({ ...profile, nickname: e.target.value })}
                                disabled={!isEditing}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="role">Role</Label>
                              <Select
                                value={profile.role}
                                onValueChange={(value) => setProfile({ ...profile, role: value })}
                                disabled={!isEditing}
                              >
                                <SelectTrigger>
                                  <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="subscriber">Subscriber</SelectItem>
                                  <SelectItem value="premium">Premium</SelectItem>
                                  <SelectItem value="admin">Admin</SelectItem>
                                </SelectContent>
                              </Select>
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="last_name">Last Name</Label>
                              <Input
                                id="last_name"
                                value={profile.last_name}
                                onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
                                disabled={!isEditing}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="display_name">Display Name Publicly as</Label>
                              <Input
                                id="display_name"
                                value={profile.display_name_publicly}
                                onChange={(e) => setProfile({ ...profile, display_name_publicly: e.target.value })}
                                disabled={!isEditing}
                              />
                            </div>
                          </div>

                          {isEditing && (
                            <div className="flex gap-4">
                              <Button type="submit" disabled={loading}>
                                <Save className="h-4 w-4 mr-2" />
                                {loading ? "Saving..." : "Save Changes"}
                              </Button>
                              <Button 
                                type="button" 
                                variant="outline" 
                                onClick={() => setIsEditing(false)}
                              >
                                Cancel
                              </Button>
                            </div>
                          )}
                        </form>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* Profile Information Tab */}
                  <TabsContent value="profile" className="space-y-4">
                    <Card className="animate-profile-card hover-lift">
                      <CardHeader>
                        <CardTitle>Profile Information</CardTitle>
                        <CardDescription>
                          Manage your public profile details
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="email" className="flex items-center gap-2">
                                <Mail className="h-4 w-4" />
                                Email (required)
                              </Label>
                              <Input
                                id="email"
                                type="email"
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="phone" className="flex items-center gap-2">
                                <Phone className="h-4 w-4" />
                                Phone
                              </Label>
                              <Input
                                id="phone"
                                value={profile.phone}
                                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                              />
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <Label htmlFor="website" className="flex items-center gap-2">
                              <Globe className="h-4 w-4" />
                              Website
                            </Label>
                            <Input
                              id="website"
                              value={profile.website}
                              onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                              placeholder="https://example.com"
                            />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* Contact Info Tab */}
                  <TabsContent value="contact" className="space-y-4">
                    <Card className="animate-profile-card hover-lift">
                      <CardHeader>
                        <CardTitle>Contact Info</CardTitle>
                        <CardDescription>
                          Add your social media and messaging contacts
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <Label htmlFor="whatsapp" className="flex items-center gap-2">
                                <MessageCircle className="h-4 w-4" />
                                WhatsApp
                              </Label>
                              <Input
                                id="whatsapp"
                                value={profile.whatsapp}
                                onChange={(e) => setProfile({ ...profile, whatsapp: e.target.value })}
                                placeholder="@username"
                              />
                            </div>
                            <div className="space-y-2">
                              <Label htmlFor="telegram" className="flex items-center gap-2">
                                <MessageCircle className="h-4 w-4" />
                                Telegram
                              </Label>
                              <Input
                                id="telegram"
                                value={profile.telegram}
                                onChange={(e) => setProfile({ ...profile, telegram: e.target.value })}
                                placeholder="@username"
                              />
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {/* About the User Tab */}
                  <TabsContent value="about" className="space-y-4">
                    <Card className="animate-profile-card hover-lift">
                      <CardHeader>
                        <CardTitle>About the User</CardTitle>
                        <CardDescription>
                          Tell others about yourself
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="space-y-2">
                            <Label htmlFor="bio">Biographical Info</Label>
                            <Textarea
                              id="bio"
                              value={profile.bio}
                              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                              placeholder="Share a little biographical information to fill out your profile..."
                              rows={6}
                            />
                            <p className="text-xs text-muted-foreground">
                              Share a little biographical information to fill out your profile. This may be shown publicly.
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Account Statistics */}
                    <Card className="animate-profile-card hover-lift">
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Shield className="h-5 w-5" />
                          Account Statistics
                        </CardTitle>
                        <CardDescription>
                          Overview of your VeilForge activity
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border hover-lift animate-stat-counter">
                            <Briefcase className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">{stats.totalProjects}</p>
                            <p className="text-sm text-blue-600 dark:text-blue-400">Total Projects</p>
                          </div>
                          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border hover-lift animate-stat-counter" style={{animationDelay: '0.1s'}}>
                            <Shield className="h-8 w-8 text-green-600 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-green-700 dark:text-green-300">{stats.filesProtected}</p>
                            <p className="text-sm text-green-600 dark:text-green-400">Files Protected</p>
                          </div>
                          <div className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border hover-lift animate-stat-counter" style={{animationDelay: '0.2s'}}>
                            <Calendar className="h-8 w-8 text-orange-600 mx-auto mb-2" />
                            <p className="text-2xl font-bold text-orange-700 dark:text-orange-300">2025</p>
                            <p className="text-sm text-orange-600 dark:text-orange-400">Member Since</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>
                </Tabs>

                {/* Universal Save Button */}
                <Card className="animate-profile-card">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Info className="h-4 w-4" />
                        Changes will be saved automatically
                      </div>
                      <div className="flex gap-3">
                        <Button variant="outline" onClick={() => navigate("/dashboard")}>
                          Back to Dashboard
                        </Button>
                        <Button onClick={handleUpdateProfile} disabled={loading}>
                          {loading ? (
                            <>
                              <Settings className="h-4 w-4 mr-2 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            <>
                              <Check className="h-4 w-4 mr-2" />
                              Save All Changes
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
