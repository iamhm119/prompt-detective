import { api } from './api';

// ==================== Types ====================

export interface AdminDashboardStats {
  total_users: number;
  active_users: number;
  verified_users: number;
  premium_users: number;
  total_analyses: number;
  analyses_today: number;
  total_api_calls: number;
  subscription_breakdown: {
    free: number;
    pro: number;
    enterprise: number;
  };
}

export interface UserDetail {
  id: number;
  email: string;
  full_name: string;
  username: string;
  subscription_tier: string;
  is_active: boolean;
  is_premium: boolean;
  is_email_verified: boolean;
  is_admin: boolean;
  is_super_admin: boolean;
  api_calls_used: number;
  api_calls_limit: number;
  created_at: string;
  total_analyses: number;
}

export interface UpdateUserRequest {
  is_active?: boolean;
  is_premium?: boolean;
  subscription_tier?: string;
  api_calls_limit?: number;
}

// ==================== Admin API Service ====================

class AdminService {
  /**
   * Get admin dashboard statistics
   */
  async getDashboardStats(): Promise<AdminDashboardStats> {
    const response = await api.get<AdminDashboardStats>('/admin/dashboard');
    return response.data;
  }

  /**
   * Get all users with optional filtering
   */
  async getUsers(params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }): Promise<UserDetail[]> {
    const response = await api.get<UserDetail[]>('/admin/users', { params });
    return response.data;
  }

  /**
   * Get specific user details
   */
  async getUserDetails(userId: number): Promise<UserDetail> {
    const response = await api.get<UserDetail>(`/admin/users/${userId}`);
    return response.data;
  }

  /**
   * Update user properties (super admin only)
   */
  async updateUser(userId: number, data: UpdateUserRequest): Promise<{ message: string; user_id: number }> {
    const response = await api.put(`/admin/users/${userId}`, data);
    return response.data;
  }

  /**
   * Delete user (super admin only)
   */
  async deleteUser(userId: number): Promise<{ message: string; user_id: number }> {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
  }

  /**
   * Reset user API usage
   */
  async resetUserUsage(userId: number): Promise<{ message: string; user_id: number }> {
    const response = await api.post(`/admin/users/${userId}/reset-usage`);
    return response.data;
  }

  /**
   * Toggle user premium status
   */
  async togglePremium(userId: number): Promise<{ message: string; user_id: number; is_premium: boolean }> {
    const response = await api.post(`/admin/users/${userId}/toggle-premium`);
    return response.data;
  }
}

export const adminService = new AdminService();
