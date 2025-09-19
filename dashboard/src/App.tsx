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
      main: '#FF8C00', // Dark orange
      light: '#FFB347', // Light orange
      dark: '#FF6600', // Darker orange
      contrastText: mode === 'dark' ? '#000000' : '#ffffff',
    },
    secondary: {
      main: mode === 'dark' ? '#FFA500' : '#FF7F00',
      light: mode === 'dark' ? '#FFD700' : '#FFA500',
      dark: mode === 'dark' ? '#FF8C00' : '#FF4500',
    },
    background: {
      default: mode === 'dark' ? '#121212' : '#fafafa',
      paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#000000',
      secondary: mode === 'dark' ? '#b3b3b3' : '#666666',
    },
    divider: mode === 'dark' ? '#333333' : '#e0e0e0',
    action: {
      hover: mode === 'dark' ? 'rgba(255, 140, 0, 0.08)' : 'rgba(0, 0, 0, 0.04)',
      selected: mode === 'dark' ? 'rgba(255, 140, 0, 0.12)' : 'rgba(0, 0, 0, 0.08)',
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
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-1px)',
            boxShadow: mode === 'dark' 
              ? '0 4px 20px rgba(255, 140, 0, 0.3)'
              : '0 4px 20px rgba(0, 0, 0, 0.1)',
          },
        },
        contained: {
          boxShadow: mode === 'dark'
            ? '0 2px 10px rgba(255, 140, 0, 0.2)'
            : '0 2px 10px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease',
          border: mode === 'dark' ? '1px solid #333333' : '1px solid #e0e0e0',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: mode === 'dark'
              ? '0 8px 30px rgba(255, 140, 0, 0.15)'
              : '0 8px 30px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          color: mode === 'dark' ? '#ffffff' : '#000000',
          boxShadow: mode === 'dark'
            ? '0 2px 10px rgba(0, 0, 0, 0.3)'
            : '0 2px 10px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            transition: 'all 0.3s ease',
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
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
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
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
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
