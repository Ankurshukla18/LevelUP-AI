import { Sidebar } from '@/components/layout/sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-slate-50 flex-col md:flex-row w-full max-w-full overflow-x-hidden">
      <Sidebar />
      <main className="flex-1 min-w-0 w-full flex flex-col min-h-screen md:h-screen md:overflow-y-auto">
        <div className="p-3 sm:p-5 lg:p-8 max-w-7xl mx-auto w-full min-w-0 box-border">
          {children}
        </div>
      </main>
    </div>
  );
}
