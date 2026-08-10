import { api } from './api';

export interface WaitlistPayload {
  email: string;
  planName?: string | null;
  source?: string | null;
  notes?: string | null;
}

export interface WaitlistResponse {
  message: string;
  already_joined: boolean;
}

export const subscribeToWaitlist = async (
  payload: WaitlistPayload
): Promise<WaitlistResponse> => {
  const response = await api.post<WaitlistResponse>('/waitlist/subscribe', {
    email: payload.email,
    plan_name: payload.planName ?? null,
    source: payload.source ?? null,
    notes: payload.notes ?? null,
  });

  return response.data;
};
