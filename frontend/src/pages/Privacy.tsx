import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Shield, Lock, Eye, Database } from "lucide-react";

const Privacy = () => {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      
      <main className="container mx-auto px-4 py-24">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-6">
              <Shield className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
              Privacy Policy
            </h1>
            <p className="text-muted-foreground">Last updated: {new Date().toLocaleDateString()}</p>
          </div>

          {/* Key Principles */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="p-6 rounded-lg border bg-card text-center">
              <Lock className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Your Data is Encrypted</h3>
              <p className="text-sm text-muted-foreground">End-to-end encryption for all files</p>
            </div>
            <div className="p-6 rounded-lg border bg-card text-center">
              <Eye className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-semibold mb-2">No Third-Party Access</h3>
              <p className="text-sm text-muted-foreground">We never share your data</p>
            </div>
            <div className="p-6 rounded-lg border bg-card text-center">
              <Database className="w-10 h-10 text-primary mx-auto mb-3" />
              <h3 className="font-semibold mb-2">You Control Your Data</h3>
              <p className="text-sm text-muted-foreground">Delete anytime you want</p>
            </div>
          </div>

          {/* Privacy Content */}
          <div className="prose prose-invert max-w-none space-y-8">
            <section>
              <h2 className="text-2xl font-bold mb-4">1. Information We Collect</h2>
              <p className="text-muted-foreground mb-4">
                We collect information that you provide directly to us, including:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-2">
                <li>Account information (email address, password)</li>
                <li>Files you upload for steganography processing</li>
                <li>Project metadata (names, timestamps, descriptions)</li>
                <li>Usage data and interaction with our services</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">2. How We Use Your Information</h2>
              <p className="text-muted-foreground mb-4">
                Your information is used to:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-2">
                <li>Provide and maintain our steganography services</li>
                <li>Process your files with advanced embedding techniques</li>
                <li>Send you service-related notifications</li>
                <li>Improve and optimize our platform</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">3. Data Security</h2>
              <p className="text-muted-foreground mb-4">
                We implement industry-standard security measures to protect your data:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-2">
                <li>End-to-end encryption for all uploaded files</li>
                <li>Secure password hashing with bcrypt</li>
                <li>Regular security audits and updates</li>
                <li>Access controls and authentication protocols</li>
                <li>Data stored on secure Supabase infrastructure</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">4. Data Retention</h2>
              <p className="text-muted-foreground">
                We retain your data only as long as necessary to provide our services. You can delete your 
                projects and account data at any time through your dashboard settings. Upon deletion, your 
                data is permanently removed from our systems within 30 days.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">5. Third-Party Services</h2>
              <p className="text-muted-foreground">
                VeilForge uses Supabase for backend infrastructure. Supabase complies with GDPR and other 
                international privacy regulations. We do not share your data with any other third parties 
                for marketing or advertising purposes.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">6. Your Rights</h2>
              <p className="text-muted-foreground mb-4">
                You have the right to:
              </p>
              <ul className="list-disc pl-6 text-muted-foreground space-y-2">
                <li>Access your personal data</li>
                <li>Correct inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Export your data in a portable format</li>
                <li>Opt-out of communications</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">7. Cookies and Tracking</h2>
              <p className="text-muted-foreground">
                We use essential cookies to maintain your session and provide functionality. We do not use 
                third-party tracking cookies or advertising cookies. You can disable cookies in your browser, 
                but this may affect the functionality of our services.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">8. Changes to This Policy</h2>
              <p className="text-muted-foreground">
                We may update this privacy policy from time to time. We will notify you of any significant 
                changes via email or through our platform. Your continued use of VeilForge after such changes 
                constitutes acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-bold mb-4">9. Contact Us</h2>
              <p className="text-muted-foreground">
                If you have questions about this privacy policy or our data practices, please contact us at:
              </p>
              <p className="text-primary font-medium mt-2">privacy@veilforge.com</p>
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Privacy;
