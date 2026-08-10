import React from 'react';
import ReactDOM from 'react-dom/client';
import { GoogleOAuthProvider } from '@react-oauth/google';
import App from './App.tsx';
import './index.css';
import { keepAliveService } from './services/keepAlive';
import { ThemeProvider } from './components/ThemeProvider';

// Get Google Client ID from environment
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

if (!GOOGLE_CLIENT_ID) {
  console.error('VITE_GOOGLE_CLIENT_ID is not set in environment variables');
}

// Start keep-alive service for backend on free tier
const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
if (import.meta.env.PROD) {
  // Only run keep-alive in production (when deployed)
  keepAliveService.start(apiBaseUrl);
  console.log('🔄 Keep-alive service started for:', apiBaseUrl);
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID || ''}>
      <ThemeProvider>
        <App />
      </ThemeProvider>
    </GoogleOAuthProvider>
  </React.StrictMode>,
);