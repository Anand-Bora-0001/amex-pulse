/**
 * AmEx Pulse — Login Page
 * ========================
 * Premium login experience with animated background.
 */

import { useState } from 'react';
import { Zap, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { authApi } from '../../lib/api';
import type { User } from '../../types';

interface LoginPageProps {
  onLogin: (user: User, token: string) => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('admin@amexpulse.com');
  const [password, setPassword] = useState('admin123');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await authApi.login(email, password);
      const { access_token, user } = res.data;
      onLogin(user, access_token);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-bg">
      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full opacity-10"
            style={{
              width: `${60 + i * 40}px`,
              height: `${60 + i * 40}px`,
              background: 'var(--amex-blue)',
              top: `${10 + i * 15}%`,
              left: `${5 + i * 16}%`,
              animation: `floatBg ${15 + i * 3}s ease-in-out infinite`,
              animationDelay: `${i * 2}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl gradient-blue mb-4 shadow-lg shadow-blue-500/30">
            <Zap size={32} className="text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">AmEx Pulse</h1>
          <p className="text-blue-300/80 text-sm mt-1">
            AI-Powered Customer Journey Intelligence
          </p>
        </div>

        {/* Login Card */}
        <div
          className="rounded-2xl p-8"
          style={{
            background: 'rgba(255, 255, 255, 0.07)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.3)',
          }}
        >
          <h2 className="text-xl font-semibold text-white mb-1">Welcome back</h2>
          <p className="text-blue-200/60 text-sm mb-6">Sign in to your dashboard</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-blue-200/80 mb-1.5">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-white placeholder-blue-300/40 text-sm
                  transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                style={{
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                }}
                placeholder="you@company.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-blue-200/80 mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl text-white placeholder-blue-300/40 text-sm
                    transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500/50 pr-11"
                  style={{
                    background: 'rgba(255, 255, 255, 0.06)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                  }}
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-blue-300/50 hover:text-blue-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl font-semibold text-white text-sm
                gradient-blue hover:opacity-90 transition-all duration-200
                flex items-center justify-center gap-2 disabled:opacity-50
                shadow-lg shadow-blue-600/30"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Sign In
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 pt-4 border-t border-white/10">
            <p className="text-blue-200/40 text-xs text-center mb-3">Demo Credentials</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                { role: 'Admin', email: 'admin@amexpulse.com', pw: 'admin123' },
                { role: 'Agent', email: 'agent@amexpulse.com', pw: 'agent123' },
                { role: 'Analyst', email: 'analyst@amexpulse.com', pw: 'analyst123' },
                { role: 'Manager', email: 'manager@amexpulse.com', pw: 'manager123' },
              ].map((cred) => (
                <button
                  key={cred.role}
                  type="button"
                  onClick={() => { setEmail(cred.email); setPassword(cred.pw); }}
                  className="px-3 py-2 rounded-lg text-blue-300/70 hover:text-white hover:bg-white/5
                    transition-all text-left border border-white/5"
                >
                  <span className="font-medium">{cred.role}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-center text-blue-300/30 text-xs mt-6">
          AmEx CodeStreet Hackathon 2026 • Enterprise Demo
        </p>
      </div>
    </div>
  );
}
