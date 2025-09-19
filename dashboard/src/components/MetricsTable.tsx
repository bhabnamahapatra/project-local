import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Paper,
  Chip,
  Box,
  Typography,
  CircularProgress,
  TablePagination,
  useTheme,
  styled,
} from '@mui/material';
import type { MetricData, AIApplication } from '../types';

interface MetricsTableProps {
  metrics: MetricData[];
  applications: AIApplication[];
  loading?: boolean;
}

type SortableKeys = keyof MetricData;

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  '& .MuiTableCell-head': {
    backgroundColor: theme.palette.mode === 'dark' 
      ? 'rgba(255, 165, 0, 0.1)' 
      : theme.palette.grey[50],
    fontWeight: 600,
    borderBottom: theme.palette.mode === 'dark'
      ? '2px solid rgba(255, 165, 0, 0.3)'
      : `2px solid ${theme.palette.divider}`,
  },
  '& .MuiTableRow-root:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 165, 0, 0.05)'
      : theme.palette.action.hover,
    boxShadow: theme.palette.mode === 'dark'
      ? '0 0 10px rgba(255, 165, 0, 0.1)'
      : 'none',
    transition: 'all 0.3s ease',
  },
  '& .MuiTableCell-root': {
    borderBottom: theme.palette.mode === 'dark'
      ? '1px solid rgba(255, 255, 255, 0.1)'
      : `1px solid ${theme.palette.divider}`,
  },
}));

const GlowingChip = styled(Chip)(({ theme, color }) => ({
  ...(theme.palette.mode === 'dark' && {
    boxShadow: `0 0 8px ${color === 'success' ? '#4caf50' : color === 'error' ? '#f44336' : color === 'warning' ? '#ff9800' : theme.palette.primary.main}40`,
    transition: 'box-shadow 0.3s ease',
    '&:hover': {
      boxShadow: `0 0 12px ${color === 'success' ? '#4caf50' : color === 'error' ? '#f44336' : color === 'warning' ? '#ff9800' : theme.palette.primary.main}60`,
    },
  }),
}));

