import React, { useState, useEffect, useRef } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';

interface WarmupIndicatorProps {
  apiBaseUrl: string;
}

const BACKEND_READY_KEY = 'backend_ready';
const MAX_RETRIES = 20; // Maximum 20 retries (60 seconds)
const RETRY_INTERVAL = 3000; // 3 seconds between retries

export const WarmupIndicator: React.FC<WarmupIndicatorProps> = ({ apiBaseUrl }) => {
  const [status, setStatus] = useState<'checking' | 'warming' | 'ready' | 'error'>('checking');
  const [startTime, setStartTime] = useState<number>(0);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [shouldShow, setShouldShow] = useState<boolean>(true);
  const retryCountRef = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Check if backend was already verified as ready in this session
    const backendReady = sessionStorage.getItem(BACKEND_READY_KEY);
    
    if (backendReady === 'true') {
      // Backend is already ready, don't show indicator
      setShouldShow(false);
      setStatus('ready');
      return;
    }

    // Start checking backend status
    checkBackendStatus();

    // Setup timer for elapsed time
    intervalRef.current = setInterval(() => {
      if (startTime > 0) {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }
    }, 1000);

    return () => {
      // Cleanup
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const checkBackendStatus = async () => {
    // Don't check if we've exceeded max retries
    if (retryCountRef.current >= MAX_RETRIES) {
      console.error('Max retries reached. Backend may be down.');
      setStatus('error');
      return;
    }

    if (retryCountRef.current === 0) {
      setStatus('checking');
      setStartTime(Date.now());
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout per request

      const response = await fetch(`${apiBaseUrl}/health`, {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        // Backend is ready!
        setStatus('ready');
        sessionStorage.setItem(BACKEND_READY_KEY, 'true');
        
        // Hide the indicator after a brief delay
        setTimeout(() => {
          setShouldShow(false);
        }, 1000);
        
        return; // Stop checking
      } else {
        // Backend responded but not healthy
        throw new Error('Backend not ready');
      }
    } catch (error) {
      retryCountRef.current += 1;
      
      if (retryCountRef.current < MAX_RETRIES) {
        setStatus('warming');
        console.log(`Backend warming up... Attempt ${retryCountRef.current}/${MAX_RETRIES}`);
        
        // Schedule next retry
        timeoutRef.current = setTimeout(checkBackendStatus, RETRY_INTERVAL);
      } else {
        setStatus('error');
      }
    }
  };

  // Don't render if we shouldn't show or if ready
  if (!shouldShow || status === 'ready') {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 max-w-sm animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="bg-white rounded-lg shadow-xl border-2 border-blue-200 p-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {(status === 'checking' || status === 'warming') ? (
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-600" />
            )}
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-gray-900">
              {status === 'checking' && 'Checking Backend...'}
              {status === 'warming' && 'Warming Up Backend'}
              {status === 'error' && 'Connection Error'}
            </h4>
            <p className="text-xs text-gray-600 mt-1">
              {status === 'warming' && (
                <>
                  The free tier server is waking up. This usually takes 30-60 seconds.
                  {elapsedTime > 0 && ` (${elapsedTime}s)`}
                </>
              )}
              {status === 'checking' && 'Please wait...'}
              {status === 'error' && 'Unable to connect to backend. Please try again later.'}
            </p>
            {status === 'warming' && (
              <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min((retryCountRef.current / MAX_RETRIES) * 100, 95)}%`,
                  }}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
