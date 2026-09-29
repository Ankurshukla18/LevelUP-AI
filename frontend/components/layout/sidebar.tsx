'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Target, Calendar, BarChart, LogOut, Activity, Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';

const routes = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/goals', label: 'My Goals', icon: Target },
  { href: '/monthly-review', label: 'Monthly Review', icon: Calendar },
  { href: '/analytics', label: 'Analytics', icon: BarChart },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Prevent background scrolling when mobile drawer is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileOpen]);

  const navContent = (onItemClick?: () => void) => (
    <>
      <nav className="flex-1 px-4 space-y-1.5 mt-4 overflow-y-auto">
        {routes.map((route) => {
          const isActive = pathname === route.href || (route.href !== '/dashboard' && pathname.startsWith(route.href));
          const Icon = route.icon;
          return (
            <Link
              key={route.href}
              href={route.href}
              onClick={onItemClick}
              className={cn(
                "flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5 shrink-0" />
              <span>{route.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 mt-auto border-t border-slate-800">
        <Button
          variant="ghost"
          className="w-full justify-start text-slate-300 hover:text-white hover:bg-slate-800 text-sm font-medium px-3.5 py-2.5"
          onClick={() => {
            if (onItemClick) onItemClick();
            logout();
          }}
        >
          <LogOut className="h-5 w-5 mr-3 shrink-0" />
          <span>Logout</span>
        </Button>
      </div>
    </>
  );

  return (
    <>
      {/* 1. Mobile Top Header Bar (<= 768px / md:hidden) */}
      <div className="md:hidden flex items-center justify-between px-4 h-16 bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-40 w-full shrink-0">
        <Link href="/dashboard" className="flex items-center gap-2.5 font-bold text-lg text-white tracking-tight">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center">
            <Activity className="h-5 w-5 text-indigo-400" />
          </div>
          <span>LevelUp AI</span>
        </Link>
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          className="p-2 -mr-1 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="h-6 w-6" />
        </button>
      </div>

      {/* 2. Mobile Drawer Backdrop & Panel (<= 768px / md:hidden) */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          {/* Overlay backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity duration-300"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />

          {/* Slide-over drawer */}
          <div
            className="relative w-72 max-w-[85vw] bg-slate-900 text-slate-100 flex flex-col h-full shadow-2xl z-50 transform transition-transform duration-300 ease-in-out"
            role="dialog"
            aria-modal="true"
            aria-label="Sidebar Navigation"
          >
            <div className="p-5 flex items-center justify-between border-b border-slate-800">
              <Link
                href="/dashboard"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-2.5 font-bold text-xl text-white tracking-tight"
              >
                <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center">
                  <Activity className="h-5 w-5 text-indigo-400" />
                </div>
                <span>LevelUp AI</span>
              </Link>
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors"
                aria-label="Close sidebar menu"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {navContent(() => setMobileOpen(false))}
          </div>
        </div>
      )}

      {/* 3. Desktop / Tablet Permanent Sidebar (>= 768px / md:flex) */}
      <aside className="hidden md:flex md:w-56 lg:w-64 border-r border-slate-800 bg-slate-900 text-slate-100 flex-col min-h-screen shrink-0 sticky top-0 h-screen z-30">
        <div className="p-6 border-b border-slate-800/80">
          <Link href="/dashboard" className="flex items-center gap-2.5 font-bold text-xl text-white tracking-tight">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center">
              <Activity className="h-5 w-5 text-indigo-400" />
            </div>
            <span>LevelUp AI</span>
          </Link>
        </div>
        {navContent()}
      </aside>
    </>
  );
}

export default Sidebar;