const MetricsTable: React.FC<MetricsTableProps> = ({
  metrics,
  applications,
  loading = false,
}) => {
  useTheme();
  const [orderBy, setOrderBy] = useState<SortableKeys>('timestamp');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // theme mode used in styled components; keep local var unused removal

  const handleSort = (property: SortableKeys) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const sortedMetrics = React.useMemo(() => {
    return [...metrics].sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return order === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return order === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });
  }, [metrics, orderBy, order]);

  const paginatedMetrics = sortedMetrics.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const getApplicationInfo = (applicationId: string) => {
    return applications.find(app => app.id === applicationId);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatNumber = (num: number, decimals = 2) => {
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

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (metrics.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          No metrics data available.
        </Typography>
      </Box>
    );
  }

  const columns: Array<{ key: keyof MetricData; label: string; align?: 'right' | 'left' } | { key: 'application'; label: string } | { key: 'timestamp'; label: string }> = [
    { key: 'application', label: 'Application' } as any,
    { key: 'timestamp', label: 'Timestamp' } as any,
    { key: 'responseTime', label: 'Response Time (ms)', align: 'right' },
    { key: 'requestCount', label: 'Requests', align: 'right' },
    { key: 'successRate', label: 'Success Rate (%)', align: 'right' },
    { key: 'errorRate', label: 'Error Rate (%)', align: 'right' },
    { key: 'averageTokens', label: 'Avg Tokens', align: 'right' },
    { key: 'cost', label: 'Cost', align: 'right' },
    { key: 'uptime', label: 'Uptime (%)', align: 'right' },
  ];

  // Add app-specific columns if present in any row
  const has = (field: keyof MetricData) => sortedMetrics.some(m => m[field] !== undefined && m[field] !== null);
  if (has('model')) columns.splice(2, 0, { key: 'model', label: 'Model' } as any);
  if (has('totalTokens')) columns.push({ key: 'totalTokens', label: 'Total Tokens', align: 'right' } as any);
  if (has('promptTokens')) columns.push({ key: 'promptTokens', label: 'Prompt Tokens', align: 'right' } as any);
  if (has('completionTokens')) columns.push({ key: 'completionTokens', label: 'Completion Tokens', align: 'right' } as any);
  if (has('totalSuggestions')) columns.push({ key: 'totalSuggestions', label: 'Suggestions', align: 'right' } as any);
  if (has('acceptedSuggestions')) columns.push({ key: 'acceptedSuggestions', label: 'Accepted', align: 'right' } as any);
  if (has('totalUsers')) columns.push({ key: 'totalUsers', label: 'Users', align: 'right' } as any);
  if (has('linesSuggested')) columns.push({ key: 'linesSuggested', label: 'Lines Suggested', align: 'right' } as any);
  if (has('linesAccepted')) columns.push({ key: 'linesAccepted', label: 'Lines Accepted', align: 'right' } as any);
  if (has('totalSeats')) columns.push({ key: 'totalSeats', label: 'Seats', align: 'right' } as any);
  if (has('activeUsers')) columns.push({ key: 'activeUsers', label: 'Active Users', align: 'right' } as any);
  if (has('monthlyActiveUsers')) columns.push({ key: 'monthlyActiveUsers', label: 'MAU', align: 'right' } as any);
  if (has('weeklyActiveUsers')) columns.push({ key: 'weeklyActiveUsers', label: 'WAU', align: 'right' } as any);
  if (has('dailyActiveUsers')) columns.push({ key: 'dailyActiveUsers', label: 'DAU', align: 'right' } as any);

  return (
    <Box>
      <Paper variant="outlined">
        <StyledTableContainer>
          <Table>
            <TableHead>
              <TableRow>
                {columns.map(col => (
                  <TableCell key={String(col.key)} align={(col as any).align || 'left'}>
                    {col.key !== 'application' && col.key !== 'timestamp' ? (
                      <TableSortLabel
                        active={orderBy === (col.key as SortableKeys)}
                        direction={orderBy === (col.key as SortableKeys) ? order : 'asc'}
                        onClick={() => handleSort(col.key as SortableKeys)}
                      >
                        {(col as any).label}
                      </TableSortLabel>
                    ) : (
                      (col as any).label
                    )}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedMetrics.map((metric) => {
                const app = getApplicationInfo(metric.applicationId);
                return (
                  <TableRow key={metric.id} hover>
                    {columns.map(col => {
                      const key = col.key as keyof MetricData;
                      if (col.key === 'application') {
                        return (
                          <TableCell key={`app-${metric.id}`}>
                            {app && (
                              <GlowingChip
                                icon={typeof app.icon === 'string' ? (
                                  <span>{app.icon}</span>
                                ) : (
                                  (() => {
                                    const IconComponent = app.icon;
                                    return <IconComponent />;
                                  })()
                                )}
                                label={app.displayName}
                                size="small"
                                sx={{ bgcolor: app.color, color: 'white' }}
                              />
                            )}
                          </TableCell>
                        );
                      }
                      if (col.key === 'timestamp') {
                        return (
                          <TableCell key={`ts-${metric.id}`}>
                            <Typography variant="body2">{formatTimestamp(metric.timestamp)}</Typography>
                          </TableCell>
                        );
                      }

                      const value = metric[key] as any;
                      let display: React.ReactNode = value;
                      if (typeof value === 'number') {
                        if (key === 'responseTime') display = formatNumber(value, 0);
                        else if (key === 'successRate' || key === 'errorRate' || key === 'uptime') display = `${formatNumber(value, 1)}%`;
                        else if (key === 'cost') display = formatCurrency(value);
                        else display = formatNumber(value, 0);
                      }
                      return (
                        <TableCell key={`${String(key)}-${metric.id}`} align={(col as any).align || 'left'}>
                          {display}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </StyledTableContainer>
      </Paper>
      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={sortedMetrics.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Box>
  );
};

export default MetricsTable;