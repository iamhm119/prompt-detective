import { useAuthStore } from '../stores/authStore';
import { api } from '../services/api';

interface LoginData {
  email: string;
  password: string;
}

interface SignupData {
  email: string;
  password: string;
  full_name: string;
  username?: string;
}

interface UpdateProfileData {
  full_name?: string;
  username?: string;
  email?: string;
}

interface DeleteAccountResult {
  success: boolean;
}

export const useAuth = () => {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    setUser,
    setTokens,
    setError,
    setLoading,
    logout: logoutStore
  } = useAuthStore();

  const login = async (data: LoginData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/login', data);
      const { access_token, refresh_token, user: userData } = response.data;
      
      setTokens(access_token, refresh_token);
      setUser(userData);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Login failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (data: SignupData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/auth/signup', data);
      const { access_token, refresh_token, user: userData } = response.data;
      
      setTokens(access_token, refresh_token);
      setUser(userData);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Signup failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const updateProfile = async (data: UpdateProfileData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.put('/auth/profile', data);
      setUser(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Profile update failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const deleteAccount = async (): Promise<DeleteAccountResult> => {
    setError(null);

    try {
      await api.delete('/account/me');
      logoutStore();
      return { success: true };
    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Failed to delete account';
      setError(detail);
      throw new Error(detail);
    }
  };

  const logout = () => {
    logoutStore();
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    signup,
    updateProfile,
    deleteAccount,
    logout
  };
};