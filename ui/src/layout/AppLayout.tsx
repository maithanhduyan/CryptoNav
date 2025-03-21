// src/layout/AppLayout.tsx
import AppHeader from './AppHeader';
import AppSidebar from './AppSidebar';

// interface LayoutProps {
//   children: ReactNode;
// }

// export default function AppLayout({ children }: LayoutProps) {
//   return (
//     <div className="flex flex-col h-screen bg-gray-950">
//       <AppHeader />
//       <div className="flex flex-1 overflow-hidden">
//         <AppSidebar />
//         <main className="flex-1 overflow-auto p-6">{children}</main>
//       </div>
//     </div>
//   );
// }

import React from "react";

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="flex min-h-screen">
      <AppSidebar />

      {/* Phần còn lại bên phải: Header + Nội dung */}
      <div className="flex flex-col flex-1">
        <AppHeader />
        <main className="flex-1 bg-gray-50 p-4">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
