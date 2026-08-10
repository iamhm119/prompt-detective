import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Compass, UploadCloud, LayoutDashboard, History, MessageSquare } from 'lucide-react';
import clsx from 'clsx';

const dockItems = [
  { icon: <Home className="h-5 w-5" />, label: 'Home', href: '/' },
  { icon: <LayoutDashboard className="h-5 w-5" />, label: 'Dashboard', href: '/dashboard' },
  { icon: <UploadCloud className="h-5 w-5" />, label: 'Upload', href: '/dashboard#upload' },
  { icon: <History className="h-5 w-5" />, label: 'History', href: '/history' },
  { icon: <MessageSquare className="h-5 w-5" />, label: 'Support', href: '/contact' },
  { icon: <Compass className="h-5 w-5" />, label: 'Explore', href: '/pricing' },
];

const AppDock: React.FC = () => {
  const location = useLocation();
  const currentKey = `${location.pathname}${location.hash}`;

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-6 z-40 flex justify-center px-4 md:hidden">
      <nav className="pointer-events-auto flex w-full max-w-xl items-center justify-between rounded-2xl border border-white/30 bg-white/80 px-3 py-2 shadow-[0_25px_60px_-30px_rgba(79,70,229,0.45)] backdrop-blur-2xl">
        {dockItems.map((item) => {
          const isActive = currentKey === item.href || location.pathname === item.href;
          return (
            <Link
              key={item.href}
              to={item.href}
              className={clsx(
                'group flex flex-1 flex-col items-center gap-1 rounded-xl px-2 py-2 text-[11px] font-semibold transition-all duration-300',
                isActive ? 'text-blue-600' : 'text-gray-500 hover:text-gray-800'
              )}
            >
              <span
                className={clsx(
                  'flex h-10 w-10 items-center justify-center rounded-2xl transition-all duration-300',
                  isActive
                    ? 'bg-blue-100 text-blue-600 shadow-inner shadow-blue-200'
                    : 'bg-white/70 text-gray-600 shadow-sm shadow-gray-200 group-hover:bg-gray-100/80'
                )}
              >
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default AppDock;
