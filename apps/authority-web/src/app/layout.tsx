import type { Metadata } from 'next';
import '@/styles/globals.css';
import { AuthProvider } from '@/lib/auth';
import { AppShell } from '@/components/layout/AppShell';

export const metadata: Metadata = {
  title: 'SEPTERIA Authority Portal | SIH26186',
  description: 'AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-slate-900 text-slate-100 min-h-screen antialiased" suppressHydrationWarning>
        <AuthProvider>
          <AppShell>{children}</AppShell>
        </AuthProvider>
      </body>
    </html>
  );
}
