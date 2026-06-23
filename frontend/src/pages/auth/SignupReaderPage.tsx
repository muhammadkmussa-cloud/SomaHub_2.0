import { useState } from 'react';
import { Link } from 'react-router-dom';

import { useMutation } from '@tanstack/react-query';
import { BookOpen, User, Mail, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { Button, Input, Alert } from '../../components/ui';
import api from '../../lib/api';

export default function SignupReaderPage() {
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm_password: '' });

  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');
  const [success, setSuccess] = useState(false);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (!form.username.trim()) errs.username = 'Username is required.';
    if (!form.email.trim()) errs.email = 'Email is required.';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters.';
    if (form.password !== form.confirm_password) errs.confirm_password = 'Passwords do not match.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const signupMutation = useMutation({
    mutationFn: () => api.post('/auth/signup/reader', form),
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
          <h2 className="text-3xl font-display font-bold text-white mb-3">Account created!</h2>
          <p className="text-obsidian-400 mb-8">
            Welcome to SomaHub. Please check your email to verify your account, then log in.
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
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center p-6">
      <div className="w-full max-w-[440px] animate-slide-up">
        <Link to="/" className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
            <BookOpen size={15} className="text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">
            Soma<span className="text-emerald-400">Hub</span>
          </span>
        </Link>

        <h1 className="text-3xl font-display font-bold text-white mb-2">Create reader account</h1>
        <p className="text-obsidian-400 mb-8">
          Already have an account?{' '}
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
          <Input
            id="username"
            label="Username"
            placeholder="johndoe"
            value={form.username}
            onChange={update('username')}
            leftAddon={<User size={16} />}
            error={errors.username}
            autoComplete="username"
            required
          />
          <Input
            id="email"
            label="Email address"
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={update('email')}
            leftAddon={<Mail size={16} />}
            error={errors.email}
            autoComplete="email"
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
            autoComplete="new-password"
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
            autoComplete="new-password"
            required
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            loading={signupMutation.isPending}
            rightIcon={<ArrowRight size={18} />}
          >
            Create account
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-obsidian-500">
          Are you a library?{' '}
          <Link to="/auth/signup/library" className="text-emerald-400 hover:text-emerald-300 transition-colors font-medium">
            Sign up as institution
          </Link>
        </p>
      </div>
    </div>
  );
}
