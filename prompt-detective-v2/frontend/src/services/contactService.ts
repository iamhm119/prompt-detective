import { api } from './api';

export interface ContactTopic {
  key: string;
  title: string;
  description: string;
  faq_examples: string[];
  expected_response_hours: number;
}

export interface SubmitContactPayload {
  name: string;
  email: string;
  topic: string;
  selected_question?: string | null;
  message?: string | null;
  account_stage?: string | null;
  consent?: boolean;
}

export interface SubmitContactResponse {
  success: boolean;
  message: string;
  reference_id: number;
}

export const getContactTopics = async (): Promise<ContactTopic[]> => {
  const response = await api.get<{ topics: ContactTopic[] }>('/support/contact/topics');
  return response.data.topics;
};

export const submitContactRequest = async (
  payload: SubmitContactPayload
): Promise<SubmitContactResponse> => {
  const response = await api.post<SubmitContactResponse>('/support/contact', payload);
  return response.data;
};
