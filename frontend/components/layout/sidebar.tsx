'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Target, Calendar, BarChart, Settings, LogOut, Activity } from 'lucide-react';
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

  return (
    <div className="w-64 border-r bg-slate-900 text-slate-100 flex flex-col min-h-screen">
      <div className="p-6">
        <Link href="/dashboard" className="flex items-center gap-2 font-bold text-xl text-white">
          <Activity className="h-6 w-6 text-indigo-500" />
          LifeTrack AI
        </Link>
      </div>
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {routes.map((route) => {
          const isActive = pathname.startsWith(route.href);
          const Icon = route.icon;
          return (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                isActive ? "bg-indigo-600 text-white" : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <Icon className="h-5 w-5" />
              {route.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 mt-auto">
        <Button variant="ghost" className="w-full justify-start text-slate-300 hover:text-white hover:bg-slate-800" onClick={logout}>
          <LogOut className="h-5 w-5 mr-3" />
          Logout
        </Button>
      </div>
    </div>
  );
}

export default Sidebar;
