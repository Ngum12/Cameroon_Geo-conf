/**
 * API Service for Project Sentinel Dashboard
 * Handles communication with Django backend
 */

import axios, { AxiosResponse, AxiosError } from 'axios';
import { EventsGeoJSON, NewsArticle, SystemStatistics, ProcessingResponse, APIError } from '../types';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication if needed
api.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log successful responses in development
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    }
    return response;
  },
  (error: AxiosError) => {
    const errorMessage = error.response?.data || error.message;
    const status = error.response?.status || 0;
    
    console.error(`❌ API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${status}`, errorMessage);
    
    // Handle specific error cases
    if (status === 401) {
      // Unauthorized - clear token and redirect to login if implemented
      localStorage.removeItem('auth_token');
      console.warn('🔐 Authentication token expired or invalid');
    } else if (status === 403) {
      console.warn('🚫 Access denied - insufficient permissions');
    } else if (status === 404) {
      console.warn('🔍 Resource not found');
    } else if (status >= 500) {
      console.error('🚨 Server error - backend may be unavailable');
    }
    
    return Promise.reject({
      error: errorMessage,
      status,
      details: error.response?.statusText,
    } as APIError);
  }
);

/**
 * Fetch events/articles as GeoJSON for map visualization
 */
export const fetchEvents = async (options: {
  limit?: number;
  days?: number;
  source?: string;
  priority?: number;
} = {}): Promise<EventsGeoJSON> => {
  try {
    const params = new URLSearchParams();
    
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.days) params.append('days', options.days.toString());
    if (options.source) params.append('source', options.source);
    if (options.priority) params.append('priority', options.priority.toString());
    
    const response = await api.get<EventsGeoJSON>(`/api/v1/events/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch events:', error);
    throw error;
  }
};

/**
 * Fetch system statistics
 */
export const fetchStatistics = async (): Promise<SystemStatistics> => {
  try {
    const response = await api.get<SystemStatistics>('/api/v1/statistics/');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch statistics:', error);
    throw error;
  }
};

/**
 * Fetch articles list with pagination
 */
export const fetchArticles = async (options: {
  page?: number;
  page_size?: number;
  status?: string;
  source?: string;
  days?: number;
} = {}): Promise<{
  count: number;
  next: string | null;
  previous: string | null;
  results: NewsArticle[];
}> => {
  try {
    const params = new URLSearchParams();
    
    if (options.page) params.append('page', options.page.toString());
    if (options.page_size) params.append('page_size', options.page_size.toString());
    if (options.status) params.append('status', options.status);
    if (options.source) params.append('source', options.source);
    if (options.days) params.append('days', options.days.toString());
    
    const response = await api.get(`/api/v1/articles/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch articles:', error);
    throw error;
  }
};

/**
 * Fetch single article details
 */
export const fetchArticle = async (articleId: string): Promise<NewsArticle> => {
  try {
    const response = await api.get<NewsArticle>(`/api/v1/articles/${articleId}/`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch article ${articleId}:`, error);
    throw error;
  }
};

/**
 * Process a new article through the NLP pipeline
 */
export const processArticle = async (articleData: {
  url: string;
  title: string;
  source: string;
  raw_text: string;
  published_date?: string;
  classification?: string;
  priority?: number;
}): Promise<ProcessingResponse> => {
  try {
    const response = await api.post<ProcessingResponse>('/api/v1/process-article/', articleData);
    return response.data;
  } catch (error) {
    console.error('Failed to process article:', error);
    throw error;
  }
};

/**
 * Health check endpoint
 */
export const checkHealth = async (): Promise<{
  status: string;
  service: string;
  timestamp: string;
  version: string;
}> => {
  try {
    const response = await api.get('/health/');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Get available news sources from the backend
 */
export const fetchNewsSources = async (): Promise<string[]> => {
  try {
    const statistics = await fetchStatistics();
    return statistics.by_source.map(item => item.source);
  } catch (error) {
    console.error('Failed to fetch news sources:', error);
    // Return default Cameroon sources as fallback
    return [
      'Cameroon Tribune',
      'Journal du Cameroun',
      'Camer.be',
      '237actu',
      'Actu Cameroun',
      'Cameroon News Agency',
      'Business in Cameroon',
      'Cameroon Intelligence Report'
    ];
  }
};

/**
 * Utility function to handle API errors consistently
 */
export const handleApiError = (error: unknown): string => {
  if (typeof error === 'object' && error !== null && 'error' in error) {
    const apiError = error as APIError;
    if (apiError.details) {
      return `${apiError.error}: ${apiError.details}`;
    }
    return apiError.error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

/**
 * Check if the backend API is accessible
 */
export const checkApiConnection = async (): Promise<boolean> => {
  try {
    await checkHealth();
    return true;
  } catch {
    return false;
  }
};

// Export the axios instance for advanced usage if needed
export { api };

// Default export with all API functions
export default {
  fetchEvents,
  fetchStatistics,
  fetchArticles,
  fetchArticle,
  processArticle,
  checkHealth,
  fetchNewsSources,
  handleApiError,
  checkApiConnection,
};
