import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material';
import {
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
  ApplicationSelector,
  MetricsTable,
  MetricsChart,
  FilterPanel,
  ThemeToggle,
} from '../components';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [applications, setApplications] = useState<AIApplication[]>([]);
  const [selectedApp, setSelectedApp] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({
    dateRange: (() => {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 30);
      return { start: start.toISOString().split('T')[0], end: end.toISOString().split('T')[0] };
    })(),
  });
  const [showFilters, setShowFilters] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadApplications();
    loadDashboardStats();
  }, []);

  useEffect(() => {
    if (selectedApp) {
      loadMetrics();
    } else {
      setMetrics([]);
    }
  }, [selectedApp, filters]);

  const loadApplications = async () => {
    const result = await apiService.getApplications();
    if (result.success) {
      setApplications(result.data);
      // Select the first app by default
      setSelectedApp(result.data[0]?.id || null);
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
      if (!selectedApp) return;
      const result = await apiService.getMetrics(selectedApp, filters);
      if (result.success) {
        setMetrics(result.data);
      } else {
        setError(result.error || 'Failed to load metrics');
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
        {/* Dashboard Stats */}
        {dashboardStats && (
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

        {/* Application Selector */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Select AI Applications
            </Typography>
            <ApplicationSelector
              applications={applications}
              selectedApp={selectedApp}
              onSelectionChange={setSelectedApp}
            />
          </CardContent>
        </Card>

        {/* Filter Panel */}
        {showFilters && (
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

        {/* Selected Application Display */}
        {selectedApp && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Showing metrics for:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {(() => {
                const app = applications.find(a => a.id === selectedApp);
                return app ? (
                  <Chip
                    icon={
                      typeof app.icon === 'string' ? (
                        <span style={{ fontSize: '16px' }}>{app.icon}</span>
                      ) : (
                        (() => {
                          const IconComponent = app.icon;
                          return <IconComponent width={16} height={16} style={{ color: 'white' }} />;
                        })()
                      )
                    }
                    label={app.displayName}
                    size="small"
                    sx={{ bgcolor: app.color, color: 'white' }}
                  />
                ) : null;
              })()}
            </Box>
          </Box>
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
                Please select at least one AI application to view metrics.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Container>
    </Box>
  );
};

export default DashboardPage;