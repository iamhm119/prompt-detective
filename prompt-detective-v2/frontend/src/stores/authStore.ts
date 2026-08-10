import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
  username?: string;
  is_active: boolean;
  is_premium: boolean;
  is_email_verified?: boolean;
  is_admin?: boolean;
  is_super_admin?: boolean;
  is_on_trial?: boolean;
  trial_started_at?: string | null;
  trial_ends_at?: string | null;
  has_used_trial?: boolean;
  api_calls_limit: number;
  api_calls_used: number;
  subscription_tier: 'free' | 'basic' | 'starter' | 'pro' | 'business' | 'enterprise' | 'admin';
  created_at: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
  updateUserProfile: (updates: Partial<User>) => void;
  initialize: () => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user: User) => {
        console.log('Setting user:', user);
        set({
          user,
          isAuthenticated: true,
          error: null
        });
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        console.log('Setting tokens');
        set({
          accessToken,
          refreshToken,
          isAuthenticated: true,
          error: null
        });
      },

      setError: (error: string | null) => set({ error, isLoading: false }),

      setLoading: (isLoading: boolean) => set({ isLoading, error: null }),

      logout: () => {
        console.log('Logging out');
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        });
      },

      updateUserProfile: (updates: Partial<User>) => {
        const currentUser = get().user;
        if (currentUser) {
          set({
            user: { ...currentUser, ...updates }
          });
        }
      },

      initialize: () => {
        const state = get();
        const hasTokens = !!(state.accessToken && state.refreshToken);
        const hasUser = !!state.user;
        
        console.log('Initializing auth store:', { hasTokens, hasUser });
        
        if (hasTokens && hasUser) {
          set({ isAuthenticated: true });
        } else {
          set({ isAuthenticated: false });
        }
      }
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

// Export the User type for use in other components
export type { User };