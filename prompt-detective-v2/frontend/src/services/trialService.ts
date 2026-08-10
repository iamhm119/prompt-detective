import { api } from './api';

export interface StartTrialResponse {
  success: boolean;
  message: string;
  subscription: {
    id: number;
    plan: string;
    status: string;
    started_at: string;
    expires_at: string | null;
    daily_limit: number;
    monthly_limit: number;
    api_calls_limit: number;
  };
  trial_info: {
    duration_days: number;
    auto_downgrade: boolean;
    downgrade_plan: string;
    message: string;
  };
}

export interface TrialStatusResponse {
  is_on_trial: boolean;
  has_used_trial: boolean;
  trial_plan?: string | null;
  trial_started?: string | null;
  trial_ends?: string | null;
  hours_remaining?: number | null;
  days_remaining?: number | null;
  is_expired: boolean;
  message?: string | null;
}

export const startTrial = async (plan: string) => {
  const response = await api.post<StartTrialResponse>('/trials/start', { plan });
  return response.data;
};

export const getTrialStatus = async () => {
  const response = await api.get<TrialStatusResponse>('/trials/status');
  return response.data;
};
