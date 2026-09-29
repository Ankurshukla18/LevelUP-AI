'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { authService } from '@/services/auth';
import { useAuth } from '@/contexts/auth-context';
import { getGoogleRedirectUri } from '@/lib/constants';
import Link from 'next/link';

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'mock_prompt'>('loading');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Mock form state if launched in simulation mode
  const [mockEmail, setMockEmail] = useState('newstudent@university.edu');
  const [mockName, setMockName] = useState('New Student');
  const [isSubmittingMock, setIsSubmittingMock] = useState(false);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');
    const isMock = searchParams.get('mock') === 'true';

    if (error) {
      setStatus('error');
      setErrorMessage(
        searchParams.get('error_description') ||
          'Google authentication was cancelled or encountered an error. Please try again.'
      );
      return;
    }

    if (isMock) {
      setStatus('mock_prompt');
      return;
    }

    if (code) {
      handleExchange({ code, state: state || undefined });
    } else {
      setStatus('error');
      setErrorMessage('Missing OAuth authorization code from Google.');
    }
  }, [searchParams]);

  const handleExchange = async (payload: {
    code?: string;
    state?: string;
    mock_email?: string;
    mock_name?: string;
    mock_oauth_id?: string;
    mock_avatar?: string;
  }) => {
    try {
      setStatus('loading');
      const response = await authService.handleGoogleCallback({
        ...payload,
        redirect_uri: getGoogleRedirectUri(),
      });

      setStatus('success');
      // Pass token, user data, and whether password setup is required
      await login(response.access_token, response.user, response.requires_password_setup);
    } catch (err: any) {
      console.error('Google callback error:', err);
      setStatus('error');
      setErrorMessage(
        err.message || 'Failed to authenticate with Google. Please check your credentials and try again.'
      );
    }
  };

  const submitMockLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmittingMock(true);
    await handleExchange({
      mock_email: mockEmail.trim().toLowerCase(),
      mock_name: mockName.trim(),
      mock_oauth_id: `google_${Date.now()}`,
      mock_avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(mockEmail)}`,
    });
    setIsSubmittingMock(false);
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800/80 backdrop-blur-md rounded-2xl border border-slate-700/60 p-8 shadow-2xl text-center">
        
        {/* LOGO */}
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 mb-6 shadow-lg shadow-cyan-500/20">
          <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14.5v-9l6 4.5-6 4.5z" />
          </svg>
        </div>

        {/* LOADING STATE */}
        {status === 'loading' && (
          <div>
            <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Connecting to Google...</h2>
            <p className="text-slate-400 text-sm">
              Securing authentication and syncing your LevelUp AI profile.
            </p>
          </div>
        )}

        {/* SUCCESS STATE */}
        {status === 'success' && (
          <div>
            <div className="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-500/40">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Authentication Successful!</h2>
            <p className="text-slate-400 text-sm">
              Setting up your session and redirecting you safely...
            </p>
          </div>
        )}

        {/* ERROR STATE */}
        {status === 'error' && (
          <div>
            <div className="w-12 h-12 bg-red-500/20 text-red-400 rounded-full flex items-center justify-center mx-auto mb-4 border border-red-500/40">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Authentication Failed</h2>
            <p className="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-6">
              {errorMessage}
            </p>
            <div className="space-y-3">
              <Link
                href="/login"
                className="w-full inline-block py-2.5 px-4 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium transition duration-200"
              >
                Back to Sign In
              </Link>
              <Link
                href="/register"
                className="w-full inline-block py-2.5 px-4 rounded-xl bg-slate-700/50 hover:bg-slate-700 text-slate-300 font-medium transition duration-200"
              >
                Create Account with Email
              </Link>
            </div>
          </div>
        )}

        {/* MOCK / SIMULATION STATE */}
        {status === 'mock_prompt' && (
          <div className="text-left">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold mb-4">
              <span>Google OAuth Simulation Mode</span>
            </div>
            <h2 className="text-xl font-bold text-white mb-1">Simulate Google Sign-In</h2>
            <p className="text-slate-400 text-xs mb-5">
              Live Google Client ID is not configured in backend `.env`. Test the full OAuth flow, automatic account creation, and mandatory password setup below.
            </p>

            <form onSubmit={submitMockLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={mockName}
                  onChange={(e) => setMockName(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                  placeholder="e.g. Alex Demo or Sarah Student"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Google Email Address
                </label>
                <input
                  type="email"
                  required
                  value={mockEmail}
                  onChange={(e) => setMockEmail(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                  placeholder="e.g. user@university.edu"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setMockName('New Student');
                    setMockEmail(`student_${Date.now().toString().slice(-4)}@gmail.com`);
                  }}
                  className="text-xs bg-slate-700/60 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-md flex-1 text-center"
                >
                  ⚡ Preset: New Google User
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMockName('Alex Demo');
                    setMockEmail('alex@demo.com');
                  }}
                  className="text-xs bg-slate-700/60 hover:bg-slate-700 text-slate-300 px-2.5 py-1.5 rounded-md flex-1 text-center"
                >
                  ⚡ Preset: Existing User
                </button>
              </div>

              <button
                type="submit"
                disabled={isSubmittingMock}
                className="w-full mt-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm transition shadow-lg shadow-cyan-500/20 disabled:opacity-50"
              >
                {isSubmittingMock ? 'Processing...' : 'Continue as Google User'}
              </button>
            </form>
          </div>
        )}

      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <GoogleCallbackContent />
    </Suspense>
  );
}
