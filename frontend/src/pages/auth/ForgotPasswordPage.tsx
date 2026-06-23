import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { BookOpen, Mail, ArrowLeft, ArrowRight } from 'lucide-react';
import { Button, Input, Alert } from '../../components/ui';
import api from '../../lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [serverError, setServerError] = useState('');

  const mutation = useMutation({
    mutationFn: () => api.post('/auth/forgot-password', { email }),
    onSuccess: () => setSubmitted(true),
    onError: () => setSubmitted(true), // Always succeed (avoids email enumeration)
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setServerError('');
    if (!email) { setServerError('Please enter your email address.'); return; }
    mutation.mutate();
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-obsidian-950 flex items-center justify-center p-6">
        <div className="text-center max-w-md animate-scale-in">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 flex items-center justify-center mx-auto mb-5">
            <Mail size={28} className="text-emerald-400" />
          </div>
          <h2 className="text-3xl font-display font-bold text-white mb-3">Check your inbox</h2>
          <p className="text-obsidian-400 mb-8">
            If <span className="text-emerald-400">{email}</span> is registered, you'll receive a password reset link shortly.
          </p>
          <Link to="/auth/login">
            <Button variant="ghost" size="sm" leftIcon={<ArrowLeft size={16} />} className="text-obsidian-400 hover:text-white">
              Back to login
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center p-6">
      <div className="w-full max-w-[420px] animate-slide-up">
        <Link to="/" className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
            <BookOpen size={15} className="text-white" />
          </div>
          <span className="font-display font-bold text-xl text-white">
            Soma<span className="text-emerald-400">Hub</span>
          </span>
        </Link>

        <Link to="/auth/login" className="inline-flex items-center gap-1.5 text-sm text-obsidian-400 hover:text-emerald-400 transition-colors mb-6">
          <ArrowLeft size={14} />
          Back to login
        </Link>

        <h1 className="text-3xl font-display font-bold text-white mb-2">Reset your password</h1>
        <p className="text-obsidian-400 mb-8">
          Enter your email and we'll send you a link to reset your password.
        </p>

        {serverError && (
          <Alert variant="error" className="mb-6">{serverError}</Alert>
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
            required
          />
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            loading={mutation.isPending}
            rightIcon={<ArrowRight size={18} />}
          >
            Send Reset Link
          </Button>
        </form>
      </div>
    </div>
  );
}
