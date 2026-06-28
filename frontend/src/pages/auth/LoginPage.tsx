import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { BookOpen, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { Button, Input, Alert } from '../../components/ui';
import { useAuthStore, getRoleDashboardPath } from '../../stores/authStore';
import api from '../../lib/api';

interface LoginResponse {
  access_token: string;
  role: 'super_admin' | 'library_admin' | 'librarian' | 'reader';
  user_id: string;
  tenant_id?: string | null;
}

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setAuth } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || null;

  const loginMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post<LoginResponse>('/auth/login', { email, password });
      return res.data;
    },
    onSuccess: (data) => {
      setAuth(
        { userId: data.user_id, role: data.role, tenantId: data.tenant_id },
        data.access_token,
      );
      const dest = from ?? getRoleDashboardPath(data.role);
      navigate(dest, { replace: true });
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message;
      setError(msg ?? 'Login failed. Please check your credentials.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }
    loginMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-obsidian-950 flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex flex-col justify-between w-[480px] bg-gradient-to-br from-obsidian-900 to-obsidian-950 border-r border-white/5 p-12 relative overflow-hidden">
        {/* Glow */}
        <div className="absolute top-1/3 left-1/3 w-72 h-72 rounded-full bg-emerald-600/15 blur-[80px] pointer-events-none" />

        <Link to="/" className="flex items-center gap-3 z-10">
          <div className="w-9 h-9 rounded-xl bg-emerald-600 flex items-center justify-center">
            <BookOpen size={18} className="text-white" />
          </div>
          <span className="font-display font-bold text-2xl text-white">
            Soma<span className="text-emerald-400">Hub</span>
          </span>
        </Link>

        <div className="z-10">
          <h2 className="text-3xl font-display font-bold text-white mb-4 leading-tight">
            The modern operating system for libraries.
          </h2>
          <p className="text-obsidian-400 leading-relaxed mb-8">
            Manage books, borrowers, and digital reading — all from one beautiful platform.
          </p>
          <div className="flex flex-col gap-3">
            {[
              'Multi-tenant library management',
              'AI-assisted book cataloging',
              'Digital bookstore with in-platform reader',
              'Real-time analytics & reporting',
            ].map((feat) => (
              <div key={feat} className="flex items-center gap-3 text-sm text-obsidian-300">
                <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                </div>
                {feat}
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-obsidian-600 z-10">
          © {new Date().getFullYear()} SomaHub Enterprise
        </p>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-[440px] animate-slide-up">
          {/* Mobile logo */}
          <Link to="/" className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
              <BookOpen size={15} className="text-white" />
            </div>
            <span className="font-display font-bold text-xl text-white">
              Soma<span className="text-emerald-400">Hub</span>
            </span>
          </Link>

          <h1 className="text-3xl font-display font-bold text-white mb-2">Welcome back</h1>
          <p className="text-obsidian-400 mb-8">
            Don't have an account?{' '}
            <Link to="/auth/signup/library" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
              Sign up free
            </Link>
          </p>

          {error && (
            <Alert variant="error" className="mb-6" onDismiss={() => setError('')}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              id="email"
              label="Email address"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftAddon={<Mail size={16} />}
              autoComplete="email"
              required
            />

            <div>
              <Input
                id="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftAddon={<Lock size={16} />}
                rightAddon={
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="text-obsidian-400 hover:text-obsidian-600 transition-colors"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                }
                autoComplete="current-password"
                required
              />
              <div className="flex justify-end mt-1.5">
                <Link
                  to="/auth/forgot-password"
                  className="text-xs text-obsidian-400 hover:text-emerald-400 transition-colors"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full"
              loading={loginMutation.isPending}
              rightIcon={<ArrowRight size={18} />}
            >
              Sign in
            </Button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <p className="text-sm text-obsidian-500">
              Are you a reader?{' '}
              <Link to="/auth/signup/reader" className="text-emerald-400 hover:text-emerald-300 transition-colors font-medium">
                Create reader account
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
