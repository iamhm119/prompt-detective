import React, { useCallback, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import clsx from 'clsx';
import TopNav, { defaultNavItems, NavItem } from './navigation/TopNav';
import AppDock from './navigation/AppDock';
import { Button } from './ui/Button';
import { useAuthStore } from '../stores/authStore';
import { useTheme } from './ThemeProvider';
import { Moon, Sun } from 'lucide-react';
import TutorialModal from './TutorialModal';
import { useUiStore } from '../stores/uiStore';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isAuthenticated, user, logout } = useAuthStore();
  const { theme, toggleTheme } = useTheme();
  const { isTutorialOpen, closeTutorial } = useUiStore();
  const userId = user?.id;

  const markTutorialSeen = useCallback(() => {
    if (userId) {
      localStorage.setItem(`hasSeenTutorial_${userId}`, 'true');
    }
  }, [userId]);

  const handleTutorialComplete = useCallback(() => {
    markTutorialSeen();
    closeTutorial();
  }, [closeTutorial, markTutorialSeen]);

  const handleTutorialClose = useCallback(() => {
    markTutorialSeen();
    closeTutorial();
  }, [closeTutorial, markTutorialSeen]);

  const isAdmin = useMemo(
    () => Boolean(user?.is_admin || user?.is_super_admin || user?.subscription_tier === 'admin'),
    [user]
  );

  const navItems = useMemo<NavItem[]>(() => {
    if (!isAuthenticated) {
      return defaultNavItems.filter((item) => !item.protected);
    }
    const items = [...defaultNavItems];
    if (!items.some((item) => item.href === '/admin') && isAdmin) {
      items.push({ label: 'Admin', href: '/admin', protected: true, adminOnly: true });
    }
    return items;
  }, [isAuthenticated, isAdmin]);

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 text-gray-900 transition-colors duration-500 dark:from-slate-950 dark:via-slate-950 dark:to-slate-900 dark:text-white/90">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_55%)] dark:bg-[radial-gradient(circle_at_top,_rgba(79,70,229,0.12),_transparent_55%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.12),_transparent_60%)] dark:bg-[radial-gradient(circle_at_bottom_right,_rgba(30,64,175,0.2),_transparent_60%)]" />
      </div>

      {/* Announcement bar */}
      <div className="sticky top-0 z-50 hidden bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-500 py-2 text-sm font-medium text-white shadow-[0_18px_35px_-20px_rgba(79,70,229,0.55)] md:block dark:from-indigo-500 dark:via-blue-600 dark:to-sky-500">
        <div className="mx-auto flex max-w-7xl items-center justify-center gap-4 px-4">
          <span className="rounded-full bg-white/20 px-3 py-1 text-xs uppercase tracking-wide">New</span>
          <span>Experience the redesigned Prompt Detective dashboard with adaptive insights.</span>
          <Link to="/dashboard" className="underline-offset-4 transition hover:underline">
            Explore updates
          </Link>
        </div>
      </div>

      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-28 pt-6 sm:px-6 lg:px-8">
        <TopNav onToggleSidebar={() => setMobileOpen((prev) => !prev)} navItems={navItems} />

        <main className="flex-1 pb-16">
          <div className="relative">
            <span className="pointer-events-none absolute inset-0 -z-10 rounded-[40px] bg-gradient-to-br from-white/60 via-white/40 to-white/20 blur-3xl dark:from-slate-900/70 dark:via-slate-900/40 dark:to-slate-900/20" />
            <div className="relative">{children}</div>
          </div>
        </main>

        <footer className="mt-auto rounded-[32px] border border-white/60 bg-white/85 p-10 shadow-[0_25px_80px_-40px_rgba(79,70,229,0.45)] backdrop-blur-2xl dark:border-white/5 dark:bg-slate-900/80 dark:shadow-[0_25px_80px_-40px_rgba(15,23,42,0.7)]">
          <div className="grid gap-10 md:grid-cols-[1.5fr,1fr,1fr,1fr]">
            <div>
              <div className="flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 text-xl font-bold text-white shadow-lg shadow-indigo-200">
                  PD
                </span>
                <div>
                  <p className="text-lg font-semibold">Prompt Detective</p>
                  <p className="text-sm text-gray-500 dark:text-white/75">Reverse engineer AI media with confidence.</p>
                </div>
              </div>
              <p className="mt-4 max-w-sm text-sm text-gray-500 dark:text-white/75">
                Designed for creators, product teams, and researchers who need trustworthy insights into
                AI-generated imagery and motion graphics.
              </p>
              <div className="mt-6 flex flex-wrap items-center gap-3 text-sm text-gray-400 dark:text-white/65">
                <span>© {new Date().getFullYear()} Prompt Detective</span>
                <span className="h-1 w-1 rounded-full bg-gray-300 dark:bg-slate-600" />
                <Link to="/privacy" className="text-gray-500 transition hover:text-gray-900 dark:text-white/75 dark:hover:text-white">
                  Privacy
                </Link>
                <Link to="/terms" className="text-gray-500 transition hover:text-gray-900 dark:text-white/75 dark:hover:text-white">
                  Terms
                </Link>
                <a href="/api/docs" className="text-gray-500 transition hover:text-gray-900 dark:text-white/75 dark:hover:text-white">
                  API Docs
                </a>
              </div>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-white/75">Product</p>
              <ul className="mt-4 space-y-2 text-sm text-gray-600 dark:text-white/75">
                <li><Link to="/pricing" className="transition hover:text-gray-900 dark:hover:text-white">Pricing & Plans</Link></li>
                <li><Link to="/coming-soon" className="transition hover:text-gray-900 dark:hover:text-white">Roadmap</Link></li>
                <li><Link to="/dashboard" className="transition hover:text-gray-900 dark:hover:text-white">Dashboard</Link></li>
                <li><Link to="/history" className="transition hover:text-gray-900 dark:hover:text-white">Usage History</Link></li>
              </ul>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-white/75">Company</p>
              <ul className="mt-4 space-y-2 text-sm text-gray-600 dark:text-white/75">
                <li><Link to="/contact" className="transition hover:text-gray-900 dark:hover:text-white">Support</Link></li>
                <li><Link to="/privacy" className="transition hover:text-gray-900 dark:hover:text-white">Security</Link></li>
                <li><Link to="/terms" className="transition hover:text-gray-900 dark:hover:text-white">Legal</Link></li>
                <li><Link to="/coming-soon" className="transition hover:text-gray-900 dark:hover:text-white">Careers</Link></li>
              </ul>
            </div>

            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-gray-500 dark:text-white/75">Stay in sync</p>
              <p className="mt-3 text-sm text-gray-500 dark:text-white/75">
                Join the release channel to get quick design breakdowns and prompt engineering tips.
              </p>
              <Button
                variant="secondary"
                size="sm"
                className="mt-4 w-full"
                onClick={() => {
                  window.open('mailto:hello@promptdetective.ai');
                }}
              >
                Contact team
              </Button>
            </div>
          </div>
        </footer>
      </div>

      <AppDock />
      <TutorialModal
        isOpen={isTutorialOpen}
        onClose={handleTutorialClose}
        onComplete={handleTutorialComplete}
      />

      {/* Mobile navigation drawer */}
      <div
        className={clsx(
          'fixed inset-0 z-50 transform bg-black/40 backdrop-blur-sm transition-opacity duration-300 md:hidden',
          mobileOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
        )}
        onClick={() => setMobileOpen(false)}
      >
        <div
          className={clsx(
            'absolute left-0 top-0 h-full w-[80%] max-w-xs transform bg-white/95 p-6 shadow-2xl transition-transform duration-300 dark:bg-slate-900/95',
            mobileOpen ? 'translate-x-0' : '-translate-x-full'
          )}
          onClick={(event) => event.stopPropagation()}
        >
          <div className="mb-6 flex items-center justify-between">
            <Link to="/" className="text-lg font-semibold text-gray-900 dark:text-white">
              Prompt Detective
            </Link>
            <button
              type="button"
              className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-600 dark:bg-slate-800 dark:text-white/80"
              onClick={() => setMobileOpen(false)}
            >
              Close
            </button>
          </div>
          <nav className="space-y-3">
            {navItems.map((item) => {
              if (item.protected && !isAuthenticated) return null;
              if (item.adminOnly && !isAdmin) return null;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  className="block rounded-2xl bg-gray-100 px-4 py-3 text-sm font-semibold text-gray-700 transition hover:bg-blue-50 hover:text-blue-600 dark:bg-slate-800/80 dark:text-white/85 dark:hover:bg-slate-800 dark:hover:text-white"
                  onClick={() => setMobileOpen(false)}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="mt-8 space-y-3">
            <Button
              variant="ghost"
              fullWidth
              onClick={() => {
                toggleTheme();
              }}
              className="justify-between rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 dark:border-slate-700 dark:bg-slate-800/80 dark:text-white/85"
              trailingIcon={theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            >
              {theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            </Button>
            {isAuthenticated ? (
              <>
                <div className="rounded-2xl bg-blue-50 p-4 text-sm text-blue-700">
                  <p className="font-semibold">Signed in as</p>
                  <p>{user?.full_name ?? user?.email}</p>
                </div>
                <Button variant="outline" fullWidth onClick={handleLogout}>
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" fullWidth component={Link} to="/login" onClick={() => setMobileOpen(false)}>
                  Log in
                </Button>
                <Button fullWidth component={Link} to="/signup" onClick={() => setMobileOpen(false)}>
                  Create account
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Layout;