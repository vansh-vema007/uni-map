import { useNavigate } from 'react-router-dom';
import { MapPin, Brain, Navigation, Users, Bell, TrendingUp, Zap, ArrowRight } from 'lucide-react';
import { getAuthToken } from '../App';
import { useEffect } from 'react';

export default function LandingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      navigate('/dashboard');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-xl bg-black/60 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#3B82F6] rounded-xl flex items-center justify-center">
              <Zap className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold tracking-tight">CampusAI</span>
          </div>
          <button
            data-testid="nav-login-btn"
            onClick={() => navigate('/auth')}
            className="px-6 py-2.5 bg-[#2563EB] hover:bg-[#3B82F6] rounded-xl font-semibold transition-colors"
          >
            Login
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-block mb-6 px-4 py-2 bg-[#111111] border border-white/10 rounded-full">
              <span className="text-sm text-[#3B82F6] font-semibold tracking-wider uppercase">AI-Powered Campus Navigation</span>
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter mb-6 leading-tight">
              Navigate Your Campus
              <span className="block mt-2 bg-gradient-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
                With Intelligence
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-[#A1A1AA] mb-10 max-w-2xl mx-auto leading-relaxed">
              Smart navigation, AI assistant, real-time schedules, and personalized recommendations. Your complete intelligent campus companion.
            </p>
            <div className="flex gap-4 justify-center">
              <button
                data-testid="hero-get-started-btn"
                onClick={() => navigate('/auth')}
                className="px-8 py-4 bg-[#2563EB] hover:bg-[#3B82F6] rounded-xl font-bold text-lg transition-all hover:scale-105 hover:shadow-lg hover:shadow-[#2563EB]/50 flex items-center gap-2"
              >
                Get Started <ArrowRight className="w-5 h-5" />
              </button>
              <button
                data-testid="learn-more-btn"
                className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl font-bold text-lg transition-all"
              >
                Learn More
              </button>
            </div>
          </div>

          {/* Hero Image */}
          <div className="mt-20 relative">
            <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-transparent z-10"></div>
            <div className="glass-panel p-4">
              <img
                src="https://images.pexels.com/photos/38271/ipad-map-tablet-internet-38271.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
                alt="Campus navigation"
                className="w-full h-[400px] object-cover rounded-xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <span className="text-sm text-[#3B82F6] font-semibold tracking-[0.2em] uppercase">Features</span>
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mt-4">Everything You Need</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div data-testid="feature-smart-navigation" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <Navigation className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Smart Navigation</h3>
              <p className="text-[#A1A1AA] leading-relaxed">AI-powered route optimization with real-time updates. Get to your class on time, every time.</p>
            </div>

            <div data-testid="feature-ai-assistant" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <Brain className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">AI Assistant</h3>
              <p className="text-[#A1A1AA] leading-relaxed">Chat with your personal campus assistant. Get instant answers about classes, faculty, and schedules.</p>
            </div>

            <div data-testid="feature-campus-map" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <MapPin className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Interactive Map</h3>
              <p className="text-[#A1A1AA] leading-relaxed">Explore campus buildings, facilities, and points of interest with our detailed interactive map.</p>
            </div>

            <div data-testid="feature-schedule" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <TrendingUp className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Smart Scheduling</h3>
              <p className="text-[#A1A1AA] leading-relaxed">Automated timetable sync with predictive insights. Never miss a class or deadline again.</p>
            </div>

            <div data-testid="feature-notifications" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <Bell className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Smart Alerts</h3>
              <p className="text-[#A1A1AA] leading-relaxed">Intelligent notifications for classes, assignments, and campus events. Stay informed effortlessly.</p>
            </div>

            <div data-testid="feature-social" className="glass-panel p-8 card-hover">
              <div className="w-14 h-14 bg-[#2563EB]/20 rounded-2xl flex items-center justify-center mb-6">
                <Users className="w-7 h-7 text-[#3B82F6]" />
              </div>
              <h3 className="text-2xl font-bold mb-3">Social Connect</h3>
              <p className="text-[#A1A1AA] leading-relaxed">Find friends on campus and join study groups. Build your academic network seamlessly.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6 bg-[#111111]/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div data-testid="stat-accuracy">
              <div className="text-5xl font-bold text-[#3B82F6] mb-2">99.9%</div>
              <div className="text-[#A1A1AA] text-lg">Navigation Accuracy</div>
            </div>
            <div data-testid="stat-time-saved">
              <div className="text-5xl font-bold text-[#3B82F6] mb-2">15min</div>
              <div className="text-[#A1A1AA] text-lg">Average Time Saved Daily</div>
            </div>
            <div data-testid="stat-users">
              <div className="text-5xl font-bold text-[#3B82F6] mb-2">10K+</div>
              <div className="text-[#A1A1AA] text-lg">Active Students</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
            Ready to Transform Your
            <span className="block mt-2 bg-gradient-to-r from-[#3B82F6] to-[#2563EB] bg-clip-text text-transparent">
              Campus Experience?
            </span>
          </h2>
          <p className="text-xl text-[#A1A1AA] mb-10">Join thousands of students already navigating smarter</p>
          <button
            data-testid="cta-get-started-btn"
            onClick={() => navigate('/auth')}
            className="px-10 py-5 bg-[#2563EB] hover:bg-[#3B82F6] rounded-xl font-bold text-xl transition-all hover:scale-105 hover:shadow-2xl hover:shadow-[#2563EB]/50"
          >
            Get Started Now
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#2563EB] to-[#3B82F6] rounded-xl flex items-center justify-center">
                <Zap className="w-6 h-6" />
              </div>
              <span className="text-xl font-bold">CampusAI</span>
            </div>
            <div className="text-[#A1A1AA]">
              © 2026 CampusAI. Built for Chandigarh University.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
