import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { BookOpen, Building2, User, Mail, Lock, Eye, EyeOff, MapPin, ArrowRight } from 'lucide-react';
import { Button, Input, Alert } from '../../components/ui';
import api from '../../lib/api';

const LIBRARY_TYPES = [
  'School Library',
  'College Library',
  'University Library',
  'Public Library',
  'Research Library',
  'Other',
];

export default function SignupLibraryPage() {
  const [form, setForm] = useState({
    library_name: '',
    admin_username: '',
    email: '',
    password: '',
    confirm_password: '',
    library_type: '',
    location: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');
  const [success, setSuccess] = useState(false);

  const update = (field: string) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.library_name.trim()) errs.library_name = 'Library name is required.';
    if (!form.admin_username.trim()) errs.admin_username = 'Admin username is required.';
    if (!form.email.trim()) errs.email = 'Email is required.';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters.';
    if (form.password !== form.confirm_password) errs.confirm_password = 'Passwords do not match.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const signupMutation = useMutation({
    mutationFn: () => api.post('/auth/signup/library', form),
    onSuccess: () => setSuccess(true),
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message;
      setServerError(msg ?? 'Signup failed. Please try again.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setServerError('');
    if (validate()) signupMutation.mutate();
  };

  if (success) {
    return (
      <div className="min-h-screen bg-obsidian-950 flex items-center justify-center p-6">
        <div className="text-center max-w-md animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-5">
            <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold text-lg">✓</div>
          </div>
          <h2 className="text-3xl font-display font-bold text-white mb-3">Library registered!</h2>
          <p className="text-obsidian-400 mb-8">
            Your library account has been created. Please verify your email address to activate your account.
          </p>
          <Link to="/auth/login">
            <Button variant="primary" size="lg" rightIcon={<ArrowRight size={18} />}>
              Go to Login
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-obsidian-950 py-12 px-6 flex items-start justify-center">
      <div className="w-full max-w-[520px] animate-slide-up">
        <Link to="/" className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
            <BookOpen size={15} className="text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">
            Soma<span className="text-emerald-400">Hub</span>
          </span>
        </Link>

        <h1 className="text-3xl font-display font-bold text-white mb-2">Register your library</h1>
        <p className="text-obsidian-400 mb-8">
          Already registered?{' '}
          <Link to="/auth/login" className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors">
            Sign in
          </Link>
        </p>

        {serverError && (
          <Alert variant="error" className="mb-6" onDismiss={() => setServerError('')}>
            {serverError}
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Library info */}
          <div className="p-5 rounded-xl bg-white/[0.04] border border-white/8 space-y-4">
            <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Library Information</p>
            <Input
              id="library_name"
              label="Library name"
              placeholder="e.g. Nairobi University Library"
              value={form.library_name}
              onChange={update('library_name')}
              leftAddon={<Building2 size={16} />}
              error={errors.library_name}
              required
            />
            <div>
              <label htmlFor="library_type" className="block text-sm font-medium text-obsidian-300 mb-1">
                Library type
              </label>
              <select
                id="library_type"
                value={form.library_type}
                onChange={update('library_type')}
                className="w-full rounded-lg border border-white/10 bg-obsidian-800 px-3.5 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400 transition-all"
              >
                <option value="">Select type (optional)</option>
                {LIBRARY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <Input
              id="location"
              label="Location (optional)"
              placeholder="City, Country"
              value={form.location}
              onChange={update('location')}
              leftAddon={<MapPin size={16} />}
            />
          </div>

          {/* Admin account */}
          <div className="p-5 rounded-xl bg-white/[0.04] border border-white/8 space-y-4">
            <p className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Admin Account</p>
            <Input
              id="admin_username"
              label="Admin username"
              placeholder="libadmin"
              value={form.admin_username}
              onChange={update('admin_username')}
              leftAddon={<User size={16} />}
              error={errors.admin_username}
              required
            />
            <Input
              id="email"
              label="Email address"
              type="email"
              placeholder="library@institution.edu"
              value={form.email}
              onChange={update('email')}
              leftAddon={<Mail size={16} />}
              error={errors.email}
              required
            />
            <Input
              id="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Min. 8 characters"
              value={form.password}
              onChange={update('password')}
              leftAddon={<Lock size={16} />}
              rightAddon={
                <button type="button" onClick={() => setShowPassword((s) => !s)} aria-label="Toggle password">
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              }
              error={errors.password}
              required
            />
            <Input
              id="confirm_password"
              label="Confirm password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Repeat password"
              value={form.confirm_password}
              onChange={update('confirm_password')}
              leftAddon={<Lock size={16} />}
              error={errors.confirm_password}
              required
            />
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            loading={signupMutation.isPending}
            rightIcon={<ArrowRight size={18} />}
          >
            Register Library
          </Button>

          <p className="text-center text-xs text-obsidian-500">
            By registering, you agree to our{' '}
            <a href="#" className="text-emerald-400 hover:underline">Terms of Service</a>
            {' '}and{' '}
            <a href="#" className="text-emerald-400 hover:underline">Privacy Policy</a>.
          </p>
        </form>
      </div>
    </div>
  );
}
