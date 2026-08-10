import React from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import clsx from 'clsx';
import { Button } from '../ui/Button';
import { useAuthStore } from '../../stores/authStore';
import { Menu, Moon, Sparkles, Sun, UserCircle2, LogOut } from 'lucide-react';
import { useTheme } from '../ThemeProvider';
import { useUiStore } from '../../stores/uiStore';

export interface NavItem {
  label: string;
  href: string;
  protected?: boolean;
  adminOnly?: boolean;
}

export const defaultNavItems: NavItem[] = [
  { label: 'Home', href: '/' },
  { label: 'Pricing', href: '/pricing' },
  { label: 'Dashboard', href: '/dashboard', protected: true },
  { label: 'History', href: '/history', protected: true },
  { label: 'Contact', href: '/contact' },
];

interface TopNavProps {
  onToggleSidebar?: () => void;
  navItems?: NavItem[];
}

const TopNav: React.FC<TopNavProps> = ({ onToggleSidebar, navItems = defaultNavItems }) => {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuthStore();
  const { theme, toggleTheme } = useTheme();
  const { openTutorial } = useUiStore();

  const isAdmin = Boolean(user?.is_admin || user?.is_super_admin || user?.subscription_tier === 'admin');

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <header className="fixed left-0 right-0 top-0 z-50 border-b border-gray-200/50 bg-white/80 backdrop-blur-md dark:border-slate-800/50 dark:bg-slate-950/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Left: Logo & Mobile Menu */}
        <div className="flex items-center gap-4">
          <button
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 transition hover:bg-gray-100 md:hidden dark:text-white/80 dark:hover:bg-slate-800"
            onClick={onToggleSidebar}
            aria-label="Toggle navigation"
          >
            <Menu className="h-5 w-5" />
          </button>
          
          <Link to="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/25">
              <span className="text-lg font-bold text-white">PD</span>
            </div>
            <div className="hidden sm:block">
              <span className="block text-base font-semibold text-gray-900 dark:text-white">Prompt Detective</span>
            </div>
          </Link>
        </div>

        {/* Center: Navigation Links */}
        <nav className="hidden items-center gap-1 md:flex">
          {navItems.map((item) => {
            if (item.protected && !isAuthenticated) return null;
            if (item.adminOnly && !isAdmin) return null;
            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={({ isActive }) =>
                  clsx(
                    'relative px-4 py-2 text-sm font-medium transition-colors duration-200',
                    isActive || location.pathname === item.href
                      ? 'text-blue-600 dark:text-blue-400'
                      : 'text-gray-600 hover:text-gray-900 dark:text-white/75 dark:hover:text-white'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {item.label}
                    {(isActive || location.pathname === item.href) && (
                      <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="hidden h-9 w-9 items-center justify-center rounded-lg text-gray-600 transition hover:bg-gray-100 md:flex dark:text-white/80 dark:hover:bg-slate-800"
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>

          <button
            onClick={() => openTutorial('navbar')}
            className="hidden items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 md:flex dark:text-white/80 dark:hover:bg-slate-800"
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Tour</span>
          </button>

          {isAuthenticated ? (
            <>
              <Link
                to="/profile"
                className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:text-white/80 dark:hover:bg-slate-800"
              >
                <UserCircle2 className="h-4 w-4" />
                <span className="hidden lg:inline">{user?.full_name ?? user?.email}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex h-9 w-9 items-center justify-center rounded-lg text-gray-600 transition hover:bg-gray-100 dark:text-white/80 dark:hover:bg-slate-800"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" component={Link} to="/login" className="hidden sm:flex">
                Log in
              </Button>
              <Button size="sm" component={Link} to="/signup">
                Sign up
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

export default TopNav;
