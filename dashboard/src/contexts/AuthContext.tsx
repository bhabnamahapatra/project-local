import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { AuthState, User } from '../types';
import { authService } from '../services/authService';

interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'REFRESH_TOKEN'; payload: { token: string } };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'REFRESH_TOKEN':
      return {
        ...state,
        token: action.payload.token,
      };
    default:
      return state;
  }
};

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
};

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      authService.validateToken(token).then((user: User | null) => {
        if (user) {
          dispatch({ type: 'LOGIN_SUCCESS', payload: { user, token } });
        } else {
          localStorage.removeItem('adminToken');
        }
      });
    }
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const result = await authService.login(username, password);
      if (result.success && result.data) {
        localStorage.setItem('adminToken', result.data.token);
        dispatch({
          type: 'LOGIN_SUCCESS',
          payload: { user: result.data.user, token: result.data.token },
        });
        return true;
      } else {
        dispatch({ type: 'LOGIN_FAILURE' });
        return false;
      }
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('adminToken');
    dispatch({ type: 'LOGOUT' });
  };

  const refreshToken = async (): Promise<boolean> => {
    try {
      const result = await authService.refreshToken();
      if (result.success && result.data) {
        localStorage.setItem('adminToken', result.data.token);
        dispatch({ type: 'REFRESH_TOKEN', payload: { token: result.data.token } });
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};