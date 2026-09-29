import './globals.css';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/contexts/auth-context';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'LevelUp AI — Plan. Track. Analyze. Improve.',
  description:
    'AI-powered personal progress management platform for setting goals, generating roadmaps, tracking progress, and improving continuously.',
  openGraph: {
    title: 'LevelUp AI — Plan. Track. Analyze. Improve.',
    description:
      'AI-powered personal progress management platform for setting goals, generating roadmaps, tracking progress, and improving continuously.',
    siteName: 'LevelUp AI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LevelUp AI — Plan. Track. Analyze. Improve.',
    description:
      'AI-powered personal progress management platform for setting goals, generating roadmaps, tracking progress, and improving continuously.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
