import React, { useState } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import type { MetricData, AIApplication } from '../types';

interface MetricsChartProps {
  metrics: MetricData[];
  applications: AIApplication[];
}

type ChartType = 'line' | 'bar';
type MetricType = 'responseTime' | 'requestCount' | 'successRate' | 'errorRate' | 'cost' | 'uptime';

const MetricsChart: React.FC<MetricsChartProps> = ({ metrics, applications }) => {
  const theme = useTheme();
  const [chartType, setChartType] = useState<ChartType>('line');
  const [metricType, setMetricType] = useState<MetricType>('responseTime');

  const isDarkMode = theme.palette.mode === 'dark';
  const chartColors = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    grid: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
    text: theme.palette.text.primary,
    background: theme.palette.background.paper,
  };

  const metricLabels: Record<MetricType, string> = {
    responseTime: 'Response Time (ms)',
    requestCount: 'Request Count',
    successRate: 'Success Rate (%)',
    errorRate: 'Error Rate (%)',
    cost: 'Cost ($)',
    uptime: 'Uptime (%)',
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatValue = (value: number, type: MetricType) => {
    switch (type) {
      case 'responseTime':
        return `${value.toFixed(0)}ms`;
      case 'requestCount':
        return value.toFixed(0);
      case 'successRate':
      case 'errorRate':
      case 'uptime':
        return `${value.toFixed(1)}%`;
      case 'cost':
        return `$${value.toFixed(2)}`;
      default:
        return value.toFixed(2);
    }
  };

  // Group metrics by timestamp and application
  const chartData = React.useMemo(() => {
    const dataMap = new Map<string, any>();

    metrics.forEach(metric => {
      const timestamp = metric.timestamp;
      if (!dataMap.has(timestamp)) {
        dataMap.set(timestamp, {
          timestamp,
          formattedTime: formatTimestamp(timestamp),
        });
      }

      const app = applications.find(a => a.id === metric.applicationId);
      if (app) {
        dataMap.get(timestamp)![app.displayName] = metric[metricType];
      }
    });

    return Array.from(dataMap.values())
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [metrics, applications, metricType]);

  // Keep colors on app objects; no separate color resolver needed

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            bgcolor: chartColors.background,
            border: 1,
            borderColor: isDarkMode ? 'rgba(255, 165, 0, 0.3)' : 'divider',
            borderRadius: 1,
            p: 2,
            boxShadow: isDarkMode ? '0 0 20px rgba(255, 165, 0, 0.2)' : 2,
            backdropFilter: isDarkMode ? 'blur(10px)' : 'none',
          }}
        >
          <Typography variant="body2" sx={{ mb: 1, color: chartColors.text }}>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {formatValue(entry.value, metricType)}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  const renderChart = () => {
    const commonProps = {
      data: chartData,
      margin: { top: 5, right: 30, left: 20, bottom: 5 },
    };

    const xAxisProps = {
      dataKey: 'formattedTime',
      tick: { fontSize: 12, fill: chartColors.text },
      interval: 'preserveStartEnd' as const,
    };

    const yAxisProps = {
      tick: { fontSize: 12, fill: chartColors.text },
      tickFormatter: (value: number) => formatValue(value, metricType),
    };

    if (chartType === 'line') {
      return (
        <LineChart {...commonProps}>
          <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
          <XAxis {...xAxisProps} />
          <YAxis {...yAxisProps} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: chartColors.text }} />
          {applications.map(app => (
            <Line
              key={app.id}
              type="monotone"
              dataKey={app.displayName}
              stroke={app.color}
              strokeWidth={2}
              dot={{ 
                r: 4, 
                fill: app.color,
                stroke: app.color,
                strokeWidth: isDarkMode ? 2 : 1,
                filter: isDarkMode ? `drop-shadow(0 0 6px ${app.color})` : 'none'
              }}
              connectNulls={false}
            />
          ))}
        </LineChart>
      );
    }

    return (
      <BarChart {...commonProps}>
        <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
        <XAxis {...xAxisProps} />
        <YAxis {...yAxisProps} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ color: chartColors.text }} />
        {applications.map(app => (
          <Bar
            key={app.id}
            dataKey={app.displayName}
            fill={app.color}
            style={{
              filter: isDarkMode ? `drop-shadow(0 0 8px ${app.color}40)` : 'none'
            }}
          />
        ))}
      </BarChart>
    );
  };

  if (metrics.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          No metrics data available for chart.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Chart Controls */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Metric</InputLabel>
          <Select
            value={metricType}
            label="Metric"
            onChange={(e) => setMetricType(e.target.value as MetricType)}
          >
            {Object.entries(metricLabels).map(([key, label]) => (
              <MenuItem key={key} value={key}>
                {label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={(_, newType) => newType && setChartType(newType)}
          size="small"
        >
          <ToggleButton value="line">Line Chart</ToggleButton>
          <ToggleButton value="bar">Bar Chart</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Chart */}
      <Box sx={{ width: '100%', height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </Box>

      {/* Chart Legend */}
      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center' }}>
        {applications.map(app => (
          <Box key={app.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                bgcolor: app.color,
                borderRadius: chartType === 'line' ? '50%' : 1,
              }}
            />
            <Typography variant="body2" component="span">
              {typeof app.icon === 'string' ? (
                <span style={{ fontSize: 14, marginRight: 6 }}>{app.icon}</span>
              ) : (
                (() => {
                  const IconComponent = app.icon;
                  return <IconComponent width={14} height={14} style={{ marginRight: 6 }} />;
                })()
              )}
              {app.displayName}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default MetricsChart;