import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { ErrorBoundary } from './components';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#FF8C00' : '#FF7F00',
      light: mode === 'dark' ? '#FFB347' : '#FFA500',
      dark: mode === 'dark' ? '#FF6600' : '#FF4500',
      contrastText: '#ffffff',
    },
    secondary: {
      main: mode === 'dark' ? '#FFA500' : '#FF8C00',
      light: mode === 'dark' ? '#FFD700' : '#FFB347',
      dark: mode === 'dark' ? '#FF8C00' : '#FF6600',
      contrastText: '#ffffff',
    },
    background: {
      default: mode === 'dark' ? '#0a0a0a' : '#fafafa',
      paper: mode === 'dark' ? '#1a1a1a' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#1a1a1a',
      secondary: mode === 'dark' ? '#b3b3b3' : '#666666',
    },
    divider: mode === 'dark' ? '#333333' : '#e0e0e0',
    error: {
      main: mode === 'dark' ? '#f44336' : '#d32f2f',
    },
    warning: {
      main: mode === 'dark' ? '#ff9800' : '#ed6c02',
    },
    info: {
      main: mode === 'dark' ? '#2196f3' : '#0288d1',
    },
    success: {
      main: mode === 'dark' ? '#4caf50' : '#2e7d32',
    },
    action: {
      hover: mode === 'dark' ? 'rgba(255, 140, 0, 0.08)' : 'rgba(255, 127, 0, 0.04)',
      selected: mode === 'dark' ? 'rgba(255, 140, 0, 0.12)' : 'rgba(255, 127, 0, 0.08)',
      disabledBackground: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
      disabled: mode === 'dark' ? 'rgba(255, 255, 255, 0.3)' : 'rgba(0, 0, 0, 0.38)',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          transition: 'background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease',
        },
        body: {
          transition: 'background-color 0.3s ease',
        },
        html: {
          scrollBehavior: 'smooth',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          transition: 'all 0.3s ease',
          minHeight: '40px',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: mode === 'dark' 
              ? '0 4px 20px rgba(255, 140, 0, 0.3)'
              : '0 4px 20px rgba(255, 127, 0, 0.2)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          boxShadow: mode === 'dark'
            ? '0 2px 10px rgba(255, 140, 0, 0.2)'
            : '0 2px 10px rgba(255, 127, 0, 0.15)',
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease',
          border: mode === 'dark' ? '1px solid #333333' : '1px solid #e0e0e0',
          boxShadow: mode === 'dark'
            ? '0 4px 20px rgba(0, 0, 0, 0.3)'
            : '0 4px 20px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: mode === 'dark'
              ? '0 8px 30px rgba(255, 140, 0, 0.15)'
              : '0 8px 30px rgba(255, 127, 0, 0.1)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' 
            ? 'rgba(26, 26, 26, 0.9)' 
            : 'rgba(255, 255, 255, 0.9)',
          color: mode === 'dark' ? '#ffffff' : '#1a1a1a',
          boxShadow: mode === 'dark'
            ? '0 2px 10px rgba(0, 0, 0, 0.5)'
            : '0 2px 10px rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(10px)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            transition: 'all 0.3s ease',
            backgroundColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)',
            '&:hover': {
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: mode === 'dark' ? '#FF8C00' : '#FF7F00',
                boxShadow: mode === 'dark'
                  ? '0 0 10px rgba(255, 140, 0, 0.2)'
                  : '0 0 10px rgba(255, 127, 0, 0.2)',
              },
            },
            '&.Mui-focused': {
              '& .MuiOutlinedInput-notchedOutline': {
                boxShadow: mode === 'dark'
                  ? '0 0 15px rgba(255, 140, 0, 0.3)'
                  : '0 0 15px rgba(255, 127, 0, 0.3)',
              },
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          fontWeight: 500,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          height: 8,
        },
        bar: {
          borderRadius: 8,
        },
      },
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.2,
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.3,
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.4,
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.95rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 600,
      fontSize: '0.875rem',
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 8,
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return !isAuthenticated ? <>{children}</> : <Navigate to="/dashboard" replace />;
};

const AppContent: React.FC = () => {
  const { mode } = useTheme();
  const theme = createAppTheme(mode);

  return (
    <MuiThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </MuiThemeProvider>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
