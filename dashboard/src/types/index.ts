export interface User {
  id: string;
  username: string;
  role: 'admin' | 'user';
  email: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

import React from 'react';

export interface AIApplication {
  id: string;
  name: string;
  displayName: string;
  icon: string | React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  color: string;
  apiEndpoint: string;
}

export interface MetricData {
  id: string;
  applicationId: string;
  timestamp: string;
  responseTime: number;
  requestCount: number;
  errorRate: number;
  successRate: number;
  averageTokens: number;
  cost: number;
  uptime: number;
  // Optional LLM/common fields
  model?: string;
  promptTokens?: number;
  completionTokens?: number;
  totalTokens?: number;
  // Copilot specific
  totalSuggestions?: number;
  acceptedSuggestions?: number;
  totalUsers?: number;
  linesSuggested?: number;
  linesAccepted?: number;
  // Cursor specific
  totalSeats?: number;
  activeUsers?: number;
  monthlyActiveUsers?: number;
  weeklyActiveUsers?: number;
  dailyActiveUsers?: number;
  tokenBreakdown?: any;
  eventBreakdown?: any;
  modelBreakdown?: any;
  meta?: any;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface FilterOptions {
  application?: string;
  dateRange?: {
    start: string;
    end: string;
  };
  sortBy?: keyof MetricData;
  sortOrder?: 'asc' | 'desc';
}

export interface DashboardStats {
  totalRequests: number;
  averageResponseTime: number;
  overallSuccessRate: number;
  totalCost: number;
  activeApplications: number;
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  application: string;
}

export interface ErrorInfo {
  message: string;
  code?: string;
  timestamp: string;
  application?: string;
}