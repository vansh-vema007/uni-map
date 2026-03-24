import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API, setAuthToken } from '../App';
import { toast } from 'sonner';
import { Zap, ArrowLeft } from 'lucide-react';

export default function AuthPage({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    roll_number: '',
    email: '',
    password: '',
    name: '',
    year: 1,
    department: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const payload = isLogin
        ? { roll_number: formData.roll_number, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      setAuthToken(response.data.token);
      setIsAuthenticated(true);
      toast.success(isLogin ? 'Login successful!' : 'Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <button
          data-testid="back-to-home-btn"
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-[#A1A1AA] hover:text-white mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to home
        </button>

        <div className="glass-panel p-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-[#2563EB] to-[#3B82F6] rounded-xl flex items-center justify-center">
              <Zap className="w-7 h-7" />
            </div>
            <span className="text-3xl font-bold tracking-tight">CampusAI</span>
          </div>

          <h2 className="text-3xl font-bold mb-2">{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
          <p className="text-[#A1A1AA] mb-8">
            {isLogin ? 'Login to access your dashboard' : 'Join the intelligent campus community'}
          </p>

          <form data-testid={isLogin ? 'login-form' : 'signup-form'} onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold mb-2" htmlFor="roll_number">
                Roll Number
              </label>
              <input
                data-testid="input-roll-number"
                type="text"
                id="roll_number"
                name="roll_number"
                value={formData.roll_number}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                placeholder="Enter your roll number"
                required
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <label className="block text-sm font-semibold mb-2" htmlFor="name">
                    Full Name
                  </label>
                  <input
                    data-testid="input-name"
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                    placeholder="Enter your name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold mb-2" htmlFor="email">
                    Email
                  </label>
                  <input
                    data-testid="input-email"
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                    placeholder="your.email@example.com"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2" htmlFor="year">
                      Year
                    </label>
                    <select
                      data-testid="input-year"
                      id="year"
                      name="year"
                      value={formData.year}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                      required
                    >
                      <option value={1}>1st Year</option>
                      <option value={2}>2nd Year</option>
                      <option value={3}>3rd Year</option>
                      <option value={4}>4th Year</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold mb-2" htmlFor="department">
                      Department
                    </label>
                    <select
                      data-testid="input-department"
                      id="department"
                      name="department"
                      value={formData.department}
                      onChange={handleChange}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                      required
                    >
                      <option value="">Select</option>
                      <option value="CSE">CSE</option>
                      <option value="ECE">ECE</option>
                      <option value="ME">ME</option>
                      <option value="CE">CE</option>
                      <option value="IT">IT</option>
                    </select>
                  </div>
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-semibold mb-2" htmlFor="password">
                Password
              </label>
              <input
                data-testid="input-password"
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-[#2563EB] focus:outline-none transition-colors"
                placeholder="Enter your password"
                required
              />
            </div>

            <button
              data-testid={isLogin ? 'login-submit-btn' : 'signup-submit-btn'}
              type="submit"
              disabled={loading}
              className="w-full py-4 bg-[#2563EB] hover:bg-[#3B82F6] rounded-xl font-bold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Please wait...' : isLogin ? 'Login' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              data-testid="toggle-auth-mode-btn"
              onClick={() => setIsLogin(!isLogin)}
              className="text-[#A1A1AA] hover:text-white transition-colors"
            >
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <span className="text-[#3B82F6] font-semibold">{isLogin ? 'Sign up' : 'Login'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
