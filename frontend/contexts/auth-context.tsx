'use client';
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User } from '@/types';
import { authService } from '@/services/auth';
import { useRouter, usePathname } from 'next/navigation';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (token: string, userData?: User, requiresPasswordSetup?: boolean) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<User | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const refreshUser = useCallback(async (): Promise<User | null> => {
    try {
      const userData = await authService.me();
      setUser(userData);
      return userData;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      return null;
    }
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
      if (token) {
        try {
          const userData = await authService.me();
          setUser(userData);
        } catch (error) {
          localStorage.removeItem('token');
          setUser(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  useEffect(() => {
    if (loading) return;

    const isPublicAuthRoute =
      pathname === '/login' ||
      pathname === '/register' ||
      pathname.startsWith('/auth/callback');

    // If not logged in and trying to access protected routes
    if (!user) {
      if (
        pathname.startsWith('/dashboard') ||
        pathname.startsWith('/goals') ||
        pathname.startsWith('/monthly-review') ||
        pathname.startsWith('/analytics') ||
        pathname === '/create-password'
      ) {
        router.push('/login');
      }
      return;
    }

    // If user is authenticated but has NO password configured
    if (user.has_password === false) {
      if (pathname !== '/create-password' && !isPublicAuthRoute) {
        router.push('/create-password');
      }
      return;
    }

    // If user already HAS a password and is on create-password, send them to dashboard
    if (user.has_password === true && pathname === '/create-password') {
      router.push('/dashboard');
    }
  }, [user, loading, pathname, router]);

  const login = async (token: string, userData?: User, requiresPasswordSetup?: boolean) => {
    localStorage.setItem('token', token);
    let resolvedUser = userData;

    if (!resolvedUser || resolvedUser.has_password === undefined) {
      try {
        const freshUser = await authService.me();
        resolvedUser = freshUser;
      } catch (e) {
        console.error('Failed to load user profile on login:', e);
      }
    }

    if (resolvedUser) {
      setUser(resolvedUser);
    }

    // If explicitly marked as requiring password setup, or user record has no password
    const mustSetupPassword =
      requiresPasswordSetup === true || (resolvedUser && resolvedUser.has_password === false);

    if (mustSetupPassword) {
      router.push('/create-password');
    } else {
      router.push('/dashboard');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
