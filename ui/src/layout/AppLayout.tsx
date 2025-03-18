// src/layout/AppLayout.tsx
import { ReactNode } from 'react';
import AppSidebar from './AppSidebar';
import AppHeader from './AppHeader';

interface LayoutProps {
  children: ReactNode;
}

export default function AppLayout({ children }: LayoutProps) {
  return (
    <div className="flex flex-col h-screen bg-gray-950">
      <AppHeader />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
