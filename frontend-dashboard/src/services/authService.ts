/**
 * 🔐 PROJECT SENTINEL - AUTHENTICATION SERVICE
 * Military-grade authentication service for defense personnel
 */

import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  display_name: string;
  role: 'ANALYST' | 'OFFICER' | 'COMMANDER' | 'ADMIN' | 'VIEWER';
  clearance_level: 'PUBLIC' | 'RESTRICTED' | 'CONFIDENTIAL' | 'SECRET' | 'TOP_SECRET';
  rank?: string;
  unit?: string;
  is_commander: boolean;
  can_access_classified: boolean;
  profile_picture?: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
  location?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginCredentials {
  username: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  employee_id?: string;
  rank?: string;
  unit?: string;
  clearance_level?: string;
  role?: string;
  phone_number?: string;
  location?: string;
}

export interface UserSession {
  id: number;
  ip_address: string;
  location: string;
  created_at: string;
  last_activity: string;
  is_current: boolean;
}

export interface UserActivity {
  action: string;
  description: string;
  ip_address: string;
  created_at: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  endpoint?: string;
  method?: string;
}

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private user: User | null = null;
  
  constructor() {
    this.loadTokensFromStorage();
    this.setupAxiosInterceptors();
  }

  /**
   * 🔐 LOGIN USER
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<LoginResponse> = await axios.post(
        `${API_BASE_URL}/auth/login/`,
        credentials
      );

      const { access, refresh, user } = response.data;
      
      this.setTokens(access, refresh);
      this.setUser(user);
      
      return response.data;
    } catch (error: any) {
      console.error('🚨 Login failed:', error.response?.data);
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * 📝 REGISTER USER
   */
  async register(data: RegisterData): Promise<LoginResponse> {
    try {
      const response: AxiosResponse<any> = await axios.post(
        `${API_BASE_URL}/auth/register/`,
        data
      );

      const { tokens, user } = response.data;
      
      this.setTokens(tokens.access, tokens.refresh);
      this.setUser(user);
      
      return {
        access: tokens.access,
        refresh: tokens.refresh,
        user: user
      };
    } catch (error: any) {
      console.error('🚨 Registration failed:', error.response?.data);
      throw new Error(error.response?.data?.details || 'Registration failed');
    }
  }

  /**
   * 🚪 LOGOUT USER
   */
  async logout(): Promise<void> {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout/`, {
        refresh: this.refreshToken
      });
    } catch (error) {
      console.error('🚨 Logout request failed:', error);
    } finally {
      this.clearAuth();
    }
  }

  /**
   * 🔄 REFRESH TOKEN
   */
  async refreshAccessToken(): Promise<string> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response: AxiosResponse<{ access: string }> = await axios.post(
        `${API_BASE_URL}/auth/token/refresh/`,
        { refresh: this.refreshToken }
      );

      const { access } = response.data;
      this.setTokens(access, this.refreshToken);
      
      return access;
    } catch (error) {
      console.error('🚨 Token refresh failed:', error);
      this.clearAuth();
      throw error;
    }
  }

  /**
   * 👤 GET USER PROFILE
   */
  async getProfile(): Promise<User> {
    try {
      const response: AxiosResponse<{ profile: User }> = await axios.get(
        `${API_BASE_URL}/auth/profile/`
      );
      
      this.setUser(response.data.profile);
      return response.data.profile;
    } catch (error) {
      console.error('🚨 Failed to get profile:', error);
      throw error;
    }
  }

  /**
   * ✏️ UPDATE USER PROFILE
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response: AxiosResponse<{ profile: User }> = await axios.put(
        `${API_BASE_URL}/auth/profile/`,
        data
      );
      
      this.setUser(response.data.profile);
      return response.data.profile;
    } catch (error) {
      console.error('🚨 Failed to update profile:', error);
      throw error;
    }
  }

  /**
   * 🔐 CHANGE PASSWORD
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    try {
      await axios.post(`${API_BASE_URL}/auth/change-password/`, {
        old_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPassword
      });
    } catch (error) {
      console.error('🚨 Failed to change password:', error);
      throw error;
    }
  }

  /**
   * 🔄 GET USER SESSIONS
   */
  async getUserSessions(): Promise<UserSession[]> {
    try {
      const response: AxiosResponse<{ sessions: UserSession[] }> = await axios.get(
        `${API_BASE_URL}/auth/sessions/`
      );
      return response.data.sessions;
    } catch (error) {
      console.error('🚨 Failed to get sessions:', error);
      throw error;
    }
  }

  /**
   * ❌ TERMINATE SESSION
   */
  async terminateSession(sessionId: number): Promise<void> {
    try {
      await axios.post(`${API_BASE_URL}/auth/sessions/${sessionId}/terminate/`);
    } catch (error) {
      console.error('🚨 Failed to terminate session:', error);
      throw error;
    }
  }

  /**
   * 📊 GET USER ACTIVITY
   */
  async getUserActivity(): Promise<UserActivity[]> {
    try {
      const response: AxiosResponse<{ activities: UserActivity[] }> = await axios.get(
        `${API_BASE_URL}/auth/activity/`
      );
      return response.data.activities;
    } catch (error) {
      console.error('🚨 Failed to get activity:', error);
      throw error;
    }
  }

  // Token and user management
  private setTokens(access: string, refresh?: string | null): void {
    this.accessToken = access;
    if (refresh) this.refreshToken = refresh;
    
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
    
    // Set default Authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
  }

  private setUser(user: User): void {
    this.user = user;
    localStorage.setItem('user', JSON.stringify(user));
  }

  private loadTokensFromStorage(): void {
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
    
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        this.user = JSON.parse(savedUser);
      } catch (error) {
        console.error('🚨 Failed to parse saved user:', error);
        localStorage.removeItem('user');
      }
    }

    if (this.accessToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
    }
  }

  private clearAuth(): void {
    this.accessToken = null;
    this.refreshToken = null;
    this.user = null;
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    delete axios.defaults.headers.common['Authorization'];
  }

  private setupAxiosInterceptors(): void {
    // Request interceptor to add auth headers
    axios.interceptors.request.use(
      (config) => {
        if (this.accessToken && !config.headers.Authorization) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newAccessToken = await this.refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return axios(originalRequest);
          } catch (refreshError) {
            console.error('🚨 Token refresh failed, redirecting to login');
            this.clearAuth();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Getters
  get isAuthenticated(): boolean {
    return !!this.accessToken && !!this.user;
  }

  get currentUser(): User | null {
    return this.user;
  }

  get tokens(): AuthTokens | null {
    if (!this.accessToken || !this.refreshToken) return null;
    return {
      access: this.accessToken,
      refresh: this.refreshToken
    };
  }

  // Role and permission helpers
  get isCommander(): boolean {
    return this.user?.is_commander || false;
  }

  get canAccessClassified(): boolean {
    return this.user?.can_access_classified || false;
  }

  get userRole(): string {
    return this.user?.role || 'VIEWER';
  }

  get clearanceLevel(): string {
    return this.user?.clearance_level || 'PUBLIC';
  }

  getRoleDisplayName(): string {
    const roleMap = {
      'ANALYST': '🔍 Intelligence Analyst',
      'OFFICER': '👮 Field Officer',
      'COMMANDER': '⭐ Operations Commander',
      'ADMIN': '🔧 System Administrator',
      'VIEWER': '👁️ Read-Only Viewer'
    };
    return roleMap[this.userRole as keyof typeof roleMap] || 'Unknown Role';
  }

  getClearanceDisplayName(): string {
    const clearanceMap = {
      'PUBLIC': '🟢 Public',
      'RESTRICTED': '🟡 Restricted',
      'CONFIDENTIAL': '🟠 Confidential',
      'SECRET': '🔴 Secret',
      'TOP_SECRET': '⚫ Top Secret'
    };
    return clearanceMap[this.clearanceLevel as keyof typeof clearanceMap] || 'Unknown';
  }
}

export const authService = new AuthService();

