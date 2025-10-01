import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';import {
  AccountCircle,
  Refresh,
  FilterList,
  TrendingUp,
  Speed,
  CheckCircle,
  AttachMoney,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { apiService } from '../services/apiService';
import type { AIApplication, DashboardStats, MetricData, FilterOptions } from '../types';
import {
  ApplicationDropdownSelector,
  MetricsTable,
  MetricsChart,
  FilterPanel,
  ThemeToggle,
  ChatgptMetricsDashboard,
  CopilotMetricsDashboard,
  ClaudeMetricsDashboard,
} from '../components';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [applications, setApplications] = useState<AIApplication[]>([]);
  const [selectedApp, setSelectedApp] = useState<string>('');
  const [submittedApp, setSubmittedApp] = useState<string>('');
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({});
  const [showFilters, setShowFilters] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);


  useEffect(() => {
    loadApplications();
    loadDashboardStats();
  }, []);

  useEffect(() => {
    if (submittedApp) {
      loadMetrics();
    } else {
      setMetrics([]);
    }
  }, [submittedApp, filters]);

  const loadApplications = async () => {
    const result = await apiService.getApplications();
    if (result.success) {
      setApplications(result.data);
    }
  };

  const loadDashboardStats = async () => {
    const result = await apiService.getDashboardStats();
    if (result.success) {
      setDashboardStats(result.data);
    }
  };

  const loadMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      if (submittedApp) {
        // Load metrics for selected app
        const result = await apiService.getMetrics(submittedApp, filters);
        if (result.success) {
          setMetrics(result.data);
        } else {
          setError(result.error || 'Failed to load metrics');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadMetrics();
    loadDashboardStats();
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleMenuClose();
  };

  const formatNumber = (num: number, decimals = 0) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Metrics Dashboard
          </Typography>

          <ThemeToggle />
          <IconButton color="inherit" onClick={handleRefresh}>
            <Refresh />
          </IconButton>
          <IconButton color="inherit" onClick={() => setShowFilters(!showFilters)}>
            <FilterList />
          </IconButton>
          <IconButton color="inherit" onClick={handleMenuClick}>
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem disabled>
              <Typography variant="body2">
                {user?.username} ({user?.role})
              </Typography>
            </MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {/* Application Dropdown Selector */}
        <ApplicationDropdownSelector
          applications={applications}
          selectedApp={selectedApp}
          onSelectionChange={setSelectedApp}
          onSubmit={() => setSubmittedApp(selectedApp)}
        />

        {/* Dashboard Stats */}
        {dashboardStats && submittedApp && (
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 3, mb: 3 }}>
            <Box>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <TrendingUp sx={{ mr: 2, color: 'primary.main' }} />
                    <Box>
                      <Typography variant="h4">
                        {formatNumber(dashboardStats.totalRequests)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Requests
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
            <Box>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Speed sx={{ mr: 2, color: 'warning.main' }} />
                    <Box>
                      <Typography variant="h4">
                        {formatNumber(dashboardStats.averageResponseTime)}ms
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Response Time
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
            <Box>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CheckCircle sx={{ mr: 2, color: 'success.main' }} />
                    <Box>
                      <Typography variant="h4">
                        {formatNumber(dashboardStats.overallSuccessRate, 1)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Success Rate
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
            <Box>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AttachMoney sx={{ mr: 2, color: 'info.main' }} />
                    <Box>
                      <Typography variant="h4">
                        {formatCurrency(dashboardStats.totalCost)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Cost
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </Box>
        )}

        {/* Admin Metrics Dashboard for ChatGPT */}
        {submittedApp === 'chatgpt' && (
          <Box sx={{ mb: 3 }}>
            <ChatgptMetricsDashboard application="chatgpt" />
          </Box>
        )}

        {/* Direct Copilot Metrics Dashboard */}
        {submittedApp === 'copilot' && (
          <Box sx={{ mb: 3 }}>
            <CopilotMetricsDashboard application="copilot" />
          </Box>
        )}

        {/* Claude Metrics Dashboard */}
        {submittedApp === 'claude' && (
          <Box sx={{ mb: 3 }}>
            <ClaudeMetricsDashboard application="claude" />
          </Box>
        )}

        {/* Filter Panel */}
        {submittedApp && showFilters && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <FilterPanel
                filters={filters}
                onFiltersChange={setFilters}
                applications={applications}
              />
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Metrics Chart */}
        {metrics.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics Over Time
              </Typography>
              <MetricsChart metrics={metrics} applications={applications} />
            </CardContent>
          </Card>
        )}

        {/* Metrics Table */}
        {metrics.length > 0 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Metrics
              </Typography>
              <MetricsTable
                metrics={metrics}
                applications={applications}
                loading={loading}
              />
            </CardContent>
          </Card>
        )}

        {/* No Data Message */}
        {!selectedApp && (
          <Card>
            <CardContent>
              <Typography variant="body1" color="text.secondary" textAlign="center">
                Please select an AI application from the dropdown above to view metrics.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Container>

    </Box>
  );
};

export default DashboardPage;