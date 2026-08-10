import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { api } from '../services/api';

interface UsageData {
  daily_usage: number;
  daily_limit: number;
  usage_percentage: number;
  can_upload: boolean;
  remaining_uploads: number;
  rolling_window_hours: number;
  window_start: string;
  current_time: string;
  user_tier: string;
  is_premium: boolean;
  usage_history?: Array<{
    timestamp: string;
    job_id: string;
    content_type: string;
  }>;
}

interface UsageHook {
  usageData: UsageData | null;
  isLoading: boolean;
  canUpload: boolean;
  refreshUsage: () => Promise<void>;
  getRemainingUploads: () => number;
  getUsagePercentage: () => number;
  getTimeUntilReset: () => string;
}

export const useUsageTracking = (): UsageHook => {
  const { accessToken } = useAuthStore();
  const [usageData, setUsageData] = useState<UsageData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUsageData = async () => {
    if (!accessToken) {
      setUsageData(null);
      setIsLoading(false);
      return;
    }

    try {
      const response = await api.get('/usage/daily');
      setUsageData(response.data);
    } catch (error) {
      console.error('Error fetching usage data:', error);
      setUsageData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUsage = async () => {
    setIsLoading(true);
    await fetchUsageData();
  };

  const canUpload = (): boolean => {
    if (!usageData) return false;
    return usageData.can_upload;
  };

  const getRemainingUploads = (): number => {
    if (!usageData) return 0;
    return usageData.remaining_uploads;
  };

  const getUsagePercentage = (): number => {
    if (!usageData) return 0;
    return usageData.usage_percentage;
  };

  const getTimeUntilReset = (): string => {
    if (!usageData || !usageData.usage_history?.length) return 'N/A';

    // Find the oldest upload in the rolling window
    const now = new Date();
    const windowHours = usageData.rolling_window_hours || 24;
    const windowStart = new Date(now.getTime() - windowHours * 60 * 60 * 1000);
    
    const recentUploads = usageData.usage_history.filter(upload => 
      new Date(upload.timestamp) >= windowStart
    );

    if (recentUploads.length === 0) return 'N/A';

    // Find the oldest upload that will expire first
    const oldestUpload = recentUploads.reduce((oldest, current) => 
      new Date(current.timestamp) < new Date(oldest.timestamp) ? current : oldest
    );

    const resetTime = new Date(new Date(oldestUpload.timestamp).getTime() + windowHours * 60 * 60 * 1000);
    const timeUntilReset = resetTime.getTime() - now.getTime();

    if (timeUntilReset <= 0) return 'Resetting...';

    const hours = Math.floor(timeUntilReset / (1000 * 60 * 60));
    const minutes = Math.floor((timeUntilReset % (1000 * 60 * 60)) / (1000 * 60));

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  useEffect(() => {
    fetchUsageData();
    
    // Refresh usage data every 5 minutes
    const interval = setInterval(fetchUsageData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [accessToken]);

  return {
    usageData,
    isLoading,
    canUpload: canUpload(),
    refreshUsage,
    getRemainingUploads,
    getUsagePercentage,
    getTimeUntilReset,
  };
};