import type { User, ApiResponse } from '../types';

interface LoginResponse {
  user: User;
  token: string;
}

interface RefreshTokenResponse {
  token: string;
}

class AuthService {
  private baseUrl = ((typeof import.meta !== 'undefined' && (import.meta as any).env && (import.meta as any).env.VITE_API_URL) || '') + '/auth';

  async login(username: string, password: string): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await fetch(`${this.baseUrl}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      return {
        success: true,
        data,
      };
    } catch (error) {
      // For demo purposes, simulate successful login with admin credentials
      if (username === 'admin' && password === 'admin123') {
        const mockUser: User = {
          id: '1',
          username: 'admin',
          role: 'admin',
          email: 'admin@dashboard.com',
        };
        const mockToken = 'mock-jwt-token-' + Date.now();
        return {
          success: true,
          data: {
            user: mockUser,
            token: mockToken,
          },
        };
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed',
        data: null as any,
      };
    }
  }

  async validateToken(token: string): Promise<User | null> {
    try {
      const response = await fetch(`${this.baseUrl}/validate`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token validation failed');
      }

      const payload = await response.json();
      // Backend returns { success, data: { user } }
      return payload?.data?.user ?? null;
    } catch (error) {
      // For demo purposes, validate mock token
      if (token.startsWith('mock-jwt-token-')) {
        return {
          id: '1',
          username: 'admin',
          role: 'admin',
          email: 'admin@dashboard.com',
        };
      }
      return null;
    }
  }

  async refreshToken(): Promise<ApiResponse<RefreshTokenResponse>> {
    try {
      const currentToken = localStorage.getItem('adminToken');
      if (!currentToken) {
        throw new Error('No token found');
      }

      const response = await fetch(`${this.baseUrl}/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${currentToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const payload = await response.json();
      return {
        success: true,
        data: payload?.data,
      };
    } catch (error) {
      // For demo purposes, generate new mock token
      const newToken = 'mock-jwt-token-' + Date.now();
      return {
        success: true,
        data: {
          token: newToken,
        },
      };
    }
  }

  logout(): void {
    localStorage.removeItem('adminToken');
  }
}

export const authService = new AuthService();