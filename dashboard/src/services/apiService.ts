import type { AIApplication, MetricData, ApiResponse, DashboardStats, FilterOptions } from '../types';
import ChatGPTIcon from '../assets/logos/chatgpt.svg?react';
import ClaudeIcon from '../assets/logos/claude.svg?react';
import CursorIcon from '../assets/logos/cursor.svg?react';
// Windsurf not available currently

interface RetryOptions {
  maxRetries: number;
  delay: number;
  backoff: number;
}

class ApiService {
  private baseUrl = (typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.VITE_API_URL) || '';
  private timeout = 10000; // 10 seconds
  private defaultRetryOptions: RetryOptions = {
    maxRetries: 3,
    delay: 1000,
    backoff: 2,
  };

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async makeRequest<T>(
    endpoint: string, 
    options: RequestInit = {},
    retryOptions: Partial<RetryOptions> = {}
  ): Promise<T> {
    const { maxRetries, delay, backoff } = { ...this.defaultRetryOptions, ...retryOptions };
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          ...options,
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorMessage = `HTTP ${response.status}: ${response.statusText}`;
          throw new Error(errorMessage);
        }

        return await response.json();
      } catch (error) {
        clearTimeout(timeoutId);
        
        if (error instanceof Error) {
          lastError = error;
          
          if (error.name === 'AbortError') {
            lastError = new Error('Request timeout - please check your connection');
          }
          
          // Don't retry on certain errors
          if (error.message.includes('401') || error.message.includes('403')) {
            throw new Error('Authentication failed - please log in again');
          }
          
          if (attempt < maxRetries) {
            const waitTime = delay * Math.pow(backoff, attempt);
            console.warn(`Request failed (attempt ${attempt + 1}/${maxRetries + 1}): ${error.message}. Retrying in ${waitTime}ms...`);
            await this.sleep(waitTime);
            continue;
          }
        } else {
          lastError = new Error('Unknown error occurred');
        }
      }
    }

    throw lastError!;
  }

  // Static app configuration
  private appConfigMap: Record<string, Pick<AIApplication, 'displayName' | 'icon' | 'color' | 'apiEndpoint'>> = {
    chatgpt: {
      displayName: 'ChatGPT',
      icon: ChatGPTIcon,
      color: '#10a37f',
      apiEndpoint: '/metrics/openai',
    },
    claude: {
      displayName: 'Claude',
      icon: ClaudeIcon,
      color: '#ff6b35',
      apiEndpoint: '/metrics/claude',
    },
    copilot: {
      displayName: 'GitHub Copilot',
      icon: ChatGPTIcon,
      color: '#0ea5e9',
      apiEndpoint: '/metrics/copilot',
    },
    cursor: {
      displayName: 'Cursor',
      icon: CursorIcon,
      color: '#8b5cf6',
      apiEndpoint: '/metrics/cursor',
    },
  };

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('adminToken');
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    };
  }

  async getApplications(): Promise<ApiResponse<AIApplication[]>> {
    const apps: AIApplication[] = Object.entries(this.appConfigMap).map(([id, cfg]) => ({
      id,
      name: id,
      displayName: cfg.displayName,
      icon: cfg.icon,
      color: cfg.color,
      apiEndpoint: cfg.apiEndpoint,
    }));
    return { success: true, data: apps };
  }

  async getMetrics(applicationId: string, filters?: FilterOptions): Promise<ApiResponse<MetricData[]>> {
    try {
      const cfg = this.appConfigMap[applicationId];
      if (!cfg) {
        throw new Error('Application not found');
      }

      const queryParams = new URLSearchParams();
      if (filters?.dateRange) {
        queryParams.append('start_date', filters.dateRange.start);
        queryParams.append('end_date', filters.dateRange.end);
      } else {
        const end = new Date();
        const start = new Date();
        start.setDate(end.getDate() - 30);
        queryParams.append('start_date', start.toISOString());
        queryParams.append('end_date', end.toISOString());
      }
      if (filters?.sortBy) {
        queryParams.append('sort_by', filters.sortBy);
        queryParams.append('sort_order', filters.sortOrder || 'desc');
      }
      const endpointPath = `${cfg.apiEndpoint}?${queryParams.toString()}`;
      const data = await this.makeRequest<{ success: boolean; data: MetricData[]; error?: string }>(endpointPath, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      if (!data.success) {
        throw new Error(data.error || `Failed to fetch metrics for ${cfg.displayName}`);
      }
      return { success: true, data: data.data || [] };
    } catch (error) {
      // Generate mock data for demo purposes
      const mockData = this.generateMockMetrics(applicationId, 20);
      return {
        success: true,
        data: mockData,
      };
    }
  }

  async getAllMetrics(filters?: FilterOptions): Promise<ApiResponse<MetricData[]>> {
    try {
      const allMetrics: MetricData[] = [];
      const appIds = Object.keys(this.appConfigMap);
      for (const appId of appIds) {
        const result = await this.getMetrics(appId, filters);
        if (result.success) {
          allMetrics.push(...result.data);
        }
      }

      // Sort by timestamp if no specific sort is provided
      if (!filters?.sortBy) {
        allMetrics.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      }

      return {
        success: true,
        data: allMetrics,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch all metrics',
        data: [],
      };
    }
  }

  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    try {
      const payload = await this.makeRequest<{ success: boolean; data: DashboardStats; error?: string }>(`/metrics/stats`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });
      if (!payload.success) {
        throw new Error(payload.error || 'Failed to fetch dashboard stats');
      }
      return { success: true, data: payload.data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch dashboard stats',
        data: {
          totalRequests: 0,
          averageResponseTime: 0,
          overallSuccessRate: 0,
          totalCost: 0,
          activeApplications: 0,
        },
      };
    }
  }

  private generateMockMetrics(applicationId: string, count: number): MetricData[] {
    const metrics: MetricData[] = [];
    const now = new Date();

    for (let i = 0; i < count; i++) {
      const timestamp = new Date(now.getTime() - (i * 60 * 60 * 1000)); // Every hour
      metrics.push({
        id: `${applicationId}-${i}`,
        applicationId,
        timestamp: timestamp.toISOString(),
        responseTime: Math.floor(Math.random() * 2000) + 100, // 100-2100ms
        requestCount: Math.floor(Math.random() * 1000) + 50, // 50-1050 requests
        errorRate: Math.random() * 5, // 0-5% error rate
        successRate: 95 + Math.random() * 5, // 95-100% success rate
        averageTokens: Math.floor(Math.random() * 500) + 100, // 100-600 tokens
        cost: Math.random() * 10 + 1, // $1-11
        uptime: 95 + Math.random() * 5, // 95-100% uptime
      });
    }

    return metrics;
  }
}

export const apiService = new ApiService();