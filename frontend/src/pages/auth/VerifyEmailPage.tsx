import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Alert, Button, Spinner } from '../../components/ui';
import api from '../../lib/api';

function getTokenFromSearch(search: string) {
  return new URLSearchParams(search).get('token') || '';
}

export default function VerifyEmailPage() {
  const location = useLocation();
  const [token] = useState(() => getTokenFromSearch(location.search));
  const [message, setMessage] = useState<string>('Verifying your email...');
  const [error, setError] = useState<string | null>(null);

  const verifyMutation = useMutation({
    mutationFn: async () => {
      if (!token) {
        throw new Error('Verification token is missing.');
      }
      const response = await api.post('/auth/verify-email', { token });
      return response.data;
    },
    onSuccess: () => {
      setMessage('Your email has been verified. You can now sign in.');
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message;
      setError(msg ?? 'Unable to verify your email. The link may have expired.');
    },
  });

  useEffect(() => {
    if (!verifyMutation.isIdle) return;
    verifyMutation.mutate();
  }, [verifyMutation]);

  return (
    <div className="min-h-screen bg-obsidian-950 flex items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-3xl border border-white/10 bg-obsidian-900/95 p-10 shadow-2xl shadow-black/20">
        <div className="text-center">
          <h1 className="text-3xl font-display font-bold text-white mb-3">Email verification</h1>
          <p className="text-obsidian-400 mb-8">Please wait while we verify your account.</p>

          {verifyMutation.isPending && (
            <div className="flex flex-col items-center gap-4">
              <Spinner size="lg" className="text-emerald-500" />
              <p className="text-obsidian-400">Verifying...</p>
            </div>
          )}

          {error && (
            <Alert variant="error" className="mb-6">
              {error}
            </Alert>
          )}

          {!verifyMutation.isPending && !error && (
            <div className="space-y-5">
              <p className="text-emerald-300">{message}</p>
              <div className="flex justify-center pt-4">
                <Link to="/auth/login">
                  <Button variant="primary" size="lg">
                    Go to Login
                  </Button>
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
