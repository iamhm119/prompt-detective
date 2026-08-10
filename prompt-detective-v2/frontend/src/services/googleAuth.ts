/**
 * Google OAuth 2.0 Service
 * Handles Google Sign-In integration
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
const GOOGLE_REDIRECT_URI =
  (import.meta.env.VITE_GOOGLE_REDIRECT_URI && import.meta.env.VITE_GOOGLE_REDIRECT_URI.trim()) ||
  '';

export interface GoogleAuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    full_name: string;
    username?: string;
    is_active: boolean;
    is_premium: boolean;
    api_calls_limit: number;
    api_calls_used: number;
    subscription_tier: string;
    created_at: string;
  };
}

export const googleAuthService = {
  /**
   * Get Google Client ID from environment
   */
  getClientId: (): string => {
    if (!GOOGLE_CLIENT_ID) {
      throw new Error('Google Client ID not configured');
    }
    return GOOGLE_CLIENT_ID;
  },

  /**
   * Exchange Google authorization code for app tokens
   * 
   * @param code - Authorization code from Google OAuth
   * @param redirectUri - The redirect URI used in OAuth flow
   * @returns Authentication response with tokens and user data
   */
  exchangeCodeForTokens: async (
    code: string,
    redirectUri: string
  ): Promise<GoogleAuthResponse> => {
    try {
      const response = await axios.post<GoogleAuthResponse>(
        `${API_BASE_URL}/auth/google/oauth`,
        {
          code,
          redirect_uri: redirectUri
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Google OAuth error:', error.response?.data || error.message);
      throw new Error(
        error.response?.data?.detail || 'Google authentication failed'
      );
    }
  },

  /**
   * Get current redirect URI based on environment
   */
  getRedirectUri: (): string => {
    if (GOOGLE_REDIRECT_URI) {
      return GOOGLE_REDIRECT_URI;
    }

    // In development and production fall back to current origin
    return window.location.origin;
  }
};

export default googleAuthService;
