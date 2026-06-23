import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { BookOpen, Lock, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { Button, Input, Alert } from '../../components/ui';
import api from '../../lib/api';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';

  const [form, setForm] = useState({ new_password: '', confirm_password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [serverError, setServerError] = useState('');

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const validate = (): boolean => {
    const errs: Record<string, string> = {};
    if (form.new_password.length < 8) errs.new_password = 'Password must be at least 8 characters.';
    if (form.new_password !== form.confirm_password) errs.confirm_password = 'Passwords do not match.';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const mutation = useMutation({
    mutationFn: () => api.post('/auth/reset-password', { token, ...form }),
    onSuccess: () => navigate('/auth/login', { state: { message: 'Password reset successfully. You can now log in.' } }),
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message;
      setServerError(msg ?? 'Failed to reset password. The link may have expired.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setServerError('');
    if (!token) { setServerError('Invalid or missing reset token.'); return; }
    if (validate()) mutation.mutate();
  };

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

        <h1 className="text-3xl font-display font-bold text-white mb-2">Set new password</h1>
        <p className="text-obsidian-400 mb-8">
          Choose a strong password for your SomaHub account.
        </p>

        {serverError && (
          <Alert variant="error" className="mb-6" onDismiss={() => setServerError('')}>
            {serverError}
          </Alert>
        )}

        {!token && (
          <Alert variant="error" className="mb-6">
            Invalid reset link. Please{' '}
            <Link to="/auth/forgot-password" className="underline">request a new one</Link>.
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <Input
            id="new_password"
            label="New password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Min. 8 characters"
            value={form.new_password}
            onChange={update('new_password')}
            leftAddon={<Lock size={16} />}
            rightAddon={
              <button type="button" onClick={() => setShowPassword((s) => !s)} aria-label="Toggle password">
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
            error={errors.new_password}
            required
          />
          <Input
            id="confirm_password"
            label="Confirm new password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Repeat password"
            value={form.confirm_password}
            onChange={update('confirm_password')}
            leftAddon={<Lock size={16} />}
            error={errors.confirm_password}
            required
          />
          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            loading={mutation.isPending}
            disabled={!token}
            rightIcon={<ArrowRight size={18} />}
          >
            Reset Password
          </Button>
        </form>
      </div>
    </div>
  );
}
