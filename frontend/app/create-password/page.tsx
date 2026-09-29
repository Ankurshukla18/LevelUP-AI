'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth-context';
import { authService } from '@/services/auth';

export default function CreatePasswordPage() {
  const router = useRouter();
  const { user, loading, refreshUser, logout } = useAuth();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // If already authenticated and already has password, navigate to dashboard
  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
      } else if (user.has_password) {
        router.push('/dashboard');
      }
    }
  }, [user, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please verify both fields.');
      return;
    }

    setSubmitting(true);
    try {
      await authService.createFirstPassword({
        password,
        confirm_password: confirmPassword,
      });

      // Update the user state so has_password is true
      await refreshUser();

      // Proceed to the dashboard
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Password creation error:', err);
      setError(
        err.message || 'Failed to set password. Please try again or refresh the page.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800/80 backdrop-blur-md rounded-2xl border border-slate-700/60 p-8 shadow-2xl">
        
        {/* HEADER */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 mb-3 border border-cyan-500/20">
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Create Your Password</h1>
          <p className="text-slate-400 text-xs mt-1">
            LifeTrack AI requires a password for all accounts so you can sign in anytime using either Google or your email.
          </p>
        </div>

        {/* LOGGED IN ACCOUNT BADGE */}
        <div className="bg-slate-900/60 border border-slate-700/50 rounded-xl p-3 mb-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white font-semibold text-xs">
              {user.name ? user.name[0].toUpperCase() : 'U'}
            </div>
            <div className="text-left">
              <p className="text-xs font-semibold text-white leading-tight">{user.name}</p>
              <p className="text-xs text-slate-400 leading-tight">{user.email}</p>
            </div>
          </div>
          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            Google Account
          </span>
        </div>

        {/* ERROR NOTIFICATION */}
        {error && (
          <div className="mb-5 bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-xs text-red-400 flex items-start gap-2">
            <svg className="w-4 h-4 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {/* FORM */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 transition pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">
              Confirm Password
            </label>
            <input
              type={showPassword ? 'text' : 'password'}
              required
              minLength={6}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter your password"
              className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500 transition"
            />
          </div>

          {/* PASSWORD HINTS */}
          <div className="bg-slate-900/40 rounded-lg p-3 space-y-1 text-xs text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className={password.length >= 6 ? 'text-emerald-400' : 'text-slate-500'}>
                ✓
              </span>
              <span>Minimum 6 characters</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={
                  confirmPassword && password === confirmPassword
                    ? 'text-emerald-400'
                    : 'text-slate-500'
                }
              >
                ✓
              </span>
              <span>Passwords match</span>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-sm transition shadow-lg shadow-cyan-500/25 disabled:opacity-50 mt-2"
          >
            {submitting ? 'Setting Password...' : 'Save Password & Enter Dashboard'}
          </button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-700/60 text-center">
          <button
            type="button"
            onClick={logout}
            className="text-xs text-slate-400 hover:text-red-400 transition"
          >
            Log out and switch account
          </button>
        </div>

      </div>
    </div>
  );
}
